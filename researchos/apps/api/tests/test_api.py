from fastapi.testclient import TestClient
from app.main import app


def test_vertical_slice():
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
