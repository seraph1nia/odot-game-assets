extends SceneTree
# Authoring only: saved Theme and editable SVGs are the independent native payload.
func box(bg: String, border: String, padding: int = 8) -> StyleBoxFlat:
	var s = StyleBoxFlat.new()
	s.bg_color = Color(bg)
	s.border_color = Color(border)
	s.set_border_width_all(1)
	s.set_corner_radius_all(10)
	s.set_content_margin_all(padding)
	return s

func painted(path: String, slice: int, padding: int) -> StyleBoxTexture:
	var s = StyleBoxTexture.new()
	s.texture = load("res://UI/art/woodland/" + path + ".svg")
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		s.set_texture_margin(side, 16 if path == "parchment_button" and side in [SIDE_TOP, SIDE_BOTTOM] else slice)
		s.set_content_margin(side, padding)
	return s

func close_mark() -> ImageTexture:
	var image = Image.create(16, 16, false, Image.FORMAT_RGBA8)
	image.fill(Color.TRANSPARENT)
	for y in range(3, 13):
		for x in range(3, 13):
			if abs(x-y) <= 1 or abs(x+y-15) <= 1: image.set_pixel(x, y, Color("f2e6cb"))
	return ImageTexture.create_from_image(image)

func _initialize() -> void:
	var t = Theme.new()
	t.default_font = load("res://UI/fonts/DejaVuSerif.ttf")
	t.default_font_size = 14
	for type in ["Label", "RichTextLabel", "Button", "OptionButton", "TabBar", "TabContainer", "PopupMenu", "CheckBox", "CheckButton", "LineEdit", "SpinBox", "TooltipLabel"]:
		for color in ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color", "font_selected_color"]:
			t.set_color(color, type, Color("f2e6cb"))
		t.set_color("font_disabled_color", type, Color("aaa394"))
		t.set_color("font_unselected_color", type, Color("d1c5ad"))
	t.set_color("default_color", "RichTextLabel", Color("f2e6cb"))
	for type in ["PanelContainer", "TabContainer", "AcceptDialog"]:
		t.set_stylebox("panel", type, painted("branch_frame", 40, 16))
	for type in ["PopupMenu", "TooltipPanel"]:
		t.set_stylebox("panel", type, box("181c26", "947347", 12))
	var mark = close_mark()
	for type in ["Window", "AcceptDialog", "ConfirmationDialog"]:
		var border = box("181c26", "947347", 12)
		border.expand_margin_top = 30
		t.set_stylebox("embedded_border", type, border)
		t.set_stylebox("embedded_unfocused_border", type, border)
		t.set_color("title_color", type, Color("f2e6cb"))
		t.set_color("title_unfocused_color", type, Color("d1c5ad"))
		t.set_constant("title_height", type, 28)
		t.set_icon("close", type, mark)
		t.set_icon("close_pressed", type, mark)
	t.set_type_variation("InformationPanel", "PanelContainer")
	t.set_stylebox("panel", "InformationPanel", painted("branch_frame", 40, 16))
	t.set_type_variation("InsetPanel", "PanelContainer")
	t.set_stylebox("panel", "InsetPanel", box("20232c", "574b46", 8))
	t.set_type_variation("QuotedPanel", "PanelContainer")
	t.set_stylebox("panel", "QuotedPanel", painted("parchment_button", 24, 6))
	t.set_color("font_color", "QuotedPanel", Color("30251e"))
	t.set_type_variation("QuoteLabel", "Label")
	t.set_color("font_color", "QuoteLabel", Color("30251e"))
	t.set_type_variation("QuoteReasonLabel", "Label")
	t.set_color("font_color", "QuoteReasonLabel", Color("584332"))
	t.set_font_size("font_size", "QuoteReasonLabel", 12)
	t.set_type_variation("ContextLabel", "Label")
	t.set_color("font_color", "ContextLabel", Color("d1c5ad"))
	t.set_font_size("font_size", "ContextLabel", 12)
	t.set_type_variation("HeadingLabel", "Label")
	t.set_font_size("font_size", "HeadingLabel", 18)
	var focus = box("00000000", "8acde4", 0)
	focus.set_border_width_all(2)
	for type in ["Button", "OptionButton", "PrimaryButton", "DangerButton", "MagicButton", "ReadyButton", "CardButton"]:
		if type not in ["Button", "OptionButton"]: t.set_type_variation(type, "Button")
		for state in ["normal", "hover", "pressed", "disabled"]:
			var color = Color("30282a")
			if type == "DangerButton": color = Color("603c3d")
			if type == "MagicButton": color = Color("493063")
			if type == "ReadyButton": color = Color("264d3d")
			if state == "hover": color = color.lightened(.12)
			if state == "pressed": color = color.darkened(.12)
			if state == "disabled": color = Color("29292c")
			var style: StyleBox = box(color.to_html(), "97714c", 8)
			if type == "PrimaryButton":
				style = painted("parchment_button", 24, 10)
				style.modulate_color = Color("ffffff") if state == "normal" else Color("ffe9b8") if state == "hover" else Color("c8ac80") if state == "pressed" else Color("857e75")
			if type == "CardButton": style = box("ffffff18" if state == "hover" else "00000018" if state == "pressed" else "00000000", "00000000", 2)
			t.set_stylebox(state, type, style)
		var ink = Color("30251e") if type in ["PrimaryButton", "CardButton"] else Color("f2e6cb")
		for color_name in ["font_color", "font_focus_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color"]: t.set_color(color_name, type, ink)
		t.set_color("font_disabled_color", type, Color("65594a") if type in ["PrimaryButton", "CardButton"] else Color("aaa394"))
		t.set_stylebox("focus", type, focus)
	for type in ["TabContainer", "TabBar"]:
		t.set_stylebox("tab_selected", type, box("64462d", "e5b46d"))
		t.set_stylebox("tab_unselected", type, box("28252c", "785d45"))
		t.set_stylebox("tab_hovered", type, box("54402e", "e5b46d"))
		t.set_stylebox("tab_disabled", type, box("29292c", "574c44"))
		t.set_stylebox("tab_focus", type, focus)
	t.set_stylebox("hover", "PopupMenu", box("64462d", "e5b46d"))
	t.set_stylebox("normal", "LineEdit", box("111722", "947347"))
	t.set_stylebox("focus", "LineEdit", focus)
	for type in ["HSlider", "HScrollBar", "VScrollBar"]:
		t.set_stylebox("slider" if type == "HSlider" else "scroll", type, box("252a33", "574c44", 3))
		t.set_stylebox("grabber_area" if type == "HSlider" else "grabber", type, box("947347", "ba965d", 3))
		t.set_stylebox("grabber_area_highlight" if type == "HSlider" else "grabber_highlight", type, box("dbad60", "ba965d", 3))
		t.set_stylebox("focus", type, focus)
	t.set_stylebox("background", "ProgressBar", box("20232c", "655444", 2))
	t.set_stylebox("fill", "ProgressBar", box("7961b5", "b497df", 2))
	var error = ResourceSaver.save(t, "res://UI/theme/ledger.tres")
	if error != OK:
		push_error("Theme export failed: " + str(error))
		quit(1)
		return
	print("UI_THEME exported native woodland Ledger theme")
	quit()
