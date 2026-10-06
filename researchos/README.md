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

## Test

```bash
npm test
.venv/bin/python -m pytest apps/api/tests
```

Local data is written to `researchos/data/researchos.db` and is ignored by Git.
