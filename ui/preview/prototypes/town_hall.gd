extends VBoxContainer
signal requested(action_id: String)
var roster: Control
var card: Control
var healing: Control
func _ready() -> void:
	WatchUI.label(self, "Town hall · Plot 4", "HeadingLabel")
	WatchUI.label(self, "Storage and healing are independent tracks. Reserve tiles are not battlefield homes.", "ContextLabel")
	var tracks = WatchUI.row(self)
	var storage = WatchUI.component("quoted_action", tracks)
	storage.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	storage.set_data({"id":"storage-upgrade", "title":"Storage III · maximum", "quote":"18 size points · 3 separate reserve tiles", "enabled":false, "reason":"Maximum storage level reached."})
	healing = WatchUI.component("quoted_action", tracks)
	healing.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	healing.set_data({"id":"healing-upgrade", "title":"Healing I → II", "quote":"6 gold · 2 wood · 2 stone\n5% → 10% maximum HP/production", "enabled":true, "reason":"Only stored living units funded in the last completed battle recover."})
	healing.requested.connect(func(id): requested.emit(id))
	var body = WatchUI.row(self, 12)
	roster = WatchUI.component("army_roster", body)
	roster.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	roster.set_data(UIFixtures.roster(true))
	card = WatchUI.component("unit_inspection", body)
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.set_data(UIFixtures.unit(true))
	roster.unit_selected.connect(func(id):
		var data = UIFixtures.unit(true)
		data.id = id
		card.set_data(data))
	card.requested.connect(func(id, _unit, _destination): requested.emit(id))

func set_read_only(reason: String) -> void:
	var quote = healing.data.duplicate(true)
	quote.enabled = false
	quote.reason = reason
	healing.set_data(quote)
	var unit = card.data.duplicate(true)
	unit.can_retire = false
	unit.can_send = false
	unit.reason = reason
	card.set_data(unit)
	# Selection is still inspection, so roster buttons stay enabled.
	roster.unit_selected.connect(func(_id):
		var selected = card.data.duplicate(true)
		selected.can_retire = false
		selected.can_send = false
		selected.reason = reason
		card.set_data(selected))
