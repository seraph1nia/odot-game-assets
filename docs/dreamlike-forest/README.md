# Dreamlike forest art pass

## Scope and predeclared hypotheses

Baseline: `102de2042734a4bffeff54642e483f249de0cd70`. The 239 original
forest source/map/export/preview hashes are preserved in [baseline.json](baseline.json).
Editable originals and embedded maps were copied to the task-local ignored
`.cache/dreamlike-forest/before/` before authoring. No builder regeneration.

The existing two kits already cover mushroom heights/colors, moss, broad leaves,
curled ferns, roots, rune stones, crystals, flowers and lantern fauna. There is no
missing model category warranting duplicate filler. Improve those reusable variants
instead; the new small texture-only decal set is separate from terrain geometry.

After reading D01–D09 and the material/UV/normal/emission/contact/library/export
procedures, inspect actual F1/F4/F5 originals (links in the existing reference index):

- **D03/D04/D07:** existing yellow-green ground/leaf support is too uniformly warm
  and saturated alongside blue/violet caps. Opt-in shared woodland palette with
  moss-green tips, turquoise roots/shadows, violet caps and quieter receiving ground.
  Village palettes, stone/wood/water maps and warm lantern roles remain unchanged.
- **D06:** cyan stems compete with localized spots/gills. Retain shaded gray-lavender
  bodies, mask upper-stem/underside emission, eliminate low whole-cap emission.
  Existing crystal edge masks, stone-bound runes and warm lantern windows already
  provide localized signals; inspect them rather than gratuitously replace them.
- **D01/D05/D08:** `hex_glowing_mushrooms`, `hex_crystal_grove`, `hex_lantern_bridge`
  are the three focal compositions. Regroup two existing peripheral leaf clusters
  at contacts per tile, opening small front approach/rest areas. Dominant caps,
  central crystal and bridge arch/amber lanterns remain recognizable without bloom.
- **D02/D09:** retain all authored geometry/UVs/normals/modifiers/material-slot links
  and shared mesh reuse. No extra triangles or prototypes. Selected material users
  require exact propagation through both libraries and their embedded tile copies;
  [scope.json](scope.json) records that dependency closure, not an all-assets redesign.

The new profile is owned by `art_style.FOREST` / `FOREST_MATERIALS` and the existing
painted-finish module. It is explicit opt-in authoring, **not** a global
`PAINTED_VERSION` bump or automatic change to unrelated generator defaults.
[`forest_refinement.py`](../../tools/asset_pack/forest_refinement.py) is a one-time
baseline-authoring recipe, not a rebuild command for the current refined sources.
It requires `--baseline <inventory.json>` with exact original source hashes, even
without `--apply`; a scope-only run writes `scope.json`, while `--apply` saves
sources/maps and writes `authored.json`. Current sources intentionally fail that
baseline check. Preserve sources/maps and existing receipts before any separately
scoped reapplication; the ignored implementation backups are not shipped here.

## Evidence policy

Fresh matched CPU Cycles source renders use the original saved camera, lights,
frame, AgX/look and 1200-pixel resolution with compositor off/on. Separate portable
views use the existing catalog renderer on actual GLBs, fresh factory scenes,
480-pixel CPU Cycles; it supplies no bloom. 192/96-pixel reductions are provisional
orthographic readability diagnostics, **not measured game occupancy**. Profiles
bind source/export/output hashes and actual settings. No Godot/game import, native
GPU, Forward+ qualification, atmosphere or performance claim is made here.

## Inspected result (implementation-worker art review)

Before is left and final after is right in the matched pairs:

| Focal / reference context | Bloom-disabled source / provisional small view | Actual exported body / emission |
|---|---|---|
| Mushroom grove / F4 | [192 pair](evidence/hex_glowing_mushrooms-source-no-bloom-192.png), [480](evidence/hex_glowing_mushrooms-source-no-bloom-480.png) | [body vs emission](evidence/hex_glowing_mushrooms-portable-body-vs-emission.png) |
| Crystal clearing / F1 | [192 pair](evidence/hex_crystal_grove-source-no-bloom-192.png), [480](evidence/hex_crystal_grove-source-no-bloom-480.png) | [body vs emission](evidence/hex_crystal_grove-portable-body-vs-emission.png) |
| Lantern bridge / F5 | [192 pair](evidence/hex_lantern_bridge-source-no-bloom-192.png), [96](evidence/hex_lantern_bridge-source-no-bloom-96.png) | [body vs emission](evidence/hex_lantern_bridge-portable-body-vs-emission.png) |

