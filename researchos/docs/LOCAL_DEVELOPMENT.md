# Local development

The `demo` search provider is deterministic and labels every result as an unverified candidate. It exists for UI development and tests only.

To add a live provider, implement `SearchProvider` in `apps/api/app/providers.py`, register it in `get_provider`, and keep credentials server-side. Provider failures must be recorded as failed runs; never silently fall back to demo data.

The seeded project is available from the dashboard button. Approve its brief, generate a research plan, and run literature search to exercise the slice.
