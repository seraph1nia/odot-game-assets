extends Control
# Standalone composition host: all actions are mock intents, never gameplay.
var screen_mode = "hud"
var state = "building"
var selection = "Producer"
var dialog: WatchModal
var active_confirmation: WatchModal
var dialog_content: Control
var dialog_opener: Control
var last_action = ""
var world_clicks = 0
var navigation: Control
var ledger: Control
var upkeep: Control
var match_controls: Control
var feedback: Control
var status_line: Label
var context: VBoxContainer
var actions: Array = []
var capture_path = ""

func _ready() -> void:
	get_window().gui_embed_subwindows = true
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screen="): screen_mode = arg.get_slice("=", 1)
		if arg.begins_with("--state="): state = arg.get_slice("=", 1)
		if arg.begins_with("--capture="): capture_path = arg.trim_prefix("--capture=")
	build()
	if screen_mode not in ["hud", "menu"]: open_dialog(screen_mode)
	if not capture_path.is_empty():
		await settle()
		await RenderingServer.frame_post_draw
		var result = get_viewport().get_texture().get_image().save_png(capture_path)
		if result != OK: push_error("UI capture failed"); get_tree().quit(1)
		else: print("UI_CAPTURE ", screen_mode, " ", state); get_tree().quit()

func settle() -> void:
	for i in range(4): await get_tree().process_frame

func build() -> void:
	var bg = ColorRect.new()
	bg.color = Color("718982")
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var margin = MarginContainer.new()
	margin.name = "Layout"
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "top", "right", "bottom"]: margin.add_theme_constant_override("margin_" + side, 12)
	add_child(margin)
	var body = WatchUI.stack(margin, 12)
	var toolbar = WatchUI.row(body)
	WatchUI.label(toolbar, "THE COMMON WATCH · UI PREVIEW", "ContextLabel")
	var scenes = OptionButton.new()
	scenes.name = "ScreenSelector"
	var screens = ["hud", "menu", "research", "town_hall", "settings", "details", "friends", "components"]
	for name in screens: scenes.add_item(name.capitalize())
	toolbar.add_child(scenes)
	scenes.select(max(0, screens.find(screen_mode)))
	scenes.item_selected.connect(func(index): switch_screen.call_deferred(screens[index]))
	var states = OptionButton.new()
	states.name = "StateSelector"
	var state_names = ["building", "ready", "preparation", "combat", "shortage", "foreign", "paused", "lost", "victory", "defeat"]
	for name in state_names: states.add_item(name.capitalize())
	states.select(max(0, state_names.find(state)))
	toolbar.add_child(states)
	states.item_selected.connect(func(index): state = state_names[index]; refresh_hud())
	var settings_button = WatchUI.button(toolbar, "Settings")
	settings_button.size_flags_horizontal = Control.SIZE_SHRINK_END
	settings_button.name = "Settings"
	settings_button.pressed.connect(func(): open_dialog("settings", settings_button))
	var area = Control.new()
	area.name = "Content"
	area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(area)
	build_content()

func switch_screen(mode: String) -> void:
	close_dialog()
	screen_mode = mode
	if mode in ["hud", "menu"]: build_content()
	else:
		if ledger == null or not is_instance_valid(ledger): screen_mode = "hud"; build_content(); screen_mode = mode
		open_dialog(mode)

