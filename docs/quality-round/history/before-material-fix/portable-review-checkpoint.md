# Portable review checkpoint — historical capture, corrected export review pending

**Update after steering 007:** the existing selected exporter now corrects the
proven material loss for exactly six audited IDs. Seven real Blender fixtures,
24 combined style/export fixtures and selected six-ID round-trip/material/packed
checks pass; source bytes remain unchanged. The captures and motion observations
below still bind the **pre-fix GLBs**, not the newly corrected exports; their
superseded copies and original metadata remain in
[history/before-material-fix](README.md).

New captures are paused after the strict old/new GLB mapping found 131 Weaver UV
accessor byte differences, with maximum numeric delta 1.1920928955078125e-7.
Other compared Weaver geometry/normal/transform/scene fields are identical.
No exact UV-byte preservation or completed material-only motion mapping is claimed.
The unchanged source UVs were not rewritten. Firstmate has the concrete diagnostic
for steering before any rerender/retry. See
[loss boundary](../../material-loss-boundary.json), [105-ID closure](../../material-closure.json)
and [selected corrected-material audit](../../material-closure-after.json).

Reviewer: implementation worker. **Not whole-catalog acceptance or shipping.**
The review uses official task-private Chrome 155.0.8059.39, the existing catalog
and bundled model-viewer, neutral environment, exposure 1.05, automatic tone mapping,
shadow intensity 1. Rendering is **ANGLE SwiftShader software**, not native GPU or
consumer performance evidence. No source, shader defaults, rig or game scene was
altered to obtain the browser evidence.

## Static coverage and framing

[portable-profiles.json](portable-profiles.json) binds **23 before/current pairs**
to actual source/GLB hashes, identical literal camera/target/FOV, frozen idle/time 0
where applicable, lighting/exposure and complete viewer rectangles. Cameras use
observed union bounds, a fixed 30° FOV / 30° azimuth / 68° polar angle and 5% fit
margin. These are portable diagnostics, not a game camera or measured target size.

The raw UID-free full-page PNGs are unchanged in private work records; they can
contain supplied-reference UI and are **not published**. The committed candidates
under [evidence/portable](evidence/portable/) are outward-rounded whole-viewer
crops, without rescaling, masking, trimming silhouettes/glow or substituting a
baseline. Raw/crop hashes, dimensions and transformations are recorded. Early
`loaded=true` knight captures preceded the catalog's final clip/camera setup;
those incomplete attempts were preserved privately and excluded from the matched
23-pair evidence. Current preparation waits the actual loaded UI and clip setup.

### Observations, not a tally of 23 visible improvements

- Archery range's taller open lookout remains visibly separated in the portable
  model. Town hall's spread/lowered right wing separates its civic tiers; left
  wing remains partly occluded. These support the source D01 judgments.
- Research tower, metal mine and Weaver retain their roles; timber cleanup is
  primarily a source close-range D04 gain, not a newly established tiny portable
  recognition benefit. Selected building GLBs intentionally exclude display terrain.
- Knight's shorter/broader plume and ranged unit's compact hood contour survive
  portable loading. The latter's intended red neck accent **does not**: see below.
- Both mushroom prototypes visibly have less regular tilted rims; stone-bound
  glyphs have wider face margins. Foam's open crescents replace closed bubbles.
  The standalone crossbow shows its loaded-bolt feathers at prop diagnostic size.
- Grove contact/secondary-crystal changes remain restrained. Changes to supporting
  caps in crystal shrine, mystical grove and butterfly glade are incidental at
  small size, not new focal-object or fauna improvements. The three dreaming
  compositions remain authored adaptations with no supplied reference match.

## Emission/form check and the halo boundary

Four selected D06 compositions—crystal grove, rune shrine, glowing mushrooms and
lantern bridge—also have before/current emission-disabled companions. Only the
loaded material emission strengths were temporarily set to zero through existing
model-viewer material APIs; no GLB/source was saved. Camera, target, vertical FOV,
pose, exposure and environment remain fixed. Whole-viewer widths differ by 10 CSS
pixels between the two states, with unchanged height/vertical projection; each
state is independently measured and each before/current pair has identical bounds.
No selective crop or artificial rescaling hides this framing difference.

