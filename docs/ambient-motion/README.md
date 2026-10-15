# Small living details — actual source and exported loops

This is the localized-motion addition to the [vivid painted recovery](../vivid-palette/README.md),
not a new animation system or game integration. The palette checkpoint is commit
`ac41b74`. Landed overgrowth, original mesh datablocks, working signatures,
material colors/maps, original orphan IDs, roots, character rigs/sockets and all
six character clips survive. Sixteen buildings each receive **one connected
animated spot**; nine water entries cover every existing water representation.

Open [the complete motion review](review.html) for fixed-camera, actual-GLB
key poses and deliberately stepped GIFs. The GIFs illustrate selected poses;
they are **not** evidence of runtime frame rate or smooth game playback. The
[neutral full-catalog comparisons](../vivid-palette/actual-review.html) bind the
final exported assets, not an obsolete palette-only export.

## Clip and playback contract

- One ordinary object-action clip named **`ambient`**, not a skeleton, particle
  simulation, shader-animation extension, animated camera or presentation overlay.
- Five authored keys at frames **1, 25, 49, 73, 97**, 24 FPS. The four-second
  rest → positive extremum → rest → negative extremum → rest sequence uses
  soft Bezier easing with zero-speed endpoints. Start and end poses agree.
- The unchanged official Blender exporter samples these actions at 24 FPS:
  **97 samples per sampler**, not 97 manually authored poses. Existing exporter
  timestamps start at `1/24` second and end at `97/24`; catalog duration therefore
  reads approximately **4.041667 seconds**, including the initial held rest.
  No global export timing changes were imposed on existing character clips.
- GlTF animation `extras.loop` and catalog `animation_policy.ambient` are `true`.
  The existing catalog discovers the actual GLB clip and defaults its Loop
  control from that policy. An association alone is never counted as animation.
- Other engines need to enable repeat on their **actual imported clip name**;
  arbitrary glTF extras are not a universal engine looping standard. In Godot,
  resolve the scene's `AnimationPlayer` and imported ambient animation (its
  library may prefix the name), set that `Animation.loop_mode` to
  `Animation.LOOP_LINEAR`, then call `AnimationPlayer.play(imported_name)`.
  In a Three.js consumer, use `mixer.clipAction(ambientClip).setLoop(LoopRepeat,
  Infinity).play()` and advance the mixer using elapsed seconds.
- Static consumers may omit playback and retain the authored rest. Consumers
  can choose per-instance starting phases to avoid synchronized lanterns; no
  runtime framework or game-repository patch is included here. Keep existing
  unit locomotion/one-shot policy separate from ambient playback.

### Building coverage

All rotations are restrained oscillations, not whole-building rocking or
continuous fast spins. Most spots turn ±2°; the academy's vertical crystal turn
is ±10°. The loom shuttle moves ±3.5 cm. Each spot uses one new empty pivot and
one animated transform channel (the shuttle's vector translation is three
scalar channels), preserving original mesh data and attachment rest transforms.

| Building | One animated spot; everything else stays fixed |
|---|---|
| Archery range | Small heraldic banner, borders and arrow relief sway together |
| Arrow tower | One hanging lantern rocks from its top hanger |
| Bakery | Existing warm entrance lantern rocks |
| Barracks | Small blue lookout flag pivots at its pole-side top edge |
| Bombarding tower | One lantern rocks; cannon, wheels and carriage stay fixed |
| Gold mine | One front hanging lantern rocks; cart and tracks stay fixed |
| Magic academy | Existing crown crystal turns gently about its vertical center |
| Metal mine | One lantern rocks; hoist, rope and loaded cart stay fixed |
| Research tower | Two connected armillary rings turn around their fixed center; telescope stays fixed |
| Stone cutter | Existing hoist hook sways under its fixed rope |
| Tavern | Beer sign and attached mug relief sway; bracket stays fixed |
| Town hall | Civic bell and its clapper rock slightly on their suspension |
| Trade market | Scales sign and its attached ornament sway together |
| Tree house | Blue banner and white tree relief breathe together below their top edge |
| Weaver | Existing loom shuttle travels across its loom; cloth/threads stay fixed |
| Woodcutter hut | Log sign and its relief sway; saw, supports and growth stay fixed |

### Water coverage

| Catalog IDs | Simple motion; preserved interface |
|---|---|
| `environment/components/forest_hex_stream` | Existing reflected-current strips drift ±2.5 cm along the channel; water body and north/south endpoints stay fixed |
| `environment/components/forest_foam` | Existing rings and beads drift ±1.2 cm together |
| `environment/components/forest_waterfall` | Existing broad/fine foam streaks drift ±8 mm sideways, remaining on the static falling sheet |
| `environment/hex_woodland_bridge`, `environment/hex_lantern_bridge` | The same three existing highlight categories move within their original local ownership; both bridge structures, river depth, banks and endpoints stay fixed |
| `environment/hex_river_overlay_{straight,turn_60,turn_120,end}` | One tiny interior shimmer strip drifts ±2.5 cm along the local centerline tangent; the entire original painted ribbon and its exact connector/occupation profile stay fixed |

