# Localized building and water motion

Use for an authorized small ambient detail, not character animation or a library
rebuild. First read the applicable [building](../families/buildings.md) or
[environment](../families/environment.md) family,
[export contract](export.md), and existing
[coverage/playback notes](../../../../docs/ambient-motion/README.md).

- Shared limits are `art_style.AMBIENT`; explicit targets are
  `tools/asset_pack/ambient_contract.py`. Keep one connected animated spot per
  building and building/tile roots, structure and vegetation static.
- Use ordinary object-action transforms exported as `ambient`, with five
  meaningful keys and matching rest endpoints. Keep the six unit clips separate.
  Avoid particles, runtime shader dependencies, moving whole water sheets,
  camera-only motion and connector-edge deformation.
- `tools/asset_pack/ambient_motion.py` is an explicit source-edit procedure, not
  an automatic rebuild hook. Preserve current manual edits before any revision.
  It scratch-saves, reloads and verifies before replacing a source. Never strip
  orphan IDs to hide save losses.
- Export existing sources via the official catalog tools; set `ambient: true`
  under each affected association's `animation_policy`. A metadata entry alone
  is not a playable animation.
- Run the independent `verify_ambient_blender.py` worker and fast ambient receipt
  tests. Check actual exported mesh motion, closed endpoints, unchanged fixed
  transforms, source/export poses and narrow geometry costs. Review matched
  exported frames/GIFs for restrained movement and attachments. Renderer/browser
  evidence is not game-engine, GPU or artist acceptance.
