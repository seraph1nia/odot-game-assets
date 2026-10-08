# Quality round — first static review checkpoint

**Work in progress, not whole-catalog acceptance or a shipping handoff.**
Authoring/static reviewer: implementation worker. Standard: merged skill at
`e929786`. The exact baseline revision is recorded in
[baseline.json](baseline.json). All 105 canonical IDs
are inventoried there using catalog precedence, not a replacement manifest.
The 473 original files remain in `.cache/quality-round/before/`; their SHA-256s
are recorded. Original references, external PNG maps, selectors and associations
have not been edited. No reference derivatives are included in this evidence.

## First reviewed batch: five painted buildings

The source art comparison is **before on the left, after on the right**.
These are fresh renders of the preserved baseline sources and authored sources,
not old thumbnails relabeled as a matched comparison. Full original before PNGs
are in [evidence/before/](evidence/before/); full after PNGs are the corresponding
`exports/previews/<name>.png`. Each source remains
`sources/buildings/<name>.blend`; each export remains
`exports/buildings/<name>.glb`. The existing collection/root selectors apply.

| Canonical ID / supplied reference | Predeclared deficiency and authored change | Static judgment / remaining limitation | Evidence |
| --- | --- | --- | --- |
| `buildings/archery_range` / [B1](../../sources/reference/more_buildings/low_poly_fantasy_archery_range.png), C-ROOF | D01: lookout roof was below the main ridge, its open platform largely merged into the cottage roof. Changed only the lookout composition root from uniform `.72` to `(.82,.82,.96)`, keeping its foundation at Z=0. D04: aligned diagonal beam grain to actual baked timber length; removed redundant fine grain/scratch tubes while retaining major joints, pegs and shingle seams. | Clearer tall open lookout and flag at 192 and 96-pixel image boxes. Bow/target/entrance remain separate. Rafters have quiet longitudinal grain rather than transverse bands. The lookout is a taller authored interpretation, not a measured copy of B1. It still uses a masonry support rather than the reference's entirely timber-led upper support. | [480](evidence/archery_range-480.jpg), [192](evidence/archery_range-192.jpg), [96](evidence/archery_range-96.jpg) |
| `buildings/research_tower` / [B2](../../sources/reference/more_buildings/fantasy_observatory_cottage_diorama.png) | D04: crosswise bands on sloped cottage rafters distracted from the dome/telescope. Aligned existing UV V to the timber's geometric principal axis on unique diagonal cuboids; removed fine grain/scratch meshes already supported by packed maps. | Cleaner uninterrupted warm roof braces at 480, subtler at 192; dome/telescope/armillary silhouette and palette retained. No new role-recognition gain is claimed. At 96 the surface correction is not reliably distinguishable. Broad dome ribs remain more dominant than B2. | [480](evidence/research_tower-480.jpg), [192](evidence/research_tower-192.jpg), [96](evidence/research_tower-96.jpg) |
| `buildings/metal_mine` / [B3](../../sources/reference/more_buildings/low_poly_medieval_iron_mine_diorama.png) | D04: corrected diagonal rafter/support UV grain and removed duplicate microscopic grain/scratch geometry. Ore/cart/hoist, rail joints and large timbers were retained. | The office's roof edge reads as wood rather than a striped decoration at 480; improvement is subtle at 192 and unclaimed at 96. The dark tunnel/loaded cart still identify the mine. Large ore outcrops remain plainer than B3; this checkpoint does not claim the rock mass is fully reference-refined. | [480](evidence/metal_mine-480.jpg), [192](evidence/metal_mine-192.jpg), [96](evidence/metal_mine-96.jpg) |
| `buildings/weaver` / [B4](../../sources/reference/more_buildings/cozy_fantasy_weaver_s_workshop.png) | D04: corrected diagonal timber grain and removed redundant tiny grain/scratches. Existing blue/cream canopy, loom threads, cloth rolls and woven sign were preserved. | Less transverse rafter noise at 480, subtle at 192; no role/proportion change. The baseline source already has a blue canopy. Initial portable review proved both pre-fix GLBs assigned red despite source blue OBJECT slots; the corrected current export now delivers blue/cream. This is a real consumer-fidelity correction, **not** a newly authored source palette or merely a stale thumbnail. Loom remains relatively small, and the cottage mass is simpler than B4. | [480](evidence/weaver-480.jpg), [192](evidence/weaver-192.jpg), [96](evidence/weaver-96.jpg) |
| `buildings/town_hall` / [B5](../../sources/reference/more_buildings/fantasy_town_hall_diorama.png) | D04: corrected unique diagonal beams' UV grain; removed duplicate fine marks. D01 iteration 2: wing roots X `±1.12` → `±1.38`, Y `.28` → `.38`, Z scale `.88` → `.80`, retaining crown/bell/entry and ground contact. | The right wing's roof/body now separate below the central civic gable, with a wider tiered silhouette at 480/192. Central crown/bell remain dominant. Left wing remains partly occluded in this saved view; not an exact B5 reconstruction or a claimed 96-pixel role gain. Triangle cost remains high. | [480](evidence/town_hall-480.jpg), [192](evidence/town_hall-192.jpg), [96](evidence/town_hall-96.jpg) |

