# Ledger production — finished intended standalone package

## Current host dialog-close acceptance

The host now synchronizes its screen mode/caption at the modal's shared `closed`
boundary, returning to the actual underlying HUD or menu. Modal hiding, input scope,
invoker focus return and confirmations remain owned by the existing modal lifecycle;
no forced reselect or extra user intent. Native regressions close and reopen the
identical selector item for all six dialog options, cover Esc/header/footer controls,
check focus return/no extra intents, and retain the menu under direct Settings closure.
The original Settings sequence and all accepted modal/scroll/input assertions remain.

The new regression executed against the pre-fix host at `cb1d78a…` in a private
assets-only copy: **300 focused checks / 19 failures / 0 captures**. Same-item reopening
and restored HUD assertions failed for all six options. Failed result retained in
`production/review-dialog-close-before/results.json`; full log
`.cache/ui-dialog-close-before/.cache/ui/before/tests.log`. This is deliberate pre-fix
regression evidence, not a passing gate or current source acceptance.

Fresh normal source-bound acceptance: **637 checks / 0 failures / 79 captures**,
`production/review-dialog-close/results.json`, `.cache/ui/review-dialog-close/tests.log`.
Serial owned X11/XTest original Settings **11/0**, modal lifecycle **64/0**, zero world
leaks: `.cache/ui-diagnosis/{full,modal}-os-none-review-dialog-close/probe.log`.
Fresh private UI-only audit: **nine scenes, Theme/seal, 32 files**,
`.cache/ui-payload/review-dialog-close/load.log`, current `payload.json` hashes.
Nine focused metadata/provenance contracts validate current and preserved evidence.
Full repository test/lint gates remain outer-pipeline-owned.

All **79 current PNGs are exact SHA256 matches with identical dimensions** to the
previous reviewed set. No changed bytes and no new image inspection claimed.
`visual-review-dialog-close.json` binds the new set to unchanged
`visual-review-review-fixes.json`; earlier historical bindings/results/failures remain
intact. Byte-identical visual inheritance does not replace the fresh source acceptance.

Same limits: Godot **4.7.2 .NET**, Xvfb, Compatibility/Mesa **llvmpipe**, Dummy audio;
mock-data controls, not game services/authority or physical/native-GPU/FPS/VRAM proof.
Unit preview remains Label-only, long-name tooltip keyboard discovery unestablished,
scroll ownership construction-time. No game access/write/import/build/launch,
migration, dependencies, installs, extra art or Blender regeneration. Only assigned
review work ran; the outer executor owns delivery and remaining gates.

## Historical first review-fix acceptance

The approved standalone scope is unchanged. Review fixed implicit 3D discovery of
only the two 2D seal sources, removed source-text portability proxies, made retained
acceptance byte contracts independent of historical Git objects, and synchronized
screen/state/selection captions without additional intents. Native navigation
regressions cover Market → Menu → Solo, both city directions, native state/selection
changes, dialog selector navigation and Return confirmation. Original Settings
order/assertions, modal lifecycle, scrolling and world-input gates remain intact.

Fresh normal acceptance: **588 checks / 0 failures / 79 captures**, source-bound
`production/review-fixes/results.json`, `.cache/ui/review-fixes/tests.log`.
Serial owned X11/XTest Settings **11/0**, modal **64/0**, zero world leaks:
`.cache/ui-diagnosis/{full,modal}-os-none-review-fixes/probe.log`.
Independent private UI-only audit: **nine scenes, Theme/seal, 32 files**,
`.cache/ui-payload/review-fixes/load.log`, current hashes in `payload.json`.

All **19 changed PNGs were opened at native dimensions**: eight start/multiplayer
frames at all four desktop sizes and eleven 1280×720 HUD state frames. Menu now
shows Menu; each state caption agrees with the corresponding projection. Approved
cream/ink/amber/rose surfaces, teal focus, fixed seal and layout hierarchy are
unchanged; no new clipping/overlap or visual regression observed. Read-only quote
reasons still intentionally extend below the scroll fold. The remaining **60 PNGs
are exact SHA256 matches** to the retained submitted image set.
`visual-review-review-fixes.json` binds all 79 current bytes and the inspected list;
`visual-review.json` remains the unchanged submitted binding, not current source
acceptance. M0/M1/representative results, IDs, original visual bindings and genuine
failed evidence are preserved. `preservation.json` freezes retained result bytes,
including recorded source hashes; it does not reconstruct historical source files.

Focused Python verification: **four export-plan tests** and **nine UI
metadata/provenance contracts**. Full repository test/lint gates are left to the
outer pipeline; historical 58-test results below are not a new gate result.

