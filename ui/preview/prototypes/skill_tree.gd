extends VBoxContainer
# Authoring host only: illustrative effects, not authoritative game skills.
var tree: Control
func _ready() -> void:
	WatchUI.label(self, "Mini skill tree · illustrative allocation", "HeadingLabel")
	var reset = WatchUI.button(self, "Reset demo · 6 points")
	reset.pressed.connect(func(): tree.set_data(UIFixtures.skill_tree()))
	tree = WatchUI.component("skill_tree", self)
	tree.set_data(UIFixtures.skill_tree())
