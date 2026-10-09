# Detailed forest-ground suite

## Delivery and authority

13 new canonical sources/GLBs: five bases, four independent dirt-path pieces and
four independent surface-river pieces. No existing terrain/library source or map
was rebuilt. Indexed art-direction guidance was extended **before authoring**, then
reloaded: [hex-ground recipe](../../.agents/skills/asset-art-direction/blender/hex-ground.md).
D03/D04/D05/D06/D08/D09 retain their existing owners; `art_style.GROUND` owns only
new-suite executable settings and palettes. Shared `HEX` defaults are unchanged.

F3 C-CONTACT and F5 C-WATER were inspected for related olive ground, attached leaf/
moss groups, clear approaches and blue water. There is no supplied picture of
these bare floors/connector pieces: these are **authored adaptations**, not a
reference-match or measured reference-pixel calibration. No reference screenshots,
crops or copied originals are included in this evidence.

## Canonical IDs and measured cost

The [README asset list](../../README.md#detailed-forest-floors-and-independent-overlays)
describes the available families; `hex_ground.IDS` owns the executable selection.
Each ID has a matching `sources/environment/<stem>.blend` and
`exports/environment/<stem>.glb`, with an explicitly selected collection in
`catalog/associations.json`.

Generated `resources` records in [verification.json](verification.json) own
per-asset triangle counts, GLB bytes, material/image counts, decoded RGBA8 image
bytes and source/export hashes. Regenerate them with the scoped verifier in the
README after an authorized source/export change, rather than maintaining a prose
copy. Compare the recorded hashes to the current files before treating the records
as current. Map dimensions come from `art_style.TEXTURES` via `ground_tiles.py`.

RGBA8 is a decoded-image accounting convention, **not measured VRAM**. Summing
`decoded_rgba8_image_bytes` counts each file's images independently; a consumer may
deduplicate identical shared foundation/path/river image sets. Mips, GPU formats,
renderer caches, instances, draw calls and the roughness packing policy can change
cost. Texture memory is the deliberate cost of rich painted detail rather than
thousands of grass/leaf meshes; these records do not establish GPU speed or a game
budget.

## Layering, footprint and consumer placement

- Flat-top hex, radius 2.55, source Z-up, tile root at origin. Base occupation
  plane is exactly Z=0, foundation bottom −0.36. Floor detail does **not displace
  vertices**. The foundation is the existing tabletop contract, not a new raised
  terrain platform. Root and shared dimensions are retained in metadata.
- Base and overlay share origin/unit scale; **no additional Z translation**.
  Path width is 0.92, center top 0.012 and edge 0.006. River water width remains
  0.91; two 0.105 banks make total width 1.12. Water top 0.008, bank lip 0.016,
  outer bank edge 0.006. Minimum geometric base/overlay clearance is 0.006.
- No tall roots/grass/rocks occupy the floor. Roots, blades, pebbles, leaves and
  fern fronds are painted marks with shallow tangent normals. Narrow overlay lips
  are millimeter-scale and do not make a raised wall.
- Ordinary depth-tested opaque Principled surfaces only. Place occupant contact
  pivots at their supporting height (review objects on path use Z=0.012); use
  reasonable contact/penetration placement for an object's actual geometry.
  Neither this repo nor standalone GLBs can enforce arbitrary consumer draw order.
- **Interface limitation:** original `hex_stream` water has center −0.18 and
  thickness 0.025, in a cut channel. A solid Z=0 floor hides it. New rivers are
  explicitly `surface_stream_v1`, not elevation-compatible with old recessed
  streams. All existing stream IDs/geometry/dimensions/interfaces are preserved;
  no new-to-old transition, excavation, bridge, crossing or junction is supplied.
- River is a shallow opaque painted surface stream, not volumetric/transparent
  water. No animation, refraction, game renderer or generator integration is implied.

## Exact topology and transforms

Edge 0 is north (+Y in source); numbered counterclockwise every 60°. The normal
is `n(e)=(-sin(e*pi/3),cos(e*pi/3))`. With `a=HEX.half_height`, midpoint is `a*n(e)`
and neighbor translation is `2*a*n(e)` (apothem ≈2.208365). Opposite edge is
`(e+3)%6`. Each connector reserves a 0.48 straight normal approach before the
interior curve; all endpoints retain identical width/profile/height and symmetric
quiet cross-profile paint. No connectors meet vertices. End caps are centered on
origin and extend at most half the ribbon width beyond center, not to another edge.

Rotate canonical assets about source Z at the tile center. GLB uses the existing
Y-up conversion; the equivalent is **positive GLB-Y rotation**. Keep unit scale.
Imported Blender GLBs may use quaternion rotation mode: don't edit inactive Euler
fields. The review helper applies world-Z placement with a matrix, verified against
actual imported mesh coordinates for all six rotations of all eight overlays.

| Canonical piece | k × 60° rotations | Unordered edge pairs / ends |
|---|---|---|
| `straight` (0,3) | k=0,1,2 | 03, 14, 25 |
| `turn_120` (0,2) | k=0,1,2,3,4,5 | 02, 13, 24, 35, 04, 15 |
| `turn_60` (0,1) | k=0,1,2,3,4,5 | 01, 12, 23, 34, 45, 05 |
| `end` (0) | k=0,1,2,3,4,5 | 0,1,2,3,4,5 → center |

Both families use this same complete coverage. Suffixes describe edge-normal
separation, not steering deflection. Through edges are unordered: these static
rivers have no imposed flow direction. Existing selectors export one canonical
collection; they do not need redundant rotated files or a new transform framework.
Typed root extras include `ground_schema`, `ground_layer`, `ground_family`,
`connector_edges` (integer array), `connector_center_end` (boolean),
`connector_piece`, `connector_interface`, width, straight-approach length,
JSON cross-profile and measured min/max heights. Source and GLB retain these extras.

## Comparable visual evidence and observed improvements

[Close + whole-floor sheet](floors-close.png), [160px image-box strip](tile-scale.png),
[all eight overlays](overlays.png), [neighbor chains](neighbors.png),
[all five ground families with both layer types](stacks.png) and
[occupied tiles](occupied.png) are CPU Cycles renders of **real GLB imports** using
`geometry.studio()`/`style_blender.preview()`: 24 samples, four threads, AgX / Medium
High Contrast; source previews retain the normal 1200² / 64-sample preset.
Review uses 400² frames (640×440 neighbors), identical camera/light/color treatment
within each comparison tier, and normalized framing for unchanged forest-kit
`forest_hex_meadow`. Close views use ortho scale 2.8; whole floors 6.6. At 400²,
new floors' projected geometry spans about 277×225 pixels; the 160px strip reduces
that to about 111×90. Close views intentionally crop the tile. Sheets resample
these frames; the 160px box is provisional, not an actual game-camera measurement.
Actual camera, hashes and projected geometry boxes are in
[review-profiles.json](review-profiles.json); projected boxes are geometric bounds,
not a segmentation measurement of visible/shadow pixels. Individual frames remain
in [renders/](renders/). No browser/native GPU performance campaign was used.

Actual image inspection led to two bounded fixes: the first floor pass had too
similar five-island layouts and faint roots/dirt; unequal family-specific drifts,
stronger branching roots, larger embedded pebbles and lobed overlapping litter now
read at the small view. The first neighbor fixture exposed inactive Euler rotations
on imported quaternion roots; matrix placement fixed the fixture and a real-root
rotation regression was added. Final neighbor images have continuous ribbons,
centered seam endpoints and no visible gaps; banks don't rise into walls. Rounded
ends remain near center, and overlays retain the underlying family's open ground.

Compared at matched views to the largely harmonic-wash old meadow:

- Moss gains cushion lobes, dark recesses, leaf fragments and uneven carpet edges.
- Grass gains broad worn-earth gaps and differently oriented blade bundles rather
  than one undifferentiated green field.
- Dirt gains distinct damp/compacted pockets, branching exposed traces and clustered
  flattened pebble/leaf fragments. It remains quieter than litter, intentionally.
- Leaf litter has readable ochre/russet/olive drift masses and lobed leaves with
  close-view veins; no broad geometry is added.
- Pine duff has elongated needle bundles, decayed traces and flattened paired fern
  leaflets. Needles become incidental at the smallest view; macro pockets still read.

Existing tree snag, archery range and knight show normal depth layering above the
new floor/path, without a ground priority trick. The archery range's existing
exported structure/receiving pad obscures much of the ground, as expected; it was
not changed to manufacture a bare-floor comparison. These are representative
occupants, not proof for every future mesh. Theme, softness and detail hierarchy
are qualitative author review, not an independent calibrated art verdict.

## Execution and verification

Reproduce from the root with the commands in
[README — detailed floors](../../README.md#detailed-forest-floors-and-independent-overlays).
Authoring scripts explicitly rebuild only these 13 **new** sources; preserve manual
edits first. Maps use `geometry.material()` and the existing `painted_finish`
packing/encoding helpers; no new exporter or global art defaults were introduced.

Executed checks:

- Fast guardrail: **53 tests**, Ruff, Python/JS syntax and worker safety.
- Existing Blender style/portable fixture suite; selected source-style audit for
  all 13 new sources; selected painted UV/channel audit for all 13.
- Existing incremental `asset-check`: all 13 new assets exported/verified, plus
  regressions for crystal grove, lantern bridge, old meadow, tree snag, archery
  range and knight. Sources remain unchanged by these checks. One byte-only
  regenerated existing archery export was restored to its original tracked file
  (same JSON/size), then reverified; no existing model binary change is delivered.
- Scoped saved-source + GLB audit: all **15 pairs + six ends per family**, both
  representations; **216 matching neighbor seams per family per representation**
  (864 total), **48 real imported-root placements**, every straight approach,
  profile/width/height, all edge containment, finite compatible UVs and typed extras.
- All **40** base + canonical-overlay stacks have ≥0.006 clearance. Source packed
  Base Color/Roughness/Normal images, color spaces, embedded GLB channels,
  effective albedo factors and reimported texture pixels are verified. Floor map
  borders fade to a neutral same-family profile; different ground families are
  deliberate visible material transitions, not universal cross-family texture seams.

Machine-readable evidence is [verification.json](verification.json), existing
`exports/validation.json` and per-fixture profile/hash records. Full worker logs
remain local at `.cache/asset-check/logs/`; they are not redistributed source art.
No installs/upgrades, global terrain regeneration, game import/code changes or
native performance claims are part of this delivery.
