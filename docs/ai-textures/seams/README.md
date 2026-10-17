# Bounded painted-ground correction

Open **[review.html](review.html)** offline. It compares the original GLBs, the
initial delivered paint, and this correction, with identical cameras/lights/color
management. Lead with the six repeated/mixed grids, then examine the material
close-ups and connected path/river views. [Comparisons and resources](comparisons.json)
contain exact per-image/per-asset hashes and settings.

**Assets-side correction implemented; actual-game acceptance is still pending.**
This is not permission to ship the rejected appearance by documenting it. The
retained RX6800 observations establish the problem, not successor acceptance.
The separate game task must import the immutable successor **after asset-main
landing**, retain original/delivered comparisons, and judge settlement, forest,
mixed, connected path and river views again. No game source/output was modified.

## Diagnosis from actual pixels

Read-only evidence inspected in the game worker's
`/home/bart/.treehouse/odot-game-b83784/1/odot-game/docs/ai-textures-game/`:
`before/` and `after/` settlement, menu-texture-forest and menu-texture-mixed PNGs,
plus `settlement-pair.png`, README and evidence JSON. [game-diagnosis.json](game-diagnosis.json)
records those exact input revisions, native camera/graphics settings, paths and
hashes. They are original/RX6800 delivered captures, **not renders of this correction**.
The finding motivating the correction was retained at
`/home/bart/projects/personal/firstmate/data/odot-ai-textures-game/nm-01M53N1KBASX7B5AF0CCH9HJGC-findings.txt`.

Three bounded causes were visible and reproducible in matched GLB views:

1. **Baked border modulation:** the former .18m transition replaced the paint with
   one constant dark olive color, independent of each family's body luminance.
   It outlined adjacent same-material cells as well as mixed ones. No shader,
   material scalar, placement gap or new geometry was needed to reproduce it.
2. **Feature scale / whole-swatch repetition:** one illustration covered one tile.
   Large identical pale slabs, daisies and corner leaves were landmarks at the
   same positions on every tile. The native inputs are only ~135–171px enlarged
   to 1024; the moss input even includes an illustrated dark frame at the left.
3. **Palette/readability:** supplied art shifted the source family means and
   made pine duff nearly the same image as leaf litter. It was not caused by a
   changed material Base Color factor: source defaults and non-color channels
   were preserved and remain protected.

The original procedural floor was itself visibly repetitive, but quieter. Merely
restoring its repeating cushion circles or removing all supplied paint would not
meet the requested correction. Nor would hiding ground under more foliage.

## Small source-preserving fix

Only five Base Color image bindings change, on
`hex_ground_{moss,grass,dirt,leaf_litter,pine_duff}`. Original materials, slot modes,
source UV coordinates, tangent normal nodes, roughness, material defaults,
geometry/topology, normals, tile origins, hex dimensions and animations survive.
No builders, terrain shader, runtime randomizer, neighbor metadata or new mesh is
introduced. Radius remains 2.55; top Z=0; bottom Z=-.36.

`ai_texture_blender.ground_detail()` prepares one portable color image per family:

- Exclude the outer 8.5% of the supplied illustration, avoiding the atlas frame.
- Bake smaller quarter-turned/flipped copies with broad overlapping feathered
  weights; spacing .28 and extent .48 in existing map coordinates. This reduces
  motif scale without producing a sharp square UV-repeat boundary. Deterministic
  offsets use seed 418. Native detail is retained, not replaced with noise.
- Match the family mean primarily to its original authored central color (80%),
  retaining 20% supplied mean and 80% painted contrast. Fine painted flowers,
  leaves, stones and grass remain visible. Original circular stamp composition
  is not superimposed again.
- Across a .48m edge band, shift hue only 20% toward related olive/humus at the
  **same luminance as the family body**; retain 85% of local detail. This is not a
  constant dark line or a smooth featureless perimeter. A first private trial
  used a stronger shared hue; inspection exposed pale green seams on dirt, so
  the final mix was reduced before final export/review.

All settings live in `art_style.AI_TEXTURE`; the existing content-keyed image
owner namespace remains `ai_texture_poc_v1`. New names carry new prepared-pixel
hashes, not a stale name-only cache hit. The strict exact-source guard was not
weakened. All original and initially delivered packed images remain unchanged;
unused originally delivered owned predecessor maps are explicitly verified as
source-only fake-user images, never additional GLB dependencies. The five rejected
private-edge-trial maps and their exact packed-source copies were preserved in a
verified owner-only archive before removing only those trial datablocks and
external companions from delivery. No original or previously delivered map was
removed; [review-r1-cleanup.json](review-r1-cleanup.json) binds the scoped change.
New Base Color images are sRGB. Existing Roughness/Normal maps stay Non-Color,
with the original tangent-space Normal Map connections.

