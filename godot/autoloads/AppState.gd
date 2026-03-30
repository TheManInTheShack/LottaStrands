## AppState.gd
## Autoload singleton. Holds the current application state and broadcasts
## changes via signals. UI components read from here and listen to signals
## rather than calling the API directly.

extends Node

signal corpus_loaded(corpus: Dictionary)
signal scenes_loaded(scenes: Array)
signal scene_selected(scene: Dictionary)
signal scene_detail_loaded(detail: Dictionary)
signal paragraphs_loaded(paragraphs: Array)
signal graph_changed()
signal error_occurred(message: String)

var corpus: Dictionary = {}
var volumes: Array = []
var selected_volume: Dictionary = {}
var scenes: Array = []
var selected_scene: Dictionary = {}
var scene_detail: Dictionary = {}
var paragraphs: Array = []
var is_loading: bool = false


func _ready() -> void:
	API.request_completed.connect(_on_api_response)
	API.request_failed.connect(_on_api_error)
	load_corpus()


func load_corpus() -> void:
	API.get_corpus()


func load_scenes() -> void:
	is_loading = true
	API.get_scenes()


func load_paragraphs() -> void:
	is_loading = true
	API.get_paragraphs()


func select_volume(volume: Dictionary) -> void:
	selected_volume = volume
	load_paragraphs()


func select_scene(scene: Dictionary) -> void:
	selected_scene = scene
	scene_selected.emit(scene)
	API.get_scene_detail(scene.get("index", 0))


func create_volume(meta: Dictionary, text: String) -> void:
	API.create_volume(meta, text)


func insert_marker(before_paragraph_id: String, level: String, heading: String = "") -> void:
	API.insert_marker(before_paragraph_id, level, heading)


func merge_scenes(indices: Array, heading: String) -> void:
	API.merge_scenes(indices, heading)


func rename_scene(index: int, heading: String) -> void:
	API.rename_scene(index, heading)


func split_scene(index: int, at_child_index: int,
				 heading_before: String, heading_after: String) -> void:
	API.split_scene(index, at_child_index, heading_before, heading_after)


func save() -> void:
	API.save_curated()


func _on_api_response(endpoint: String, data: Variant) -> void:
	is_loading = false
	if endpoint == "/corpus":
		corpus = data
		volumes = data.get("volumes", [])
		if volumes.size() > 0:
			selected_volume = volumes[0]
		corpus_loaded.emit(corpus)
	elif endpoint == "/paragraphs":
		paragraphs = data
		paragraphs_loaded.emit(paragraphs)
	elif endpoint == "/scenes":
		scenes = data
		scenes_loaded.emit(scenes)
	elif endpoint.begins_with("/scenes/"):
		scene_detail = data
		scene_detail_loaded.emit(data)
	elif endpoint == "/volumes":
		# Volume created — reload corpus and paragraphs
		load_corpus()
		load_paragraphs()
		graph_changed.emit()
	elif endpoint == "/curate/insert_marker":
		load_paragraphs()
		graph_changed.emit()
	elif endpoint in ["/curate/merge", "/curate/rename", "/curate/split"]:
		load_paragraphs()
		graph_changed.emit()
	elif endpoint == "/curate/save":
		print("Graph saved.")
	elif endpoint == "/curate/reload":
		load_paragraphs()
		graph_changed.emit()


func _on_api_error(endpoint: String, error: String) -> void:
	is_loading = false
	var msg := "Error on %s: %s" % [endpoint, error]
	push_error(msg)
	error_occurred.emit(msg)
