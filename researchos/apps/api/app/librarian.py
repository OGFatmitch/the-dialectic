import os
import re
from difflib import SequenceMatcher
from urllib.parse import quote

import httpx


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi.strip().lower())
    return value or None


def _title(message: dict) -> str:
    titles = message.get("title") or []
    return titles[0].strip() if titles else ""


def _authors(message: dict) -> list[str]:
    return [" ".join(filter(None, [author.get("given"), author.get("family")])).strip() for author in message.get("author", [])]


def _year(message: dict) -> int | None:
    for field in ("published-print", "published-online", "issued"):
        parts = (message.get(field) or {}).get("date-parts") or []
        if parts and parts[0]:
            return parts[0][0]
    return None


class CrossrefLibrarian:
    provider = "crossref"

    def __init__(self):
        email = os.getenv("CROSSREF_MAILTO")
        contact = f"mailto:{email}" if email else "https://github.com/OGFatmitch/the-dialectic"
        self.headers = {"User-Agent": f"ResearchOS/0.1 ({contact})"}

    def verify(self, candidate: dict) -> tuple[dict, str, dict | None]:
        doi = normalize_doi(candidate.get("doi"))
        try:
            with httpx.Client(timeout=20, headers=self.headers) as client:
                if doi:
                    response = client.get(f"https://api.crossref.org/works/{quote(doi, safe='')}")
                    if response.status_code == 404:
                        return candidate, "unverified", None
                    response.raise_for_status()
                    message = response.json()["message"]
                else:
                    response = client.get("https://api.crossref.org/works", params={"query.bibliographic": candidate["title"], "rows": 1, "select": "DOI,title,author,published-print,published-online,issued,container-title,URL,type"})
                    response.raise_for_status()
                    items = response.json()["message"]["items"]
                    if not items or SequenceMatcher(None, candidate["title"].casefold(), _title(items[0]).casefold()).ratio() < 0.88:
                        return candidate, "unverified", None
                    message = items[0]
            canonical = dict(candidate)
            canonical.update({"title": _title(message) or candidate["title"], "authors": _authors(message) or candidate["authors"], "publication_year": _year(message) or candidate.get("publication_year"), "venue": ((message.get("container-title") or [None])[0] or candidate.get("venue")), "source_type": message.get("type") or candidate["source_type"], "doi": normalize_doi(message.get("DOI")) or doi, "url": message.get("URL") or candidate.get("url")})
            return canonical, "verified", message
        except (httpx.HTTPError, KeyError, ValueError, TypeError):
            return candidate, "verification_failed", None
