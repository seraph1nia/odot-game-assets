extends Node
# Bounded mock UI contracts, using actual events; no game/service integration.
var ui: Control
var runner: Node
var checks = 0
var failures: Array = []
func expect(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message); push_error("Production UI: " + message)
func frames() -> void: await runner.frames()
func key(code: Key) -> void: await runner.key(code)
func click(control: Control) -> void:
	control.grab_focus()
	await frames()
	await runner.click(control)
func choose(control: OptionButton, index: int) -> void:
	control.grab_focus()
	await key(KEY_ENTER)
	var focused = control.get_popup().get_focused_item()
	for i in range(absi(index - focused)): await key(KEY_DOWN if index > focused else KEY_UP)
	await key(KEY_ENTER)
	expect(control.selected == index, "native selector index " + str(index) + " actual " + str(control.selected))
func button(parent: Node, text: String) -> Button:
	for child in parent.find_children("*", "Button", true, false):
		if child.text == text: return child
	return null
func wheel(scroll: ScrollContainer, down: bool = true) -> void:
	var point = scroll.get_global_rect().get_center()
	var motion = InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	for i in range(4):
		var event = InputEventMouseButton.new()
		event.position = point
		event.global_position = point
		event.button_index = MOUSE_BUTTON_WHEEL_DOWN if down else MOUSE_BUTTON_WHEEL_UP
		event.pressed = true
		Input.parse_input_event(event)
		await frames()
func run() -> void:
	ui.switch_screen("hud")
	ui.state = "building"
	ui.refresh_hud()
	await frames()
	var world = ui.world_clicks
	await scrolling()
	await research()
	await inspection()
	await settings()
	await friends()
	await menu()
	await hud()
	expect(ui.world_clicks == world, "all production UI interactions block world actions")
	ui.switch_screen("hud")
	ui.state = "building"
	ui.refresh_hud()
	await frames()
func scrolling() -> void:
	for kind in ["research", "town_hall", "details", "friends"]:
		ui.open_dialog(kind)
		await frames()
		var scroll = ui.dialog.get_scroll()
		expect(scroll.get_v_scroll_bar().max_value > scroll.size.y, "body overflows " + kind)
		for inner in ui.dialog_content.find_children("*", "ScrollContainer", true, false):
			# Native child dropdown Windows retain their own viewport/list scrolling.
			if inner.get_viewport() != ui.dialog.get_viewport(): continue
			expect(inner.vertical_scroll_mode == ScrollContainer.SCROLL_MODE_DISABLED, "single vertical scroll owner " + kind + " " + str(inner.get_path()) + " mode=" + str(inner.vertical_scroll_mode))
		var before = scroll.scroll_vertical
		await wheel(scroll)
		expect(scroll.scroll_vertical > before, "real wheel moves body " + kind)
		await wheel(scroll, false)
		expect(scroll.scroll_vertical < before + 200, "real reverse wheel " + kind)
		var target: Control
		if kind == "research": target = ui.dialog_content.choices[3].get_node("Body/Action")
		elif kind == "friends": target = ui.dialog_content.buttons[1013]
		elif kind == "town_hall": target = ui.dialog_content.roster.buttons[109]
		else: target = ui.dialog_content.find_child("ArmyRoster", true, false).buttons[118]
		ui.dialog.get_ok_button().grab_focus()
		for index in range(65):
			if get_viewport().gui_get_focus_owner() == target: break
			await key(KEY_TAB)
		expect(get_viewport().gui_get_focus_owner() == target, "long Tab reaches far row " + kind)
		expect(scroll.get_global_rect().encloses(target.get_global_rect()), "follow-focus reveals whole target " + kind)
		await key(KEY_ENTER)
		if kind == "friends": expect(ui.last_action.contains("invite-1013"), "far friend intent")
		elif kind == "details": expect(ui.last_action.contains("inspect-118"), "far field unit intent")
		elif kind == "town_hall": expect(ui.dialog_content.card.data.id == 109, "far reserve selection")
		else: expect(ui.last_action.contains("assault"), "far research purchase intent")
		await key(KEY_ESCAPE)
		expect(not ui.dialog.visible, "scrolled modal still cancels " + kind)
		ui.close_dialog()
