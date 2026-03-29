## CorpusMenu.gd
## Entry point screen. Shows the corpus, its volumes, and action buttons
## to enter each phase of the workflow.

extends Control

@onready var corpus_name_label: Label = $VBox/Body/Left/CorpusName
@onready var volume_list: ItemList = $VBox/Body/Left/VolumeList
@onready var curate_button: Button = $VBox/Body/Right/Curate


func _ready() -> void:
	AppState.corpus_loaded.connect(_on_corpus_loaded)
	# If corpus already loaded (e.g. returning from curation), populate now
	if AppState.corpus.size() > 0:
		_on_corpus_loaded(AppState.corpus)


func _on_corpus_loaded(corpus: Dictionary) -> void:
	corpus_name_label.text = corpus.get("title", corpus.get("name", ""))
	volume_list.clear()
	var volumes: Array = corpus.get("volumes", [])
	for vol in volumes:
		var label := "%s (%s, %s)" % [
			vol.get("title", ""),
			vol.get("type", ""),
			str(vol.get("year", ""))
		]
		volume_list.add_item(label)
	if volume_list.item_count > 0:
		volume_list.select(0)
		curate_button.disabled = false


func _on_volume_selected(_index: int) -> void:
	var volumes: Array = AppState.corpus.get("volumes", [])
	if _index < volumes.size():
		AppState.selected_volume = volumes[_index]
	curate_button.disabled = false


func _on_curate_pressed() -> void:
	AppState.load_scenes()
	get_tree().change_scene_to_file("res://scenes/Main.tscn")


# Placeholder handlers for future phases
func _on_new_volume_pressed() -> void:
	pass

func _on_load_source_pressed() -> void:
	pass

func _on_set_type_pressed() -> void:
	pass

func _on_parse_pressed() -> void:
	pass
