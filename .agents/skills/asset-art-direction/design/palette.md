<a id="d03"></a>
# D03 — Palette, value and saturation hierarchy

## Evidence and observation

[IDs](../references/index.md) V0/A2/B4 combine warm timber, muted pale masonry,
cool roof/cloth and small amber/gold accents. V2 has a red roof. E1–E4 use dark
armor/cloth, bone and red signals. F1–F8 place cyan/violet magic against natural
green/gray/brown support. Reference ground can be bright yellow-green, but it
occupies a bounded diorama rather than a verified full-screen game landscape.

## Standard and rationale

Assign support/body/role/accent color roles. Keep related variation within
surfaces and protect material/focal separation in grayscale as well as color.
Preserve existing unit/faction identity. Coherence is relational, not exact
screen-pixel matching under unknown reference lights.

## Scope and exceptions

All families. Bakery red roof/tree-house greens, dark enemy/red flame and
luminous forest cyan/violet are named exceptions to a simplified blue-roof,
warm-window village palette. Do not impose a universally muted palette on magic
or paint enemy equipment in hero colors. Family leaves link these exceptions
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
