## InsertStrip.gd
## A touch-friendly tap target between paragraph cards.
## Emits marker_requested when the user taps to insert a hierarchy boundary.

extends PanelContainer

signal marker_requested(before_paragraph_id: String)

var before_paragraph_id: String = ""

@onready var add_button: Button = $CenterBox/AddButton


func setup(para_id: String) -> void:
	before_paragraph_id = para_id


func _on_add_button_pressed() -> void:
	if before_paragraph_id:
		marker_requested.emit(before_paragraph_id)
