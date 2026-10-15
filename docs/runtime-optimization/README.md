# Runtime-friendly building and water exports

Start from landed vivid/ambient revision
`9a69b514e9fd7b101bf75d358e202da822bbe2c0`, not historical mesh-count prose.
[Actual fixed-camera comparisons and all25 costs](actual-review.html),
[per-asset metrics](metrics.json), [fidelity/loop validation](validation.json),
and [headless Godot measurements](godot.json) bind the exported files by SHA-256.

## What changes, and what does not

The official selected-source exporter now prepares a **runtime representation**
for the 16 animated buildings and two dense bridge tiles:

1. Evaluate the existing source/modifiers with effective object material slots.
2. Temporarily simplify only repeated small `Woodland shared moss cushion`
   prototypes to 50% triangles, retaining their existing painted color/roughness
   maps and interpolated UVs. Build one evaluated mesh variant per shared
   prototype/effective-material tuple, not one modifier/mesh per placement.
3. Reduce two-segment bevels to one segment only at widths no greater than 5mm
   in both local and scaled world space. Broad architectural bevels, joints,
   crystals, signatures, leaves, working props and all placements remain.
4. Export ordinary portable glTF, then bake stationary transforms into compatible
   material/layout batches **under the nearest animation/placement owner**.
   Preserve every animated target and its full ancestor TRS chain. Never bake
   animated motion into stationary geometry or group across owners.
5. Deduplicate only exactly equivalent material contracts, not related shades.
   Retain vertex/UV/normal seams. Preserve distinct coincident corner indices
   where welding would otherwise change Blender reimport topology. BLEND nodes
   would remain separate to preserve sorting; no scoped asset requires a new
   transparency implementation.
6. Replace the GLB atomically, restore every temporary source binding/modifier,
   and never save the `.blend`.

All **23 selected editable source files are byte-identical** to the landed
baseline, including packed maps, original detailed meshes, collection/kit reuse,
UVs, material overrides, animation actions and presentation scenes. Temporary
runtime variants are removed even on exceptions. Character rigs/equipment and
unselected assets never enter the optimization hook.

The other **seven water selections are assessed and retained**: three small water
components and four river overlays already consist of a handful of purposeful
animated/static meshes. The hook refuses consolidation that would increase or
not reduce total scene nodes. Their complete current/foam/waterfall/shimmer loops
remain ordinary transform clips; no water-sheet animation, particles or new shader
contract was introduced. Two dense bridge tiles benefit from the same static
material batching as buildings.

## Costs and recommendation

This is the asset-side best practice for these predominantly stationary tabletop
buildings: keep rich editable authoring sources, reduce runtime node/surface
fragmentation, and isolate a tiny animated part. The existing painted maps already
carry genuinely fine grain/wear; creating extra bake atlases or procedural game
shaders just for this pass would add fidelity/channel risks without addressing the
measured node problem.

All25 counts are in [metrics.json](metrics.json); the HTML table shows both sides
for every asset. Representative actual results (warm headless instantiate medians):

| Asset | Mesh nodes | Surfaces | Triangle instances | Instantiate ms |
| --- | ---: | ---: | ---: | ---: |
| Academy | 7,418 → 40 | 12,100 → 40 | 248,974 → 160,886 | 14.051 → 0.050 |
| Barracks | 5,417 → 35 | 8,812 → 35 | 184,615 → 121,567 | 9.979 → 0.044 |
| Town hall | 7,047 → 52 | 11,100 → 52 | 281,055 → 189,303 | 13.946 → 0.065 |
| Arrow tower | 3,618 → 32 | 5,855 → 32 | 124,101 → 81,285 | 6.348 → 0.042 |

