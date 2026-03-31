"""
Graph curation operations: merge, split, rename.

All operations work on a Graph instance in place.
After structural changes, affected levels are renumbered sequentially.
"""

from engine.graph.model import Graph

HIERARCHY = ["corpus", "volume", "scene", "shot", "paragraph", "sentence"]


def child_label(level: str) -> str:
    idx = HIERARCHY.index(level.lower())
    return HIERARCHY[idx + 1].capitalize() if idx + 1 < len(HIERARCHY) else None


def get_nodes_by_level(g: Graph, level: str) -> dict:
    """Return {index: node} for all nodes at the given level."""
    return {
        n.properties.get("index"): n
        for n in g.get_nodes_by_label(level.capitalize())
    }


def renumber_level(g: Graph, level: str):
    """Renumber all nodes at a level sequentially by current index."""
    nodes = sorted(
        g.get_nodes_by_label(level.capitalize()),
        key=lambda n: n.properties.get("index", 0)
    )
    for i, node in enumerate(nodes, start=1):
        node.properties["index"] = i


def rename_node(g: Graph, level: str, index: int, heading: str):
    nodes = get_nodes_by_level(g, level)
    if index not in nodes:
        raise ValueError(f"No {level} with index {index}")
    nodes[index].properties["heading"] = heading


def merge_nodes(g: Graph, level: str, indices: list, heading: str):
    """
    Merge N nodes at the given level into one.
    All children are re-parented to the new node in narrative order.
    PRECEDES edges are updated at both the merged level and child level.
    """
    label = level.capitalize()
    nodes_map = get_nodes_by_level(g, level)
    nodes_to_merge = [nodes_map[i] for i in sorted(indices) if i in nodes_map]

    if len(nodes_to_merge) < 2:
        raise ValueError(f"Need at least 2 nodes to merge, got {len(nodes_to_merge)}")

    first = nodes_to_merge[0]

    # Create merged node, preserving original parse indices for traceability
    merged = g.create_node([label], {
        "heading": heading,
        "index": first.properties.get("index"),
        "parse_indices": [n.properties.get("index") for n in nodes_to_merge]
    })

    # Re-parent all children in order, renumbering
    child_index = 1
    prev_child = None

    for parent in nodes_to_merge:
        children = _get_ordered_children(g, parent.id)
        for child in children:
            # Remove old CONTAINS edge
            g.edges = [e for e in g.edges
                       if not (e.type == "CONTAINS"
                               and e.from_id == parent.id
                               and e.to_id == child.id)]
            # Add new CONTAINS edge
            g.create_edge("CONTAINS", merged.id, child.id, {"index": child_index})
            child.properties["index"] = child_index
            child_index += 1

            # Stitch PRECEDES across the old scene boundary
            if prev_child:
                if not _precedes_exists(g, prev_child.id, child.id):
                    g.create_edge("PRECEDES", prev_child.id, child.id)
            prev_child = child

    # Re-parent merged node to the parent of the first merged node
    parent_edge = next(
        (e for e in g.edges if e.type == "CONTAINS" and e.to_id == first.id), None
    )
    if parent_edge:
        parent_id = parent_edge.from_id
        # Remove all CONTAINS edges from parent to merged nodes
        merged_ids = {n.id for n in nodes_to_merge}
        g.edges = [e for e in g.edges
                   if not (e.type == "CONTAINS"
                           and e.from_id == parent_id
                           and e.to_id in merged_ids)]
        g.create_edge("CONTAINS", parent_id, merged.id,
                      {"index": merged.properties["index"]})

    # Update PRECEDES at this level
    merged_ids = {n.id for n in nodes_to_merge}
    pred = next((e for e in g.edges
                 if e.type == "PRECEDES" and e.to_id == first.id), None)
    succ = next((e for e in g.edges
                 if e.type == "PRECEDES" and e.from_id == nodes_to_merge[-1].id), None)

    g.edges = [e for e in g.edges
               if not (e.type == "PRECEDES"
                       and (e.from_id in merged_ids or e.to_id in merged_ids))]

    if pred:
        g.create_edge("PRECEDES", pred.from_id, merged.id)
    if succ:
        g.create_edge("PRECEDES", merged.id, succ.to_id)

    # Remove merged nodes
    for node in nodes_to_merge:
        del g.nodes[node.id]

    renumber_level(g, level)


