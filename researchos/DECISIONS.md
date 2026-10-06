# Architecture Decisions

## ADR-001 — Application-owned orchestration

Use bounded agent contracts behind application services. Models never mutate workflow state or canonical metadata directly.

## ADR-002 — SQLite first, PostgreSQL production

Use SQLAlchemy-compatible domain shapes, but keep this slice dependency-light with Python's SQLite driver. Stable UUIDs and ISO timestamps make migration straightforward.

## ADR-003 — Deterministic provider by default

The local demo provider returns clearly labeled seed candidates. This makes the entire slice runnable without credentials. Live providers remain modular and must never fabricate missing metadata.

## ADR-004 — Explicit gates

Transitions are allow-listed. Returning to an earlier stage is recorded with a reason; moving forward cannot skip required gates.

## ADR-005 — Metadata authority

Search creates `candidate` sources. Only the Evidence Librarian service may normalize, verify, merge, or promote canonical source metadata.

## ADR-006 — No silent model fallback

If a configured live provider fails, its run fails visibly. The system does not substitute invented results.
