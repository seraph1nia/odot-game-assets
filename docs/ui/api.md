# Portable UI boundary and migration preparation

Scope: finished intended standalone Phase E component library, Phase F functional
mock compositions and Phase G migration-ready package, clarified in inbox 007.
**Do not migrate now.** See `coverage.md`, `tasks.json` and `production.md` for
checked acceptance and separate external integration obligations.

## Payload

Copy candidate: only `ui/preview/UI/` to a future game's `res://UI/` after separate
authorization. `payload.json` records 35 source/import/UID/resource files and hashes.
A fresh private project containing only this directory loaded all ten scenes,
Theme and seal with no preview, game or authoring-tool dependency.

Do not copy `prototypes/`, `tests/`, `explorations/`, project settings, `.godot` caches,
Blender sources/generators or reference images as runtime dependencies. The
prototypes demonstrate composition/projections; they are not the game's root or
service adapters. Global script names `WatchUI` and `WatchModal` need collision
checking in the future target. Tested engine/backend only: Godot 4.7.2 .NET.
No guarantee for earlier Godot, game canvas-items scaling, native GPU or desktop.

## Scenes and interfaces

Paths below are relative to `res://UI/components/`. Data are Godot Dictionary/Array
projections, copied/rendered/formatted locally, not authority calculations. Missing
optional fields show empty/default presentation. Supply exact already-formatted
quantities, quote/effect/reason text and eligibility from the game. Call after
adding to the tree for all components; follow existing script fields for the full
shape. `prototypes/fixtures.gd` is illustrative data only, never a runtime dependency.

| Scene | Data entry | Intent signal | Important fields / ownership |
|---|---|---|---|
| `resource_ledger.tscn` | `set_data(Dictionary)` | none | title, rows{name,stock,income}, income_heading, context; six resources externally supplied |
| `upkeep_summary.tscn` | `set_data(Dictionary)` | none | heading, rows{label,value}, detail; forecast/receipt/wave decided externally |
| `quoted_action.tscn` | `set_data(Dictionary)` | `requested(action_id:String)` | id,title,quote,enabled,reason,variant; never spends resources |
| `city_navigation.tscn` | `set_data(Array, selected_id:int)` | `city_requested(city_id:int)` | id,label,context; game clears selection/camera and determines edit rights |
| `match_controls.tscn` | `set_data(Dictionary)` | `requested(action_id:String)` | phase,counters,ready/pause labels/ids/eligibility/visibility,terminal; no phase transition |
| `session_feedback.tscn` | `set_data(Dictionary)` | `requested(action_id:String)` | status,message,reconnect,fresh; no sockets, tokens or teardown |
| `unit_inspection.tscn` | `set_data(Dictionary)` | `requested(action_id:String, unit_id:int, destination_id:String)` | profile/health/status/recovery text, destinations, can_send/can_retire/reason; funding/recovery/model/status clocks stay external |
| `army_roster.tscn` | `set_data(Dictionary)` | `unit_selected(unit_id:int)` | title,context,tiles,units,selected_id; display separate tile budgets, not pooling/transfer logic |
| `skill_tree.tscn` | `set_data(Dictionary) -> bool` | `selected(id)`, `purchased(id, remaining_points)`, `rejected(id, reason)` | one-point root, three small chains, supplied points/owned; local guarded allocation, not game authority (below) |
| `modal.tscn` | local lifecycle below | `canceled`, `confirmed`, `closed` | native Control composition, not a Window or session owner |

Core quote/city/match/feedback and inspection/roster scenes have meaningful native
input/state acceptance including one/four-city, lobby, connection/rejection, empty/
stale/fragmented and recovery edges. This is not exhaustive Cartesian-product
coverage. Projected world health bars are NOT added or modified.
The inspector `Body/PreviewSlot` is an adapter-owned Control (mouse-filter Ignore);
attach native preview content there and project `show_preview=true`. No model loader
or service is supplied. `army_roster` uses a native exclusive ButtonGroup; the
adapter still owns selected identity/lifetime, not row indices.

## Compact skill-tree allocation

`skill_tree.tscn` extends the existing research-node/`quoted_action` presentation:
its graph uses native inspectable Buttons and decorative links, and its selected
node uses the existing quoted-action control for description, cost, prerequisite
reason and purchase. It does not replace the historical research composition or
its canonical `research-node` alias. Demo: choose **skill_tree** in the showcase
screen selector. The host/fixtures are authoring-only; costs/effects are illustrative.

Supply a complete typed snapshot after adding to the tree (or before ready):

