# ADR 001 — Flat ingest over automated parse

## Context
The original approach was an automated screenplay parser that classified each line by indentation and keyword patterns (scene headings, shot openers, stage directions, dialogue). This produced a structured hierarchy directly.

## Problem
Edge cases were unpredictable and required significant per-source tweaking:
- "CRANE JACKSON'S FOUNTAIN STREET THEATER" — misclassified as a shot direction
- "A HIGHWAY SIGN: SIMI VALLEY ROAD" — misclassified as a scene heading
- Line breaks mid-sentence in source created false positives
- Every new source type (novel, comic) would need its own classifier

Every automated classification decision required human review anyway. The parse was doing work that couldn't be trusted.

## Decision
Replace the parse-first approach with:
1. **Flat ingest**: entire text → one scene → paragraphs split by blank lines; no classification
2. **Human curation**: user inserts hierarchy markers interactively via the Godot UI

The old `engine/parse/screenplay.py` is kept as a reference/archive but is not in the active workflow.

## Consequences
- The curation UI becomes the primary work surface (CurationView, InsertStrip, HierarchyMarker)
- Structure is always correct because the human creates it
- Different source types are handled uniformly — the same ingest + curation flow works for any text
- Automated parse shortcuts can be explored as supplements later (not replacements)
