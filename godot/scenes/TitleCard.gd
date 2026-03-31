## TitleCard.gd
## Opening animation: PLOT word sequence → PLOTZ → final title → CorpusMenu

extends Control

@onready var word_label: Label        = $WordLabel
@onready var title_container: Control = $TitleContainer
@onready var title_line1: Label       = $TitleContainer/TitleLine1
@onready var title_line2: Label       = $TitleContainer/TitleLine2

const WORDS: Array = ["Parse", "Lexicon", "Ontology", "Taxonomy", "Z", "PLOTZ"]

const FADE_IN_TIME       := 0.4
const WORD_HOLD_TIME     := 0.75
const WORD_FADE_OUT_TIME := 0.25
const PLOTZ_HOLD_TIME    := 1.5
const PLOTZ_FADE_OUT     := 0.5
const TITLE_HOLD_TIME    := 1.5
const TITLE_FADE_OUT     := 0.25


func _ready() -> void:
	word_label.modulate.a = 0.0
	title_container.modulate.a = 0.0
	_run_animation()


func _run_animation() -> void:
	for word in WORDS:
		word_label.text = word

		var tw := create_tween()
		tw.tween_property(word_label, "modulate:a", 1.0, FADE_IN_TIME)
		await tw.finished

		var hold := PLOTZ_HOLD_TIME if word == "PLOTZ" else WORD_HOLD_TIME
		await get_tree().create_timer(hold).timeout

		var fade_out := PLOTZ_FADE_OUT if word == "PLOTZ" else WORD_FADE_OUT_TIME
		tw = create_tween()
		tw.tween_property(word_label, "modulate:a", 0.0, fade_out)
		await tw.finished

	# Final title
	var tw := create_tween()
	tw.tween_property(title_container, "modulate:a", 1.0, FADE_IN_TIME)
	await tw.finished

	await get_tree().create_timer(TITLE_HOLD_TIME).timeout

	tw = create_tween()
	tw.tween_property(title_container, "modulate:a", 0.0, TITLE_FADE_OUT)
	await tw.finished

	get_tree().change_scene_to_file("res://scenes/CorpusMenu.tscn")
