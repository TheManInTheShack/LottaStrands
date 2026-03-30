## VolumeListItem.gd
## A single selectable row in the volume list.
## Text overflows auto-scroll horizontally on hover.
## Delete button emits delete_requested for confirmation upstream.

extends Control

signal selected(index: int)
signal delete_requested(volume_id: String, volume_title: String)

const COLOR_NORMAL   := Color(0, 0, 0, 0)
const COLOR_HOVER    := Color(1, 1, 1, 0.06)
const COLOR_SELECTED := Color(0.25, 0.55, 1.0, 0.28)

var item_index: int = 0
var volume_id: String = ""
var volume_title: String = ""
var _is_selected: bool = false
var _scroll_dist: float = 0.0
var _tween: Tween = null

@onready var bg: ColorRect     = $BG
@onready var clip_box: Control = $HBox/ClipBox
@onready var label: Label      = $HBox/ClipBox/Label
@onready var delete_btn: Button = $HBox/DeleteButton


func setup(idx: int, text: String, vol_id: String, vol_title: String) -> void:
	item_index = idx
	volume_id = vol_id
	volume_title = vol_title
	label.text = text
	call_deferred("_compute_scroll")


func set_selected(on: bool) -> void:
	_is_selected = on
	bg.color = COLOR_SELECTED if on else COLOR_NORMAL


func reset_hover() -> void:
	if _tween:
		_tween.kill()
		_tween = null
	label.position.x = 0
	if not _is_selected:
		bg.color = COLOR_NORMAL
	delete_btn.release_focus()


func _compute_scroll() -> void:
	_scroll_dist = maxf(0.0, label.get_minimum_size().x - clip_box.size.x)


func _on_mouse_entered() -> void:
	if not _is_selected:
		bg.color = COLOR_HOVER
	_compute_scroll()
	if _scroll_dist > 0.0:
		if _tween:
			_tween.kill()
		_tween = create_tween().set_loops()
		var dur := clampf(_scroll_dist / 80.0, 0.5, 3.0)
		_tween.tween_property(label, "position:x", -_scroll_dist, dur).set_ease(Tween.EASE_IN_OUT)
		_tween.tween_interval(0.4)
		_tween.tween_property(label, "position:x", 0.0, dur).set_ease(Tween.EASE_IN_OUT)
		_tween.tween_interval(0.4)


func _on_mouse_exited() -> void:
	if not _is_selected:
		bg.color = COLOR_NORMAL
	if _tween:
		_tween.kill()
		_tween = null
	create_tween().tween_property(label, "position:x", 0.0, 0.15)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			# Only select if click wasn't on the delete button
			if not delete_btn.get_global_rect().has_point(event.global_position):
				selected.emit(item_index)


func _on_delete_button_pressed() -> void:
	delete_requested.emit(volume_id, volume_title)