Platform remains Godot **4.7.2 .NET**, owned Xvfb, Compatibility/Mesa **llvmpipe**,
Dummy audio. This is mock-data/native-control coverage, not physical input, native
GPU/VRAM/FPS or game integration. Unit preview was tested with a Label, not a model;
long duplicate friend identity may require a tooltip, with keyboard-only discovery
unestablished. Scroll ownership remains construction-time. No game access/write,
import/build/launch, migration, installs, dependencies, new decoration or Blender
regeneration occurred. Only this review phase ran; the outer pipeline owns delivery.

## Historical submitted standalone E–G acceptance (inbox 007)

MAIN directed continued autonomous completion, accepting the previous representative
commit `a8cf17354c120f7775dabe3e60d2c1e0a54142ae` without mistaking it for full
integration. The intended **Phase E component library, Phase F functional mock
compositions and Phase G migration-ready package are now complete and checked**.
Meaningful discovered UI states, intended desktop dimensions and projection/intent
interfaces are the boundary, not new exhaustive services/platform cross-products.
`coverage.md` and `tasks.json` give current scope; publication/game integration
remain unauthorized and unperformed. Historical M0/M1/representative records below
remain as accepted, with recorded source bindings and exact image bytes preserved.

### Added functional projections and input

- Details native planning/paid-current-wave/last-completed-wave/fresh selector and
  `set_data()` projection seam. Current/previous receipt, forecast, reward, roster
  and allocation remain separate. Fresh removes prior values rather than leaking
  a previous wave. Host selects paid for combat, last for victory/defeat. External
  foreign inspection annotation survives switching. No reward/upkeep computation.
- Hall native occupied/empty/stale/storage/recovery/fragmented selectors and supplied
  `set_data()` seam. Independent storage/healing quotes and supplied per-unit recovery
  text; selected id and read-only gate survive roster interactions. Empty hides stale
  inspection actions and permits projected sale; occupied sale/stale commands reject.
  Storage II→III **12 gold / 2 wood / 3 stone**, 12→18 capacity, verified against
  pinned game source—not derived from authority locally. Recovery distinguishes
  funded wounded survivor, unfunded reserve and full-health projections. Size-two
  transfer cannot use separate free sizes 1+1; no pooling/transfer/healing gameplay.
- Lobby Start, fallen-owner/no-future-income with shared pause, stale HUD inspection;
  connecting/connected/reconnecting/expired/rejected feedback selectors and fresh
  intent; native one/four-city navigation, construction groups, ranged recruiter
  and insufficient Mage quote. Intents leave mock resources/world clicks unchanged.
- Original Settings sequence, all old component/phase/layout/modal assertions and
  real wheel/far-row interaction tests remain intact; no weakening or test cancellation.

### Fresh unchanged-source acceptance

**568 checks / 0 failures / 79 actual captures**, Godot **4.7.2 .NET**, owned Xvfb,
Compatibility/Mesa **llvmpipe**, Dummy audio. Logs `.cache/ui/standalone-final/tests.log`;
source hashes, actual dimensions/renderer and results in
`production/standalone-final/results.json`. Focused added-input acceptance:
**231/0** (`standalone-focused-1`). No failed new gate; earlier failures remain failed.

Serial owned OS XTest: **11 full Settings / 64 modal checks, zero world leaks**,
`.cache/ui-diagnosis/{full,modal}-os-none-standalone-final/probe.log`; both driver
commands exited 0 without infrastructure race. No physical-input claim; added
composition inputs otherwise use native injected Godot events.

Fresh private UI-only audit: **nine scenes, Theme/seal, 32 files**,
`.cache/ui-payload/standalone-final/load.log`, current hashes `payload.json`.
No prototypes/fixtures/services/game/tools as runtime dependencies. Total audited
file bytes **100,661** (not engine package/GPU cost); only original 192px/48px seal
**34,237 PNG / 147,456 decoded RGBA bytes**. `api.md` specifies all scene data/signals,
Details/hall mock projection seams, scroll lifecycle, authority and migration order.

### Actual image review and art judgment

All **79 final image bytes reviewed**: **50 new/changed frames opened** at native
size, **29 exact SHA-256 matches** to previously inspected representative frames.
No changed view inherits old acceptance. `visual-review.json` binds the ordered
all-image digest/dimensions, explicit newly inspected filenames and prior byte
bindings in `visual-review-components.json`. Plan checks verify this coverage.
M1 original binding remains byte-for-byte `visual-review-m1.json`.

