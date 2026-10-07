# Selective bevels, normals and topology

Use for razor edges, bulging face shading, lost facets or organic smoothing.
Primary visual owner: [D02](../design/shape-edges.md#d02).
Pipeline owners: [style_blender.py](../../../../tools/asset_pack/style_blender.py),
[geometry.mesh](../../../../tools/asset_pack/geometry.py) and
[style_validation.py](../../../../tools/asset_pack/style_validation.py).

## Preconditions

Identify material/shape, actual prototype scale and target view. Source/modifier
edits need authorization and preserved source; a shared mushroom/stone change
first needs [library ownership](libraries.md). Current selective organic softness
is the baseline adaptation; do not restore universal faceting by weakening tests.

## Procedure

1. Diagnose silhouette versus surface normals under a neutral/glancing light.
   In Blender inspect face orientation/normals and object scale; distinguish a
   topology problem from accidental smooth flags, bevel shading or strong normal
   texture. Check a glow-off view for crystals.
2. Keep broad crystal/armor/blade planes flat/readable. `forest_kit.crystal()`
   deliberately assigns face colors and flat normals. A Normal Map should not
   be used to round every crystal facet; inspect UV/highlight placement as well.
3. For stone, reuse `style_blender.stone_edges(obj)`: selective angle-limited
   Bevel, hardened bevel normals, then Weighted Normal with `keep_sharp`.
   Width/angle/segments are owned by `art_style.GEOMETRY`. Verify modifier order
   and actual settings: helper idempotence checks presence by type and does not
   repair an existing incompatible modifier's settings automatically.
4. For timber/large construction joints, `g.mesh()`/`g.cube()` add the shared
   selective bevel. Don't inflate wall panels or add bevels to all detail meshes.
   Check apparent edge width at final scale; object nonuniform scale can change
   it. Do not duplicate mesh data or apply bone/instance transforms blindly.
5. For mushrooms use the existing cap/stem construction and
   `style_blender.smooth_sides()` **only on suitable topology**: it smooths quad
   faces and leaves other faces flat, not semantic “side” detection on any mesh.
   `forest_kit.leaves()` authors its own smooth flags and root-tip UVs.
   Skin/gloves are selectively rounded by unit helpers; stone is not skin.
6. Preserve sufficient rings/planes for curved silhouettes, large seams and
   joints. Do not impose all-quads on flat crystals or dense triangles on every
   organic surface. Fix accidental winding/degenerate geometry; support deforming
   joints only with authorized weighting/pose tests in [units](units.md).
7. Inspect exported/reimported normals/plane gradients in matched views after
   an authorized selected export. Run applicable source-style/round-trip checks
   via [pipeline](../pipeline/index.md#checks); artist review still judges softness.

## Output, failures and version limits

Expected: readable broad planes with selective light-catching boundaries,
curved organic silhouette where intended, no blanket subdivision/Shade Smooth.
A mechanical “some faces smooth” check does not certify attractive normal flow.
If a broad stone face gradients unexpectedly, inspect smooth flags/Weighted Normal/
hard edges before increasing bevel geometry. If the cap loses identity, compare
broad form/painted planes rather than introducing dense faceted noise.

Use the existing pinned Blender contract. Modifier/export behavior must be
verified when changing runtime; this is not generic cross-version certification.
Do not manually apply an armature modifier as part of normal cleanup or export.
