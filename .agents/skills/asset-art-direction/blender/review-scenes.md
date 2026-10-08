# Comparable review scenes and deterministic evidence

Use to compare appearance without mistaking framing/light changes for art gain.
Primary visual owner: [D08](../design/presentation.md#d08), including provisional
inspection tiers. Pipeline owners: [geometry.studio](../../../../tools/asset_pack/geometry.py),
[style_blender.preview](../../../../tools/asset_pack/style_blender.py),
[render_previews.py](../../../../tools/asset_pack/render_previews.py) and
[catalog render_blender.py](../../../../tools/asset_catalog/render_blender.py).

## Preconditions

Selected ID/reference, baseline hashes, pose/frame and chosen profile; rendering,
source edits and calibration fixtures must be explicitly authorized. Guidance
review can inspect existing images only. Preserve source/previews before any
command overwrites outputs. Missing actual game view sizes remain a limitation.

## Profiles and procedure

1. **Authored source art:** use `geometry.studio(target_z,scale)` when authoring
   a scene; it creates an orthographic camera, separate studio collection and
   shared Area lights, then calls `style_blender.preview(scene)`. Settings are
   `PREVIEW`, `LIGHTS` and `UNITS` in
   [art_style.py](../../../../tools/asset_pack/art_style.py). Record actual camera
   location/target/ortho scale, pose/frame, occupied pixel height, world/light settings,
   exposure/view transform/look and bloom state. Don't copy this leaf's own preset.
2. `style_blender.preview()` is idempotent for its lighting/compositor setup, but
   a source must contain the appropriate lights. It uses current
   `scene.compositing_node_group`/Glare inputs and AgX settings; don't promise
   older Blender compatibility. Existing custom compositor without a Glare node
   raises an error; preserve authored work instead of deleting it blindly.
3. **Saved source baseline:** `render_previews.py` opens existing scenes, bounds
   CPU threads and renders without saving sources. It does **not** restyle them.
   Older units/libraries retain saved presentation and are intentionally exempt
   from new individual painted-asset preview audits. Record actual saved settings;
   a differently lit before image is diagnostic, not a matched acceptance baseline.
4. **Portable GLB/catalog:** `render_blender.py` imports GLB, frames bounds using
   a radius-fit orthographic camera and three SUN lights, rendering CPU thumbnails.
   It does not open/save .blend sources. This is a separate profile from the authored
   Area-light studio: preserve its purpose, don't silently force profile identity.
   Use catalog thumbnail selection for isolated component previews; saved-source
   selection is documented in [README](../../../../README.md#asset-development-checks).
5. **Target view:** use approved actual camera/elevation/occupied-pixel evidence
   when available. D08's provisional image boxes are diagnostics only; record
   image dimensions and occupied size separately. Never modify/run another worker's
   game scene or engine just to claim real-view coverage. If unavailable, label
   that limit and review source/portable/provisional views honestly.
6. Compare before/reference/after with normalized framing and matched source/after
   profile/pose. Reference lighting is unknown; compare structural/color relationships
   rather than asserting precise albedo identity. Add silhouette/grayscale/glow-off
   companions only for relevant changed rules. Closeups diagnose; small views accept.

## Reproducibility, cost and failure handling

Record runtime version/build hash, source/GLB/map/style/kit hashes, scene profile
and output hash in [acceptance evidence](../review/acceptance.md). `clear_scene()`
resets the geometry RNG; field sampling is deterministic. This does not promise
byte-identical .blend files or denoised renders across machines. Hash immutable
files, tolerance-compare geometry/pose where appropriate, visually review balance.

Bound rendering through the existing worker/preset; no new orchestrator or global
sample/light escalation. If the source has no camera, mismatched pose or old preset,
report it and scope a comparison setup before scoring improvement. A preview file
with no demonstrated source/profile freshness is not new validation evidence.
Fog Glow is scene-only; portable emission needs a renderer effect for halos.
No native performance or animation appeal result follows from these stills.
