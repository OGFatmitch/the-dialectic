export type ProjectStage =
  | "IDEA" | "BRIEF_APPROVED" | "RESEARCHING" | "RESEARCH_GATE"
  | "THESIS_DEVELOPMENT" | "THESIS_APPROVAL" | "OUTLINE_DEVELOPMENT"
  | "OUTLINE_APPROVAL" | "DRAFTING" | "ADVERSARIAL_REVIEW"
  | "CLAIM_AUDIT" | "REVISION" | "VENUE_REVIEW" | "FINAL_REVIEW"
  | "APPROVED" | "FORMATTED" | "SUBMISSION_READY";

export interface Project {
  id: string; title: string; slug: string; research_question: string;
  initial_thesis: string | null; venue: string; target_submission_date: string | null;
  stage: ProjectStage; created_at: string; updated_at: string;
}

export interface ResearchPlan { id: string; project_id: string; version: number; content: string; created_at: string; }
export interface Source { id: string; title: string; authors: string[]; publication_year: number | null; venue: string | null; source_type: string; doi: string | null; url: string | null; abstract: string | null; relevance_score: number; relevance_reason: string; discovery_query: string; status: "candidate" | "accepted" | "rejected" | "verified"; }
export interface SearchRun { run_id: string; query_count: number; sources_added: number; }
