from typing import Protocol


class SearchProvider(Protocol):
    name: str
    def search(self, query: str) -> list[dict]: ...


class DemoSearchProvider:
    """Deterministic, explicitly non-verified candidates for local development."""
    name = "demo"

    def search(self, query: str) -> list[dict]:
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
        return corpus[:1]


def get_provider(name: str) -> SearchProvider:
    if name == "demo":
        return DemoSearchProvider()
    raise ValueError(f"Unknown or unconfigured search provider: {name}")
