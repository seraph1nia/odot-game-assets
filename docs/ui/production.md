# Ledger production — checked M1 foundation, broader acceptance continues

## Current checked milestone

Ledger/only original small menu seal approved in `decisions.md`. M1 D foundation
is checked: reusable Theme, resource/upkeep scenes, retained editable source/PNG
linkage, independent namespace, owned input/capture runner and actual visual review.
The local modal is also behaviorally checked. **This is not overall A–G completion,
production-ready game integration, or acceptance of every implemented prototype.**

Final fresh unchanged-source run: **271 checks, zero failures, 27 frames**, full log
`.cache/ui/m1-tab-scope/tests.log`, result/source SHA-256 bindings
`production/m1-tab-scope/results.json`. Godot 4.7.2 .NET, owned Xvfb, Compatibility/Mesa
llvmpipe, Dummy audio. Import has no errors; V-Sync driver warning is retained.

### Resolved ui-dialog-escape

Inbox 005 authorized replacing only newly authored modal internals. The reusable
`UI/components/modal.tscn` is a full-rect blocking scrim plus native centered
PanelContainer/header/ScrollContainer/content/footer. Its small script scopes
input to the visible modal, leaves owned native dropdowns first refusal, contains
Tab/Shift-Tab, consumes its cancellation event before underlying input, and restores
a valid visible invoker on close. Hidden scopes disable processing. It never grabs
Window focus on application focus loss. Confirmation uses the same local boundary.

The exact original sequence remains in `tests/run_ui.gd::test_dialogs()`: Settings
→ Enter dropdown → dropdown-only Esc → Fullscreen selection → Audio keyboard
slider → outside-world click → Esc closes Settings and returns invoker focus.
No moved/weakened assertion, test refocus before cancellation, direct test cancel,
new global router, preference/service logic or game changes.

Final OS XTest checks: **11 full-sequence checks** and **64 modal-scope checks**,
logs `.cache/ui-diagnosis/{full,modal}-os-none-m1-tab-scope/probe.log`. Actual X11 keys,
Shift-Tab, pointer/tab/slider, nested confirmation, Enter close, hide/reopen,
application focus away/back on a second owned X11 window, invoker return and zero
leaked world actions pass. An unhandled-input spy proves active dropdown/modal Esc
never reaches underlying input; deliberate hidden-modal Esc does reach it.
Earlier isolated baseline/dropdown/Fullscreen/slider-focus/slider/outside cases
all passed in fresh processes on both routes under `*-none-control-modal/` logs.
Full automated acceptance reuses the same focused scope checks.

### Actual visual review and one targeted layout correction

All **27 final frames** were actually inspected at their native dimensions through
image attachments: HUD/menu at 1100×820, 1280×720, 1600×900, 1920×1080; seven modal
compositions at the first two sizes; preparation/shortage/lost/combat/foreign at
1280×720. Final frames are byte-identical to the inspected `control-modal-r1/`
frames; SHA-256/dimension/review bindings are in `visual-review.json`.

Judgment: cream planes/dark ink remain cohesive with approved Ledger; amber primary
and muted rose irreversible actions are distinguishable; teal 2px native focus
outline is clear; quantities remain right-aligned/exact. Menu title/seal/primary
order reads cleanly; the unchanged 48px relief is subordinate. Four-size pixel-
preserving layouts keep legible body/control text, not scaled screenshots. Settings
scrim/close/tab/content hierarchy is clear and body text stays inside its panel.
No missing resources, glyph boxes, ornamental stretch or non-scroll text collisions
seen. The sparse tabletop is explicitly abstract mock context, not game art evidence.

First Control-modal full run (`control-modal-final/`) failed one of 264 checks:
long mock return-intent feedback grew the preparation footer to touch the upkeep
panel at 1280×720. A single 12px upper-stack offset correction produced breathing
room without shrinking text/removing content. `control-modal-r1/` passed 264;
then test-only coverage grew for OS focus loss/underlying-Esc evidence, and the
a source-bound run passed 267. Local focus traversal was then corrected to include
native internal TabBars/scrollbars (excluding child Windows). Added checks prove Tab
actually reaches categories and Right/Left changes them, not just containment among
other controls. Final fresh automated/OS/payload processes passed 271/64/9 scenes.
All prior failures remain failures; no source changed during final validation.

### Remaining acceptance, not silently waived

Dense research/Town hall/Details/friends show nested body/list scrollbars and some
rows below the visible fold. Need a simpler scroll ownership decision plus actual
wheel/long-focus traversal before M3/M4 acceptance; geometry alone is insufficient.
Menu multiplayer/back/host, complete About/update/error and friends busy/refresh/
long-name state input coverage remains partial. Inspector/model-preview slot,
all research state interactions and full roster transfer intents remain future
acceptance. E–G tasks are in progress, not completed because scripts exist.

