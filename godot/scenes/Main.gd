## Main.gd
## Curation view. Scene list on the left, detail panel and command strip on the right.

extends Control

@onready var status_label: Label = $VBox/Header/StatusLabel


func _ready() -> void:
	AppState.scenes_loaded.connect(_on_scenes_loaded)
	AppState.error_occurred.connect(_on_error)
	status_label.text = "Loading..."


func _on_scenes_loaded(scenes: Array) -> void:
	status_label.text = "%d scenes" % scenes.size()


func _on_error(message: String) -> void:
	status_label.text = "Error: " + message


func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/CorpusMenu.tscn")


func _on_reload_pressed() -> void:
	status_label.text = "Reloading..."
	AppState.load_scenes()


func _on_save_pressed() -> void:
	AppState.save()
	status_label.text = "Saved."


# Command strip — placeholder handlers for now
func _on_merge_pressed() -> void:
	pass

func _on_split_pressed() -> void:
	pass

func _on_rename_pressed() -> void:
	pass

func _on_save_curation_pressed() -> void:
	AppState.save()
	status_label.text = "Curation saved."
