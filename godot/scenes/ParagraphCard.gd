## ParagraphCard.gd
## Displays a single paragraph as a card with an optional scope bar on the left
## indicating hierarchy depth.

extends PanelContainer

@onready var index_label: Label = $HBox/Content/IndexLabel
@onready var text_label: Label = $HBox/Content/TextLabel
@onready var scope_bar: ColorRect = $HBox/ScopeBar

var paragraph_data: Dictionary = {}


func setup(data: Dictionary) -> void:
	paragraph_data = data
	index_label.text = "#%d" % data.get("index", 0)
	text_label.text = data.get("text", "")


func set_scope_color(color: Color) -> void:
	scope_bar.color = color
	scope_bar.visible = true
