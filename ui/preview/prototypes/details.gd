extends VBoxContainer
signal unit_selected(unit_id: int)
func _ready() -> void:
	WatchUI.label(self, "City details · P1", "HeadingLabel")
	WatchUI.label(self, "Connected · owner · city 100/100 · army 18\nYou may edit only while unpaused, unready Building/Preparation.")
	var food = WatchUI.component("upkeep_summary", self)
	food.set_data({"heading":"Upkeep · Next battle", "rows":[{"label":"Food demand", "value":"18"}, {"label":"Projected payment", "value":"1 food"}, {"label":"Food after payment", "value":"0"}], "detail":"17 field soldiers will sit out. Shortage does not disable Ready."})
	WatchUI.label(self, "Last shared-clear reward · W1", "HeadingLabel")
	WatchUI.label(self, "2 gold · 5 food · 1 wood · 1 research point\nProjected snapshot text; no reward/payment logic in UI.", "ContextLabel")
	var roster = WatchUI.component("army_roster", self)
	roster.set_data(UIFixtures.roster())
	roster.unit_selected.connect(func(id): unit_selected.emit(id))
	WatchUI.label(self, "Enemy allocation", "HeadingLabel")
	WatchUI.label(self, "Boneguard II ×3 · deployed\nHooded crossbowman II ×2 · queued\nQueued status: ● Poison ×1 · strength 2 · 3.0 simulated seconds")
