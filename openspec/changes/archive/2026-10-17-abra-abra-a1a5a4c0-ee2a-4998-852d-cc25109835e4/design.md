# Design

## Context

See `proposal.md` for motivation and `investigation.md` for native read/glob/grep evidence. Sources include manually edited Blender files and texture companions; generated GLBs are required deliverables, and some `docs/` images are catalog inputs or active hash-checked historical evidence. The reference-authority index distinguishes supplied art from generated diagnostics. `tools/asset_pack/test_vivid_review.py:30-46` requires real image/derivative hashes; AI texture tests preserve original/delivered/corrected comparisons. `tools/asset_catalog/ui_assets.py` checks current preview and payload dependencies. These contracts constrain cleanup more than filenames do.

No stat/Git/hash tool is available to Explore or, per retained answer `tracked-size-inventory`, the supervisor. Path existence is observed, but arbitrary paths' tracking status, sizes, duplicate identity, relative size distribution and Git/LFS storage are unknown. The supervisor explicitly directs a qualitative plan with first-Apply measurement. There is no quantitative savings estimate or guaranteed minimum reduction.

## Goals / Non-Goals

**Goals:** Apply one conservative cleanup of expendable PNG diagnostics under the bounded roots below; preserve useful art history and functional dependencies; quantify actual savings before deletion; prevent new evidence run accumulation with explicit retention checks.

**Non-Goals:** No history rewrite, Git garbage collection, LFS migration, personal-cache cleanup, Blender regeneration/re-export, texture recompression/downsampling, UI recapture, runtime optimization reversal, or deletion of authored sources/inputs/reference originals. Non-PNG archives, videos, JSON and large binaries are measured and classified but not removed in this change. No deletion outside the roots below, even if the inventory finds a larger opportunity.

## Decisions

### 1. Measurement first, safe selection second

After human plan approval, Apply obtains read-only Git-aware inventory at the assigned base and actual starting HEAD (record and explain any mismatch). Enumerate tracked paths from Git, not a filesystem walk alone; compute logical file sizes and SHA-256 image groups with installed Python/Git. Resolve Git's common directory for worktree object accounting; identify LFS attributes/pointers and available resolved payloads. Do not fetch/install assets or run maintenance to improve measurements. Record missing payload/storage-tool availability and conservatively exclude uncertain candidates.

Provide directory and extension totals, largest files, total tracked logical bytes, per-candidate-root totals, and duplicate-group potential savings without double-counting. Distinguish unique content bytes from per-path checkout bytes; Git may already store identical files once. Separate ignored/untracked summaries without deleting them. Use a compact report at `docs/repository-cleanup.md` and exact selected dispositions in `docs/evidence-cleanup.json`; avoid committing a huge all-file hash dump as new bloat. Full raw measurements can live in ignored scratch.

Alternative rejected: estimate savings from screenshot counts, image dimensions or old per-asset runtime reports. These cannot establish current file bytes or tracked size distribution.

### 2. Explicit candidate boundary

Only tracked `.png` files beneath this exact union are candidates (nested paths included):

- `docs/whisperwood/evidence/before/` and `docs/whisperwood/evidence/after/`
- `docs/quality-round-two/evidence/before/` and `docs/quality-round-two/evidence/after/`
- `docs/vivid-palette/evidence/before/`, `docs/vivid-palette/evidence/after/`, `docs/vivid-palette/evidence/browser/`
- The following children of `docs/ui/catalog/`: `browser/`, `mini-skill-tree-1/`, `mini-skill-tree-2/`, `mini-skill-tree-final/`, `native-5/`, `review-branch-artifacts-1/`, `vivid-palette-explicit/`, `whisperwood-1/`, `woodland-accepted/`, `woodland-final/`, `woodland-hover-refreshed/`, `woodland-live-resize-accepted/`, `woodland-reviewed/`, `worldtree-pre-review/`, `worldtree-prior/`, `worldtree-ready/`, `worldtree-shipping-refresh/`.

