from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from engine.api import state
from engine.api.routes import graph, curate

GRAPH_PATH = Path("model/data/graph.json")
CURATION_PATH = Path("model/config/curation.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load(GRAPH_PATH, CURATION_PATH)
    yield


app = FastAPI(title="LottaStrands Engine", lifespan=lifespan)

app.include_router(graph.router)
app.include_router(curate.router, prefix="/curate")


@app.get("/")
def root():
    return {"status": "ok", "service": "LottaStrands Engine"}
