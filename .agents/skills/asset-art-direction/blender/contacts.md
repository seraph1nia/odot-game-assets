# Planted contacts and detail allocation

Use for hovering rocks, detached growth, uniform borders or hard ground disks.
Primary visual owner: [D05](../design/contacts.md#d05).
Pipeline owners: [painted_finish.ground](../../../../tools/asset_pack/painted_finish.py),
[forest_tiles.py](../../../../tools/asset_pack/forest_tiles.py),
[enchanted_tiles.py](../../../../tools/asset_pack/enchanted_tiles.py) and
[forest grid verifier](../../../../tools/asset_pack/verify_forest_blender.py).

## Preconditions

Selected family/reference, export scope and receiver, composition/prototype
ownership, preserved source/maps and authorized edits. Read [libraries](libraries.md)
for shared shapes and [UV lifecycle](uv-maps.md) before generating receiver images.
Building display terrain is not part of its portable model by default.

## Procedure

1. Inspect reference focal/contact/quiet regions (F3 C-CONTACT, F8 approach).
   Locate actual mesh/ground contacts, not just object origins; retain useful
   paths/bridge apertures/sign visibility before placing more vegetation.
2. Use existing forest/village placements sharing mesh data. Vary group scale,
   rotation, silhouette curvature and overlaps instead of duplicating identical
   clumps evenly around edges. Grow roots/ivy/moss from contacts/supports;
   don't float leaf patches near a wall and rely on a shadow to connect them.
3. Correct large physical contact/embedding and footprint first. A receiver map
   cannot fix a visibly hovering rock or fill a silhouette gap. Preserve deliberate
   buried roots/rocks and the tile base/root conventions; don't move tile origin.
4. For recognized terrain receivers, call `painted_finish.ground(collection,name,
   category)` only after approved geometry/material placement and UV preparation.
   It updates the view layer, samples world XY, creates local ground color/emission
   images, copies the receiver material and assigns object-linked material slots.
   Tunable contact/bounce settings remain in `art_style.TEXTURES`.
5. Understand its limitations: receiver names must start with the implementation's
   meadow/bank prefixes; no receiver means an early return. Contacts require
   tagged `kit_asset` roots, a parent and low-Z placement, and only selected kind
   names produce fields. It is not a ray-traced bake or arbitrary wall/window
   bounce system. Inspect actual image/UV coverage; do not assume all architecture
   shadows were painted because the function returned successfully.
6. Check shared receiver mesh users before UV changes: `ground()` writes mesh UVs
   in world coordinates. A shifted/rotated shared receiver could affect other
   users. Preserve the grid base's identity transform and authorized scope; don't
   solve unique receiver variation by silently duplicating all prototypes.
7. Inspect feathering, plant attachment and negative space in full/small/glow-off
   views. No floating opaque black/cyan/amber disks should substitute for mapped
   receiving shade. Verify footprint/base/river/library signatures through
   [checks](../pipeline/index.md#checks) when approved; judge density visually.

## Output and failures

Expected: planted contacts, locally varied groups and preserved rest areas,
with receiver maps only where the source/export scope owns them.
If ground maps remain stale, see [map refresh](uv-maps.md); reusing existing image
names is not recalibration. If the base rotates/shifts to improve composition,
stop: move scenery, not shared grid geometry. If growth hides the cue, remove/
recompose subordinate clusters before adding texture contrast. No global tuft
count or occlusion strength is extracted from reference images.