func research() -> void:
	ui.open_dialog("research")
	var tree = ui.dialog_content
	for role in range(3):
		var tabs = tree.get_node("Classes")
		tabs.grab_focus()
		await key(KEY_HOME)
		for i in range(role): await key(KEY_RIGHT)
		expect(tree.role == role and tree.choices.size() == 5, "native research class " + str(role))
		await choose(tree.get_node("AccessSample"), 0)
		expect(tree.choices[0].get_node("Body/Action").disabled, "owned foundation " + str(role))
		expect(tree.choices[2].get_node("Body/Action").disabled, "mastery prerequisite " + str(role))
		await click(tree.choices[1].get_node("Body/Action"))
		expect(ui.last_action.contains(tree.choices[1].data.id), "class specialization intent " + str(role))
		await choose(tree.get_node("AccessSample"), 1)
		expect(tree.choices[2].data.reason.contains("3 more") and tree.choices[3].data.reason.contains("locked"), "insufficient and permanent lock " + str(role))
		await choose(tree.get_node("AccessSample"), 3)
		await click(tree.choices[2].get_node("Body/Action"))
		expect(ui.last_action.contains("mastery"), "funded mastery intent " + str(role))
		await choose(tree.get_node("AccessSample"), 2)
		for choice in tree.choices: expect(choice.get_node("Body/Action").disabled, "foreign research gate")
	ui.close_dialog()
func inspection() -> void:
	ui.open_dialog("town_hall")
	var hall = ui.dialog_content
	await click(hall.healing.get_node("Body/Action"))
	expect(ui.last_action.contains("healing-upgrade"), "independent healing quote intent")
	await click(hall.roster.buttons[103])
	expect(hall.card.data.id == 103 and not hall.roster.buttons[101].button_pressed, "one native selected reserve")
	await click(hall.card.get_node("Body/Send"))
	expect(ui.last_action.contains("send-field unit=103 destination=field"), "opaque reserve transfer selectors")
	await click(hall.card.get_node("Body/Retire"))
	expect(ui.last_action.contains("retire unit=103"), "explicit retire intent")
	hall.set_read_only("Paused inspection")
	await click(hall.roster.buttons[104])
	expect(hall.card.get_node("Body/Send").disabled and hall.card.get_node("Body/Retire").disabled, "selection preserves readonly gates")
	ui.close_dialog()
	ui.open_dialog("unit")
	var card = ui.dialog_content
	await choose(card.get_node("Body/Destination"), 1)
	expect(card.get_node("Body/Send").disabled and card.get_node("Body/Reason").text.contains("No fitting"), "native full destination gate")
	await choose(card.get_node("Body/Destination"), 0)
	await click(card.get_node("Body/Send"))
	expect(ui.last_action.contains("hall-4-generation-2"), "field-to-storage opaque generation selector")
	var projection = card.data.duplicate(true)
	projection.destinations = []
	projection.show_preview = true
	projection.health_percent = 9
	projection.health_text = "5 / 54 HP"
	card.set_data(projection)
	expect(card.get_node("Body/Send").disabled and card.get_node("Body/PreviewSlot").visible, "no destination and independent preview slot")
	expect(card.get_node("Body/Health").value == 9, "low health projection exact")
	var slot = card.get_node("Body/PreviewSlot")
	var preview = Label.new()
	preview.text = "External model-renderer content slot (test only)"
	slot.add_child(preview)
	expect(slot.get_child_count() == 1 and slot.mouse_filter == Control.MOUSE_FILTER_IGNORE, "adapter-owned preview content without model dependency")
	ui.close_dialog()
	ui.state = "foreign"
	ui.open_dialog("details")
	expect(ui.dialog_content.heading.text.contains("P2") and ui.dialog_content.context_label.text.contains("Read-only"), "foreign Details context")
	ui.close_dialog()
	ui.state = "building"
func settings() -> void:
	ui.open_dialog("settings")
	var options = ui.dialog_content
	var tabs = options.get_node("Categories").get_tab_bar()
	tabs.grab_focus()
	await key(KEY_RIGHT)
	options.volume.grab_focus()
	await key(KEY_HOME)
	expect(options.volume.value == 0, "native volume zero")
	tabs.grab_focus()
	await key(KEY_RIGHT)
	var about = options.get_node("Categories/About")
	var sample = about.find_child("UpdateSample", true, false)
	for state in range(6):
		await choose(sample, state)
		await click(about.find_child("CheckUpdates", true, false))
		expect(options.update_status.text.contains(["Development", "checking", "up to date", "available", "failed", "save failed"][state]), "mock About feedback " + str(state))
	var return_button = button(options, "Return to menu")
	await click(return_button)
	await key(KEY_ESCAPE)
	expect(ui.active_confirmation == null and ui.dialog.visible, "Return cancellation keeps Settings and HUD")
	expect(get_viewport().gui_get_focus_owner() == return_button, "Return cancellation focus")
	await click(return_button)
	await click(ui.active_confirmation.get_ok_button())
	expect(ui.screen_mode == "menu" and ui.dialog == null, "Return confirmation mock navigation")
	ui.switch_screen("hud")
