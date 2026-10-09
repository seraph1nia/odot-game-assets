extends Node
# Temporary bounded causal probe, not a shipped input router.
var ui: Control
var autorun = true
var scenario = "baseline"
var input_mode = "synthetic"
var ack_path = ""
var counterfactual = "none"
var sequence = 0
var canceled = 0
var close_requests = 0
var esc_windows: Array = []
var failures: Array = []
var checks = 0
var unhandled_esc = 0

func _unhandled_input(event: InputEvent) -> void:
	if is_esc(event): unhandled_esc += 1

func _ready() -> void:
	if not autorun: return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--case="): scenario = arg.get_slice("=", 1)
		if arg.begins_with("--input="): input_mode = arg.get_slice("=", 1)
		if arg.begins_with("--counterfactual="): counterfactual = arg.get_slice("=", 1)
		if arg.begins_with("--ack="): ack_path = arg.trim_prefix("--ack=")
	get_window().position = Vector2i.ZERO
	get_window().window_input.connect(func(event): observe_esc("root-window", event))
	ui = load("res://prototypes/showcase.tscn").instantiate()
	add_child(ui)
	await frames()
	var opener = ui.find_child("Settings", true, false)
	opener.grab_focus()
	ui.open_dialog("settings", opener)
	await frames()
	var window = ui.dialog
	var settings = ui.dialog_content
	if window is Window:
		window.window_input.connect(func(event): observe_esc("settings-window", event))
		window.close_requested.connect(func(): close_requests += 1; print("CLOSE_REQUEST settings"))
	window.canceled.connect(func(): canceled += 1; print("CANCELED settings"))
	for control in [settings.display_mode, settings.resolution, settings.volume, window.get_ok_button()]:
		var name = control.name
		control.gui_input.connect(func(event):
			if is_esc(event): print("GUI_ESC ", name, " handled=", control.get_viewport().is_input_handled()))
	settings.display_mode.get_popup().window_input.connect(func(event): observe_esc("dropdown-window", event))
	print("NATIVE_WINDOW ", DisplayServer.window_get_native_handle(DisplayServer.WINDOW_HANDLE))
	snapshot("opened")
	if scenario == "modal":
		await modal_scope(settings, opener)
		print("DIAG_RESULT ", JSON.stringify({"case":scenario,"input":input_mode,"checks":checks,"failures":failures,"world_clicks":ui.world_clicks}))
		get_tree().quit(0 if failures.is_empty() else 1)
		return
	if scenario in ["dropdown", "full"]:
		settings.display_mode.grab_focus()
		await key(KEY_ENTER)
		snapshot("dropdown-open")
		expect(settings.display_mode.get_popup().visible, "Enter opens native dropdown")
		await key(KEY_ESCAPE)
		snapshot("dropdown-closed")
		expect(not settings.display_mode.get_popup().visible and window.visible, "dropdown-first Esc")
	if scenario in ["fullscreen", "full"]:
		settings.display_mode.grab_focus()
		await key(KEY_ENTER)
		await key(KEY_DOWN)
		await key(KEY_ENTER)
		snapshot("fullscreen-selected")
		expect(settings.resolution.disabled, "Fullscreen selected with native keys")
	if scenario in ["slider", "slider-focus", "full"]:
		settings.get_node("Categories").current_tab = 1
		await frames()
		settings.volume.grab_focus()
		var previous = settings.volume.value
		if scenario != "slider-focus": await key(KEY_RIGHT)
		snapshot("slider-focus-or-edit")
		if scenario != "slider-focus": expect(settings.volume.value > previous, "slider keyboard edit")
	if scenario in ["outside", "full"]:
		await click_point(Vector2(80,220))
		snapshot("outside-click")
		expect(window.visible, "outside click does not dismiss")
		expect(ui.world_clicks == 0, "outside world click blocked")
		if counterfactual == "focus":
			window.grab_focus()
			await frames()
			snapshot("counterfactual-focus-restored")
	snapshot("before-final-esc")
	esc_windows.clear()
	await key(KEY_ESCAPE)
	snapshot("after-final-esc")
	expect(not window.visible, "Esc closes dialog")
	expect(canceled == 1, "one modal cancellation")
	expect(get_viewport().gui_get_focus_owner() == opener, "focus returns to invoker")
	expect(ui.world_clicks == 0, "zero leaked world actions")
	expect(unhandled_esc == 0, "active modal and dropdown consume Esc before underlying input")
	print("DIAG_RESULT ", JSON.stringify({"case":scenario,"input":input_mode,"visible":window.visible,
		"canceled":canceled,"close_requests":close_requests,"esc_windows":esc_windows,"world_clicks":ui.world_clicks,
		"checks":checks,"failures":failures}))
	get_tree().quit(0 if failures.is_empty() else 1)

