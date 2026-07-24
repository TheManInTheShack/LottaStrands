---
updated: 2026-07-24
status: open
---

# Engine/Corpus Audit — Findings for the Plotz Extraction

## Purpose

LottaStrands is being split: the reusable **Plotz engine** (backend + most of
the Godot UI) is moving out into its own repo, and this repo becomes one of
several **corpus example** repos that consume it. `docs/howto/new-model-repo.md`
already describes the target end-state ("engine as a package," thin shell
repos). This doc is a pre-migration audit — what's already lined up for that
split, and what will bite whoever does it if it's not fixed first.

Written on the laptop side after a documentation once-over requested by the
user, specifically to hand off to the instance doing the actual extraction.

---

## 1. Critical: the "engine" is not actually corpus-agnostic yet

The howto's own "Engine (do not change per-corpus)" list includes all of
`engine/`. That's not true today — two files bake in the LottaStrands identity
directly instead of reading it from config:

- **`engine/ingest/flat_ingest.py`** (lines ~21-25 and ~28-32) — when a new
  `Corpus` node is created, `flat_ingest()` hardcodes:
  ```python
  corpus = g.create_node(["Corpus"], {
      "name": "lottastrands",
      "title": "LottaStrands",
      "corpus_type": "mixed",
  })
  ```
  in *both* branches (fresh graph and existing-graph-with-no-Corpus-node),
  even though `model/config/hierarchy.json` already carries `name`/`title`/
  `corpus_type` fields for exactly this purpose. The function receives a
  `config` dict param but never uses it to source these three values —
  `hierarchy.json` and the actual graph disagree by construction.
- **`engine/api/app.py`** — `FastAPI(title="LottaStrands Engine")` and the
  health check body (`{"service": "LottaStrands Engine"}`) are also literal.

**Fix before or during extraction:** thread `hierarchy.json`'s `name`/`title`/
`corpus_type` into `flat_ingest()` (it already takes a `config` arg — likely
just needs to load/pass `hierarchy.json` in, or accept corpus fields
alongside the volume config), and parameterize the FastAPI app title/service
name the same way. Otherwise every new corpus repo silently creates graphs
internally labeled "lottastrands" regardless of its own hierarchy.json.

## 2. `docs/howto/new-model-repo.md` Step 4 shows the wrong schema

The doc's example `hierarchy.json`:
```json
{
  "corpus": "yourcorpusname",
  "levels": ["scene", "paragraph"]
}
```
The real file (`model/config/hierarchy.json`) is:
```json
{
  "name": "lottastrands",
  "title": "LottaStrands",
  "corpus_type": "mixed",
  "levels": ["corpus", "volume", "scene", "shot", "paragraph", "sentence"]
}
```
Different key names (`corpus` vs. `name`+`title`+`corpus_type`) and a
different level list. Anyone forking the repo and following the howto
literally would produce a config the code doesn't actually expect. Fix the
example to match reality — or better, fix once §3 below is resolved, so
there's one canonical schema to document.

## 3. The hierarchy/level system is documented three inconsistent ways

`docs/dashboard.md` already flags `architecture/hierarchy.md` as "(to
write)" — this is why it's needed. Three sources currently disagree on what
the levels even are:

| Source | Levels |
|---|---|
| `docs/concepts/methodology.md` table | Corpus, Volume, Chapter, Scene, Paragraph, Sentence, Word |
| `docs/architecture/graph-model.md` diagram | Corpus → Volume → Scene → Paragraph → Sentence *(future)* → Term *(future)* |
| actual `model/config/hierarchy.json` | corpus, volume, scene, **shot**, paragraph, sentence |

Nobody agrees whether "Chapter" or "Shot" is real. Since the level system is
presumably central to whatever "data model" gets extracted as the core, this
should get one authoritative answer — written as `docs/architecture/
hierarchy.md` — before the schema is locked into a package boundary.

## 4. Other missing docs (linked via `[[wikilinks]]`, files don't exist)

- `docs/architecture/hierarchy.md` — see §3
- `docs/workflow/plot-stages.md`
- `docs/workflow/curation-flow.md`
- `docs/concepts/lexicon.md`, `docs/concepts/ontology.md`, `docs/concepts/taxonomy.md`
  (linked from `concepts/introduction.md`)
- Related: `graph-model.md`'s edge-type table mentions `IS_A` / "Ontology
  assertion" but its node-label table only lists `Lexicon` and `Taxonomy`,
  not `Ontology` — same underlying gap.

## 5. Staleness (low priority, but will confuse whoever picks this up)

- `docs/status.md` still says "Active branch: `claude/analyze-repo-NPR0L` —
  pull this on VM to get latest changes." That branch was merged to `main`
  on the laptop side; status.md wasn't updated after.
- `docs/sessions/_index.md` only lists the 2026-03-30 session; the
  2026-03-31 session file exists but was never added to the index.
- `docs/architecture/system.md`'s layer diagram labels the Godot UI layer
  with a scene called "Main" — that scene was renamed to `CurationScreen`
  in the same merge.

## What's already solid (don't rebuild this)

The engine/corpus conceptual split itself is well-formed and directly
usable: `CLAUDE.md`'s "Engine layout" / "Godot layout" sections, ADR 002
(Godot as UI layer), ADR 003 (multi-volume corpus model), and the flat-ingest
decision (ADR 001) are all internally coherent and match the code as of this
audit. `docs/howto/new-model-repo.md` is a legitimate fork procedure today
(modulo §2) and already anticipates the package-extraction end state in its
closing section — that's the plan to execute against, not something to
redesign from scratch.

## Suggested order of operations

1. Write `docs/architecture/hierarchy.md` — pin down the real level list
   (resolve §3) before anything downstream depends on it.
2. Fix `flat_ingest.py` / `app.py` hardcoding (§1) so the engine is actually
   corpus-agnostic in practice, not just in intent.
3. Fix the `new-model-repo.md` schema example (§2) to match.
4. Then proceed with the actual extraction per `new-model-repo.md`'s
   "Future: engine as a package" section.
5. Sweep the staleness items in §5 whenever convenient — cosmetic, not
   blocking.
