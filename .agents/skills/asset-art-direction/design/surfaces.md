<a id="d04"></a>
# D04 — Material and painted-surface hierarchy

## Evidence and observation

[IDs](../references/index.md) A7/B1/F3 show broad color washes, restrained
longitudinal timber grain and delicate stone marks, alongside substantial real
joints. [C-WOOD and C-ROOF](../references/evidence.md#crops) distinguish quiet
surface treatment from geometry that contributes thickness/separation. Enemy
metal/cloth also retain broad planes rather than realistic grunge everywhere.

## Standard and rationale

Use geometry for silhouette, broad seams, layered shingles and major joints.
Fine grain, delicate cracks/veins, shallow wear and related washes belong in
portable maps. Maintain readable stylized material differences; fine texture
must remain subordinate to role, structure and broad planes.
This keeps painted depth portable without accumulating tiny decorative geometry.

## Scope and exceptions

Painted buildings/forest/props. Existing older unit surfaces are not automatically
required to acquire texture maps: migration is separate work. Essential raised
insignia, large pegs and real shingle overlap can stay geometric. A marked larger
joint is not “fine detail” merely because it is a repeated kit part.

## Qualitative examples

- **Pass anchor:** A7 table grain follows plank length; F3 restrained stone
  variation supports steps and monolith faces.
- **Fail criterion:** raised crack tubes across every stone, crosswise grain,
  high-frequency grunge hiding a sign, or procedural shaders losing appearance
  when exported to GLB.
- Inspect normal depth in glancing light and small-view stability. A channel's
  presence passes a mechanical contract, not the visual noise/softness criterion.

## Uncertainty and calibration

Stills cannot reveal UVs, roughness or normal amplitude. No poly/texture budget or
shader numeric target is extracted. Existing `TEXTURES`, material family and
normal-family settings live in
[art_style.py](../../../../tools/asset_pack/art_style.py). Compare matched material
patches and portable GLB channels before proposing changes. Preserve manually
painted maps; repeated generator calls do not guarantee freshness.

How: [UV/maps and bake exceptions](../blender/uv-maps.md),
[materials/color](../blender/materials.md). Existing map implementation:
[painted_finish.py](../../../../tools/asset_pack/painted_finish.py).
