# Reference authority and asset-view index

Read before claiming resemblance or selecting an asset's intended picture.
IDs here are **citation aliases**, not another association manifest.
[Catalog associations](../../../../catalog/associations.json),
[export manifest](../../../../exports/asset_manifest.json) and
[schema](../../../../catalog/SCHEMA.md) own asset IDs, reference paths/crops,
source/export selectors and metadata precedence. Associations override manifest
fields; the E-series references currently come from manifest records. The
[offline reference library](../../../../sources/reference/index.html) provides
full-size viewing; [crop evidence](evidence.md) directs visual inspection.

<a id="authority"></a>
## Authority and provenance

The 26 existing PNGs across five supplied sets define intended visual evidence.
They map to 32 asset views (seven board crops plus 25 individual images).
Their originals were visually inspected during the 2026-10-07 guidance scout;
25 archive image dimensions/hashes matched the checked-in manifests. No original
was edited. Archive hashes are recorded declarations: the archives themselves
were not independently reverified.

| Set | Image size/count | Provenance owner |
|---|---|---|
| V: original village board | 1536×1024, one PNG/seven crops | [Board](../../../../sources/reference/fantasy_village.png), [catalog framing](../../../../tools/asset_pack/catalog.py); supplied-view declaration in [README](../../../../README.md#reference-asset-set) |
| A: new autobattler | 1254×1254, eight PNGs | [Manifest](../../../../sources/reference/autobattler/manifest.json), user-supplied `new_autobattler_assets.zip` |
| E: evil units | 1024×1024, four PNGs | [Manifest](../../../../sources/reference/evil_autobattler/manifest.json), user-supplied `evil_autobattler_units.zip` |
| B: more buildings | 1254×1254, five PNGs | [Manifest](../../../../sources/reference/more_buildings/manifest.json), [provenance](../../../../sources/reference/more_buildings/PROVENANCE.md) |
| F: magical forest | 1254×1254, eight PNGs | [Manifest](../../../../sources/reference/magical_forest/manifest.json), [provenance](../../../../sources/reference/magical_forest/PROVENANCE.md) |

B/F provenance says unchanged imports from supplied archives containing no
attribution/license document. V0 has no adjacent archive manifest or named creator/
license; current original SHA-256 is
`b25f5421dea51daf82dbed988afd87a6e2e7f8431d5d7db17ea576836ee6b32a`.
User supply and checksums do **not** establish rights, source author or whether
pictures were generated. Do not infer CC0 or external publication permission.
Link existing tracked originals; do not publish new copied/cropped/annotated
pictures or acquire references without a separate rights/scope decision.

Current `exports/previews/` and thumbnails are generated **baselines/diagnostics**,
not intended references. Historical game/KayKit audits are integration context,
not current authored Blender standards. Prior building/softness summaries are
project decisions/history, not fresh acceptance results. Still pictures cannot
establish rig correctness, animation timing/appeal, rights or native GPU quality.
Dreaming forest has no explicit supplied-reference association: see
[authored adaptation](../families/environment.md#dreaming).

## Board views

V0 is the whole [fantasy village board](../../../../sources/reference/fantasy_village.png).
Natural-pixel crops below are the existing association rectangles `[x,y,w,h]`,
not body segmentation or extracted proportion metrics.

| Evidence ID | Canonical asset ID | Existing crop |
|---|---|---|
| V1 | `buildings/tree_house` | `[0,0,382,440]` |
| V2 | `buildings/bakery` | `[383,0,384,440]` |
| V3 | `buildings/gold_mine` | `[769,0,383,440]` |
| V4 | `buildings/woodcutter_hut` | `[1153,0,383,440]` |
| V5 | `characters/knight` | `[0,515,486,388]` |
| V6 | `characters/mage` | `[488,515,499,388]` |
| V7 | `characters/archer` | `[989,515,547,388]` |

## Individual images

Use the asset mapping in metadata if it changes; aliases do not override it.
All images below are full-image associations, not invented individual component
turnarounds. Environment components derive context from their associated tile.

| ID | Canonical asset ID | Existing original |
|---|---|---|
| A1 | `buildings/arrow_tower` | [Arrow tower](../../../../sources/reference/autobattler/arrow_tower.png) |
| A2 | `buildings/barracks` | [Barracks](../../../../sources/reference/autobattler/barracks.png) |
| A3 | `characters/berserker` | [Berserker](../../../../sources/reference/autobattler/berserker.png) |
| A4 | `buildings/bombarding_tower` | [Bombarding tower](../../../../sources/reference/autobattler/bombarding_tower.png) |
| A5 | `buildings/magic_academy` | [Magic academy](../../../../sources/reference/autobattler/magic_academy.png) |
| A6 | `buildings/stone_cutter` | [Stone cutter](../../../../sources/reference/autobattler/stone_cutter.png) |
| A7 | `buildings/tavern` | [Tavern](../../../../sources/reference/autobattler/tavern.png) |
| A8 | `buildings/trade_market` | [Trade market](../../../../sources/reference/autobattler/trade_market.png) |
| E1 | `characters/evil_melee_unit` | [Evil melee](../../../../sources/reference/evil_autobattler/evil_melee_unit.png) |
| E2 | `characters/evil_mage_unit` | [Evil mage](../../../../sources/reference/evil_autobattler/evil_mage_unit.png) |
| E3 | `characters/evil_ranged_unit` | [Evil ranged](../../../../sources/reference/evil_autobattler/evil_ranged_unit.png) |
| E4 | `characters/evil_berserker_unit` | [Evil berserker](../../../../sources/reference/evil_autobattler/evil_berserker_unit.png) |
| B1 | `buildings/archery_range` | [Archery range](../../../../sources/reference/more_buildings/low_poly_fantasy_archery_range.png) |
| B2 | `buildings/research_tower` | [Observatory](../../../../sources/reference/more_buildings/fantasy_observatory_cottage_diorama.png) |
| B3 | `buildings/metal_mine` | [Iron mine](../../../../sources/reference/more_buildings/low_poly_medieval_iron_mine_diorama.png) |
| B4 | `buildings/weaver` | [Weaver](../../../../sources/reference/more_buildings/cozy_fantasy_weaver_s_workshop.png) |
| B5 | `buildings/town_hall` | [Town hall](../../../../sources/reference/more_buildings/fantasy_town_hall_diorama.png) |
| F1 | `environment/hex_crystal_grove` | [Crystal grove](../../../../sources/reference/magical_forest/enchanted_crystal_grove_tile.png) |
| F2 | `environment/hex_mystical_grove` | [Mystical grove](../../../../sources/reference/magical_forest/mystical_crystal_grove_diorama.png) |
| F3 | `environment/hex_rune_shrine` | [Rune shrine](../../../../sources/reference/magical_forest/enchanted_forest_rune_shrine.png) |
| F4 | `environment/hex_glowing_mushrooms` | [Glowing mushrooms](../../../../sources/reference/magical_forest/enchanted_glowing_mushroom_grove.png) |
| F5 | `environment/hex_lantern_bridge` | [Lantern bridge](../../../../sources/reference/magical_forest/enchanted_lantern_bridge_diorama.png) |
| F6 | `environment/hex_bioluminescent_grove` | [Bioluminescent grove](../../../../sources/reference/magical_forest/enchanted_bioluminescent_mushroom_grove.png) |
| F7 | `environment/hex_woodland_bridge` | [Woodland bridge](../../../../sources/reference/magical_forest/enchanted_woodland_bridge_diorama.png) |
| F8 | `environment/hex_crystal_shrine` | [Crystal shrine](../../../../sources/reference/magical_forest/enchanted_crystal_shrine_diorama.png) |

For inspection, open the actual image, identify the applicable crop/landmarks and
record observation versus decision. Do not infer aesthetics from filenames.
Missing/ambiguous association: report the exact ID/path or source-selection
question; use only evidence-supported common rules, not a fabricated reference.
