<a id="d09"></a>
# D09 — Evidence and resource restraint

## Evidence and observation

[IDs B1/F3](../references/index.md) and
[C-ROOF/C-CONTACT](../references/evidence.md#crops) show substantial focal structure
with subordinate marks/clusters, supporting purposeful detail rather than object
count as a quality goal. Supplied pictures establish no polygon/draw-call/texture
budget. Current libraries reuse mesh data, while generated GLBs can contain many
material/image variants; portable maps and geometric detail both have costs.
A file's triangle count is not measured GPU time.

## Standard and rationale

Accepted refinement records rule-level benefit at target size, mechanical
correctness and resource deltas. Keep detail that contributes; don't grow map/
material complexity merely for closeups or reduce geometry indiscriminately.
Source fidelity, portable correctness and artist judgment are separate acceptance
dimensions. Preserve prototype sharing and manual source work.

## Scope and exceptions

All exported 3D families. Hero/focal assets may justify different resource
allocation, but there is no universal measured budget here. Until calibrated,
flag any increase in GLB bytes/images/materials/unique primitive triangle totals
for explanation, **not automatic rejection**. Family budgets require actual
consumer measurements and approval.

## Qualitative examples

- **Pass criterion:** subordinate grain moves from tubes into existing maps while
  large joints/identity survive, with current export evidence and small-view benefit.
- **Fail criterion:** blanket decimation flattening a hero silhouette, copying
  prototype meshes for every placement, or claiming fewer materials proves FPS gain.
- Compare benefits against unchanged-rule regressions; a mechanical pass cannot
  override lost visual hierarchy. Inspection counts must use a stated convention.

## Uncertainty and calibration

[Catalog metadata](../../../../tools/asset_catalog/metadata.py) counts unique mesh
primitive triangle totals and material definitions; instances, renderer batching,
compression/mips and scene composition alter runtime cost. Keep bytes/image/
material counts with the actual GLB hash. Native performance needs a controlled
consumer-renderer measurement under separate authorization, not a still or this
skill. No new metric/policy engine or blanket optimization pass is implied.

How: [export/check interpretation](../blender/export.md).
Evidence, regression and rollback procedure:
[acceptance](../review/acceptance.md).
