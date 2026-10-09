# Finished standalone acceptance boundary

Scope: original approved Phase E component library, Phase F functional standalone
mock compositions and Phase G migration preparation, clarified by inbox 007.
**The intended standalone backlog is complete and checked. Game integration,
publication and rollout are not performed or certified.** Accepted M0/M1 and the
scrolling/representative milestone remain unchanged historical evidence.

Current normal acceptance: **568 checks / zero failures / 79 captures**;
[production record](production.md), [source-bound results](production/standalone-final/results.json).
This is meaningful discovered state coverage, not every phase×selection×eligibility
Cartesian product or an exhaustive future-platform campaign.

## Checked component and composition criteria

| Area | Completed standalone coverage | Evidence owner |
|---|---|---|
| Foundation/art | Native Ledger Theme and semantic variants; exact six-resource/upkeep conventions; unchanged original 48px menu seal with editable source/PNG linkage | M1 plus fresh full regression, source/payload manifests |
| Modal/input | Original Settings sequence unchanged; dropdown-first Esc, outside block without dismissal, visible-only local Tab/Shift-Tab containment, invoker return, hidden/focus-loss/reopen/nested confirmation ownership | `tests/run_ui.gd`, serial OS `tests/diagnose_settings.gd` |
| Scrolling | Research/hall/Details/friends one vertical body owner; native wheel/reverse-wheel, long Tab reveals whole far-row controls, Enter emits correct opaque identities | `tests/production_checks.gd::scrolling()` |
| Quote/navigation/phase/feedback | Long quote/reason text, insufficient/read-only rejection, one/four-city disabled/wrapped navigation, lobby Start, ready/unready/preparation, shared pause/resume, lost reconnect/fresh, connecting/connected/reconnecting/expired/rejected feedback | Original checks plus production `hud()` / `edge_controls()` |
| HUD | All discovered selected-context families populated; actual construction tabs/ranged recruiter/Mage rejection, quotes do not spend stock; building/ready/preparation/combat/shortage/foreign/paused/lost/outcome plus fallen/stale inspection projections | Original checks plus production `hud()` / `edge_controls()` |
| Research | All three five-node class paths; native class/access selectors, available specialization/funded mastery intent, owned/prerequisite/insufficient/permanent sibling lock, foreign/paused suppression; points/progress/tower rate distinct | production `research()`, old assertions retained |
| Inspection/roster/hall | Exact profile/health/shaped statuses; field/stored/empty/native exclusive selection; no/full/fragmented destination; independent storage/healing quotes and maxima, occupied-sale refusal/empty-sale intent, stale/read-only selection, funded wounded/unfunded wounded/full-health recovery projections; no local heal/transfer/retire/capacity mutation | production `inspection()` / `hall_projections()` |
| Details | Native planning/paid-current-wave/last-wave/fresh switching; current receipt versus previous reward and next forecast versus last receipt kept separate; fresh clears old receipt/reward/roster/allocation; foreign owner survives view switch; combat/outcome host projection | production `details_projections()` |
| Menu/options/friends | Native solo/multiplayer/host/Back, Exit/Return cancel/confirm, Settings focus return; Graphics dropdown/Fullscreen gate, Audio keyboard/zero, six About/update/save feedback projections; seven friends projections, native Refresh/far-row invite/immediate busy/recoverable mock result/long-name tooltip | production `menu()` / `settings()` / `friends()`, original Settings/OS fixture |
| Portability | UI-only 32-file copy loads nine scenes/Theme/seal in a fresh private project; no game/tool/prototype dependency; relative paths/hashes, editable source linkage, texture budget, data/intent APIs and adapter order | `tools/ui/audit_payload.py`, `payload.json`, `api.md`, `migration.json` |

## Desktop visual and input review

Chosen desktop sizes: **1100×820, 1280×720, 1600×900, 1920×1080**, matching pinned
intake. HUD, start/multiplayer and all seven base dialog compositions have measured
frames at all four sizes. About-error, long friends and scrolled locked research
also have four-size frames. Details paid/last/fresh and hall empty/stale/storage/
recovery/fragmented have two-size state pictures. Eleven meaningful HUD state views
are additionally captured at 1280×720. No claim that every state has four pictures.

All **79 final image bytes have actual visual review**: 50 new frames opened at
native dimensions, 29 proven byte-identical to previously inspected frames from the
accepted representative package. `visual-review.json` binds the ordered image-set
SHA-256, dimensions, explicitly newly inspected filenames and earlier review bytes.
New/changed views never inherit acceptance merely because old screenshots exist.

Input uses real native Godot Controls with injected mouse/wheel/keyboard events;
Settings/modal also have serial owned X11/XTest coverage. Direct projection changes
in screenshots are not called input tests. Values are representative supplied
snapshots; fixtures do not advance gameplay, clocks or services.

## External integration requirements and honest limits

These are **not current E–G blockers** and were not certified here:

- Real Steam/HTTP/update installation/audio/preferences/network/session lifetimes,
  invitation/host-leave effects, stale async completion after teardown, credential
  handling and command authority. Game adapters must revalidate costs, eligibility,
  selected generation/phase, atomic transfer, funding/recovery and lifetime guards.
- Model loading/rendering, world picking/projected/offscreen health/status clocks,
  and moving label-removal compatibility. The independent 192×80 native preview
  slot is tested with a Label, not a 3D model. No removed world text is restored.
- Current-game baseline and its canvas-items/expand behavior, HiDPI/native desktop/
  GPU/compositor/physical input/audio, earlier engine versions, arbitrary tiny
  windows, localization/RTL and mobile/controller. Tested platform is Godot 4.7.2
  .NET, Xvfb, Compatibility/Mesa llvmpipe, Dummy audio. No FPS/VRAM claims.

Known presentation tradeoffs: dense bodies deliberately scroll below the fold;
very long duplicate friends ellipsize before Invite and retain full tooltip identity
rather than guaranteed inline suffix; keyboard-only tooltip discoverability is not
established. Scroll ownership is chosen at construction: host before `_ready()`
builds its body under the intended owner, not arbitrary later reparenting.

Only `ui/preview/UI/` is the runtime copy candidate after separate authorization.
`prototypes/` are reusable composition/projection examples, not the game's root or
service adapters. Details/hall `set_data()` contracts accept supplied snapshots;
mock selectors and `UIFixtures` are intentionally authoring-only. Follow [API](api.md)
and [migration mapping](migration.json); re-pin the moving game and check namespace
collisions before any copy. No moving integration-code copy occurred.

## Handoff

Standalone E–G completion means the artifacts/contracts above are implemented and
checked, not publication or production-ready game integration. MAIN will route the
same-worker configured no-mistakes handoff with full original captain intent and
exact Ledger/small-seal approval. No independent pipeline, push, merge, release or
migration is authorized by this record.