Across all25 selections: **60,729 → 767 mesh nodes (−98.74%)**,
**96,852 → 767 surface instances (−99.21%)**, and
**2,184,583 → 1,511,903 triangle instances (−30.79%)**. GLBs grow from
**105.93MB → 187.65MB (+77.14%)**. The Captain explicitly accepted this measured
GLB-size tradeoff for the reported scene-complexity/instantiation savings:
“Thats a tradeoff I'm willing to make definitly.” This accepts only these measured
bytes, not arbitrary future growth, fidelity waivers, or universal memory/rendered
performance claims. The primary Godot run began with an empty
project/import cache, spent **68.13s** importing all50 before/after scenes, and
then measured a fresh headless process with no other task-owned asset workers. **Scene-reachable mesh nodes, material/surface instances and
triangle instances** are measured from actual glTF buffers/hierarchies. Unique
mesh-definition triangle totals are reported separately: they are not the cost of
all repeated placements.

There is a real tradeoff: batching expands formerly shared prototype geometry into
per-asset vertex/index buffers, so GLB bytes and unique topology grow even while
scene nodes/surfaces and total triangle instances fall. Those buffers remain shared
by multiple Godot instances of the same imported PackedScene; they are not copied
for each building placement. The retained material palette, alpha, images and
silhouettes are not traded away to obtain the node reduction. The measured headless
instantiation reduction, rather than a claim about Blender mesh sharing, supports
this representation.

Actual consumer import/load costs are separate from instantiation. The committed
fresh-project run imported all50 scenes together in 68.13s; it does not isolate a
before/after import-time improvement. First resource loads in the subsequent
process totaled 1,389.60ms before versus 1,277.85ms after (OS cache not flushed),
but woodland bridge grew from 197.122ms to 203.059ms and lantern bridge from
200.528ms to 205.419ms. These single loads are evidence, not stable latency
promises. The consumer must download/import larger GLBs and store larger unique
geometry buffers per asset; sharing a PackedScene across placements does not
remove that per-asset cost. Peak import memory, resident memory, GPU cost and
rendered FPS were not measured and cannot be inferred from node reductions.

### Tactics assessed

| Tactic | Decision and evidence |
| --- | --- |
| Combine compatible stationary detail | Applied to all16 buildings and both dense bridges; actual hierarchy/surface reductions in per-asset metrics. |
| Shared meshes / instancing | Preserve editable kit sharing and share temporary simplified prototypes. Runtime source sharing alone still produced thousands of Godot mesh nodes; prefer measured material batches here. No unsupported glTF GPU-instancing extension or game MultiMesh framework. |
| Shared materials | Deduplicate byte-equivalent shader/texture contracts, ignoring only names. Preserve related color variation and all original encoded maps. |
| Model less invisible detail | Applied to small moss topology and subpixel bevel segments, with actual matched 192/96px standalone views. No deletion of overgrowth placements or wholesale decimation. |
| Texture/shader detail | Retain existing portable painted maps for fine surface detail. No gratuitous texture-atlas, smoke, shimmer or water shader rewrite; current loops/maps are already lightweight. Presentation-only smoke remains excluded by the original selector. |
| Separate animated parts | Preserve every target/ancestor/transform/curve. The same localized crystal, rings, flags, sign, hook, bell, shuttle, lantern and water motion remains. |
| Distance simplification | No new blanket LOD system: node creation was the demonstrated problem; the headless results do not measure distance-dependent GPU cost. The bounded export detail profile is sufficient for this pass. |
| Game-side batching | Not required to address this measured node overhead. Consider only if later real renderer measurements demonstrate a remaining need. No game repository changed. |

## Fidelity, normals and loops

`verify_runtime_blender.py` checks:

- Exact source-file preservation and baseline GLB identities.
- Every **serialized transformed triangle**, all declared vertex attributes and
  material/layout ownership **one-to-one**, with full multiplicity. No zero-area,
  near-zero or legitimate coincident face is filtered or deduplicated.
- Source → unbatched, source → actual optimized GLB and source → reimport
  triangles match one-to-one, allowing cyclic corner rotations but never reversed
  winding or changed connectivity. Full triangle/corner multiplicity survives at
  the source boundary, not just the independent raw → runtime boundary. Serialized
  positions, UVs and normals retain their fixed tolerances; reimport normals remain
  diagnostic only. The reference correctly models the installed exporter's local four-decimal
  corner-normal rounding/normalization before inverse-transpose; it does not
  enlarge a tolerance to fit a measured failure. Actual serialized normal checks
  use a fixed `0.00002` component tolerance, ten times tighter than the initial
  experimental check. Unsupported ill-conditioned transforms fail closed.