```gdscript
var tree = preload("res://UI/components/skill_tree.tscn").instantiate()
parent.add_child(tree)
tree.set_data({"points": 3, "owned": [],
    "root": {"id": "start", "title": "Foundation", "cost": 1,
             "description": "Open three paths."},
    "branches": [
        {"title": "Protection", "nodes": [
            {"id": "guard", "parent": "start", "title": "Guard", "cost": 1},
            {"id": "resolve", "parent": "guard", "title": "Resolve", "cost": 2}]},
        {"title": "Precision", "nodes": [
            {"id": "aim", "parent": "start", "title": "Aim", "cost": 1}]},
        {"title": "Support", "nodes": [
            {"id": "spark", "parent": "start", "title": "Spark", "cost": 1}]}]})
```

- Exactly three branch Dictionaries, each with 1–3 node Dictionaries. Branch
  array order determines heading identity and position; branch titles need not
  be unique and are preserved in headings and selected-node quotes. Root and
  nodes have unique nonempty String `id`s, short `title`s and optional
  `description`s. Root `cost` must be 1 (default 1); other costs are positive
  integers (default 1). `points` is a nonnegative integer. Every node's explicit
  String `parent` must be the previous step (first step's parent is root).
  No sibling exclusion or cross-branch dependencies. `owned` is an Array of
  unique known String ids with their entire parent chain already owned.
- `set_data` copies the snapshot, resets selection to root and replaces local
  allocation; invalid topology/cost/ownership returns false without changing the
  previous snapshot. This fixed small layout is not an arbitrary graph engine.
- `select_node(id)` inspects; `node_state(id)` returns `owned`, `locked`,
  `insufficient`, `available`, or `unknown`. Prerequisite failure takes priority
  over funding. Owned nodes and locked nodes remain focusable/inspectable.
- `purchase(id) -> bool` checks unknown/owned/parent/funding, spends exactly the
  supplied cost once and updates labels, purchase eligibility and links before
  emitting `purchased(id:String, remaining_points:int)`. A rejection leaves points
  and ownership unchanged, displays a reason and emits `rejected(id, reason)`.
  The native purchase button is disabled unless available. There is no refund,
  respec, currency conversion, save or asynchronous game command system.
- Links: muted = parent missing; amber = parent met (including insufficient
  points); thick teal = owned. Node text states the distinction; pressed styling
  marks selection and a teal outline marks native keyboard focus. All choices
  remain readable independently of color.
- Tab/Shift-Tab and Enter use Godot's native focus/activation. The fixed 960×550
  graph has its own two-axis `ScrollContainer` with `follow_focus`; narrow hosts
  clip/scroll the graph instead of shrinking text. Initial/replaced snapshots
  present the root after native container sorting, without stealing focus or
  retaining retired controls in callbacks; later user scroll stays unchanged. Put descriptions under a final
  outer scroll owner for unusually long supplied copy. Short graph titles may
  clip; the description and tooltip retain full copy. No global input interception.

This component intentionally owns **local allocation only** (unlike intent-only
quoted actions). Callers supply starting points/definitions/ownership and receive
allocation signals; a future game's authority must validate/persist and replace
snapshots itself. No economy/balance or illustrative effect becomes game policy.

## Local modal lifecycle

Host under a viewport-sized, unclipped **Control outside layout containers**,
same viewport as its invoking controls. It blocks pointer input across the viewport
without dismissing on outside click. Add confirmation siblings after their parent
modal so the active visible scope gets input first; close children before teardown.

```gdscript
var modal = preload("res://UI/components/modal.tscn").instantiate()
overlay_host.add_child(modal)
modal.title = "Settings"
modal.invoker = settings_button
modal.get_content().add_child(settings_content) # Native controls, not services.
modal.popup_centered_clamped(Vector2i(560, 540))
```

`get_content()` returns the VBox in the native ScrollContainer. `get_scroll()`
returns that body owner for composition/accessibility/validation. `get_panel()`
returns the actual centered panel (use this for bounds, not full-rect scrim).
`get_ok_button()` is the native Close/primary button. `cancel()` emits cancellation
then closes; `close()` hides/disables its input scope, restores a still-valid visible
invoker only while the app window is focused, and emits `closed`. The host decides
when to queue_free or reuse. External hide also disables the input scope.
Set `confirmation=true` and `ok_button_text="Confirm"` for the Cancel/Confirm footer;
confirmation emits `confirmed` before closing. No deletion/session logic is embedded.

Tab/Shift-Tab select visible enabled native controls within this modal. Owned native
PopupMenu/OptionButton windows retain their first Esc and arrow/Enter behavior.
Otherwise the visible local modal consumes ui_cancel before closing; it does not
swallow Esc when hidden. There is no application Window-focus recovery callback.
Do not reintroduce the disproved embedded Window topology, speculative flags or
forced focus in tests. Diagnosis/contrary results remain in `settings-diagnosis.md`
and `modal-alternatives.md`; the full original event sequence stays tested.

The game still needs its own explicit local world-input owner guard while modal UI
is visible (picking/drag/keyboard commands may bypass GUI). Do not substitute a
viewport scrim for that service boundary or assume this preview covers game input.
`WatchUI.scroll(parent, name, minimum_height)` uses one ancestor vertical-scroll
owner when present; otherwise the list scrolls independently. The modal follows
focus. Add the component under its final scroll owner before `_ready()` constructs
its body; this ownership decision is not automatically recomputed on reparenting.
Actual wheel/reverse-wheel and long Tab/Enter reachability pass for research/hall/
Details/friends. Native child dropdowns are separate viewport scopes, not disabled
body scrollbars.

## Functional composition projection examples (authoring-only)

`prototypes/details.gd::set_data(Dictionary)` and
`prototypes/town_hall.gd::set_data(Dictionary)` expose supplied snapshot seams for
future game-owned compositions. These scripts deliberately import `UIFixtures` for
their native demo selectors; **do not copy them as runtime payload dependencies**.
Adapt their arrangement and `set_data` shapes, not their mock selectors/defaults.
Add the content under its final modal owner before `_ready()` builds its body.

- Details: `sample` (demo selector only), `title`, `context`, `food` (Array of
  independent `upkeep_summary` projections), `reward_heading`, `reward`, `roster`,
  `allocation_heading`, `allocation` (already formatted String). No computation
  of receipts/forecast/allocation. Fresh snapshots replace previous summaries,
  reward, roster and allocation. Prototype-only `set_context(state)` supplies a
  title/inspection annotation that survives switching; adapters should instead
  supply exact owner/context and command rights. `unit_selected(unit_id:int)`
  forwards the roster's selection intent, not an edit command.
- Hall: `sample` (demo selector only), `title`, `context`, `roster`, `storage`,
  `healing`, `sale` (three independent `quoted_action` projections), `profiles`
  (Dictionary keyed by int unit id, inspection projections), `selected_id`.
  `set_read_only(reason:String)` is the external persistent command gate;
  individual quotes/profiles also carry their supplied enabled/can_send/can_retire
  eligibility. Signals: `requested(action_id:String)` and
  `unit_requested(action_id:String, unit_id:int, destination_id:String)`.
  A disabled quote cannot emit a command, but that is not authority validation.
  Read-only gates survive selection/demo switching.
- Future adapters supply occupied-sale rejection, exact track maxima/prices,
  individual tile availability, funded recovery/health eligibility, hall/selection
  generations and stale/foreign gates. No authority is inferred from view names.
- Other prototype native signals and fixtures demonstrate menu navigation,
  selection, About feedback and busy invitation presentation. A deferred mock
  result is not a service/session implementation. Retain existing game's save,
  query/send, lifetime, host/leave, update and audio services rather than copying
  the prototype's callbacks or request-status labels.

## Payload budget

The audited **35 files total 109,055 bytes** on disk including scripts, UID/import
metadata and Theme, not a packaged-game or GPU-memory estimate. The only standalone
image file is the 192×192 RGBA original seal:
**34,237 PNG file bytes / 147,456 decoded RGBA bytes**, displayed at 48px with
transparent surround. Native StyleBoxFlat planes require no nine-slice texture;
no additional font/image files or Blender ornaments. Packed Godot import
formats, rendering cost/FPS/VRAM and target-game package overhead are unmeasured.
Authoring `.blend`, fixture/test/tool bytes are not runtime payload. Source/output
hashes are in `exploration-assets.json`; resource hashes are in `payload.json`.

## Migration order and authority (later authorization only)

1. Re-pin game/reconcile removed labels and current UI screenshots; confirm engine,
   scale, DPI and rights. M0 source revision is evidence, not a live baseline.
2. Copy/audit `UI/`; complement ApplicationTheme before replacing existing kit art.
3. Adapt resource/upkeep projections first, then quote/city/match/feedback signals.
4. Preserve opaque slot/building/hall generation and phase/stage guards in command
   adapters. Authority validates costs, eligibility and stale selection again.
5. Adapt modal/inspection/roster/research presentation and actual world-input guards.
   Do not retain faulty Window-focus assumptions merely for API similarity.
6. Compose full HUD/menu/settings after separate integration authorization and
   a fresh current-game baseline; use finished standalone `coverage.md` as the
   reference, not live-game certification. Keep networking/Steam/friends/
   persistence/audio/update/model-loader services in game.
7. Run authorized game slice tests then required full delivery gates; re-review
   current game renders. No game operation in this asset milestone did any of this.

`migration.json` binds these responsibilities to inspected game files. Unsupported
small windows/localization/RTL and actual game/async input remain explicit target
risks, not presumed passes from screenshot generation or new standalone blockers.