D01 gain is substantial for archery range; town hall iteration 2 improves civic
mass separation more modestly. Research tower, mine and weaver are restrained D04
craftsmanship improvements, **not** five silhouette upgrades. Their 96-pixel
results preserve appearance rather than establish small-game readability gains.
No numerical resemblance/recognition score or game occupied-size is invented.

### Matched presentation and map preservation

[profiles.json](profiles.json) records actual source hashes, camera matrices,
lights, frame/FPS, image dimensions, exposure/view transform/look, compositor,
and projected geometric occupied height. For all 18 completed comparisons the
saved before/after presentation fields are identical. The five building scenes
use their saved Cycles 1200×1200, 64-sample, AgX / Medium High Contrast setup;
no lights, exposure, camera, sample preset or global style version were migrated.
The 480/192/96 boxes are ImageMagick downscales of these whole frames, not actual
game sizes. Projected before/after heights in the 1200-pixel image are:

- Archery range: 875.7 → 960.6 px, because its lookout is taller.
- Research tower: 869.3 → 869.3 px.
- Metal mine: 817.6 → 817.6 px.
- Weaver: 906.8 → 906.8 px.
- Town hall: 1094.9 → 1094.9 px.

These are projected mesh-vertex extents including display terrain, not alpha
segmentation, and scale proportionally within the provisional boxes.
Reference lighting is unknown. Comparison establishes structural/surface
relationships, not calibrated reference albedo.

Every retained image used by the authored scene has unchanged packed PNG bytes.
The removed stair-scratch-only `painted_stone_dark_color` is no longer used in
archery range/town hall; its external map and original packed source are preserved.
Blender saves also omit pre-existing unused orphan images from some sources;
those are retained in the baseline backups and are not a repainted map revision.
No map generation, global palette or texture version change occurred.

### Measured building resource costs

Unique GLB mesh-primitive triangles, material/image definitions and actual file
bytes; not instance-expanded triangles, renderer draw calls, GPU memory or FPS.
Full source/export bindings and before/after GLB hashes: [resources.json](resources.json).

| ID | Triangles before → after | Materials | Images | Byte delta |
| --- | ---: | ---: | ---: | ---: |
| `buildings/archery_range` | 41,298 → 40,838 | 38 → 37 | 31 → 30 | -178,664 |
| `buildings/metal_mine` | 36,248 → 35,968 | 35 → 35 | 32 → 32 | -29,168 |
| `buildings/research_tower` | 41,962 → 41,742 | 36 → 36 | 32 → 32 | -22,844 |
| `buildings/town_hall` | 88,355 → 87,575 | 30 → 29 | 31 → 30 | -210,416 |
| `buildings/weaver` | 38,908 → 38,688 | 33 → 33 | 32 → 32 | -22,580 |

Removal of redundant fine mark meshes explains the triangle decrease; absent
scratch-only material/image definitions explain the larger archery/hall byte
savings. The enlarged lookout reuses the same mesh data and adds no triangles.
None of these changes establishes consumer performance improvements.

### Mechanical evidence, distinct from visual judgment

Runtime verified: Blender **5.2.2 LTS**, build `d13f752e3b9c`.

- `UV_OFFLINE=1 mise run check`: 47 tests, Python lint and Python/JS syntax passed,
  using the already cached pinned Ruff; no installation/upgrade.
- Selected `tools.asset_pack.check`: authored sources exported and verified;
  five buildings, 11 dependent forest tiles, four selected forest components,
  knight, evil ranged unit and crossbow have current selected check records.
- `verify_style_blender.py --all`: all 105 authored catalog selections passed.
- `verify_painted_blender.py`: selected 20 painted building/forest IDs passed
  UV/packed/source/embedded-channel checks.
- `verify_forest_blender.py`: all 11 forest tiles passed footprint, base/river
  endpoint and fresh embedded-prototype geometry checks.
- Attachment fixtures passed. They do not certify motion appeal.

Full isolated worker logs remain `.cache/asset-check/logs/quality-*.log`.
Current source/export hash-bound mechanical results remain
`exports/validation.json`; none substitutes for missing visual evidence.

## Completed selected static evidence — portable acceptance remains open

Both original workers remain **failed partial jobs**: they completed the same
15 IDs, then raised `KeyError: 'hex_hollow_watchers'` in reference-only `BY_ID`.
The minimal route correction reuses the catalog export planner's authoritative
source ownership. A behavioral test reproduced that exact failure before the fix;
seven selection regressions now pass, including ordinary IDs and unknown/ambiguous
refusal before opening sources. [render-selection.json](render-selection.json)
binds actual before/current identities and hashes. All 473 originals were rehashed.

