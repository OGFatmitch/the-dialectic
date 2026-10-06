CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, slug TEXT NOT NULL UNIQUE,
  research_question TEXT NOT NULL, venue TEXT NOT NULL, initial_thesis TEXT,
  target_submission_date TEXT, stage TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_plans (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  version INTEGER NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL,
  created_by TEXT NOT NULL, agent_name TEXT NOT NULL, model TEXT NOT NULL,
  run_id TEXT NOT NULL, input_artifacts TEXT NOT NULL, parent_version TEXT,
  human_approved INTEGER NOT NULL DEFAULT 0,
  UNIQUE(project_id, version)
);
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  title TEXT NOT NULL, authors TEXT NOT NULL, publication_year INTEGER,
  venue TEXT, source_type TEXT NOT NULL, doi TEXT, url TEXT, abstract TEXT,
  relevance_score REAL NOT NULL, relevance_reason TEXT NOT NULL,
  discovery_query TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'candidate',
  created_at TEXT NOT NULL, run_id TEXT NOT NULL,
  UNIQUE(project_id, title, publication_year)
);
CREATE TABLE IF NOT EXISTS search_queries (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  query TEXT NOT NULL, provider TEXT NOT NULL, timestamp TEXT NOT NULL,
  results_reviewed INTEGER NOT NULL, sources_added TEXT NOT NULL,
  agent_run_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  agent_name TEXT NOT NULL, task TEXT NOT NULL, model TEXT NOT NULL,
  status TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT,
  input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
  cached_tokens INTEGER NOT NULL DEFAULT 0, tool_cost REAL NOT NULL DEFAULT 0,
  estimated_cost REAL NOT NULL DEFAULT 0, error TEXT
);
CREATE TABLE IF NOT EXISTS human_decisions (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  decision_type TEXT NOT NULL, from_stage TEXT, to_stage TEXT,
  rationale TEXT, created_at TEXT NOT NULL
);
