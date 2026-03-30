# LottaStrands
There's a lotta strands in the ol' Duder's head.

This is a generalized system for storing and analyzing knowledge about narratives, using the screenplay of The Big Lebowski as a primary example. The goal is to produce a **property graph** — a structured knowledge graph of nodes and edges with properties — that captures the full narrative in a queryable, extensible form. Other narratives (novels, series, comics, etc.) are equally valid inputs.

## About the name: Plotz / plotzed

The engine and product built on this system is called **Plotz** (website: [plotzed.com](https://plotzed.com)).

The name works on a few levels:

- **PLOT** is an acronym for the core procedure: **P**arse → **L**exicon → **O**ntology → **T**axonomy — the four stages by which raw narrative text becomes a structured, annotated knowledge graph.
- **Plot-Z** and **Plot-Zed** both suggest a *zero point* of a plot — the origin or coordinate anchor of the narrative space — which fits the graph-as-coordinate-system metaphor.
- **Plotz** is also a Yiddish word meaning to be overwhelmed to the point of collapse, which captures something true about the ambition of the project: to hold the full weight of a story all at once.

The working repo and corpus is **LottaStrands** (a Lebowski reference and a nod to the density of the graph). Plotz is the name of the broader product and site.

## Core goal: the knowledge graph
The primary artifact of this system is a property graph representing the narrative. Nodes are things (text units, characters, locations, events, terms, tags). Edges are relationships (`CONTAINS`, `PRECEDES`, `MENTIONS`, `OCCURS_AT`, `IS_A`, etc.). Both nodes and edges carry properties.

The graph is built in stages — parsed from source, structured into a hierarchy, enriched with vocabulary and annotation — and ultimately intended for use with Neo4j, though the initial representation is a Python dict of nodes and an adjacency list serialized to JSON.

## Workflow
### Stage 1: Parse
Convert the raw source (screenplay, novel, etc.) into a common hierarchical JSON format, according to the hierarchy configuration for that corpus type.

### Stage 2: Ingest
Transform the parsed hierarchy into the property graph structure. Build the lexicon from sentence-level text. Output the graph as JSON and optionally as human-readable Excel.

### Stage 3: Interaction
A Godot-based interface for visualizing and interacting with the graph — navigating the narrative hierarchy, exploring relationships, and annotating nodes with ontological tags.

### Stage 4: Analysis
Derived views and outputs from the graph: timelines, location maps, character networks, linguistic analyses, and other context views.


## Narrative hierarchy
The hierarchy is a **configurable** ordered set of levels, defined per corpus type. The sentence is the atomic text unit — the lowest level of the hierarchy proper. Below the sentence, unique terms form the lexicon (not individual word occurrence nodes). Different media use different level names:

- Film trilogy: `Corpus → Series → Film → Scene → Paragraph → Sentence`
- Novel series: `Corpus → Series → Novel → Chapter → Section → Paragraph → Sentence`
- Comic: `Corpus → Series → Issue → Page → Panel → Balloon → Sentence`

The default hierarchy (used here for The Big Lebowski):
- Corpus
- Volume
- Scene
- Paragraph
- Sentence

Each level node connects downward via `CONTAINS` edges and sideways via `PRECEDES`/`FOLLOWS` edges to siblings, encoding both structure and sequence.

## Vocabulary - Lexicon, Ontology, Taxonomy
These three layers sit on top of the hierarchy and together form the semantic enrichment of the graph:

- **Lexicon** — the raw terms as nodes, one per unique word form (e.g. `"dude"`, `"rug"`, `"walter"`). Sentence nodes connect to term nodes via `CONTAINS` edges carrying occurrence properties (position, POS tag, raw form).
- **Ontology** — edges that assert meaning and relationships between terms and other nodes (e.g. `"dude" IS_A CHARACTER`, `"rug" BELONGS_TO SETTING`, `"walter" KNOWS "dude"`). This is where human annotation enriches the graph.
- **Taxonomy** — the classification structure itself: the schema of tag types and categories (e.g. `CHARACTER`, `SETTING`, `OBJECT` as nodes belonging to higher category nodes). The taxonomy defines what kinds of ontological assertions are valid.

The taxonomy is the *schema* of tags. The ontology is the *application* of those tags to the lexicon. The lexicon is the raw material. All three live in the same graph as different node and edge types.

## Taxonomic categories
The basic elements can be built up with different kinds of tags that can be combined to create major substructures, each of which interacts with each other and could be analyzed on its own in a myriad of different ways.  The idea here is to allow these major items to become formalized into known kinds of useful structures that are common across all/most narratives.

### Timelines
All narratives have at least ONE timeline, which can be said to be the indexing of the original text - the sentences were said in that order.  Anything past abstracted poetry will also have a chronological timeline, which might be the implicit 'real' timeline of history, or one or more fictional timelines that might relate to each other or real history in various ways. A formal way of keeping these timelines and mapping between them is part of this.

#### Calendar/Almanac
Any timeline can be divided into its own hierarchical index - we generally use the whole year-month-day-hour-minute-second thing, but this might be anything. In this structure, the 'calendar' is the system itself, and the 'almanac' are references to individual units within that calendar - so the calendar is the idea of June being a month of a year and having 30 days, and the almanac has things like "June 21, 1986".

#### Events
Generally narratives are made up of actions or events, whether conversation topics or individual shots in a battle scene - any given timeline is made up of these, in fact, laid on top of the calendar.

### Locations
Settings for a narrative may be simple or variegated; in any case, the spatial relationship is something looked at separately from timelines.

### Characters
The dramatis personae is its own list, with sets of attributes that make sense for characters.

### Elements
Stories are full of 'things' - dogs, knives, jewels, corporations, movies, etc. There may be any number of thes categories relevant to a story or not; collectively they can be thought of as the elements of a story though. 
- Flora
- Fauna
- Food
- Objects
- Titles
- Entities
- Organizations
- Jobs
- Exclamations
