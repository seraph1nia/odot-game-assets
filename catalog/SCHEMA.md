# Catalog associations v1 and generated index v2

`catalog/associations.json` is tracked, human-editable metadata. The catalog's
generated index at `exports/catalog.json` is disposable and should not be edited.
Every exported GLB appears without an association. No external reference image
is inferred from an export filename or from a pack-wide reference path.

```json
{
  "schema_version": 1,
  "assets": {
    "exports/props/kit/roof_tile.glb": {
      "title": "Roof tile",
      "source": "sources/props/shared_village_kit.blend",
      "reference": {
        "path": "sources/reference/my_sheet.png",
        "crop": [100, 40, 320, 250]
      },
      "preview": "exports/previews/roof_tile.png",
      "thumbnail": "exports/thumbnails/props/kit/roof_tile.png",
      "animation_policy": {"settle": false, "turn": true}
    }
  }
}
```

All paths are relative to the repository root. Missing files are unavailable
until they exist. Paths outside the repository are rejected. The fields are optional:

| Field | Meaning |
| --- | --- |
| `title` | Display name; otherwise manifest title or a readable export stem |
| `source` | Editable `.blend`; default is the matching relative path in `sources/` |
| `reference` | Object with `path` and optional `[x, y, width, height]` pixel crop; a string path also works |
| `preview` | Rendered image; legacy manifest assets default to `exports/previews/<stem>.png` |
| `thumbnail` | Grid thumbnail; default `exports/thumbnails/<asset-id>.png` |
| `animation_policy` | Clip names mapped to `true` (loop) or `false` (one shot) |
| `export_collection` | Explicit Blender collection to export, for terrain or shared libraries |
| `export_object` | Explicit Blender root object to export with its descendants |

Use `null` to suppress a default source, preview, thumbnail, or reference. Reference
crops use the image's natural pixel dimensions. Without a crop, the full image is
shown. Associations for missing exports are retained but do not create cards.
Export selectors are optional and mutually exclusive. Without one, the exporter
uses a collection or root object matching the asset ID's final segment. See
[batch export selection](#batch-export-selection) for discovery exclusions and
shared-library mappings.

The export manifest at `exports/asset_manifest.json` may provide these same fields
on entries in its `assets` array, keyed by `file`. Explicit associations override
them. Export byte size, mesh count, triangle count, material count, clip names, and
available clip durations come from the GLB itself; they cannot be overridden by
prose or stale counts in a manifest. Meshes count serialized mesh definitions, not
scene instances; the selected exporter also refreshes the existing manifest `meshes`
field from these facts. Triangle totals count mesh primitives (triangle lists,
strips, and fans), matching the existing pack's geometry statistics, rather than
duplicating counts for instances. Materials count material definitions.

Clip loop policy is chosen in this order: association `animation_policy`, per-asset
manifest `animation_policy`, GLB animation `extras.loop` boolean, then manifest
`one_shot_clips` / `looping_clips` defaults for that manifest's listed assets only.
Unknown policy remains `null` in the index; the UI starts with Loop unchecked.
The viewer always discovers playable clips from the actually loaded GLB.

The generated index includes `schema_version`, `revision`, `warnings`, and `assets`.
Each GLB asset has a stable `id` (export-relative path without extension), `category`,
display metadata, statistics, `animations` with `{name, duration, loop}`, and
available `model`, `source`, `reference`, `preview`, and `thumbnail` records.
File records contain repository-relative `path` and cache `version`. The model
version is a SHA-256 hash of the whole GLB; ancillary versions track file changes.
`error` records a model inspection failure while preserving the card.

## Native UI entries (generated index v2)

Associations and export-manifest formats remain unchanged. The generated index
uses `schema_version: 2`. Existing GLB asset IDs, facts, file records, animation
policies and behavior are unchanged; a missing `kind` denotes a legacy GLB entry
with a non-null `model`. Consumers of the mixed index must dispatch on `kind` or
presence of `model`, not assume every asset is 3D. Blender thumbnail generation
filters by `model`; native UI never enters implicit 3D discovery.

`tools/asset_catalog/ui_assets.py` adapts the landed UI inventory's actual
`implementation.resource` bindings and `payload.json`, not a parallel inventory.
It deduplicates resource aliases, excludes omitted/planned work and advertises
only `UI/` resources plus the useful HUD/menu authoring examples. Native records
have `model: null`, empty `animations`, null geometry statistics, and:

| Field | Meaning |
| --- | --- |
| `kind` | `godot-scene`, `godot-theme`, or `image` |
| `role` | `component`, `theme`, `art`, or `showcase`; compositions are not runtime components |
| `id` | Stable `ui/<inventory-id>`; original seal uses `ui/menu-seal` (historical inventory key `watch-seal`, **not** the rejected Watch exploration image) |
| `inventory_id`, `inventory`, `aliases` | Owning inventory binding and other inventory concepts illustrated by this same resource; no duplicate research-node/health-style component |
| `authored_resource` | Repository-relative source resource path, retained even for unpublished showcase scenes |
| `resource`, `source` | Native runtime file records; showcase downloads are suppressed in both live/static catalogs (`resource_excluded: true`) |
| `package`, `api`, `provenance` | One shared runtime ZIP, interface documentation, and source/render provenance file records |
| `dependencies`, `dependency_scope` | Explicit **shared package** file/hash set, not a claim of a per-scene minimal dependency closure |
| `preview`, `thumbnail`, `preview_label` | Actual native capture/original PNG and honest static/mock-data/sample label |

Categories are `ui/components`, `ui/theme`, `ui/art`, `ui/showcases`. All published
file links are repository-relative and content-hashed. The browser uses an image
and documented resource/download view for native entries, with no model-viewer,
animation or camera controls. PNG alpha has checkerboard receiving backgrounds.
The full-size image link preserves access to dense native compositions.

The normal build checks source/dependency hashes, native-loaded resource identity,
image hashes/dimensions, original seal linkage and capture-generator binding.
It copies the single runtime dependency set, shared ZIP, selected views and owning
documentation into the normal static artifact; private history/logs and prototypes
are never bundled as runtime. Fixed ZIP member times/permissions and stored members
make bytes independent of file timestamps and compressor versions. See
[UI catalog evidence and authoring](../docs/ui/catalog/README.md).

## Batch export selection

`tools/asset_catalog/export_sources.py::plan_exports()` discovers nested `.blend`
sources for 3D export. Implicit discovery skips root-level overview scenes, shared
libraries named in explicit `source` mappings, and these two 2D UI authoring sources:

- `sources/ui/menu_seal.blend`
- `sources/ui/explorations/watch_seal.blend`

The UI sources remain editable PNG-authoring projects, not automatic GLB assets.
Other nested sources retain discovery behavior. Existing GLBs and explicit catalog
mappings still supply candidates; explicit asset-ID selection is unchanged. Shared
libraries use per-asset `source` mappings and selectors rather than exporting an
entire library implicitly.
