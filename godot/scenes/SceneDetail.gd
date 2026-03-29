## SceneDetail.gd
## Right panel component for the curation view.
## Shows key/value metadata and full text content of the selected scene.

extends VBoxContainer

@onready var placeholder: Label = $PlaceholderLabel
@onready var meta: VBoxContainer = $Meta
@onready var sep: HSeparator = $Sep
@onready var content: VBoxContainer = $Content
@onready var index_value: Label = $Meta/Grid/IndexValue
@onready var heading_value: Label = $Meta/Grid/HeadingValue
@onready var shots_value: Label = $Meta/Grid/ShotsValue
@onready var paragraphs_value: Label = $Meta/Grid/ParagraphsValue
@onready var content_text: TextEdit = $Content/ContentText


func _ready() -> void:
	AppState.scene_detail_loaded.connect(_on_detail_loaded)
	content_text.editable = false


func _on_detail_loaded(detail: Dictionary) -> void:
	placeholder.visible = false
	meta.visible = true
	sep.visible = true
	content.visible = true

	index_value.text = str(detail.get("index", ""))
	heading_value.text = detail.get("heading", "")
	shots_value.text = str(detail.get("shot_count", ""))
	paragraphs_value.text = str(detail.get("paragraph_count", ""))
	content_text.text = detail.get("full_text", "")
