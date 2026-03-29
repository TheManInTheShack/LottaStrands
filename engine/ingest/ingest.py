"""
Ingest pipeline: takes parsed screenplay structure and builds the property graph.

Hierarchy: Corpus -> Scene -> Paragraph -> Sentence
Lexicon:   Sentence -[CONTAINS]-> Term  (with position, pos, raw form as edge properties)
"""

import sys
from pathlib import Path
from textblob import TextBlob

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from engine.graph.model import Graph


def ingest(parsed, config):
    g = Graph()

    # Corpus node
    corpus = g.create_node(['Corpus'], {
        'name': config['name'],
        'title': config['title'],
        'corpus_type': config['corpus_type']
    })

    # Term registry: normalized text -> Node
    terms = {}

    def get_or_create_term(word):
        key = word.lower()
        if key not in terms:
            terms[key] = g.create_node(['Term'], {'text': key})
        return terms[key]

    prev_scene_node = None

    for scene_data in parsed['scenes']:
        scene = g.create_node(['Scene'], {
            'heading': scene_data['heading'],
            'index': scene_data['index']
        })
        g.create_edge('CONTAINS', corpus.id, scene.id, {'index': scene_data['index']})
        if prev_scene_node:
            g.create_edge('PRECEDES', prev_scene_node.id, scene.id)
        prev_scene_node = scene

        prev_para_node = None

        for para_data in scene_data['paragraphs']:
            props = {
                'type': para_data['type'],
                'index': para_data['index'],
                'text': para_data['text']
            }
            if para_data['type'] == 'dialogue':
                props['speaker'] = para_data['speaker']

            para = g.create_node(['Paragraph'], props)
            g.create_edge('CONTAINS', scene.id, para.id, {'index': para_data['index']})
            if prev_para_node:
                g.create_edge('PRECEDES', prev_para_node.id, para.id)
            prev_para_node = para

            # Split paragraph text into sentences
            blob = TextBlob(para_data['text'])
            sentences = blob.sentences or [blob]

            prev_sent_node = None

            for s_idx, sentence in enumerate(sentences, start=1):
                sent_text = str(sentence).strip()
                if not sent_text:
                    continue

                sent = g.create_node(['Sentence'], {
                    'text': sent_text,
                    'index': s_idx
                })
                g.create_edge('CONTAINS', para.id, sent.id, {'index': s_idx})
                if prev_sent_node:
                    g.create_edge('PRECEDES', prev_sent_node.id, sent.id)
                prev_sent_node = sent

                # Connect sentence to term nodes via occurrence edges
                for pos_idx, (word, pos) in enumerate(TextBlob(sent_text).tags, start=1):
                    term = get_or_create_term(word)
                    g.create_edge('CONTAINS', sent.id, term.id, {
                        'position': pos_idx,
                        'pos': pos,
                        'raw': word
                    })

    # Lexicon node as a named container for all terms
    lexicon = g.create_node(['Lexicon'], {
        'name': config['name'],
        'term_count': len(terms)
    })
    for term_node in terms.values():
        g.create_edge('CONTAINS', lexicon.id, term_node.id)

    return g
