extends VBoxContainer
# Mock host accepts already-formatted projections; no receipt/reward calculation.
signal unit_selected(unit_id: int)
var data: Dictionary = {}
var heading: Label
var context_label: Label
var food: VBoxContainer
var reward_heading: Label
var reward: Label
var roster: Control
var allocation_heading: Label
var allocation: Label
var sample: OptionButton
var context_title = ""
var context_text = ""
func _ready() -> void:
	sample = OptionButton.new()
	sample.name = "DetailsSample"
	for title in ["Planning forecast", "Paid current wave", "Last completed wave", "Fresh session"]: sample.add_item(title)
	add_child(sample)
	sample.item_selected.connect(func(index): set_data(UIFixtures.details(["planning", "paid", "last", "fresh"][index])))
	heading = WatchUI.label(self, "", "HeadingLabel")
	context_label = WatchUI.label(self, "", "ContextLabel")
	food = WatchUI.stack(self)
	reward_heading = WatchUI.label(self, "", "HeadingLabel")
	reward = WatchUI.label(self, "", "ContextLabel")
	roster = WatchUI.component("army_roster", self)
	roster.unit_selected.connect(func(id): unit_selected.emit(id))
	allocation_heading = WatchUI.label(self, "", "HeadingLabel")
	allocation = WatchUI.label(self, "")
	set_data(UIFixtures.details("planning"))
func set_data(value: Dictionary) -> void:
	data = value.duplicate(true)
	sample.select(["planning", "paid", "last", "fresh"].find(str(data.get("sample", "planning"))))
	heading.text = context_title if not context_title.is_empty() else str(data.get("title", "City details"))
	context_label.text = context_text if not context_text.is_empty() else str(data.get("context", ""))
	WatchUI.clear(food)
	for summary in data.get("food", []):
		WatchUI.component("upkeep_summary", food).set_data(summary)
	reward_heading.text = str(data.get("reward_heading", "Shared-clear reward"))
	reward.text = str(data.get("reward", "No completed clear receipt."))
	roster.set_data(data.get("roster", {}))
	allocation_heading.text = str(data.get("allocation_heading", "Enemy allocation"))
	allocation.text = str(data.get("allocation", ""))
func set_context(state: String) -> void:
	context_title = "City details · P2 inspection" if state == "foreign" else "City details · P1"
	context_text = "Read-only inspection · " + state + " · city 100/100 · army 18" if state not in ["building", "preparation", "shortage"] else ""
	set_data(data)
