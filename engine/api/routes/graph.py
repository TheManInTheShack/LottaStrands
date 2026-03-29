from fastapi import APIRouter
from engine.api import state

router = APIRouter()


@router.get("/graph")
def get_graph():
    return state.get_graph().to_dict()


@router.get("/scenes")
def get_scenes():
    g = state.get_graph()
    scenes = sorted(
        g.get_nodes_by_label("Scene"),
        key=lambda n: n.properties.get("index", 0)
    )
    result = []
    for scene in scenes:
        shot_edges = [e for e in g.get_edges_from(scene.id) if e.type == "CONTAINS"]
        result.append({
            "id": scene.id,
            "index": scene.properties.get("index"),
            "heading": scene.properties.get("heading"),
            "shot_count": len(shot_edges),
        })
    return result
