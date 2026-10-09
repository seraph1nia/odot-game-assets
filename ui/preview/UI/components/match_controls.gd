extends VBoxContainer
signal requested(action_id: String)
var data: Dictionary = {}
func _ready() -> void:
	$Ready.pressed.connect(func(): requested.emit(str(data.get("ready_id", "ready"))))
	$Pause.pressed.connect(func(): requested.emit(str(data.get("pause_id", "pause"))))
	$Start.pressed.connect(func(): requested.emit("start"))
func set_data(value: Dictionary) -> void:
	data = value.duplicate(true)
	$Phase.text = str(data.get("phase", "Lobby"))
	$Counters.text = str(data.get("counters", ""))
	$Ready.text = str(data.get("ready_label", "Ready"))
	$Ready.disabled = not bool(data.get("can_ready", false))
	$Ready.visible = bool(data.get("show_ready", true)) and not bool(data.get("terminal", false))
	$Pause.text = str(data.get("pause_label", "Pause whole match"))
	$Pause.disabled = not bool(data.get("can_pause", false))
	$Pause.visible = bool(data.get("show_pause", true))
	$Start.visible = bool(data.get("show_start", false))
	$Start.disabled = not bool(data.get("can_start", false))
	$Context.text = str(data.get("context", ""))
	$Context.visible = bool(data.get("show_context", true))