func build_content() -> void:
	var area = $Layout.get_child(0).get_node("Content")
	WatchUI.clear(area)
	ledger = null
	var field_note = WatchUI.label(area, "Original abstract tabletop context · mock data · no game services", "ContextLabel")
	field_note.position = Vector2(8, 8)
	field_note.size = Vector2(590, 24)
	var width = get_viewport_rect().size.x
	for row in range(5):
		for column in range(7):
			var tile = Polygon2D.new()
			var points = PackedVector2Array()
			for i in range(6): points.append(Vector2(cos(i * TAU / 6), sin(i * TAU / 6)) * 38 * Vector2(1, .58))
			tile.polygon = points
			tile.position = Vector2(width * .40 + (column-3)*60, 80+row*44+(column%2)*22)
			tile.color = Color("a3ac78") if (row+column)%3 else Color("939f70")
			area.add_child(tile)
	if screen_mode == "menu":
		var center = CenterContainer.new()
		center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		area.add_child(center)
		var menu = load("res://prototypes/menu.tscn").instantiate()
		center.add_child(menu)
		menu.requested.connect(func(id):
			if id == "solo": switch_screen("hud")
			elif id == "settings": open_dialog("settings", menu.get_node("Body/Settings"))
			elif id == "exit": confirm("Exit Game", "Exit request only: this preview does not end a game session.", "exit")
			else: last_action = id)
		return
	var right = VBoxContainer.new()
	right.name = "Information"
	right.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	right.offset_left = -260
	right.offset_top = 0
	area.add_child(right)
	ledger = WatchUI.component("resource_ledger", right)
	upkeep = WatchUI.component("upkeep_summary", right)
	var footer = PanelContainer.new()
	footer.name = "HudFooter"
	footer.grow_vertical = Control.GROW_DIRECTION_BEGIN
	footer.theme_type_variation = "InformationPanel"
	footer.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	footer.offset_top = -224
	area.add_child(footer)
	var columns = WatchUI.row(footer, 16)
	var city = WatchUI.stack(columns)
	city.custom_minimum_size.x = 220
	city.size_flags_horizontal = Control.SIZE_FILL
	navigation = WatchUI.component("city_navigation", city)
	navigation.city_requested.connect(func(id): state = "foreign" if id == 2 else "building"; refresh_hud())
	WatchUI.label(city, "City 100/100 · Army 6")
	var links = WatchUI.row(city)
	for item in [["Details", "details"], ["Research", "research"]]:
		var id = item[1]
		var b = WatchUI.button(links, item[0])
		b.pressed.connect(func(): open_dialog(id, b))
	var invite = WatchUI.button(city, "Invite friends")
	invite.pressed.connect(func(): open_dialog("friends", invite))
	status_line = WatchUI.label(city, "Connected · mock", "ContextLabel")
	status_line.max_lines_visible = 2
	context = WatchUI.stack(columns)
	context.name = "Context"
	context.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	context.custom_minimum_size.x = 380
	var picker = OptionButton.new()
	picker.name = "Selection"
	for text in ["Producer", "Empty plot", "Locked plot", "Recruiter", "Market", "Town hall", "Army homes", "Unit"]: picker.add_item(text)
	context.add_child(picker)
	picker.item_selected.connect(func(index): selection = picker.get_item_text(index); refresh_context())
	var context_body = VBoxContainer.new()
	context_body.name = "Actions"
	context.add_child(context_body)
	match_controls = WatchUI.component("match_controls", columns)
	match_controls.requested.connect(record_action)
	feedback = WatchUI.component("session_feedback", match_controls)
	feedback.requested.connect(record_action)
	refresh_hud()

func refresh_hud() -> void:
	if ledger == null or not is_instance_valid(ledger): return
	ledger.set_data(UIFixtures.resources(state))
	upkeep.set_data(UIFixtures.upkeep(state))
	match_controls.set_data(UIFixtures.match_state(state))
	navigation.set_data([{"id":1, "label":"P1 · You", "context":"Owner"}, {"id":2, "label":"P2", "context":"Read-only inspection"}], 2 if state == "foreign" else 1)
	status_line.text = "Disconnected · inspection" if state == "lost" else "Connected · mock" if last_action.is_empty() else last_action
	feedback.visible = state == "lost"
	feedback.set_data({"status":"Reconnect or fresh lobby", "message":"Expired credentials require a fresh session.", "reconnect":state == "lost", "fresh":state == "lost"})
	refresh_context()

