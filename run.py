"""
Top-level runner for the narrative knowledge graph pipeline.

Usage:
    python run.py

Reads:  model/config/hierarchy.json
        model/source/<source_file>

Writes: model/data/parsed.json   (intermediate parse output)
        model/data/graph.json    (property graph)
"""

import json
import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root))

from engine.parse.screenplay import parse_screenplay
from engine.ingest.ingest import ingest


def main():
    config_path = root / 'model' / 'config' / 'hierarchy.json'
    with open(config_path) as f:
        config = json.load(f)

    source_path = root / 'model' / 'source' / config['source']['file']
    output_dir = root / 'model' / 'data'
    output_dir.mkdir(exist_ok=True)

    print(f"Source: {source_path.name}")

    print("\nStage 1: Parsing...")
    parsed = parse_screenplay(str(source_path))
    parse_output = output_dir / 'parsed.json'
    with open(parse_output, 'w') as f:
        json.dump(parsed, f, indent=2)
    print(f"  {parsed['scene_count']} scenes -> {parse_output}")

    print("\nStage 2: Ingesting...")
    graph = ingest(parsed, config)
    graph_output = output_dir / 'graph.json'
    graph.save(str(graph_output))


if __name__ == '__main__':
    main()
