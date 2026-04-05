# Methodology

## Hierarchy Levels

Track things at different levels so that quantitative techniques can be applied against each population:

| Level | Description |
|---|---|
| Corpus | The whole collection |
| Volume | One source text |
| Chapter | Major division within a volume |
| Scene | Structural unit created by curation |
| Paragraph | The base unit of flat ingest |
| Sentence | Sub-paragraph granularity (future) |
| Word | Lexical unit |

Each level is a list of text blobs. Aggregate or filter across any combination.

## Fragmentization

A possible division layer: separating spoken dialogue (text in quotes) from pure narration. Relevant for works with heavy dialogue like screenplays.

## Multi-Level Analysis

With granular views (sentences, words), you can aggregate up to arbitrary groups — mixing and matching across levels. Tag individual sentences thematically, group paragraphs into artificial scenes, etc.

## Plotz Mapping

The Plotz graph hierarchy maps these levels to nodes connected by CONTAINS edges:

```
Corpus → Volume → Scene → Paragraph
```

Additional levels (Chapter, Shot, Sentence) are supported in the hierarchy config and can be inserted via curation. See [[architecture/graph-model]].