**The four path, four river and Archery GLBs and sources are byte-for-byte
unchanged from the initial delivery.** The shared foundation material and its
packed maps are unchanged inside the five resaved base-ground sources; it has no
separate source or GLB. These mapping/animation contracts need no further change
to remove the base-ground dark outline. They are included in refreshed
preservation/ground checks and the handoff, not silently rebuilt.
Ribbon U-across/V-along, banks, endpoint paint, widths and moving shimmer survive.
The existing quiet-to-detailed bands in paths are still a limitation of the first
POC, not a new ground-boundary fix or justification for an unrelated redesign.

## Image inspection / acceptance conclusions

Implementation-worker visual judgment, not an automated pass or GPU acceptance:

| Surface/view | Original → delivered → correction |
| --- | --- |
| Moss repeated neighbors | Original cushion islands repeat; delivered pale slabs repeat at whole-tile size with a dark border. Correction keeps painted moss/stone structure at smaller scale and removes the conspicuous enclosing dark line. At close range the overlapped illustration is softer, not new high-resolution relief. |
| Grass repeated neighbors | Large identical daisies no longer dominate each tile center. Smaller flowers/blade strokes remain. The continuous field is visibly better at the representative overview size; a careful search can still find the same baked image on every identically oriented tile. |
| Dirt repeated neighbors | Warm pebbled earth remains readable; large pebble landmarks and the dark olive perimeter are less dominant. More small pebbles increase local density. The final weak hue blend avoids the first trial's greenish outline. |
| Leaf litter | Smaller overlapping leaf marks retain painted warmth without one large leaf arrangement owning an entire tile. Fine close-view softness remains. |
| Pine duff | Original darker family mean recovers some separation from leaf litter. Input art still contains broad leaves, not a convincing pine-needle painting: no claim of production pine-specific identity. |
| Mixed same-scale grid | Material identity/hue changes remain visible (intentional); the added thin dark grid is gone. A fixed texture cannot know its actual neighbor, so dissimilar family boundaries are not perfectly continuous. No square patch boundaries were observed. |
| Mixed path and connected river | Ground no longer contributes the strong dark perimeter, while the exact existing ribbons and banks remain readable. Original connector/detail-density compromises remain visible close up. Water motion is preserved by exact animation/sample proofs, not inferred from a static render. |
| Representative scale | Six-cell grids display roughly 100px per tile in the desktop gallery, isolated tiles roughly 260px, spanning retained game overview/close-up scales. These are approximate pixel-size diagnostics, not calibrated game captures. Painted detail is not simply erased; the worst giant repeated landmarks are less conspicuous. |

**Conclusion:** the matched GLBs demonstrate a material reduction in the reported
border/whole-tile-landmark regression, with useful painted detail preserved.
One immutable image per material necessarily repeats; elimination of all repeat
would require variants or runtime mapping outside this bounded correction. This
work does **not** authorize conspicuous regression in game or claim the strongest
criterion is already met. Reopen actual GPU acceptance on the landed content set.

## Evidence and resource deltas

- Original baseline: `133c7cdeb368cada408d1c95c9414e08488371a9`; original PNGs and
  hashes remain in `../renders/before`, `../baseline.json` and original audits.
- Initially delivered baseline: `2d88d355393f145aedfc19fa198960dac741c6fb`, delivered
  at https://github.com/seraph1nia/odot-game-assets/pull/14.
  [baseline.json](baseline.json) binds all fourteen source/export predecessors.
  `pr14/` retains its original actual GLB PNGs/profiles unmodified, and the
  `pr14-*.json` records are historical receipts, **not current-source passes**.
- Correction: exact current GLB hashes/content-set identity in
  [../handoff.json](../handoff.json). No guessed future merge revision is used.
- 35 original-review terrain triples (five floor families and close-ups, all
  eight overlays, connected neighbors, mixed path/river), plus six new repeated/
  mixed-grid triples. The new grid worker renders all three revisions rather
  than relabeling earlier images. Identical 24-sample CPU Cycles, four threads,
  Area lights, AgX/Medium High Contrast, camera, framing and frame 1 are recorded.
- [../validation.json](../validation.json) now independently checks both the
  original and immediate delivered predecessor. All previous packed maps, all
  other source state, GLB triangle corners/normals/UVs, non-color channels and
  animation targets/samples must match. The immediate-source signature is
  normalized only for the five declared Base Color image bindings.
- Generated [comparisons.json](comparisons.json) owns per-terrain-asset byte and
  decoded-image deltas from the initial delivery; [../resources.json](../resources.json)
  owns current sizes for the full set, including Archery and editable sources after
  excluding the privately archived trial maps. Export growth is confined to the
  five base GLBs; image count, decoded RGBA8 estimate (no mips) and
  triangle/material/mesh counts remain unchanged from delivered exports.
  Historical source sizes are in [pr14-resources.json](pr14-resources.json), not
  current-source measurements. More detailed PNGs compress less; retained
  original/delivered source-only predecessors are not
  loaded by the GLBs. No GPU-time or FPS claim is made from CPU renders.