Directory presence alone is not eligibility. This enumerates historical render tiers, browser diagnostics and capture iterations discovered during Explore, not an instruction to delete entire directories. No implicit matching of future similarly named directories. `docs/**/evidence/sheets/`, focal PNGs outside these roots, all AI-texture/current seam evidence, runtime/ambient/dreamlike/detailed-ground evidence and all reference trees are excluded from removal.

Within this boundary, removal must satisfy one of:

1. **Unreferenced superseded diagnostic:** no consumer remains in repository text, structured records, tests, dynamic path-generation logic or catalog/payload closure; it is demonstrably a superseded run/tier, with a useful surviving comparison or newer relevant run identified. Unique failure/regression evidence and ambiguous art-review value are retained.
2. **Unbound exact duplicate:** measured byte-identical SHA-256 to a retained image; only mutable explanatory Markdown/HTML links need repointing, preserving revision/stage labels. A retained canonical copy must be useful and survive the cleanup; near duplicates or same-named different images do not qualify.

All immutable receipt/image bindings, current catalog/payload dependencies and active test/report input paths override both rules and remain unchanged, including historical bindings. A text search is necessary but not sufficient: inspect indirect JSON consumers and generated path logic. Unexplained references or selection ambiguity mean keep. Never delete an image merely because its palette is obsolete; grey-vs-vivid and three-revision regression comparisons can be useful.

Alternative rejected: remove all historical evidence or keep only one small sheet per campaign. That breaks current tests/provenance and requires a broader redesign of evidence contracts. Such a broader reduction needs separate scope and renewed approval; this plan deliberately accepts smaller savings.

### 3. Exact dispositions and reference handling

Before removing anything, `docs/evidence-cleanup.json` records selected path, base hash, bytes, classification, justification, known consumers, action, and retained replacement for consolidation. Include explicit protected/uncertain groups in the compact human report. Human approval authorizes these bounded rules, not automatic interpretation of every generated file as trash. Apply must stop on a needed expansion or protected-file change. If no candidates qualify, report zero eligible removals rather than force a cleanup.

Affected reference owners to inspect/update when applicable:

- Root README art/history navigation and reference-library links.
- `docs/whisperwood/README.md`, `actual-review.html`, `direction-review.html`; inspect `renders.json`, `completion.json` and `contact-sheets.json` as protected consumer evidence.
- `docs/quality-round-two/README.md`, `actual-review.html`; protected `renders.json`, `inventory.json`, grayscale receipts.
- `docs/vivid-palette/README.md`, `actual-review.html`; protected render/inventory/browser records and `test_vivid_review.py` consumers.
- `docs/ui/catalog/README.md`, `docs/ui/validation.md`, `woodland.md`, `worldtree.md`, `skill-tree-validation.md` and relevant historical review pages; protect selected `previews.json`, `worldtree-validation.json`, package and campaign records, plus their full transitive input closure.
- Catalog associations/manifest, reference index, static-site copy selectors and UI payload adapter: verify they need no path changes; any current input selected here is protected, not a cleanup target.

Do not rewrite historical JSON receipts or their hashes to hide deletion. Retire a mutable image link only with truthful prose identifying retained equivalent evidence; preserve failures and acceptance limits. Immutable commit/path recovery notes are optional supplementary history, never a new prerequisite for normal checks/builds. Keep source/external-reference licensing statements untouched.

### 4. Retention policy without invalidating bound generators

Add a small JSON retained-evidence allowlist, `docs/evidence-retention.json`, with monitored roots, exact retained PNG paths, per-path byte caps and concise grouped purpose/provenance. Monitor the candidate roots above plus existing `docs/**/evidence/`, `docs/ai-textures/{renders,comparisons,seams}/`, and `docs/ui/{previews,production,catalog}/` PNG evidence; exclude `docs/ui/references/` and all authored source/export trees. Implementation must enumerate the concrete existing matched evidence roots and document them; unknown future diagnostic roots require explicit promotion rather than broad ignore rules.

Implement a small dependency-free `tools/evidence_retention.py` validator and `tools/test_evidence_retention.py`. Existing `tools/checks.py:69-71` discovers fast tests, so no new CI service is needed. Validate actual PNG paths within monitored roots against exact allowlist entries, per-file caps and aggregate cap (initial aggregate is the sum of retained per-file caps). Reject missing entries/files, traversal, duplicates and exceeded budgets with actionable paths. Do not treat this budget as source/PNG freshness validation; existing byte/hash tests stay authoritative. Allowlist/budget increases require purpose/provenance and explicit reviewed edits, not automatic baseline regeneration on every run. No runtime asset budget is introduced.

