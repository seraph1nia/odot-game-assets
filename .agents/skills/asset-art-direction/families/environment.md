# Forest tiles, components and authored adaptations

Use for groves/shrines/bridges or shared forest pieces. Choose
[contacts](../blender/contacts.md), [emission/water](../blender/emission-water.md)
or [normals](../blender/normals.md) for the actual issue. A shared edit also needs
[library ownership](../blender/libraries.md). Common criteria stay in
[D01–D09 owners](../design/index.md), not a forest-only copy.

## Supplied tile signatures and exceptions

[Reference IDs](../references/index.md) F1/F2: dominant crystal group with rock/
leaf support; F3: rune monolith/steps; F4/F6: dominant luminous mushroom with
varied smaller caps; F5: stone arch/lantern stream; F7: curved wooden bridge;
F8: central floating crystal/stone ring and open approach.
Protect each focal mass/negative space, rather than making every tile a uniformly
dense collection of glowing components. D06 cyan/violet/amber accents are not a
reason to make the entire ground/cap luminous. D02 retains selective smooth
organic normals despite visible reference cap facets; crystals stay flat.

## Actual libraries and grid

[forest_kit.py](../../../../tools/asset_pack/forest_kit.py) owns the original
prototypes, [forest_tiles.py](../../../../tools/asset_pack/forest_tiles.py) the
compositions; component exports have explicit shared-source/collection mappings
in [associations](../../../../catalog/associations.json). Their tile-reference
links are contextual, not supplied component turnarounds.

Flat-top footprint, radius/surface/bottom, river dimensions and neighbor spacing
come from [art_style.HEX](../../../../tools/asset_pack/art_style.py). Preserve
origin-root/base placement and north/south endpoint contracts. Tile GLBs retain
terrain; studio is omitted. Shape changes never excuse footprint breaks.
Use [forest verifier](../../../../tools/asset_pack/verify_forest_blender.py) after
authorized changes for edge/base/library signatures. Its endpoint checks plus
existing builder fixtures are mechanical evidence, not an art verdict.

<a id="dreaming"></a>
## Dreaming forest: authored adaptation, not reference fidelity

`shared_enchanted_kit.blend` and three dream tiles/nine companion pieces have no
explicit supplied-reference association. Their present previews are authored
baselines, not untouched supplied art. The approved starting scope treats them
as adaptations inheriting common rules, with consistent painted wings/fur,
broad tree planes and localized luminous accents. Do not fabricate a missing
picture or claim a reference-match pass. Read [authority](../references/index.md#authority).

[enchanted_kit.py](../../../../tools/asset_pack/enchanted_kit.py) and
[enchanted_tiles.py](../../../../tools/asset_pack/enchanted_tiles.py) own the
companion prototypes/compositions. Preserve the original forest library and
explicit dependency closure. Fauna are static scenery, not rigged units;
butterfly/moth pivots are body-centered flight placements, other companion
pieces use ground-zero placement. Do not add shared unit clips.

Review dream assets for consistency/role/density with explicit adaptation status;
small fauna may become incidental at small views. New creative motifs or stronger
reference authority require scoped approval, not external acquisition by default.
