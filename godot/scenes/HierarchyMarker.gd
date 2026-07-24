## HierarchyMarker.gd
## Displays a scene/shot boundary marker between paragraph cards.
## The user can remove it to merge the two adjacent scenes back together.

extends PanelContainer

signal remove_requested(scene_index: int)

var scene_index: int = 0
var prev_scene_index: int = 0

@onready var heading_label: Label = $HBox/HeadingLabel
@onready var level_bar: ColorRect = $HBox/LevelBar


func setup(index: int, heading: String, prev_index: int, level: String = "scene") -> void:
	scene_index = index
	prev_scene_index = prev_index
	heading_label.text = "▶ Scene %d — %s" % [index, heading]
	match level:
		"scene": level_bar.color = Color(0.25, 0.55, 1.0, 1.0)
		"shot":  level_bar.color = Color(0.25, 0.8, 0.45, 1.0)


func _on_remove_button_pressed() -> void:
	remove_requested.emit(scene_index)
