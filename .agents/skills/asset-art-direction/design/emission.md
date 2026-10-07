<a id="d06"></a>
# D06 — Emission, water and magical readability

## Evidence and observation

[IDs](../references/index.md) F1/F2 show shaded colored crystal faces with bright
edges; F4/F6 emphasize underside/stem/spot glow; F3's runes lie on stones.
F5/F7 have a coherent stream/fall and contact foam. A5 uses few violet focal
accents; E2 uses flame/eyes against a dark aperture.
[C-MAGIC, C-CAP and C-WATER](../references/evidence.md#crops) locate those cues.

## Standard and rationale

Localize emission to runes, luminous undersides/windows/eyes/flame and narrow
crystal highlights while retaining shaded body form. Feather local receiving
bounce. Water silhouette, level and flow must read without transparent realism.
Bloom reinforces identity; it must not be required to recognize the object.
Glow should not hide material/shape deficiencies or wash out the broad faces.

## Scope and exceptions

Magical forest, academy/mages, enemy signals, windows/lanterns. Nonluminous props
need no emission. Opaque stylized water is the existing technical adaptation,
not an optical property proven by a picture. Reference particles are presentation
accents: no automatic requirement for exported dynamic lights or animated VFX.

## Qualitative examples

- **Pass anchor:** F1's colored facets survive cyan edges; F5 foam groups at the
  fall/rock contacts rather than equally spaced decorations.
- **Fail criterion:** white uniformly glowing crystals, whole luminous caps/armor,
  hard light rings on ground, or rune strips floating away from the stone plane.
- Compare bloom-off and bloom-on; check body value/color separation in both.

## Uncertainty and calibration

No emission strength, bloom radius or water shader target can be recovered from
unknown image lighting/tonemapping. Existing material/preview settings live in
[art_style.py](../../../../tools/asset_pack/art_style.py). Game bloom is a separate
renderer effect: compositor Fog Glow does not export. Native GPU or moving-water
quality cannot be certified by stills.

How: [emission/water](../blender/emission-water.md),
[review profiles](../blender/review-scenes.md). Existing map masks:
[painted_finish.py](../../../../tools/asset_pack/painted_finish.py).
