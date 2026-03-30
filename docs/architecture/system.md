# System Architecture

## Layers

```
┌─────────────────────────────────┐
│  Godot 4 UI (WebAssembly)       │  ← CurationView, CorpusMenu, Main
│  served by nginx                │
├─────────────────────────────────┤
│  FastAPI (Python)               │  ← routes: corpus, volumes, paragraphs, curate
│  uvicorn (dev) / gunicorn (prod)│
├─────────────────────────────────┤
│  Graph model (in-memory)        │  ← engine/graph/model.py
│  Curation operations            │  ← engine/curate/operations.py
│  Flat ingest                    │  ← engine/ingest/flat_ingest.py
├─────────────────────────────────┤
│  graph.json  |  curation.json   │  ← model/data/ and model/config/
└─────────────────────────────────┘
```

## Data flow

1. User pastes source text into New Volume form (Godot)
2. `POST /volumes` → `flat_ingest()` appends Volume to corpus in graph.json
3. User enters curation view; `GET /paragraphs` returns flat ordered list
4. User taps InsertStrip → `POST /curate/insert_marker` → splits scene at that paragraph
5. HierarchyMarker appears; user can remove it to merge scenes back
6. User saves → `POST /curate/save` writes graph_curated.json

## Key design choices
- [[decisions/001-flat-ingest]] — why flat ingest instead of auto-parse
- [[decisions/002-godot-ui]] — why Godot
- [[decisions/003-multi-volume]] — how volumes and shared semantic layer coexist

## Related
- [[graph-model]] — property graph structure
- [[hierarchy]] — narrative hierarchy and PLOT stages
- [[storage]] — file layout
