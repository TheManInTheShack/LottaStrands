"""
In-memory graph state for the API.

On startup: loads graph.json, then re-applies curation.json if it exists.
Operations modify the in-memory working graph and append to curation.json.
The raw graph.json is never modified.
"""

import json
import copy
from pathlib import Path

from engine.graph.model import Graph

_graph = None           # working in-memory graph (post-curation)
_raw_graph_path = None  # path to graph.json
_curation_path = None   # path to curation.json
_operations = []        # list of applied operations (mirrors curation.json)


def load(graph_path: Path, curation_path: Path):
    global _graph, _raw_graph_path, _curation_path, _operations
    _raw_graph_path = graph_path
    _curation_path = curation_path

    _graph = Graph.load(str(graph_path))

    if curation_path.exists():
        with open(curation_path) as f:
            _operations = json.load(f)
        from engine.curate.operations import apply_operations
        apply_operations(_graph, _operations)
    else:
        _operations = []

    print(f"Graph loaded: {len(_graph.nodes)} nodes, {len(_graph.edges)} edges")
    if _operations:
        print(f"Curation applied: {len(_operations)} operations")


def get_graph() -> Graph:
    return _graph


def get_operations() -> list:
    return _operations


def add_operation(op: dict):
    """Record an operation and persist to curation.json."""
    _operations.append(op)
    with open(_curation_path, 'w') as f:
        json.dump(_operations, f, indent=2)


def save_curated(output_path: Path):
    """Write the current working graph to graph_curated.json."""
    _graph.save(str(output_path))


def reload():
    """Re-load raw graph and re-apply all recorded operations."""
    load(_raw_graph_path, _curation_path)