func expect(condition: bool, message: String) -> void:
	checks += 1
	if not condition: failures.append(message); push_error("Modal assertion: " + message)

func frames() -> void:
	for i in range(4): await get_tree().process_frame
func is_esc(event: InputEvent) -> bool:
	return event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE
func observe_esc(view: String, event: InputEvent) -> void:
	if is_esc(event):
		esc_windows.append(view)
		print("WINDOW_ESC ", view)
func click_control(control: Control) -> void:
	await click_point(control.get_global_rect().get_center())

func inside(modal: Control) -> bool:
	var focus = get_viewport().gui_get_focus_owner()
	return focus != null and modal.is_ancestor_of(focus)

func modal_scope(settings: Control, opener: Control) -> void:
	var initial_world_clicks = ui.world_clicks
	var modal = ui.dialog
	if input_mode == "os":
		await native_request({"focus":"away"})
		for index in range(12): await get_tree().process_frame
		expect(not get_window().has_focus() and modal.visible, "application focus loss does not steal focus or close modal")
		await native_request({"focus":"back"})
		expect(get_window().has_focus(), "owned OS fixture returns application focus")
	await click_control(settings.display_mode)
	expect(settings.display_mode.get_popup().visible, "pointer opens native dropdown")
	await key(KEY_ESCAPE)
	expect(modal.visible and not settings.display_mode.get_popup().visible, "pointer dropdown owns first Esc")
	expect(unhandled_esc == 0, "dropdown Esc does not reach underlying input")
	modal.get_ok_button().grab_focus()
	var visited = {}
	for shift in [false, true]:
		for index in range(14):
			await key(KEY_TAB, shift)
			expect(inside(modal), "Tab containment shift=" + str(shift) + " step=" + str(index))
			var current = get_viewport().gui_get_focus_owner()
			if current != null: visited[current.get_instance_id()] = true
	var tabs = settings.get_node("Categories")
	var bar = tabs.get_tab_bar()
	expect(visited.has(bar.get_instance_id()), "Tab visits native internal category TabBar")
	for index in range(10):
		if get_viewport().gui_get_focus_owner() == bar: break
		await key(KEY_TAB)
	expect(get_viewport().gui_get_focus_owner() == bar, "Tab reaches categories without fixture refocus")
	await key(KEY_RIGHT)
	expect(tabs.current_tab == 1, "native category Right selects Audio")
	await key(KEY_LEFT)
	expect(tabs.current_tab == 0, "native category Left returns Graphics")
	await click_point(bar.get_global_position() + bar.get_tab_rect(1).get_center())
	expect(tabs.current_tab == 1, "pointer selects Audio tab")
	var previous = settings.volume.value
	await click_point(settings.volume.get_global_position() + settings.volume.size * Vector2(.75,.5))
	expect(settings.volume.value != previous, "pointer adjusts native slider")
	await click_control(modal.get_node("Center/Panel/Body/Header/Cancel"))
	expect(not modal.visible and canceled == 1, "pointer closes active modal")
	expect(get_viewport().gui_get_focus_owner() == opener, "pointer close returns focus")
	await key(KEY_ENTER)
	expect(ui.dialog.visible and ui.dialog != modal, "invoker Enter reopens fresh modal")
	var hidden = ui.dialog
	var hidden_cancels = {"count":0}
	hidden.canceled.connect(func(): hidden_cancels.count += 1)
	hidden.hide()
	await frames()
	expect(not hidden.is_processing_input(), "hidden modal disables input scope")
	await key(KEY_ESCAPE)
	expect(hidden_cancels.count == 0, "hidden modal does not consume Esc")
	expect(unhandled_esc == 1, "hidden modal allows ordinary underlying input")
	await click_control(opener)
	expect(ui.dialog.visible, "pointer reopens after external hide")
	await key(KEY_ENTER)
	expect(not ui.dialog.visible, "native Enter closes focused Close button")
	expect(get_viewport().gui_get_focus_owner() == opener, "Enter close focus return")
	await key(KEY_ENTER)
	settings = ui.dialog_content
	modal = ui.dialog
	var return_button = settings.get_child(1)
	return_button.grab_focus()
	await key(KEY_ENTER)
	expect(ui.active_confirmation != null and ui.active_confirmation.visible and modal.visible, "Enter opens owned confirmation")
	for shift in [false,true]:
		for index in range(4):
			await key(KEY_TAB, shift)
			expect(inside(ui.active_confirmation), "confirmation focus scope " + str(shift) + str(index))
	await key(KEY_ESCAPE)
	expect(ui.active_confirmation == null and modal.visible, "Esc cancels only confirmation")
	expect(get_viewport().gui_get_focus_owner() == return_button, "confirmation restores Settings invoker")
	await click_control(return_button)
	expect(ui.active_confirmation != null, "pointer reopens confirmation")
	await key(KEY_ENTER)
	expect(ui.screen_mode == "menu" and ui.dialog == null, "native confirmation Enter applies mock return intent")
	expect(ui.last_action.contains("return-menu"), "return intent is distinct")
	expect(ui.world_clicks == initial_world_clicks, "zero leaked world actions across modal lifecycle")
	expect(unhandled_esc == 1, "only deliberate hidden-modal Esc reaches underlying input")

