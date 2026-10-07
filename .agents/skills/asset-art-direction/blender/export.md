# Source/export compatibility and selected verification

Use before exporting/checking a refined source or interpreting portable differences.
Primary visual owner: [D09](../design/evidence-cost.md#d09).
Pipeline owners: [catalog schema](../../../../catalog/SCHEMA.md),
[blender_selection.load_asset](../../../../tools/asset_catalog/blender_selection.py),
[export_blender.py](../../../../tools/asset_catalog/export_blender.py),
[check.py](../../../../tools/asset_pack/check.py) and
[verify_pack.py](../../../../tools/asset_pack/verify_pack.py).

## Preconditions

Canonical selected IDs, preserved authored sources/manual maps, selector metadata,
authorized export scope and actual runtime. Export writes GLBs/manifest/index;
`asset-check` may export/write validation/cache. Neither is pure read-only even
though it does not rebuild/save .blend sources. Use
[command/side-effect selection](../pipeline/index.md#checks).

## Procedure

1. Resolve `sources/<ID>.blend` or explicit shared `source` and mutually exclusive
   `export_collection`/`export_object` via metadata. Default is collection/root
   matching ID stem; root-level overview sources aren't batch exports. Do not
   hand-edit generated catalog index or guess source from a similar filename.
2. Confirm selected source objects include intended descendants and unit
   `EQUIPMENT`, not studio/atmosphere/display terrain. Forest tile terrain is
   included; standalone display bases use explicit collection mappings. Review
   intrinsic building parts versus display-only dressing before selection.
3. Preserve root at ground zero/source Z-up and −Y forward. Props retain grip/
   placement origin and authored scale. GLB uses the exporter's Y-up conversion
   (project forward becomes +Z); don't manually pre-rotate and export again.
   Tile dimensions/neighbor spacing remain `art_style.HEX`, not this leaf's numbers.
4. Preserve Armature modifiers, weights and used non-deforming weapon sockets;
   anatomical bones remain deforming. The exporter uses selected objects, skins/
   actions/extras and `export_apply=True`, not a manual Apply All preparation step.
   Do not flatten rigs to resolve an export problem.
5. Use selected-source catalog export or incremental asset-check, not legacy
   `export_pack.py` for hand-edited work: that older path can regenerate standalone
   component sources. Current exporter stages a temporary GLB, reads its facts,
   atomically replaces output and updates manifest/index; no .blend save/render.
6. Verify source→reimported GLB finite bounds/materials, root placement, repeated
   mesh sharing and selected animation samples/loop endpoints. Bind validation
   records to current source/export hashes. A stale record or changed kit remains
   unaccepted even if an older verification says success.
7. Painted maps need separate source packing/UV/colorspace and embedded GLB channel
   audits; a materials-present round trip alone is not image coverage. Forest tiles
   need footprint/base/endpoints/library signatures too. Choose relevant
   [checks](../pipeline/index.md#checks), not an all-catalog campaign by default.
8. Compare portable appearance under matched profiles, record triangles/materials/
   image/byte deltas with the GLB hash and explain growth. `metadata.read_glb()`
   counts unique primitive totals, not repeated-instance cost or draw calls.

## Output and failures

Expected: portable asset with preserved editable source, correct selection/rig/
pivots/axes/maps, current hash-bound checks and honest visual/cost evidence.
An `asset-check` kit-change notice means embedded models need explicit source
propagation; export does not perform that rebuild. Read [libraries](libraries.md).
Unsupported nodes/UV/image losses route to [materials](materials.md)/[maps](uv-maps.md).
Bounded pose/bounds tests do not certify animation appeal or every vertex path.

On failure print one focused result and final worker log tail with full log path;
retain source and inspect actual error. Don't retry by saving a rebuilt source,
relaxing validators, running GUI Blender or changing runtime. Default/rig/game
migration is a separate approval, not automatic compatibility repair.
