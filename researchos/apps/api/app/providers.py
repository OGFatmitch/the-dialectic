import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[4] / ".env")
load_dotenv()


@dataclass
class SearchBatch:
    sources: list[dict]
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    tool_calls: int = 0


class SearchProvider(Protocol):
    name: str
    model: str
    def search(self, query: str, context_size: str = "medium", candidate_limit: int = 5) -> SearchBatch: ...


class DemoSearchProvider:
    """Deterministic, explicitly non-verified candidates for local development."""
    name = "demo"
    model = "deterministic-v1"

    def search(self, query: str, context_size: str = "medium", candidate_limit: int = 5) -> SearchBatch:
        corpus = [
            {
                "title": "AI Risk Management Framework (AI RMF 1.0)",
                "authors": ["National Institute of Standards and Technology"],
                "publication_year": 2023,
                "venue": "NIST",
                "source_type": "standard",
                "doi": "10.6028/NIST.AI.100-1",
                "url": "https://doi.org/10.6028/NIST.AI.100-1",
                "abstract": "A voluntary framework for managing risks in the design, development, deployment, and use of AI systems.",
            },
            {
                "title": "Concrete Problems in AI Safety",
                "authors": ["Dario Amodei", "Chris Olah", "Jacob Steinhardt", "Paul Christiano", "John Schulman", "Dan Mané"],
                "publication_year": 2016,
                "venue": "arXiv",
                "source_type": "preprint",
                "doi": None,
                "url": "https://arxiv.org/abs/1606.06565",
                "abstract": "A discussion of practical research problems in accident prevention for machine learning systems.",
            },
        ]
        words = {word.lower().strip("+,:?()") for word in query.split() if len(word) > 3}
        for item in corpus:
            haystack = f"{item['title']} {item['abstract']}".lower()
            overlap = sum(word in haystack for word in words)
            item["relevance_score"] = min(1.0, 0.45 + overlap * 0.1)
            item["relevance_reason"] = f"Candidate intersects {max(overlap, 1)} search concepts; metadata requires librarian verification."
        return SearchBatch(corpus[:1])


SOURCE_SCHEMA = {
    "type": "object",
    "properties": {"sources": {"type": "array", "maxItems": 5, "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"}, "authors": {"type": "array", "items": {"type": "string"}},
            "publication_year": {"type": ["integer", "null"]}, "venue": {"type": ["string", "null"]},
            "source_type": {"type": "string"}, "doi": {"type": ["string", "null"]},
            "url": {"type": ["string", "null"]}, "abstract": {"type": ["string", "null"]},
            "relevance_score": {"type": "number", "minimum": 0, "maximum": 1},
            "relevance_reason": {"type": "string"},
        },
        "required": ["title", "authors", "publication_year", "venue", "source_type", "doi", "url", "abstract", "relevance_score", "relevance_reason"],
        "additionalProperties": False,
    }}},
    "required": ["sources"], "additionalProperties": False,
}


class OpenAIWebSearchProvider:
    name = "openai"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.project_id = os.getenv("OPENAI_PROJECT_ID")
        self.model = os.getenv("RESEARCHOS_SEARCH_MODEL", "gpt-5.5")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured on the API server")

    def search(self, query: str, context_size: str = "medium", candidate_limit: int = 5) -> SearchBatch:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.project_id:
            headers["OpenAI-Project"] = self.project_id
        prompt = (
            "You are the Literature Scout in a high-integrity scholarly system. Search for up to five real, "
            f"high-quality sources relevant to the query below (maximum {candidate_limit}). Prefer peer-reviewed original research, official "
            "standards, government publications, and primary technical documentation. Include contradictory work "
            "when relevant. Never infer metadata from a title and never invent a DOI. Use null when uncertain. "
            "Return candidate metadata only; a separate librarian will verify it.\n\nQUERY: " + query
        )
        payload = {
            "model": self.model,
            "tools": [{"type": "web_search", "search_context_size": context_size}],
            "include": ["web_search_call.action.sources"], "input": prompt,
            "text": {"format": {"type": "json_schema", "name": "literature_candidates", "strict": True, "schema": SOURCE_SCHEMA}},
            "store": False,
        }
        with httpx.Client(timeout=120) as client:
            response = client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        if response.is_error:
            try: detail = response.json().get("error", {}).get("message", response.text)
            except ValueError: detail = response.text
            raise RuntimeError(f"OpenAI search failed ({response.status_code}): {detail}")
        body = response.json()
        text = next(content["text"] for item in body.get("output", []) if item.get("type") == "message" for content in item.get("content", []) if content.get("type") == "output_text")
        usage = body.get("usage") or {}
        tool_calls = sum(1 for item in body.get("output", []) if item.get("type") == "web_search_call" and (item.get("action") or {}).get("type", "search") == "search")
        return SearchBatch(json.loads(text)["sources"], usage.get("input_tokens", 0), usage.get("output_tokens", 0), (usage.get("input_tokens_details") or {}).get("cached_tokens", 0), tool_calls)


def get_provider(name: str) -> SearchProvider:
    if name == "demo":
        return DemoSearchProvider()
    if name == "openai":
        return OpenAIWebSearchProvider()
    raise ValueError(f"Unknown or unconfigured search provider: {name}")
