# Detailed hex floors and independent surface overlays

Use when authoring moss/grass/dirt/leaf-litter/needle floors, or adding path and
surface-stream straight/turn/end pieces. This is an authoring recipe, not a game
path generator, renderer-order feature or permission to overwrite existing art.
Read [environment](../families/environment.md), [props](../families/props.md),
[UV/maps](uv-maps.md), [water](emission-water.md) and [export](export.md) first.
D03/D04/D05/D06/D08/D09 retain their single [design owners](../design/index.md).

## Reference interpretation and ground composition

F3 C-CONTACT shows moss joining rocks/steps, varied overlapping leaves and an
open approach. F5 C-WATER shows blue shaded water, warm stone banks and localized
contact foam. Those are theme/context evidence, **not supplied pictures of these
new bare floors or connector parts**. Label the new suite authored adaptations;
no inferred pixel-to-albedo calibration or claim of reference-match acceptance.
Keep occupants dominant: leafy olive greens, muted ochre humus, warm worn earth,
cool teal water; no glowing ground, neon turf or realistic grunge.

Make a readable composition before adding micro marks. Use several unequal,
curving patches and quiet intervening ground, not evenly scattered particles:

- Moss: overlapping cushion-shaped lobes with dark interstices, smaller light
  tips, exposed humus pockets and a few embedded seed leaves/stone flecks.
- Grass: broad sod islands broken by worn earth; directional painted blade
  bundles within islands, darker roots and quieter cut/worn centers. No tall tufts.
- Dirt: compacted warm earth, feathered damp pockets, branching shallow root
  traces, small flattened pebbles, leaf fragments and worn broad lanes. Cracks
  stay delicate; this is forest soil, not a cracked desert.
- Leaf litter: overlapping ochre/russet/olive leaf drifts on dark humus, curved
  stems and midribs, decayed gaps and decomposed small fragments. Vary leaf sizes
  inside intentionally placed drifts; avoid a uniform confetti pattern.
- Pine floor: layered needle bundles along broad duff pockets, scattered painted
  fern fronds with paired tapering leaflets, decaying wood traces and moss gaps.
  Fronds are ground graphics, not big foliage meshes hiding usable floor.

Fine veins/roots/blades, worn micro relief and softened local overlap shadows
belong in Base Color/Roughness/shallow tangent Normal maps (D04), without baking
strong directional scene light. Broad patch differences must survive a tile-scale
view; closeup-only speckle is not a richness upgrade. Use explicit patch layouts
plus deterministic local variation; don't increase triangles to simulate texture.

## Executable owners, coordinates and occlusion

Shared footprint is [art_style.HEX](../../../../tools/asset_pack/art_style.py):
flat-top, Z up, center/root zero. New local heights, widths, approach lengths,
map palettes and relief scales live in additive `art_style.GROUND`, not altered
shared defaults. [hex_ground.py](../../../../tools/asset_pack/hex_ground.py) owns
only authored connector topology/rotation coverage; the builder is
[ground_tiles.py](../../../../tools/asset_pack/ground_tiles.py). Neither is runtime
terrain generation. Preserve all old sources/maps/IDs.

Base occupation plane remains `HEX.surface`, foundation remains `HEX.bottom`.
Painted base normals do not move vertices. Overlays are thin open top surfaces,
not full-hex opaque cards: path/stream cover only their ribbon and rounded end.
Their bottoms and highest lips are explicitly bounded in `GROUND`. Translate
base and overlay to the same tile origin, with no extra Z offset. Normal depth
occlusion is required; no depth-test bypass, render priority or always-on-top
material. Place contact pivots of occupants at the local supporting top surface
if they sit directly on an overlay. A GLB cannot guarantee that an arbitrary
future consumer's object will occlude ground; consumer must preserve depth tests,
up-axis conversion and sensible placement. Report this rather than promise order.

**Old river exception:** existing `hex_stream` water is below Z=0 (see
`HEX.water_center`/`water_thickness`) and works because its base has a cut channel.
A solid Z=0 base hides that water. New independent river pieces are explicitly
`surface_stream_v1`, at positive shallow height, with the old channel width but
not old elevation/bank interface. Do not silently change existing streams or
claim new-to-old height compatibility. Joining those families needs a separately
scoped transition/cut base. A surface stream is intentionally a painted shallow
water overlay, not excavated volumetric river terrain.

## Exact connector construction and transforms

Number edge midpoints counterclockwise: edge 0 is north (+Y), edge 1 northwest,
2 southwest, 3 south, 4 southeast, 5 northeast. With apothem `a=HEX.half_height`,
normal `n(e)=(-sin(e*pi/3), cos(e*pi/3))`, midpoint `a*n(e)`, neighbor center
translation `2*a*n(e)`. Connect only midpoints, never hex vertices or the center
of the image's top side in perspective. Opposite edge is `(e+3)%6`.

