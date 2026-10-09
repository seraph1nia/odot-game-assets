extends SceneTree
# Image content check without Pillow or graphical display dependencies.
func _initialize() -> void:
	for direction in ["ledger", "watch"]:
		var image := Image.load_from_file(ProjectSettings.globalize_path("res://art/explorations/" + direction + "_seal.png"))
		if image == null or image.get_size() != Vector2i(192, 192) or image.detect_alpha() == Image.ALPHA_NONE:
			push_error("Invalid seal dimensions/alpha: " + direction)
			quit(1)
			return
		if image.get_pixel(0, 0).a != 0.0 or image.get_pixel(96, 96).a < 0.99:
			push_error("Seal lacks transparent border / opaque center: " + direction)
			quit(1)
			return
	print("UI_IMAGE_CHECK passed: 2 transparent RGBA seals, 192px, opaque centers")
	quit()
