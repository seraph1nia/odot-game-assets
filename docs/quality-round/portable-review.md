# Portable review — bounded quality iteration

Implementation-worker acceptance review for this iteration, **not a claim that all
105 assets visibly improved or that every reference/game requirement is final**.
Existing task-private Chrome 155.0.8059.39/model-viewer renders through ANGLE
SwiftShader software. No native GPU/FPS benchmark, independent reviewer, new
renderer, game integration or release claim.

## Current bindings and preservation

[27 matched portable pairs](portable-profiles.json), [27 resource bindings](resources.json),
[18 saved-source profiles](profiles.json), [eight unit binding comparisons](unit-bindings.json)
and [60 current/original motion bindings](motion-profiles.json) account for current
outputs. The corrected material closure is six IDs: Weaver, all four evil units
and standalone evil shield. Original 105 GLBs/473 preserved files were never
regenerated to make the comparison look better. Original partial-render failures,
iteration-1 rejections and sparse browser recordings remain distinct history.

[Historical pre-material-fix captures/bindings](history/before-material-fix/README.md)
retain all original 23 pairs/60 movies and superseded wrong-palette views. Existing
whole-viewer UID-free capture is used; unmodified full-page reference-containing
PNGs stay private. Published crops include the entire measured rectangle, no
rescaling, masks, glow trimming or favorable silhouette clipping.

Before/current literal camera/target/FOV, pose/time/speed, environment/exposure,
tone mapping and viewer/viewport dimensions match. Union-bounds fit uses 30° FOV,
30° azimuth, 68° polar angle and 5% margin. Those are diagnostics, **not a measured
game occupancy/camera**. Corrected outputs reuse existing contexts; only four newly
affected IDs require additional paired framing. Static preparation waits the actual
catalog/clip setup, not merely `loaded=true`.

## Observed gains and acceptance limits

- Archery range: taller open lookout separates its role at the provisional small
  views. Town hall: right wing/civic tier separation is clearer at 480/192; left
  wing remains partly occluded and no 96-pixel role gain is credited.
- Research tower, mine and Weaver: restrained diagonal timber-grain/duplicate
  micro-geometry cleanup. Retain role and major joints; these are craftsmanship
  gains, not newly established small-size silhouette improvements.
- Knight: shorter/broader plume retains face/sword/shield and survives playback.
  Ranged: compact hood and loaded-bolt feathers remain coherent; the hood is still
  more upright/faceted than supplied E3 and feathers are close-range details.
- Mushrooms: dominant tilted rims and quieter stems read; supporting caps in
  shrine/mystical/butterfly scenes are incidental. Glyphs have wider stone margins;
  foam's contact crescents are less like decorative floating bubbles. Crystal
  grove's secondary lean/contact regrouping is restrained, not a new crystal body.
- Dreaming trees/fauna remain unchanged authored adaptations, not supplied matches.
  Whole-frame source evidence retains empty peripheral ground/busy local contacts;
  no new fauna or tiny-role recognition quality is claimed.

### Corrected SOURCE→GLB palettes: actual current visual review

| ID | Current source-fidelity result |
| --- | --- |
| [Weaver](evidence/portable/buildings/weaver/current-on.png) | Blue/cream canopy now matches the already-blue source instead of [red baseline](evidence/portable/buildings/weaver/before-on.png). Roof/cloth/loom/wood relationships remain; source blue was not newly invented. |
| [Evil berserker](evidence/portable/characters/evil_berserker_unit/current-on.png) | Bare torso/skin hands and steel skirt panels replace unintended common blue/leather; horns, skull and dual axes retain readable silhouette. |
| [Evil mage](evidence/portable/characters/evil_mage_unit/current-on.png) | Dark aperture/hands and muted faction-purple body replace brighter human skin/purple, keeping localized eye/flame cues and readable hood planes. |
| [Evil melee](evidence/portable/characters/evil_melee_unit/current-on.png) | Dark steel body/neck and matching shield replace common blue/gold, separating faction from knight without changing armor facets or grip. |
| [Evil ranged](evidence/portable/characters/evil_ranged_unit/current-on.png) | Source red neck is now actually delivered, with steel rather than common-blue body. Skull, compact hood and crossbow stay legible; no new 96-pixel feather claim. |
| [Evil shield](evidence/portable/props/evil_shield/current-on.png) | Steel field/edge around red motif coherently match equipped melee shield, not common blue/gold. Geometry, pivot and outline retained. |

