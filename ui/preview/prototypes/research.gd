extends VBoxContainer
signal requested(technology_id: String)
var role = 0
var mode = "available"
var read_only_reason = ""
var choices: Array = []
var points_label: Label
func _ready() -> void:
	points_label = WatchUI.label(self, "6 research points · progress 2/3", "HeadingLabel")
	WatchUI.label(self, "Towers: +1 progress/production · +1 point/shared clear", "ContextLabel")
	var tabs = TabBar.new()
	tabs.name = "Classes"
	for name in ["Melee", "Ranged", "Magic"]: tabs.add_tab(name)
	add_child(tabs)
	tabs.tab_changed.connect(func(index): role = index; refresh())
	var sample = OptionButton.new()
	sample.name = "AccessSample"
	for name in ["Available", "First specialization owned", "Foreign inspection", "Funded mastery"]: sample.add_item(name)
	add_child(sample)
	sample.item_selected.connect(func(index): mode = ["available", "owned", "foreign", "funded"][index]; refresh())
	var scroll = WatchUI.scroll(self, "TreeScroll", 340)
	var nodes = WatchUI.stack(scroll)
	nodes.name = "Nodes"
	refresh()
func refresh() -> void:
	points_label.text = ("12" if mode == "funded" else "6") + " research points · progress 2/3"
	WatchUI.clear($TreeScroll/Nodes)
	choices.clear()
	var definitions = UIFixtures.technologies(role)
	for index in range(definitions.size()):
		var data = definitions[index]
		if not read_only_reason.is_empty(): data.enabled = false; data.reason = read_only_reason
		elif mode == "foreign": data.enabled = false; data.reason = "Read-only: another player's research."
		elif mode == "funded" and index > 0:
			data.enabled = index == 2
			data.reason = "Owned" if index == 1 else "Available; replaces earlier effect." if index == 2 else "Permanently locked by sibling specialization."
		elif mode == "owned" and index > 0:
			data.enabled = false
			data.reason = "Owned" if index == 1 else "Need 3 more research points." if index == 2 else "Permanently locked by sibling specialization."
		var node = WatchUI.component("quoted_action", $TreeScroll/Nodes)
		node.set_data(data)
		node.requested.connect(func(id): requested.emit(id))
		choices.append(node)