- Exact encoded PNG bytes and independently decoded samples/alpha, original
  material texture/color-space channel bindings, and exact animation targets,
  timestamps, values, interpolation and loop extras. No Blender float-image hashes.
- Actual source/runtime-profile and reimported GLB geometry at five poses, fixed
  structure world matrices, moving localized detail, closed endpoints and <0.1mm
  pose point-cloud error. Blender reimport normals are diagnostics, not substituted
  for actual-buffer normal checks.

The [independent diagnosis](diagnosis/README.md) preserves the failed pilots,
exact affected triangles, unmodified load/export/reimport counterfactuals,
analytical normal-rounding bounds, synthetic exports and negative controls. It
explains both the coincident-index compatibility correction and why applying the
known exporter conversion to the reference is not a source-normal waiver.

The ordinary source/GLB round-trip verifier separately checks all25 bounds, finite
geometry and applicable ground-zero roots against **detailed** sources; no placement,
hex footprint, river connector or presentation-collection boundary was moved.

## Standalone visuals and headless timings

Eight representative before/after pairs include academy, barracks, town hall,
arrow tower, bakery, weaver, lantern bridge and a river overlay
([actual native-192px contact sheet](evidence/matched-sheet.png)). Each uses actual
GLBs and **one unchanged camera, neutral SUN-light/world setup and exposure** per
pair. 480px originals and canonical native 192/96px derivatives are retained with
camera/hash receipts. These are gameplay-like diagnostic canvases, not measured
game occupied pixels, artist approval or renderer FPS qualification. Visual review
retains vivid blue/red roofs, purple magic, warm wood, planted overgrowth and role
silhouettes; the moss/bevel simplification has little visible payoff to lose at
those small tiers.

The isolated Godot benchmark imports all50 before/after files and exercises every
`ambient` clip. It checks resolvable tracks, real localized mesh motion and closed
endpoints. Its timing is **PackedScene.instantiate only**, one warmup followed by
11 timed warm trials with immediate frees. Resource loading, editor import,
`add_child`, physics and rendering are excluded from the instantiate interval and
recorded separately where applicable. The JSON explicitly distinguishes an empty
versus reused Godot import cache. The OS page cache is not flushed; “fresh project”
is **not** a cold-OS-cache claim. No actual-game graphical test was performed, and
rendered in-game performance remains **unqualified**.

## Repeatable commands

Use verified installed executables; no installation/global tool changes are needed.
Restore the baseline GLBs from the exact revision if the disposable cache is absent:

```sh
python3 - <<'PY'
import json, subprocess
from pathlib import Path
baseline = json.loads(Path('docs/runtime-optimization/baseline.json').read_text())
for aid in baseline['assets']:
    path = 'exports/' + aid + '.glb'
    out = Path('.cache/runtime-optimization/before') / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(subprocess.check_output(['git', 'show', baseline['revision'] + ':' + path]))
PY

# ASSETS is the explicit existing 16-building + nine-water selection.
IDS=$(python3 -c 'from tools.asset_pack.ambient_contract import ASSETS; print(" ".join(ASSETS))')
python3 -m tools.asset_pack.worker tools/asset_catalog/export_blender.py --label runtime-export --audit-dir .cache/runtime-optimization/unbatched $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/test_runtime_blender.py --label runtime-fixtures
python3 -m tools.asset_pack.worker tools/asset_pack/diagnose_normal_quantization_blender.py --label normal-quantization
python3 -m tools.asset_pack.worker tools/asset_pack/verify_runtime_blender.py --label runtime-fidelity
python3 -m tools.asset_pack.worker tools/asset_pack/verify_pack.py --label runtime-bounds $IDS

# One selected fixed-camera pair; repeat for runtime_review.FOCAL:
python3 -m tools.asset_pack.worker tools/asset_pack/render_runtime_blender.py --label runtime-render buildings/magic_academy

# Supply installed paths. The .NET build also needs its installed DOTNET_ROOT/PATH;
# use process-local environment variables, never a global mise change.
python3 -m tools.asset_pack.runtime_benchmark --godot /path/to/verified/godot --project .cache/runtime-optimization/godot-fresh
python3 -m tools.asset_pack.runtime_review
mise run check
```

