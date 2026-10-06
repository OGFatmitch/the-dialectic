from datetime import date
from pydantic import BaseModel, Field, HttpUrl
from .workflow import Stage


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    research_question: str = Field(min_length=10)
    venue: str = "IEEE Software"
    initial_thesis: str | None = None
    target_submission_date: date | None = None


class Project(BaseModel):
    id: str
    title: str
    slug: str
    research_question: str
    venue: str
    initial_thesis: str | None
    target_submission_date: str | None
    stage: Stage
    created_at: str
    updated_at: str


class TransitionRequest(BaseModel):
    target: Stage
    reason: str | None = None


class Source(BaseModel):
    id: str
    title: str
    authors: list[str]
    publication_year: int | None
    venue: str | None
    source_type: str
    doi: str | None
    url: str | None
    abstract: str | None
    relevance_score: float
    relevance_reason: str
    discovery_query: str
    status: str


class ResearchPlan(BaseModel):
    id: str
    project_id: str
    version: int
    content: str
    created_at: str


class SearchRequest(BaseModel):
    provider: str = "demo"


class SearchResult(BaseModel):
    run_id: str
    query_count: int
    sources_added: int
