extends VBoxContainer
# Standalone supplied projections. Selection/action never author acquired state.
var tree: Control
var stage = 0
var status: Label
var picker: OptionButton

func _ready() -> void:
	var toolbar = HBoxContainer.new()
	add_child(toolbar)
	picker = OptionButton.new()
	for title in ["A · Root only", "B · Trunk awakened", "C · Main branches awakened", "D · Independent left family"]: picker.add_item(title)
	toolbar.add_child(picker)
	picker.item_selected.connect(show_stage)
	var demonstration = Button.new()
	demonstration.text = "Demonstrate one child awakening"
	toolbar.add_child(demonstration)
	demonstration.pressed.connect(demonstrate)
	status = Label.new()
	status.text = "Externally supplied visual states · no allocation"
	status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toolbar.add_child(status)
	tree = preload("res://UI/components/worldtree.tscn").instantiate()
	add_child(tree)
	tree.node_action_requested.connect(func(id): status.text = "Action requested: " + id + " (no local acquisition)")
	show_stage(0)

func fixture(index: int) -> Dictionary:
	var acquired: Array = tree.topology.activation_fixtures[index].owned.duplicate()
	var available: Array = []
	var icons: Dictionary = {}
	for n in tree.topology.nodes:
		icons[n.id] = n.icon_key
		if n.id not in acquired and n.parent in acquired: available.append(n.id)
	return {"acquired":acquired,"available":available,"icons":icons,"selected":"root","points":5}

func show_stage(index: int) -> void:
	stage = index
	picker.select(index)
	tree.set_data(fixture(index))

func demonstrate() -> void:
	# Demo driver, not the component action callback, supplies a new snapshot.
	show_stage(2)
	var next = fixture(2)
	next.acquired.append("secondary_left_a")
	next.available.erase("secondary_left_a")
	next.available.append_array(["terminal_left_a_1", "terminal_left_a_2"])
	next.selected = "secondary_left_a"
	tree.set_data(next, "secondary_left_a")
