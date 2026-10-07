# Prototype versus composition edits and propagation

Use before changing a shared mushroom/roof/prop/animal, not just before a builder.
Primary visual owner: [D07](../design/consistency.md#d07).
Pipeline owners: [village_kit.place](../../../../tools/asset_pack/village_kit.py),
[forest_kit.place](../../../../tools/asset_pack/forest_kit.py),
[enchanted_kit.py](../../../../tools/asset_pack/enchanted_kit.py),
[check.py](../../../../tools/asset_pack/check.py) and
[verify_forest_blender.py](../../../../tools/asset_pack/verify_forest_blender.py).

## Inputs and stop conditions

Selected asset/feature, actual `kit_asset`/`kit_source`, current source/maps,
manual-edit inventory, dependent compositions and authorized edit/rebuild scope.
If manual work cannot be preserved or the dependency closure exceeds approval,
stop and report that exact scope rather than regenerating to discover damage.
No library or dependent rebuild is authorized by installing this guidance.

## Ownership decision

| Desired change | Owner |
|---|---|
| One instance placement/scale/rotation or composition density | Containing model/tile recipe/source |
| Repeated prototype silhouette, UVs, face normals, intrinsic details | Named shared-library prototype |
| Unique approved role/material variant | Explicit variant ownership; inspect shared mesh/material/image users first |
| All-family palette/field/runtime policy | Existing settings/helper owner; separate migration scope, not a local repair |

`village_kit.place()` appends `kit_<kind>` once to a prototype cache and copies
objects while retaining mesh data; forest placement appends `forest_<kind>` from
its chosen library similarly. Root custom properties track kind/source. Materials
can have object-linked variants (roof tiles) without duplicating the mesh.
Embedded models are portable authored copies, **not live links**.

## Procedure

1. Inspect root tags and mesh/material/image users. Resolve actual sources and
   selectors through [catalog metadata](../../../../catalog/associations.json),
   not a guessed shared library filename. Enchanted placement uses the companion
   library; don't merge it into the original forest library.
2. Locate prototype and every affected composition/standalone export via current
   manifest kit usage/source mappings and tile/builder recipes. Record the closure
   explicitly; existing fingerprints detect changed libraries but do not by
   themselves identify all intended semantic dependents or propagate geometry.
3. Preserve hand-edited source .blends, external/packed maps and existing exports/
   review baselines. Document which builder inputs reproduce them and which edits
   must be retained manually. Backups aren't permission to overwrite unknown work.
4. For a prototype change, edit that prototype once in approved owned authoring
   work; use [normals](normals.md)/[UV maps](uv-maps.md) only as relevant. For a
   composition change, modify placement/recipe while retaining shared mesh data.
   Avoid accidental Edit Mode changes to a shared mesh when only placement varies.
5. If rebuilding is approved, explicitly rebuild the named library before its
   named dependent models, after preserving manual refinements. Existing builder
   commands are in [README](../../../../README.md#reference-asset-set); they save
   sources and may write maps/previews. `--no-render` skips rendering, **not source
   or map writes**. Don't run all assets because selecting dependencies is hard.
6. Export/check existing selected sources only after source propagation is complete.
   `asset-check` notices a changed kit but exporting does not refresh embedded
   prototype geometry. “Export passed” does not close a stale-library notice.
7. Verify repeated mesh sharing and forest prototype geometry signatures through
   [existing checks](../pipeline/index.md#checks). Inspect normals/materials/maps
   too: forest geometry signatures compare local vertices/topology, not all
   material/UV/normal semantics. Preserve current guarantees without overstating them.
8. Review the changed prototype in at least relevant assembled contexts and target
   view profiles; record changed rules and cost deltas under [acceptance](../review/acceptance.md).

## Output, failure and reversibility

Output: one owner per repeated form, preserved mesh reuse, explicit fresh source
propagation and approved dependent evidence. If a library changed but models remain
stale, stop acceptance and scope the rebuild, not a validator bypass. If a manual
prototype diverges, preserve/document it before deciding a variant or library edit;
never silently fork every mesh to get a green check.

Rollback restores library **and compatible dependent source/export/maps** together.
Changing `PAINTED_VERSION`/global style or runtime requires scoped tests/migration;
this procedure creates no new build orchestrator or automated blanket rollout.