func focus_name(view: Viewport) -> String:
	var focus = view.gui_get_focus_owner()
	return str(focus.get_path()) if focus != null else "none"
func snapshot(stage: String) -> void:
	print("OBS ", JSON.stringify({"stage":stage,"root_focus":focus_name(get_viewport()),
		"dialog_focus":focus_name(ui.dialog.get_viewport()), "dialog_visible":ui.dialog.visible,
		"parent_type":ui.dialog.get_parent().get_class(), "parent_path":str(ui.dialog.get_parent().get_path()),
		"last_exclusive":str(ui.get_last_exclusive_window().get_path()),
		"window_focus":ui.dialog.get_window().has_focus(), "canceled":canceled,"world_clicks":ui.world_clicks}))
func native_request(data: Dictionary) -> void:
	sequence += 1
	data.sequence = sequence
	print("NATIVE_EVENT ", JSON.stringify(data))
	var deadline = Time.get_ticks_msec() + 3000
	while Time.get_ticks_msec() < deadline:
		if FileAccess.file_exists(ack_path):
			var file = FileAccess.open(ack_path, FileAccess.READ)
			if int(file.get_as_text()) == sequence:
				await frames()
				return
		await get_tree().process_frame
	push_error("Native driver did not acknowledge event")
	get_tree().quit(1)
func key(code: Key, shift: bool = false) -> void:
	if input_mode == "os":
		await native_request({"key":{KEY_ENTER:"Return", KEY_ESCAPE:"Escape", KEY_DOWN:"Down", KEY_RIGHT:"Right", KEY_LEFT:"Left", KEY_TAB:"Tab"}[code], "shift":shift})
		return
	for pressed in [true,false]:
		var event = InputEventKey.new()
		event.keycode = code
		event.shift_pressed = shift
		event.pressed = pressed
		Input.parse_input_event(event)
		await frames()
func click_point(point: Vector2) -> void:
	if input_mode == "os":
		await native_request({"click":[int(point.x),int(point.y)]})
		return
	var motion = InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	for pressed in [true,false]:
		var event = InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = point
		event.global_position = point
		event.pressed = pressed
		Input.parse_input_event(event)
		await frames()