All six current source-effective material bindings pass the semantic audit, including
shader/texture/channel/alpha/emission identity; no source DATA recolor hid the loss.
See [export fidelity](export-fidelity.md) and [selected after audit](material-closure-after.json).
Weaver's software capture is softer than its baseline, so no fine-texture sharpness
improvement is credited. Paint/grain remains aligned to the same parts and no seam,
orientation/layout or visible mapping regression is observed. The numerical/source
UV/image checks support mapping preservation, not an exhaustive pixel equivalence.

## Semantic UV and exact motion geometry

[Six old→new GLB mappings](material-only-mapping.json) prove unchanged geometry,
normals, skins/joints/weights, animation bytes, node/parent transforms and extras.
Weaver's 131 finite UV byte differences are disclosed separately: maximum numeric
delta 1.1920928955078125e-7 with layout/type/order/correspondence and authored source
unchanged. Firstmate 008 accepts the **semantic** contract, not bit-exact UV;
no new tolerance/validator weakening/ULP-count or source rewrite is used.
[UV context](weaver-uv-context.json) records 512 px PNGs, LINEAR/trilinear filtering,
default REPEAT and no texture transform. Shield separately corrects a legacy scene
display label to its authoritative source; canonical root/parent/pivot remain exact.

## Six actual 1× clips, not clip-name certification

One authorized nonsecurity scheduling adjustment improved the observed run from
2 to 126 callbacks over 2.1 seconds and 1–2 to 14 decoded walk-pilot frames. It is
not causal/native performance proof. Existing actual playback/canvas recording
preserves browser wall timestamps and has 5–28 decoded frames per clip, no retiming.

All eight current units have real idle/walk/run/attack/hit/death evidence (48), plus
original-before six-clip comparisons for the two geometry-edited units (12). Only
24 current faction clips were re-recorded after palette correction because their
rendered appearance changed. The other 36 artifacts remain correctly bound to their
unchanged binaries/original versions; original pre-fix 60 remain historical.

Ordered poses and real elapsed advancement show idle breathing, alternating
in-place locomotion, attack, hit recoil and backward death/held end. Weapons follow
hands in observed sequences; new plume/hood does not introduce an evident clipping
or detachment regression. Corrected skin/black gloves/steel collars remain readable
through those poses. All eight source rig/NLA/action slots/key/weight/parent binding
fields remain unchanged; six source files are byte-identical. This accepts continuity
and delivered appearance, **not new motion-appeal improvements**. Generic ranged
starter aim, rigid cloth/capes and software cadence remain explicit limitations;
no new reload/projectile/VFX or high-frame-rate game smoothness was authored.

## Emission/form, not unsupported halo proof

Four selected D06 compositions—crystal grove, rune shrine, glowing mushrooms and
lantern bridge—have source/GLB-bound before/current emission-disabled companions.
Only loaded material strength is temporarily zeroed; no source/GLB is saved.
Colored facet/cap/stone bodies and opaque channels remain readable without emission;
cyan glyph/foam base color remains, rather than disappearing with emission.

The existing viewer has no bloom/effect composer: these are **emission-on/off**,
not fabricated halo-on/off. Source Fog Glow remains separately profiled and does
not export. On/off crop widths differ by 10 CSS px, unchanged height/vertical FOV;
each before/current state is exactly matched and whole-viewer measured. No renderer
expansion, game bloom integration or calibrated halo performance is claimed.

## Overall disposition

Current 23 authored IDs plus four additional consumer-fidelity corrections are
accepted for this bounded iteration with the limits above. Some library dependents
are only incidental improvements, not a tally of 27 newly excellent assets.
[Coverage](coverage.md) assesses all 105 canonical IDs and retains unchanged assets,
role/reference exceptions and remaining opportunities. Full component turnarounds,
actual game occupancy/native rendering and future fauna/animation appeal work are
not silently certified. Remaining pipeline review/tests/docs/lint/push/PR/CI belong
to the same no-mistakes run; human asset merge authorization is separate.