Full 1200-pixel source off/on images and 480-pixel actual GLB images are under
[evidence/before](evidence/before/) and [evidence/after](evidence/after/). Source
Fog Glow is genuinely switched off/on; portable views have **no bloom** and their
body-state companions switch actual imported material emission off, not just a
source preview setting. [Portable profiles](portable-profiles.json) bind five
before/after GLBs, including reusable mushroom and spiral-willow components.
[Current components](evidence/components-current.png) were inspected for unintended
palette/glow drift; row order follows the component IDs in scope.json.

- **D01/D03/D04/D07 — pass for the bounded refinement:** the caps now have quieter
  slate-blue/lavender washes; ground support is moss-green rather than yellow-lime.
  Cool leaf roots and softer green tips relate to the teal/lilac enchanted plants.
  These differences remain visible in the 192-pixel pairs. The tall cap and crystal
  still dominate their compositions. Stone facets, timber warmth, water and fauna
  body palettes were retained, not newly improved or reference-certified.
- **D06 — pass with limitations:** cyan is no longer spread over the whole stem.
  Gray-lavender shaded bodies support cyan spots/upper gills, while crystal edges,
  stone-bound glyphs and amber windows retain their original localized roles.
  The [low-view underside before](evidence/forest_mushroom_blue-underside-before.png)
  and [after](evidence/forest_mushroom_blue-underside-after.png) expose the actual
  emitted mask/body rather than hiding them behind the cap. The remaining original
  radial gill geometry and small static spores were not added by this pass.
  Bright spots are still intentionally hot at large size; there is no whole white
  cap, new halo mesh or baked directional light. Subtle game bloom is unqualified.
- **D02/D05 — pass for preservation/contact hierarchy:** original tilted caps,
  smooth organic sides, flat crystal/stone planes and shared meshes are retained.
  Two existing peripheral leaf groups per focal tile were moved/shrunk at contacts;
  this is a modest rest-area improvement at 480/192, **not** a new silhouette family
  or a reliably discernible leaf-placement gain at 96. Bridge aperture and water
  interfaces remain intact. Existing receiving contact/bounce maps were graded,
  not replaced with sunlight/shadow/fog bakes.
- **D08 — bounded diagnostic pass, not game acceptance:** source camera/light/frame
  controls are matched; portable SUN-lit views use their own matched profile.
  [Projected occupancy](occupancy.json) excludes studio and measures selected mesh
  bounds: at a 192 image box the three source assets occupy approximately 132,
  127 and 101 pixels high. A 96 box is half those heights. No current game camera,
  GPU, renderer-import or atmosphere result is claimed.
- **D09 — disclosed cost:** resource growth is small relative to these existing
  texture-heavy assets, but this is not an optimization or performance receipt.
  See the exact definition counts and physical-byte deltas below.

### Rejected iteration and real diagnostic history

[Iteration 1](history/iteration1/) is deliberately retained: removing broad cyan
emission exposed overly dark stems in the occluded source view. [Iteration 2](iteration2.json)
raises **diffuse** lavender body/root value, with a gentler root tint; it does not
add an emission floor, new light, bloom or directional albedo. Final full/small
and underside views were actually inspected after this correction. Intermediate
editable sources/maps remain task-local in `.cache/dreamlike-forest/iteration1/`;
current source/export hashes are in resources.json, not the rejected profile.

The initial before-portable attempt accidentally inherited the source compositor;
those private images remain under `.cache/dreamlike-forest/history-inherited-profile/`.
Only the fresh **factory-scene** canonical portable rerenders are accepted. A first
channel diagnostic wrongly required a nonemitting cap to omit emissiveTexture.
Actual glTF legally retains that texture while omitted emissiveFactor defaults to
`[0,0,0]`. The corrected audit checks the real factor, not texture absence; the
failed diagnostic is retained in checks. A final freshness audit also caught the
native-pass duplicate portable hash after the canonical portable rerender replaced
that PNG; [superseded hashes](history/superseded-portable-bindings.json) remain
historical, and source/portable profiles now have separate output ownership. CPU
renders are not promised byte-identical even with equal controls. No exporter,
validator epsilon or source emitter identity was changed to make these audits pass.

## Source/export fidelity and resources

[Authored recipe receipt](authored.json) preserves the original source hashes,
per-mesh positions/topology/material-index/smooth/UV checksums, effective DATA/OBJECT
slot links and modifier identities. [Iteration 2](iteration2.json) records the later
gill-only source revision. [Current resources](resources.json) bind **22 exact IDs**
to final sources/selectors/GLBs, image PNG hashes/dimensions, material factors,
texture UV/sampler bindings and before/current counts. All serialized POSITION,
NORMAL, TEXCOORD_0 and index **numeric values** match their original counterparts
exactly (maximum delta zero); only six leaf-group node transforms intentionally
change, separately logged. This is not a claim of whole-GLB binary identity.

