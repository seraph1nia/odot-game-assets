extends SceneTree
# Production authoring tool only. The saved Theme has no dependency on this script.
func box(bg: String, border: String, padding: int = 8) -> StyleBoxFlat:
	var s = StyleBoxFlat.new()
	s.bg_color = Color(bg)
	s.border_color = Color(border)
	s.set_border_width_all(1)
	s.set_corner_radius_all(6)
	s.set_content_margin_all(padding)
	return s

func close_mark() -> ImageTexture:
	# Original native semantic mark, embedded in Theme; not a decorative art family.
	var image = Image.create(16, 16, false, Image.FORMAT_RGBA8)
	image.fill(Color.TRANSPARENT)
	for y in range(3, 13):
		for x in range(3, 13):
			if abs(x-y) <= 1 or abs(x+y-15) <= 1: image.set_pixel(x, y, Color("302f2a"))
	return ImageTexture.create_from_image(image)

func _initialize() -> void:
	var t = Theme.new()
	t.default_font_size = 14
	for type in ["Label", "RichTextLabel", "Button", "OptionButton", "TabBar", "TabContainer", "PopupMenu", "CheckBox", "CheckButton", "LineEdit", "SpinBox", "TooltipLabel"]:
		for color in ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color", "font_selected_color"]:
			t.set_color(color, type, Color("302f2a"))
		t.set_color("font_disabled_color", type, Color("736e60"))
		t.set_color("font_unselected_color", type, Color("605d50"))
	t.set_color("default_color", "RichTextLabel", Color("302f2a"))
	for type in ["PanelContainer", "PopupMenu", "TabContainer", "TooltipPanel", "AcceptDialog"]:
		t.set_stylebox("panel", type, box("efe4cd", "a99b7e", 12))
	var mark = close_mark()
	for type in ["Window", "AcceptDialog", "ConfirmationDialog"]:
		var border = box("efe4cd", "a99b7e", 12)
		border.expand_margin_top = 30
		t.set_stylebox("embedded_border", type, border)
		t.set_stylebox("embedded_unfocused_border", type, border)
		t.set_color("title_color", type, Color("302f2a"))
		t.set_color("title_unfocused_color", type, Color("605d50"))
		t.set_constant("title_height", type, 28)
		t.set_icon("close", type, mark)
		t.set_icon("close_pressed", type, mark)
	t.set_type_variation("InformationPanel", "PanelContainer")
	t.set_stylebox("panel", "InformationPanel", box("efe4cd", "a99b7e", 8))
	t.set_type_variation("InsetPanel", "PanelContainer")
	t.set_stylebox("panel", "InsetPanel", box("e6dbc4", "c6b99d", 8))
	t.set_type_variation("ContextLabel", "Label")
	t.set_color("font_color", "ContextLabel", Color("605d50"))
	t.set_font_size("font_size", "ContextLabel", 12)
	t.set_type_variation("HeadingLabel", "Label")
	t.set_font_size("font_size", "HeadingLabel", 18)
	var focus = box("00000000", "23889b", 0)
	focus.set_border_width_all(2)
	for type in ["Button", "OptionButton", "PrimaryButton", "DangerButton"]:
		if type.ends_with("Button") and type not in ["Button", "OptionButton"]:
			t.set_type_variation(type, "Button")
		var base = "e6dbc4"
		if type == "PrimaryButton": base = "f0c779"
		if type == "DangerButton": base = "e2c4b7"
		for state in ["normal", "hover", "pressed", "disabled"]:
			var color = Color(base)
			if state == "hover": color = color.lightened(.06)
			if state == "pressed": color = color.darkened(.07)
			if state == "disabled": color = Color("ded5c0")
			t.set_stylebox(state, type, box(color.to_html(), "a99b7e", 8))
			t.set_color("font_" + state + "_color", type, Color("736e60") if state == "disabled" else Color("302f2a"))
		for color in ["font_color", "font_focus_color", "font_hover_pressed_color"]:
			t.set_color(color, type, Color("302f2a"))
		t.set_stylebox("focus", type, focus)
	for type in ["TabContainer", "TabBar"]:
		t.set_stylebox("tab_selected", type, box("f0c779", "a99b7e"))
		t.set_stylebox("tab_unselected", type, box("e6dbc4", "a99b7e"))
		t.set_stylebox("tab_hovered", type, box("f3d496", "a99b7e"))
		t.set_stylebox("tab_disabled", type, box("ded5c0", "a99b7e"))
		t.set_stylebox("tab_focus", type, focus)
	t.set_stylebox("hover", "PopupMenu", box("f0c779", "a99b7e"))
	t.set_stylebox("normal", "LineEdit", box("f5eddd", "a99b7e"))
	t.set_stylebox("focus", "LineEdit", focus)
	for type in ["HSlider", "HScrollBar", "VScrollBar"]:
		t.set_stylebox("slider" if type == "HSlider" else "scroll", type, box("b7a990", "a99b7e", 3))
		t.set_stylebox("grabber_area" if type == "HSlider" else "grabber", type, box("b28a49", "a99b7e", 3))
		t.set_stylebox("grabber_area_highlight" if type == "HSlider" else "grabber_highlight", type, box("d5a855", "a99b7e", 3))
		t.set_stylebox("focus", type, focus)
	t.set_stylebox("background", "ProgressBar", box("b7a990", "a99b7e", 2))
	t.set_stylebox("fill", "ProgressBar", box("b36651", "a99b7e", 2))
	var error = ResourceSaver.save(t, "res://UI/theme/ledger.tres")
	if error != OK:
		push_error("Theme export failed: " + str(error))
		quit(1)
		return
	print("UI_THEME exported native Ledger theme")
	quit()
