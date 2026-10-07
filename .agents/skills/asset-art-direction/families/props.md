# Props and terrain: context and pivots

Use for standalone kit props, weapons and terrain bases. Resolve the canonical ID,
source and export selector through [reference metadata](../references/index.md).
Props take contextual style evidence from their containing image/crop; do not
invent supplied individual turnarounds. Primary visual owner:
[D01](../design/silhouette.md#d01); how: [construction](../blender/construction.md).

## Placement class before geometry

- Removable weapons: grip-local pivot and authored attachment scale; read
  [units/equipment](units.md) and [rig procedure](../blender/units.md).
- Ground props: intended contact pivot; preserve authored prototype placement.
- Forest components: collection-local placement conventions from
  [environment](environment.md); butterfly/moth flight pivots are not ground roots.
- Standalone display terrain: explicit `DISPLAY_TERRAIN` export selection in
  [associations](../../../../catalog/associations.json). Building/character display
  bases and grid forest tiles are different use cases; do not force one footprint
  onto every prop or character pedestal.

## Library and material exceptions

Repeated barrel/crate/shingle/lantern/skull/spike geometry belongs to the existing
[village/forest libraries](../blender/libraries.md); copies share mesh data.
Metal weapons preserve facets; organic scenery can smooth selectively under
[D02](../design/shape-edges.md#d02). Lantern emission is a localized D06 exception,
not a rule to add glow to all props. Fine marks follow
[D04](../design/surfaces.md#d04)/[UV maps](../blender/uv-maps.md); kit palette
variants stay with their existing code owner, not this leaf's new color table.

## Acceptance scope

Check functional silhouette at intended size, pivot/scale on placement, shared
mesh/material reuse and portable export channels. Tiny props may reduce to a
clear cue instead of retaining every book page/bolt. Resource count conventions
are owned by [D09](../design/evidence-cost.md#d09), not a blanket decimator.
Component previewing routes through catalog thumbnails or an explicitly authorized
review scene; `render_previews.py` only supports its catalog model/tile names.
See [export](../blender/export.md) and [checks](../pipeline/index.md#checks).
