## CurationView.gd
## Scrollable list of paragraph cards with insert strips between them.
## Scene boundary markers appear where the user has inserted divisions.
## Tapping an InsertStrip inserts a scene marker; tapping × on a marker removes it.

extends VBoxContainer

const ParagraphCardScene = preload("res://scenes/ParagraphCard.tscn")
const InsertStripScene   = preload("res://scenes/InsertStrip.tscn")
const MarkerScene        = preload("res://scenes/HierarchyMarker.tscn")

@onready var card_list: VBoxContainer = $Scroll/CardList


func _ready() -> void:
	AppState.paragraphs_loaded.connect(_on_paragraphs_loaded)
	if AppState.paragraphs.size() > 0:
		_on_paragraphs_loaded(AppState.paragraphs)


func _on_paragraphs_loaded(paras: Array) -> void:
	for child in card_list.get_children():
		child.queue_free()

	var prev_scene_index: int = -1

	for i in paras.size():
		var para: Dictionary = paras[i]
		var scene_idx: int = para.get("scene_index", 0)
		var is_boundary: bool = (i > 0) and (scene_idx != prev_scene_index)

		if i > 0:
			if is_boundary:
				# Scene boundary — show a hierarchy marker (removable)
				var marker = MarkerScene.instantiate()
				card_list.add_child(marker)
				marker.setup(scene_idx, para.get("scene_heading", ""), prev_scene_index)
				marker.remove_requested.connect(_on_remove_marker)
			else:
				# No boundary — show an insert strip (tap to add one)
				var strip = InsertStripScene.instantiate()
				card_list.add_child(strip)
				strip.setup(para.get("id", ""))
				strip.marker_requested.connect(_on_insert_marker)

		prev_scene_index = scene_idx

		var card = ParagraphCardScene.instantiate()
		card_list.add_child(card)
		card.setup(para)


func _on_insert_marker(before_paragraph_id: String) -> void:
	AppState.insert_marker(before_paragraph_id, "scene")


func _on_remove_marker(scene_index: int) -> void:
	# Merge scene_index-1 with scene_index; keep the first scene's heading
	var prev_idx := scene_index - 1
	if prev_idx < 1:
		prev_idx = 1
	var heading := ""
	for s in AppState.scenes:
		if s.get("index") == prev_idx:
			heading = s.get("heading", "")
			break
	AppState.merge_scenes([prev_idx, scene_index], heading)
