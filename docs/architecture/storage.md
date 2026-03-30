# Storage Layout

```
model/
  data/
    graph.json          ← full working corpus graph (all volumes + future lex/ont/tax)
    graph_curated.json  ← written on POST /curate/save; snapshot of curated state
    parsed.json         ← DEAD ARTIFACT from old screenplay auto-parse; safe to delete

  config/
    hierarchy.json      ← corpus-level config: name, title, level list
    curation.json       ← log of curation operations; [] = clean baseline
                           RESET on every volume add (bake-in pattern; see below)

  source/
    the_big_lebowski.txt ← source text for the primary example volume
    parse_issues.md      ← notes from old parse debugging; historical
    corrections.md       ← corrections made to source; historical
```

## The bake-in pattern

`state.load()` loads `graph.json` and then replays `curation.json` operations.

When a new volume is added:
1. `state.get_graph()` returns the already-curated in-memory graph
2. `flat_ingest()` adds the new Volume to it
3. The result is saved as `graph.json` — this is the curated state baked in
4. `curation.json` is reset to `[]`
5. `state.load()` loads the graph (already fully curated) with no ops to replay

This avoids double-application of operations. Past curation work is preserved (it's in graph.json). Future curation starts fresh from the new baseline.

**Implication:** once a volume is added, previous individual curation operations cannot be individually undone. This is a known limitation; per-volume curation scoping is future work.

## Future: per-volume source storage

Currently all source texts share `model/source/`. As volumes accumulate, a per-volume folder structure makes sense: `model/source/{volume_id}/source.txt`. Not yet implemented.
