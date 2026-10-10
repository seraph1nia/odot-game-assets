extends SceneTree
# Focused native resource host. Fixture data and Theme sample are authoring-only.
var output: String
var host: Control
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
	call_deferred("capture")
func settle() -> void:
	for i in range(6): await process_frame
	await RenderingServer.frame_post_draw
func fresh() -> VBoxContainer:
	if is_instance_valid(host):
		host.queue_free()
		await process_frame
	host = Control.new()
	host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	host.theme = load("res://UI/theme/ledger.tres")
	root.add_child(host)
	var background = ColorRect.new()
	background.color = Color("718982")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	host.add_child(background)
	var margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "top", "right", "bottom"]: margin.add_theme_constant_override("margin_" + side, 24)
	host.add_child(margin)
	return WatchUI.stack(margin, 12)
func save_view(id: String, resource: String) -> void:
	await settle()
	var error = root.get_texture().get_image().save_png(output.path_join(id + ".png"))
	if error != OK: push_error("Catalog capture failed: " + id); quit(1)
	print("UI_CATALOG_CAPTURE ", id, " ", resource)
func capture() -> void:
	root.size = Vector2i(640, 480)
	var names = {"resource-table":"resource_ledger", "upkeep":"upkeep_summary", "action-quote":"quoted_action", "city-navigation":"city_navigation", "match-controls":"match_controls", "session-feedback":"session_feedback", "unit-inspection":"unit_inspection", "roster":"army_roster", "dialog-shell":"modal"}
	for id in names:
		var body = await fresh()
		var component = load("res://UI/components/" + names[id] + ".tscn").instantiate()
		if id == "dialog-shell":
			# Modal is deliberately outside layout containers, per the API.
			host.add_child(component)
			component.title = "Scrollable dialog shell"
			WatchUI.label(component.get_content(), "Example content supplied by the host.\nThe shell owns header, scroll body, close and focus scope.")
			component.popup_centered_clamped(Vector2i(520, 330))
		else:
			body.add_child(component)
			match id:
				"resource-table": component.set_data(UIFixtures.resources("building"))
				"upkeep": component.set_data(UIFixtures.upkeep("building"))
				"action-quote": component.set_data({"id":"upgrade", "title":"Upgrade Sawmill I → II", "quote":"4 gold · 2 wood · 1 stone\nOutput +2 wood per building turn", "enabled":true, "reason":"Supplied quote; this control emits intent only."})
				"city-navigation": component.set_data([{"id":0, "label":"P1 · Your city", "context":"Owner"}, {"id":1, "label":"P2 · Inspection", "context":"Read-only"}], 0)
				"match-controls": component.set_data(UIFixtures.match_state("preparation"))
				"session-feedback": component.set_data({"status":"Connection lost", "message":"The host supplies this message and recovery eligibility.", "reconnect":true, "fresh":true})
				"unit-inspection": component.set_data(UIFixtures.unit())
				"roster": component.set_data(UIFixtures.roster(true))
		await save_view(id, component.scene_file_path)
	var body = await fresh()
	var panel = PanelContainer.new()
	body.add_child(panel)
	var controls = WatchUI.stack(panel, 10)
	WatchUI.label(controls, "Ledger Theme · native control sample", "HeadingLabel")
	WatchUI.label(controls, "Not an additional runtime component", "ContextLabel")
	var row = WatchUI.row(controls)
	WatchUI.button(row, "Normal")
	var selected = WatchUI.button(row, "Selected")
	selected.toggle_mode = true
	selected.button_pressed = true
	var disabled = WatchUI.button(row, "Disabled")
	disabled.disabled = true
	var focus = WatchUI.button(controls, "Keyboard focus")
	focus.grab_focus()
	var choice = OptionButton.new()
	choice.add_item("Native option")
	controls.add_child(choice)
	var edit = LineEdit.new()
	edit.text = "Native text entry"
	controls.add_child(edit)
	var slider = HSlider.new()
	slider.value = 65
	controls.add_child(slider)
	var progress = ProgressBar.new()
	progress.value = 63
	controls.add_child(progress)
	await save_view("theme", host.theme.resource_path)
	quit()
