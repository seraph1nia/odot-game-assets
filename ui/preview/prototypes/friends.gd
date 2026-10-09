extends VBoxContainer
signal invite_requested(friend_id: int)
var buttons: Dictionary = {}
var available = true
var status: Label
var rows: VBoxContainer
func _ready() -> void:
	WatchUI.label(self, "Invite Steam friends", "HeadingLabel")
	WatchUI.label(self, "Your friend needs their own copy of The Common Watch running.", "ContextLabel")
	var sample = OptionButton.new()
	sample.name = "Availability"
	for text in ["Mock friends", "Offline", "Empty list"]: sample.add_item(text)
	add_child(sample)
	sample.item_selected.connect(func(index): available = index != 1; refresh(index == 2))
	var refresh_button = WatchUI.button(self, "Refresh")
	refresh_button.name = "Refresh"
	refresh_button.pressed.connect(func(): refresh(false))
	var scroll = ScrollContainer.new()
	scroll.name = "FriendScroll"
	scroll.custom_minimum_size.y = 260
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	add_child(scroll)
	rows = WatchUI.stack(scroll)
	status = WatchUI.label(self, "", "ContextLabel")
	refresh(false)
func refresh(empty: bool) -> void:
	WatchUI.clear(rows)
	buttons.clear()
	if not empty:
		for i in range(14):
			var id = 1000 + i
			var row = WatchUI.row(rows)
			var label = WatchUI.label(row, "Morgan (…"+str(id)+") — " + ("Online" if i < 4 else "Offline"))
			label.autowrap_mode = TextServer.AUTOWRAP_OFF
			label.clip_text = true
			label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			label.tooltip_text = label.text
			var b = WatchUI.button(row, "Invite")
			b.size_flags_horizontal = Control.SIZE_SHRINK_END
			b.custom_minimum_size.x = 82
			b.disabled = not available
			b.pressed.connect(func(): request_invite(id))
			buttons[id] = b
	status.text = "Open Steam and log in, then refresh." if not available else "No Steam friends found." if empty else "Mock names only. Choose a friend; no platform calls."
func request_invite(id: int) -> void:
	for b in buttons.values(): b.disabled = true
	status.text = "Sending invitation… (mock)"
	invite_requested.emit(id)
	finish_invite.call_deferred()
func finish_invite() -> void:
	status.text = "Mock invitation requested; nothing sent."
	for b in buttons.values(): b.disabled = not available
