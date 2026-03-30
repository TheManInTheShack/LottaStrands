## CorpusMenu.gd
## Entry point screen. Volumes list on the left, actions on the right.
## Includes inline New Volume form and test data for scrolling demonstration.

extends Control

const VolumeListItemScene = preload("res://scenes/VolumeListItem.tscn")

@onready var corpus_name: Label        = $HBox/Content/CorpusName
@onready var empty_hint: Label         = $HBox/Content/EmptyHint
@onready var volumes_panel: PanelContainer = $HBox/Content/VolumesPanel
@onready var volumes_list: VBoxContainer   = $HBox/Content/VolumesPanel/VolumesScroll/VolumesList
@onready var curate_button: Button     = $HBox/Content/Curate

@onready var form_panel: PanelContainer = $NewVolumePanel
@onready var title_input: LineEdit     = $NewVolumePanel/FormVBox/TitleRow/TitleInput
@onready var type_option: OptionButton = $NewVolumePanel/FormVBox/TypeRow/TypeOption
@onready var year_input: LineEdit      = $NewVolumePanel/FormVBox/YearRow/YearInput
@onready var author_input: LineEdit    = $NewVolumePanel/FormVBox/AuthorRow/AuthorInput
@onready var text_input: TextEdit      = $NewVolumePanel/FormVBox/TextInput
@onready var form_status: Label        = $NewVolumePanel/FormVBox/FormButtons/StatusLabel

var _volume_items: Array = []
var _selected_idx: int = -1

# Temporary test volumes — replace with real data once volumes are created via API
const TEST_VOLUMES := [
	{"title": "The Big Lebowski (A Very Long Title That Tests the Marquee Scroll Functionality on Hover)", "type": "screenplay", "year": 1998},
	{"title": "The Big Lebowski", "type": "screenplay", "year": 1998},
	{"title": "No Country for Old Men", "type": "screenplay", "year": 2007},
	{"title": "Blood Meridian", "type": "novel", "year": 1985},
	{"title": "The Road", "type": "novel", "year": 2006},
	{"title": "Fargo", "type": "screenplay", "year": 1996},
	{"title": "Barton Fink", "type": "screenplay", "year": 1991},
	{"title": "True Grit", "type": "screenplay", "year": 2010},
]


func _ready() -> void:
	AppState.corpus_loaded.connect(_on_corpus_loaded)
	AppState.graph_changed.connect(_on_graph_changed)

	type_option.add_item("screenplay")
	type_option.add_item("novel")
	type_option.add_item("short story")
	type_option.add_item("unknown")

	if AppState.corpus.size() > 0:
		_on_corpus_loaded(AppState.corpus)
	else:
		# Show test volumes while no real data exists
		_populate_volumes(TEST_VOLUMES)


func _on_corpus_loaded(corpus: Dictionary) -> void:
	corpus_name.text = corpus.get("title", corpus.get("name", ""))
	var vols: Array = corpus.get("volumes", [])
	if vols.size() > 0:
		_populate_volumes(vols)
	else:
		_populate_volumes(TEST_VOLUMES)


func _on_graph_changed() -> void:
	AppState.load_corpus()


func _populate_volumes(vols: Array) -> void:
	for child in volumes_list.get_children():
		child.queue_free()
	_volume_items.clear()
	_selected_idx = -1

	if vols.size() == 0:
		empty_hint.visible = true
		volumes_panel.visible = false
		curate_button.disabled = true
		return

	empty_hint.visible = false
	volumes_panel.visible = true

	for i in vols.size():
		var vol := vols[i]
		var lbl := "%s (%s, %s)" % [
			vol.get("title", ""),
			vol.get("type", ""),
			str(vol.get("year", ""))
		]
		var item = VolumeListItemScene.instantiate()
		volumes_list.add_child(item)
		item.setup(i, lbl)
		item.selected.connect(_on_volume_item_selected)
		_volume_items.append(item)

	_select_item(0)
	AppState.selected_volume = vols[0] if vols.size() > 0 else {}
	curate_button.disabled = false


func _select_item(idx: int) -> void:
	for i in _volume_items.size():
		_volume_items[i].set_selected(i == idx)
	_selected_idx = idx


func _on_volume_item_selected(idx: int) -> void:
	_select_item(idx)
	var vols: Array = AppState.corpus.get("volumes", [])
	if idx < vols.size():
		AppState.selected_volume = vols[idx]
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

	form_panel.visible = false