- [checks.json](checks.json) records actual current-source commands/results;
  current-source receipts are regenerated after the cleanup save/export. Earlier
  executions remain anchored to their exact pre-cleanup revision in
  [review-r1-before-checks.json](review-r1-before-checks.json), rather than relabeled
  as current passes. Unchanged GLB renders retain their original execution profiles
  and pixel hashes; refreshed galleries bind them to the new source content set.

## Reproduce / review / rollback

Use existing pinned Blender 5.2.2 LTS/workers; no installs. Keep desktop Blender
for review. Never run an old builder or overwrite a manually edited source.

To inspect/reapply this delivered correction, use an isolated copy with its
committed sources/maps. First reconstruct both predecessor caches as described
below and obtain a verified original audit via the
[original-cache audit procedure](../README.md#reproduce-without-rebuilding-geometry).
Keep the delivered predecessor images in the current sources: the final recipe
alone cannot recreate those historical maps from original-only sources.
The verifier also reads local applied receipts for all fourteen assets, including
unchanged overlays and Archery. The first command reconstructs missing receipts
from committed validation data only after checking exact current source hashes;
it refuses stale existing receipts rather than overwriting them.

```sh
python3 - <<'PY'
import json
from pathlib import Path
from tools.asset_pack.ai_texture_contract import ASSETS, sha

validation = json.loads(Path('docs/ai-textures/validation.json').read_text())
receipts = Path('.cache/ai-textures/applied')
receipts.mkdir(parents=True, exist_ok=True)
for aid in ASSETS:
    row = validation['assets'][aid]
    current = sha(Path('sources') / (aid + '.blend'))
    assert current == row['source_after_sha256'], (aid, 'unrecognized source bytes')
    path = receipts / (aid.replace('/', '_') + '.json')
    if path.exists():
        receipt = json.loads(path.read_text())
        assert receipt['id'] == aid and receipt['source_sha256'] == current, (aid, 'stale local receipt')
    else:
        path.write_text(json.dumps({'id': aid, 'source_sha256': current,
                                    'materials': row['materials']}, indent=2) + '\n')
PY
BASES='environment/hex_ground_moss environment/hex_ground_grass environment/hex_ground_dirt environment/hex_ground_leaf_litter environment/hex_ground_pine_duff'
IDS="$(python3 -c 'from tools.asset_pack.hex_ground import IDS; print(" ".join(IDS))')"
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_blender.py --label seams-idempotence idempotence $BASES
python3 -m tools.asset_pack.check $BASES
python3 -m tools.asset_pack.worker tools/asset_pack/verify_ai_textures_blender.py --label seams-preservation
python3 -m tools.asset_pack.worker tools/asset_pack/verify_style_blender.py --label seams-style $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/verify_painted_blender.py --label seams-painted $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/verify_ground_blender.py --label seams-ground --output docs/ai-textures/ground-verification.json
python3 -m tools.asset_pack.worker tools/asset_pack/test_ai_textures_blender.py --label seams-fixtures
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_review.py --label seams-after after $IDS mixed neighbors
for stage in before pr14 after; do
  python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_seams_review.py --label seams-grid-$stage $stage
done
python3 -m tools.asset_pack.ai_texture_report
python3 -m tools.asset_pack.ai_texture_seams_report
mise run check
```

Before any current→successor application, retain the exact delivered
bytes and applied receipt; the local last-applied receipt takes precedence over
committed receipt data and refuses unknown later edits. For reconstruction from
Git, populate `.cache/ai-textures-seams/pr14/{sources,exports}` from the full
`2d88d355393f145aedfc19fa198960dac741c6fb` Git objects and verify `baseline.json`
hashes; do not copy into production sources. Populate the original cache from
`133c7cdeb368cada408d1c95c9414e08488371a9` the same way. `audit-baseline` opens only
those verified original copies. Never weaken the current-source guard or treat
an intervening manual material edit as an owned predecessor.
Reapplication saves .blend bytes even when semantics are idempotent: always rerun
export/check/report afterward; old handoff/source hashes must not be reused.

Rollback is a coherent Git revert of this bounded correction, keeping all later
manual edits. That restores the delivered source/maps/export/receipt content set,
not an unrelated Archery or terrain builder. If the correction was imported, the
game task separately restores its prior immutable assets-main pin and matching
manifest/dependencies together; it must never import an unpublished branch, swap
GLBs under an old pin, or declare GPU acceptance from these source-review images.