Canonical pieces per overlay family:

| Piece | Edges | Recipe |
|---|---|---|
| straight | 0,3 | constant-width ribbon along Y |
| turn_120 | 0,2 | straight normal approaches; cubic rounded interior linking approach shoulders |
| turn_60 | 0,1 | same approach contract, tighter cubic interior; no edge overshoot |
| end | 0 → center | straight approach to center; semicircular terminal cap centered on origin |

Suffixes state **edge-normal separation**, not vehicle steering angle. Two
through edges are unordered (water has no enforced flow direction). At each edge,
reserve a `GROUND.approach`-long straight segment normal to that edge. Keep its
width, cross-profile, Z values and map appearance invariant. Curves start only
inward of the approach. Tangent along the connector is radial; transverse axis
is tangent to the edge. Use monotonic arc-length V and transverse U so turns do
not stretch markings arbitrarily. Do not put rocks/ripples/roots across the seam;
fade endpoint-specific variation to the same crosswise paint profile at BOTH ends.
Round dead ends near center; they are not connectors to the opposite edge.

Rotate around source Z by `k*60` degrees, with unit scale and zero translation
relative to base. In GLB the exporter converts Z-up → Y-up once; source CCW maps
to positive GLB-Y rotation. No manually pre-rotated GLB variants are needed:
selector resolves canonical collection, placement rotation belongs to consumer.
For a neighboring seam rotate/translate independently so the neighbor's opposite
edge meets the selected edge, not by copying the same rotation blindly.

Coverage recipe: turn_60 at k=0..5 gives {01,12,23,34,45,05}; turn_120 at k=0..5
gives {02,13,24,35,04,15}; straight at k=0..2 gives {03,14,25}; end at k=0..5
covers all six center-ending directions. Verify this against actual source AND
reimported GLB mesh edges after transforms, not just string metadata. No crossings,
T-junctions, bridges or extra redundant files are required.

## Maps, save and registration

Create materials with `geometry.material()`, run `painted_finish.apply()` for UV/
supported surfaces, and install family-specific authored maps through its
`image_map()` linear→sRGB contract. Leave unsupported custom floor fields under
their explicit owner; don't rename them to trick generic ground shading into
replacing them. Pack every authored image; keep portable Principled image links.
Color is sRGB; roughness/normal Non-Color. Sizes come from `TEXTURES`; broad floor
receivers use `ground_size`. Reuse foundation/maps among sources; retain editable
PNG companions under `sources/environment/textures/ground/`. UV footprint maps
are XY-local for floors; connector maps are transverse/arc-length local. Verify
TEXCOORD_0 and effective material color factors, not merely image presence.

Save new sources with matching collection/ID stem and ground-zero root. Register
through existing `catalog/associations.json` (`source`, `export_collection`,
`title`, no fabricated `reference`) and selected catalog export; never a new
exporter/selector framework. Root extras own typed layer/edge/profile/height
semantics, validated with real meshes; README documents them for consumers.
Export tools derive catalog facts from actual GLB; don't edit generated index.

## Seam, stack and visual acceptance

Use the scoped verifier/review worker described in README's detailed-ground
section. It opens saved sources, then GLBs, without rebuilding old terrain.
Required mechanical evidence:

1. All 15 unordered through pairs and six end directions **for both families**;
   enumerate pair→canonical piece/rotation and test transformed mesh interfaces.
2. Endpoint positions/width/elevation/full cross-section match neighboring pieces,
   approaches are straight, geometry is within footprint; no endpoint seam bands
   become gaps/overlapping walls. Validate map border profile as well as geometry.
3. All five bases × all eight overlays compose without z-fighting; measure relief
   envelope/clearance. Source/GLB axis, root, channels, finite UV and material color
   fidelity remain coherent. Existing terrain/representative occupants regressions
   use existing checks, not rebuilds.
4. Render complete suite at comparable close and representative tile views,
   straight and both turn/end neighbor chains, and occupied tree/building/unit
   examples. Include unchanged floor from existing forest kit at the same view.
   Inspect actual images for noise, seams, weak patch readability, missing textures
   and clipping; automated geometry cannot certify D03/D04/D05. Private reference
   screenshots must not become public review sheets.

Bound review resolution/samples/CPU threads and report actual profile; actual game
occupied pixels remain unknown. CPU Blender-imported GLB renders are portable
software evidence, not native GPU/game performance. Record GLB hashes, bytes,
triangles (unique primitives), materials, images and decoded texture memory costs
with limitations (mips, instances and draw calls differ in a renderer). Thin
ribbons and painted detail deliberately trade texture memory for low geometry;
PNG compression/file size is not VRAM usage. Report the new-to-old stream interface
limitation and occupation placement requirement with final evidence.
