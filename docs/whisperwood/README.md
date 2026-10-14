# Whisperwood overhaul — direction, inventory and evidence

This is the landed **first-round** record. The
[second selective quality round](../quality-round-two/README.md) supersedes five
building source/export/image rows; the other 128 catalog entries are retained.
The exact renderer/derivative bindings below remain historical first-round evidence,
not fresh qualification of changed second-round sources. Do not rewrite this ledger
with later exports or rerun its authoring/report scripts as a current-round refresh.

## Direction analysis (before implementation)

The supplied [board](../../sources/reference/whisperwood/direction.png) is an
illustration, not demonstrated 3D detail. Its painterly edges, forest background,
atmospheric depth, smoke and tiny flowers cannot be reproduced merely by changing
RGB values. No rendered acceptance is claimed here. Source provenance and exact
bytes are in the [reference manifest](../../sources/reference/whisperwood/manifest.json).

Observed: tree trunks become structural arches; roots grip masonry; moss shelves
sit on roof overlaps; foliage trails across aged timber rather than forming an
even border. Cool desaturated slate, gray-green leaves and weathered brown wood
support small amber interiors and cyan/violet lantern/crystal accents. Open door
arches stay visible amid abundant growth. Role-specific working arrangements are
large: lumbermill wheel/hoist/log racks; bakery cap roof/bread/wheat; gold mine
low portal/cart/ore; stonecutter standing blocks/crane; metal mine tall dark
rock/rails; weaver flowing cloth/loom; market tent peaks/scales; town hall antler
branches/tall civic glazing. Each trade has a different massing rhythm, not the
same house with different signs.

The [visual direction report](direction-review.html) shows the supplied board
against preserved actual `woodcutter_hut`, `weaver`, `knight` and
`hex_glowing_mushrooms` previews. It uses the project's offline reference-library
tokens/serif hierarchy. A working Lavish session was opened with current
`lavish-axi` help/playbooks; the result was handed back with a receipt, not left
with an untracked feedback poll. Serve the repository over localhost to load its
full JSON ledger. This is before/reference analysis, not a before/after verdict.

Compared with the inspected existing previews: our bright grass and saturated blue roofs,
clean rectilinear framing, exposed foundation edges and sparsely dressed large
planes read as tidy toy villages. Existing forest caps and crystals can dominate
through saturation/glow. Units already have useful role cues but much less
material wear, traveling equipment and personality layering. Preserve their
chibi faces and weapons, not the board's implied realistic anatomy.

Transferable decisions: exaggerate a different functional silhouette per asset;
add roots/vines/moss at real contacts and clustered story detail; use related
low-saturation body shades and quieter emissive bodies; reserve luminosity for
small functional accents; retain open approaches, faces, grips and weapon
negative space. Materials carry delicate grain/lichen/staining; meshes carry
branches, joints and readable purposeful props. A gloomy *material* direction
must survive neutral GLB previews; darkening studio lights alone is insufficient.
No surrounding forest backdrop is added to exported buildings.

## Inventory and preservation

[Completion matrix](completion.json) starts with **133 actual catalog IDs**:
118 3D exports (16 buildings, 8 characters, 60 environment IDs including 34
shared components and 13 detailed-ground/overlay variants, 34 props) and 15 native
UI entries. Aliases, rotations and the six unit clips are not extra assets.
The 3D planner resolves 67 unique saved source files. Root overview sources,
two UI seal authoring sources, four woodland decals, painted texture companions,
reference pictures, native theme artwork and animations are additional dependencies,
not silently omitted IDs. Empty audio/effects categories have no existing assets.

[Baseline](baseline.json) records catalog selection, exact source/export hashes
and export selectors. Exact originals and existing previews/thumbnails were copied
to `.cache/whisperwood/before/` before authoring. Do not rebuild these edited
sources from the old pack scripts: refinement must preserve manual meshes, UVs,
material variants, rigs, clips, attachment transforms and root/hex contracts.
The cache is local preservation, not distributable evidence; before-view images
used by the final comparison must be tracked separately.

## Scope and review gates

The task authorizes isolated asset previews and saved-source exports/checks, not
game launches, game journeys, imports, global settings or tool installation.
Mechanical checks do not establish artist acceptance, native GPU performance or
actual game-camera quality. Review matched before/after exported views at 96,
192 and 480 px canvas tiers (provisional, not measured occupied/game pixels).
Keep the neutral renderer/lighting procedure identical; its automatic geometry
fit is not a frozen camera projection. Authored studio views are supplementary,
not quantitative matched views. Rows require actual source/export/check/image
evidence; material-only rows are not individually redesigned silhouettes.

