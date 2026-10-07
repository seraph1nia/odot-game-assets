# Pipeline owners, version contract and command side effects

Read the relevant section before an operation; this is navigation to existing
implementation, **not a second executable specification**. Settings/checks remain
where they are. These procedures do not grant source/export/render/pilot scope.

<a id="owners"></a>
## Authoritative existing owners

| Concern | Owner / interface |
|---|---|
| Shared numeric settings/version | [art_style.py](../../../../tools/asset_pack/art_style.py): `STYLE_ID`, `PAINTED_VERSION`, `TEXTURES`, `GEOMETRY`, `HEX`, `PREVIEW`, `LIGHTS`, `UNITS`, palettes, `CLIP_FRAMES`, `LOOP_CLIPS` |
| Mesh/material/studio helpers | [geometry.py](../../../../tools/asset_pack/geometry.py): `material`, `palette`, `mesh`, `cube`, `lathe`, `beam`, `tube`, `studio`, deterministic RNG |
| Selective normals/preview | [style_blender.py](../../../../tools/asset_pack/style_blender.py); [style_validation.py](../../../../tools/asset_pack/style_validation.py) |
| Painted image/UV/receiver authoring | [painted_finish.py](../../../../tools/asset_pack/painted_finish.py): `apply`, `ground`, `project_uv`, `texture_material`, `image_map` |
| Prototype versus composition | [village_kit.py](../../../../tools/asset_pack/village_kit.py), [forest_kit.py](../../../../tools/asset_pack/forest_kit.py), [enchanted_kit.py](../../../../tools/asset_pack/enchanted_kit.py); [forest_tiles.py](../../../../tools/asset_pack/forest_tiles.py), [enchanted_tiles.py](../../../../tools/asset_pack/enchanted_tiles.py) |
| Rig/equipment/clips | [characters.py](../../../../tools/asset_pack/characters.py): `create_rig`, `equip`, `animate`; [attachment tests](../../../../tools/asset_pack/test_attachments_blender.py) |
| Identity/crops/source/export selectors | [associations](../../../../catalog/associations.json) overriding [manifest records](../../../../exports/asset_manifest.json), [schema](../../../../catalog/SCHEMA.md), [pack reference catalog](../../../../tools/asset_pack/catalog.py), [export planning](../../../../tools/asset_catalog/export_sources.py), [selection](../../../../tools/asset_catalog/blender_selection.py) |
| Export without source rebuild/save | [export_blender.py](../../../../tools/asset_catalog/export_blender.py) |
| Incremental cache and round trip | [check.py](../../../../tools/asset_pack/check.py), [verify_pack.py](../../../../tools/asset_pack/verify_pack.py) |
| Style/grid/packed channels | [source-style audit](../../../../tools/asset_pack/verify_style_blender.py), [forest audit](../../../../tools/asset_pack/verify_forest_blender.py), [paint audit](../../../../tools/asset_pack/verify_painted_blender.py) |
| Worker/error/log interface | [worker.py](../../../../tools/asset_pack/worker.py) |
| Current task/CI command definitions | [mise.toml](../../../../mise.toml), [tools/checks.py](../../../../tools/checks.py), [catalog workflow](../../../../.github/workflows/catalog-pages.yml) |

Read symbols instead of copying their numeric values into recipes/family leaves.
Current bevel/map/preview/hex/clip values are implementation facts, not extracted
picture truths or newly calibrated universal art targets. Some kit-specific
materials remain authored in their builders; this guide does not move them.

## Runtime and reproducibility

Current worker/CI support is Blender **5.2.2 LTS**. Worker resolution: explicit
`--blender`, `BLENDER`, PATH, then the machine's pinned fallback path. Catalog
`export`/`thumbnails` have their own `--blender` default (`blender`): pass an
explicit available executable when needed; don't assume worker fallback applies
to every catalog command. Record actual runtime/version/build hash in evidence.
No installation, upgrade or desktop/add-on operation follows from this guide.

The current compositor uses `scene.compositing_node_group` and Glare input sockets;
unit actions/NLA use action slots. Test those operations before claiming another
runtime supports them. Python/uv/MCP expectations remain in existing setup docs.
`clear_scene()` seeds geometry RNG; image fields are deterministic, but source
files/renders are not promised byte-identical across runtimes/devices.

<a id="preview"></a>
## Preview contracts

