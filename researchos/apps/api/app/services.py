import json
import re
import uuid
from datetime import datetime, timezone
from .database import connect, decode
from .providers import get_provider
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
    queries, added = research_queries(project), 0
    with connect() as db:
        db.execute("INSERT INTO agent_runs VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0, 0, 0, 0, 0, NULL)",
                   (run_id, project_id, "Literature Scout", "Discover candidate literature", provider.name, "running", started))
        for query in queries:
            source_ids = []
            results = provider.search(query)
            for candidate in results:
                source_id = uid()
                cursor = db.execute(
                    "INSERT OR IGNORE INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'candidate', ?, ?)",
                    (source_id, project_id, candidate["title"], json.dumps(candidate["authors"]), candidate["publication_year"],
                     candidate["venue"], candidate["source_type"], candidate["doi"], candidate["url"], candidate["abstract"],
                     candidate["relevance_score"], candidate["relevance_reason"], query, now(), run_id),
                )
                if cursor.rowcount:
                    source_ids.append(source_id)
                    added += 1
            db.execute("INSERT INTO search_queries VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (uid(), project_id, query, provider.name, now(), len(results), json.dumps(source_ids), run_id))
        db.execute("UPDATE agent_runs SET status = 'completed', completed_at = ? WHERE id = ?", (now(), run_id))
        if project["stage"] == Stage.BRIEF_APPROVED:
            db.execute("UPDATE projects SET stage = ?, updated_at = ? WHERE id = ?", (Stage.RESEARCHING, now(), project_id))
    return {"run_id": run_id, "query_count": len(queries), "sources_added": added}


def list_sources(project_id: str) -> list[dict]:
    with connect() as db:
        return [decode(row) for row in db.execute("SELECT id, title, authors, publication_year, venue, source_type, doi, url, abstract, relevance_score, relevance_reason, discovery_query, status FROM sources WHERE project_id = ? ORDER BY relevance_score DESC, publication_year DESC", (project_id,))]
