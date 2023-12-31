# LottaStrands
There's a lotta strands in the ol' Duder's head.

This is an examination of the script to The Big Lebowski, as an example of a generalized system for analyzing stories from a data-oriented perspective.

## Workflow
### Stage 1: Parse
This is different for each project, but the idea is to take whatever the starting form and put it into a common hierarchical format

### Stage 2: Ingest
Regardless of the pre-parse origin, this takes that output and reconfigures it as a series of tables, saved in two Excel files for direction interaction (though this will eventually become little sql databases).  One of the output documents is an intermediate 'cleaning' stage, allowing pruning and editing of the original input.  The other output is a 'narrative map' which shows a viewpoint of each level of the hierarchy.

### Stage 3: Interaction
This is an interactive dashboard system, built in Python with Plotly/Dash, that reads the ingested data from step 2 and allows organized tagging and annotation of the hierarchical data, allowing enrichment.

### Stage 4: Analysis
As an adjunct to the same dashboard, there are other views that act as outputs - various ways of looking at timelines, settings and linguistic analyses.


## Narrative hierarchy
The hierarchy is basically a way of precisely indexing each bit of the subject - we think of the 'sentence' as the base level - from there we can roll it up into 'paragraphs', 'sceneces' and 'chapters'. Since there might be multiple inputs making up a subject, we think of each of those as a 'volume', and the entire thing is the 'corpus'.  From the base sentence level we can also drill down into 'words', which have along with them part of speech and are the bottom of the hierarchy.  For different subjects, one or more levels might not be necessary - that's fine, it's just down to what the parsing steps does, but the whole hierarchy will be treated in the formal system.
- Corpus
- Volume
- Chapter
- Scene
- Paragraph
- Sentence
- Word

## Vocabulary - Lexicon, Ontology, Taxonomy
From the words level, we can aggregate to a list of the unique terms and look at them as the basis of a vocabulary system - this is the 'lexicon'.  The items in the lexicon can be tagged individually to attach appropriate meanings - this the 'ontology'.  The confluence of the tags in the ontology is a final structure on top of this, that's the 'taxonomy'.  All of this part makes up the basis of any advanced analysis - it's the building blocks which are derived from (and could reconstruct) the text.

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
