# Whisperwood — second selective quality round

Baseline: landed `5cda624`, including https://github.com/seraph1nia/odot-game-assets/pull/10.
The first-round [completion ledger](../whisperwood/completion.json) and exact
canonical renderer/derivative bindings remain historical evidence, not regenerated
second-round claims. All 133 catalog IDs were inspected through all nine 3D paired
contact sheets and both native UI sheets, alongside the original W0 board. Before
images here are preserved **landed first-round after** images, not the earlier
bright pre-overhaul baseline. Exact source/export bytes are preserved locally in
`.cache/quality-round-two/before/`; hashes and tracked actual images bind them.

## Predeclared observations and hypotheses

- `buildings/bakery`: the broad brown porch cap reads as a flat wooden oval.
  Recover a layered warm ochre bread/mushroom shelter, cream underside and raised
  curved crown without hiding the bread/window. D01/D03/D04.
- `buildings/weaver`: crowded roof growth competes with loom/cloth; hanging cloth
  reads as stiff straight strips. Clear independent growth from a roof rest lane,
  bend the existing drapes into alternating flowing folds and edged fabric.
  Preserve loom, sign, bobbins and cloth identity. D01/D04/D05.
- `buildings/magic_academy`: feature orb is a uniformly bright lilac disk, not a
  shaded body. Reduce body emission, retain purple facets, add narrow brass
  armillary bands as purposeful scholarly craft, clear independent roof growth
  around the front ridge. D03/D05/D06.
- `buildings/town_hall`: canopy growth competes with civic bell. Clear independent
  top growth and bring the existing bell forward into its opening; retain canopy,
  civic banners and original emblem. D01/D05.
- `buildings/woodcutter_hut`: wheel reads as a wagon wheel and hoist as a beam with
  ropes. Add readable saw teeth and a working pulley, tilt the existing suspended
  log slightly as a dynamic working arrangement. Preserve doorway/window and
  structural branches. D01/D04.

The other 128 IDs retain already fitting role/faction, planar/faceted/organic
normals, planted contacts, ground connectors, equipment grip and UI structure.
Native controls were visually inspected, not redesigned or rerun as a new native
campaign: their existing quiet ornament, readable states and original seal need
no additional decoration. Per-ID reasons belong to `inventory.json`.

All five edits preserve original saved meshes except named focal subparts and
explicitly thinned independent growth. The suspended log's original pose was
retained instead of the proposed tilt: its supporting ropes already read correctly
and a further pose edit offered no reliable small-view gain. Embedded kit children remain unchanged.
Surviving independent leaf/moss growth retains its source instances and shared
mesh data; only the identified quiet lanes are thinned. Newly authored geometry
belongs to the building hierarchy and preserves its authored world transform.
No kit rebuild, global lighting/style defaults or new control framework. Broad
source-lit planes and limited luminous cores—not darker preview lights—are the
lighting strategy. Canonical neutral SUN renderer remains byte-identical;
authored Area-light views are supplementary.

## Evidence and limits

`inventory.json` accounts for every ID; `renders.json` binds actual neutral views,
96/192 derivatives, renderer fingerprint, source/export hashes and resource counts.
`actual-review.html` is the portable side-by-side review surface. Canvas tiers are
provisional, not measured game occupied pixels; auto-fit is not a frozen camera.
Headless source/export/texture checks and CPU actual renders do not qualify game
integration, native GPU timing/draw calls, animation appeal or artist acceptance.
No game process, import, purchase, release or global tool/config change is authorized
or performed. Active mesh nodes are instance counts, not measured GPU performance.
Resource changes are recorded with their counting convention in [renders.json](renders.json).

Reproduce focused authoring only from preserved landed baseline hashes:
`python3 -m tools.asset_pack.worker tools/asset_pack/quality_round_two.py --label quality-two-author --apply`.
This explicit script refuses changed sources; it never rebuilds a library.
After authoring use the ordinary saved-source checks and render routes documented
in the root README. `python3 -m tools.asset_pack.quality_round_two_review --render`
refreshes these five actual neutral comparisons; omit `--render` only to verify
current bindings and compile the report. Baseline GLBs must remain under
`.cache/quality-round-two/before/exports/buildings/`; recover missing baseline
source/GLB bytes from `5cda624` with `git show`, never rebuild a substitute.
`python3 -m tools.asset_pack.worker tools/asset_pack/verify_quality_round_two_blender.py --label quality-two-preservation`
compares original meshes/UVs/transforms and every embedded kit child against those
preserved sources. Do not rerun first-round authoring/report scripts to rewrite
historical first-round evidence as if it were current second-round qualification.

## Actual review and measured tradeoffs

