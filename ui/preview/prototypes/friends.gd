extends VBoxContainer
# Mock projections of platform feedback only; no Steam queries or timers/services.
signal invite_requested(friend_id: int)
var buttons: Dictionary = {}
var available = true
var busy = false
var mode = "populated"
var status: Label
var rows: VBoxContainer
func _ready() -> void:
	WatchUI.label(self, "Invite Steam friends", "HeadingLabel")
	WatchUI.label(self, "Your friend needs their own copy of The Common Watch running.", "ContextLabel")
	var sample = OptionButton.new()
	sample.name = "Availability"
	var modes = ["populated", "offline", "empty", "busy", "refresh-failure", "invite-failure", "long-names"]
	for text in ["Mock friends", "Offline", "Empty list", "Sending", "Refresh failure", "Invite failure", "Long duplicate names"]: sample.add_item(text)
	add_child(sample)
	sample.item_selected.connect(func(index):
		mode = modes[index]
		available = mode != "offline"
		busy = mode == "busy"
		refresh(mode == "empty"))
	var refresh_button = WatchUI.button(self, "Refresh")
	refresh_button.name = "Refresh"
	refresh_button.pressed.connect(func(): refresh(mode == "empty"))
	var scroll = WatchUI.scroll(self, "FriendScroll", 260)
	rows = WatchUI.stack(scroll)
	status = WatchUI.label(self, "", "ContextLabel")
	status.name = "Feedback"
	refresh(false)
func refresh(empty: bool) -> void:
	WatchUI.clear(rows)
	buttons.clear()
	if mode == "refresh-failure":
		status.text = "Mock refresh failed. Retry Refresh; no platform request made."
		return
	if not empty:
		for i in range(14):
			var id = 1000 + i
			var row = WatchUI.row(rows)
			var name = "Morgan of the extraordinarily long cooperative village name" if mode == "long-names" else "Morgan"
			var label = WatchUI.label(row, name + " (…"+str(id)+") — " + ("Online" if i < 4 else "Offline"))
			label.name = "FriendName"
			label.autowrap_mode = TextServer.AUTOWRAP_OFF
			label.clip_text = true
			label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			label.tooltip_text = label.text
			var b = WatchUI.button(row, "Invite")
			b.size_flags_horizontal = Control.SIZE_SHRINK_END
			b.custom_minimum_size.x = 82
			b.disabled = not available or busy
			b.pressed.connect(func(): request_invite(id))
			buttons[id] = b
	status.text = "Sending invitation… (mock)" if busy else "Open Steam and log in, then refresh." if not available else "No Steam friends found." if empty else "Mock names only. Choose a friend; no platform calls."
func request_invite(id: int) -> void:
	if not available or busy or not buttons.has(id): return
	busy = true
	for b in buttons.values(): b.disabled = true
	status.text = "Sending invitation… (mock)"
	invite_requested.emit(id)
	finish_invite.call_deferred()
func finish_invite() -> void:
	busy = false
	status.text = "Mock invitation failed; retry is available." if mode == "invite-failure" else "Mock invitation requested; nothing sent."
	for b in buttons.values(): b.disabled = not available
