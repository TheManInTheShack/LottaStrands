## SceneList.gd
## Displays the full list of scenes as scrollable SceneCards.
## Listens to AppState for data updates and selection changes.

extends VBoxContainer

const SceneCardScene = preload("res://scenes/SceneCard.tscn")

@onready var header_label: Label = $HeaderLabel
@onready var scroll: ScrollContainer = $ScrollContainer
@onready var list: VBoxContainer = $ScrollContainer/List

var _cards: Array = []
var _selected_index: int = -1


func _ready() -> void:
	AppState.scenes_loaded.connect(_on_scenes_loaded)
	AppState.scene_selected.connect(_on_scene_selected)


func _on_scenes_loaded(scenes: Array) -> void:
	_clear()
	header_label.text = "Scenes (%d)" % scenes.size()
	for scene_data in scenes:
		var card: PanelContainer = SceneCardScene.instantiate()
		list.add_child(card)
		card.setup(scene_data)
		card.scene_pressed.connect(_on_card_pressed)
		_cards.append(card)


func _on_card_pressed(scene_data: Dictionary) -> void:
	AppState.select_scene(scene_data)


func _on_scene_selected(scene: Dictionary) -> void:
	_selected_index = scene.get("index", -1)
	for card in _cards:
		card.set_selected(card.scene_data.get("index") == _selected_index)


func _clear() -> void:
	for child in list.get_children():
		child.queue_free()
	_cards.clear()
