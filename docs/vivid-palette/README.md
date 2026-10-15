# Vivid painted color recovery

Current direction supersedes the rejected grey/desaturated material treatment,
not the landed organic overgrowth or selective quality refinements. Baseline is
`cfdb114`. The first and second overhaul ledgers remain historical read-only
records; their hashes are not current acceptance bindings.

The additional authorized [localized-motion delivery](../ambient-motion/README.md)
adds actual `ambient` clips to all 16 buildings and nine water entries. The color
checkpoint is `ac41b74`; neutral pairs below record the detailed exports landed at
`9a69b514`. Motion has separate strict preservation, playback and evidence receipts.
Those render/count ledgers are now immutable historical snapshots, not current
optimized-export bindings; see the [runtime successor record](../runtime-optimization/README.md)
for current comparisons and verification.

## Reference-led observations and implementation

The original supplied village board has blue/terracotta roofs, honey timber,
yellow-green foliage, blue/gold knight and violet mage. The original mushroom
reference separates blue/violet caps, cyan undersides and living greens.
These illustrations inform hue relationships, not exact albedo samples. W0
continues to inform planted roots, layered roof growth and working identities;
its grey palette is no longer the target. No new reference images are acquired.

Actual pre-greying saved materials and packed maps are compared with current
materials before authoring. Restore selected original color channels, retain
current roughness/normal maps, low form-preserving emission and all geometry.
Explicitly recolor the added moss/ivy/lichen/cloth and bakery shelter roles.
Soft broad hue washes, fine leaf veins and quiet grain remain subordinate to
existing painted contacts, facets and working detail. Do not apply a global
saturation slider, replace entire historical sources, rebuild kits, or grade
rendered previews to conceal unchanged material colors.

## Actual review and retained/refined accounting

[Actual comparisons](actual-review.html) contain twelve representative model pairs,
96px canvas companions, two native UI pairs and eleven full-catalog sheets.
[Inventory](inventory.json): **133 assessed; 128 refined, five retained**. All
118 models recover selected material channels; only ten native views inherit
changed ornament pixels. The seal, city navigation, match controls, session
feedback and roster views retain identical pixels. Per-ID material lists are
filtered to each exported selection, not every material in a shared owner.

Implementation-agent inspection covered all nine current 3D paired sheets and
both current native sheets, plus full focal building/unit/forest and HUD/Worldtree
captures. Original supplied village and mushroom pictures informed relationships;
[actual saved-material comparisons](material-comparison.json) establish that this
is color recovery in source, not preview grading. Illustrations are inspiration;
current actual exports, checks and agent judgments are iteration evidence, not
commissioned artist acceptance.

| Family / focal examples | Agent judgment | Retained quality and limits |
| --- | --- | --- |
| Buildings: woodcutter, bakery, weaver, academy | Blue roofs and warm timber separate again from living green growth; bakery's terracotta/ochre shelter and woven blue/cream cloth recover role color. | Dense roof/contact growth, saw teeth/pulley, shaped bakery crown, folded cloth, civic bell and shaded armillary orb all survive. Fine paint is close-view detail, not a new small-scale geometry cue. |
| Units/equipment: knight, mage, evil units | Blue/gold, violet and enemy red/purple recover faction separation without making dark armor bright primary paint. | Faces, grips, portable equipment, original socket fixes and six in-place clips survive; stills do not qualify motion appeal. |
| Forest components/tiles | Blue/violet caps and cyan crystals separate from greens; snail shell/teal body and butterfly hues recover distinct identities. | Planted foliage density and shared leaf/moss meshes survive. Low luminous strengths retain shaded colored bodies, not glowing disks. |
| Floors, paths, rivers | Green floors, ochre leaf litter and teal streams recover coherent hue distinctions while retaining gentle painted variation. | Flat occupied planes, alpha, channel width/heights and endpoints stay unchanged. Ground remains support, not uniformly saturated noise. |
| Props | Warm shafts, straps, crates and handles distinguish metal/tool parts; heraldic signals recover blue/red and gold. | Original functional silhouettes, wraps, relief, root/grip ownership and prototype reuse remain unchanged. |
| Native UI | Parchment, leaves and violet ornament regain color while readable dark panels and existing state hierarchy stay intact. | Six SVG palettes only; all path geometry, opacity, native code/layout/theme metrics, APIs, topology and original seal bytes retained. |

The color-only checkpoint retains all original geometry/material/animation
counts. The final cohesive delivery preserves all original geometry and skin
joint counts, adds 25 explicitly inventoried ambient clips and sixteen detail
pivots, plus exactly four new water-shimmer mesh/material definitions and instances
(**32 triangle definitions/instances total**). No other geometry grows. Counts
and export bytes are recorded in `renders.json::facts` and `summary.json`;
packed color companions, persistent orphan source data and the small clips/maps
are costs, not GPU performance claims. The [serialization diagnosis](diagnosis/README.md) explains
why zero-user authored variants/prototypes now have fake-user persistence rather
than being lost on ordinary saves. Independent read-only comparison covers every
saved source, including those unused authored IDs.

## Evidence ownership

