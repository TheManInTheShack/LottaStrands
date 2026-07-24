## TitleCard.gd
## Corpus-specific title screen for this LottaStrands instance.
## Plays after PlotZIntro. Different corpora replace this with their own title.

extends Control

@onready var title_container: Control = $TitleContainer

const FADE_IN_TIME   := 0.4
const TITLE_HOLD     := 1.5
const TITLE_FADE_OUT := 0.25


func _ready() -> void:
	title_container.modulate.a = 0.0
	_run_animation()


func _run_animation() -> void:
	var tw := create_tween()
	tw.tween_property(title_container, "modulate:a", 1.0, FADE_IN_TIME)
	await tw.finished

	await get_tree().create_timer(TITLE_HOLD).timeout

	tw = create_tween()
	tw.tween_property(title_container, "modulate:a", 0.0, TITLE_FADE_OUT)
	await tw.finished

	get_tree().change_scene_to_file("res://scenes/CorpusMenu.tscn")
