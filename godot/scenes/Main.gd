## Main.gd
## Curation view. Header bar with navigation + full-screen scrollable paragraph list.

extends Control

@onready var status_label: Label = $VBox/Header/StatusLabel


func _ready() -> void:
	AppState.paragraphs_loaded.connect(_on_paragraphs_loaded)
	AppState.error_occurred.connect(_on_error)
	status_label.text = "Loading..."
	AppState.load_paragraphs()


func _on_paragraphs_loaded(paragraphs: Array) -> void:
	status_label.text = "%d paragraphs" % paragraphs.size()


func _on_error(message: String) -> void:
	status_label.text = "Error: " + message


func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/CorpusMenu.tscn")


func _on_reload_pressed() -> void:
	status_label.text = "Reloading..."
	AppState.load_paragraphs()


func _on_save_pressed() -> void:
	AppState.save()
	status_label.text = "Saved."