`baseline.json` binds all 118 model IDs and 67 saved source owners before editing.
`authored.json` records material decisions and strict palette-checkpoint source
preservation; `../ambient-motion/authored.json` chains the 23 intentionally edited
motion sources to their final hashes. Unaffected sources still bind directly.
`inventory.json` accounts for every catalog ID, including retained UI subparts.
`renders.json` binds newly rendered representative actual before/after GLBs using
the unchanged canonical renderer, plus full-catalog contact-sheet inspection.
The portable `actual-review.html` presents those actual comparisons, not mockups.

Neutral CPU asset renders and standalone browser review are allowed evidence,
not game camera, GPU performance, artist acceptance or animation appeal.
Separate game consumption, imports and all game repository changes are out of scope.
Original seal identity, native UI structure, shared foliage instances, source
root ownership, rigs, sockets, clips, UVs, alpha, roughness and normal channels
must survive. No new dependencies, purchases or global configuration changes.

Reproduction uses existing isolated workers with an explicit installed Blender:

```sh
python3 -m tools.asset_pack.worker tools/asset_pack/vivid_refinement.py --label vivid-author --blender /path/to/blender --apply
```

Authoring fails closed if preserved baseline/current bytes do not match. It never
rebuilds geometry. Preserve `.cache/vivid-palette/before/` for local comparisons;
recover missing bytes from `cfdb114`, not from a builder. Historical colorful
source bytes are from `cadf037` and their hashes are checked against the original
first-round baseline. The validation section below records actual results, not promises made by this
procedure.

## Validation and reproduction

[Checks](checks.json), [independent preservation](preservation.json),
[render bindings](renders.json), [presentation views](presentation.json),
[decal alpha](decals.json) and [standalone browser review](browser-review.json)
separate mechanical results from visual judgments.

- `mise run check`: fast tests plus Ruff, Python/JS syntax and worker safety;
  the exact final count/log is bound in `../ambient-motion/checks.json`.
- `mise run style-tests`: 27 shared Blender fixtures; four additional focused
  `test_vivid_blender.py` fixtures cover color/alpha, orphan persistence and exact
  encoded-map/binding negative controls. Five ambient Blender fixtures cover
  localized ownership, rejection boundaries and presentation-buffer classification.
- `python3 -m tools.asset_pack.check --all --blender /path/to/blender`:
  118 saved-source exports and geometry/material/rig round-trip checks.
- `verify_style_blender.py --all`: all 118 authored selections.
- `verify_painted_blender.py` with all 118 baseline IDs: packed images, UVs and
  embedded Base Color/Roughness/Normal/Emission channels where authored.
- `verify_forest_blender.py`: all eleven tile compositions retain footprint,
  river interfaces, shared component geometry and library freshness.
- `verify_vivid_blender.py`: independent comparison of 67 saved sources against
  their palette checkpoint (or unchanged final source), composed with the hash-bound
  landed motion audit for the 23 later edited owners. Original structure,
  IDs, Non-Color pixels, texture alpha and physical defaults/emission strengths
  survive; declared ambient pivots/new shimmer geometry are not disguised as old.
  [Exact packed/encoded PNG proofs](../ambient-motion/README.md#exact-image-preservation-not-normalized-float-hashes)
  replace unstable Blender-normalized float hashing, without epsilon or omitted
  maps; per-map byte/sample/alpha/binding hashes cover every protected channel.
- Native qualification: 3,626 checks / 121 actual captures, fourteen current
  catalog captures, independent 175-file/eleven-scene UI-only load and a directly
  loaded **fresh current ZIP**, bound in `../ui/worldtree-validation.json`.
- 118 canonical neutral actual render pairs, 192/96 derivatives and refreshed
  catalog thumbnails. The 35 saved-source presentation previews are explicitly
  **palette-checkpoint views**, without source saves; `presentation.json` retains
  their original source/image bindings, not falsely rebound final hashes. They
  are not motion evidence. Final neutral/motion GLB renders qualify the landed
  detailed output. Neutral renderer bytes are unchanged; auto-fit is not a game camera.
- Standalone task-private Chrome reviewed the portable Lavish export at desktop
  and narrow widths; all 63 displayed images loaded with no horizontal overflow.
  Project reference-library tokens/serif hierarchy supplied the page design.

Run authoring/check scripts only in isolated workers. For the painted audit,
pass canonical IDs from `baseline.json::jobs`; no-ID behavior is not a substitute
for the explicit full selection. Do not rerun `vivid_review` against optimized
exports: it enforces the historical detailed-geometry counts and can partially
rewrite the landed receipts before failing. Use the runtime successor procedure
linked above for current export comparisons. Separate export processes can reorder
GLB bytes, so old image hashes must not be rebound to a later export without
rerendering. Freshness tests retain image, derivative and renderer hash checks;
changed exports require the separately hash-bound runtime successor audit.

Root overview assemblies and two seal-authoring Blender sources remain historical
assemblies, unchanged; they are not silently rebuilt or advertised as synchronized
current views. Earlier overhaul evidence ledgers remain byte-identical. No game
repository was read/imported/changed. Separate game consumption is out of scope.
Local validation is not the required no-mistakes/forge CI delivery gate.
