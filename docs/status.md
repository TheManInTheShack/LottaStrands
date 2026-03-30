---
updated: 2026-03-30
---

# Plotz / LottaStrands — Current Status

## What's working
- FastAPI backend running with `python dev.py`; serves on `:8000`
- `GET /corpus` — returns corpus + volume list
- `GET /paragraphs` — flat ordered list of all paragraphs with scene context
- `POST /volumes` — appends a new volume to the corpus via flat ingest (blank-line paragraph split); resets curation log
- `POST /volumes/delete` — removes a volume subgraph by BFS from volume node
- `POST /curate/insert_marker` — splits containing scene at a given paragraph ID
- `POST /curate/merge|split|rename` — standard curation operations
- Godot UI running in editor; main screens: CorpusMenu, Main (curation)
- CorpusMenu: volume list with marquee scroll on hover, delete with confirmation, New Volume form
- New Volume form: stays open with status feedback during API call; closes on success
- CurationView: scrollable paragraph cards with InsertStrips and HierarchyMarkers

## What's not yet verified
- End-to-end New Volume creation (just fixed curation double-replay bug — needs testing)
- Multi-volume append (second volume should appear in list alongside first)
- InsertStrip → insert_marker → scene split flow (UI built, needs full test)
- HierarchyMarker remove → merge scenes (UI built, needs test)

## Known issues / next up
- No file picker for source text (paste-only in New Volume form for now)
- Curation ops are corpus-wide; per-volume scoping is future work
- `model/data/parsed.json` is a dead artifact from old screenplay parse; can be deleted
- Godot web export not yet configured
- DigitalOcean deployment not started

## Active branch
`claude/analyze-repo-NPR0L` — pull this on VM to get latest changes