`--audit-dir` is optional, constrained to this repository's `.cache`, and preserves
pre-batch runtime-profile GLBs for independent attribute comparison. Neither export
nor checks rebuild/save authored sources. After an explicitly authorized procedural
authoring rebuild, run the official selected-source exporter again: legacy
`export_pack.py` remains an authoring/component-generation path, not the bounded
runtime serialization hook. Full logs are under
`.cache/asset-check/logs/`; generated reports bind current source/export hashes.
The verifier accumulates the entire requested audit before atomically publishing
`validation.json`; selected runs preserve unselected hash-bound records and failed
or interrupted audits leave the previous ledger untouched. A selected run does
not revalidate those preserved records; consumers still require current hashes.
The standalone ambient verifier delegates to this successor audit and never
rewrites historical ambient validation receipts.

## Verification completed for this implementation

- `python3 -m tools.checks`: **130 tests**, lint and both inline JavaScript checks pass.
- Runtime Blender fixtures cover real export/reimport, actual normal-quantization
  counterfactuals and exception-safe source restoration. Successor regression
  controls also reject same-count connectivity/winding/corner-multiplicity changes
  and changed animation poses, exercise runtime-aware standalone dispatch, and
  preserve ledger bytes on selected/failing/interrupted/unpublishable audits.
- Shared Blender style fixtures pass.
- **25/25** existing-source bounds/root and **25/25** full fidelity/five-pose loop checks pass.
- **50/50** actual headless Godot imports/track resolution/motion/loop endpoints pass.
- **8/8** actual matched render pairs are hash/camera-bound; the contact sheet
  was visually inspected for palette, silhouettes and overgrowth retention.

These are implementation checks, not a claim that subsequent no-mistakes/CI
shipping or consumer-game validation has already completed.

## Downstream import handoff

Import the **exact landed main revision** for this change, not a mix of previous
files, new exports and old material tables. Regenerate any derived consumer
manifest/material bindings from those actual bytes. This branch does not edit the
game or complete its parked integration.

- All catalog IDs, selected authored contents, placement roots, source −Y forward /
  glTF +Z forward, ground-zero pivots, bounds and terrain/connector conventions stay.
- Static submesh names and material indices are **not stable attachment APIs**:
  static nodes are replaced by `Runtime surface ...` batches, and exact duplicate
  material definitions can disappear. Preserve image **indexed identity** and
  actual channel bindings; do not reuse old material indices or a name-only fallback.
- Animated target names, their ancestor TRS, the `ambient` clip name, samples and
  loop metadata stay. Different numbers of mesh nodes may now share one moving
  material/owner; this is still the same localized detail, not extra motion.
  A mesh animation target can become a Node3D owner with material-surface children;
  consumers should resolve transform tracks as Node3D, not require MeshInstance3D.
- Godot imports `ambient` with loop mode NONE both before and after. As with the
  landed assets, consumers must apply the catalog's `ambient: true` policy when
  starting continuous playback; GLB extras are not an automatic Godot loop-mode API.
- No skeleton/weapon socket/equipment/unit clip API changes, no new shader/effect
  dependency and no runtime batching framework are required. Source compositor
  glow remains a renderer effect, not newly embedded geometry.
- Recheck the imported counts, loop playback and headless scene instantiation in
  the consumer. Do not infer rendered FPS acceptance from this asset-side report.

Earlier vivid/ambient render ledgers remain immutable snapshots of the landed
**detailed** exports, not relabeled optimized renders. Their tests chain exact
baseline identities to the separately verified runtime successors here.
