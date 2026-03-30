# ADR 003 — Multi-volume corpus model

## Context
The initial implementation created a fresh graph for each volume (replacing the previous one). Needed to support multiple volumes coexisting in one corpus.

## Decision
All volumes live as sibling nodes under a single Corpus node in one `graph.json`. The shared semantic layer (Lexicon, Ontology, Taxonomy) also lives in the same graph as non-Volume-parented nodes.

## Structure
```
Corpus ("LottaStrands")
  ├─ Volume: "The Big Lebowski"
  │    └─ Scene → Paragraphs
  ├─ Volume: "No Country for Old Men"
  │    └─ Scene → Paragraphs
  └─ [future] LexiconNode, TaxonomyNode ...  ← shared; not under any Volume
```

Deleting a volume: BFS traversal from the Volume node removes only its descendants. Corpus and shared nodes are never touched.

## Curation log reset on volume add
When a volume is added, `curation.json` is reset to `[]`. The in-memory curated graph becomes the new raw baseline in `graph.json`. This prevents the double-replay problem (loading a graph that already has operations applied, then applying them again).

**Trade-off:** individual curation operations cannot be undone after a volume add. Per-volume curation scoping is the correct long-term solution; not yet implemented.

## Naming
- **Corpus** is implicit — the app instance IS the corpus ("LottaStrands"). Not shown in UI.
- Users only work at the Volume level and below.
