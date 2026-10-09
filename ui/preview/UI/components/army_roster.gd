extends PanelContainer
signal unit_selected(unit_id: int)
var buttons: Dictionary = {}
func set_data(data: Dictionary) -> void:
	WatchUI.clear($Body)
	buttons.clear()
	WatchUI.label($Body, str(data.get("title", "Army roster")), "HeadingLabel")
	WatchUI.label($Body, str(data.get("context", "")), "ContextLabel")
	var tiles = GridContainer.new()
	tiles.columns = 3
	$Body.add_child(tiles)
	for tile in data.get("tiles", []):
		WatchUI.label(tiles, str(tile), "ContextLabel")
	var scroll = ScrollContainer.new()
	scroll.name = "RosterScroll"
	scroll.custom_minimum_size.y = 180
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	$Body.add_child(scroll)
	var rows = WatchUI.stack(scroll)
	for unit in data.get("units", []):
		var id = int(unit.get("id", -1))
		var b = WatchUI.button(rows, str(unit.get("label", "Unit")))
		b.toggle_mode = true
		b.button_pressed = id == int(data.get("selected_id", -1))
		b.pressed.connect(func(): unit_selected.emit(id))
		buttons[id] = b
		WatchUI.label(rows, str(unit.get("detail", "")), "ContextLabel")
	if buttons.is_empty(): WatchUI.label(rows, "No units in this roster")
