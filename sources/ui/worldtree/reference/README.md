# Worldtree visual reference and implementation handoff

**Target:** `seraph1nia/odot-game-assets` — standalone native Godot visual/art work only.

## Start here

1. Read **`IMPLEMENTATION_PROMPT.md`**, the complete copy-ready coding-agent assignment.
2. Open **`CONTACT_SHEET.png`** to browse the visual reference set.
3. Open **`canonical/exact_24_node_tree.png`** and the four `canonical/activation_stages/*.png` screenshots to see the **machine-verified topology**. Their SVG counterparts are editable.
4. Use **`canonical/worldtree_topology.json`** as the only authoritative structural source. It defines node IDs, parent edges, slots, positions, icon keys and reproducible state fixtures.
5. Use `art_references/` and `starter_icon_svgs/` to explore styling and assets, not to infer game rules.

## Contents

| Folder/file | Purpose |
|---|---|
| `art_references/` | Six AI-generated concept boards illustrating dead, alive, progressive and icon art style. Reference only, not runtime textures. |
| `canonical/worldtree_topology.json` | The exact 24-node, 23-connection tree contract with four test fixtures. |
| `canonical/exact_24_node_tree.svg/.png` | Deterministic 24-node graph drawing with positions/numbers. |
| `canonical/activation_stages/` | Four exact topology states, each as editable SVG and PNG. |
| `starter_icon_svgs/` | Thirty simple, original vector starter silhouettes (not final decorative node sprites). |
| `icon_catalog.json` | Stable icon key vocabulary; no gameplay effects. |
| `IMPLEMENTATION_PROMPT.md` | Agent-first instructions tailored to the existing asset repo. |
| `CONTACT_SHEET.png` | Click-free visual index of concept references and canonical diagram. |

## Important: two distinct truths

**Artistic reference** comes from the AI-generated boards (bark, glows, dead-to-alive feel, mushrooms, critters). Those boards are not precise asset sheets. They may visually contain inaccurate counts, imperfect joints or repeated labels. Don't crop/ship them.

**Mechanical layout** comes exclusively from `canonical/worldtree_topology.json` and its deterministic SVG/PNG rendering. The exact distribution is:

- 1 root
- 2 stacked trunk nodes
- 3 primary branches
- 6 secondary branches (2 per primary)
- 12 terminal branches (2 per secondary)
- **24 socket nodes total; 23 parent-to-child connectors total.**

A dormant or alive state is applied **per individual node and incoming connection**. Neither state should require swapping or regenerating a full-screen tree image. Each edge glows only when its child is acquired and its parent is acquired.

## Exact state examples

| Snapshot | Acquired count | Alive areas |
|---|---:|---|
| `01_root_only` | 1 | Root only |
| `02_trunk_awakened` | 3 | Root + 2 trunk |
| `03_three_primaries_awakened` | 6 | Root + trunk + 3 primary |
| `04_left_branch_family_awakened` | 10 | Root + trunk + left primary + its 2 secondaries + its 4 terminals |

## Source & usage note

The concept reference pictures were generated for this conversation. The deterministic graph vectors, JSON data, stage drawings and minimal starter icon SVGs were programmatically authored for this handoff. This ZIP does not contain proprietary Blender models, third-party paid asset packs, or game code. The concept art is a **visual design reference**, not a screenshot to be copied or a verified game asset. The target agent should author/review clean original runtime artwork and keep source/output provenance in the asset repository.
