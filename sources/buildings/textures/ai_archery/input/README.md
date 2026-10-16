# Odot / Archery Range — AI-generated material POC

This is **an executable material input kit**, not a finished Blender export or a camera-aligned 3D paint-over. The raw artwork was image-generated for this conversation. Source-image swatches were cropped from generated sheets; edge pixels on tiling candidates were numerically matched and resized. They are not guaranteed to tile aesthetically without repeated seams.

## Files

- `textures/`: individually named Base Color, Roughness, Normal PNGs. Main 8 swatches at 1024 x 1024; small supporting crops at 512 x 512.
- `decals/`: transparent extracted detail sheets and circular archery target. Dark-backdrop removal is heuristic; review feathering/halos before production.
- `asset_recipe.json`: material candidates, exact channel paths, color spaces, source-crop resolution, size and limitations.
- `source_sheets/`: original generated texture artwork for re-cropping.
- `previews/material_contact_sheet.png`: visual index of all Base Color materials.
- `docs/BLENDER_AGENT_TASK.md`: non-destructive Blender workflow.
- `docs/PAINTOVER_PROMPT.md`: prompt for the subsequent mesh-aligned image-edit step.
- `docs/material_id_palette.json`: suggested masks for Blender guide passes.

## Constraints

1. Source of truth: `sources/buildings/archery_range.blend` in `seraph1nia/odot-game-assets`.
2. Inspect actual material slots and UV layouts before assigning. `material_candidates` are hints, not verified exact current material-slot inventories.
3. Do not duplicate a shingle pattern over already modeled shingles unless the scale matches.
4. Keep Base Color sRGB and Normal/Roughness Non-Color. Use a `ShaderNodeNormalMap` for normal maps. Roughness PNGs are scalar. Metallic behavior remains an authored Blender scalar (no metalness maps provided).
5. Normal and roughness are lightweight **heuristic companions**, not ground-truth PBR. In particular avoid image-derived normals on cloth, complex existing normals or stylized rock if they harm shape.
6. Only edit an isolated copy of the original .blend; preserve packed manual images and existing geometry/UVs/animations. Never run an old builder to update maps.
7. The camera-projection pass requires a **real screenshot and material/depth masks from Blender** before an aligned paint-over can be generated. No fabricated aligned paint-over is included.
8. Use `mise run asset-style-check -- buildings/archery_range` and existing selected-source export/check route after intentional source save. Compare before/after neutral GLB views and actual in-game camera.

## Suggested first iteration

Apply only `wood_warm_planks`, `roof_blue_shingles`, `plaster_warm` and `stone_mossy_masonry` as material variations in a copy of the Archery Range scene. Keep existing normals and roughness where superior. Capture same camera before/after. Then add decals and projection later.

## Source artwork / rights

The supplied reference path above points to an existing image in your GitHub repository; the external reference image is NOT embedded here. This kit contains newly generated pictures, including overview sheets, produced during this chat; they are art experiments rather than proof of license for unrelated reference material. Preserve provenance and review any intended public redistribution separately.

## Delivered POC scope

This ZIP includes **12 complete color/roughness/normal material families** and one RGBA bullseye decal. Other decorative decals described as possibilities in the implementation prompt are **not included**. The package is intentionally not a mesh-aligned paint-over.
