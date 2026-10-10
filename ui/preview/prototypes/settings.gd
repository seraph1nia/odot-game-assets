extends VBoxContainer
signal changed(key: String, value: Variant)
signal return_requested()
var volume: HSlider
var display_mode: OptionButton
var resolution: OptionButton
var update_status: Label
var update_sample = 0
func _ready() -> void:
	var tabs = TabContainer.new()
	tabs.name = "Categories"
	tabs.custom_minimum_size.y = 240
	add_child(tabs)
	var graphics = page(tabs, "Graphics")
	WatchUI.label(graphics, "Display mode")
	display_mode = OptionButton.new()
	display_mode.name = "DisplayMode"
	display_mode.add_item("Windowed")
	display_mode.add_item("Fullscreen")
	graphics.add_child(display_mode)
	display_mode.item_selected.connect(func(index): resolution.disabled = index == 1; changed.emit("display_mode", index))
	WatchUI.label(graphics, "Windowed resolution")
	resolution = OptionButton.new()
	resolution.name = "Resolution"
	for size in ["1100 × 820", "1280 × 720", "1600 × 900", "1920 × 1080"]: resolution.add_item(size)
	graphics.add_child(resolution)
	resolution.item_selected.connect(func(index): changed.emit("resolution", resolution.get_item_text(index)))
	WatchUI.label(graphics, "Fullscreen uses monitor native size; choices here are mock data.", "ContextLabel")
	var audio = page(tabs, "Audio")
	var amount = WatchUI.label(audio, "Master volume: 50")
	volume = HSlider.new()
	volume.name = "MasterVolume"
	volume.min_value = 0
	volume.max_value = 100
	volume.value = 50
	volume.custom_minimum_size.y = 36
	audio.add_child(volume)
	volume.value_changed.connect(func(value): amount.text = "Master volume: " + str(int(value)); changed.emit("master_volume", int(value)))
	WatchUI.label(audio, "0 mutes all audio. Music keeps playing while muted.", "ContextLabel")
	var about = page(tabs, "About")
	WatchUI.label(about, "Version: development preview")
	var feedback = OptionButton.new()
	feedback.name = "UpdateSample"
	for text in ["Development", "Checking", "Up to date", "Update available", "Check failed", "Save failed"]: feedback.add_item(text)
	about.add_child(feedback)
	feedback.item_selected.connect(func(index): update_sample = index; show_update())
	update_status = WatchUI.label(about, "", "ContextLabel")
	update_status.name = "UpdateFeedback"
	var check = WatchUI.button(about, "Check for updates (mock)")
	check.name = "CheckUpdates"
	check.pressed.connect(show_update)
	show_update()
	WatchUI.button(self, "Return to menu").pressed.connect(func(): return_requested.emit())
	WatchUI.label(self, "Settings blocks local world input, not the shared match.\nMock values only; no display, audio or preference changes.", "ContextLabel")
func show_update() -> void:
	update_status.text = ["Development builds do not compare against published releases.", "Mock checking… no HTTP request made.", "Mock result: up to date.", "Mock update available. Installation remains game-owned; nothing downloaded.", "Mock check failed. Retry is available; no HTTP request made.", "Mock settings save failed. No real preferences were written."][update_sample]

func page(tabs: TabContainer, title: String) -> VBoxContainer:
	var margin = MarginContainer.new()
	margin.name = title
	for side in ["left", "top", "right", "bottom"]: margin.add_theme_constant_override("margin_"+side, 12)
	tabs.add_child(margin)
	return WatchUI.stack(margin)
