## CorpusMenu.gd
## Entry point screen. Shows the corpus, its volumes, and action buttons.
## Also contains the inline "New Volume" form panel.

extends Control

@onready var corpus_name_label: Label   = $VBox/Body/Left/CorpusName
@onready var volume_list: ItemList      = $VBox/Body/Left/VolumeList
@onready var empty_hint: Label          = $VBox/Body/Left/EmptyHint
@onready var curate_button: Button      = $VBox/Body/Right/Curate

@onready var form_panel: PanelContainer = $NewVolumePanel
@onready var title_input: LineEdit      = $NewVolumePanel/FormVBox/TitleRow/TitleInput
@onready var type_option: OptionButton  = $NewVolumePanel/FormVBox/TypeRow/TypeOption
@onready var year_input: LineEdit       = $NewVolumePanel/FormVBox/YearRow/YearInput
@onready var author_input: LineEdit     = $NewVolumePanel/FormVBox/AuthorRow/AuthorInput
@onready var text_input: TextEdit       = $NewVolumePanel/FormVBox/TextInput
@onready var form_status: Label         = $NewVolumePanel/FormVBox/FormButtons/StatusLabel


func _ready() -> void:
	AppState.corpus_loaded.connect(_on_corpus_loaded)
	AppState.graph_changed.connect(_refresh_after_change)

	# Populate type dropdown
	type_option.add_item("screenplay")
	type_option.add_item("novel")
	type_option.add_item("short story")
	type_option.add_item("unknown")

	if AppState.corpus.size() > 0:
		_on_corpus_loaded(AppState.corpus)


func _on_corpus_loaded(corpus: Dictionary) -> void:
	corpus_name_label.text = corpus.get("title", corpus.get("name", ""))
	var volumes: Array = corpus.get("volumes", [])
	volume_list.clear()
	for vol in volumes:
		var label := "%s (%s, %s)" % [
			vol.get("title", ""),
			vol.get("type", ""),
			str(vol.get("year", ""))
		]
		volume_list.add_item(label)

	if volumes.size() > 0:
		empty_hint.visible = false
		volume_list.visible = true
		volume_list.select(0)
		AppState.selected_volume = volumes[0]
		curate_button.disabled = false
	else:
		empty_hint.visible = true
		volume_list.visible = false
		curate_button.disabled = true


func _refresh_after_change() -> void:
	AppState.load_corpus()


func _on_volume_selected(index: int) -> void:
	var volumes: Array = AppState.corpus.get("volumes", [])
	if index < volumes.size():
		AppState.selected_volume = volumes[index]
	curate_button.disabled = false


func _on_curate_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/Main.tscn")


# --- New Volume form ---

func _on_new_volume_pressed() -> void:
	form_status.text = ""
	form_panel.visible = true


func _on_cancel_form() -> void:
	form_panel.visible = false


func _on_submit_volume() -> void:
	var title := title_input.text.strip_edges()
	var text  := text_input.text.strip_edges()
	if title.is_empty():
		form_status.text = "Title required."
		return
	if text.is_empty():
		form_status.text = "Source text required."
		return

	form_status.text = "Creating..."

	var type_map := ["screenplay", "novel", "short story", "unknown"]
	var authors: Array = []
	var raw_author := author_input.text.strip_edges()
	if not raw_author.is_empty():
		for a in raw_author.split(","):
			authors.append(a.strip_edges())

	var year_val = null
	if not year_input.text.strip_edges().is_empty():
		year_val = int(year_input.text.strip_edges())

	var meta := {
		"title": title,
		"type": type_map[type_option.selected],
		"year": year_val,
		"authors": authors,
	}

	AppState.create_volume(meta, text)
	# Response handled in AppState._on_api_response -> graph_changed -> _refresh_after_change
	form_panel.visible = false
