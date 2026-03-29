## API.gd
## Autoload singleton. Handles all HTTP communication with the Python engine.
## All calls are async — listen to request_completed / request_failed signals.

extends Node

const BASE_URL = "http://localhost:8000"

signal request_completed(endpoint: String, data: Variant)
signal request_failed(endpoint: String, error: String)


# --- Public API ---

func get_corpus() -> void:
	_http_get("/corpus")

func get_scenes() -> void:
	_http_get("/scenes")

func get_scene_detail(index: int) -> void:
	_http_get("/scenes/%d" % index)

func get_graph() -> void:
	_http_get("/graph")

func get_operations() -> void:
	_http_get("/curate/operations")

func merge_scenes(indices: Array, heading: String) -> void:
	_http_post("/curate/merge", {
		"level": "scene",
		"indices": indices,
		"heading": heading
	})

func split_scene(index: int, at_child_index: int,
				 heading_before: String, heading_after: String) -> void:
	_http_post("/curate/split", {
		"level": "scene",
		"index": index,
		"at_child_index": at_child_index,
		"heading_before": heading_before,
		"heading_after": heading_after
	})

func rename_scene(index: int, heading: String) -> void:
	_http_post("/curate/rename", {
		"level": "scene",
		"index": index,
		"heading": heading
	})

func save_curated() -> void:
	_http_post("/curate/save", {})

func reload_graph() -> void:
	_http_post("/curate/reload", {})


# --- Internals ---

func _http_get(endpoint: String) -> void:
	var http := HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(
		_on_completed.bind(endpoint, http)
	)
	var err := http.request(BASE_URL + endpoint)
	if err != OK:
		_fail(endpoint, "Request error: %d" % err)
		http.queue_free()


func _http_post(endpoint: String, body: Dictionary) -> void:
	var http := HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(
		_on_completed.bind(endpoint, http)
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := http.request(
		BASE_URL + endpoint,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
	)
	if err != OK:
		_fail(endpoint, "Request error: %d" % err)
		http.queue_free()


func _on_completed(result: int, code: int, _headers: PackedStringArray,
				   body: PackedByteArray, endpoint: String, http: HTTPRequest) -> void:
	http.queue_free()
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		_fail(endpoint, "HTTP %d" % code)
		return
	var json := JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		_fail(endpoint, "JSON parse error")
		return
	request_completed.emit(endpoint, json.data)


func _fail(endpoint: String, error: String) -> void:
	push_error("API [%s]: %s" % [endpoint, error])
	request_failed.emit(endpoint, error)
