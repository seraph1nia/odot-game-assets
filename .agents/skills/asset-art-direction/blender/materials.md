# Materials and color management

Use for palette separation, unsupported nodes, double encoding or shader drift.
Primary visual owner: [D03](../design/palette.md#d03).
Pipeline owners: [geometry.material/palette](../../../../tools/asset_pack/geometry.py),
[reference_finish.palette](../../../../tools/asset_pack/reference_finish.py) and
[art_style.py](../../../../tools/asset_pack/art_style.py).
For UV/channel lifecycle use [maps](uv-maps.md), not a copied material generator.

## Preconditions

Resolve family/reference and determine existing base versus painted material
stage. Preserve manual materials/maps; material edits and preview/export work
need explicit scope. Establish one view profile before comparing surface color.

## Procedure

1. Inspect the active Material Output's Surface connection, not merely whether
   an unused Principled node exists. Native Principled BSDF must own the surface;
   portable channels should be image-linked rather than unexportable procedural
   networks. `style_validation._principled()` checks the connected shader.
2. Initialize palettes through `geometry.palette()` for the base family or
   `reference_finish.palette()` for the painted family. Create with
   `geometry.material(name,rgb,roughness,metal,emission)` instead of duplicating
   node-building code. Shared palette specs belong to `art_style`; kit-specific
   authored overrides belong to existing builders. Do not invent a new leaf palette.
3. Treat supplied `rgb` as sRGB: `geometry.material()` calls `srgb_to_linear`
   for Principled inputs/diffuse color. Don't pass already-linear sampled values
   through this interface again. When reading shader default values, they are
   linear; do not compare them directly to rendered screenshot pixels.
4. Preserve meaningful family names/`texture_family` metadata; suffix-normalizing
   `material_name()` handles appended `.001` variants. A new renamed material
   outside recognized families can skip painted-map requirements: a green check
   then is not proof it received intended surface treatment.
5. Inspect Base Color and Emission images as sRGB; Roughness/Normal as Non-Color.
   Use a tangent Normal Map node for shallow relief. See [UV/maps](uv-maps.md)
   for packing/encoding/refresh; don't run palette/apply over manually painted
   loaded sources expecting safe restyling.
6. In a matched studio compare support/body/role/accent relationships, grayscale,
   and bloom-off. Keep unit faction/role differences; don't apply forest/building
   palette globally to no-map units. V2 bakery red roof is deliberate.
7. After authorized export, verify connected material/UV/image channels and
   compare the portable profile, documenting differences from source AgX/light.
   Use [checks](../pipeline/index.md#checks) and [acceptance](../review/acceptance.md).

## Output and failures

Expected: native portable shader, preserved family relationships and one color
encoding path. If colors look washed out, inspect image colorspace and linear/
sRGB conversion before changing palette constants. If shader survives but material
looks wrong, distinguish pipeline coverage from visual balance. If linked images
remain stale, use map ownership/refresh decisions rather than more node duplicates.

Exact roughness/metallic/RGB values are existing code facts, not quantities
recoverable from reference pictures. Changing shared material settings requires
scoped calibration/dependency work; guidance alone changes none.
