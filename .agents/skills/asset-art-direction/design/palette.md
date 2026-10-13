<a id="d03"></a>
# D03 — Palette, value and saturation hierarchy

## Evidence and observation

[IDs](../references/index.md) V0/A2/B4 combine warm timber, muted pale masonry,
cool roof/cloth and small amber/gold accents. V2 has a red roof. E1–E4 use dark
armor/cloth, bone and red signals. F1–F8 place cyan/violet magic against natural
green/gray/brown support. The superseding [W0 woodland board](../references/index.md#whisperwood)
uses cool slate, gray-green growth and aged brown timber with small amber and
cyan/violet lights. Older bright yellow-green reference ground is historical
context, not the target for the authorized Whisperwood overhaul.

## Standard and rationale

Assign support/body/role/accent color roles. Use substantially lower-saturation support and body colors, retaining related
variation within surfaces and material/focal separation in grayscale as well as
color. Gloom comes from weathered materials and cool support values, not crushed
blacks or merely dimming preview lights. Warm windows remain small readable accents.
Preserve existing unit/faction identity. Coherence is relational, not exact
screen-pixel matching under unknown reference lights.

## Scope and exceptions

All families. Bakery red roof/tree-house greens, dark enemy/red flame and
luminous forest cyan/violet are named exceptions to a simplified blue-roof,
warm-window village palette. Mute magic bodies as well as natural supports; concentrate chroma and emission
on narrow highlights, runes, eyes and lantern/window centers. Preserve different
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
