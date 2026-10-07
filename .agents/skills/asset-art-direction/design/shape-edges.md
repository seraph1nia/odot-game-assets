<a id="d02"></a>
# D02 — Shape and edge language

## Evidence and observation

[IDs](../references/index.md) A2/A7/B1 have broad timber/stone planes and
light-catching chamfer-like edges. A3's beard/axes, E1's armor/skull and F1's
crystals remain angular. [C-JOINT, C-ROOF and C-CAP](../references/evidence.md#crops)
show the distinction: F4/F6 caps visibly contain facets. Universally smooth caps
are **not** an observed convention of these pictures.

## Standard and rationale

Retain chunky silhouettes and broad planes. Soften selected construction edges
just enough to catch light; preserve crystal, blade and armor faces. Curved
organic silhouettes and selective normals are preferable to uniform subdivision
or dense noisy facets. Softness comes from edge/light/material hierarchy, not
rounding everything.

**Chosen adaptation:** preserve the project's current selective smoothing for
skin/gloves, mushroom cap/stem sides and leaves while retaining broad form and
restrained painted variation. Explain that as an adaptation from reference
faceting, not an exact copy. Do not reverse existing normal tests to make a new
faceted experiment pass. Stronger organic faceting needs a separately accepted
comparison and scoped contract change.

## Scope and exceptions

Architecture, stone, cloth/armor, foliage and magical forms. Intentional crystal
faces and blade/armor facets stay sharp. Rounded skin/caps differ from broad
planar stone; this rule is not blanket Shade Smooth or a universal bevel.

## Qualitative examples

- **Pass anchor:** A2's stone courses remain distinct with softened corners;
  F1's colored crystal faces remain distinct around narrow highlights.
- **Fail criterion:** inflated pillow-like masonry, perfectly razor-sharp timber
  everywhere, smooth glass crystals with lost face hierarchy, or micro-facet noise
  over every mushroom face.
- Inspect silhouette and face shading separately: good silhouette alone does not
  justify a shading gradient that erases a broad stone plane.

## Uncertainty and calibration

Pictures do not reveal bevel widths, segments, face normals or topology.
Existing settings are facts owned by `GEOMETRY` in
[art_style.py](../../../../tools/asset_pack/art_style.py), not picture measurements.
Do not copy tunables into this leaf. A later authorized edge/normal ladder should
compare the real prototype scale and target view before any metric is revised.

How: [normals/topology](../blender/normals.md),
[construction](../blender/construction.md). Existing normal-treatment owner:
[style_blender.py](../../../../tools/asset_pack/style_blender.py).
