# Property Graph Model

## Structure

Every entity is a **Node** (id, labels list, properties dict).
Every relationship is an **Edge** (id, type, from_id, to_id, properties dict).
The graph is a dict of nodes by id plus a list of edges.

Neo4j-compatible by design — migrating from JSON to Neo4j is a matter of import format, not structural change.

## Node labels in use

| Label | Description |
|---|---|
| `Corpus` | Root node; one per instance; always "LottaStrands" |
| `Volume` | One source text (screenplay, novel, etc.) |
| `Scene` | A named division within a volume; initially just "FULL TEXT" |
| `Paragraph` | One blank-line-separated block of text |
| `Lexicon` | *(future)* unique term node |
| `Taxonomy` | *(future)* classification node |

## Edge types in use

| Type | Meaning |
|---|---|
| `CONTAINS` | Parent → child in hierarchy; carries `index` property |
| `PRECEDES` | Sequential ordering between siblings |
| `MENTIONS` | *(future)* Paragraph → Lexicon term occurrence |
| `IS_A` | *(future)* Ontology assertion |

## Hierarchy

```
Corpus
  └─ Volume (N)
       └─ Scene (N per volume; starts as one "FULL TEXT")
            └─ Paragraph (N; split by blank lines on ingest)
                 └─ Sentence (future; TextBlob splitting)
                      └─ Term (future; unique per corpus; Lexicon)
```

Scenes are created by the user inserting markers during curation. The flat ingest creates exactly one scene per volume.

## Shared semantic layer

Lexicon, Ontology, and Taxonomy nodes are NOT children of any Volume. They sit as peers of the Volume nodes under the Corpus, or as standalone nodes connected by semantic edges. This is what makes them naturally shared across all volumes.

## Related
- [[system]] — how the graph fits in the overall architecture
- [[hierarchy]] — the configurable level system
