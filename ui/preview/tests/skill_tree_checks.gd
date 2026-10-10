extends Node
# Uses the existing native event/capture runner and an owned in-viewport host.
var runner: Node
func run() -> void:
	var window = get_window()
	window.size = Vector2i(1100, 820)
	runner.ui.hide()
	var background = ColorRect.new()
	background.color = Color("718982")
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	runner.add_child(background)
	var host = MarginContainer.new()
	host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]: host.add_theme_constant_override("margin_" + side, 24)
	runner.add_child(host)
	var tree = WatchUI.component("skill_tree", host)
	runner.expect(tree.set_data(UIFixtures.skill_tree()), "skill tree accepts caller snapshot")
	await runner.frames(8)
	runner.expect(tree.nodes.size() == 10, "compact root plus nine branch nodes")
	runner.expect(tree.node_state("foundation") == "available", "middle available first")
	for id in ["guard", "aim", "spark"]:
		runner.expect(tree.node_state(id) == "locked", "root required " + id)
	runner.expect(not tree.purchase("guard") and tree.points == 6, "outward purchase before root refused")
	await runner.capture("skill-tree-root-1100x820")
	tree.buttons.foundation.grab_focus()
	await runner.key(KEY_ENTER)
	runner.expect(tree.selected_id == "foundation", "native Enter selects middle")
	await runner.click(tree.detail.get_node("Body/Action"))
	runner.expect(tree.points == 5 and tree.node_state("foundation") == "owned", "native root purchase costs exactly one")
	for id in ["guard", "aim", "spark"]:
		runner.expect(tree.node_state(id) == "available", "three starting choices " + id)
		runner.expect(tree.links[id].default_color == Color("b88d44"), "available connector " + id)
	await runner.capture("skill-tree-three-choices-1100x820")
	tree.buttons.guard.grab_focus()
	await runner.key(KEY_ENTER)
	tree.detail.get_node("Body/Action").grab_focus()
	await runner.key(KEY_ENTER)
	runner.expect(tree.node_state("guard") == "owned" and tree.node_state("resolve") == "available", "keyboard parent unlocks next")
	runner.expect(tree.node_state("bulwark") == "locked", "grandchild remains parent-locked")
	runner.expect(tree.links.guard.width == 4 and tree.links.guard.default_color == Color("23889b"), "owned connector distinct")
	tree.select_node("resolve")
	await runner.capture("skill-tree-parent-unlock-1100x820")
	runner.expect(tree.purchase("resolve") and tree.purchase("bulwark"), "subsequent steps require preceding parent")
	runner.expect(tree.purchase("aim") and tree.points == 0, "point accounting across independent branches")
	tree.select_node("tempo")
	runner.expect(tree.node_state("tempo") == "insufficient", "funding gate separate from prerequisite")
	runner.expect(not tree.purchase("tempo") and tree.points == 0, "insufficient purchase never spends")
	runner.expect(tree.detail.get_node("Body/Action").disabled, "native purchase unavailable when insufficient")
	await runner.capture("skill-tree-insufficient-1100x820")
	tree.select_node("guard")
	var count = tree.owned.size()
	runner.expect(not tree.purchase("guard") and tree.points == 0 and tree.owned.size() == count, "already owned never spends twice")
	runner.expect(tree.detail.data.reason.contains("Already owned"), "already owned reason visible")
	await runner.capture("skill-tree-owned-1100x820")
	for titles in [["Combat", "Combat", "Support"], ["Combat", "Support", "Support"], ["Combat", "Support", "Combat"], ["Foundation", "Foundation", "Foundation"]]:
		var snapshot = UIFixtures.skill_tree()
		for branch_index in range(3):
			snapshot.branches[branch_index].title = titles[branch_index]
		runner.expect(tree.set_data(snapshot), "duplicate branch titles accepted " + str(titles))
		await runner.frames(8)
		var headings: Array = []
		for child in tree.canvas.get_children():
			if child is Label: headings.append(child)
		runner.expect(headings.size() == 3, "one heading per branch despite duplicate titles " + str(titles))
		for branch_index in range(3):
			var position = [Vector2(130, 215), Vector2(640, 215), Vector2(575, 345)][branch_index]
			var matching: Array = []
			for heading in headings:
				if heading.position == position: matching.append(heading)
			runner.expect(matching.size() == 1 and matching[0].text == titles[branch_index], "heading title at branch position " + str(branch_index) + " " + str(titles))
			for step in snapshot.branches[branch_index].nodes:
				tree.select_node(step.id)
				var quote = titles[branch_index] + " · " + str(step.cost) + " skill point(s)\n" + step.description
				runner.expect(tree.detail.get_node("Body/Quote").text == quote, "selected quote preserves supplied branch title and description " + step.id + " " + str(titles))
		if titles == ["Combat", "Combat", "Support"]:
			await runner.capture("skill-tree-duplicate-titles-1100x820")
	tree.set_data(UIFixtures.skill_tree(0))
	var invalid = UIFixtures.skill_tree()
	invalid.root.cost = 2
	runner.expect(not tree.set_data(invalid) and tree.points == 0, "invalid root cost rejected atomically")
	invalid = UIFixtures.skill_tree()
	invalid.branches[0].nodes[1].parent = "aim"
	runner.expect(not tree.set_data(invalid), "cross branch prerequisite rejected")
	invalid = UIFixtures.skill_tree()
	invalid.owned = ["guard"]
	runner.expect(not tree.set_data(invalid), "incomplete supplied ownership rejected")
	runner.expect(not tree.purchase("missing"), "unknown node refused")
	var events: Array = []
	tree.purchased.connect(func(id, remaining): events.append([id, remaining]))
	tree.set_data(UIFixtures.skill_tree(20))
	tree.purchase("foundation")
	for chain in [["guard", "resolve", "bulwark"], ["aim", "tempo", "pierce"], ["spark", "ward", "beacon"]]:
		for id in chain:
			runner.expect(tree.node_state(id) == "available" and tree.purchase(id), "all branches parent progression " + id)
	runner.expect(events.size() == 10 and events[0] == ["foundation", 19] and events[9] == ["beacon", 7], "allocation signals carry exact ids and remaining points")
	tree.set_data(UIFixtures.skill_tree(0))
	runner.expect(tree.node_state("foundation") == "insufficient" and not tree.purchase("foundation"), "unfunded root cannot unlock branches")
	window.size = Vector2i(420, 700)
	tree.set_data(UIFixtures.skill_tree())
	await runner.frames(8)
	var pointer_events: Array = []
	for target in [[tree.buttons.foundation, "root"], [tree.detail.get_node("Body/Action"), "purchase"]]:
		target[0].gui_input.connect(func(event):
			if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
				pointer_events.append(target[1] + (":down" if event.pressed else ":up")))
	runner.expect(tree.scroll.get_global_rect().encloses(tree.buttons.foundation.get_global_rect()), "middle initially visible in narrow host without stealing focus")
	runner.expect(tree.scroll.get_h_scroll_bar().max_value > tree.scroll.size.x, "narrow graph clipped by native horizontal scroll")
	var before = tree.scroll.scroll_vertical
	await wheel(tree.scroll, MOUSE_BUTTON_WHEEL_DOWN)
	runner.expect(tree.scroll.scroll_vertical > before, "native wheel scrolls clipped graph")
	before = tree.scroll.scroll_vertical
	await wheel(tree.scroll, MOUSE_BUTTON_WHEEL_UP)
	runner.expect(tree.scroll.scroll_vertical < before, "native reverse wheel scrolls graph")
	runner.expect(Input.get_mouse_button_mask() == 0, "synthetic wheel delivery releases button mask before pointer interaction")
	await runner.click(tree.buttons.foundation)
	await runner.click(tree.detail.get_node("Body/Action"))
	runner.expect(pointer_events == ["root:down", "root:up", "purchase:down", "purchase:up"], "real pointer press/release reaches both expected native targets")
	runner.expect(tree.points == 5, "narrow native root purchase costs one")
	for id in ["guard", "aim", "spark"]:
		runner.expect(tree.node_state(id) == "available", "narrow root exposes three choices " + id)
	tree.buttons.guard.grab_focus()
	await runner.key(KEY_ENTER)
	tree.detail.get_node("Body/Action").grab_focus()
	await runner.key(KEY_ENTER)
	runner.expect(tree.node_state("resolve") == "available" and tree.node_state("bulwark") == "locked", "narrow keyboard purchase unlocks parent-dependent next step")
	tree.buttons.pierce.grab_focus()
	await runner.frames(8)
	runner.expect(tree.scroll.get_global_rect().encloses(tree.buttons.pierce.get_global_rect()), "focus follows far-right node into clipped viewport")
	await runner.key(KEY_ENTER)
	runner.expect(tree.selected_id == "pierce", "locked node keyboard inspection")
	await runner.key(KEY_TAB)
	runner.expect(get_viewport().gui_get_focus_owner() != tree.buttons.pierce, "native Tab advances graph focus")
	tree.buttons.beacon.grab_focus()
	await runner.frames(8)
	runner.expect(tree.scroll.get_global_rect().encloses(tree.buttons.beacon.get_global_rect()), "focus follows bottom node vertically")
	await runner.capture("skill-tree-narrow-420x700")
	var user_scroll = Vector2(tree.scroll.scroll_horizontal, tree.scroll.scroll_vertical)
	tree.scroll.queue_sort()
	await runner.frames(8)
	runner.expect(Vector2(tree.scroll.scroll_horizontal, tree.scroll.scroll_vertical) == user_scroll, "later native sorts preserve user scroll")
	var retired: Control = tree.buttons.foundation
	tree.set_data(UIFixtures.skill_tree(0))
	tree.set_data(UIFixtures.skill_tree())
	host.remove_child(tree)
	await runner.frames(8)
	runner.expect(not is_instance_valid(retired), "rebuild retired control freed before any later layout")
	host.add_child(tree)
	await runner.frames(8)
	runner.expect(tree.scroll.get_global_rect().encloses(tree.buttons.foundation.get_global_rect()), "current root visible after removal and reattachment")
	runner.expect(tree.node_state("foundation") == "available" and tree.points == 6, "latest snapshot wins rapid rebuild")
	var disposed = WatchUI.component("skill_tree", host)
	disposed.set_data(UIFixtures.skill_tree())
	disposed.queue_free()
	await runner.frames(8)
	runner.expect(not is_instance_valid(disposed), "remove-before-sort disposes without stale-control work")
	host.queue_free()
	background.queue_free()
	await runner.frames()
	runner.ui.show()
	# The normal native modal host can open/close before its first layout, then
	# reopen at the same narrow dimensions without obsolete target callbacks.
	runner.ui.open_dialog("skill_tree")
	runner.ui.close_dialog()
	runner.ui.open_dialog("skill_tree")
	await runner.frames(8)
	var reopened = runner.ui.dialog_content.tree
	runner.expect(reopened.scroll.get_global_rect().encloses(reopened.buttons.foundation.get_global_rect()), "narrow modal reopening presents current middle")
	runner.expect(get_viewport().gui_get_focus_owner() == runner.ui.dialog.get_ok_button(), "root presentation does not steal modal focus")
	reopened.buttons.foundation.grab_focus()
	await runner.key(KEY_ENTER)
	reopened.detail.get_node("Body/Action").grab_focus()
	await runner.frames(8)
	await runner.key(KEY_ENTER)
	runner.expect(reopened.points == 5 and reopened.node_state("spark") == "available", "reopened narrow modal supports keyboard root purchase")
	runner.ui.close_dialog()
	window.size = Vector2i(1100, 820)

func wheel(scroll: ScrollContainer, code: MouseButton) -> void:
	# Pair the synthetic wheel press/release like the native platform delivery.
	# An unreleased wheel leaves Input's button mask and GUI mouse capture held,
	# so a subsequent real left click never reaches the hovered native Button.
	for pressed in [true, false]:
		var event = InputEventMouseButton.new()
		event.position = scroll.get_global_rect().get_center()
		event.global_position = event.position
		event.button_index = code
		event.pressed = pressed
		Input.parse_input_event(event)
		await runner.frames()
