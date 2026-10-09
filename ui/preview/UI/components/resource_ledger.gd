extends PanelContainer
# Caller supplies exact snapshot stocks/income. No economy computation.
var data: Dictionary = {}
var value_labels: Dictionary = {}

func _ready() -> void:
	refresh()

func set_data(value: Dictionary) -> void:
	data = value.duplicate(true)
	if is_node_ready(): refresh()

func refresh() -> void:
	WatchUI.clear($Body)
	value_labels.clear()
	WatchUI.label($Body, str(data.get("title", "Resources")), "HeadingLabel")
	var grid = GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 1)
	$Body.add_child(grid)
	for heading in ["Resource", "Stock", data.get("income_heading", "Income/turn")]:
		var l = WatchUI.label(grid, str(heading), "ContextLabel")
		l.autowrap_mode = TextServer.AUTOWRAP_OFF
	for item in data.get("rows", []):
		var name = str(item.get("name", ""))
		WatchUI.label(grid, name)
		var stock = WatchUI.label(grid, str(item.get("stock", "0")))
		var income = WatchUI.label(grid, str(item.get("income", "0")))
		for l in [stock, income]:
			l.autowrap_mode = TextServer.AUTOWRAP_OFF
			l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		value_labels[name] = [stock, income]
	var context = str(data.get("context", ""))
	if not context.is_empty(): WatchUI.label($Body, context, "ContextLabel")
