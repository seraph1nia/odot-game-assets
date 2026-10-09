extends PanelContainer
signal requested(action_id: String)
var multiplayer_view = false
var offline = true
func _ready() -> void:
	show_menu()
func show_menu() -> void:
	WatchUI.clear($Body)
	var seal = TextureRect.new()
	seal.texture = load("res://UI/art/menu_seal.png")
	seal.custom_minimum_size = Vector2(48, 48)
	seal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	seal.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	$Body.add_child(seal)
	var title = WatchUI.label($Body, "The Common Watch")
	title.add_theme_font_size_override("font_size", 30)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var subtitle = WatchUI.label($Body, "Build and provision your village.\nHold together against automatic waves.", "ContextLabel")
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	$Body.add_child(HSeparator.new())
	if multiplayer_view:
		WatchUI.label($Body, "Host a private game, then invite Steam friends.\nInvitations join through the game platform.")
		var host = WatchUI.button($Body, "Host game", "PrimaryButton")
		host.pressed.connect(func(): requested.emit("host"))
		var back = WatchUI.button($Body, "Back")
		back.pressed.connect(func(): multiplayer_view = false; show_menu())
		host.grab_focus()
	else:
		for item in [["Single player", "solo"], ["Multiplayer", "multiplayer"], ["Settings", "settings"], ["Exit Game", "exit"]]:
			var id = item[1]
			var b = WatchUI.button($Body, item[0], "PrimaryButton" if id == "solo" else "")
			b.name = id.capitalize()
			b.pressed.connect(func():
				if id == "multiplayer": multiplayer_view = true; show_menu()
				else: requested.emit(id))
			if id == "solo": b.grab_focus()
	WatchUI.label($Body, "Open Steam to log in" if offline else "Mock friend · online", "ContextLabel")