The scope ruling includes all 15 native UI entries, followed by the clarification
**“Only do the sub parts that need refinement.”** The board has no UI design:
retain the existing Ledger structure, native API, contrast/hit geometry, fonts
and original seal. Only six SVG ornamental palettes needed muting; they and
unchanged native resources are recorded in [ui-refined.json](ui-refined.json).
The three root overview sources/renders are explicitly historical assemblies,
not synchronized Whisperwood outputs; preserving their manual assembly content
avoids silently replacing it with a rebuild. Two seal authoring sources remain
unchanged along with the original seal identity.

## Delivery evidence

- [Actual 133-ID before/after review](actual-review.html): actual exported GLBs
  and native captures, not generated illustrations. [Nine 3D contact sheets](contact-sheets.json)
  cover all 118 GLBs; two UI sheets live in `evidence/sheets/ui-{1,2}.png`.
- [Completion matrix](completion.json): per-ID refined/retained subparts and
  reasons, current source/export/image hashes, measured resource deltas,
  selected saved-pose bounds and explicit noncatalog decisions.
- [Authored sources](authored.json): all 67 canonical owners, baseline gates,
  shared-geometry correction, original-UV preservation and corrected bow/crossbow
  wraps fitted to actual grip geometry—not attachment pivots.
- [Render receipts](renders.json): 118 genuine before/after pairs, renderer
  fingerprint, hashes and derived 192/96 canvases. Before bytes are the original
  published exports, not a reconstruction or an assumption that every old source
  preview was fresh. All 118 published thumbnails now bind current exports.
- [Check receipts](checks.json): saved-source exports, portable embedded channels,
  source-style/forest-grid/interface checks and focused Blender fixtures.
- [Decals](decals-refined.json): four muted source/export PNG pairs; their 512px
  dimensions and every alpha coverage byte are unchanged. [Original records](decals-baseline.json)
  and tracked before images preserve that comparison.
- [Current native qualification](../ui/worldtree-validation.json): 3,626 checks,
  121 actual full-campaign captures, 14 native catalog images, independent
  UI-only payload/ZIP load. The first 180-second software-rendered full campaign
  timed out; the explicit bounded 600-second retry passed without dropping cases.

Agent inspection covered every paired contact sheet and full-size building,
unit and native UI focal images. It found/corrected inward-normal growth placement,
shared-data copying, missing UVs on newly textured original users, and floating
new bow/crossbow wraps. The material-volume guard has actual saved-bakery node/link
and exclusive presentation-use evidence; unknown portable surfaces still fail closed.
No acceptance check was waived.

### Limitations and preservation

This is a source-preserving iteration toward the illustration, not a claim of
reference fidelity or commissioned artist approval. Existing architecture,
organic caps/facets, faces, rigs/actions, functional narrow parts and flat floors
remain where already fitting. Muted material-only rows are identified as such.
No game process/import/release, actual game camera, GPU performance or automated
artistic judgment is qualified. The native campaign uses software Mesa/Xvfb.

Dense roof/contact growth increases mesh instances substantially: the current
academy has 7,495 active exported mesh nodes. Mesh datablock reuse is preserved,
but it does not promise renderer batching or game frame rate. Per-ID active
primitive/triangle instances and mesh-definition/material/byte deltas are in the
matrix; optimization/LOD/game budgets need renderer-specific review, not a waiver.

Exact baseline `.blend`/GLB files remain locally in `.cache/whisperwood/before/`;
tracked baseline hashes and the original checkpoint commit preserve their
provenance. Color maps are intentionally pixel-graded copies preserving painted
variation; existing roughness/normal maps and authored UVs are retained. Newly
created color/finish companions sit under source-category `textures/whisperwood/`
(or the existing category texture ownership), are packed and are embedded in GLB.
Do not regenerate manual sources or historical assemblies from old builders.

### Reproduce the mechanical evidence

Run `mise run check`, `mise run style-tests`, `mise run asset-check -- --all`
and `mise run asset-style-check -- --all`. Run the read-only forest verifier
and `verify_painted_blender.py` through `tools.asset_pack.worker` with the
118 canonical IDs from `baseline.json::jobs`. Focused fixtures are
`test_woodland_blender.py` and `test_woodland_bindings_blender.py`.
After checked exports, `python3 -m tools.asset_pack.woodland_review --stage after`
refreshes actual neutral views; `woodland_inventory_blender.py` records selected
subparts and `python3 -m tools.asset_pack.woodland_report` binds the ledger.
The before-stage requires preserved original exported bytes.

Implementation/check/image artifacts are complete for the canonical catalog.
Required no-mistakes/PR delivery remains a separate firstmate-directed gate;
these local checks are not a green pipeline or non-draft PR claim.
