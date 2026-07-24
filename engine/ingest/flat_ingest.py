"""
Flat ingest: takes raw text and adds a Volume to the property graph.

If an existing Graph is provided (corpus already has volumes), the new volume
is appended under the existing Corpus node. If no graph is given, a fresh one
is created with a new Corpus.

Hierarchy added: Corpus -> Volume -> Scene ("FULL TEXT") -> Paragraphs
"""

from datetime import datetime, timezone

from engine.graph.model import Graph


def flat_ingest(text: str, config: dict, existing_graph: Graph = None) -> Graph:
    if existing_graph is not None and existing_graph.nodes:
        g = existing_graph
        corpus = next(iter(g.get_nodes_by_label("Corpus")), None)
        if corpus is None:
            corpus = g.create_node(["Corpus"], {
                "name": "lottastrands",
                "title": "LottaStrands",
                "corpus_type": "mixed",
            })
    else:
        g = Graph()
        corpus = g.create_node(["Corpus"], {
            "name": "lottastrands",
            "title": "LottaStrands",
            "corpus_type": "mixed",
        })

    volume = g.create_node(["Volume"], {
        "title": config["title"],
        "type": config.get("type", "unknown"),
        "year": config.get("year"),
        "authors": config.get("authors", []),
        "format": config.get("format", "plain text"),
        "url": config.get("url", ""),
        "added_at": datetime.now(timezone.utc).isoformat(),
    })
    g.create_edge("CONTAINS", corpus.id, volume.id)

    scene = g.create_node(["Scene"], {"heading": "FULL TEXT", "index": 1})
    g.create_edge("CONTAINS", volume.id, scene.id, {"index": 1})

    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    prev = None
    for i, block in enumerate(blocks, start=1):
        para = g.create_node(["Paragraph"], {"text": block, "index": i, "type": "text"})
        g.create_edge("CONTAINS", scene.id, para.id, {"index": i})
        if prev:
            g.create_edge("PRECEDES", prev.id, para.id)
        prev = para

    print(f"Flat ingest: added '{config['title']}' — {len(blocks)} paragraphs")
    return g


def replace_volume_text(g: Graph, volume_id: str, text: str) -> None:
    """Remove all descendant nodes of a Volume and re-ingest new text.

    The Volume node itself is preserved (title, type, authors, etc. unchanged).
    Called by the update endpoint when source text is replaced; caller must
    reset curation.json afterward.
    """
    to_delete: set = set()
    queue = [volume_id]
    while queue:
        nid = queue.pop()
        for edge in g.get_edges_from(nid):
            if edge.type == "CONTAINS" and edge.to_id not in to_delete:
                to_delete.add(edge.to_id)
                queue.append(edge.to_id)

    g.edges = [e for e in g.edges
               if e.from_id not in to_delete and e.to_id not in to_delete]
    for nid in to_delete:
        del g.nodes[nid]

    scene = g.create_node(["Scene"], {"heading": "FULL TEXT", "index": 1})
    g.create_edge("CONTAINS", volume_id, scene.id, {"index": 1})

    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    prev = None
    for i, block in enumerate(blocks, start=1):
        para = g.create_node(["Paragraph"], {"text": block, "index": i, "type": "text"})
        g.create_edge("CONTAINS", scene.id, para.id, {"index": i})
        if prev:
            g.create_edge("PRECEDES", prev.id, para.id)
        prev = para

    print(f"replace_volume_text: '{volume_id}' — {len(blocks)} paragraphs")