Document ignored scratch/cache evidence as the default for screenshots and exploratory output. Existing capture scripts can write to docs by design and some are generator-hash bound; do not edit them or relabel their hashes. Stage their explicit runs in isolated disposable checkouts, inspect outputs, then promote only necessary evidence and its real binding records under existing authoring approval. This cleanup does not run a capture to refresh those records. Add brief navigation in AGENTS.md/README to the retention policy; existing `.gitignore` scratch/cache coverage is sufficient. Do not globally ignore PNGs or all docs.

Alternative rejected: change default output of hash-bound capture generators now. That would invalidate current native previews and require a separately justified recapture/qualification. The check catches accidental committed accumulation without that risk.

### 5. Size claims and acceptance

**Planning size distribution and expected saving: unmeasured.** No MB, percentage, duplicate count or ranking is claimed. Qualitatively, repeated image tiers/capture campaigns are plausible cleanup opportunities, while `.blend` and required GLBs may dominate total bytes. All candidates might be protected; zero eligible removals is a valid measured result, not evidence that broader deletion is approved.

After inventory, report gross eligible removed logical bytes `R`, added policy/report bytes `A`, baseline tracked logical payload `T`, and expected net `R - A` with MiB (`/ 1048576`) and percentage (`100 * (R - A) / T`). Allow negative net savings honestly if only guardrails are feasible. Re-measure final tracked payload consistently after changes, distinguishing pending tracked deletions/new files in the worktree from base Git entries. Report retained/removed counts and preservation hashes. Git packs, shared worktree objects and LFS historical payload are different denominators: normal deletion leaves old blobs reachable. No full-history clone reduction, remote storage reclamation, cache cleanup or history rewrite is promised or performed.

## Risks / Trade-offs

- [Conservative protection limits savings] → Report measured zero/small gains and return broader redesign for approval, not silent scope expansion.
- [Indirect consumer missed] → Trace dynamic producer/receipt closure, preserve uncertainty, run fast tests and offline index/static build, and inspect changed links.
- [Documentation loses useful historical meaning] → Keep sheets/focals, unique failures and immutable records; require equivalent retained evidence and honest labels for any consolidation.
- [Allowlist becomes another bulky artifact] → Keep only retained evidence paths/caps with grouped rationale, not full binary/image copies or repetitive all-file histories.
- [Accidental regenerated outputs] → Validation must not rebuild/re-export sources or run native capture; hash-check protected inputs before/after.
- [Growth can bypass an editable budget] → Make purpose/provenance and explicit review requirements visible; checks enforce declared bounds, not human approval authenticity.

## Migration Plan

1. Controller validates these planning artifacts and obtains human approval; no worker can approve this step.
2. Apply inventories read-only, resolves protected closures, records exact eligible dispositions and pre-deletion estimates. Stop for renewed approval if scope must change.
3. Delete only eligible paths, repoint eligible explanatory links, add retention guardrails and guidance. No authored/required-export/reference/current-image byte changes.
4. Run `mise run check`, focused retention/catalog/UI tests and `mise run catalog-build` in an isolated environment. Verify unchanged catalog IDs, native selected-image hashes, runtime payload member identities and model export hashes. Static packaging may generate ignored output only; it must not invoke Blender/Godot. Validate changed local Markdown/HTML image references and image loading; if a page changed, perform task-owned browser checks with scratch-only screenshots.
5. Produce measured before/after report. Controller owns independent review/delivery. Rollback uses an ordinary corrective revision restoring only this cleanup's deleted paths and link/policy edits from recorded base identities; no history reset/rewrite or unrelated work removal.

## Open Questions

Measured sizes, duplicate groups and exact eligible rows are intentionally deferred to the first Apply task under the retained supervisor decision. They do not change the approved selection rules. Any result requiring broader deletions becomes a new scope decision, not a deferrable implementation choice.
