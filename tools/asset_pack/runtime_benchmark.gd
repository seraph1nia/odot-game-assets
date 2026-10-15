extends SceneTree
## Isolated, headless imported PackedScene measurement. No game code or renderer.

func meshes_in(node: Node) -> Array[MeshInstance3D]:
	var result: Array[MeshInstance3D] = []
	if node is MeshInstance3D:
		result.append(node)
	for child in node.get_children():
		result.append_array(meshes_in(child))
	return result

func count_nodes(node: Node) -> int:
	var result := 1
	for child in node.get_children():
		result += count_nodes(child)
	return result

func measure(path: String) -> Dictionary:
	var start := Time.get_ticks_usec()
	var scene := load(path) as PackedScene
	assert(scene != null, path)
	var load_us := Time.get_ticks_usec() - start
	var samples: Array[int] = []
	var result := {"path": path, "load_us": load_us}
	for trial in range(12):
		start = Time.get_ticks_usec()
		var instance := scene.instantiate()
		var elapsed := Time.get_ticks_usec() - start
		if trial > 0:
			samples.append(elapsed)
		if trial == 0:
			get_root().add_child(instance)
			var meshes := meshes_in(instance)
			var surfaces := 0
			var triangles := 0
			for mesh in meshes:
				surfaces += mesh.mesh.get_surface_count()
				for surface in range(mesh.mesh.get_surface_count()):
					var arrays := mesh.mesh.surface_get_arrays(surface)
					triangles += (arrays[Mesh.ARRAY_INDEX].size() if arrays[Mesh.ARRAY_INDEX] != null else arrays[Mesh.ARRAY_VERTEX].size()) / 3
			result.merge({"nodes": count_nodes(instance), "mesh_nodes": meshes.size(), "surfaces": surfaces, "triangles": triangles})
			var players := instance.find_children("*", "AnimationPlayer", true, false)
			assert(players.size() == 1, path + ": one animation player required")
			var player := players[0] as AnimationPlayer
			assert(player.has_animation("ambient"), path + ": ambient missing")
			var animation := player.get_animation("ambient")
			for track in range(animation.get_track_count()):
				assert(player.get_node(player.root_node).get_node_or_null(animation.track_get_path(track)) != null, "unresolved animated target")
			var initial: Array[Transform3D] = []
			var changed: Array[bool] = []
			player.play("ambient"); player.seek(0, true)
			for mesh in meshes:
				initial.append(mesh.global_transform)
				changed.append(false)
			for fraction in [0.25, 0.5, 0.75]:
				player.seek(animation.length * fraction, true)
				for i in range(meshes.size()):
					changed[i] = changed[i] or not meshes[i].global_transform.is_equal_approx(initial[i])
			player.seek(animation.length, true)
			var moving := 0
			for i in range(meshes.size()):
				assert(meshes[i].global_transform.is_equal_approx(initial[i]), path + ": loop endpoints differ")
				moving += int(changed[i])
			assert(moving > 0 and moving <= meshes.size(), path + ": no ambient mesh motion")
			result.merge({"ambient_length": animation.length, "ambient_tracks": animation.get_track_count(),
				"imported_loop_mode": animation.loop_mode, "moving_meshes": moving, "fixed_meshes": meshes.size() - moving,
				"loop_endpoints_equal": true, "all_track_targets_resolve": true})
		instance.free()
	samples.sort()
	result.merge({"instantiate_us": samples, "median_instantiate_us": samples[5], "min_instantiate_us": samples[0], "max_instantiate_us": samples[10]})
	return result

func _initialize() -> void:
	# SceneTree root has not entered the tree during _initialize. Exercise
	# global animated transforms only after the root is actually live.
	call_deferred("_run")

func _run() -> void:
	var file := FileAccess.open("res://selection.json", FileAccess.READ)
	var selection: Array = JSON.parse_string(file.get_as_text())
	var results: Array = []
	for path in selection:
		results.append(measure(path))
		print("Measured headless PackedScene: ", path)
	var output := FileAccess.open("res://results.json", FileAccess.WRITE)
	output.store_string(JSON.stringify({"engine": Engine.get_version_info(), "samples": results,
		"scope": "One fresh headless process after editor import. First ResourceLoader load (OS cache not flushed); 1 unmeasured instantiation then 11 warm trials, immediate free. Instantiate only; excludes add_child/render/physics and import time. No FPS/GPU acceptance."}, "\t"))
	quit()