Not established: current-game theme baseline, localized/RTL/extreme-window/HiDPI,
physical keyboard/audio, native GPU/compositor, older engine, controller/mobile or
runtime game behavior. Game stretch-policy/label-removal compatibility is a later
separately authorized migration gate. No dependency install, extra art, pipeline,
push, merge, release or migration. `payload.json` and `api.md` define this milestone's
portable boundary and remaining adapter responsibilities.

---

## Historical pre-005 checkpoint (not current state)

The following retained record describes failed Window-based work before the
in-tree correction; pending/blocking statements below are historical only.

### Ownership alone disproved

Inbox 004's single native ownership candidate also failed the exact focused
sequence. Dialog is a direct child of root Window and reported as its last exclusive
child; outside click still drops Window focus and final Esc reaches only root.
No broad retry or second speculative fix. Twelve focused processes total;
all prior logs and source are preserved. `modal-alternatives.md` records exact
contrary observations and trades: local guarded focus lifecycle versus replacing
only modal internals with an in-tree native Control composition (recommended).
No final capture/production acceptance or migration. Await guidance.

## Earlier bounded diagnosis

Inbox 003 authorized causal investigation, not another broad retry. Eleven fresh
focused probes now isolate the outside click as the trigger: embedded Window focus
drops while Control focus remains, and Esc reaches only root. Slider/dropdown/
Fullscreen-only cases pass. Actual owned X11/XTest keys and pointer reproduce the
same failing full sequence. Diagnostic-only native focus restoration makes Esc
cancel Settings, but is a masking condition, not a production fix.

A single native candidate (`popup_window=true`, retaining transient/exclusive)
failed the next same-sequence focused check. Stopped as instructed; the candidate
flag and contrary evidence remain preserved, no full acceptance rerun or assertion
change. Detailed trace/outcomes/falsifiers: `settings-diagnosis.md`. Explicit local
world-input guard has fresh bounded evidence (zero leaked clicks in all cases),
but no full acceptance. Need guidance on the unresolved native modal ownership/
focus boundary before continuing. All prior captures remain unaccepted.

Approval recorded in `decisions.md`. New production work is preserved in this
worktree and is **not an accepted milestone or production-ready package**.

Implemented but not fully accepted: native Ledger Theme authoring/export,
resource/upkeep/quote/city/phase/session/unit/roster components under
`ui/preview/UI/`, only the approved original menu seal (moved, unchanged bytes),
mock HUD/menu/research/Town hall/settings/Details/friends/state compositions and
owned native-input/layout/capture tests. No game mutation or runtime game dependency.

## Earlier blocker: ui-dialog-escape (now resolved above)

Two bounded graphical checks were executed:

- `.cache/ui/initial/tests.log`: 185 assertions, three failures (local-world input
  blocking, Esc close, information/footer separation), plus menu script parse error
  from naming a member `multiplayer` which collides with Godot's native property.
- `.cache/ui/corrected/tests.log`: 209 assertions, **one remaining failure**:
  `Esc closes dialog`. Other declared native assertions completed, but this is a
  failed overall gate. 27 actual captures were generated in each run; corrected
  captures have not yet received full visual review and must not be marked accepted.

Reproduction sequence in `ui/preview/tests/run_ui.gd` / `test_dialogs()`:
open Settings → open dropdown via Enter → Esc closes dropdown while dialog stays
open → select Fullscreen with keyboard → Audio tab → keyboard slider adjustment →
outside-world click → Esc. The Settings dialog remains visible at the final assertion.

Corrections already attempted: exclusive native modal window, compact information
panel spacing, ink-colored embedded native close mark, relocation of reconnect/
fresh controls to the match column, pixel-preserving footer bounds, menu member
rename. Native world blocking and geometric overlap assertions passed in the
corrected run. An additional explicit local-input guard was added during that run;
that source edit is not yet validated on a fresh process. No third retry was launched.

Selected original failed visual evidence and failed results remain under
`docs/ui/production/history/initial/`. Corrected actual frames are under
`docs/ui/production/` and results still record the failure. Renderer logs identify
Godot 4.7.2 Compatibility / Mesa llvmpipe, owned Xvfb, Dummy audio; no native GPU,
performance or game integration claim.

Per worker contract, stopped after the repeated obstacle and asked Firstmate for
guidance. D remains in progress; E–G are not marked complete. Partial source work
is uncommitted on the preserved task branch; the last accepted commit remains M0
`7739e31933b7178c4ab5d334213a7384d762b177`. No pipeline, push, merge or migration.
