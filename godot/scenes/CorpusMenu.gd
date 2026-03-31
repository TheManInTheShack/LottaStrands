## CorpusMenu.gd
## Entry point screen. Shows volumes, action buttons, and inline New Volume form.
## Delete button on each volume row triggers a confirmation dialog.

extends Control

const VolumeListItemScene = preload("res://scenes/VolumeListItem.tscn")

@onready var empty_hint: Label              = $HBox/Content/EmptyHint
@onready var volumes_panel: PanelContainer  = $HBox/Content/VolumesPanel
@onready var volumes_list: VBoxContainer    = $HBox/Content/VolumesPanel/VolumesScroll/VolumesList
@onready var curate_button: Button          = $HBox/Content/Curate

@onready var form_panel: PanelContainer     = $NewVolumePanel
@onready var title_input: LineEdit          = $NewVolumePanel/FormVBox/TitleRow/TitleInput
@onready var type_option: OptionButton      = $NewVolumePanel/FormVBox/TypeRow/TypeOption
@onready var year_input: LineEdit           = $NewVolumePanel/FormVBox/YearRow/YearInput
@onready var author_input: LineEdit         = $NewVolumePanel/FormVBox/AuthorRow/AuthorInput
@onready var text_input: TextEdit           = $NewVolumePanel/FormVBox/TextInput
@onready var form_status: Label             = $NewVolumePanel/FormVBox/FormButtons/StatusLabel

@onready var delete_confirm: ConfirmationDialog = $DeleteConfirm

var _volume_items: Array = []
var _selected_idx: int = -1
var _pending_delete_id: String = ""
# Parallel array to _volume_items; holds raw volume dicts from the API
var _volumes_data: Array = []


func _ready() -> void:
	AppState.corpus_loaded.connect(_on_corpus_loaded)
	AppState.graph_changed.connect(_on_graph_changed)
	AppState.volume_created.connect(_on_volume_created)
	AppState.error_occurred.connect(_on_api_error)

	type_option.add_item("screenplay")
	type_option.add_item("novel")
	type_option.add_item("short story")
	type_option.add_item("unknown")

	if AppState.corpus.size() > 0:
		_on_corpus_loaded(AppState.corpus)


func _on_corpus_loaded(corpus: Dictionary) -> void:
	_populate_volumes(corpus.get("volumes", []))


func _on_graph_changed() -> void:
	AppState.load_corpus()


func _populate_volumes(vols: Array) -> void:
	for child in volumes_list.get_children():
		child.queue_free()
	_volume_items.clear()
	_volumes_data.clear()
	_selected_idx = -1

	if vols.size() == 0:
		empty_hint.visible = true
		volumes_panel.visible = false
		curate_button.disabled = true
		return

	empty_hint.visible = false
	volumes_panel.visible = true

	for i in vols.size():
		var vol: Dictionary = vols[i]
		var lbl := "%s (%s, %s)" % [
			vol.get("title", ""),
			vol.get("type", ""),
			str(vol.get("year", ""))
		]
		var item = VolumeListItemScene.instantiate()
		volumes_list.add_child(item)
		item.setup(i, lbl, vol.get("id", ""), vol.get("title", ""))
		item.selected.connect(_on_volume_item_selected)
		item.delete_requested.connect(_on_delete_requested)
		_volume_items.append(item)
		_volumes_data.append(vol)

	_select_item(0)
	AppState.selected_volume = vols[0]
	curate_button.disabled = false


func _select_item(idx: int) -> void:
	for i in _volume_items.size():
		_volume_items[i].set_selected(i == idx)
	_selected_idx = idx


func _on_volume_item_selected(idx: int) -> void:
	_select_item(idx)
	if idx < _volumes_data.size():
		AppState.selected_volume = _volumes_data[idx]
	curate_button.disabled = false


func _on_curate_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/CurationScreen.tscn")


# --- Delete ---

func _on_delete_requested(volume_id: String, volume_title: String) -> void:
	_pending_delete_id = volume_id
	delete_confirm.dialog_text = (
		"Delete \"%s\"?\n\nThis will remove the entire volume subgraph and cannot be undone." % volume_title
	)
	delete_confirm.popup_centered()


func _on_delete_confirmed() -> void:
	if _pending_delete_id:
		AppState.delete_volume(_pending_delete_id)
	_pending_delete_id = ""


func _on_delete_cancelled() -> void:
	_pending_delete_id = ""
	for item in _volume_items:
		item.reset_hover()


# --- New Volume form ---

func _on_new_volume_pressed() -> void:
	form_status.text = ""
	_set_form_submitting(false)
	form_panel.visible = true


func _on_cancel_form() -> void:
	form_panel.visible = false


func _set_form_submitting(submitting: bool) -> void:
	$NewVolumePanel/FormVBox/FormButtons/SubmitButton.disabled = submitting
	$NewVolumePanel/FormVBox/FormButtons/CancelButton.disabled = submitting


func _on_volume_created(_data: Dictionary) -> void:
	form_panel.visible = false
	_set_form_submitting(false)


func _on_api_error(message: String) -> void:
	# Show errors that occur while the form is open
	if form_panel.visible:
		form_status.text = message
		_set_form_submitting(false)


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
	_set_form_submitting(true)

	var type_map := ["screenplay", "novel", "short story", "unknown"]
	var authors: Array = []
	var raw := author_input.text.strip_edges()
	if not raw.is_empty():
		for a in raw.split(","):
			authors.append(a.strip_edges())

	var year_val = null
	var yr := year_input.text.strip_edges()
	if not yr.is_empty() and yr.is_valid_int():
		year_val = int(yr)

	AppState.create_volume({
		"title": title,
		"type": type_map[type_option.selected],
		"year": year_val,
		"authors": authors,
	}, text)
