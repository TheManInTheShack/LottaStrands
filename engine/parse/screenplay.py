"""
Parse template for screenplay format.

Line classification by leading tab count:
  indent=0  + ALL CAPS  -> scene heading, shot description, or stage direction
  indent>=3 + ALL CAPS  -> character cue (introduces dialogue)
  indent>=1             -> dialogue (when following character cue)
  indent=0  + mixed     -> action / description

Scene heading sub-classification (all are indent=0 + ALL CAPS):
  stage_direction : ends with ':'
  scene           : contains location keywords or INTERIOR/EXTERIOR
  shot            : everything else (camera directions, character panels, etc.)
"""

import re
from pathlib import Path


# Words that indicate a camera/framing shot rather than a location scene
SHOT_KEYWORDS = {
    'WIDER', 'WIDE', 'CLOSE', 'CLOSER', 'TRACKING', 'TRACK', 'REVERSE',
    'POV', 'ANGLE', 'SHOT', 'CRANE', 'PAN', 'TILT', 'DOLLY', 'FADE',
    'CUT', 'BLACK', 'BLACKNESS', 'PINS', 'FLASH', 'FLASHBACK',
    'CRASH', 'SLOW', 'FAST', 'BACK'
}

# If a heading STARTS with one of these words it is always a shot,
# even if it also contains location keywords
SHOT_OPENERS = {
    'WIDER', 'WIDE', 'CLOSE', 'CLOSER', 'TRACKING', 'TRACK', 'REVERSE',
    'BACK', 'FADE', 'CUT', 'SLOW', 'FAST'
}

# Patterns that indicate a true scene heading (location change)
SCENE_PATTERNS = [
    re.compile(r'^(INTERIOR|EXTERIOR|INT\.|EXT\.)', re.IGNORECASE),
    re.compile(r"\b(HOUSE|ROOM|LANE|ALLEY|OFFICE|CAR|LOT|STREET|BEACH|"
               r"LOFT|SHOP|BAR|THEATER|HALLWAY|BUNGALOW|MANSION|HIGHWAY|"
               r"AREA|DOOR|FOOTWELL|DENNY'S)\b"),
]


def leading_tabs(line):
    return len(line) - len(line.lstrip('\t'))


def is_all_caps(text):
    text = text.strip()
    return bool(text) and text == text.upper() and any(c.isalpha() for c in text)


def classify_heading(text):
    """Classify an ALL CAPS zero-indent line as scene, shot, or stage_direction."""
    if text.endswith(':'):
        return 'stage_direction'
    # If it opens with a camera/movement word, it's always a shot
    first_word = re.split(r'[\s\-]', text)[0]
    if first_word in SHOT_OPENERS:
        return 'shot'
    if any(p.search(text) for p in SCENE_PATTERNS):
        return 'scene'
    words = set(re.findall(r'[A-Z]+', text))
    if words & SHOT_KEYWORDS:
        return 'shot'
    # Default: treat as shot (conservative — keeps scenes clean)
    return 'shot'


def classify_line(line):
    content = line.rstrip()
    stripped = content.strip()

    if not stripped:
        return 'blank', 0, ''

    tabs = leading_tabs(content)
    upper = is_all_caps(stripped)

    if tabs == 0 and upper:
        heading_type = classify_heading(stripped)
        return heading_type, tabs, stripped
    elif tabs >= 3 and upper:
        return 'character', tabs, stripped
    elif tabs >= 1:
        return 'dialogue', tabs, stripped
    else:
        return 'action', tabs, stripped


