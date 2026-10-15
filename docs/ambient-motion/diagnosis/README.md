# Retained verification failures and boundaries

These are failed observations, not accepted checks. Final successful commands
and exact artifact bindings are in [checks.json](../checks.json).

- `float-read-first.log` and `float-read-second.log`: the original strict
  normalized-float comparisons disagreed on different Non-Color maps.
- `fresh-original-map.json`: one affected map's baseline/palette/final packed
  bytes and fresh decoded reads agreed exactly.
- `sequence-counterfactual.json`: a complete sequence probe found no differing
  sources in that run; it does not establish deterministic Blender reads.
- [The raw API probe](../pixel-api-probe.json) subsequently found repeat-read
  instability even in a fresh process. **No specific Blender/cache mechanism is
  established.** Exact packed 8-bit PNG/sample proofs replace that unsuitable
  normalized-float hashing method under explicit authorization. The source files
  and texture maps were not changed to make the audit pass.
- [The real-source controls](../encoded-map-controls.json) include separate-process
  baseline/palette/final reads, repeat positives, and true one-sample mutations
  with the same image/node identity. The final fixtures also reject color-space,
  binding, mapping, routing and use-state changes. Initially calling `pack()` on
  an already-packed image did not embed the changed test PNG; that unmodified
  intermediate was not counted as a negative control. Correct controls explicitly
  reload and repack the changed task-local data.
- `viewer-classification.log`: compositor Viewer and empty Render Result IDs are
  unbound, nonpersistent presentation buffers, not encoded source texture maps.
  They remain inventoried with metadata and zero-ID-user checks. Binding either
  as a texture fails; no unsupported texture is silently omitted.
- `incomplete-fixture-job.log`: a new fixture omitted canonical selector fields.
  The complete four-field job contract was inspected and corrected for collection
  and object selection without changing production selection semantics.
- `metal-mine-shutdown.log`: a renderer crashed on shutdown after writing poses.
  File existence was not treated as successful execution. A clean retry exited
  successfully; final pose/camera/derivative receipts reference successful jobs.

All source checkpoint copies, raw arrays, intermediate controls and complete
worker logs remain in the task-local `.cache/ambient-motion/` / `.cache/asset-check/`
while this worktree exists. They are not required new game/runtime dependencies.
