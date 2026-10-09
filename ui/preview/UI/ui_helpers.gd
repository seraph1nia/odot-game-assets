class_name WatchUI
extends RefCounted
# Small native-layout helpers, not a replacement widget framework.
static func label(parent: Node, text: String, role: String = "") -> Label:
	var l = Label.new()
	l.text = text
	l.theme_type_variation = role
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l

static func button(parent: Node, title: String, variant: String = "") -> Button:
	var b = Button.new()
	b.text = title
	b.theme_type_variation = variant
	b.custom_minimum_size.y = 36
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(b)
	return b

# A modal/parent scroll owns the whole body; standalone lists keep their own scroll.
static func scroll(parent: Node, name: String, minimum_height: int) -> ScrollContainer:
	var s = ScrollContainer.new()
	s.name = name
	s.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	s.follow_focus = true
	var ancestor = parent
	var inherited = false
	while ancestor != null:
		if ancestor is ScrollContainer and ancestor.vertical_scroll_mode != ScrollContainer.SCROLL_MODE_DISABLED:
			inherited = true
			break
		ancestor = ancestor.get_parent()
	s.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED if inherited else ScrollContainer.SCROLL_MODE_AUTO
	s.custom_minimum_size.y = 0 if inherited else minimum_height
	parent.add_child(s)
	return s

static func stack(parent: Node, spacing: int = 8) -> VBoxContainer:
	var v = VBoxContainer.new()
	v.add_theme_constant_override("separation", spacing)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(v)
	return v

static func row(parent: Node, spacing: int = 8) -> HBoxContainer:
	var h = HBoxContainer.new()
	h.add_theme_constant_override("separation", spacing)
	h.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parent.add_child(h)
	return h

static func clear(parent: Node) -> void:
	for child in parent.get_children():
		parent.remove_child(child)
		child.queue_free()

static func component(path: String, parent: Node) -> Control:
	var scene = load("res://UI/components/" + path + ".tscn")
	var c = scene.instantiate()
	parent.add_child(c)
	return c
