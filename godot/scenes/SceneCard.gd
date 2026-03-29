## SceneCard.gd
## A single row in the scene list. Displays scene index, heading, and shot count.
## Emits scene_pressed when clicked.

extends PanelContainer

signal scene_pressed(scene: Dictionary)

var scene_data: Dictionary = {}

@onready var index_label: Label = $HBox/IndexLabel
@onready var heading_label: Label = $HBox/HeadingLabel
@onready var shots_label: Label = $HBox/ShotsLabel
@onready var button: Button = $Button


func setup(data: Dictionary) -> void:
	scene_data = data
	index_label.text = str(data.get("index", ""))
	heading_label.text = data.get("heading", "")
	shots_label.text = "%d shots" % data.get("shot_count", 0)


func set_selected(selected: bool) -> void:
	# Highlight selected card
	if selected:
		add_theme_stylebox_override("panel", _selected_style())
	else:
		remove_theme_stylebox_override("panel")


func _on_button_pressed() -> void:
	scene_pressed.emit(scene_data)


func _selected_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.2, 0.4, 0.6, 0.5)
	return style
