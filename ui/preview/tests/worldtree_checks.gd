extends Node
var runner: Node

func fixture(tree: Control, index: int) -> Dictionary:
	var acquired: Array = tree.topology.activation_fixtures[index].owned.duplicate()
	var icons: Dictionary = {}
	var available: Array = []
	for n in tree.topology.nodes:
		icons[n.id] = n.icon_key
		if n.id not in acquired and n.parent in acquired: available.append(n.id)
	return {"acquired":acquired,"available":available,"icons":icons,"selected":"root","points":5}

func witness(tree: Control, id: String) -> Array:
	var v: Dictionary = tree.visuals[id]
	var result = [tree.buttons[id].position, v.halo.modulate, v.icon.modulate, v.icon.texture.resource_path]
	if tree.edges.has(id):
		var e: Dictionary = tree.edges[id]
		result.append_array([e.sap.progress,e.fresh.modulate,e.dead.visible,e.bark.position,e.sap.route])
	return result

func run() -> void:
	runner.ui.hide()
	var tree = preload("res://UI/components/worldtree.tscn").instantiate()
	tree.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	runner.add_child(tree)
	await runner.frames(8)
	runner.expect(not tree.canvas.visible and tree.action.disabled, "no snapshot cannot imply an acquired/available visual state")
	var pending = preload("res://UI/components/worldtree.tscn").instantiate()
	runner.expect(pending.set_data(fixture(tree,0)), "complete pre-ready snapshot accepted")
	runner.add_child(pending)
	await runner.frames(2)
	runner.expect(pending.canvas.visible and pending.node_state("root") == "acquired" and pending.edges.trunk_1.sap.progress == 0, "pre-ready snapshot presents root-only without stale living children")
	pending.queue_free()
	await runner.frames(2)
	runner.expect(tree.buttons.size() == 24 and tree.edges.size() == 23, "Worldtree exactly 24 native controls / 23 independent wooden edges")
	for child in tree.find_children("*", "TextureRect", true, false): runner.expect(child.mouse_filter == Control.MOUSE_FILTER_IGNORE, "all artwork pointer-inert " + child.texture.resource_path)
	var stable: Dictionary = {}
	for id in tree.buttons: stable[id] = tree.buttons[id].get_instance_id()
	for dimensions in [Vector2i(1100,820),Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080)]:
		get_window().size = dimensions
		await runner.frames(8)
		for stage in range(4):
			runner.expect(tree.set_data(fixture(tree,stage)), "Worldtree accepts complete stage " + str(stage))
			await runner.frames(4)
			runner.expect(tree.snapshot.acquired.size() == [1,3,6,10][stage], "exact acquired count stage " + str(stage))
			for n in tree.topology.nodes:
				var id: String = n.id
				runner.expect(tree.buttons[id].get_instance_id() == stable[id], "immutable physical native node " + id)
				runner.expect(Rect2(Vector2.ZERO,Vector2(dimensions)).encloses(tree.buttons[id].get_global_rect()), "all sockets visible " + id)
				if tree.edges.has(id):
					var e: Dictionary = tree.edges[id]
					runner.expect(e.sap.progress == (1.0 if id in tree.snapshot.acquired else 0.0), "only acquired incoming wood emits sap " + id)
					runner.expect(e.fresh.modulate.a == (1.0 if id in tree.snapshot.acquired else 0.0), "independent foliage " + id)
			await runner.capture("worldtree-" + ["A","B","C","D"][stage] + "-" + str(dimensions.x) + "x" + str(dimensions.y))
	get_window().size = Vector2i(1280,720)
	tree.set_data(fixture(tree,2))
	await runner.frames(8)
	var selections: Array = []
	var requests: Array = []
	tree.node_selected.connect(func(id): selections.append(id))
	tree.node_action_requested.connect(func(id): requests.append(id))
	await runner.click(tree.buttons.secondary_left_a)
	runner.expect(tree.snapshot.selected == "secondary_left_a" and selections.has("secondary_left_a"), "native pointer selects correct Worldtree ID through inert decoration")
	var before = tree.snapshot.duplicate(true)
	await runner.click(tree.action)
	runner.expect(requests == ["secondary_left_a"] and tree.snapshot == before, "action emits exact intent without acquiring/spending")
	tree.buttons.terminal_right_b_2.grab_focus()
	await runner.key(KEY_TAB)
	runner.expect(get_viewport().gui_get_focus_owner() == tree.action and tree.snapshot.selected == "secondary_left_a", "native Tab reaches request footer without changing inspected available node")
	await runner.key(KEY_ENTER)
	runner.expect(requests == ["secondary_left_a","secondary_left_a"] and tree.snapshot == before, "native keyboard request emits intent only")
	tree.buttons.terminal_right_b_2.grab_focus()
	await runner.key(KEY_ENTER)
	runner.expect(tree.snapshot.selected == "terminal_right_b_2", "native Enter inspects dormant terminal")
	tree.buttons.root.grab_focus()
	await runner.key(KEY_ENTER)
	runner.expect(tree.snapshot.selected == "root" and tree.action.disabled, "acquired root inspectable, action disabled")
	var valid = fixture(tree,2)
	for key in ["acquired","available","icons","selected","points"]:
		var invalid = valid.duplicate(true)
		invalid.erase(key)
		var previous = tree.snapshot.duplicate(true)
		runner.expect(not tree.set_data(invalid) and tree.snapshot == previous, "missing complete snapshot field rejected atomically " + key)
	for invalid in [merge(valid,{"points":-1}),merge(valid,{"points":"5"}),merge(valid,{"selected":"unknown"}),merge(valid,{"acquired":["root","root"]}),merge(valid,{"acquired":["trunk_1"]}),merge(valid,{"available":["missing"]}),merge(valid,{"available":["root"]}),merge(valid,{"icons":{"root":"missing"}})]:
		var previous = tree.snapshot.duplicate(true)
		runner.expect(not tree.set_data(invalid) and previous == tree.snapshot, "malformed visual snapshot atomic rejection")
	var unknown_icon = fixture(tree,2)
	unknown_icon.icons.root = "not_an_icon"
	runner.expect(not tree.set_data(unknown_icon), "unknown full-snapshot icon rejected")
	var zero = fixture(tree,2)
	zero.points = 0
	zero.selected = "secondary_left_a"
	tree.set_data(zero)
	tree.request_action()
	runner.expect(requests[-1] == "secondary_left_a" and tree.snapshot.points == 0, "displayed points never interpreted as eligibility or spent")
	for key in tree.topology.icon_catalog:
		var replace = fixture(tree,2)
		replace.icons.root = key
		runner.expect(tree.set_data(replace) and tree.visuals.root.icon.texture != null, "each distinct replaceable icon imported " + key)
	tree.set_data(fixture(tree,2))
	# Unfocus to remove focus-dependent selection from the rendering witnesses.
	get_viewport().gui_release_focus()
	await runner.frames(4)
	var unrelated: Dictionary = {}
	for id in tree.buttons:
		if id != "secondary_left_a": unrelated[id] = witness(tree,id)
	await runner.capture("worldtree-transition-before-1280x720")
	var next = fixture(tree,2)
	next.acquired.append("secondary_left_a")
	next.available.erase("secondary_left_a")
	# Keep unrelated snapshots unchanged to demonstrate module isolation exactly.
	var finished: Array = []
	tree.awakening_finished.connect(func(id): finished.append(id))
	runner.expect(tree.set_data(next,"secondary_left_a"), "real externally supplied child awakening starts")
	await get_tree().create_timer(.55).timeout
	var progress: float = tree.edges.secondary_left_a.sap.progress
	runner.expect(progress > .05 and progress < .95 and tree.edges.secondary_left_a.fresh.modulate.a == 0, "travelling sap in wood precedes foliage reveal")
	for id in unrelated: runner.expect(witness(tree,id) == unrelated[id], "unrelated module unchanged during travel " + id)
	await runner.capture("worldtree-transition-in-flight-1280x720")
	await get_tree().create_timer(1.7).timeout
	runner.expect(finished == ["secondary_left_a"] and tree.edges.secondary_left_a.sap.progress == 1 and tree.edges.secondary_left_a.fresh.modulate.a == 1, "child reaches endpoint then foliage and finish")
	for id in unrelated: runner.expect(witness(tree,id) == unrelated[id], "unrelated module unchanged after awakening " + id)
	await runner.capture("worldtree-transition-after-1280x720")
	runner.expect(not tree.set_data(next,"secondary_left_a"), "already acquired cannot replay false acquisition")
	tree.set_data(fixture(tree,2))
	tree.set_data(next,"secondary_left_a")
	await runner.frames(2)
	tree.set_data(fixture(tree,0))
	await get_tree().create_timer(2).timeout
	runner.expect(tree.edges.secondary_left_a.sap.progress == 0 and tree.edges.secondary_left_a.fresh.modulate.a == 0, "replacement snapshot cancels old tween without stale mutation")
	tree.hide()
	var gallery = PanelContainer.new()
	gallery.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	gallery.theme = tree.theme
	runner.add_child(gallery)
	var grid = GridContainer.new()
	grid.columns = 6
	grid.add_theme_constant_override("h_separation",30)
	grid.add_theme_constant_override("v_separation",16)
	gallery.add_child(grid)
	for key in tree.topology.icon_catalog:
		var cell = VBoxContainer.new()
		cell.custom_minimum_size = Vector2(170,112)
		grid.add_child(cell)
		var image = TextureRect.new()
		image.texture = load("res://UI/art/worldtree/icons/"+key+".svg")
		image.custom_minimum_size = Vector2(64,64)
		image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		image.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cell.add_child(image)
		var label = Label.new()
		label.text = key.replace("_"," ")
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		cell.add_child(label)
	await runner.frames(8)
	await runner.capture("worldtree-30-icon-library-1280x720")
	gallery.queue_free()
	tree.queue_free()
	await runner.frames()
	runner.ui.show()
	runner.ui.switch_screen("worldtree")
	await runner.frames(8)
	var demo = runner.ui.get_node("Layout").get_child(0).get_node("Content").get_child(0)
	runner.expect(demo.tree.buttons.size() == 24, "existing showcase discovers additive standalone Worldtree")
	await check_host(runner.ui, demo, "switch-to Worldtree")
	demo.show_stage(3)
	runner.expect(demo.picker.selected == 3, "demo stage selector matches externally shown family")
	await runner.frames(4)
	await runner.capture("worldtree-showcase-1280x720")
	await runner.click(demo.get_child(0).get_child(1))
	await get_tree().create_timer(.5).timeout
	runner.expect(demo.tree.awakening_id == "secondary_left_a" and demo.tree.edges.secondary_left_a.sap.progress > 0, "native showcase demo button drives real child transition")
	runner.expect(demo.picker.selected == 2, "child demonstration synchronizes baseline stage selector")
	runner.ui.hide()
	var direct = preload("res://prototypes/showcase.tscn").instantiate()
	direct.screen_mode = "worldtree"
	runner.add_child(direct)
	await runner.frames(8)
	var direct_demo = direct.get_node("Layout").get_child(0).get_node("Content").get_child(0)
	await check_host(direct, direct_demo, "direct Worldtree")
	direct.queue_free()
	await runner.frames()
	runner.ui.show()
	for mode in ["menu", "hud"]:
		runner.ui.switch_screen(mode)
		await runner.frames(8)
		await check_settings(runner.ui, mode, "Settings over " + mode)
	runner.ui.switch_screen("hud")
	await runner.frames(8)

