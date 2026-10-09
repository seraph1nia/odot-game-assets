extends Node
# Actual native input/layout/state checks on the independent preview, not game E2E.
var ui: Control
var failures: Array = []
var checks = 0
var captures: Array = []
var output = ""
var only = "all"

func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
		if arg.begins_with("--only="): only = arg.trim_prefix("--only=")
	if output.is_empty(): push_error("--output required"); get_tree().quit(1); return
	ui = load("res://prototypes/showcase.tscn").instantiate()
	add_child(ui)
	await frames()
	if only == "all":
		await test_components()
		await test_input()
		await test_dialogs()
		await test_modal_scope()
	await test_production()
	if only == "all": await test_layouts()
	var result = {"checks":checks, "failures":failures, "captures":captures,
		"scope":"Standalone native controls; no game integration or native GPU claim", "selection":only}
	var file = FileAccess.open(output.path_join("results.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "\t") + "\n")
	print("UI_TESTS ", checks, " checks; ", failures.size(), " failures; ", captures.size(), " captures")
	get_tree().quit(0 if failures.is_empty() else 1)

func frames(count: int = 4) -> void:
	for i in range(count): await get_tree().process_frame

func expect(condition: bool, name: String) -> void:
	checks += 1
	if not condition:
		failures.append(name)
		push_error("UI assertion: " + name)

func key(code: Key) -> void:
	var event = InputEventKey.new()
	event.keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await frames(2)
	event = InputEventKey.new()
	event.keycode = code
	event.pressed = false
	Input.parse_input_event(event)
	await frames(2)

func click_point(position: Vector2) -> void:
	var motion = InputEventMouseMotion.new()
	motion.position = position
	motion.global_position = position
	Input.parse_input_event(motion)
	for pressed in [true, false]:
		var event = InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = position
		event.global_position = position
		Input.parse_input_event(event)
		await frames(2)

func click(control: Control) -> void:
	var point = control.get_global_rect().get_center()
	if control.get_window() != get_window(): point += Vector2(control.get_window().position)
	await click_point(point)

func test_components() -> void:
	expect(ui.ledger.value_labels.size() == 6, "six resource rows")
	expect(ui.ledger.value_labels["Metal"][0].text == "12", "exact metal stock")
	expect(ui.ledger.value_labels["Food"][1].text == "+5", "positive income prefix")
	for state in ["building", "ready", "preparation", "combat", "shortage", "foreign", "paused", "lost", "victory", "defeat"]:
		ui.state = state
		ui.refresh_hud()
		await frames()
		var can_edit = state in ["building", "preparation", "shortage"]
		expect(ui.actions[0].get_node("Body/Action").disabled == not can_edit, "quote edit gate " + state)
		expect(ui.match_controls.get_node("Ready").disabled == not (can_edit or state == "ready"), "readiness gate " + state)
		if state == "preparation": expect(ui.ledger.data.context.to_lower().contains("no income"), "preparation does not grant income")
		if state == "shortage": expect(ui.upkeep.data.detail.contains("5 field soldiers"), "shortage consequences")
		if state in ["combat", "victory", "defeat"]: expect(ui.upkeep.data.heading.contains("W2"), "wave receipt " + state)
		if state in ["victory", "defeat"]: expect(ui.ledger.value_labels["Gold"][1].text == "0", "terminal future income " + state)
		if state == "lost": expect(ui.feedback.get_node("Actions/Fresh").visible and ui.feedback.get_node("Actions/Reconnect").visible, "distinct reconnect/fresh actions")
	ui.state = "building"
	for selection in ["Empty plot", "Locked plot", "Recruiter", "Market", "Town hall", "Army homes", "Unit", "Producer"]:
		ui.selection = selection
		ui.refresh_hud()
		await frames()
		expect(ui.context.get_node("Actions/Heading").text.length() > 0, "selection heading " + selection)
		if selection == "Recruiter":
			for role in [1, 2]:
				ui.fill_recruit_quotes(ui.context.get_node("Actions/QuoteScroll/Choices"), role, true, "")
				expect(ui.actions.size() == 1, "role recruitment " + str(role))
		if selection == "Market": expect(ui.actions.size() == 5, "all five fixed trades")
		if selection == "Empty plot":
			for group in range(4):
				ui.fill_build_quotes(ui.context.get_node("Actions/QuoteScroll/Choices"), group, true, "")
				expect(ui.actions.size() > 0, "construction group " + str(group))

func test_input() -> void:
	ui.state = "building"
	ui.selection = "Producer"
	ui.refresh_hud()
	await frames()
	var b = ui.actions[0].get_node("Body/Action")
	await click(b)
	expect(ui.last_action.contains("upgrade"), "native mouse action signal")
	ui.last_action = ""
	b.grab_focus()
	await key(KEY_ENTER)
	expect(ui.last_action.contains("upgrade"), "native Enter action signal")
	await key(KEY_TAB)
	expect(get_viewport().gui_get_focus_owner() != b, "native Tab focus traversal")
	ui.state = "foreign"
	ui.refresh_hud()
	ui.last_action = "unchanged"
	await frames()
	await click(ui.actions[0].get_node("Body/Action"))
	expect(ui.last_action == "unchanged", "disabled quote refuses mouse activation")
	ui.state = "building"
	ui.refresh_hud()
	await frames()
	await click(ui.navigation.get_node("Row/Next"))
	expect(ui.state == "foreign", "city switch emits inspection request")
	expect(ui.actions[0].get_node("Body/Action").disabled, "foreign city cannot edit")
	ui.state = "building"
	ui.refresh_hud()
	await frames()
	var before = ui.world_clicks
	await click_point(Vector2(400, 330))
	expect(ui.world_clicks == before + 1, "world mock receives background input")
	before = ui.world_clicks
	await click(ui.ledger)
	expect(ui.world_clicks == before, "resource panel blocks world click")
	await click(ui.upkeep)
	expect(ui.world_clicks == before, "upkeep panel blocks world click")

func test_dialogs() -> void:
	var opener = ui.find_child("Settings", true, false)
	opener.grab_focus()
	ui.open_dialog("settings", opener)
	await frames()
	var settings = ui.dialog_content
	settings.display_mode.grab_focus()
	await key(KEY_ENTER)
	expect(settings.display_mode.get_popup().visible, "keyboard opens dropdown")
	await key(KEY_ESCAPE)
	expect(not settings.display_mode.get_popup().visible and ui.dialog.visible, "Esc dismisses dropdown first")
	# Native item selection through keyboard, not direct signal invocation.
	settings.display_mode.grab_focus()
	await key(KEY_ENTER)
	await key(KEY_DOWN)
	await key(KEY_ENTER)
	expect(settings.resolution.disabled, "fullscreen disables resolution")
	settings.get_node("Categories").current_tab = 1
	await frames()
	settings.volume.grab_focus()
	var previous = settings.volume.value
	await key(KEY_RIGHT)
	expect(settings.volume.value > previous, "keyboard slider changes mock value")
	var before = ui.world_clicks
	await click_point(Vector2(80, 220))
	expect(ui.world_clicks == before, "native dialog blocks world input")
	await key(KEY_ESCAPE)
	expect(not ui.dialog.visible, "Esc closes dialog")
	expect(get_viewport().gui_get_focus_owner() == opener, "dialog returns focus to opener")
	ui.close_dialog()
	for kind in ["research", "town_hall", "unit", "details", "friends", "components"]:
		ui.open_dialog(kind, opener)
		await frames()
		expect(ui.dialog.visible, "dialog loads " + kind)
		if kind == "research":
			for role in range(3):
				ui.dialog_content.role = role
				ui.dialog_content.refresh()
				expect(ui.dialog_content.choices.size() == 5, "five technologies for class " + str(role))
			ui.dialog_content.mode = "owned"
			ui.dialog_content.refresh()
			expect(ui.dialog_content.choices[3].data.reason.contains("locked"), "permanent sibling research lock")
			var scroll = ui.dialog.get_scroll()
			await frames()
			expect(scroll.get_v_scroll_bar().max_value > scroll.size.y, "research content scrolls")
		elif kind == "town_hall":
			expect(ui.dialog_content.roster.buttons.size() == 9, "stored roster population")
			expect(ui.dialog_content.card.data.profile.contains("Stored reserve"), "stored unit not field participant")
			ui.dialog_content.set_read_only("Paused inspection")
			expect(ui.dialog_content.card.get_node("Body/Retire").disabled, "read-only retirement gate")
		elif kind == "unit":
			var card = ui.dialog_content
			card.get_node("Body/Destination").select(1)
			card.update_destination()
			expect(card.get_node("Body/Send").disabled and card.get_node("Body/Reason").text.contains("No fitting"), "full destination gate")
		elif kind == "friends":
			expect(ui.dialog_content.buttons.size() == 14, "friends scroll sample")
			ui.dialog_content.available = false
			ui.dialog_content.refresh(false)
			expect(ui.dialog_content.buttons[1000].disabled, "offline invites disabled")
		ui.close_dialog()
		await frames()
	ui.state = "paused"
	ui.open_dialog("research")
	await frames()
	expect(ui.dialog_content.choices[1].get_node("Body/Action").disabled, "paused research purchase gate")
	ui.close_dialog()
	ui.state = "building"

func test_production() -> void:
	var probe = load("res://tests/production_checks.gd").new()
	probe.ui = ui
	probe.runner = self
	add_child(probe)
	await probe.run()
	checks += probe.checks
	failures.append_array(probe.failures)
	probe.queue_free()

func test_modal_scope() -> void:
	var probe = load("res://tests/diagnose_settings.gd").new()
	probe.autorun = false
	probe.ui = ui
	add_child(probe)
	var opener = ui.find_child("Settings", true, false)
	ui.open_dialog("settings", opener)
	await frames()
	ui.dialog.canceled.connect(func(): probe.canceled += 1)
	await probe.modal_scope(ui.dialog_content, opener)
	checks += probe.checks
	failures.append_array(probe.failures)
	probe.queue_free()
	ui.switch_screen("hud")
	await frames()

func capture(name: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	var path = output.path_join(name + ".png")
	var image = get_viewport().get_texture().get_image()
	expect(image.save_png(path) == OK, "capture " + name)
	captures.append({"path":name+".png", "width":image.get_width(), "height":image.get_height()})

func test_layouts() -> void:
	for size in [Vector2i(1100,820), Vector2i(1280,720), Vector2i(1600,900), Vector2i(1920,1080)]:
		get_window().size = size
		await frames(6)
		ui.screen_mode = "hud"
		ui.build_content()
		await frames()
		var rect = Rect2(Vector2.ZERO, Vector2(size))
		var footer = ui.find_child("HudFooter", true, false)
		expect(rect.encloses(ui.ledger.get_global_rect()), "ledger viewport fit " + str(size))
		expect(rect.encloses(footer.get_global_rect()), "footer viewport fit " + str(size))
		expect(ui.upkeep.get_global_rect().end.y < footer.get_global_rect().position.y, "information/footer separation " + str(size))
		for variant in ["preparation", "shortage", "lost"]:
			ui.state = variant
			ui.refresh_hud()
			await frames()
			expect(rect.encloses(footer.get_global_rect()), "state footer fit " + variant + str(size))
			expect(ui.upkeep.get_global_rect().end.y < footer.get_global_rect().position.y, "state separation " + variant + str(size))
		ui.state = "building"
		ui.refresh_hud()
		await frames()
		for pair in ui.ledger.value_labels.values():
			for label in pair: expect(label.get_minimum_size().x <= label.size.x, "resource text width " + str(size))
		await capture("hud-"+str(size.x)+"x"+str(size.y))
		ui.switch_screen("menu")
		await frames()
		expect(ui.find_child("StartMenu", true, false).get_global_rect().size.x == 460, "menu pixel-preserving width " + str(size))
		await capture("menu-"+str(size.x)+"x"+str(size.y))
		if size.x <= 1280:
			var start = ui.find_child("StartMenu", true, false)
			start.multiplayer_view = true
			start.show_menu()
			await capture("menu-multiplayer-"+str(size.x)+"x"+str(size.y))
			ui.switch_screen("hud")
			for kind in ["research", "town_hall", "settings", "details", "friends", "unit", "components"]:
				ui.open_dialog(kind)
				await frames()
				expect(rect.encloses(ui.dialog.get_panel().get_global_rect()), "dialog viewport fit " + kind + str(size))
				await capture(kind+"-"+str(size.x)+"x"+str(size.y))
				if kind == "settings":
					ui.dialog_content.get_node("Categories").current_tab = 2
					ui.dialog_content.find_child("UpdateSample", true, false).select(4)
					ui.dialog_content.update_sample = 4
					ui.dialog_content.show_update()
					await capture("settings-about-error-"+str(size.x)+"x"+str(size.y))
				elif kind == "friends":
					ui.dialog_content.get_node("Availability").select(6)
					ui.dialog_content.mode = "long-names"
					ui.dialog_content.refresh(false)
					await capture("friends-long-"+str(size.x)+"x"+str(size.y))
				elif kind == "research":
					ui.dialog_content.get_node("AccessSample").select(1)
					ui.dialog_content.mode = "owned"
					ui.dialog_content.refresh()
					await frames()
					ui.dialog.get_scroll().scroll_vertical = 10000
					await capture("research-locked-scrolled-"+str(size.x)+"x"+str(size.y))
				ui.close_dialog()
	get_window().size = Vector2i(1280,720)
	ui.switch_screen("hud")
	for state in ["preparation", "shortage", "lost", "combat", "foreign"]:
		ui.state = state
		ui.refresh_hud()
		await capture("hud-"+state+"-1280x720")