Source studio: `geometry.studio()`/`style_blender.preview()` with live style preset.
Saved-scene rendering: [render_previews.py](../../../../tools/asset_pack/render_previews.py)
does not restyle/save. Individual painted assets audit saved presets; older assets/
libraries keep authored presentation until explicit migration.
Portable thumbnails: [render_blender.py](../../../../tools/asset_catalog/render_blender.py)
uses its separate bounds-fit GLB lighting/camera profile. Neither profile is game
lighting. [Review scenes](../blender/review-scenes.md) owns the comparison procedure;
[D08](../design/presentation.md#d08) alone owns provisional view tiers.

<a id="checks"></a>
## Choose a check or operation (commands run from repository root)

Use canonical `category/name` IDs for selected jobs. Short pack names are accepted
by `asset-check`/source-style routes; don't assume that for catalog CLI IDs.
These are **later authorized command examples**, not a requirement to execute them
for a documentation change. Help/source inspection can verify arguments without
starting Blender. Avoid `--all` unless broad scope is approved.

| Purpose | Existing command | Side effects / coverage |
|---|---|---|
| Fast source-independent route | `mise run check` | Lint, AST/Python/JS syntax, worker guards, fast unit tests using temporary/mocked fixtures; no production Blender/asset generation. Missing Ruff falls back to `uvx`, which can fetch/install its pinned requirement: check availability/permission first. |
| Selected source-style audit | `mise run asset-style-check -- buildings/archery_range environment/hex_crystal_grove characters/knight` | Opens existing sources in worker; nodes/maps/UVs/normals/root/rig checks; no .blend save/rebuild/render/export. Worker writes log. Old preset exemptions retained. |
| Shared style fixtures | `mise run style-tests` | Creates temporary Blender fixtures/maps and a real test GLB export; not read-only; use for approved helper/default changes, not docs calibration. |
| Attachment fixtures | `mise run blender-tests` | Isolated fixture rig/attachment checks, not production rebuild; needs actual runtime and fixture scope. |
| Incremental export + round trip | `mise run asset-check -- buildings/archery_range environment/hex_crystal_grove characters/knight` | May write GLBs/manifest/index/validation/cache/logs; never geometry rebuild, source-save or render. Unchanged verified inputs start no Blender worker. |
| Selected direct source export | `python3 -m tools.asset_catalog export buildings/archery_range --blender /path/to/blender` | Writes requested GLB/manifest/index atomically; no .blend save/rebuild/render. `--blender` is catalog executable selection. |
| Forest grid/library audit | `python3 -m tools.asset_pack.worker tools/asset_pack/verify_forest_blender.py --label forest-grid hex_crystal_grove hex_lantern_bridge` | Opens sources/loads prototypes in memory; footprint/base/river endpoint and geometry signature evidence; writes worker log, no source save. |
| Packed/embedded image coverage | `python3 -m tools.asset_pack.worker tools/asset_pack/verify_painted_blender.py --label painted-maps buildings/archery_range environment/hex_crystal_grove` | Opens sources and reads GLBs; writes `.cache/softness/texture-validation.json` plus log; no source/map/export generation. |
| Render existing saved scene | `python3 -m tools.asset_pack.worker tools/asset_pack/render_previews.py --label selected-previews archery_range hex_crystal_grove knight` | Writes corresponding `exports/previews/` PNGs/logs; no source save/restyle. Supports pack catalog model/tile names, not arbitrary component IDs. |
| Portable component thumbnails | `python3 -m tools.asset_catalog thumbnails environment/components/forest_crystal_blue --blender /path/to/blender` | GLB-import rendering; writes thumbnails/state/cache, not source. |
| Review gallery | `python3 tools/asset_pack/gallery.py` | Writes local review surface/download copies; no art verdict. Before/after review generators need preserved baseline caches. |

`--force` on asset-check ignores verification cache; on thumbnails rerenders the
selection. `--no-render` on builders skips rendering only: **builders still save
sources and can write maps**. Current build commands remain in
[README](../../../../README.md#reference-asset-set); inspect manual edits/dependencies
through [libraries](../blender/libraries.md) before using any.
Legacy `export_pack.py` can regenerate standalone component sources; selected
catalog export is the source-preserving route for manual refinements.

## Interpret results and failures once

- Worker prints start/finish/duration/log path. Full logs in `.cache/asset-check/logs/`;
  on failure show one focused result and final twenty log lines plus path.
- Hashes of source/export/exporter/verifier/runtime/selection/kits invalidate cache.
  Export/check does not propagate library edits to embedded models. A kit-change
  notice requires explicitly scoped source rebuild after preservation.
- Round-trip verifier samples geometry/material/skin/loop/pose bounds and repeated
  mesh reuse; it is not complete animation appeal, all vertex-path or GPU proof.
- Source-style tests enforce channel/color-space/UV/shape/root/socket/clip contracts;
  they don't measure visual resemblance/palette balance/readability. Forest signature
  checks compare geometry, not all material/normal/UV semantics.
- Missing runtime/auth or unsafe source overwrite: stop/report exact problem;
  don't install tools, manipulate GUI, weaken checks or broaden the campaign.
- Asset refinements require both current mechanical evidence and
  [visual acceptance](../review/acceptance.md). A docs-only task should use bounded
  navigation checks, not execute the asset commands above merely to prove links.