Colored crystal faces, cap bodies, broad stone and the opaque channel remain
readable without emission. Glyph/foam geometry remains cyan through its base
color; removing emission does not remove the underlying painted/geometric marks.
This supports body-form preservation, **not a calibrated light/halo match**.

The existing catalog has no bloom/effect composer. These are explicitly
**emission-on/off** comparisons, not fabricated bloom-on/off images. Source Fog
Glow is represented in the separately matched saved-source renders and does not
export. A same-renderer portable halo comparison is unavailable without a renderer
change, which is outside this review; no game bloom integration is claimed.

## Actual six-clip playback and immutable source bindings

One authorized private Chrome scheduling change added only the three documented
nonsecurity background-throttling prevention flags. Runtime/profile/viewport and
SwiftShader backend were preserved. The same 2.1-second diagnostic observed
2 callbacks before and 126 after; the single short walk pilot changed from 1–2
decoded frames to 14. This is evidence of the changed run, **not proof of a causal
mechanism or native FPS performance**. Old sparse recordings and ref errors remain.

[motion-profiles.json](motion-profiles.json) records **60 actual 1× recordings**:
all six current clips for all eight units (48), plus six original-before clips
for each of the two geometry-modified units (12). Videos retain original browser
wall timestamps; none was slowed, sped up or synthetically retimed. Each has
5–28 decoded frames, actual clip advancement/loop/finish state, source/export
bindings and artifact hash. Visual review used timestamp-ordered original decoded
poses alongside real playback advancement; this is more than clip-name/static
pose validation, but does not claim high-frame-rate native-game smoothness.

Idle breathing, alternating in-place walk/run, attack gestures, hit recoil and
backward death/held end poses remain readable. Weapons follow their attachment
hands in the observed sequences, with no new detachment or plume/hood clipping
regression evident. Ranged attack is still a compact generic starter aim gesture,
not newly authored crossbow timing/reload/VFX; cloth/capes remain rigid-part
starter deformation rather than a new soft-skin animation pass. No motion-appeal
improvement is credited to unchanged curves or the scheduling fix.

[unit-bindings.json](unit-bindings.json) gives exact read-only source comparisons:

- Archer, mage, berserker and three other evil units: **both source and GLB bytes
  unchanged**, no changed mesh geometry, material slots or bindings.
- Knight: only `Blue sweeping helmet plume` mesh geometry changes; no material
  assignment, existing weights, parent/basis/inverse or armature modifier changes.
- Evil ranged: `Open cloth hood` geometry changes, `Folded cloth collar` changes
  effective slot `evil_purple` → `evil_red`, and two loaded-bolt feather meshes
  are added under the existing equipment hierarchy. Existing bindings unchanged.
- All eight: rig/rest-bone/deform flags/matrices, NLA assignments/ranges, action
  slots/frame ranges and every serialized F-curve key/handle/interpolation digest
  remain identical. FPS/frame bindings match. This is preservation evidence, not
  proof that every pre-existing motion is artistically final.

## Needs refinement: effective object materials are lost in portable export

The source/portable palette difference is real, not just a stale thumbnail:

| Source object | Effective source slot | Mesh-data slot | Current GLB primitive |
| --- | --- | --- | --- |
| Weaver `Canvas canopy stripe` (and blue stripe copies) | `blue`, link `OBJECT` | `red` | `red` |

The canonical planner/selector loads the correct source and selects the stripe;
its Principled base color is blue. The corresponding GLB node is present but
uses the underlying red material. Thus the native canopy is red in both before
and current exports while both source scenes render blue. Ranged's source red
collar likewise remains blue in portable evidence; enemy palette fidelity needs
the same effective-material audit. Do not accept D03/faction identity from these
portable images or call the source red-neck change successfully delivered.

Exact read-only source-slot/GLB-node evidence remains private in
`.cache/quality-round/browser/weaver-export-material-divergence.json`. No exporter
patch, global palette migration or source-material overwrite has been made.
Firstmate has been asked to authorize the smallest existing export-route correction
with an executed Blender regression and exact affected dependency closure. Current
motion geometry/binding observations remain useful, but **overall portable art
acceptance and publication are blocked** on this genuine serialization defect.
