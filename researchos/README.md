# ResearchOS

High-integrity autonomous research and publication system. This repository contains the first vertical slice.

## Run locally

```bash
cd researchos
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/api/requirements.txt
npm install
npm run dev
```

The API runs on `http://localhost:8000`; the web app runs on `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL` to override the API URL.

Copy the repository-root `.env.example` to `.env` and configure `OPENAI_API_KEY` and `OPENAI_PROJECT_ID`. Keys are loaded only by the FastAPI process. `RESEARCHOS_SEARCH_MODEL` defaults to `gpt-5.5`; `CROSSREF_MAILTO` identifies the client to Crossref's polite pool.

The literature-search button performs five independent web searches and therefore incurs API and tool charges. Failed calls are retained in the run inspector rather than silently replaced with demo data.

## Test

```bash
npm test
.venv/bin/python -m pytest apps/api/tests
```

Local data is written to `researchos/data/researchos.db` and is ignored by Git.
