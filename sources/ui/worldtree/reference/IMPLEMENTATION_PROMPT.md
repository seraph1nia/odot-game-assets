# Agent task: Build the modular, living Worldtree asset system

**Target repository:** `https://github.com/seraph1nia/odot-game-assets/`

**Task type:** Implement an original, modular **Godot UI visual component and asset library** in the **assets repository only**. Do not add gameplay skill definitions, balancing, research costs, player saves, multiplayer commands, or any changes to `odot-game`.

## 0. Repository inspection and boundaries

Read `AGENTS.md`, `docs/ui/README.md`, `docs/ui/woodland.md`, `docs/ui/api.md`, `docs/ui/architecture.md`, `docs/ui/skill-tree-validation.md`, and relevant tests before changing files. Inspect the existing `ui/preview/UI/components/skill_tree.gd/.tscn`, `ui/preview/UI/theme/ledger.tres`, `ui/preview/prototypes/`, `tools/ui/validate.py`, and the UI packaging/audit conventions.

The current `skill_tree` is a small 10-node **standalone local allocation demo**. **Preserve its API, old tests and existing working UI components.** Implement the larger tree as a new additive `worldtree.tscn` component rather than silently changing that historical contract. Any migration/replacement should be a separate future task.

Use the attached `worldtree_reference_pack` as design input. In it:

- `art_references/*.png`: visual references for wood/leaf/mushroom styling, dead/alive transformation, icon silhouettes, and sparse gloomy magical forest mood. These AI-generated images are **concept references only**, not export-ready textures or proof of exact node counts.
- `canonical/worldtree_topology.json`: **authoritative visual-structure contract**. This alone defines the node IDs, parents, branch membership, 24 nodes and 23 directed connections. There are no gameplay effects in it.
- `canonical/exact_24_node_tree.svg/.png`: machine-validated arrangement. Match this structure, not mistakes in the generated posters.
- `canonical/activation_stages/*.svg/.png`: four exact and independently reproducible state examples.
- `starter_icon_svgs/*.svg` and `icon_catalog.json`: 30 editable, minimal placeholder silhouettes; improve and refine them in the established woodland style as needed. Icons must not embed node backgrounds or gameplay meanings.

Do not crop or use the AI posters as flattened runtime tree textures; recreate original, editable art layers and preserve source/art provenance. The reference pack itself may live as clearly marked non-runtime documentation, but must not be bundled as the shipping UI payload.

## 1. Exact tree topology — non-negotiable

Implement a *physical* slender cartoon tree growing bottom-to-top. Its wooden edges and junctions must be the skill-graph edges and nodes, not merely a tree image with arbitrary nodes overlaid.

- **1 root** node at the ground/base.
- **2 consecutive trunk** nodes above it (`root → trunk_1 → trunk_2`).
- **3 primary** branches leaving `trunk_2` (left/center/right).
- Each of those has **2 secondary** children (six total).
- Each secondary branch has **2 terminal** children (twelve total).

Exactly **24 separately addressable node sockets** and **23 separately addressable parent connections**. Unique, stable IDs must match the JSON. The first acquisition always begins at the **root**, proceeds up the trunk, and then outwards. No visual progression from a mid-tree node down towards roots.

Build a cheap deterministic validator that counts role cardinality, rejects missing/duplicate IDs, verifies each parent's role, checks acyclicity, ensures the entire graph is connected, and confirms the degrees of `root` (one child), `trunk_1` (one), `trunk_2` (three), each primary (two), each secondary (two), each terminal (zero). This validator should run without launching Godot where practical.

## 2. Independent dead/alive modules

The key deliverable is a **living tree assembled from independently switchable parts**. An agent should be able to toggle **one arbitrary node and its incoming physical branch** without replacing the rest of the tree or rebuilding a large image.

Produce aligned dead and alive variants of the same reusable geometry:

- Root/base artwork and its magic-growth overlay.
- Two trunk segments.
- Three primary branch segments, six secondary branch segments, twelve terminal twig segments.
- Node socket artwork, separate from the icon placed inside.
- An overlaid animated living vein/sap/glow per **incoming edge** (23), attached to the corresponding branch segment.
- Optional leaves, blue glowing mushrooms, delicate blossoms and mana crystals that bloom with their module, not globally.
- Optional small owl, rabbit, squirrel and snail accents as transparent, mouse-ignoring illustrations. These should not obscure any node hit target.

Use the same anchor/pivot and silhouette for dormant and living variants, so toggling does not cause geometry to jump. Different orientations may use genuinely different authored modules, but can share geometry/pattern where appropriate. Preserve all individual socket and edge IDs.

**Dormant:** dead/bare dark bark; no flowing sap; sparse dull leaves; dark socket.
**Available:** parent acquired; socket has a subtle and clearly distinguishable ready-to-purchase highlight; no fully alive downstream branch yet.
**Acquired:** gold/amber life flows through the edge to the node, fresh leaves/fungi appear and the node lights up. Unrelated branches stay dark.
**Awakening:** one brief visual transition from dormant to acquired, e.g. a traveling light from parent to child followed by a few buds/leaves appearing. It must not block input or represent authoritative purchase confirmation.

A connection should be fully lit only when its **child** node is acquired and its parent is acquired. Clicking, selecting, hovering, and moving focus must not permanently activate branches. Applying a snapshot is authoritative for visual state and must deterministically settle to the same image. Respect reduced-motion or instant-completion test modes; don't use background game time for the animation.

