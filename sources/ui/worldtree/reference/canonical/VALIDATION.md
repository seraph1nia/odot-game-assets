# Canonical Worldtree structure checks

All values below are derived from `worldtree_topology.json` and verified during pack generation.

- Node count: **24**.
- Directed parent-child edge count: **23**.
- Roles: root=1, trunk=2, primary=3, secondary=6, terminal=12.
- Every node has a stable unique ID.
- All non-root nodes have exactly one existing parent.
- Each node has a valid ancestor chain to the root (no cycle).
- Root has one child (`trunk_1`).
- `trunk_1` has one child (`trunk_2`).
- `trunk_2` has three children (left, center, right primary branches).
- Each primary has two children, each secondary has two children, each terminal has none.
- Acquired fixture counts, in order: **1, 3, 6, 10**; every acquired set is ancestor-closed.

Treat these as code-level acceptance tests in `odot-game-assets`, not just a design document. The machine-generated SVGs use these nodes/edges and are the accurate reference, even if a concept-art poster shows fewer or more circular sockets.