The four otherwise single-mesh surface overlays need a small movable feature:
**one 10-vertex / 8-triangle strip each**, 22 cm long and 7 mm broad, with a
restrained related water shade, packed 512px Base Color/Roughness maps and UVs.
No receiving bank, original texture alpha, river mesh or endpoint moves. These
are **32 explicitly added triangle definitions and instances across the catalog**,
not unexplained geometry growth or a whole-surface oscillation. No other model
gets new mesh geometry or a new material. Repeated foliage/prototype datablocks
are not copied or made real.

## Preservation and evidence chain

1. [Palette authoring receipts](../vivid-palette/authored.json) bind the landed
   sources to the strictly preserved color checkpoint. The original serializer
   orphan-ID failure was causally resolved **before** this motion authoring.
2. [Motion authoring receipts](authored.json) bind those exact palette source
   hashes to the final sources, describing every new pivot, changed immediate
   parent, animated object/channel and the four small shimmer additions.
3. [Independent validation](validation.json) opens checkpoint and final saved
   sources separately: every original ID, geometry/UV/modifier/reuse/rig/action,
   object tag, collection membership, material slot/override, full shader values,
   and complete packed color/data maps survive. Only declared inserted pivot
   binds are allowed. All original world rest matrix entries are independently
   checked within `2e-6` (translation entries in meters) before normalization of
   floating-point bind noise for the structural fingerprint.
4. The audit imports **each of the 25 actual published GLBs**, evaluates mesh
   vertices at all five authored key times, checks movement and closed endpoints,
   confirms every fixed source object's world transform stays fixed, and compares
   source/export point clouds with a symmetric nearest-point bound of 0.1 mm.
   It does not treat a clip name or screenshot as proof of playback.
5. [Render receipts](renders.json) bind the current exports, renderer recipe,
   fixed crop camera and every PNG/GIF derivative. [The final color audit](../vivid-palette/preservation.json)
   composes checkpoint preservation with the independently verified motion stage;
   it does not falsely claim that the newly inserted pivots existed before.

The first broad style audit correctly rejected unpainted new shimmer materials.
Those four **new** materials received the required packed maps without modifying
any original material; their intermediate sources and failed logs were retained
under `.cache/ambient-motion/revision1/` and the original validation log. The
fixture failures were incomplete test-job metadata, not a production selection
failure: the canonical four-field selector contract and an existing passing
fixture were inspected before the bounded correction. Both selection modes and
rejection of unrelated geometry, color and parent regressions are exercised.

## Exact image preservation, not normalized-float hashes

Two chained audits disagreed on normalized float32 reads from unchanged packed
8-bit roughness PNGs. Separate-process comparisons and repeated reads showed that
process isolation alone does not eliminate the instability. The retained
[raw API probe](pixel-api-probe.json) records the observations, including one
8-ULP / `1.1920928955078125e-7` decoded-sample difference. **The underlying Blender
mechanism remains unproven**; this report does not assert a cache root cause.
Failed audits were not accepted as passes. [Retained failure evidence](diagnosis/README.md)
records the exact boundaries; full task-local snapshots remain available.

Under the explicitly approved narrow verification correction,
`tools/asset_pack/encoded_images.py` independently validates PNG chunk CRCs,
inflates and reverses all five PNG row filters, and compares **exact original
packed bytes/hash plus exact encoded samples and alpha**, dimensions, channel
count, bit depth, source type, alpha mode and image color-space. It performs no
float conversion, epsilon comparison, visual tolerance or re-encoding of an asset.
Material image identity, node routing, coordinate graphs, mapping inputs and
sampler/use-state are separately checked. All materials, including unused authored
variants, remain covered. Nonempty generated/unpacked/float maps, other encodings,
unsupported bit depths or interlacing fail explicitly instead of disappearing
from coverage. Empty Render Result placeholders and nonpersistent compositor
Viewer buffers are explicitly inventoried as presentation IDs, with exact metadata
and a required **zero-ID-user dependency check**. They are not texture maps or
persisted pixel payloads. A fixture deliberately binds either buffer as a texture
and requires failure, so this classification cannot hide an unsupported map.

[Real-source controls](encoded-map-controls.json) bind separately loaded
baseline/palette/final images for both originally failing examples, with repeated
identical-map reads and real one-sample mutations. The Blender fixture also checks
that identical samples bound to a different image, changed color-space, mapping,
channel routing or mute state are rejected. The fast decoder fixtures exercise
all five PNG filters, exact alpha, one-byte content changes, unsupported cases and
identical samples with different packed bytes. Complete per-source/per-map encoded
proofs—not only the first two examples—are retained in
[the final 67-source audit](../vivid-palette/preservation.json) and the 23-source
motion audit. No existing material, texture, model or export was altered to fix
the read-method issue.