func check_settings(host: Control, mode: String, label: String) -> void:
	var settings = host.find_child("Settings", true, false)
	var selector = host.find_child("ScreenSelector", true, false)
	var area = host.get_node("Layout").get_child(0).get_node("Content")
	var children = area.get_children()
	for escape in [false, true]:
		await runner.click(settings)
		runner.expect(host.dialog.visible, label + " native opener shows dialog")
		if escape: await runner.key(KEY_ESCAPE)
		else: await runner.click(host.dialog.get_ok_button())
		runner.expect(not host.dialog.visible and host.screen_mode == mode, label + " close preserves underlying screen")
		runner.expect(selector.get_item_text(selector.selected) == mode.capitalize(), label + " selector matches underlying screen")
		runner.expect(area.get_children() == children, label + " content identities survive dialog close")
		runner.expect(get_viewport().gui_get_focus_owner() == settings, label + " native invoker focus restored")
		host.close_dialog()
	await runner.click(settings)
	host.open_dialog("friends", settings)
	await runner.frames()
	await runner.key(KEY_ESCAPE)
	runner.expect(host.screen_mode == mode and area.get_children() == children, label + " dialog replacement preserves underlying screen")
	host.close_dialog()

func check_host(host: Control, demo: Control, label: String) -> void:
	await check_settings(host, "worldtree", label)
	var tree = demo.tree
	var ids: Array = tree.definitions.keys()
	var settings = host.find_child("Settings", true, false)
	var screens = host.find_child("ScreenSelector", true, false)
	var states = host.find_child("StateSelector", true, false)
	var demonstration = demo.get_child(0).get_child(1)
	for selected in ["root", "secondary_left_a", "root"]:
		var value = fixture(tree, 2)
		value.selected = selected
		tree.set_data(value)
		var before = tree.snapshot.duplicate(true)
		var enabled: bool = selected == "secondary_left_a"
		var context = label + (" enabled footer" if enabled else " disabled footer")
		tree.buttons[ids[0]].grab_focus()
		for id in ids.slice(1):
			await runner.key(KEY_TAB)
			runner.expect(get_viewport().gui_get_focus_owner() == tree.buttons[id], context + " ordered forward " + id)
		if enabled:
			await runner.key(KEY_TAB)
			runner.expect(get_viewport().gui_get_focus_owner() == tree.action, context + " terminal reaches footer")
		await runner.key(KEY_TAB)
		runner.expect(get_viewport().gui_get_focus_owner() == settings, context + " forward escape to host")
		await runner.key(KEY_TAB, true)
		runner.expect(get_viewport().gui_get_focus_owner() == (tree.action if enabled else tree.buttons[ids[-1]]), context + " backward re-entry from host")
		if enabled:
			await runner.key(KEY_TAB, true)
			runner.expect(get_viewport().gui_get_focus_owner() == tree.buttons[ids[-1]], context + " footer returns to terminal")
		var reverse = ids.slice(0, -1)
		reverse.reverse()
		for id in reverse:
			await runner.key(KEY_TAB, true)
			runner.expect(get_viewport().gui_get_focus_owner() == tree.buttons[id], context + " ordered backward " + id)
		await runner.key(KEY_TAB, true)
		runner.expect(get_viewport().gui_get_focus_owner() == demonstration, context + " backward escape to host")
		await runner.key(KEY_TAB)
		runner.expect(get_viewport().gui_get_focus_owner() == tree.buttons[ids[0]], context + " forward re-entry from host")
		await runner.key(KEY_TAB, true)
		for control in [demo.picker, states, screens, settings]:
			await runner.key(KEY_TAB, true)
			runner.expect(get_viewport().gui_get_focus_owner() == control, context + " backward host navigation " + control.name)
		for control in [screens, states, demo.picker, demonstration, tree.buttons[ids[0]]]:
			await runner.key(KEY_TAB)
			runner.expect(get_viewport().gui_get_focus_owner() == control, context + " forward host navigation " + control.name)
		runner.expect(tree.snapshot == before, context + " traversal cannot change inspection or acquisition")

func merge(value: Dictionary, replacement: Dictionary) -> Dictionary:
	var result = value.duplicate(true)
	result.merge(replacement,true)
	return result
