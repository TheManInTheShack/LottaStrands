# LottaStrands / Plotz — Project Briefing

> **Plotz** is a context layering engine for narrative text.

> **Session start:** read `docs/status.md` and the most recent `docs/sessions/YYYY-MM-DD.md`.
> Update both when significant things are decided or built.

## What this is
**Plotz** (plotzed.com) is a narrative knowledge graph engine.
**PLOT** = Parse → Lexicon → Ontology → Taxonomy — the four stages of building a structured graph from raw narrative text.

This repo, **LottaStrands**, is the working instance. The Big Lebowski screenplay is the primary example corpus. Other narrative forms (novels, comics, series) are equally valid.

The end artifact is a **property graph**: nodes and edges with properties, Neo4j-compatible, initially stored as JSON.

## Stack
| Layer | Tech |
|---|---|
| Backend API | Python FastAPI + uvicorn (dev) / gunicorn (prod) |
| Frontend | Godot 4.x → WebAssembly export |
| Storage | `model/data/graph.json` → Neo4j (future) |
| Serving | nginx (static Godot export + reverse proxy to API) |
| Deployment | DigitalOcean |

## Key concepts and naming
- **Corpus** = the whole collection; implicit, always named "LottaStrands"; never shown in UI
- **Volume** = one source text the user adds (screenplay, novel, etc.)
- **Scene / Paragraph** = structural hierarchy within a volume; created by user via curation markers
- **Lexicon / Ontology / Taxonomy** = shared semantic layer across all volumes; future work

## Data model conventions
- `model/data/graph.json` — full working graph (all volumes + future lex/ont/tax)
- `model/config/curation.json` — log of curation operations; **reset when a volume is added** (the saved graph is already the curated state; avoids double-replay on reload)
- `model/config/hierarchy.json` — corpus-level config only (levels list, corpus name)
- Source texts live in `model/source/`

## UI conventions (Godot)
- No right-click menus; no hover-only interactions — phone/tablet is the real use case
- Minimum 44px touch targets
- InsertStrip pattern: tap strip between paragraph cards to insert hierarchy markers
- `÷` symbol for insert strips; `×` for remove/delete actions

## GDScript conventions
- Always use explicit types; never rely on `:=` inference from `Dictionary.get()` or other Variant sources
- `Dictionary.get()` always returns Variant — type the receiving variable explicitly: `var x: String = dict.get("key", "")`
- Prefer `var x: Variant = dict.get("key")` over untyped `var x = dict.get("key")` when the value may be null
- Warn the user if a pattern would produce Variant inference warnings in strict mode

## Engine layout
```
engine/
  graph/model.py          Node, Edge, Graph classes; JSON save/load
  ingest/flat_ingest.py   Appends a Volume to existing corpus from raw text
  curate/operations.py    merge_nodes, split_node, rename_node, apply_operations
  api/
    app.py                FastAPI app; loads state on startup
    state.py              In-memory graph; load/reload/add_operation
    routes/
      graph.py            GET /corpus, /scenes, /paragraphs
      volumes.py          POST /volumes, POST /volumes/delete
      curate.py           POST /curate/merge|split|rename|insert_marker|save|reload
    models.py             Pydantic request models
```

## Godot layout
```
godot/
  autoloads/
    API.gd                HTTP layer; _http_get/_http_post; one node per request
    AppState.gd           Signals + state; UI reads from here, never calls API directly
  scenes/
    PlotZIntro            Engine-level opening: PLOT word sequence → PLOTZ → TitleCard (reusable)
    TitleCard             Corpus-specific title screen: "LOTTA STRANDS" → CorpusMenu (swap per repo)
    CorpusMenu            Entry screen; volume list with marquee scroll + delete; New Volume form
    CurationScreen        Curation screen; header bar + full-width CurationView
    CurationView          Scrollable paragraph cards with InsertStrips and HierarchyMarkers
    ParagraphCard         Single paragraph display
    InsertStrip           Tap target between cards to insert scene boundary
    HierarchyMarker       Colored rule showing existing scene boundary (removable)
    VolumeListItem        Volume row with marquee scroll on hover + delete button
```

## Code hygiene
After a significant batch of changes, prompt the user to do a cleanup pass:
- Dead files (scenes, scripts, assets no longer referenced)
- Stale names (files whose names no longer reflect their purpose)
- Dead artifact data files in `model/data/` or `model/source/`
- Orphaned routes or API endpoints with no UI callers

The user prefers a garbage-free codebase. Raise it proactively; don't wait to be asked.

## Run locally
```bash
python dev.py        # FastAPI on :8000 with reload
# Then open Godot project and hit Play
```
