extends VBoxContainer
# Presentation only: all costs, recovery and sale/transfer eligibility are supplied.
signal requested(action_id: String)
signal unit_requested(action_id: String, unit_id: int, destination_id: String)
var data: Dictionary = {}
var roster: Control
var card: Control
var storage: Control
var healing: Control
var sale: Control
var heading: Label
var context_label: Label
var empty_label: Label
var sample: OptionButton
var read_only_reason = ""
func _ready() -> void:
	sample = OptionButton.new()
	sample.name = "HallSample"
	for title in ["Occupied reserves", "Empty hall", "Stale hall", "Storage upgrade", "Recovery eligibility", "No fitting field tile"]: sample.add_item(title)
	add_child(sample)
	sample.item_selected.connect(func(index): set_data(UIFixtures.hall(["occupied", "empty", "stale", "storage", "recovery", "fragmented"][index])))
	heading = WatchUI.label(self, "", "HeadingLabel")
	context_label = WatchUI.label(self, "", "ContextLabel")
	var tracks = WatchUI.row(self)
	storage = WatchUI.component("quoted_action", tracks)
	storage.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	storage.requested.connect(func(id): requested.emit(id))
	healing = WatchUI.component("quoted_action", tracks)
	healing.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	healing.requested.connect(func(id): requested.emit(id))
	sale = WatchUI.component("quoted_action", self)
	sale.requested.connect(func(id): requested.emit(id))
	var body = WatchUI.row(self, 12)
	roster = WatchUI.component("army_roster", body)
	roster.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card = WatchUI.component("unit_inspection", body)
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	empty_label = WatchUI.label(self, "No reserve selected. An empty hall has no transfer or retirement action.", "ContextLabel")
	roster.unit_selected.connect(select_unit)
	card.requested.connect(func(id, unit, destination): unit_requested.emit(id, unit, destination))
	set_data(UIFixtures.hall("occupied"))
func set_data(value: Dictionary) -> void:
	data = value.duplicate(true)
	sample.select(["occupied", "empty", "stale", "storage", "recovery", "fragmented"].find(str(data.get("sample", "occupied"))))
	heading.text = str(data.get("title", "Town hall"))
	context_label.text = str(data.get("context", ""))
	for entry in [[storage, "storage"], [healing, "healing"], [sale, "sale"]]:
		var quote: Dictionary = data.get(entry[1], {}).duplicate(true)
		if not read_only_reason.is_empty(): quote.enabled = false; quote.reason = read_only_reason
		entry[0].set_data(quote)
	roster.set_data(data.get("roster", {}))
	select_unit(int(data.get("selected_id", -1)))
func select_unit(id: int) -> void:
	var profiles: Dictionary = data.get("profiles", {})
	card.visible = profiles.has(id)
	empty_label.visible = not card.visible
	if not card.visible: return
	data.selected_id = id
	data.roster.selected_id = id
	var unit: Dictionary = profiles[id].duplicate(true)
	if not read_only_reason.is_empty():
		unit.can_retire = false
		unit.can_send = false
		unit.reason = read_only_reason
	card.set_data(unit)
func set_read_only(reason: String) -> void:
	read_only_reason = reason
	set_data(data)
	# One selection callback reapplies the external projection gate, not gameplay rules.
