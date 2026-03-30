## VolumeListItem.gd
## A single selectable row in the volume list.
## Text that overflows the container auto-scrolls horizontally on hover/focus.

extends Control

signal selected(index: int)

const COLOR_NORMAL   := Color(0, 0, 0, 0)
const COLOR_HOVER    := Color(1, 1, 1, 0.06)
const COLOR_SELECTED := Color(0.25, 0.55, 1.0, 0.28)

var item_index: int = 0
var _is_selected: bool = false
var _scroll_dist: float = 0.0
var _tween: Tween = null

@onready var bg: ColorRect   = $BG
@onready var clip_box: Control = $ClipBox
@onready var label: Label    = $ClipBox/Label


func setup(idx: int, text: String) -> void:
	item_index = idx
	label.text = text
	call_deferred("_compute_scroll")


func set_selected(on: bool) -> void:
	_is_selected = on
	bg.color = COLOR_SELECTED if on else COLOR_NORMAL


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
			selected.emit(item_index)