HUD, start/multiplayer and all seven base dialogs at **1100×820, 1280×720,
1600×900, 1920×1080**; About-error/long-friends/scrolled-lock also four sizes.
Details paid/last/fresh and hall empty/stale/storage/recovery/fragmented at two smaller
sizes; eleven meaningful HUD state frames at 1280×720. This is not a claim of four
pictures for every state.

New frames retain approved cream/dark ink, quiet amber primaries, muted rose
permanent actions and teal native focus; no further decoration family/font/art.
At larger sizes, deliberately centered bounded dialogs keep readable line lengths
and stable controls rather than filling the entire viewport. Empty/fresh messages
have adequate breathing room; storage prices/upgrade outcomes and stale reasons
wrap without non-scroll overlap. Paid/previous/forecast headings distinctly identify
receipt timing, with reward separate. Fragmented destination and recovery reasons
stay text rather than icon-only eligibility. Dense hall/allocation/research/friends
continue below the fold intentionally, with one body scroll and stable Close; actual
wheel/focus tests prove hidden-row access. Very long duplicate names still ellipsize
before Invite with full tooltip identity; inline suffix/keyboard tooltip discovery
is not guaranteed. New lobby/outcome/fallen/stale HUD controls and status text retain
separate city/context/match hierarchy. No missing glyph or non-scroll collision
observed. The abstract tabletop is preview context, not a claim about the game's
current 3D world or projected health.

Metadata/history/source/image/payload contracts **9 passed**;
`.cache/ui/standalone-final/plan.log`. Offline fast repository **58 tests and two
inline JavaScript programs passed**, lint/syntax/guardrails;
`.cache/ui/standalone-final/repo-check.log`. Whitespace passed. No
configured delivery pipeline, push, PR, merge, release or migration runs here.
No game edits/refs/import/build/launch, dependencies, shared Blender/MCP mutations
or world palette changes. External risks stay external per `coverage.md`, not
unbounded new standalone acceptance criteria.

---

## Historical accepted representative package (inbox 006)

Accepted M0/M1 commits and their exact evidence are preserved. M1 at
`eb8ec20ca33ecc94ebcfd9ccb4ccf218562103cc` remains FOUNDATION/modal only.
This next package checks representative standalone E–G interaction contracts;
**it is not full production completion, game integration or publication**.

Final unchanged-source acceptance: **438 checks, zero failures, 35 captures**,
`.cache/ui/production-package-reviewed/tests.log`; hashes and results in
`production/production-package-reviewed/results.json`. Same Godot 4.7.2 .NET,
owned Xvfb, Compatibility/Mesa llvmpipe, Dummy audio. No installation or new art.

### Implemented and exercised

- One vertical body-scroll owner for research, Town hall, Details and friends.
  `WatchUI.scroll()` disables embedded list scrolling when an ancestor owns it;
  standalone lists retain their own scroll. Modal body follows native focus.
  Actual wheel/reverse-wheel events move each body; long Tab traversal reveals
  whole far-row buttons and Enter activates the correct opaque id. Child native
  dropdowns in separate viewports retain independent popup scrolling.
- Research native class and access selectors cover all three five-node paths,
  owned foundation, available specialization, insufficient points, permanent
  sibling locks, funded mastery, foreign/paused purchase suppression. Points,
  progress and tower-rate text stay separate; mastery explicitly replaces effect.
- Exclusive native roster selection, independent healing quote, reserve transfer
  and permanent retirement intents include selected unit/destination identifiers.
  Selection preserves read-only gates. Field-to-storage destination availability,
  no destination, exact low-health projection and adapter-owned native preview
  slot are exercised; no model loader or gameplay added.
- Friends populated/offline/empty/busy/refresh-failure/invite-failure/long duplicate
  name projections: native Refresh, far-row invitation, immediate busy disabling,
  one intent, deferred mock result/retry feedback, ellipsis and full-name tooltip.
  No Steam query/send. Mock completion is not an asynchronous service simulation.
- Graphics/Audio/About: retained original Settings sequence, native zero-volume,
  six update/save feedback projections, native mock check button. Return-to-menu
  confirmation cancellation/focus return and confirmation navigation. No HTTP,
  download, real display/audio changes or preference write.
- Menu Tab/Enter multiplayer/host, native Back, Settings focus return, exit
  cancellation/confirmation and solo navigation. HUD selected-context quotes,
  insufficient trade rejection, unchanged resource stock, ready/unready,
  preparation, shared pause/resume, reconnect and distinct fresh-session intents.
  Existing phase/read-only/outcome/quote/layout assertions remain intact.
- All new interactions leave the underlying mock world-click count unchanged.
  This does not replace the game's explicit world-input ownership guards.