Rendered PNG metadata is frame-specific, and rendering is not promised bitwise
deterministic: 24 of 25 endpoint image pairs have identical decoded pixels; the
straight overlay pair differs by one encoded level in 21 rendered pixels. This is
not used as a tolerance or a source-data preservation claim. Loop closure is checked
on the actual source/imported GLB mesh vertices at the two endpoints, not inferred
from equal PNG file bytes. Every actual image/derivative retains its own exact hash.

The metal-mine renderer once crashed during Blender shutdown after writing its
poses; those files alone were **not** accepted. The original failure log remains
`.cache/ambient-motion/metal-mine-render-shutdown.log`. A clean task-owned retry
exited successfully and the final complete pose/camera/derivative hashes are bound
in `renders.json` to a successful worker. There was no shutdown-crash waiver.

## Reproduce checks and review

Use the already-installed Blender explicitly if it is not on PATH:

```sh
BLENDER=/home/bart/.local/opt/blender-5.2.2-linux-x64/blender
UV_OFFLINE=1 mise run check
python3 -m tools.asset_pack.worker tools/asset_pack/test_ambient_blender.py \
  --label ambient-fixtures-corrected --blender "$BLENDER"
python3 -m tools.asset_pack.check --all --blender "$BLENDER"
python3 -m tools.asset_pack.worker tools/asset_pack/verify_ambient_blender.py \
  --label ambient-preservation-playback --blender "$BLENDER"
python3 -m tools.asset_pack.worker tools/asset_pack/verify_vivid_blender.py \
  --label ambient-vivid-chain --blender "$BLENDER"
python3 -m tools.asset_pack.worker tools/asset_pack/verify_style_blender.py --all \
  --label ambient-style --blender "$BLENDER"
python3 - "$BLENDER" <<'PY'
import sys
from pathlib import Path
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_pack.worker import run_blender
root = Path.cwd()
run_blender('tools/asset_pack/verify_painted_blender.py',
    [job['id'] for job in plan_exports(root)], root=root,
    label='ambient-painted', blender=sys.argv[1])
PY
python3 -m tools.asset_pack.worker tools/asset_pack/verify_forest_blender.py \
  --label ambient-forest --blender "$BLENDER"
python3 -m tools.asset_pack.vivid_review --render --blender "$BLENDER"
python3 -m tools.asset_pack.ambient_review --render --blender "$BLENDER"
python3 -m tools.asset_catalog build
```

Verification uses byte-bound, task-local checkpoints. On a fresh checkout,
reconstruct the palette-stage source files from `ac41b74` into
`.cache/ambient-motion/before/<source-path>` using the paths and hashes in
`authored.json`; reconstruct the original landed baseline as described in the
[vivid recovery procedure](../vivid-palette/README.md). Never rebuild source
geometry to recreate a comparison. `ambient_motion.py` is explicit authoring,
not a check. It always plans the complete `ASSETS` inventory: all 16 buildings
and nine water entries. Neither its Python entry point nor its CLI accepts an
asset selector. Source-level completion is recorded only after all selected
collections in that source have been authored and audited together; in particular,
`shared_forest_kit.blend` covers the stream, foam and waterfall in one operation.
A repeat invocation keeps already bound sources and refuses to silently overwrite
subsequent manual edits. An interrupted run resumes unfinished sources using the
same complete inventory, not a partial-asset mode.

For authorized authoring only (not verification), use the isolated worker without
asset arguments; `--help` describes its complete-inventory contract:

```sh
python3 -m tools.asset_pack.worker tools/asset_pack/ambient_motion.py \
  --label ambient-author --blender "$BLENDER"
```

The fast orchestration regressions run without Blender:

```sh
python3 -m unittest tools.asset_pack.test_ambient_motion
```

They exercise real catalog job planning, shared-source feature coverage, persisted
source receipts, complete-run and interrupted-run resume, manual-edit refusal,
and CLI argument handling with Blender authoring/auditing replaced by test doubles.
The Blender fixtures and independent playback audit above remain the geometry,
material-preservation and exported-motion checks.

The catalog's hash-only “shared kit changed” advisories are expected after
library source edits. They are not permission to regenerate planted compositions.
The independent forest checks assess actual shared mesh/material/grid consistency
at rest. Non-water component exports remain static; a shared source's ambient
slots do not justify leaking clips into unrelated collection selections.

[Checks and final resource accounting](checks.json) bind completed commands and
current artifact hashes. All review here is standalone CPU asset/browser
inspection. **Game import, actual-game camera/playback, GPU cost and artist
acceptance remain separate queued work**, not acceptance claimed by these checks.