func refresh_context() -> void:
	WatchUI.clear(context.get_node("Actions"))
	actions.clear()
	var host = context.get_node("Actions")
	var editable = state in ["building", "preparation", "shortage"]
	var reason = "" if editable else "Read-only while ready, paused, disconnected, in combat or inspecting another city."
	var title = "Metal mine · Level 1"
	var quotes = []
	match selection:
		"Producer":
			quotes = [{"id":"upgrade", "title":"Upgrade", "quote":"2 wood · 2 stone\n4 → 8 metal/turn", "enabled":editable, "variant":"PrimaryButton"}, {"id":"sell", "title":"Sell building", "quote":"Refund 1 wood", "enabled":editable, "variant":"DangerButton"}]
		"Empty plot":
			title = "Purchased plot · Construction"
			var tabs = TabBar.new()
			for name in ["Production", "Army", "Defense", "Trade"]: tabs.add_tab(name)
			host.add_child(tabs)
			tabs.tab_changed.connect(func(index): fill_build_quotes(host.get_node("QuoteScroll/Choices"), index, editable, reason))
		"Locked plot":
			title = "Locked plot · Land expansion"
			quotes = [{"id":"buy-plot", "title":"Buy plot", "quote":"5 gold · purchase is permanent", "enabled":editable, "variant":"PrimaryButton"}]
		"Recruiter":
			title = "Barracks · Level 1"
			var recruiter = OptionButton.new()
			recruiter.name = "RecruiterType"
			for name in ["Barracks", "Archery range", "Magic academy"]: recruiter.add_item(name)
			host.add_child(recruiter)
			recruiter.item_selected.connect(func(index): fill_recruit_quotes(host.get_node("QuoteScroll/Choices"), index, editable, reason))
		"Market":
			title = "Market · Fixed-bundle sales"
			quotes = [{"id":"trade-wood", "title":"Sell wood", "quote":"5 wood → 1 gold", "enabled":editable}, {"id":"trade-stone", "title":"Sell stone", "quote":"5 stone → 1 gold", "enabled":false, "reason":"Need 1 more stone."}, {"id":"trade-metal", "title":"Sell metal", "quote":"5 metal → 2 gold", "enabled":editable}, {"id":"trade-cloth", "title":"Sell cloth", "quote":"5 cloth → 2 gold", "enabled":false, "reason":"Need 5 more cloth."}, {"id":"trade-food", "title":"Sell food", "quote":"25 food → 1 gold", "enabled":false, "reason":"Need 10 more food. Selling food changes battle sit-outs."}]
		"Army homes":
			title = "Army homes · 2 purchased · 12 size points"
			quotes = [{"id":"buy-home", "title":"Buy unit space", "quote":"5 gold · next six-size home", "enabled":editable, "reason":"Six size-two units occupy the current homes. Town hall upgrades never buy field space."}]
		"Town hall":
			title = "Town hall · Storage and healing"
			var b = WatchUI.button(host, "Town hall roster")
			b.pressed.connect(func(): open_dialog("town_hall", b))
			quotes = [{"id":"sell-hall", "title":"Sell building", "quote":"Investment half-refund", "enabled":false, "reason":"Cannot sell an occupied Town hall."}]
		"Unit":
			title = "Knight II · Inspection"
			var b = WatchUI.button(host, "Inspect unit")
			b.pressed.connect(func(): open_dialog("unit", b))
	var heading = WatchUI.label(host, title, "HeadingLabel")
	heading.name = "Heading"
	host.move_child(heading, 0)
	var scroll = ScrollContainer.new()
	scroll.name = "QuoteScroll"
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	scroll.custom_minimum_size.y = 132
	host.add_child(scroll)
	var grid = GridContainer.new()
	grid.name = "Choices"
	grid.columns = 2
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(grid)
	if selection == "Empty plot": fill_build_quotes(grid, 0, editable, reason)
	elif selection == "Recruiter": fill_recruit_quotes(grid, 0, editable, reason)
	else:
		for data in quotes:
			if not editable: data.reason = reason
			add_action(grid, data)

func add_action(parent: Node, data: Dictionary) -> void:
	var card = WatchUI.component("quoted_action", parent)
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.set_data(data)
	card.requested.connect(record_action)
	actions.append(card)

func fill_build_quotes(grid: Node, group: int, editable: bool, reason: String) -> void:
	WatchUI.clear(grid)
	actions.clear()
	var groups = [
		[["Woodcutter hut", "Lumbermill", "1 wood · +1 wood/turn"], ["Bakery", "Farm", "2 wood · +5 food/turn"], ["Gold mine", "Mine", "2 wood · +1 gold/turn"], ["Stonecutter", "Stonecutter", "2 wood · +1 stone/turn"], ["Metal mine", "MetalMine", "2 wood · +4 metal/turn"], ["Weaver", "Weaver", "2 wood · +4 cloth/turn"]],
		[["Barracks", "Barracks", "2 wood"], ["Archery range", "ArcheryRange", "2 wood"], ["Magic academy", "Arcanum", "5 gold · 2 wood · 3 stone"], ["Research tower", "ResearchTower", "2 wood · 2 stone"], ["Town hall", "TownHall", "5 gold · 2 wood · 2 stone"]],
		[["Arrow tower", "ArrowTower", "4 gold · 3 wood"], ["Bombard tower", "CatapultTower", "6 gold · 4 wood · 3 stone · 2 metal"]],
		[["Market", "Market", "2 wood · 2 stone"]]]
	for entry in groups[group]: add_action(grid, {"id":"build-"+entry[1], "title":entry[0], "quote":entry[2], "enabled":editable, "reason":reason})
	if group == 0:
		add_action(grid, {"id":"gold-recovery", "title":"Woodcutter · recovery", "quote":"4 gold · explicit alternative", "enabled":false, "reason":"Only eligible at exactly zero wood."})

func fill_recruit_quotes(grid: Node, role: int, editable: bool, reason: String) -> void:
	grid.get_parent().get_parent().get_node("Heading").text = ["Barracks", "Archery range", "Magic academy"][role] + " · Level 1"
	WatchUI.clear(grid)
	actions.clear()
	var groups = [
		[{"id":"recruit-Swordsman", "title":"Recruit Knight", "quote":"2 metal · size 2 · food 1/battle"}, {"id":"recruit-Berserker", "title":"Recruit Berserker", "quote":"3 metal · size 2 · food 2/battle"}],
		[{"id":"recruit-Crossbowman", "title":"Recruit Archer", "quote":"1 metal · 2 wood · size 2 · food 1/battle"}],
		[{"id":"recruit-Mage", "title":"Recruit Mage", "quote":"3 cloth · 1 gold · size 2 · food 2/battle", "reason":"Need 3 more cloth. Build or upgrade a Weaver."}]]
	for data in groups[role]:
		data.enabled = editable and role != 2
		if not editable: data.reason = reason
		add_action(grid, data)