func friends() -> void:
	ui.open_dialog("friends")
	var list = ui.dialog_content
	var sample = list.get_node("Availability")
	for index in [1,2,3,4,5,6,0]:
		await choose(sample, index)
		await click(list.get_node("Refresh"))
		expect(list.mode == ["populated", "offline", "empty", "busy", "refresh-failure", "invite-failure", "long-names"][index], "native Refresh keeps selected projection")
		if index == 1: expect(list.buttons[1000].disabled and list.status.text.contains("log in"), "offline friends")
		elif index == 2: expect(list.buttons.is_empty(), "empty friends")
		elif index == 3: expect(list.buttons[1000].disabled and list.busy, "busy invite suppression")
		elif index == 4: expect(list.buttons.is_empty() and list.status.text.contains("failed"), "refresh error feedback")
		elif index == 6:
			var label = list.rows.get_child(0).get_node("FriendName")
			expect(label.clip_text and label.tooltip_text.contains("extraordinarily"), "long duplicate names retain tooltip identity")
		else:
			var observed = {"count":0,"busy":false}
			var listener = func(_id): observed.count += 1; observed.busy = list.busy and list.buttons[1000].disabled
			list.invite_requested.connect(listener)
			await click(list.buttons[1000])
			expect(observed.count == 1 and observed.busy, "one invite intent with immediate busy projection")
			expect(not list.busy and list.status.text.contains("failed" if index == 5 else "nothing sent"), "recoverable send result")
			list.invite_requested.disconnect(listener)
	ui.close_dialog()
func menu() -> void:
	ui.switch_screen("menu")
	await frames()
	var menu = ui.find_child("StartMenu", true, false)
	await key(KEY_TAB)
	await key(KEY_ENTER)
	expect(menu.multiplayer_view, "native menu Tab/Enter multiplayer")
	await key(KEY_ENTER)
	expect(ui.last_action == "host", "host mock intent without service")
	await click(button(menu, "Back"))
	expect(not menu.multiplayer_view, "native multiplayer Back")
	await click(menu.get_node("Body/Settings"))
	await key(KEY_ESCAPE)
	expect(get_viewport().gui_get_focus_owner() == menu.get_node("Body/Settings"), "menu modal focus return")
	await click(menu.get_node("Body/Exit"))
	await key(KEY_ESCAPE)
	expect(ui.active_confirmation == null and ui.screen_mode == "menu", "Exit confirmation cancellation")
	await click(menu.get_node("Body/Exit"))
	await click(ui.active_confirmation.get_ok_button())
	expect(ui.last_action.contains("exit") and ui.screen_mode == "menu", "Exit mock intent does not quit process")
	await click(menu.get_node("Body/Solo"))
	expect(ui.screen_mode == "hud", "native solo navigation")
func hud() -> void:
	ui.state = "building"
	ui.refresh_hud()
	var metal = ui.ledger.value_labels["Metal"][0].text
	for selection in ["Producer", "Empty plot", "Locked plot", "Recruiter", "Market", "Army homes"]:
		ui.selection = selection
		ui.refresh_hud()
		await frames()
		var target = ui.actions[0].get_node("Body/Action")
		await click(target)
		expect(ui.last_action.contains(ui.actions[0].data.id), "native selected context quote " + selection)
		expect(ui.ledger.value_labels["Metal"][0].text == metal, "intent never spends resources " + selection)
	ui.selection = "Market"
	ui.refresh_hud()
	await frames()
	var last = ui.last_action
	await runner.click(ui.actions[1].get_node("Body/Action"))
	expect(ui.last_action == last, "insufficient trade refuses native pointer")
	ui.selection = "Producer"
	for state in ["building", "ready", "preparation", "paused"]:
		ui.state = state
		ui.refresh_hud()
		await frames()
		if state != "paused":
			await click(ui.match_controls.get_node("Ready"))
			expect(ui.last_action.contains("unready" if state == "ready" else "ready"), "readiness intent " + state)
		await click(ui.match_controls.get_node("Pause"))
		expect(ui.last_action.contains("resume" if state == "paused" else "pause"), "shared pause intent " + state)
	ui.state = "lost"
	ui.refresh_hud()
	await frames()
	await click(ui.feedback.get_node("Actions/Reconnect"))
	expect(ui.last_action.contains("reconnect"), "reconnect intent")
	await click(ui.feedback.get_node("Actions/Fresh"))
	expect(ui.last_action.contains("fresh"), "fresh session distinct intent")
