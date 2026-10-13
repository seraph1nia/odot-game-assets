# Whisperwood overhaul — direction, inventory and evidence

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
192 and 480 occupied-pixel inspection tiers (provisional, not measured game views).
Keep before/after lighting identical; an additional gloomy presentation view is
allowed only if labeled as such. Inventory rows remain pending until actual
source/export/check/image evidence exists; a material-only row cannot be called
an individually redesigned silhouette.

Native UI is present in the catalog, but the supplied board has no UI design.
It already uses a muted woodland Ledger theme and an original menu seal with
source-bound native captures. Whether to restyle that API-compatible native suite
or retain it as a category-appropriate exception requires an explicit scope
resolution, not silently counting it as a 3D pass. Overview scenes must likewise
be synchronized or disclosed as historical assemblies rather than fresh outputs.

## Delivery evidence

Actual output comparison, per-ID status, portable channels, root/rig/clip/hex
checks, resource deltas and known limitations will be bound here as they are
produced. Guidance changes alone complete no asset. Current phase: direction and
inventory captured; implementation and visual verification are pending.
