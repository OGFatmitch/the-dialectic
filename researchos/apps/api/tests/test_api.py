from fastapi.testclient import TestClient
from app.main import app


def test_vertical_slice(monkeypatch):
    monkeypatch.setattr("app.services.CrossrefLibrarian.verify", lambda self, candidate: (candidate, "verified", {"DOI": candidate.get("doi")}))
    with TestClient(app) as client:
        created = client.post("/projects", json={
            "title": "Governing Autonomous AI at Scale",
            "research_question": "What controls are required to govern autonomous AI agents?",
            "initial_thesis": "Enterprises need a dedicated control plane.",
        })
        assert created.status_code == 201
        project = created.json()
        assert project["stage"] == "IDEA"
        assert client.post(f"/projects/{project['id']}/research-plan").status_code == 201
        result = client.post(f"/projects/{project['id']}/search", json={"provider": "demo"})
        assert result.status_code == 200
        assert result.json()["query_count"] == 5
        sources = client.get(f"/projects/{project['id']}/sources").json()
        assert sources and sources[0]["status"] == "candidate"
        assert sources[0]["verification_status"] == "verified"
        reviewed = client.post(f"/projects/{project['id']}/sources/review", json={"source_ids": [sources[0]["id"]], "decision": "accepted"})
        assert reviewed.json()["updated"] == 1
        preflight = client.get(f"/projects/{project['id']}/search/preflight", params={"provider": "demo", "mode": "standard"}).json()
        assert preflight["new_query_count"] == 0
        assert preflight["duplicate_query_count"] == 5
        second = client.post(f"/projects/{project['id']}/search", json={"provider": "demo", "mode": "standard"}).json()
        assert second["query_count"] == 0
        budget = client.get(f"/projects/{project['id']}/budget").json()
        assert budget["project_limit_usd"] == 100
