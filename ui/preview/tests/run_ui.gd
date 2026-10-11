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
	if only not in ["skill-tree", "woodland", "worldtree"]: await test_production()
	if only not in ["woodland", "worldtree"]:
		var skill_probe = load("res://tests/skill_tree_checks.gd").new()
		skill_probe.runner = self
		add_child(skill_probe)
		await skill_probe.run()
		skill_probe.queue_free()
	if only in ["all", "worldtree"]:
		var worldtree_probe = load("res://tests/worldtree_checks.gd").new()
		worldtree_probe.runner = self
		add_child(worldtree_probe)
		await worldtree_probe.run()
		worldtree_probe.queue_free()
	if only == "woodland": await test_woodland()
	if only == "all":
		await test_layouts()
		await test_woodland()
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

func key(code: Key, shift: bool = false) -> void:
	var event = InputEventKey.new()
	event.keycode = code
	event.shift_pressed = shift
	event.pressed = true
	Input.parse_input_event(event)
	await frames(2)
	event = InputEventKey.new()
	event.keycode = code
	event.shift_pressed = shift
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

# Added visual/input acceptance for the shared woodland skin, not a second tree.
func visible_tooltip(node: Node, text: String) -> bool:
	if node is Label and node.text == text and node.is_visible_in_tree() and node.get_window().visible and node.get_window() != get_window():
		return true
	for child in node.get_children(true):
		if visible_tooltip(child, text): return true
	return false

func test_woodland() -> void:
	await test_live_hud_resize()
	await test_information_layout()
	for size in [Vector2i(1100, 820), Vector2i(1280, 720)]:
		get_window().size = size
		ui.state = "building"
		ui.selection = "Empty plot"
		ui.switch_screen("hud")
		await frames(6)
		var footer = ui.find_child("HudFooter", true, false)
		expect(ui.information_scroll.get_global_rect().intersection(ui.upkeep.get_global_rect()).end.y < footer.get_global_rect().position.y, "woodland construction panes separate " + str(size))
		await capture("hud-choices-" + str(size.x) + "x" + str(size.y))
		var progress = ui.match_controls.get_node("Progress")
		var panel = ui.match_controls.get_parent()
		var received = [0, 0]
		var on_controls = func(event):
			if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed: received[0] += 1
		var on_panel = func(event):
			if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed: received[1] += 1
		ui.match_controls.gui_input.connect(on_controls)
		panel.gui_input.connect(on_panel)
		var ready = ui.match_controls.get_node("Ready")
		ready.grab_focus()
		var world_before = ui.world_clicks
		var action_before = ui.last_action
		var hover = InputEventMouseMotion.new()
		hover.position = progress.get_global_rect().get_center()
		hover.global_position = hover.position
		Input.parse_input_event(hover)
		await get_tree().create_timer(0.8).timeout
		await frames()
		expect(visible_tooltip(get_tree().root, "Building turn · 2 / 3 (illustrative projection)"), "supplied progress description appears in native tooltip " + str(size))
		await capture("hud-progress-tooltip-" + str(size.x) + "x" + str(size.y))
		await click(progress)
		expect(received == [1, 1], "progress pointer propagates through controls to containing HUD " + str(size))
		expect(ui.world_clicks == world_before and ui.last_action == action_before, "progress pointer neither leaks to world nor requests actions " + str(size))
		expect(get_viewport().gui_get_focus_owner() == ready, "progress hover/click preserves keyboard focus " + str(size))
		ui.match_controls.gui_input.disconnect(on_controls)
		panel.gui_input.disconnect(on_panel)
	var action = ui.actions[0].get_node("Body/Action")
	var world = ui.world_clicks
	action.grab_focus()
	await frames()
	expect(get_viewport().gui_get_focus_owner() == action, "woodland card retains native focus")
	await capture("hud-focus-1280x720")
	var motion = InputEventMouseMotion.new()
	motion.position = action.get_global_rect().get_center()
	motion.global_position = motion.position
	Input.parse_input_event(motion)
	await frames()
	expect(action.is_hovered(), "woodland card receives native pointer hover")
	await capture("hud-hover-1280x720")
	var tabs = ui.context.get_node("Actions").get_child(1)
	tabs.grab_focus()
	for i in range(4): await key(KEY_RIGHT)
	expect(ui.dialog != null and ui.dialog.visible, "Skill Tree tab opens landed compact tree modal")
	# Check real native font metrics against the authored node inset, not source
	# text or a smaller-font substitute. Point/state labels must remain complete.
	check_tree_text_width(ui.dialog_content.tree)
	await capture("hud-skill-tab-1280x720")
	var unfunded_tree = UIFixtures.skill_tree(0)
	unfunded_tree["owned"] = ["foundation"]
	ui.dialog_content.tree.set_data(unfunded_tree)
	await frames(4)
	check_tree_text_width(ui.dialog_content.tree)
	await key(KEY_ESCAPE)
	expect(get_viewport().gui_get_focus_owner() == tabs, "Skill Tree closure restores native tab focus")
	# Re-select the same tab: no dead entry after dialog closure.
	await click_point(tabs.get_global_rect().position + tabs.get_tab_rect(4).get_center())
	expect(ui.dialog.visible, "same Skill Tree tab reopens landed compact tree modal")
	await key(KEY_ESCAPE)
	expect(ui.world_clicks == world, "woodland art/tab interactions do not leak world input")
	ui.state = "preparation"
	ui.refresh_hud()
	await frames()
	expect(ui.information_scroll.get_global_rect().intersection(ui.upkeep.get_global_rect()).end.y < ui.find_child("HudFooter", true, false).get_global_rect().position.y, "variable preparation copy leaves woodland construction space")
	await capture("hud-choices-preparation-1280x720")

