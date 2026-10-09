# UI workspace and ownership

Current checked slice: **representative standalone Ledger component/composition
package**, built on accepted M1 foundation/local modal. Broader projection and game
integration acceptance remains explicit in [coverage.md](coverage.md).
State: [tasks.json](tasks.json).
Interfaces/migration boundary: [api.md](api.md); actual evidence:
[production.md](production.md). Existing world tooling/MCP/palettes remain unchanged.

| Path | Responsibility |
|---|---|
| `docs/ui/` | Discovery, exact approval, inventory/backlog, reviews, source bindings, migration |
| `docs/ui/previews/` | Historical M0 Ledger/Watch comparisons |
| `docs/ui/production/production-package-reviewed/` | Current source-bound 35 captures/results |
| `docs/ui/production/m1-tab-scope/` | Preserved accepted 27-frame M1 foundation evidence |
| `docs/ui/production/` other folders | Preserved failed/intermediate captures, not relabeled as current acceptance |
| `sources/ui/menu_seal.blend` | Approved original editable source, retained byte-for-byte from M0 |
| `sources/ui/explorations/watch_seal.blend` | Rejected-alternative study, not runtime payload |
| `ui/preview/UI/` | Portable relative runtime namespace; Theme, fixed art, helper, nine component scenes |
| `ui/preview/prototypes/` | Standalone mocked compositions/fixtures, not game adapters or payload |
| `ui/preview/explorations/`, `art/explorations/` | Historical study host/Watch PNG; not payload |
| `ui/preview/tests/` | Actual native-event/state/layout checks, diagnosis and modal-scope fixtures |
| `tools/ui/` | Small authoring/capture/check drivers, not runtime dependencies or general framework |
| `.cache/ui*`, `.cache/asset-check/logs/` | Private owned processes/XDG state/full logs, ignored |

## Native semantics first

Theme/StyleBoxFlat own flexible surfaces. Native Buttons, Labels, grids, scrolling,
OptionButton/PopupMenu, HSlider and TabContainer own ordinary widget behavior.
The approved Blender gate seal stays fixed at 48px from a transparent 192px PNG;
no dynamic text is baked and there is no decorative frame/icon family or nine-slice
texture. Native semantic close marking is not extra Blender artwork.

The new modal uses an in-tree Control/scrim/centered panel rather than Window.
Its small visible-only lifecycle handles local cancellation, Tab scope and valid
invoker restoration; native child dropdowns get first Esc. No global input router,
Window focus stealing or forced shared pause. One ancestor vertical-scroll owner
handles embedded bodies; native child popup viewports retain their own scrolling.
Construction-time ownership/reparenting limitation is documented in `api.md`.
That modal boundary follows the causal
Window failure evidence, not an aesthetic redesign. See `api.md` for hosting.

Components accept projections and emit intents. Game adapters keep quotes,
eligibility, generations/stage guards, networking/session, Steam, preferences,
audio/update, unit picking/model rendering and gameplay authority. GDScript scenes
have no C# gameplay reference or runtime checkout/cloud dependency. The UI-only
private audit loaded all nine scenes without preview fixtures or tooling.

## Source/render/validation traceability

`exploration-assets.json` keeps original source/output hashes, including approved
Ledger's renamed source/PNG. No bytes changed in that move. The existing worker
built both studies with geometry.material(), editable meshes, Cycles CPU/32 samples,
orthographic 192px transparent RGBA, AgX/Medium High Contrast and a large Area key.
Those UI-only render parameters do not change world art_style defaults. The saved
source's old exploration collection/path metadata is historical authoring state,
not current approval or runtime dependency. Preserve manual edits before regeneration.

`tools/ui/build_theme.gd` authors the saved standalone Theme, which has no runtime
dependence on its generator. `tools/ui/validate.py` owns fresh import, software display,
source hashes and actual captures. `tools/ui/audit_payload.py` copies only UI/ into
a private new project and checks resource paths/loading. Full exports, shared
library rebuilds and GUI Blender mutations are unnecessary for this UI-only slice.

Do not copy project.godot stretch policy into the game: disabled stretching here
keeps test pixels/text stable; game canvas-items/expand still needs integration
measurement. No AGENTS/CLAUDE rewrite, shared scene access or unrelated assets.
