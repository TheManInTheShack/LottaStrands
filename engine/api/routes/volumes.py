from fastapi import APIRouter
from pathlib import Path

from engine.api import state
from engine.api.models import VolumeCreate
from engine.ingest.flat_ingest import flat_ingest

router = APIRouter()

GRAPH_PATH = Path("model/data/graph.json")
CURATION_PATH = Path("model/config/curation.json")


@router.post("/volumes")
def create_volume(body: VolumeCreate):
    config = {
        "name": body.title,
        "title": body.title,
        "type": body.type,
        "year": body.year,
        "authors": body.authors,
        "format": body.format,
        "url": body.url,
    }
    g = flat_ingest(body.text, config)

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    g.save(str(GRAPH_PATH))

    # Reset curation — new volume starts fresh
    CURATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURATION_PATH.write_text("[]")

    state.load(GRAPH_PATH, CURATION_PATH)

    para_count = len(g.get_nodes_by_label("Paragraph"))
    corpus = g.get_nodes_by_label("Corpus")
    volumes = g.get_nodes_by_label("Volume")

    return {
        "status": "ok",
        "corpus": corpus[0].properties if corpus else {},
        "volume": volumes[0].properties if volumes else {},
        "paragraph_count": para_count,
    }