func test_live_hud_resize() -> void:
	get_window().size = Vector2i(1280, 720)
	ui.state = "building"
	ui.selection = "Empty plot"
	ui.switch_screen("hud")
	await frames(6)
	var world = ui.world_clicks
	var tabs = ui.context.get_node("Actions").get_child(1)
	var footer = ui.find_child("HudFooter", true, false)
	var ready = ui.match_controls.get_node("Ready")
	var cards: Array
	for group in [0, 1]:
		if group == 1: await click_point(tabs.get_global_rect().position + tabs.get_tab_rect(group).get_center())
		var scroll = ui.context.get_node("Actions/QuoteScroll")
		var grid = scroll.get_node("Choices")
		cards = ui.actions.duplicate()
		ready.grab_focus()
		await wheel_at(scroll, true)
		var sizes = [Vector2i(1100, 820), Vector2i(1280, 720), Vector2i(1100, 720), Vector2i(1100, 820), Vector2i(1280, 820), Vector2i(1280, 720)]
		for index in range(sizes.size()):
			var before_scroll = scroll.scroll_vertical
			var size = sizes[index]
			get_window().size = size
			await frames(6)
			expect(ui.state == "building" and ui.selection == "Empty plot", "live resize preserves state/selection " + str(size))
			expect(scroll == ui.context.get_node("Actions/QuoteScroll") and grid == scroll.get_node("Choices") and cards == ui.actions, "live resize retains quote controls " + str(size))
			expect(tabs.current_tab == group, "live resize preserves category " + str(group))
			expect(grid.columns == (3 if size.x >= 1280 else 2) and scroll.custom_minimum_size.y == (156 if size.y >= 820 else 144), "live width/height breakpoints " + str(size))
			var available = Rect2(Vector2(12, 12), Vector2(size) - Vector2(24, 24))
			for pane in footer.get_child(0).get_children(): expect(available.encloses(pane.get_global_rect()), "live pane stays inside actual margins " + str(size))
			expect(get_viewport().gui_get_focus_owner() == ready, "live resize keeps native focus " + str(size))
			expect(scroll.scroll_vertical <= mini(before_scroll, int(scroll.get_v_scroll_bar().max_value - scroll.get_v_scroll_bar().page)) and (before_scroll == 0 or scroll.get_v_scroll_bar().max_value <= scroll.get_v_scroll_bar().page or scroll.scroll_vertical > 0), "live resize retains scroll without reset, allowing native clamp " + str(size) + " group=" + str(group) + " before/actual/limit=" + str(Vector3(before_scroll, scroll.scroll_vertical, scroll.get_v_scroll_bar().max_value - scroll.get_v_scroll_bar().page)))
			expect(scroll.size.y >= scroll.custom_minimum_size.y, "live quote viewport remains allocated " + str(size))
			await wheel_at(scroll, true)
			expect(scroll.get_global_rect().encloses(cards[-1].get_global_rect()), "live quote tail reachable with native wheel " + str(size))
			await click(ready)
			expect(ui.last_action.contains("Request: ready"), "live footer receives native pointer " + str(size))
			if index < 2: await capture("hud-live-" + str(group) + "-" + str(size.x) + "x" + str(size.y))
		if group == 0:
			var target = cards[5].get_node("Body/Action")
			target.grab_focus()
			await frames()
			expect(scroll.get_global_rect().encloses(target.get_global_rect()), "live quote native focus reveals far action")
			await key(KEY_ENTER)
			expect(ui.last_action.contains("build-Weaver"), "live quote keyboard activation retains opaque identity")
	await click_point(tabs.get_global_rect().position + tabs.get_tab_rect(4).get_center())
	var modal = ui.dialog
	var modal_focus = get_viewport().gui_get_focus_owner()
	for size in [Vector2i(1100, 820), Vector2i(1280, 720)]:
		get_window().size = size
		await frames(6)
		expect(ui.dialog == modal and modal.visible and modal.invoker == tabs and ui.dialog_opener == tabs, "live modal/invoker retained " + str(size))
		expect(get_viewport().gui_get_focus_owner() == modal_focus, "live modal keeps native focus " + str(size))
		expect(cards == ui.actions, "live modal resize retains underlying category controls " + str(size))
		await capture("hud-live-modal-" + str(size.x) + "x" + str(size.y))
	await key(KEY_ESCAPE)
	expect(get_viewport().gui_get_focus_owner() == tabs, "live modal close restores retained tab invoker")
	for projection in ["preparation", "lost"]:
		ui.state = projection
		ui.refresh_hud()
		await frames()
		var scroll = ui.context.get_node("Actions/QuoteScroll")
		for size in [Vector2i(1100, 820), Vector2i(1280, 720)]:
			get_window().size = size
			await frames(6)
			expect(ui.state == projection and ui.selection == "Empty plot", "live projection resize preserves snapshot " + projection)
			expect(scroll == ui.context.get_node("Actions/QuoteScroll"), "live projection retains quote viewport " + projection)
			expect(scroll.custom_minimum_size.y == (156 if size.y >= 820 else 112), "live projection quote height follows viewport " + projection)
			var available = Rect2(Vector2(12, 12), Vector2(size) - Vector2(24, 24))
			for pane in footer.get_child(0).get_children(): expect(available.encloses(pane.get_global_rect()), "live projection pane bounds " + projection + str(size))
			await wheel_at(scroll, true)
			await wheel_at(scroll, true)
			expect(scroll.get_global_rect().encloses(ui.actions[-1].get_node("Body/Reason").get_global_rect()), "live projection complete tail reason remains reachable " + projection + str(size) + " viewport=" + str(scroll.get_global_rect()) + " reason=" + str(ui.actions[-1].get_node("Body/Reason").get_global_rect()))
			await click(ui.match_controls.get_node("Ready") if projection == "preparation" else ui.feedback.get_node("Actions/Reconnect"))
			expect(ui.last_action.contains("ready") if projection == "preparation" else ui.last_action.contains("reconnect"), "live projection footer input retained " + projection)
	expect(ui.world_clicks == world, "live resize/category/modal/quote input never leaks to world")