Final OS checks: **11 original Settings-sequence checks** at
`.cache/ui-diagnosis/full-os-none-production-package-serial/probe.log` and **64
modal-scope checks** at `.cache/ui-diagnosis/modal-os-none-production-package-reviewed/probe.log`.
Zero world leaks; original event order/assertions unchanged. These OS checks cover
Settings/modal lifecycle, not the whole new production fixture. Other interaction
checks use Godot native Controls with injected events, not physical input claims.

Fresh independent UI-only payload: **nine scenes, Theme/seal, 32 files**,
`.cache/ui-payload/production-package-reviewed/load.log`, hashes in `payload.json`.
No prototypes, tests, tools or game copied. `api.md`/`migration.json` document the
portable component boundary and future adapter/scale/lifetime risks.

### Actual visual judgment

All **35 final image bytes** reviewed at native dimensions: 27 base frames from
`production-package/` are byte-identical to final frames; multiplayer, About-error,
long friends and scrolled locked research at both 1100×820 and 1280×720 were opened
separately (the final corrected About/friends images also opened). Bindings in
`visual-review-components.json`; accepted M1 bindings preserved in `visual-review-m1.json`.
HUD/menu have four-size pictures; dialogs have two-size pictures, not four-size
visual acceptance. State HUD frames at 1280×720 remain preparation/shortage/lost/
combat/foreign. See `coverage.md` for the exact boundary and outstanding acceptance.

Cream/dark-ink planes, amber primaries, muted rose permanent actions and teal native
focus remain cohesive Ledger. The unchanged 48px seal stays subordinate. Research
reasons and replacement effects wrap clearly; the scrolled lock view keeps Close
outside the fold. Dense roster/friends bodies now have one visible scrollbar,
not competing nested tracks. Far rows remain below the fold by design and behavior
checks prove reachability. Long friends ellipsize before the Invite button and
retain full tooltip identity; the identity suffix is not always visible inline.
About feedback fits within its tab pane. Multiplayer title/action/Back hierarchy
is consistent with the start menu. No non-scroll collisions or missing glyphs seen.
Read-only HUD quote bodies at 720px still scroll; that is deliberate, not evidence
that all content is simultaneously visible. Abstract hex context is not game art.

### Focused failures and bounded corrections retained

`eg-focused-1`: 111 checks / 20 failures. The native selector test used KEY_HOME
inside PopupMenu as an assumed first-item shortcut. Changed only the test driver to
navigate from `get_focused_item()` using arrows; no state gate weakened.
`eg-focused-2`: 138 / 3 failures. The single-body-owner assertion incorrectly included
native popup lists in separate viewports. Narrowed that assertion to the body's
viewport; real wheel, long traversal and activation assertions retained.
`eg-focused-3`: 135/0; `eg-focused-4`: 148/0; `eg-focused-5`: 159/0 after native Refresh,
Return confirmation and external preview-slot coverage. All earlier result files
and full logs remain as produced. No runtime assertion failure was hidden.

`production-package`: 419/0/27. Added eight warranted state captures and the final
interaction checks; `production-package-final`: 438/0/35. Image review found mock
selector captions inconsistent with capture-only state assignment in About/friends;
aligned selectors in capture setup, without changing runtime or input assertions.
Final fresh `production-package-reviewed`: 438/0/35. This was the source-bound
acceptance for the representative milestone, not reused M1 proof.

Parallel owned Xvfb starts caused a wrapper failure for the reviewed-label OS full
probe: its 11 UI checks passed, but xvfb-run exited 1 (`Server is already active
for display 100`, cleanup `kill: No such process`). Kept the failed command/log,
no UI fix or weakening; one isolated serial rerun passed with exit 0. Run graphical
drivers serially. No speculative engine/Window regression claim.

Metadata/history/source/image contracts **8 passed**; existing offline fast route
**57 tests and two inline JavaScript programs passed**, lint/syntax/guardrails;
logs `.cache/ui/production-package-reviewed/{plan,repo-check}.log`. Whitespace passed.
Read-only game Git observation now reports clean HEAD `606b102f790f8dec0551f262b418d7b7f3f54cbc`;
the independent integration work moved it since M0's pin. No files/refs changed here,
no moving branch copied, and discovery stays bound to its historical revision.

Remaining breadth and integration limits are explicit in `coverage.md`, tasks and
roadmap; E–G remain in progress beyond this representative package. No pipeline,
push, merge, release, extra Blender work or game migration was performed.

---

## Historical accepted M1 record (foundation only)

### Checked milestone at M1

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
frames; SHA-256/dimension/review bindings are in `visual-review-m1.json`.

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
then test-only coverage grew for OS focus loss/underlying-Esc evidence, and a
source-bound run passed 267. Local focus traversal was then corrected to include
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