The initial implementation agent inspected the five full-size pairs and 96/192
canvas derivatives, [supplementary grayscale](grayscale.json) for bakery/academy,
and the standalone HTML in a task-private headless Chrome session. That historical
inspection loaded all 20 displayed images without horizontal overflow at desktop
and 390px-wide layouts; it has not been repeated against the refreshed page. The earlier
shared CDP target was unavailable. Explicit follow-up approval authorized **only**
the missing task-local browser dependency: official Chrome for Testing, unchanged
already-installed MCP, private profile and process-local argument adapter. The
[provenance receipt](browser-provenance.json) records official HTTPS distribution,
Google Storage MD5/length verification and locally computed SHA-256. No signed
supply-chain attestation, GPU or actual-game result is implied.

| Asset | Agent visual judgment under D01/D03/D04/D05/D06 | Limits |
| --- | --- | --- |
| Bakery | Raised warm cap reads as a shelter distinct from roof/timber; wheat, bread and warm window remain clear. D01/D03/D04 pass provisionally. | Broad faceted cap, not illustrative mushroom fidelity; cream underside remains a secondary close-view layer. |
| Weaver | Alternating folded cloth stays suspended at its original top edge; quieter ridge and loom/sign remain legible. D01/D04/D05 pass provisionally. | Fine selvedges are close-view craft, not claimed 96px detail; embedded roof growth remains dense. |
| Academy | Orb retains shaded facets with fine armillary lines instead of a flat emissive disk. Small warm windows and upper purple crystal no longer compete with a uniform bright lower orb. D03/D05/D06 pass provisionally. | This is material/emission strategy, not a new renderer light rig or game bloom result. |
| Town hall | Visible blue canopy rest plane separates the civic crown from surrounding planted growth. D01/D05 pass provisionally. | Bell lean/forward shift is a secondary close-view cue, not a claimed new small-view recognition result. |
| Woodcutter | Broad saw teeth provide a working-tool silhouette; wheel opening, window and hoist remain clear. D01/D04 pass provisionally. | Pulley is purposeful close-view craft; no moving machinery or animation was added. |

D02/D07 remain unchanged fitting family treatment. D08 uses the identical neutral
renderer/auto-fit procedure (not a fixed projection); D09 requires the cost caveat
below. These are agent judgments, not commissioned artist acceptance.

The generated [render receipt](renders.json) owns per-building before/after resource
counts; [the generated review page](actual-review.html) displays node and triangle
instance deltas. Both are produced by `tools.asset_pack.quality_round_two_review`
from the preserved baseline and current GLBs, rather than a hand-maintained table.

Surviving leaves and moss retain shared mesh data rather than being joined into
baked unique mesh definitions. Kit instances retain canonical mesh data. These
resource counts are not draw-call counts, a memory/frame-rate claim or a tested
game/GPU budget; renderer-specific batching/LOD remains unqualified. Exact
definition, instance, material and byte counts are in [renders.json](renders.json).

## Validation receipts and reproduction limits

[Checks](checks.json) and [preservation](preservation.json) bind current sources
and outputs. [Browser review](browser-review.json) preserves the historical browser
inspection and dependency provenance; it does not qualify the refreshed page.

- Historical initial receipts: `mise run check` (99 fast tests, Ruff, Python/JS
  syntax and worker guardrails), `mise run style-tests` (27 Blender fixtures),
  and `mise run asset-style-check -- --all` (118 authored selections). These were
  not rerun in this focused fix round and do not qualify the changed scripts.
- Current focused verification covers the second-round Blender fixtures and
  report freshness tests, five source preservation comparisons, five round trips,
  five painted-channel checks, GLB hierarchy and exact current evidence bindings.
  Saved-source exports never regenerate geometry.
- Focused `verify_painted_blender.py`: all five sources have packed maps, UVs and
  corresponding embedded GLB material channels. Focused second-round Blender
  fixtures test retained shared leaf/moss instances across all five refinement
  paths, selective thinning, kit exclusion, planted cloth tops, scoped orb emission,
  preserved new-geometry world transforms and translation/rotation with the root.
- Preservation comparison verifies nonfocal original mesh data/transforms/UVs,
  every embedded kit child, surviving growth instances/shared mesh ownership and
  new geometry's root ownership. Shader/pixel equivalence is not claimed.
- Five saved-source presentation previews, five neutral catalog thumbnails and
  five canonical neutral comparisons were refreshed through isolated workers
  using the explicitly supplied Blender executable. Renderer bytes and derivative
  recipes remain unchanged.
- Static catalog packaging passed in the initial implementation, not rerun here;
  native UI code/resources remain unchanged, so no new native campaign/capture
  qualification is asserted.

The supplementary grayscale PNGs were re-encoded as explicit RGBA PNG after an
agent image-input decoding interruption; their receipt hashes/recipes were updated.
The refreshed canonical neutral images retain the exact renderer and 192/96
derivative recipe; hashes bind the current outputs.
No-mistakes/forge CI delivery is a separate gate, not implied by these local checks.