def parse_screenplay(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    # First pass: classify each line
    classified = [classify_line(line) for line in lines]

    # Second pass: group into raw blocks
    # Block types: title, scene, shot, stage_direction, action, dialogue
    blocks = []
    title_found = False
    i = 0

    while i < len(classified):
        ltype, tabs, content = classified[i]

        if ltype == 'blank':
            i += 1
            continue

        if ltype in ('scene', 'shot'):
            blocks.append({'type': ltype, 'heading': content})
            i += 1
            continue

        if ltype == 'stage_direction':
            # Fold into next dialogue block as a modifier; store for now
            blocks.append({'type': 'stage_direction', 'text': content.rstrip(':').strip()})
            i += 1
            continue

        if ltype == 'character':
            if not title_found:
                title_found = True
                blocks.append({'type': 'title', 'text': content})
                i += 1
                continue

            speaker = content
            i += 1
            dialogue_lines = []

            while i < len(classified):
                dt, _, dcontent = classified[i]
                if dt == 'blank':
                    i += 1
                    break
                if dt in ('scene', 'shot', 'stage_direction', 'character'):
                    break
                dialogue_lines.append(dcontent)
                i += 1

            if dialogue_lines:
                blocks.append({
                    'type': 'dialogue',
                    'speaker': speaker,
                    'lines': dialogue_lines
                })
            continue

        if ltype in ('action', 'dialogue'):
            action_lines = [content]
            i += 1
            while i < len(classified):
                at, _, acontent = classified[i]
                if at == 'blank':
                    i += 1
                    break
                if at in ('scene', 'shot', 'stage_direction', 'character'):
                    break
                action_lines.append(acontent)
                i += 1
            blocks.append({'type': 'action', 'lines': action_lines})
            continue

        i += 1

    # Third pass: organize blocks into corpus -> scene -> shot -> paragraphs
    # A pending stage_direction modifies the next dialogue paragraph
    scenes = []
    current_scene = None
    current_shot = None
    scene_index = 0
    shot_index = 0
    para_index = 0
    pending_stage_dir = None

    def ensure_scene():
        nonlocal current_scene, current_shot, scene_index, shot_index, para_index
        if current_scene is None:
            scene_index += 1
            current_scene = {'heading': 'PROLOGUE', 'index': scene_index, 'shots': []}
            current_shot = None

    def ensure_shot(heading=''):
        nonlocal current_shot, shot_index, para_index
        ensure_scene()
        if current_shot is None:
            shot_index += 1
            current_shot = {'heading': heading, 'index': shot_index, 'paragraphs': []}
            current_scene['shots'].append(current_shot)
            para_index = 0

    def add_paragraph(para):
        ensure_shot()
        para_index_local = len(current_shot['paragraphs']) + 1
        para['index'] = para_index_local
        current_shot['paragraphs'].append(para)

    for block in blocks:
        if block['type'] == 'title':
            continue

        if block['type'] == 'scene':
            if current_scene is not None:
                scenes.append(current_scene)
            scene_index += 1
            current_scene = {'heading': block['heading'], 'index': scene_index, 'shots': []}
            current_shot = None
            shot_index = 0
            para_index = 0
            continue

        if block['type'] == 'shot':
            ensure_scene()
            shot_index += 1
            current_shot = {'heading': block['heading'], 'index': shot_index, 'paragraphs': []}
            current_scene['shots'].append(current_shot)
            para_index = 0
            continue

        if block['type'] == 'stage_direction':
            pending_stage_dir = block['text']
            continue

        if block['type'] == 'action':
            para = {'type': 'action', 'text': ' '.join(block['lines'])}
            if pending_stage_dir:
                para['direction'] = pending_stage_dir
                pending_stage_dir = None
            add_paragraph(para)

        if block['type'] == 'dialogue':
            para = {
                'type': 'dialogue',
                'speaker': block['speaker'],
                'text': ' '.join(block['lines'])
            }
            if pending_stage_dir:
                para['direction'] = pending_stage_dir
                pending_stage_dir = None
            add_paragraph(para)

    if current_scene is not None:
        scenes.append(current_scene)

    return {
        'title': 'The Big Lebowski',
        'corpus_type': 'screenplay',
        'scene_count': len(scenes),
        'scenes': scenes
    }
