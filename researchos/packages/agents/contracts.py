from typing import Literal
from pydantic import BaseModel, Field


class Provenance(BaseModel):
    run_id: str
    agent_name: str
    model: str
    input_artifacts: list[str]


class ResearchDirectorInput(BaseModel):
    project_id: str
    research_question: str
    venue: str
    initial_thesis: str | None = None


class ResearchPlanOutput(BaseModel):
    searchable_subquestions: list[str] = Field(min_length=3)
    theoretical_domains: list[str]
    counterevidence_queries: list[str] = Field(min_length=1)
    saturation_criteria: list[str]
    provenance: Provenance


class CandidateSource(BaseModel):
    title: str
    authors: list[str]
    publication_year: int | None
    venue: str | None
    source_type: str
    doi: str | None
    url: str | None
    abstract: str | None
    relevance_score: float = Field(ge=0, le=1)
    relevance_reason: str
    discovery_query: str
    status: Literal["candidate"] = "candidate"


class LiteratureScoutOutput(BaseModel):
    sources: list[CandidateSource]
    provenance: Provenance
