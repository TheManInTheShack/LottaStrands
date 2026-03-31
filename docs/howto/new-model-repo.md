# How to Set Up a New Model Repo

A **model repo** is a corpus-specific instance of the Plotz engine — one source text (or collection), one Godot project, one running API. This guide covers what to clone, what to change, and what to wire by hand.

> **Status note:** Engine and corpus are currently co-located in this repo. Physical separation into a reusable engine package is future work. Until then, fork this repo and strip the corpus-specific pieces as described below.

---

## Concepts

| Term | Meaning |
|---|---|
| **Engine** | Reusable Plotz code: Python backend, most Godot scenes, autoloads |
| **Corpus** | The model-specific layer: source text, graph data, TitleCard, repo name |
| **Volume** | One source text added via the UI (screenplay, novel, etc.) |

---

## Step 1 — Fork and rename

Fork `LottaStrands` or clone it fresh. Rename the repo to match your corpus — e.g. `BigSleep`, `MobyCorpus`, whatever.

Update the Godot project name in `godot/project.godot`:

```ini
config/name="YourCorpusName"
config/description="Brief description of what this models"
```

---

## Step 2 — Replace the TitleCard

`godot/scenes/TitleCard.gd/.tscn` is the only corpus-specific Godot scene. Edit both files.

**In `TitleCard.tscn`**, change the two label text values:

```
text = "YOUR CORPUS TITLE"        # TitleLine1 — big, wild font
text = "your subtitle here"       # TitleLine2 — monospace, small
```

**In `TitleCard.gd`**, the only corpus-specific value is the destination scene — it should already point to `CorpusMenu.tscn`, which is correct for all instances.

`PlotZIntro` is engine-level. Do not change it. It chains to `TitleCard` automatically.

**Optional — custom font for TitleLine1:**

1. Download a `.ttf` (Boogaloo, Righteous, Monoton, or Creepster from Google Fonts work well)
2. Drop it into `godot/fonts/` (create the folder)
3. In `TitleCard.tscn`, replace the `SystemFont_title` sub-resource with:

```ini
[ext_resource type="FontFile" path="res://fonts/YourFont.ttf" id="FontFile_title"]
```

And on the `TitleLine1` node:

```ini
theme_override_fonts/font = ExtResource("FontFile_title")
```

---

## Step 3 — Clear the corpus data

The cloned repo will have LottaStrands graph data. Start clean:

```bash
rm -f model/data/graph.json
rm -f model/config/curation.json
# Leave model/config/hierarchy.json in place — edit it instead (see Step 4)
```

Also delete any source texts that came with the clone:

```bash
rm -f model/source/*
```

---

## Step 4 — Update hierarchy config

`model/config/hierarchy.json` contains corpus-level configuration. At minimum update the name:

```json
{
  "corpus": "yourcorpusname",
  "levels": ["scene", "paragraph"]
}
```

The corpus name is internal/machine-readable. Keep it lowercase, no spaces.

---

## Step 5 — Update CLAUDE.md

Edit `CLAUDE.md` at the repo root. Change:

- The repo/corpus name in the header and **Key concepts** section
- The `TitleCard` entry in the **Godot layout** block to reflect your title text
- Any project-specific notes

This is what future Claude instances will read to understand the project. Keep it accurate.

---

## Step 6 — Update docs/

Replace the documentation vault content for your corpus:

- `docs/status.md` — clear to a fresh state; mark everything as unverified
- `docs/sessions/` — delete prior session notes; start fresh
- `docs/dashboard.md` — update the corpus name at the top

Architecture and decision docs (`docs/architecture/`, `docs/decisions/`) are engine-level — keep them as-is or add corpus-specific notes.

---

## Step 7 — Run and add first volume

```bash
python dev.py   # starts FastAPI on :8000
```

Open the Godot project and hit Play. You should see:

1. PlotZIntro animation (PLOT word sequence → PLOTZ)
2. Your new TitleCard
3. CorpusMenu with empty volume list

Use **New Volume** to paste in your first source text. The API will ingest it, build the graph, and return. The volume will appear in the list.

---

## What's engine vs. corpus — reference

### Engine (do not change per-corpus)
- `engine/` — entire Python backend
- `godot/autoloads/API.gd`, `AppState.gd`
- `godot/scenes/PlotZIntro.gd/.tscn`
- `godot/scenes/CorpusMenu.gd/.tscn`
- `godot/scenes/CurationScreen.gd/.tscn`
- `godot/scenes/CurationView.gd/.tscn`
- `godot/scenes/ParagraphCard.gd/.tscn`
- `godot/scenes/InsertStrip.gd/.tscn`
- `godot/scenes/HierarchyMarker.gd/.tscn`
- `godot/scenes/VolumeListItem.gd/.tscn`

### Corpus-specific (change per instance)
- `godot/scenes/TitleCard.gd/.tscn` — title text, optional custom font
- `godot/project.godot` — project name and description
- `model/data/graph.json` — the working graph (starts empty)
- `model/config/curation.json` — curation log (starts as `[]`)
- `model/config/hierarchy.json` — corpus name and level config
- `model/source/` — source text files
- `CLAUDE.md` — project briefing for Claude sessions
- `docs/` — documentation vault

---

## Future: engine as a package

When the engine is extracted into a standalone package (pip install / git submodule), this process simplifies to:

1. Create a new repo
2. Install the engine package
3. Create `TitleCard.tscn` from the provided template
4. Configure `hierarchy.json` and `CLAUDE.md`
5. Run

This guide will be updated when that separation happens.