[Channel fidelity](channels.json) compares each effective source material with
actual embedded GLB PNGs: Base Color/Normal/Emission bytes match their packed source
maps exactly; exported standard **G-channel roughness** matches source scalar pixels
with measured maximum delta **zero**. Gill emission maps have **62.3046875% exactly
black texels**, with exported emissive factor approximately `[0.72,0.72,0.72]`.
Caps have source strength zero and exported factor zero, even where a now-unused
legacy emissive texture is retained. Existing crystal/window/rune factors/channels
and normal maps remain portable. The reference palette helper now respects the
explicit forest tag for both base and suffixed appended materials, so later kit
reuse cannot silently restore the old emission factors.

Totals across the 22 selected GLBs (definitions, not instances):

| Resource | Delta |
|---|---:|
| Unique primitive triangles | **0** |
| Serialized meshes / material definitions | **0 / 0** |
| Embedded image definitions summed across exports | **+32** |
| GLB physical bytes | **+1,311,500 (+1.34%)**, 97,574,948 → 98,886,448 |

New source PNG companions total 6,229,557 bytes in 28 maps, at the existing
512/1024 dimensions. Per-material roughness variants account for additional image
definitions; some currently share identical scalar pixels. This authoring/storage
cost is explicit, not a claim of better batching, draw calls, memory or FPS. Future
roughness-map deduplication may be useful, but no broad pack optimization is bundled
into this visible pass. **193 protected original forest files** (including all
unselected component GLBs and original external maps) retain exact baseline hashes.
Village/units/props/UI source and exported art remain untouched.

## Decals and conditional wind data

The compact four-texture [decal library](../../sources/environment/decals/README.md)
contains source/export-identical transparent PNGs, with straight sRGB RGB and linear
coverage alpha. [Receipts](decals.json), [decoded actual PNG validation](decal-validation.json)
and inspected [dark](evidence/decals-dark.png) / [light](evidence/decals-light.png)
background sheets establish feathering, transparent borders and a ≤0.42 peak
opacity. Dimensions, scale, source/GLB orientation and bounded receiver placement
are documented there. No speculative emission/roughness set, terrain projection
or texture-platform/schema changes.

**No new wind channel is justified or delivered.** Actual source meshes contain
no existing color attributes to overwrite, and original exported leaf root→tip UVs
are retained exactly; root-local/UV-based procedural weighting is possible without
changing the art channels. The future importer/shader must verify UV-V orientation
and stationary contacts (glTF UV serialization is not the same orientation as the
Blender editor). No authorized current game foliage interface/import proof was
provided, so this is a conservative data-preservation decision, **not** a claim of
convincing Godot wind or interoperability. No custom glTF extension/mask schema.

## Executed validation and preview refresh

- `UV_OFFLINE=1 mise run check`: **66 fast tests**, lint/syntax and two inline JS
  programs pass, using existing cached tooling without dependency installation.
- `mise run style-tests`: **27 real Blender fixtures** pass, including localized
  emission's real GLB export/import, UV/normal/slot preservation, and tag-aware
  palette reuse, plus the existing effective OBJECT override/modifier/failure-cleanup
  regressions. No contract was removed or weakened.
- `mise run asset-style-check -- <22 IDs>` and `mise run asset-check -- <22 IDs>`:
  source style and selected source→GLB geometry/material/bounds/reuse checks pass.
- Existing forest footprint/base/endpoints/library freshness and packed-channel
  audits pass for all eleven affected tiles / the 22 selected IDs respectively.
- Pixel/factor fidelity audit passes on the actual exported resources. All eleven
  selected saved-source previews and 22 selected portable catalog thumbnails were
  refreshed; unselected exports were not regenerated.

The [checks](checks/) directory retains successful and real failed diagnostic logs.
[Validation bindings](validation.json) bind the implementation's final
assets/maps/previews and output hashes, and record its implementation-time
code/runtime inputs. These are historical evidence, not results rerun by later
documentation or lint housekeeping. No EIO/Btrfs recurrence was observed during
this bounded CPU-only campaign; it neither fixes nor disproves the host's prior filesystem or
unqualified llvmpipe history. No game repository, UI art, browser/GPU qualification,
engine/runtime/driver change, merge or release is part of this implementation.
The same-worker no-mistakes pipeline owns subsequent review/fixes/test/docs/lint/
push/PR/CI after the implementation handoff.
