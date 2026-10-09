# Progressive UI roadmap

Authorized scope remains discovery → design → planning → production foundation →
components → HUD/menu compositions → migration preparation, with continuous
validation. **Actual migration, merging and runtime game changes are not included.**
A–C is the first delivery, not completion of the overall UI system.

## Resume state

Current phase: intended standalone **E–G completed**, coordinated delivery handoff
pending. Accepted M0/M1/representative evidence preserved. `production.md` records
fresh **637/0, 79 image bytes with visual-review coverage**, serial OS 11+64, independent UI-only audit
and historical failures. `coverage.md` distinguishes the finished standalone
boundary from exhaustive Cartesian products and separately authorized integration.
Machine authority for status/dependencies/acceptance: [tasks.json](tasks.json).
Inventory: [inventory.json](inventory.json). Exact approval: [decisions.md](decisions.md).
Read [discovery.md](discovery.md) before investigating again; source is pinned.
Read [art-direction.md](art-direction.md) and actual previews before resolving
`artistic-approval`. If game inputs change, re-pin relevant evidence rather than
launching/building/importing the game checkout. Label-removal work is pending;
this plan neither grants permission for it nor reintroduces removed world labels.

## Milestones

1. **M0 — A–C discovery / alternatives / plan.** Read-only game evidence,
   original Ledger/Watch comparisons, inventory, minimal layout, machine tasks
   and initial migration mapping. Actual captures/PNG/plan checks plus manual
   image review establish this milestone only. Request artistic approval.
2. **M1 — D first end-to-end vertical slice, approval-dependent.** One approved
   native Theme; reusable resource ledger plus upkeep summary; one optional
   fixed-size original seal refined for the existing start-menu header; owned
   showcase/capture and data/signal interfaces. Prove editable source → Blender
   export → Godot import → screenshot → issue/revision log. No large generic
   pipeline. Validate first two target sizes then 1600×900/1920×1080 before
   component acceptance. At most two justified revisions before review.
3. **M2 — E core interaction building blocks.** Quote/eligibility control, city
   navigation, phase/ready/pause, connection feedback, native dialog styles.
   Exercise actual semantic states, pointer and keyboard, focus, scroll and
   modal input boundaries. Long text and read-only states before ornament.
4. **M3 — E inspection blocks.** Unit profile slot, health/status treatment,
   field/storage capacity and roster, research choice/prerequisite/lock rows.
   Preserve data semantics and no gameplay logic in this repository.
5. **M4 — F full compositions.** Settlement HUD, Details, personal research,
   Town hall; start/multiplayer, Graphics/Audio/About and confirmations. Mock
   actual systems, no new game feature. Four measured target sizes, dense
   strings/rosters and paused/lost/foreign/outcome states. Review screenshots
   for hierarchy, noise, surface unity and legibility at actual size.
6. **M5 — G migration preparation.** Fresh independent resource load/import,
   dependency/path audit, source/output linkage, ordinary PNG dimensions/bytes/
   decoded-size budgets and slice/alpha validation; explicit adapter APIs,
   replacement order and integration risks. No Blender at runtime. Not a
   migration or proof of native GPU performance.

Coordinate logical milestone commits/publication with MAIN. Configured
no-mistakes owns delivery review/fixes/tests/docs/lint/push/PR/CI after the
appropriate milestone, not artistic approval. Do not independently publish or
commission another reviewer while deciding the direction.

## Keep / redesign / missing

**Keep:** native interaction/layout/focus, authoritative quotes and eligibility,
exact resource/income/upkeep meanings, scrollable inspection, existing session
and settings services, health/status shape/text signals. Current off-the-shelf
art is not automatically bad or disposable.

**Redesign proposed:** shared hierarchy and native surfaces; cramped action/cost
and multiline research/roster presentation; clearer phase/readiness versus local
settings; uniform feedback/dialog presentation. Risks require current rendered
validation, not historical screenshot guesses.

**Produced here:** portable scene/component package, original-source render linkage,
functional standalone showcase, UI-specific validation/state review and migration
manifest/APIs. No missing RPG gameplay panels; generic assets explicitly rejected.

## Approval and unresolved questions

- Resolved: Ledger; only the small original menu seal as initial Blender decoration.
- Resolved technical blocker: in-tree native Control modal replaces the newly
  authored unreliable embedded Window shell. No new artistic decision required.
- New font remains a future decision, not a dependency now. Default Godot font
  with clearer scale is the low-risk initial recommendation.
- Current-game visual/interaction baseline and label-removal result need refreshed
  read-only evidence before migration. Older docs screenshots are not current.

Approval records must name decision, date/authority, exact direction/revision and
scope. Technical decisions within approved style remain autonomous. M1 and the
representative milestone are accepted/preserved; intended M2–M5 standalone criteria
are now complete per `coverage.md`: meaningful HUD/city/session edges, expanded
Details receipts, empty/stale/storage/recovery/sale hall, four-size base dialogs,
portable payload and adapter preparation. No exhaustive service/platform campaign
is silently added as a standalone blocker. Future target integration is not done.
A generated file never constitutes tested acceptance. Report checked commit/coverage
to MAIN for its coordinated same-worker delivery workflow with original captain
intent and exact Ledger/small-seal approval; no independent pipeline/publication.