## 3. Icon library (not game abilities)

Author/import a coherent set of at least 30 standalone **symbol silhouettes**, for example:

`world_seed, shield, spark, leaf, flame, crossed_swords, heart, book, spiral, bow, paw, crystal, mushroom, crescent_moon, lantern, water_drop, tree_roots, thorn_vine, antlers, eye, acorn, feather, tower, rune, snowflake, poison_drop, stone, boot, owl, squirrel`.

Icons must be individually swappable per node by a string key. Do not bake symbols into bark, glow rings, socket borders or the reference screenshots. Use scalable SVG source (or original editable sources with runtime exports) and tint/lighting from node state; avoid four duplicated raster icons per state if tinting can cover the difference. Use a deterministic fallback icon for unknown keys. Icon names are purely *visual vocabulary*, not promises about buffs or skill effects.

## 4. Portable Godot component / demonstration

Implement at minimum:

- `ui/preview/UI/components/worldtree.tscn` and companion script.
- Portable art resources within `ui/preview/UI/art/worldtree/`.
- Editable original sources in `sources/ui/worldtree/` and provenance/source-output bindings per existing repository practice.
- A standalone preview or showcase selector for `worldtree` with fixtures for the four canonical activation states and a fifth mixed state if useful.
- Tests and screenshots exercising one node, a trunk node, and a deeply nested terminal node with real native pointer and keyboard input.

Use the existing Godot 4.7.2 .NET-compatible native UI/Theme infrastructure and portable `res://UI/` layout. The scene must be independently loadable with only the portable `UI/` payload; no game-side C# dependency, Blender runtime dependency, absolute file paths or network downloads.

Suggested presentation API (adapt names to project conventions and document the final API):

```gdscript
# `topology` is the fixed shipped 24-node data file (IDs/parent/positions/icons).
# This snapshot is presentation-only; no game prices or abilities.
worldtree.set_data({
    "skill_points": 5,
    "selected_id": "root",
    "acquired_ids": ["root", "trunk_1", "trunk_2"],
    "available_ids": ["primary_left", "primary_center", "primary_right"],
    "icon_overrides": {"primary_left": "leaf"},
    "instant": true
})
# Signals: node_selected(id), node_action_requested(id)
```

The visual widget **must not subtract points or change ownership** on its own; emit an intent if a user requests a purchase. It may simulate acquisitions in its authoring-only showcase, clearly labeled as mock data. Keep locked/owned nodes inspectable and keyboard focusable; only an eligible purchase affordance should be disabled. Use `MouseFilter` appropriately: scenery passes/ignores pointer input while nodes remain native controls.

The selected-node footer should be compact and generic. The finished UI should show a Skill Points value at top-left, **no X/24 Owned counter, and no top-right stage/title text**, matching the latest selected screen direction. The standalone showcase can display stage labels outside the real UI for evidence.

Support correct scaling and panning/scrolling at `1100×820`, `1280×720`, `1600×900`, and `1920×1080`, without overlapping sockets or tiny illegible icons. Do not enlarge the tree into a fat trunk or hide terminal nodes offscreen without an explicit accessible scroll/pan affordance.

## 5. Proof that modules are independent

Provide reproducible visual proof for each of the canonical fixtures:

1. **Root only:** exactly 1 acquired node; only root/root-neighborhood alive.
2. **Trunk acquired:** exactly 3 acquired nodes (root + 2 trunk nodes); every branch still dead.
3. **Primary branches:** exactly 6 acquired nodes (root + trunk + 3 primaries); secondaries/terminals remain dead.
4. **Left branch family:** exactly 10 acquired nodes (root + trunk + left primary + its 2 secondary children + its 4 terminal children), leaving the center and right families dead.

Then test a controlled state change that activates just one more valid child under a selected branch; assert no sibling branch changes. Set the exact same snapshot twice and assert no duplicate nodes, no duplicate signals, and identical visual state. Test native hover, focus, mouse selection and keyboard navigation; camera/world input is not part of this repo's runtime but portable modal input must not leak through controls.

The code and its tests should **programmatically** assert `24 nodes`, `23 edges`, and the role counts. Generated reference-sheet captions are not acceptable count assertions. Capture real Godot frames at the supported sizes and examine the screenshots for visibly correct node positions, legibility, alive/dead continuity, clipping, scaling, and actual contrast. Run the relevant existing `mise run check`, `python tools/ui/validate.py --only skill-tree` (or a new independently selectable worldtree slice), UI-only payload audit, and packaging checks according to AGENTS/README. Do not claim a full existing suite passed if you only ran a filtered slice.

## 6. Required handoff/output

Deliver:

1. Source art, runtime assets and native Godot scene/scripts that actually render the 24-node tree.
2. The 30-icon source/runtime library with stable keys and sensible fallback.
3. A component API document with accepted snapshots and emitted intents.
4. Four source-bound native screenshots of the deterministic activation states, including at least one mixed living/dead configuration.
5. A strict node/edge count validation result and independent portable-load/package result.
6. A short inspection/acceptance report with original art files, export provenance, test commands and outcomes, and remaining risks.

**Do not change or claim to have implemented actual skill abilities, costs, balance, research authority, saves, networking, or the main game HUD.** Treat this as a standalone, reusable, visually excellent Worldtree asset component ready for a future, separately authorized game integration.

Create a reviewable scoped branch/PR only through the repository's existing workflow. Preserve historical accepted evidence and avoid rebuilding unrelated Blender libraries or refactoring the entire UI system.
