## AppState.gd
## Autoload singleton. Holds the current application state and broadcasts
## changes via signals. UI components read from here and listen to signals
## rather than calling the API directly.

extends Node

signal scenes_loaded(scenes: Array)
signal scene_selected(scene: Dictionary)
signal graph_changed()
signal error_occurred(message: String)

var scenes: Array = []
var selected_scene: Dictionary = {}
var is_loading: bool = false


func _ready() -> void:
	API.request_completed.connect(_on_api_response)
	API.request_failed.connect(_on_api_error)
	load_scenes()


func load_scenes() -> void:
	is_loading = true
	API.get_scenes()


func select_scene(scene: Dictionary) -> void:
	selected_scene = scene
	scene_selected.emit(scene)


func merge_scenes(indices: Array, heading: String) -> void:
	API.merge_scenes(indices, heading)


func rename_scene(index: int, heading: String) -> void:
	API.rename_scene(index, heading)


func split_scene(index: int, at_child_index: int,
				 heading_before: String, heading_after: String) -> void:
	API.split_scene(index, at_child_index, heading_before, heading_after)


func save() -> void:
	API.save_curated()


# --- API response handler ---

func _on_api_response(endpoint: String, data: Variant) -> void:
	is_loading = false
	match endpoint:
		"/scenes":
			scenes = data
			scenes_loaded.emit(scenes)
		"/curate/merge", "/curate/rename", "/curate/split":
			# Structural change — reload scene list
			load_scenes()
			graph_changed.emit()
		"/curate/save":
			print("Graph saved.")
		"/curate/reload":
			load_scenes()
			graph_changed.emit()


func _on_api_error(endpoint: String, error: String) -> void:
	is_loading = false
	var msg := "Error on %s: %s" % [endpoint, error]
	push_error(msg)
	error_occurred.emit(msg)