Only the three missing dreaming pairs and two iteration-2 after views were then
rendered. The original 15 before views and 13 still-current after views were reused;
the other two original after views/sources are preserved as iteration-1 evidence.
The new workers passed in 188.74 s and 260.52 s, respectively. Original nonzero
verdicts/logs remain in [render-outcome.json](render-outcome.json), alongside new
completed lists and artifact hashes. No whole-catalog rerender or source rebuild.

Current town hall and ranged evidence/profiles/resources now bind **iteration 2**,
not its rejected predecessor. Existing selected source/export checks passed for
both; all five remaining source selections passed style checks. The 18 matched
saved presentation profiles and retained used map buffers were reverified.

[Forest and unit static review](forest-units.md) records visible gains, genuinely
incidental changes and remaining limits. Prototype propagation was inspected from
`kit_asset`/`kit_source` tags and original geometry before changing named meshes;
no companion library, manual composition, maps or rig curves were regenerated.
The crossbow feather closure preserves standalone/equipped grip pivots and scale.
Skeleton/action/loop/socket interfaces remain; no normal-speed or portable glow
acceptance is inferred from stills.

### Browser review — scheduling resolved; portable palette defect remains

The missing-runtime diagnosis below is historical. Following explicit steering
`004.msg`, a task-private official Chrome for Testing **155.0.8059.39** was
installed without tool upgrades, global configuration changes or sandbox bypass.
Its 0700 profile/owned PID/loopback CDP endpoint and existing named AXI bridge were
verified. Successful about:blank snapshot/evaluation reports **ANGLE SwiftShader
software WebGL**, not hardware-GPU or performance evidence. Private setup evidence
is `.cache/quality-round/browser/setup.json`.

The current knight GLB actually loaded and exposed all six clips. Two UID-scoped
captures failed with `STALE_REF`; those exact errors remain privately preserved.
Steering `005.msg` authorized the existing UID-free full-page screenshot route,
which succeeded. The unmodified raw PNG remains private because its UI contains
supplied references. [Current portable knight](evidence/portable/knight-current.png)
is the entire measured viewer rectangle, rounded outward without rescaling,
masking or selective geometry cropping. Coordinates, raw/crop dimensions/hashes,
source/GLB hash and camera/clip/light context are in private
`.cache/quality-round/browser/knight-current-capture.json`. It is a current-only
diagnostic, **not yet a matched portable before/after gain**.

Those initial native recordings yielded only one/two decoded frames in 1.5 seconds
and two animation-frame callbacks over 2.1 seconds. Steering `006.msg` authorized
one private scheduling adjustment using three existing documented nonsecurity
flags, preserving runtime/profile/viewport/SwiftShader. The single new diagnostic
observed 126 callbacks and the walk pilot yielded 14 real frames. Old failures and
sparse videos remain; no causal mechanism or native GPU performance is inferred.

[Portable review](portable-review.md) now records 27 matched GLB pairs, four
emission/form on/off cases and 60 actual 1× six-clip recordings, with source/GLB
bindings and software limits. Existing source rigs/NLA/action keys/weights/bindings
are unchanged; only the two named unit geometry candidates and collar assignment
changed. No whole-catalog art or motion improvement is inferred from these checks.

The genuine serialization defect—effective OBJECT slots lost by applied-modifier
mesh conversion—is corrected in the existing selected exporter for exactly six
proven IDs. Seven executed fixtures and 24 combined style/export fixtures pass;
source palettes/data are not overwritten. Current Weaver blue/cream and ranged red
neck/steel body now match source. Four affected-unit appearance sets (24 clips)
were refreshed; old wrong-palette profiles/videos remain historical. [Fidelity](export-fidelity.md)
discloses exact geometry/rig/animation mappings versus Weaver's tiny finite semantic
UV differences; no exact-byte UV/source rewrite or native performance claim.

#### Historical missing-Chrome diagnosis

The task-owned AXI session `odot-assets-quality-iteration` at derived port 9954
was confirmed by its shallow health response. Its deep health reason is:

> Could not find Google Chrome executable for channel 'stable' at:
>  - /opt/google/chrome/chrome.

This is **not** evidence that an attached Chrome exited. The bridge wraps a
missing-executable tool error as `BRIDGE_NOT_READY`. The existing cached MCP
supports executable selection, but AXI's documented launcher does not expose an
executable-path setting, and no installed supported Chrome channel was found on
PATH. No new dependency, security flag disable, personal profile, shared endpoint
or fallback browser harness was used during that earlier diagnosis. The later
approved private-runtime setup resolved it; the later scheduling and material
serialization findings above supersede that setup diagnosis. Still-source evidence is unchanged.

No whole-catalog completion, PR, release or game integration is claimed here.
