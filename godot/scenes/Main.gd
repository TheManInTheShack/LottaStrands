## Main.gd
## Root scene. Sets up the top-level layout and wires up toolbar actions.

extends Control

@onready var status_label: Label = $VBox/Header/StatusLabel
@onready var reload_button: Button = $VBox/Header/ReloadButton
@onready var save_button: Button = $VBox/Header/SaveButton
@onready var detail_label: Label = $VBox/Body/DetailPanel/DetailLabel


func _ready() -> void:
	AppState.scenes_loaded.connect(_on_scenes_loaded)
	AppState.scene_selected.connect(_on_scene_selected)
	AppState.error_occurred.connect(_on_error)
	status_label.text = "Loading..."


func _on_scenes_loaded(scenes: Array) -> void:
	status_label.text = "%d scenes loaded" % scenes.size()


func _on_scene_selected(scene: Dictionary) -> void:
	detail_label.text = "[%d] %s\n%d shots" % [
		scene.get("index", 0),
		scene.get("heading", ""),
		scene.get("shot_count", 0)
	]


func _on_error(message: String) -> void:
	status_label.text = "Error: " + message


func _on_reload_pressed() -> void:
	status_label.text = "Reloading..."
	AppState.load_scenes()


func _on_save_pressed() -> void:
	AppState.save()
	status_label.text = "Saved."
