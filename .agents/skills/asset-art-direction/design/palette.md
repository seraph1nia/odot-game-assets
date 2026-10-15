<a id="d03"></a>
# D03 — Palette, value and saturation hierarchy

## Evidence and observation

[IDs](../references/index.md) V0/A2/B4 combine warm timber, muted pale masonry,
cool roof/cloth and small amber/gold accents. V2 has a red roof. E1–E4 use dark
armor/cloth, bone and red signals. F1–F8 place cyan/violet magic against natural
green/gray/brown support. Original supplied village/unit/forest pictures again
inform color: blue and terracotta roofs, warm timber, living greens and distinct
cyan/violet bodies. [W0](../references/index.md#whisperwood) informs growth and
role identity, not its rejected grey/desaturated treatment. Reference lighting
is not albedo; compare actual source materials and neutral exported renders.

## Standard and rationale

Assign support/body/role/accent color roles. Use rich coherent body colors with
related shades within surfaces; separate warm timber/plaster from colored roofs,
cloth, foliage and magic. Keep stone and metal materially recognizable, not a
uniform grey wash across every family. Fine grain, leaf-root/tip shifts, cloth
fold shades and restrained patina add lifelike softness without noisy saturation.
Preserve material/focal separation in grayscale as well as color. Warm windows
remain small readable accents; do not grade previews to disguise unchanged maps.
Preserve existing unit/faction identity. Coherence is relational, not exact
screen-pixel matching under unknown reference lights.

## Scope and exceptions

All families. Bakery red roof/tree-house greens, dark enemy/red flame and
luminous forest cyan/violet are named exceptions to a simplified blue-roof,
warm-window village palette. Keep colored shaded magic bodies; concentrate
emission (not all chroma) on narrow highlights, runes, eyes and window centers. Preserve different
hero/enemy hues rather than painting enemy equipment in hero colors. Family leaves link these exceptions
without creating independent swatch tables.

## Qualitative examples

- **Pass anchor:** B4's cloth/loom signal weaving while masonry supports it;
  E2's eyes/flame stand out against the dark face aperture.
- **Fail criterion:** equally saturated ground/flowers/roof/emblem, or dark enemy
  armor merging with the hood's facial recess. Bloom cannot replace value hierarchy.
- Use matched neutral/studio views and a grayscale companion before attributing
  old-versus-new preview differences to the material palette.

## Uncertainty and calibration

Rendered reference pixels contain lighting, tone mapping and emission; they are
not albedo swatches. No exact RGB, roughness or saturation range is extracted.
Annotate comparable material regions, consider distributions, and test relational
separation through a common view profile before suggesting numerical targets.
Current shared palettes and sRGB conversion are owned by
[art_style.py](../../../../tools/asset_pack/art_style.py); kit-specific authored
materials remain in their existing builders. This guide duplicates neither.

How: [materials/color](../blender/materials.md). Cross-view evidence:
[review scenes](../blender/review-scenes.md).
