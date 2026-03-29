"""
Parse template for screenplay format.

Line classification by leading tab count:
  indent=0  + ALL CAPS  -> scene heading
  indent>=3 + ALL CAPS  -> character cue (introduces dialogue)
  indent>=1             -> dialogue (when following character cue)
  indent=0  + mixed     -> action / description
"""

import json
from pathlib import Path


def leading_tabs(line):
    return len(line) - len(line.lstrip('\t'))


def is_all_caps(text):
    text = text.strip()
    return bool(text) and text == text.upper() and any(c.isalpha() for c in text)


def classify_line(line):
    content = line.rstrip()
    stripped = content.strip()

    if not stripped:
        return 'blank', 0, ''

    tabs = leading_tabs(content)
    upper = is_all_caps(stripped)

    if tabs == 0 and upper:
        return 'scene', tabs, stripped
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
    # Block types: title, scene, action, dialogue
    blocks = []
    title_found = False
    i = 0

    while i < len(classified):
        ltype, tabs, content = classified[i]

        if ltype == 'blank':
            i += 1
            continue

        if ltype == 'scene':
            blocks.append({'type': 'scene', 'heading': content})
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
                if dt in ('scene', 'character'):
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
                if at in ('scene', 'character'):
                    break
                action_lines.append(acontent)
                i += 1
            blocks.append({'type': 'action', 'lines': action_lines})
            continue

        i += 1

    # Third pass: organize blocks into scenes
    scenes = []
    current_scene = {'heading': 'PROLOGUE', 'index': 0, 'paragraphs': []}
    para_index = 0

    for block in blocks:
        if block['type'] == 'title':
            continue

        if block['type'] == 'scene':
            if current_scene['paragraphs']:
                scenes.append(current_scene)
            current_scene = {
                'heading': block['heading'],
                'index': len(scenes) + 1,
                'paragraphs': []
            }
            para_index = 0
            continue

        if block['type'] == 'action':
            para_index += 1
            current_scene['paragraphs'].append({
                'type': 'action',
                'index': para_index,
                'text': ' '.join(block['lines'])
            })

        if block['type'] == 'dialogue':
            para_index += 1
            current_scene['paragraphs'].append({
                'type': 'dialogue',
                'speaker': block['speaker'],
                'index': para_index,
                'text': ' '.join(block['lines'])
            })

    if current_scene['paragraphs']:
        scenes.append(current_scene)

    return {
        'title': 'The Big Lebowski',
        'corpus_type': 'screenplay',
        'scene_count': len(scenes),
        'scenes': scenes
    }
