from fastapi import APIRouter, HTTPException
from engine.api import state
from engine.api.models import MergeRequest, SplitRequest, RenameRequest
from engine.curate import operations
from engine.graph.model import Graph
from pathlib import Path
import json

router = APIRouter()


@router.get("/preview")
def preview():
    """Return current working graph state (all operations applied)."""
    return state.get_graph().to_dict()


@router.get("/operations")
def get_operations():
    """Return the list of recorded curation operations."""
    return state.get_operations()


@router.post("/merge")
def merge(req: MergeRequest):
    g = state.get_graph()
    try:
        operations.merge_nodes(g, req.level, req.indices, req.heading)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    state.add_operation({
        "op": "merge",
        "level": req.level,
        "indices": req.indices,
        "heading": req.heading
    })
    return {"status": "ok", "scene_count": len(g.get_nodes_by_label("Scene"))}


@router.post("/split")
def split(req: SplitRequest):
    g = state.get_graph()
    try:
        operations.split_node(
            g, req.level, req.index, req.at_child_index,
            req.heading_before, req.heading_after
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    state.add_operation({
        "op": "split",
        "level": req.level,
        "index": req.index,
        "at_child_index": req.at_child_index,
        "heading_before": req.heading_before,
        "heading_after": req.heading_after
    })
    return {"status": "ok"}


@router.post("/rename")
def rename(req: RenameRequest):
    g = state.get_graph()
    try:
        operations.rename_node(g, req.level, req.index, req.heading)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    state.add_operation({
        "op": "rename",
        "level": req.level,
        "index": req.index,
        "heading": req.heading
    })
    return {"status": "ok"}


@router.post("/save")
def save():
    """Write the current working graph to graph_curated.json."""
    output_path = Path("model/data/graph_curated.json")
    state.save_curated(output_path)
    return {"status": "ok", "path": str(output_path)}


@router.post("/reload")
def reload():
    """Re-load raw graph and re-apply all recorded operations."""
    state.reload()
    return {"status": "ok"}
