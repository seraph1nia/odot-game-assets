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
	await selector_navigation()
	await scrolling()
	await research()
	await inspection()
	await details_projections()
	await hall_projections()
	await edge_controls()
	await settings()
	await friends()
	await menu()
	await hud()
	expect(ui.world_clicks == world, "all production UI interactions block world actions")
	ui.switch_screen("hud")
	ui.state = "building"
	ui.refresh_hud()
	await frames()
func selector_navigation() -> void:
	var screen = ui.find_child("ScreenSelector", true, false)
	var state_picker = ui.find_child("StateSelector", true, false)
	var observed = {"screen":0, "state":0, "selection":0}
	screen.item_selected.connect(func(_index): observed.screen += 1)
	state_picker.item_selected.connect(func(_index): observed.state += 1)
	var picker = ui.context.get_node("Selection")
	picker.item_selected.connect(func(_index): observed.selection += 1)
	await choose(picker, 4)
	expect(ui.selection == "Market" and ui.actions[0].data.id == "trade-wood", "native Market selection projects market quotes")
	var last = ui.last_action
	await choose(screen, 1)
	expect(ui.screen_mode == "menu" and screen.get_item_text(screen.selected) == "Menu", "screen selector navigates to menu")
	await click(ui.find_child("StartMenu", true, false).get_node("Body/Solo"))
	picker = ui.context.get_node("Selection")
	expect(screen.get_item_text(screen.selected) == "Hud", "Solo synchronizes screen caption")
	expect(picker.get_item_text(picker.selected) == "Market" and ui.actions[0].data.id == "trade-wood", "HUD rebuild retains Market caption and quotes")
	expect(observed.screen == 1 and observed.selection == 1 and ui.last_action == last, "rebuild synchronization emits no additional selection or mock intents")
	await click(ui.navigation.get_node("Row/Next"))
	expect(ui.state == "foreign" and state_picker.get_item_text(state_picker.selected) == "Foreign", "next city synchronizes foreign state caption")
	await click(ui.navigation.get_node("Row/Previous"))
	expect(ui.state == "building" and state_picker.get_item_text(state_picker.selected) == "Building", "previous city synchronizes owner state caption")
	expect(observed.state == 0 and ui.last_action == last, "city caption synchronization emits no state or gameplay intents")
	await choose(state_picker, 6)
	expect(ui.state == "paused" and ui.actions[0].get_node("Body/Action").disabled, "native state selection retains paused quote gate")
	await choose(state_picker, 0)
	await choose(picker, 0)
	expect(ui.selection == "Producer" and ui.actions[0].data.id == "upgrade", "native selection returns to ordinary Producer quotes")
	await choose(screen, 2)
	expect(ui.dialog.visible and screen.get_item_text(screen.selected) == "Research", "screen selector opens requested dialog")
	await key(KEY_ESCAPE)
	await choose(screen, 0)
	expect(ui.screen_mode == "hud" and ui.dialog == null, "screen selector returns from dialog to HUD")
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
func details_projections() -> void:
	ui.open_dialog("details")
	var details = ui.dialog_content
	for index in range(4):
		await choose(details.sample, index)
		var summaries = details.food.get_children()
		if index == 0:
			expect(summaries.size() == 1 and summaries[0].data.heading.contains("Next battle"), "Details planning forecast only")
		elif index == 1:
			expect(summaries.size() == 1 and summaries[0].data.heading.contains("Paid this battle"), "Details immutable paid current wave")
			expect(summaries[0].data.rows[0].value == "18" and details.reward_heading.text.contains("W1"), "current paid and previous reward distinct")
		elif index == 2:
			expect(summaries.size() == 2 and summaries[0].data.heading.contains("Next battle") and summaries[1].data.heading.contains("Last completed"), "last receipt and forecast separate")
			expect(summaries[1].data.rows[2].value == "17" and details.reward_heading.text.contains("W2"), "last wave exact sitouts and reward wave")
		else:
			expect(summaries.size() == 1 and summaries[0].data.heading.contains("No completed"), "fresh projection clears paid receipts")
			expect(details.roster.buttons.is_empty() and details.reward.text.contains("Nothing carried") and details.allocation.text.contains("No queued"), "fresh projection clears roster reward allocation")
	await choose(details.sample, 0)
	await click(details.roster.buttons[101])
	expect(ui.last_action.contains("inspect-101"), "Details restored roster emits identity")
	details.set_context("foreign")
	await choose(details.sample, 1)
	expect(details.heading.text.contains("P2") and details.context_label.text.contains("Read-only"), "Details view switching preserves external readonly owner")
	ui.close_dialog()
	for state in ["combat", "victory"]:
		ui.state = state
		ui.open_dialog("details")
		expect(ui.dialog_content.sample.selected == (1 if state == "combat" else 2), "host projects Details receipt " + state)
		ui.close_dialog()
	ui.state = "building"
