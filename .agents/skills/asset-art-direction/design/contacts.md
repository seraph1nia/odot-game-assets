<a id="d05"></a>
# D05 — Contacts, vegetation and detail density

## Evidence and observation

[IDs](../references/index.md) F1/F3/F5/F8 and V1–V4 attach rocks/roots/moss/ivy
to structural contacts. Leaf groups overlap, vary in shape/scale and climb
surfaces; dark roots support brighter tips. F8 retains an approach to its altar.
[C-CONTACT](../references/evidence.md#crops) shows planted clusters and open space,
not a uniformly decorated six-sided border.

## Standard and rationale

Cluster secondary detail around meaningful contacts and role/story areas; vary
scale, rotation, curvature and overlap. Preserve rest areas and negative space.
Paint feathered contact darkening and local colored bounce on receiving surfaces,
not floating hard disks. Contacts make the miniature feel planted; uncontrolled
repetition makes it busy and procedural.

## Scope and exceptions

Terrain-bearing tiles; building display dressing; props only when their export
scope owns a receiver. Buildings/units omit display terrain from portable exports,
so do not require its bounce/shadow to travel inside their GLB. A footprint/grid
contract still limits a tile even if a plant overhang would look attractive.

## Qualitative examples

- **Pass anchor:** F8's open path with growth near stone supports; F3 ivy/steps
  integrate the central rune mass.
- **Fail criterion:** evenly spaced tufts on every edge, detached black/cyan disks,
  hovering rocks, or plants obscuring the role sign/bridge aperture.
- Evaluate a small view for hierarchy and a close view for actual contact; density
  alone is not a quality score. Keep purposeful quiet ground when reducing noise.

## Uncertainty and calibration

No universal tuft count or surface-coverage percentage follows from these stills.
Annotate focal/contact/quiet regions and compare negative space at matched views.
Current contact/bounce parameters live in `TEXTURES` in
[art_style.py](../../../../tools/asset_pack/art_style.py); the actual receiver/tag
limitations belong to [painted_finish.ground](../../../../tools/asset_pack/painted_finish.py).
It is not an arbitrary architectural occlusion bake.

How: [contacts procedure](../blender/contacts.md),
[library ownership](../blender/libraries.md). Mechanical footprint/freshness:
[pipeline checks](../pipeline/index.md#checks).
