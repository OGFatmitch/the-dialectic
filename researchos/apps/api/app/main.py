from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from . import services
from .database import initialize
from .schemas import AgentRun, Project, ProjectCreate, ResearchPlan, SearchRequest, SearchResult, Source, SourceReview, TransitionRequest


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    yield


app = FastAPI(title="ResearchOS API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health(): return {"status": "ok"}


@app.get("/projects", response_model=list[Project])
def projects(): return services.list_projects()


@app.post("/projects", response_model=Project, status_code=201)
def create_project(body: ProjectCreate): return services.create_project(body.model_dump())


@app.get("/projects/{project_id}", response_model=Project)
def project(project_id: str):
    value = services.get_project(project_id)
    if not value: raise HTTPException(404, "Project not found")
    return value


@app.post("/projects/{project_id}/transition", response_model=Project)
def transition(project_id: str, body: TransitionRequest):
    try: return services.transition(project_id, body.target, body.reason)
    except KeyError: raise HTTPException(404, "Project not found")
    except ValueError as error: raise HTTPException(409, str(error))


@app.get("/projects/{project_id}/research-plan", response_model=ResearchPlan | None)
def plan(project_id: str): return services.get_plan(project_id)


@app.post("/projects/{project_id}/research-plan", response_model=ResearchPlan, status_code=201)
def generate_plan(project_id: str):
    try: return services.generate_plan(project_id)
    except KeyError: raise HTTPException(404, "Project not found")


@app.post("/projects/{project_id}/search", response_model=SearchResult)
def search(project_id: str, body: SearchRequest):
    try: return services.run_search(project_id, body.provider)
    except KeyError: raise HTTPException(404, "Project not found")
    except ValueError as error: raise HTTPException(400, str(error))
    except RuntimeError as error: raise HTTPException(502, str(error))


@app.get("/projects/{project_id}/sources", response_model=list[Source])
def sources(project_id: str): return services.list_sources(project_id)


@app.post("/projects/{project_id}/sources/review")
def review_sources(project_id: str, body: SourceReview):
    try: return {"updated": services.review_sources(project_id, body.source_ids, body.decision, body.rationale)}
    except KeyError as error: raise HTTPException(404, str(error))


@app.get("/projects/{project_id}/runs", response_model=list[AgentRun])
def runs(project_id: str): return services.list_runs(project_id)
