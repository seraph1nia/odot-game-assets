# Form-preserving emission and water contacts

Use for white/flat glowing bodies, detached runes, floating light disks or foam.
Primary visual owner: [D06](../design/emission.md#d06).
Pipeline owners: [painted_finish.texture_material](../../../../tools/asset_pack/painted_finish.py),
[forest_kit.py](../../../../tools/asset_pack/forest_kit.py),
[forest_tiles.bridge](../../../../tools/asset_pack/forest_tiles.py) and
[style_blender.preview](../../../../tools/asset_pack/style_blender.py).

## Preconditions

Selected reference (F1/F3/F5/F6/E2 as relevant), material/map ownership,
matched view/bloom state and authorized source/maps work. Preserve existing
fields/packed images; shared edits route through [libraries](libraries.md).

## Procedure

1. Inspect the body with compositor glow off before changing emission. Separate
   colored/shaded body, narrow bright accents and halo. A washed-out crystal can
   be a material/light/color-management issue, not insufficient geometry.
2. Reuse current crystal/gill/window/rune/eye/flame families via existing
   palette/material helpers. The map generator masks crystal emission toward
   narrow painted edges and preserves darker bodies; don't replace it with a
   uniformly bright shader or new luminous tube meshes over every edge.
   Live emission/preview tunables belong to `art_style`, not copied leaf values.
3. Keep crystal faces flat and UV-aligned; cap/stem organics retain selective
   smoothing. Runes lie on actual stone surfaces without z-fighting or detached
   strips. Inspect stone plane orientation and existing rune helper placement
   from front and side, not just the flattering preview angle.
4. Use [receiving contacts](contacts.md) for feathered local cyan/amber bounce.
   Do not add hard glow disks as geometry. `ground()` only handles recognized
   receivers/tagged low roots; architecture/window spill may need a separately
   scoped, calibrated case, not a claim that all surfaces receive dynamic light.
5. For bridges/streams, reuse `hex_stream`, `waterfall`, `foam` and bridge
   composition helpers. Preserve `art_style.HEX` channel/height/endpoints and
   unchanged base placement. Water is an opaque stylized mesh; don't add a
   transparent/refraction network that cannot match the portable contract.
6. Keep flow direction/readable fall and foam at fall/rock contacts (C-WATER).
   If current foam appears detached rings, first revise subordinate shape/
   placement under approved scope rather than changing shared endpoint heights
   or increasing glow to hide separation. Check both adjoining edges.
7. Compare full/small views with bloom off/on under [recorded profiles](review-scenes.md).
   Verify packed emissive images/GLB channels and grid through
   [pipeline checks](../pipeline/index.md#checks) after authorized export.

## Output and failures

Expected: colored forms remain readable without halo; glow reinforces selected
locations; water feels embedded and preserves grid compatibility. No uniform
white body, full glowing armor/cap or floating rune patch passes on bloom alone.
If channels are present but glow absent in another viewer, distinguish emitter
maps from renderer bloom: source Fog Glow does not export, and game bloom needs
a separate renderer effect. Don't silently export studio lights or promise GPU
quality/animated water from a still. Particles/flames in references do not grant
VFX/rig/dynamic-light implementation scope.
