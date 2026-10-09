extends Control
# Approval-only layouts; not production components or gameplay adapters.
var direction := "ledger"
var composition := "hud"
var capture := ""
var ink: Color
var muted: Color
var surface: Color
var edge: Color
var accent: Color

func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--direction="): direction = arg.get_slice("=", 1)
		if arg.begins_with("--composition="): composition = arg.get_slice("=", 1)
		if arg.begins_with("--capture="): capture = arg.trim_prefix("--capture=")
	var light := direction == "ledger"
	ink = Color("302f2a") if light else Color("f3e9d4")
	muted = Color("605d50") if light else Color("b7c5c7")
	surface = Color("efe4cd") if light else Color("243940")
	edge = Color("a99b7e") if light else Color("647c82")
	accent = Color("f0c779") if light else Color("385764")
	theme = make_theme()
	backdrop()
	var caption := label(self, "EXPLORATION  /  " + direction.to_upper() + "  /  " + composition.to_upper() + "  ·  mock data", 13)
	caption.position = Vector2(18, 14)
	if composition == "hud": hud()
	else: menu()
	await get_tree().process_frame
	await get_tree().process_frame
	if not capture.is_empty():
		await RenderingServer.frame_post_draw
		var result := get_viewport().get_texture().get_image().save_png(capture)
		if result != OK:
			push_error("Capture failed: " + str(result))
			get_tree().quit(1)
		else:
			print("CAPTURE ", direction, " ", composition, " ", get_viewport_rect().size)
			get_tree().quit()

func flat(color: Color, border: Color, padding := 12) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.set_content_margin_all(padding)
	return style

func make_theme() -> Theme:
	var t := Theme.new()
	t.default_font_size = 14
	t.set_color("font_color", "Label", ink)
	t.set_stylebox("panel", "PanelContainer", flat(surface, edge, 16))
	for state in ["normal", "hover", "pressed", "disabled"]:
		var color := accent
		if state == "hover": color = accent.lightened(.12)
		if state == "pressed": color = accent.darkened(.12)
		if state == "disabled": color = surface.darkened(.08)
		t.set_stylebox(state, "Button", flat(color, edge, 8))
		t.set_color("font_" + state + "_color", "Button", muted if state == "disabled" else ink)
	for name in ["font_color", "font_focus_color", "font_hover_pressed_color"]:
		t.set_color(name, "Button", ink)
	var focus := flat(Color.TRANSPARENT, Color("23889b") if direction == "ledger" else Color("e8c57e"), 0)
	focus.set_border_width_all(2)
	t.set_stylebox("focus", "Button", focus)
	return t

func label(parent: Node, text: String, px := 14, subdued := false) -> Label:
	var node := Label.new()
	node.text = text
	node.add_theme_font_size_override("font_size", px)
	if subdued: node.add_theme_color_override("font_color", muted)
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(node)
	return node

func button(parent: Node, text: String, disabled := false) -> Button:
	var node := Button.new()
	node.text = text
	node.disabled = disabled
	node.custom_minimum_size.y = 36
	node.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(node)
	return node

func stack(parent: Node, spacing := 8) -> VBoxContainer:
	var node := VBoxContainer.new()
	node.add_theme_constant_override("separation", spacing)
	parent.add_child(node)
	return node

func panel_at(rect: Rect2) -> PanelContainer:
	var node := PanelContainer.new()
	add_child(node)
	node.position = rect.position
	node.size = rect.size
	return node

func backdrop() -> void:
	var bg := ColorRect.new()
	bg.color = Color("718982")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	# Original abstract tabletop field: layout context, not a game screenshot or art acceptance.
	var width := get_viewport_rect().size.x
	for row in range(5):
		for column in range(7):
			var tile := Polygon2D.new()
			var points := PackedVector2Array()
			for i in range(6): points.append(Vector2(cos(i * TAU / 6), sin(i * TAU / 6)) * 42 * Vector2(1.0, .58))
			tile.polygon = points
			tile.position = Vector2(width * .43 + (column - 3) * 66, 130 + row * 48 + (column % 2) * 24)
			tile.color = Color("a3ac78") if (row + column) % 3 else Color("939f70")
			add_child(tile)
	var note := label(self, "Abstract tabletop context — not a current game capture", 12)
	note.position = Vector2(18, 38)

func seal(parent: Node) -> void:
	var image := TextureRect.new()
	image.texture = load("res://art/explorations/" + direction + "_seal.png")
	image.custom_minimum_size = Vector2(48, 48)
	image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	image.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(image)

func hud() -> void:
	var view := get_viewport_rect().size
	var resources := panel_at(Rect2(view.x - 272, 48, 260, 0))
	var body := stack(resources, 7)
	label(body, "P1 · YOUR CITY", 14)
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 14)
	grid.add_theme_constant_override("v_separation", 4)
	body.add_child(grid)
	for text in ["Resource", "Stock", "Income/turn"]: label(grid, text, 12, true)
	for row in [["Gold", "24", "+2"], ["Food", "15", "+5"], ["Wood", "8", "+1"], ["Stone", "4", "0"], ["Metal", "12", "+4"], ["Cloth", "0", "0"]]:
		for index in range(3):
			var value := label(grid, row[index], 14)
			if index > 0:
				value.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	body.add_child(HSeparator.new())
	label(body, "UPKEEP · NEXT BATTLE", 12, true)
	label(body, "Payment                         6 food", 14)
	label(body, "Food after payment                 9", 14)
	var bottom := panel_at(Rect2(12, view.y - 190, view.x - 24, 178))
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 24)
	bottom.add_child(columns)
	var city := stack(columns)
	city.custom_minimum_size.x = 205
	label(city, "P1 · Your city", 18)
	label(city, "City 100/100 · Army 6", 14)
	button(city, "Details")
	button(city, "Research")
	var context := stack(columns)
	context.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label(context, "Metal mine · Level 1", 20)
	label(context, "Produces 4 metal each building turn", 14)
	label(context, "Upgrade: 2 wood · 2 stone → 8 metal/turn", 13, true)
	var actions := HBoxContainer.new()
	context.add_child(actions)
	button(actions, "Upgrade")
	button(actions, "Sell · 1 wood")
	label(context, "Connected · mock inspection", 12, true)
	var match_controls := stack(columns)
	match_controls.custom_minimum_size.x = 230
	label(match_controls, "Building · Wave 2", 18)
	label(match_controls, "Production 2 of 3", 14, true)
	button(match_controls, "Ready").grab_focus()
	button(match_controls, "Pause whole match")

func menu() -> void:
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var panel := PanelContainer.new()
	panel.custom_minimum_size.x = 460
	center.add_child(panel)
	var body := stack(panel, 12)
	seal(body)
	var title := label(body, "The Common Watch", 30)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var subtitle := label(body, "Build and provision your village.\nHold together against automatic waves.", 14, true)
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(HSeparator.new())
	button(body, "Single player").grab_focus()
	button(body, "Multiplayer")
	button(body, "Settings")
	button(body, "Exit Game")
	label(body, "Open Steam to log in", 13, true)
	label(body, "State sample: unavailable action", 12, true)
	button(body, "Host game · login required", true)
