# Odot Ground / Water POC texture files

**Downloadable texture inputs, not a completed game asset import.** This pack follows existing Odot `ground_tiles.py` contracts and preserves every mesh/animation.

## Included

24 individually named 1024x1024 PNG maps: Base Color, Roughness and Normal for `moss`, `grass`, `dirt`, `leaf_litter`, `pine_duff`, `foundation`, `path`, `river`. Plus source art sheets, a contact sheet, a river bank mask and JSON/agent handoff. The material image swatches are **only ~135–171px natively**, enlarged as working texture inputs; this POC tests the pipeline, not final 1K texture fidelity. Color-derived normal/roughness are conservative estimates and optional.

## Material binding

* Five floor assets: `environment/hex_ground_<family>.glb`, bind `floor_<family>`.
* All base sidewalls and bottoms: bind `floor_foundation` with `foundation` maps.
* Path overlays: `environment/hex_path_{straight,turn_60,turn_120,end}.glb`, bind `floor_path`.
* River overlays: `environment/hex_river_overlay_{straight,turn_60,turn_120,end}.glb`, bind `floor_river`.
* Existing UVs remain unchanged. Hex radius=2.55, top Z=0, bottom Z=-0.36. Ribbon U goes **across**; V goes **along**. River water occupies U=[0.09375,0.90625], banks the remaining edges. Preserve ambient animation and path/river elevation.
* `*_basecolor.png` is `sRGB`, `*_roughness.png` and `*_normal.png` are `Non-Color`; normal via tangent-space Normal Map node. Keep metalness 0 and game-specific opacity/render settings.

## Important caveats

Blending 5 different materials across adjacent hexes may show hard boundaries despite each texture's outer edges matching. Avoid changing hex geometry or connector interfaces as a workaround. The river texture follows UV bank profile, but must be tested on turns, straights and endpoints and against real Godot lighting. Source builder `ground_tiles.py` **rewrites Blender sources**; do not run it to install maps. Use texture relinking in an isolated Blender source copy, followed by the selected-source export and existing checks.