func record_action(id: String) -> void:
	last_action = "Request: " + id + " (mock; no game change)"
	if status_line != null and is_instance_valid(status_line): status_line.text = last_action

func open_dialog(kind: String, opener: Control = null) -> void:
	close_dialog()
	dialog_opener = opener if opener != null else get_viewport().gui_get_focus_owner()
	dialog = load("res://UI/components/modal.tscn").instantiate()
	dialog.name = "PreviewDialog"
	dialog.title = kind.capitalize().replace("_", " ")
	dialog.invoker = dialog_opener
	add_child(dialog)
	var scroll = dialog.get_content()
	if kind == "unit":
		dialog_content = WatchUI.component("unit_inspection", scroll)
		dialog_content.set_data(UIFixtures.unit())
	elif kind == "components": dialog_content = component_samples(scroll)
	else:
		dialog_content = load("res://prototypes/" + kind + ".tscn").instantiate()
		scroll.add_child(dialog_content)
	dialog_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if state not in ["building", "preparation", "shortage"]:
		var reason = "Read-only: " + state + ". Inspection remains available."
		if kind == "research": dialog_content.read_only_reason = reason; dialog_content.refresh()
		elif kind == "town_hall": dialog_content.set_read_only(reason)
		elif kind == "unit":
			var data = dialog_content.data.duplicate(true)
			data.can_retire = false
			data.can_send = false
			data.reason = reason
			dialog_content.set_data(data)
	if dialog_content.has_signal("requested"):
		if kind == "unit": dialog_content.requested.connect(func(id, _unit, _destination): record_action(id))
		else: dialog_content.requested.connect(record_action)
	if kind == "settings":
		dialog_content.changed.connect(func(key, value): last_action = "Mock " + key + " = " + str(value))
		dialog_content.return_requested.connect(func(): confirm("Return to menu?", "This unsaved session would end. Mock confirmation only.", "return-menu"))
	# The reusable modal owns close/cancel, Tab scope and invoker restoration.
	var width = 760 if kind == "town_hall" else 650 if kind in ["research", "details", "components"] else 560
	dialog.popup_centered_clamped(Vector2i(width, 610 if kind in ["town_hall", "details"] else 540), .9)
	dialog.get_ok_button().grab_focus()

func close_dialog() -> void:
	if dialog != null and is_instance_valid(dialog):
		dialog.close()
		dialog.queue_free()
	dialog = null
	dialog_content = null

func confirm(title: String, message: String, id: String) -> void:
	var confirmation: WatchModal = load("res://UI/components/modal.tscn").instantiate()
	confirmation.title = title
	confirmation.ok_button_text = "Confirm"
	confirmation.confirmation = true
	confirmation.invoker = get_viewport().gui_get_focus_owner()
	add_child(confirmation)
	active_confirmation = confirmation
	WatchUI.label(confirmation.get_content(), message)
	confirmation.confirmed.connect(func():
		record_action(id)
		if id == "return-menu": switch_screen("menu"))
	confirmation.closed.connect(func():
		if active_confirmation == confirmation: active_confirmation = null
		confirmation.queue_free())
	confirmation.popup_centered_clamped(Vector2i(460, 280))

func component_samples(parent: Node) -> Control:
	var body = WatchUI.stack(parent)
	body.custom_minimum_size.x = 570
	WatchUI.label(body, "Native state and quote samples", "HeadingLabel")
	for data in [
		{"id":"primary", "title":"Ready for battle", "quote":"No additional production", "enabled":true, "variant":"PrimaryButton"},
		{"id":"insufficient", "title":"Unavailable quote", "quote":"14 gold · 2 wood · 4 stone · 3 metal · 2 cloth", "enabled":false, "reason":"Need 10 more stone. Build or upgrade a Stonecutter; synchronized quote remains authoritative."},
		{"id":"retire", "title":"Retire unit", "quote":"Permanent · no refund", "enabled":true, "variant":"DangerButton"}]: add_action(body, data)
	WatchUI.label(body, "▲ Burn · ● Poison ×2 · ◆ Chill · shaped text, not color alone")
	return body

func _unhandled_input(event: InputEvent) -> void:
	# Match the game's explicit local-input owner guard, including non-GUI world actions.
	if dialog != null and is_instance_valid(dialog) and dialog.visible: return
	if active_confirmation != null and is_instance_valid(active_confirmation) and active_confirmation.visible: return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		world_clicks += 1