func hall_projections() -> void:
	ui.open_dialog("town_hall")
	var hall = ui.dialog_content
	var observed: Array = []
	var listener = func(id): observed.append(id)
	hall.requested.connect(listener)
	var last = ui.last_action
	await runner.click(hall.sale.get_node("Body/Action"))
	expect(ui.last_action == last and hall.sale.data.reason.contains("occupied"), "occupied sale rejected with visible reason")
	await choose(hall.sample, 1)
	expect(hall.roster.buttons.is_empty() and not hall.card.visible and hall.empty_label.visible, "empty hall has no stale unit actions")
	await click(hall.sale.get_node("Body/Action"))
	expect(observed.back() == "sell-hall", "empty hall sale emits only adapter intent")
	expect(hall.roster.buttons.is_empty(), "sale intent does not mutate hall projection")
	await choose(hall.sample, 2)
	await click(hall.roster.buttons[103])
	expect(hall.card.data.id == 103 and hall.card.get_node("Body/Send").disabled and hall.card.get_node("Body/Retire").disabled, "stale hall selection remains inspection")
	for quote in [hall.storage, hall.healing, hall.sale]:
		last = ui.last_action
		await click(quote.get_node("Body/Action"))
		expect(quote.get_node("Body/Action").disabled and ui.last_action == last, "stale quote refuses pointer intent")
	await choose(hall.sample, 3)
	expect(hall.roster.buttons.size() == 6 and hall.storage.data.quote.contains("12 gold"), "storage track projection exact independent tile/quote")
	await click(hall.storage.get_node("Body/Action"))
	expect(observed.back() == "storage-upgrade" and hall.roster.buttons.size() == 6, "storage intent never changes capacity locally")
	await click(hall.healing.get_node("Body/Action"))
	expect(observed.back() == "healing-upgrade", "healing remains independent of storage")
	await choose(hall.sample, 4)
	expect(hall.card.get_node("Body/Recovery").text.contains("Funded survivor"), "completed funding recovery eligibility")
	var hp = hall.card.get_node("Body/HealthText").text
	await key(KEY_ENTER)
	expect(hall.card.get_node("Body/HealthText").text == hp, "selection never applies a heal")
	await click(hall.roster.buttons[102])
	expect(hall.card.get_node("Body/Recovery").text.contains("not eligible") and hall.card.get_node("Body/HealthText").text == "34 / 54 HP", "unfunded wounded reserve no recovery")
	expect(hall.healing.get_node("Body/Action").disabled, "maximum healing projection")
	await click(hall.roster.buttons[103])
	expect(hall.card.get_node("Body/Recovery").text.contains("Full health"), "full-health recovery text")
	await choose(hall.sample, 5)
	expect(hall.card.get_node("Body/Send").disabled and hall.card.get_node("Body/Reason").text.contains("cannot fit"), "fragmented field destination no pooled space")
	hall.set_read_only("Foreign inspection")
	await choose(hall.sample, 1)
	expect(hall.sale.get_node("Body/Action").disabled, "external readonly survives empty hall projection")
	await choose(hall.sample, 4)
	await click(hall.roster.buttons[102])
	expect(hall.card.get_node("Body/Retire").disabled, "external readonly survives recovery view selection")
	hall.requested.disconnect(listener)
	ui.close_dialog()