func check_tree_text_width(tree) -> void:
	for node_button in tree.buttons.values():
		var inset = node_button.get_theme_stylebox("normal")
		var available_width = node_button.size.x - inset.get_content_margin(SIDE_LEFT) - inset.get_content_margin(SIDE_RIGHT)
		for line in node_button.text.split("\n"):
			var text_width = node_button.get_theme_font("font").get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, node_button.get_theme_font_size("font_size")).x
			expect(text_width <= available_width, "inherited tree node title/cost/state fits native font metrics " + line)

func wheel_at(scroll: ScrollContainer, down: bool) -> void:
	var point = scroll.get_global_rect().get_center()
	var motion = InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	for i in range(10):
		# Wheel indices are buttons to the synthetic parser: each real pulse must
		# release, or its held mask prevents subsequent left clicks reaching GUI.
		for pressed in [true, false]:
			var event = InputEventMouseButton.new()
			event.position = point
			event.global_position = point
			event.button_index = MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP
			event.pressed = pressed
			Input.parse_input_event(event)
	await frames()

func test_information_layout() -> void:
	var world = ui.world_clicks
	for size in [Vector2i(1280, 720), Vector2i(1100, 820)]:
		get_window().size = size
		ui.switch_screen("hud")
		for selection in ["Producer", "Empty plot"]:
			ui.selection = selection
			for state in ["building", "combat", "preparation", "lost", "building"]:
				ui.state = state
				ui.refresh_hud()
				await frames(6)
				var scroll = ui.information_scroll
				var footer = ui.find_child("HudFooter", true, false)
				expect(scroll.get_global_rect().end.y + 15 <= footer.get_global_rect().position.y, "native information/footer allocation " + state + selection + str(size))
				expect(Rect2(Vector2.ZERO, Vector2(size)).encloses(footer.get_global_rect()), "native footer bounds " + state + selection + str(size))
				for pair in ui.ledger.value_labels.values():
					for label in pair: expect(label.get_minimum_size().x <= label.size.x and label.get_theme_font_size("font_size") == 14, "information quantities retain native font/width " + state)
				await wheel_at(scroll, true)
				var last = ui.upkeep.get_node("Body").get_child(ui.upkeep.get_node("Body").get_child_count()-1)
				expect(scroll.get_global_rect().encloses(last.get_global_rect()), "last information line reachable " + state + selection + str(size))
				await wheel_at(scroll, false)
				expect(scroll.scroll_vertical == 0, "reverse wheel restores stocks " + state)
				expect(Input.get_mouse_button_mask() == 0, "paired native wheel pulses leave no held buttons " + state)
				var b = ui.match_controls.get_node("Ready") if state in ["building", "preparation"] else ui.feedback.get_node("Actions/Reconnect") if state == "lost" else ui.match_controls.get_node("Pause")
				ui.last_action = ""
				await click(b)
				expect(ui.last_action.begins_with("Request:"), "footer action clickable through information boundary " + state)
	# Falsifying content case: no reduced font/padding or omitted text.
	get_window().size = Vector2i(1280, 720)
	ui.state = "preparation"
	ui.selection = "Empty plot"
	ui.refresh_hud()
	await frames()
	var footer_y = ui.find_child("HudFooter", true, false).get_global_rect().position.y
	var data = ui.ledger.data.duplicate(true)
	data.context = "Next building turn.\nNo income on Ready for battle.\nAdditional externally supplied localized explanation of preparation.\nThis deliberately longer paragraph preserves all information and native font minima.\nNo action has spent resources."
	ui.ledger.set_data(data)
	await frames()
	expect(ui.find_child("HudFooter", true, false).get_global_rect().position.y == footer_y, "long supplied copy cannot displace footer")
	expect(ui.information_scroll.get_v_scroll_bar().max_value > ui.information_scroll.size.y, "long supplied copy uses native overflow")
	await wheel_at(ui.information_scroll, true)
	var last = ui.upkeep.get_node("Body").get_child(ui.upkeep.get_node("Body").get_child_count()-1)
	expect(ui.information_scroll.get_global_rect().encloses(last.get_global_rect()), "long copy remains fully reachable")
	# Construction costs below the fold retain real wheel/focus/Enter ownership.
	var choices = ui.context.get_node("Actions/QuoteScroll")
	await wheel_at(choices, true)
	expect(choices.scroll_vertical > 0, "construction quotes retain real wheel scrolling")
	var target = ui.actions[5].get_node("Body/Action")
	target.grab_focus()
	await frames()
	expect(choices.get_global_rect().encloses(target.get_global_rect()), "native focus reveals far construction action")
	await key(KEY_ENTER)
	expect(ui.last_action.contains("build-Weaver"), "far construction action emits opaque id")
	expect(ui.world_clicks == world, "information/quote scrolling and footer clicks do not leak world input")

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
		expect(ui.information_scroll.get_global_rect().intersection(ui.upkeep.get_global_rect()).end.y < footer.get_global_rect().position.y, "information/footer separation " + str(size))
		for variant in ["preparation", "shortage", "lost"]:
			ui.state = variant
			ui.refresh_hud()
			await frames()
			expect(rect.encloses(footer.get_global_rect()), "state footer fit " + variant + str(size))
			expect(ui.information_scroll.get_global_rect().intersection(ui.upkeep.get_global_rect()).end.y < footer.get_global_rect().position.y, "state separation " + variant + str(size))
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
		if size.x <= 1920:
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
				elif kind == "details" and size.x <= 1280:
					for view in ["paid", "last", "fresh"]:
						ui.dialog_content.set_data(UIFixtures.details(view))
						ui.dialog.get_scroll().scroll_vertical = 0
						await capture("details-"+view+"-"+str(size.x)+"x"+str(size.y))
				elif kind == "town_hall" and size.x <= 1280:
					for view in ["empty", "stale", "storage", "recovery", "fragmented"]:
						ui.dialog_content.set_data(UIFixtures.hall(view))
						ui.dialog.get_scroll().scroll_vertical = 0
						await frames()
						if view in ["recovery", "fragmented"]:
							ui.dialog.get_scroll().scroll_vertical = int(ui.dialog_content.card.get_global_rect().position.y - ui.dialog.get_scroll().get_global_rect().position.y)
						await capture("town_hall-"+view+"-"+str(size.x)+"x"+str(size.y))
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
	for state in ["preparation", "shortage", "lost", "combat", "foreign", "paused", "victory", "defeat", "lobby", "fallen", "stale"]:
		ui.state = state
		ui.refresh_hud()
		await capture("hud-"+state+"-1280x720")
