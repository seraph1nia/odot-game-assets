# Woodland decal source textures

Four authored, reusable **512 × 512, 8-bit RGBA transparent PNGs**. The identical
source/export bytes and SHA-256 receipts are in
[`docs/dreamlike-forest/decals.json`](../../../docs/dreamlike-forest/decals.json).
Source images remain editable; deterministic regeneration is explicit:
`python3 -m tools.asset_pack.forest_decals` (overwrites these four source/export PNGs).
Preserve hand painting before rerunning. No mesh, projection bake, glTF extension,
new catalog export schema, dynamic light or game integration is included.

| Filename (`forest_decal_*.png`) | Use | Suggested square footprint in existing asset units |
|---|---|---|
| `rune_circle` | Faint cyan concentric glyph with six understated strokes; empty center under a stone/prop | 1.2–2.0 |
| `moss_wash` | Irregular overlapping green growth/color wash near rocks and roots | 0.5–1.2 |
| `fairy_ring` | Broken lavender ring/spore hints, not a solid spotlight disk | 0.8–1.6 |
| `spore_growth` | Turquoise branching colony with small soft terminals | 0.3–0.7 |

## Channel and placement contract

- RGB is **sRGB straight/unassociated color**. The standard PNG sRGB chunk is
  present. Alpha is **linear coverage/opacity**, not an emission or wind channel.
  Do not premultiply again unless the consumer explicitly expects premultiplied
  input. Color extends through transparent pixels; this avoids black fringes.
- Peak alpha is at most 0.42; edges are feathered, with a fully transparent border
  guard band. Use alpha compositing/consumer decal blending, linear texture filtering
  and mips as appropriate. Do not use opaque/cutout interpretation.
- The entire image is the square footprint above. Image center is placement pivot;
  PNG top points to source **+Y**, right to **+X**. Projection normal is source **+Z**.
  Through the existing Z-up→glTF Y-up conversion, top is **−Z** and projection normal
  is **+Y** in GLB coordinates. Rotate freely for reuse; these are not hex connectors.
- Project onto receiving ground/stone only, with a bounded depth to avoid painting
  over standing foliage or through a bridge. Keep hex boundaries and river/bridge
  surfaces unchanged. Ground-only placement needs the consuming game's filter/layer
  controls; none are verified by this PNG-only delivery.
- No dedicated Emission/Roughness maps: the intended game integration is not yet
  qualified, and duplicating speculative channels would waste resources. Default
  use is unlit color variation **without emission**. A separately tested consumer
  may reuse alpha for very faint localized rune emission; never treat the full
  square as a light source or bake fog/bloom/directional lighting into these files.

All four exports total 97,676 compressed bytes. Full decoded RGBA is 4 MiB for
both sets separately (four images × 512² × four bytes), before consumer mips and
compression; source/export copies need not both be loaded at runtime. This is a
storage/format statement, not a GPU-memory or performance measurement.
A neutral-background inspection sheet is in
[`docs/dreamlike-forest/evidence/decals-dark.png`](../../../docs/dreamlike-forest/evidence/decals-dark.png).
