"""
Flat ingest: takes raw text and builds a minimal property graph.

Hierarchy: Corpus -> Volume -> Scene (one) -> Paragraph (one per blank-line block)

No structural classification is performed. All paragraphs sit under a single
"FULL TEXT" scene. The user refines the structure through curation.
"""

from engine.graph.model import Graph


def flat_ingest(text: str, config: dict) -> Graph:
    g = Graph()

    corpus = g.create_node(['Corpus'], {
        'name': config['name'],
        'title': config['title'],
        'corpus_type': config.get('type', 'unknown')
    })

    volume = g.create_node(['Volume'], {
        'title': config['title'],
        'type': config.get('type', 'unknown'),
        'year': config.get('year'),
        'authors': config.get('authors', []),
        'format': config.get('format', 'plain text'),
        'url': config.get('url', '')
    })
    g.create_edge('CONTAINS', corpus.id, volume.id)

    scene = g.create_node(['Scene'], {
        'heading': 'FULL TEXT',
        'index': 1
    })
    g.create_edge('CONTAINS', volume.id, scene.id, {'index': 1})

    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]

    prev = None
    for i, block in enumerate(blocks, start=1):
        para = g.create_node(['Paragraph'], {
            'text': block,
            'index': i,
            'type': 'text'
        })
        g.create_edge('CONTAINS', scene.id, para.id, {'index': i})
        if prev:
            g.create_edge('PRECEDES', prev.id, para.id)
        prev = para

    print(f"Flat ingest: {len(blocks)} paragraphs")
    return g
