from fastapi import APIRouter, HTTPException
from engine.api import state

router = APIRouter()


@router.get("/graph")
def get_graph():
    return state.get_graph().to_dict()


@router.get("/corpus")
def get_corpus():
    g = state.get_graph()
    corpus = next(iter(g.get_nodes_by_label("Corpus")), None)
    volumes = sorted(g.get_nodes_by_label("Volume"),
                     key=lambda n: n.properties.get("title", ""))
    return {
        "name": corpus.properties.get("name") if corpus else "",
        "title": corpus.properties.get("title") if corpus else "",
        "volumes": [{"id": v.id, **v.properties} for v in volumes]
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
