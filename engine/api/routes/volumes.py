from fastapi import APIRouter, HTTPException
from pathlib import Path

from engine.api import state
from engine.api.models import VolumeCreate, VolumeDelete
from engine.ingest.flat_ingest import flat_ingest

router = APIRouter()

GRAPH_PATH = Path("model/data/graph.json")
CURATION_PATH = Path("model/config/curation.json")


@router.post("/volumes")
def create_volume(body: VolumeCreate):
    config = {
        "title": body.title,
        "type": body.type,
        "year": body.year,
        "authors": body.authors,
        "format": body.format,
        "url": body.url,
    }
    # Append to existing corpus; pass None only if graph is genuinely empty
    existing = state.get_graph()
    g = flat_ingest(body.text, config,
                    existing_graph=existing if existing.nodes else None)

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    g.save(str(GRAPH_PATH))

    # Initialise curation log only if it doesn't exist yet
    if not CURATION_PATH.exists():
        CURATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        CURATION_PATH.write_text("[]")

    state.load(GRAPH_PATH, CURATION_PATH)

    volumes = g.get_nodes_by_label("Volume")
    return {
        "status": "ok",
        "volume_count": len(volumes),
        "paragraph_count": len(g.get_nodes_by_label("Paragraph")),
    }


@router.post("/volumes/delete")
def delete_volume(body: VolumeDelete):
    g = state.get_graph()
    volume = g.nodes.get(body.volume_id)
    if not volume or "Volume" not in volume.labels:
        raise HTTPException(status_code=404, detail="Volume not found")

    # BFS: collect the volume and all its descendant nodes
    to_delete: set = set()
    queue = [body.volume_id]
    while queue:
        nid = queue.pop()
        to_delete.add(nid)
        for edge in g.get_edges_from(nid):
            if edge.type == "CONTAINS" and edge.to_id not in to_delete:
                queue.append(edge.to_id)

    # Drop all edges that touch any deleted node
    g.edges = [e for e in g.edges
               if e.from_id not in to_delete and e.to_id not in to_delete]

    # Drop the nodes themselves
    for nid in to_delete:
        del g.nodes[nid]

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    g.save(str(GRAPH_PATH))
    state.reload()

    return {"status": "ok", "deleted_node_count": len(to_delete)}
