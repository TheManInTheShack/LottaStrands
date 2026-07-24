import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from engine.api import state

HIERARCHY_PATH = Path("model/config/hierarchy.json")

router = APIRouter()


def _volume_counts(g, volume_id: str) -> dict:
    """BFS from a Volume node; count descendant nodes by label."""
    counts = {}
    queue = [volume_id]
    visited = set()
    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        node = g.nodes.get(node_id)
        if node and node_id != volume_id:
            for label in node.labels:
                counts[label] = counts.get(label, 0) + 1
        for edge in g.get_edges_from(node_id):
            if edge.type == "CONTAINS" and edge.to_id not in visited:
                queue.append(edge.to_id)
    return counts


@router.get("/graph")
def get_graph():
    return state.get_graph().to_dict()


@router.get("/corpus")
def get_corpus():
    g = state.get_graph()
    corpus = next(iter(g.get_nodes_by_label("Corpus")), None)
    all_volumes = g.get_nodes_by_label("Volume")

    # Use saved display order if present; fall back to added_at
    saved_order: list = []
    if HIERARCHY_PATH.exists():
        try:
            saved_order = json.loads(HIERARCHY_PATH.read_text()).get("volume_order", [])
        except Exception:
            saved_order = []

    if saved_order:
        vol_map = {v.id: v for v in all_volumes}
        volumes = [vol_map[vid] for vid in saved_order if vid in vol_map]
        ordered_ids = set(saved_order)
        volumes += sorted(
            [v for v in all_volumes if v.id not in ordered_ids],
            key=lambda n: n.properties.get("added_at", "")
        )
    else:
        volumes = sorted(all_volumes, key=lambda n: n.properties.get("added_at", ""))

    return {
        "name": corpus.properties.get("name") if corpus else "",
        "title": corpus.properties.get("title") if corpus else "",
        "volumes": [
            {"id": v.id, **v.properties, "counts": _volume_counts(g, v.id)}
            for v in volumes
        ]
    }


@router.get("/scenes")
def get_scenes():
    g = state.get_graph()
    scenes = sorted(g.get_nodes_by_label("Scene"),
                    key=lambda n: n.properties.get("index", 0))
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


@router.get("/paragraphs")
def get_paragraphs():
    g = state.get_graph()
    scenes = sorted(g.get_nodes_by_label("Scene"),
                    key=lambda n: n.properties.get("index", 0))
    result = []
    for scene in scenes:
        para_nodes = sorted(
            [g.nodes[e.to_id] for e in g.get_edges_from(scene.id)
             if e.type == "CONTAINS"
             and e.to_id in g.nodes
             and "Paragraph" in g.nodes[e.to_id].labels],
            key=lambda n: n.properties.get("index", 0)
        )
        for para in para_nodes:
            result.append({
                "id": para.id,
                "index": para.properties.get("index"),
                "text": para.properties.get("text", ""),
                "type": para.properties.get("type", "text"),
                "scene_id": scene.id,
                "scene_index": scene.properties.get("index"),
                "scene_heading": scene.properties.get("heading", ""),
            })
    return result


@router.get("/scenes/{index}")
def get_scene(index: int):
    g = state.get_graph()
    scene = next(
        (n for n in g.get_nodes_by_label("Scene")
         if n.properties.get("index") == index),
        None
    )
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene {index} not found")

    shot_nodes = sorted(
        [g.nodes[e.to_id] for e in g.get_edges_from(scene.id)
         if e.type == "CONTAINS" and e.to_id in g.nodes],
        key=lambda n: n.properties.get("index", 0)
    )

    shots = []
    para_count = 0
    text_parts = []

    for shot in shot_nodes:
        para_nodes = sorted(
            [g.nodes[e.to_id] for e in g.get_edges_from(shot.id)
             if e.type == "CONTAINS" and e.to_id in g.nodes],
            key=lambda n: n.properties.get("index", 0)
        )
        paragraphs = []
        for para in para_nodes:
            ptype = para.properties.get("type")
            text = para.properties.get("text", "")
            p = {"type": ptype, "text": text}
            if ptype == "dialogue":
                speaker = para.properties.get("speaker", "")
                p["speaker"] = speaker
                text_parts.append(f"{speaker}: {text}")
            else:
                text_parts.append(text)
            paragraphs.append(p)
        para_count += len(paragraphs)
        shots.append({
            "index": shot.properties.get("index"),
            "heading": shot.properties.get("heading", ""),
            "paragraphs": paragraphs
        })

    return {
        "id": scene.id,
        "index": scene.properties.get("index"),
        "heading": scene.properties.get("heading"),
        "shot_count": len(shots),
        "paragraph_count": para_count,
        "full_text": "\n\n".join(text_parts),
        "shots": shots
    }
