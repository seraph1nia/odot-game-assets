# Buildings: role signatures and export scope

Use for village/economy/defense/civic models. Resolve the selected ID in
[references](../references/index.md), then read
[construction/blockout](../blender/construction.md) and its primary
[D01](../design/silhouette.md#d01). Other rules apply as relevant, not read-all.

## Role-specific cues and exceptions

These qualify common silhouette/palette/construction rules, not new thresholds.

| References | Signature to protect |
|---|---|
| V1 | Tree canopy/trunk, raised room/platform/stairs; tree-led D01 exception |
| V2 | Bread sign/display, recessed bakery opening; red-roof D03 exception |
| V3/V4 | Mine entrance/cart/ore versus wood stack/chopping/stumps |
| A1/A4 | Tall open lookout/arrows versus hollow cannon/battlements/ammunition |
| A2 | Sword/shield insignia, substantial entrance, spear rack |
| A5 | Crystal spire/orb, arcane symbols and books; localized D06 magic |
| A6/A7/A8 | Crane/grinding stone versus mug sign/table versus striped market/scale |
| B1/B2 | Lookout/target/bow emblem versus observatory dome/telescope/armillary |
| B3/B4/B5 | Ore outcrop/hoist/cart versus loom/canopy/cloth versus civic wings/bell/shield |

Don't turn every role into a cottage plus tiny attachments. Protect different
masses and the main sign before adding detail. Shared construction/palette follows
[D02](../design/shape-edges.md#d02)/[D03](../design/palette.md#d03); no independent
roof swatch or bevel table belongs here.

## Actual authoring owners

- Original four: [buildings.py](../../../../tools/asset_pack/buildings.py).
- Seven added defense/workshop buildings:
  [autobattler_buildings.py](../../../../tools/asset_pack/autobattler_buildings.py).
- Five added buildings: [more_buildings.py](../../../../tools/asset_pack/more_buildings.py),
  with [reference_finish.building_finish](../../../../tools/asset_pack/reference_finish.py)
  and [painted maps](../blender/uv-maps.md).
- Repeated shingles/props/stone: [village kit](../blender/libraries.md).
  Some tiny grain/scratch/seam geometry remains in `building_finish`; do not
  assume applying maps removed it. A later authorized refinement may replace only
  subordinate marks, preserving major joints/insignia.

## Export and review

Building root remains ground-zero and faces source −Y. Display terrain, atmosphere
and studio stay separate; the exported building does not automatically carry their
contact shading/trees/smoke. See [export selection](../blender/export.md), not an
instruction to merge all presentation collections. Foliage intrinsic to a tree
house remains part of that building's authored role.

Review full and provisional/actual target views under [matched profiles](../blender/review-scenes.md).
Painted newer sources and older saved previews may differ in lighting/settings;
compare normalized silhouette before attributing color differences to a model.
Existing 11-building refinement history does not certify current 16-building
acceptance. No rebuild/pilot is authorized by this family route.
