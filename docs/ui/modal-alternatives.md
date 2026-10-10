# Historical native modal ownership candidate — contrary result

This record preserves the failed Window candidate and then-proposed corrections.
The in-tree Control alternative was subsequently implemented; see
[modal lifecycle](api.md#local-modal-lifecycle) and [production.md](production.md).
Pending/source-state statements below refer only to this historical checkpoint.

Inbox 004 authorized one bounded ownership-based candidate and required stopping
if its focused reproduction still failed. **It failed; no whole-suite retry.**

## Candidate and falsifying observation

Version-matched installed Godot 4.7.2 API documentation describes
`Node.get_last_exclusive_window()` as the containing Window or last exclusive child
in its chain; native `Window.popup_exclusive_*` helpers parent dialogs there.
Changed prototype dialog parenting from the UI `Control` to
`get_last_exclusive_window().add_child(dialog)`, retaining transient/exclusive.
Removed the previously disproved popup-window flag. Confirmation parenting was
made consistent with that ownership, and the world guard now covers the dialog
reference/native exclusive chain instead of searching only the UI Control's children.
No test refocus, global Esc handling, assertion removal or source-art expansion.

Fresh exact full synthetic sequence:
`.cache/ui-diagnosis/full-synthetic-none-owned-window/probe.log`.
Native observations show:

- Actual parent type **Window**, path `/root`.
- `last_exclusive=/root/PreviewDialog` both before and after the outside click.
- `embedded=true`, `transient=true`, `exclusive=true`, `popup_window=false`.
- Focus true after dropdown history, Fullscreen selection and slider edit.
- Outside click changes Window focus to false while retaining slider Control focus.
- Final unchanged Esc reaches root Window only; `canceled=0`, `close_requests=0`,
  Settings stays visible; zero leaked world actions.

Thus simple Control parenting or missing native exclusive-child registration is
**not the sole explanation**. Correcting that ownership alone does not establish
the required contract on this embedded backend. The underlying engine behavior
remains unknown; no engine bug, SDK upgrade or alternate GPU is asserted as a remedy.

Stopped after this first focused candidate check, per instruction. Did not run
another OS-after check or broad acceptance after the synthetic candidate already
failed. Earlier OS XTest failure and diagnostic focus-restoration success remain
in `settings-diagnosis.md`, not relabeled as evidence for this candidate.

## Minimal competing implementations (not implemented or accepted)

### A. Keep native Window, component-local guarded focus restoration

Own the modal's focus-exit lifecycle. If it remains visible and no owned native
child popup has taken input, defer a native Window focus restoration. Closing/
hiding and child-dropdown ownership must suppress restoration. Keep native
AcceptDialog cancellation and close-request, actual keys, existing local world
blocking and opener focus return. No unconditional root Esc consumer.

Evidence favoring it: the small diagnostic `Window.grab_focus()` counterfactual
already makes the unchanged failing Esc cancel Settings. This is presently only
a masking observation; production lifecycle handling would need its own proof.
Likely small source change (~10–25 lines plus focused tests) and least visual/API
change. Risk: steals focus from dropdowns or nested confirmation windows, races
hide/application focus loss, or varies by backend; needs careful child-popup and
teardown checks. Must not keep pulling focus when the application loses OS focus.

### B. Replace only prototype modal internals with in-tree native Controls

A visible full-rect input-blocking Control/scrim with a centered themed
PanelContainer, native ScrollContainer/content, close/cancel Button and a local
visible-modal cancel/focus controller. Keep OptionButton/PopupMenu, HSlider,
TabContainer and native Button events. The modal is in the same viewport as its
invoker, removing the disproved embedded Window focus boundary. Outside clicks
stop at the scrim and do not dismiss; dropdown-first Esc stays native; subsequent
Esc closes only the visible modal and restores its invoker's focus.

Roughly 70–120 lines of composition/local lifecycle instead of flag toggles.
Clear scene hierarchy and predictable same-viewport layout; existing content
components and Theme remain reusable. Trade-off: locally owns modal focus scope,
cancel/close and layout rather than inheriting AcceptDialog's embedded window
header/ownership. Requires explicit keyboard focus containment and child-dropdown
cancel tests. Not a new global input router, gameplay service or dependence on the
game. Migration must document this composition boundary and retain the game's own
local world-input guards. No major artistic change: same approved Ledger surfaces.

Recommendation if further correction is authorized: **B** removes the now-proven
unreliable embedded Window boundary rather than repeatedly repairing its focus.
A is smaller but maintains the backend-sensitive focus relationship. This is a
technical recommendation, not another artistic approval request.

## Preserved state

Twelve focused fresh processes total across inbox 003/004; all logs retained.
Current ownership candidate and all earlier uncommitted component/prototype/tool
work are preserved. M0 remains last accepted commit. No production milestone,
new full-source acceptance, final 27-frame visual acceptance, pipeline, push, game
mutation or migration. Await guidance before implementing another candidate.