func edge_controls() -> void:
	var observed = {"city":-1}
	var listener = func(id): observed.city = id
	ui.navigation.city_requested.connect(listener)
	ui.navigation.set_data([{"id":1,"label":"Only city","context":"Owner"}], 1)
	var before = ui.last_action
	await runner.click(ui.navigation.get_node("Row/Next"))
	expect(ui.navigation.get_node("Row/Next").disabled and observed.city == -1 and ui.last_action == before, "one-city navigation disabled")
	var cities = [{"id":1,"label":"P1"},{"id":2,"label":"P2"},{"id":3,"label":"P3"},{"id":4,"label":"P4"}]
	ui.navigation.set_data(cities, 4)
	await click(ui.navigation.get_node("Row/Next"))
	expect(observed.city == 1, "four-city wrap intent")
	ui.navigation.set_data(cities, 1)
	await click(ui.navigation.get_node("Row/Previous"))
	expect(observed.city == 4, "four-city reverse wrap intent")
	ui.navigation.city_requested.disconnect(listener)
	for state in ["lobby", "fallen", "stale"]:
		ui.state = state
		ui.refresh_hud()
		await frames()
		expect(ui.actions[0].get_node("Body/Action").disabled, "edge readonly quote " + state)
		if state == "lobby":
			await click(ui.match_controls.get_node("Start"))
			expect(ui.last_action.contains("start"), "lobby native Start intent")
		elif state == "fallen":
			expect(ui.ledger.value_labels["Gold"][1].text == "0", "fallen city future income zero")
			await click(ui.match_controls.get_node("Pause"))
			expect(ui.last_action.contains("pause"), "fallen owner retains shared pause")
		else: expect(ui.ledger.data.context.contains("Stale"), "stale snapshot explicit context")
	ui.state = "building"
	ui.selection = "Empty plot"
	ui.refresh_hud()
	var tabs = ui.context.get_node("Actions").get_child(1)
	for index in range(4):
		tabs.grab_focus()
		await key(KEY_HOME)
		for i in range(index): await key(KEY_RIGHT)
		await click(ui.actions[0].get_node("Body/Action"))
		expect(ui.last_action.contains(ui.actions[0].data.id), "native construction group intent " + str(index))
	ui.selection = "Recruiter"
	ui.refresh_hud()
	var recruiter = ui.context.get_node("Actions/RecruiterType")
	await choose(recruiter, 1)
	await click(ui.actions[0].get_node("Body/Action"))
	expect(ui.last_action.contains("Crossbowman"), "native ranged recruiter intent")
	await choose(recruiter, 2)
	before = ui.last_action
	await runner.click(ui.actions[0].get_node("Body/Action"))
	expect(ui.last_action == before and ui.actions[0].data.reason.contains("Weaver"), "native insufficient Mage quote")
	ui.selection = "Producer"
	ui.open_dialog("components")
	var samples = ui.dialog_content
	var feedback = samples.get_node("FeedbackCard")
	for index in range(5):
		await choose(samples.get_node("FeedbackSample"), index)
		expect(feedback.get_node("Status").text == ["Connecting", "Connected", "Reconnecting", "Expired session", "Action rejected"][index], "feedback projection " + str(index))
		if index == 3:
			await click(feedback.get_node("Actions/Fresh"))
			expect(ui.last_action.contains("fresh-session"), "expired session exposes distinct fresh intent")
	ui.close_dialog()
	ui.refresh_hud()
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
	var screen = ui.find_child("ScreenSelector", true, false)
	expect(screen.get_item_text(screen.selected) == "Menu", "Return confirmation synchronizes screen caption")
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
