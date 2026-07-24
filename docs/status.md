---
updated: 2026-03-31
---

# Plotz / LottaStrands — Current Status

## What's working
- FastAPI backend running with `python dev.py`; serves on `:8000`
- `GET /corpus` — returns corpus + volume list
- `GET /paragraphs` — flat ordered list of all paragraphs with scene context
- `POST /volumes` — appends a new volume to the corpus via flat ingest; resets curation log
- `POST /volumes/delete` — removes a volume subgraph by BFS from volume node
- `POST /curate/insert_marker` — splits containing scene at a given paragraph ID
- `POST /curate/merge|split|rename` — standard curation operations
- Godot UI: PlotZIntro → TitleCard → CorpusMenu → CurationScreen flow wired
- PlotZIntro: PLOT word sequence animation (engine-level, reusable)
- TitleCard: LOTTA STRANDS corpus-specific title (swap per repo)
- CorpusMenu: volume list with marquee scroll, delete with confirmation, New Volume form
- New Volume form: opaque overlay, waits for API response before closing, shows errors inline
- CurationScreen: header bar + full-width CurationView
- CurationView: scrollable paragraph cards with InsertStrips and HierarchyMarkers
- Documentation vault: CLAUDE.md, docs/, /wrap command, SessionStart hook

## What's not yet verified (needs test on VM)
- End-to-end New Volume creation (curation double-replay bug fixed — needs confirmation)
- Multi-volume append (second volume alongside first)
- InsertStrip → insert_marker → scene split flow
- HierarchyMarker remove → merge scenes flow

## Known issues / next up
- No file picker for source text (paste-only for now)
- Curation ops are corpus-wide; per-volume scoping is future work
- `model/data/parsed.json` is a dead artifact from old screenplay parse; can be deleted
- Font for "LOTTA STRANDS" in TitleCard is placeholder (Impact italic); swap a .ttf into `godot/fonts/` when ready
- Engine/corpus separation is structural intent but not yet physically split into separate packages
- Godot web export not yet configured
- DigitalOcean deployment not started

## Active branch
`claude/analyze-repo-NPR0L` — pull this on VM to get latest changes

## Scene chain
`PlotZIntro` → `TitleCard` → `CorpusMenu` → `CurationScreen`
