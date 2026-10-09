# Portable UI boundary and migration preparation

Scope: checked M1 foundation/local modal plus implemented, partially accepted
components. **Do not migrate now.** See `tasks.json` and `production.md` for coverage.

## Payload

Copy candidate: only `ui/preview/UI/` to a future game's `res://UI/` after separate
authorization. `payload.json` records 32 source/import/UID/resource files and hashes.
A fresh private project containing only this directory loaded all nine scenes,
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
| `unit_inspection.tscn` | `set_data(Dictionary)` | `requested(action_id:String, unit_id:int, destination_id:String)` | profile/health/status text, destinations, can_send/can_retire/reason; model/status clocks stay external |
| `army_roster.tscn` | `set_data(Dictionary)` | `unit_selected(unit_id:int)` | title,context,tiles,units,selected_id; display separate tile budgets, not pooling/transfer logic |
| `modal.tscn` | local lifecycle below | `canceled`, `confirmed`, `closed` | native Control composition, not a Window or session owner |

Core quote/city/match/feedback and inspection/roster scenes are implemented and
loadable, but their complete state/input acceptance is still M2/M3 work. Projected
world health bars are NOT added; only inspector style samples currently exist.

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

`get_content()` returns the VBox in the native ScrollContainer. `get_panel()`
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
Current shell plus nested list scrolls is a known composition issue: simplify nested
ownership and test real wheel/long-focus traversal before broader scene acceptance.

## Migration order and authority (later authorization only)

1. Re-pin game/reconcile removed labels and current UI screenshots; confirm engine,
   scale, DPI and rights. M0 source revision is evidence, not a live baseline.
2. Copy/audit `UI/`; complement ApplicationTheme before replacing existing kit art.
3. Adapt resource/upkeep projections first, then quote/city/match/feedback signals.
4. Preserve opaque slot/building/hall generation and phase/stage guards in command
   adapters. Authority validates costs, eligibility and stale selection again.
5. Adapt modal/inspection/roster/research presentation and actual world-input guards.
   Do not retain faulty Window-focus assumptions merely for API similarity.
6. Compose full HUD/menu/settings only after outstanding M2–M4 acceptance. Keep
   networking/Steam/friends/persistence/audio/update/model-loader services in game.
7. Run authorized game slice tests then required full delivery gates; re-review
   current game renders. No game operation in this asset milestone did any of this.

`migration.json` binds these responsibilities to inspected game files. Unsupported
small windows/localization/RTL, complete async/error states and actual game input
remain explicit later gates, not presumed passes from screenshot generation.
