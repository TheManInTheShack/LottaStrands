## PlotZIntro.gd
## Engine-level opening animation: P-L-O-T word sequence → Z → PLOTZ → model title.
## Reusable across any LottaStrands/Plotz corpus instance.

extends Control

@onready var word_label: Label = $WordLabel

const WORDS: Array = ["Parse", "Lexicon", "Ontology", "Taxonomy", "Z", "PLOTZ"]

const FADE_IN_TIME       := 0.2
const WORD_HOLD_TIME     := 0.38
const WORD_FADE_OUT_TIME := 0.12
const PLOTZ_HOLD_TIME    := 1.5
const PLOTZ_FADE_OUT     := 0.25


func _ready() -> void:
	word_label.modulate.a = 0.0
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

	get_tree().change_scene_to_file("res://scenes/TitleCard.tscn")
