import json
import re
import uuid
from datetime import datetime, timezone
from .database import connect, decode
from .providers import get_provider
from .librarian import CrossrefLibrarian
from .workflow import Stage, validate_transition


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid() -> str:
    return str(uuid.uuid4())


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def create_project(data: dict) -> dict:
    timestamp, project_id = now(), uid()
    slug = slugify(data["title"])
    with connect() as db:
        suffix = 1
        candidate = slug
        while db.execute("SELECT 1 FROM projects WHERE slug = ?", (candidate,)).fetchone():
            suffix += 1
            candidate = f"{slug}-{suffix}"
        db.execute(
            "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (project_id, data["title"], candidate, data["research_question"], data["venue"],
             data.get("initial_thesis"), str(data.get("target_submission_date")) if data.get("target_submission_date") else None,
             Stage.IDEA, timestamp, timestamp),
        )
    return get_project(project_id)


def list_projects() -> list[dict]:
    with connect() as db:
        return [decode(row) for row in db.execute("SELECT * FROM projects ORDER BY updated_at DESC")]


def get_project(project_id: str) -> dict | None:
    with connect() as db:
        return decode(db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())


def transition(project_id: str, target: Stage, reason: str | None) -> dict:
    project = get_project(project_id)
    if not project:
        raise KeyError(project_id)
    validate_transition(Stage(project["stage"]), target, reason)
    timestamp = now()
    with connect() as db:
        db.execute("UPDATE projects SET stage = ?, updated_at = ? WHERE id = ?", (target, timestamp, project_id))
        db.execute("INSERT INTO human_decisions VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (uid(), project_id, "WORKFLOW_TRANSITION", project["stage"], target, reason, timestamp))
    return get_project(project_id)


def research_queries(project: dict) -> list[str]:
    core = project["research_question"].rstrip("?")
    return [
        f"{core} architecture governance",
        "agentic AI runtime governance human oversight",
        "autonomous software systems monitoring fail-safe architecture",
        "enterprise AI governance access control observability",
        "AI agents counterevidence governance limitations",
    ]


def generate_plan(project_id: str) -> dict:
    project = get_project(project_id)
    if not project:
        raise KeyError(project_id)
    run_id, timestamp = uid(), now()
    queries = research_queries(project)
    content = "\n".join([
        "# Research Plan", "", f"## Research question\n\n{project['research_question']}",
        "", "## Search streams", "", *[f"- {query}" for query in queries],
        "", "## Integrity checks", "", "- Identify seminal and recent work.",
        "- Search independently for contradictory evidence.", "- Follow primary citation chains.",
        "- Treat the initial thesis as provisional.", "- Stop only at literature saturation.",
    ])
    with connect() as db:
        version = db.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM research_plans WHERE project_id = ?", (project_id,)).fetchone()[0]
        plan_id = uid()
        db.execute("INSERT INTO agent_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, NULL)",
                   (run_id, project_id, "Research Director", "Generate research plan", "deterministic-v1", "completed", timestamp, timestamp))
        db.execute("INSERT INTO research_plans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (plan_id, project_id, version, content, timestamp, "agent", "Research Director", "deterministic-v1", run_id, "[]", None, 0))
    return get_plan(project_id)


def get_plan(project_id: str) -> dict | None:
    with connect() as db:
        return decode(db.execute("SELECT id, project_id, version, content, created_at FROM research_plans WHERE project_id = ? ORDER BY version DESC LIMIT 1", (project_id,)).fetchone())


def run_search(project_id: str, provider_name: str) -> dict:
    project = get_project(project_id)
    if not project:
        raise KeyError(project_id)
    provider, run_id, started = get_provider(provider_name), uid(), now()
    queries, added, verified = research_queries(project), 0, 0
    totals = {"input": 0, "output": 0, "cached": 0}
    with connect() as db:
        db.execute("INSERT INTO agent_runs VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0, 0, 0, 0, 0, NULL)",
                   (run_id, project_id, "Literature Scout", "Discover candidate literature", provider.model, "running", started))
    librarian = CrossrefLibrarian()
    try:
        for query in queries:
            source_ids = []
            batch = provider.search(query)
            totals["input"] += batch.input_tokens
            totals["output"] += batch.output_tokens
            totals["cached"] += batch.cached_tokens
            with connect() as db:
                for candidate in batch.sources:
                    candidate, verification_status, raw_metadata = librarian.verify(candidate)
                    source_id = uid()
                    cursor = db.execute(
                        "INSERT OR IGNORE INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'candidate', ?, ?)",
                        (source_id, project_id, candidate["title"], json.dumps(candidate["authors"]), candidate["publication_year"], candidate["venue"], candidate["source_type"], candidate.get("doi"), candidate.get("url"), candidate.get("abstract"), candidate["relevance_score"], candidate["relevance_reason"], query, now(), run_id),
                    )
                    if cursor.rowcount:
                        source_ids.append(source_id)
                        added += 1
                        db.execute("INSERT INTO source_verifications VALUES (?, ?, ?, ?, ?, ?)", (uid(), source_id, librarian.provider, verification_status, now(), json.dumps(raw_metadata) if raw_metadata else None))
                        verified += int(verification_status == "verified")
                db.execute("INSERT INTO search_queries VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (uid(), project_id, query, provider.name, now(), len(batch.sources), json.dumps(source_ids), run_id))
        with connect() as db:
            db.execute("UPDATE agent_runs SET status = 'completed', completed_at = ?, input_tokens = ?, output_tokens = ?, cached_tokens = ? WHERE id = ?", (now(), totals["input"], totals["output"], totals["cached"], run_id))
            if project["stage"] == Stage.BRIEF_APPROVED:
                db.execute("UPDATE projects SET stage = ?, updated_at = ? WHERE id = ?", (Stage.RESEARCHING, now(), project_id))
    except Exception as error:
        with connect() as db:
            db.execute("UPDATE agent_runs SET status = 'failed', completed_at = ?, input_tokens = ?, output_tokens = ?, cached_tokens = ?, error = ? WHERE id = ?", (now(), totals["input"], totals["output"], totals["cached"], str(error)[:1000], run_id))
        raise
    return {"run_id": run_id, "query_count": len(queries), "sources_added": added, "sources_verified": verified}


def list_sources(project_id: str) -> list[dict]:
    with connect() as db:
        return [decode(row) for row in db.execute("SELECT s.id, s.title, s.authors, s.publication_year, s.venue, s.source_type, s.doi, s.url, s.abstract, s.relevance_score, s.relevance_reason, s.discovery_query, s.status, v.status AS verification_status FROM sources s LEFT JOIN source_verifications v ON v.source_id = s.id AND v.provider = 'crossref' WHERE s.project_id = ? ORDER BY s.relevance_score DESC, s.publication_year DESC", (project_id,))]


def review_sources(project_id: str, source_ids: list[str], decision: str, rationale: str | None) -> int:
    placeholders = ",".join("?" for _ in source_ids)
    with connect() as db:
        found = db.execute(f"SELECT id FROM sources WHERE project_id = ? AND id IN ({placeholders})", (project_id, *source_ids)).fetchall()
        if len(found) != len(set(source_ids)):
            raise KeyError("One or more sources do not belong to this project")
        db.execute(f"UPDATE sources SET status = ? WHERE project_id = ? AND id IN ({placeholders})", (decision, project_id, *source_ids))
        db.execute("INSERT INTO human_decisions VALUES (?, ?, ?, NULL, NULL, ?, ?)", (uid(), project_id, f"SOURCE_{decision.upper()}", rationale or json.dumps(source_ids), now()))
    return len(found)


def list_runs(project_id: str) -> list[dict]:
    with connect() as db:
        return [decode(row) for row in db.execute("SELECT id, agent_name, task, model, status, started_at, completed_at, input_tokens, output_tokens, cached_tokens, estimated_cost, error FROM agent_runs WHERE project_id = ? ORDER BY started_at DESC", (project_id,))]
