# Blockout and substantial construction

Use for unclear role/silhouette or thin/generic construction.
Primary visual owner: [D01](../design/silhouette.md#d01).
Pipeline owners: [geometry.py](../../../../tools/asset_pack/geometry.py),
[build_pack.py](../../../../tools/asset_pack/build_pack.py) and
[catalog selection](../../../../catalog/SCHEMA.md).
For edge treatment alone use [normals](normals.md), not another blockout.

## Inputs and preconditions

Selected canonical ID, [reference/crop](../references/index.md), relevant
[family](../families/index.md), change hypothesis and view profile. Source edit
and any build/render/export must be explicitly authorized. Preserve .blend/maps
and dependency baselines first; builders overwrite. If the feature is shared,
read [library ownership](libraries.md) before changing geometry.

## Procedure

1. Separate model/export collection, equipment (units), display terrain,
   atmosphere and studio. Keep the existing ground-zero root and forward
   convention; do not select all scene objects as a shortcut. Confirm actual
   source/selector through metadata before editing.
2. State the primary mass and role cue, e.g. B1 cottage+raised lookout+target.
   Open the picture itself and annotate comparable silhouette landmarks in notes.
   Separate body/structure from base, plume/weapon/trees when comparing ratios.
   Use occupied-height normalization rather than matching reference pixels blindly.
3. Block only dominant masses with `g.cube`, `g.lathe`, `g.mesh`, `g.beam` or
   `g.tube`. Check negative space between the role cue and supporting mass from
   the intended elevated view and an opposing view. Do not begin with bolts/grain.
4. For buildings use the existing family builder's architectural helpers; place
   coherent courses, strong posts/braces, overhanging layered roof and recessed
   door/window framing. Reuse village shingles/stone/props via `kit.place()`.
   Adjust relative mass/placement rather than shrinking every cue to make room
   for more dressing. For units, joint/body changes route to [rigs](units.md).
5. Reserve role objects and paths; place secondary props only after the primary
   silhouette reads. Keep larger joints/steps/shingle thickness geometric; route
   fine grain/scratches to [UV/maps](uv-maps.md). Display trees/fences may support
   a building preview but need not travel in its GLB.
6. Apply only selected edge treatment under [normals](normals.md); settings come
   from `art_style.GEOMETRY`, not hard-coded copied bevel values. Check how instance
   scale changes apparent edge width. Do not apply transforms indiscriminately
   to shared prototypes/attached props to “fix” appearance.
7. Compare full and target/provisional small silhouettes and lit views using
   [review scenes](review-scenes.md); record which D01 cue improved. Check origin,
   finite bounds and selection through [export/checks](export.md) when authorized.

## Output and failure handling

Output is an editable source retaining export/presentation separation and a
clearer predeclared role cue, with matched evidence—not more objects by default.
If the cue still merges at small size, revisit mass/negative space before detail.
If proportions require a shared/global change, stop at dependency/scope review,
not an unmarked private prototype copy or all-library rebuild.

One reference view cannot determine hidden/back surfaces or exact scale ratios.
Document coherent authored reconstruction choices and uncertainty. No blockout,
source overwrite, render or quality loop is authorized by this recipe itself.