def split_node(g: Graph, level: str, index: int, at_child_index: int,
               heading_before: str = None, heading_after: str = None):
    """
    Split a node at at_child_index.
    Children [0, at_child_index) go to the first half.
    Children [at_child_index, end) go to the second half.
    """
    label = level.capitalize()
    nodes_map = get_nodes_by_level(g, level)
    if index not in nodes_map:
        raise ValueError(f"No {level} with index {index}")
    node = nodes_map[index]

    children = _get_ordered_children(g, node.id)
    if at_child_index < 1 or at_child_index >= len(children):
        raise ValueError(
            f"at_child_index {at_child_index} out of range (1..{len(children)-1})"
        )

    before = children[:at_child_index]
    after = children[at_child_index:]
    heading = node.properties.get("heading", "")

    node_before = g.create_node([label], {
        "heading": heading_before or heading,
        "index": index,
        "parse_indices": [index]
    })
    node_after = g.create_node([label], {
        "heading": heading_after or heading + " (cont.)",
        "index": index + 0.5,  # temporary; renumbered below
        "parse_indices": [index]
    })

    # Remove all old CONTAINS edges from node
    g.edges = [e for e in g.edges
               if not (e.type == "CONTAINS" and e.from_id == node.id)]

    # Assign children
    for i, child in enumerate(before, start=1):
        g.create_edge("CONTAINS", node_before.id, child.id, {"index": i})
        child.properties["index"] = i
    for i, child in enumerate(after, start=1):
        g.create_edge("CONTAINS", node_after.id, child.id, {"index": i})
        child.properties["index"] = i

    # Re-parent in parent node
    parent_edge = next(
        (e for e in g.edges if e.type == "CONTAINS" and e.to_id == node.id), None
    )
    if parent_edge:
        parent_id = parent_edge.from_id
        g.edges = [e for e in g.edges
                   if not (e.type == "CONTAINS"
                           and e.from_id == parent_id
                           and e.to_id == node.id)]
        g.create_edge("CONTAINS", parent_id, node_before.id, {"index": index})
        g.create_edge("CONTAINS", parent_id, node_after.id, {"index": index + 0.5})

    # Update PRECEDES at this level
    pred = next((e for e in g.edges
                 if e.type == "PRECEDES" and e.to_id == node.id), None)
    succ = next((e for e in g.edges
                 if e.type == "PRECEDES" and e.from_id == node.id), None)
    g.edges = [e for e in g.edges
               if not (e.type == "PRECEDES"
                       and (e.from_id == node.id or e.to_id == node.id))]

    if pred:
        g.create_edge("PRECEDES", pred.from_id, node_before.id)
    g.create_edge("PRECEDES", node_before.id, node_after.id)
    if succ:
        g.create_edge("PRECEDES", node_after.id, succ.to_id)

    # Stitch PRECEDES at child level across the split boundary
    if before and after:
        if not _precedes_exists(g, before[-1].id, after[0].id):
            g.create_edge("PRECEDES", before[-1].id, after[0].id)

    del g.nodes[node.id]
    renumber_level(g, level)


def apply_operations(g: Graph, ops: list):
    """Re-apply a list of operations to a graph (used on reload).

    Invalid ops are skipped with a warning rather than crashing startup.
    A stale curation.json (e.g. from before a volume add) should not make
    the application unlaunchable.
    """
    for i, op in enumerate(ops):
        try:
            if op["op"] == "merge":
                merge_nodes(g, op["level"], op["indices"], op["heading"])
            elif op["op"] == "split":
                split_node(g, op["level"], op["index"], op["at_child_index"],
                           op.get("heading_before"), op.get("heading_after"))
            elif op["op"] == "rename":
                rename_node(g, op["level"], op["index"], op["heading"])
        except Exception as e:
            print(f"WARNING: skipping invalid curation op [{i}] {op.get('op')}: {e}")


# --- helpers ---

def _get_ordered_children(g: Graph, parent_id: str) -> list:
    edges = [e for e in g.edges if e.type == "CONTAINS" and e.from_id == parent_id]
    children = [g.nodes[e.to_id] for e in edges if e.to_id in g.nodes]
    return sorted(children, key=lambda n: n.properties.get("index", 0))


def _precedes_exists(g: Graph, from_id: str, to_id: str) -> bool:
    return any(e for e in g.edges
               if e.type == "PRECEDES" and e.from_id == from_id and e.to_id == to_id)
