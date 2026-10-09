# UI discovery — pinned intake

Phase A findings, 2026-10-09. **No game change, import, build or launch performed.**
Game input: `/home/bart/projects/personal/firstmate/projects/odot-game`, revision
`d7e697710e15addade9ce82d28d6de94c05aacab`, clean at inspection.
Asset baseline: `ddd1ef1a35bd8db5bf3d1a405672d254aff68174`.
All game-relative paths below refer to that revision, not a moving sibling worktree.

## Established evidence reused

Read game `AGENTS.md`, `README.md`, `docs/gameplay.md`, `docs/assets.md`,
`docs/runtime-rendering.md`; asset `README.md`, `docs/quality-round/README.md`,
`.agents/skills/asset-art-direction/SKILL.md`, its reference index, design index
and D03 palette owner. These already establish world art, migrated asset identities,
licensing limits and software-renderer caveats. This is not another 3D quality audit.
Detailed-hex-tile work is independent and not an input. No shared palette/source
changes, library rebuild or MCP scene takeover is needed.

## Confirmed existing UI and player jobs

| Surface / job | Evidence in game | Classification and implications |
|---|---|---|
| Start, solo, multiplayer host/back, exit; Steam identity/offline feedback | `src/Game/GameApplication.cs` (menu creation, 460px panel, 42px buttons), `GameBrand.cs` | Functional; keep navigation and session ownership. Improve shared hierarchy, not invented matchmaking. |
| In-game Steam friends invitation list | `src/Game/SteamFriendsDialog.cs` | Current native 560×420 scrollable dialog, Refresh/Invite/Close, online-first sorting, duplicate-name disambiguation, busy/offline/error states and focus return. Older gameplay prose emphasizes external overlay; current code also provides this owned UI. Keep behavior and mock it without Steam calls. |
| Settings, Graphics/Audio/About, return confirmation | `src/Game/ClientSettings.cs`, `GameApplication.cs` | Functional native dialogs, tabs, dropdowns, 0–100 slider, update feedback and focus restoration. About is in code although older gameplay docs describe only two tabs. Keep behavior; apply consistent surfaces. No runtime update service in the asset preview. |
| Six-resource table and phase-dependent income; food forecast/receipt | `src/Game/TabletopHud.cs`, `Tabletop.cs` refresh logic; `docs/gameplay.md` | Confirmed dense informational HUD, 260px wide at top right; Gold/Food/Wood/Stone/Metal/Cloth. Income versus next-turn context and forecast versus paid receipt must remain explicit. No icon-only replacement. |
| Bottom city switch, Details, status/rejection messages, construction groups and quotes | `TabletopHud.cs`, `Tabletop.cs`, `ProgressionPresentation.cs` | Functional native containers but compact 11–12px controls, overridden button padding and large mixed text duties. Redesign hierarchy and quote wrapping; preserve stable slot/generation/command guards. |
| Land purchase; explicit gold-recovery woodcutter; upgrade/sell; fixed-bundle trades | same; `docs/gameplay.md` | Confirmed context-specific actions, not generic inventory or crafting. Preserve affordability reasons, investment refund, food-sale consequences, read-only foreign/paused/ready states. |
| Paid recruitment and physical army homes; retire/store/send; hall capacity/healing | `src/Game/ArmyPanel.cs`, `UnitInspector.cs`, `docs/gameplay.md` | Confirmed army controls and scrollable Town hall roster. Field homes and stored tiles are not interchangeable. Retire has no refund. No new equipment screen. |
| Personal research tree, class tabs, costs/prerequisites/exclusive locks | `src/Game/ResearchPanel.cs` | Existing scrollable native dialog and multiline buttons. Keep real three-class tree and immutable authority quotes; increase visual separation of owned/available/locked without changing purchase semantics. |
| Unit inspection, actual 3D preview, health/damage/capabilities/statuses, deadlines | `src/Game/UnitInspector.cs`, `ProgressionPresentation.cs` | Already implemented; reusable inspection layout, not new hero portraits or character progression. Preserve 192×80 preview and text alternatives; do not copy gameplay/rig code into UI kit. |
| Ready/Unready, production/preparation/battle, pause/resume, start, reconnect/fresh-session, invite, outcome | `TabletopHud.cs`, `Tabletop.cs`, `GameApplication.cs` | Confirmed cooperative control/feedback. Opening settings is local input blocking, not shared pause. Fallen owners still inspect/pause. Distinguish reconnect from fresh session and loss from pause. |
| Projected unit/home health, Roman levels; shaped burn/poison/chill badges | `UnitHealthBar.cs`, `HomeHealthBar.cs`, `ProgressionPresentation.cs`, `docs/gameplay.md` | Keep authority projection and shape/text redundancy. Styling can complement world art; do not reintroduce ambient plot/building/resource text labels. |

`src/Game/Scenes/Main.tscn` contains only a scripted `Game` Node. Most UI hierarchy
is created in C# at runtime: `GameApplication` → application controls/menu/settings,
`Tabletop` → resource panel/inspection/bottom panel/dialogs. Inspecting only `.tscn`
would miss essentially all functional requirements. Numerical rules belong in
`src/Game.Core`; reusable preview controls must not import that assembly or networking.

## Shared assets worth keeping

`src/Game/ApplicationTheme.cs` already centralizes default 14px font, parchment
20px sliced panel, amber derived button states with 14/14/14/18 margins, teal 2px
focus outline, tabs/dialogs/popups/tooltips, native slider/scrollbars and health
slices. Native Godot controls and shared texture caching in `UiAssets.cs` are worth
retaining. No custom font resource was found in the theme/project: Godot default
font is the verified starting point, not an invented medieval typeface requirement.

`src/Game/Assets/TrioUI/README.md`, `UPSTREAM-README.txt`, `manifest.json` record
Moonpunch Trio UI free v2.2 and derived geometry. Existing use is owner-approved,
but redistribution of source kit files is restricted; **do not copy the kit into
this independently publishable repository**. Reuse existing game-side slices in
an eventual incremental migration where permitted, or replace only justified
surfaces with original artwork. Retain familiar interactions and semantic text.

Important current-code divergence: `UiAssets.Decorate()` explicitly sets
`button.Icon = null`; `Cost()` creates 11px textual costs. The README's icon mapping
is available art, not proof that icons are visible on current buttons. No enforced
need to author forty new icons follows from the unused kit inventory.

## Visual identity, observations versus uncertainty

Inspected `docs/images/source-building.png` (1100×820) and
`docs/images/settings-graphics.png` (1280×720) in the game: dark green native-looking
HUD, small cream text, a yellow-green board and old Blacksmith/three-resource
presentation. **Historical captures, not current-theme acceptance.** They cannot
establish current clipping or prove the present parchment theme is poor. No newer
run PNGs are available in this input checkout; references to ignored logs in
`docs/assets.md` are retained report evidence, not images newly inspected here.

Inspected asset `sources/reference/more_buildings/cozy_fantasy_weaver_s_workshop.png`:
chunky timber joinery, quiet cream masonry, blue cloth/roof planes, tiny warm lamps,
soft bevel highlights and substantial negative space. Current owned
`docs/quality-round/evidence/weaver-480.jpg` and `town_hall-480.jpg` are available
review context. Reference rights are not established for public republishing;
link existing originals only. World identity is painted medieval tabletop with
role/faction variation, not mandatory wooden UI frames or crystal buttons.
UI can echo warmth/value relationships without reproducing building materials.

## Gaps and quality opportunities (not invented missing gameplay)

Confirmed production gaps here: no standalone UI preview project, UI inventory,
UI source/export linkage, reusable UI scenes or current UI-specific visual review
ledger in assets. Game has reusable runtime theme helpers but very few portable
scene components. Propose these production facilities, not a gameplay rewrite.

Current code suggests readability risk: bottom buttons forced to 11px, long costs
and prerequisite/lock strings inside buttons; tooltip dependence; settings/about
feedback sharing generic label styling. These are **risks pending current rendered
measurement**, not proven defects. Resource table's explicit quantities/income and
upkeep are strong information design to keep. The older screenshots' unthemed
settings mismatch is historical, not evidence of a current mismatch.

No confirmed need for quests, minimap, inventory, crafting, skill hotbar, account
progression, monetization, save browser or matchmaking. Omit them. Walls, host
migration and general healing are expressly deferred in `docs/gameplay.md`.

## Runtime / tools actually detected

Godot 4.7.2 stable .NET (`ed1daf0bf`) exists in the local mise installation; the
unconfigured `godot` shim does not run from this worktree. Blender 5.2.2 LTS exists
at the existing worker fallback. `tools/asset_pack/worker.py` owns isolated factory
startup and `.cache/asset-check/logs/`; reuse it. `geometry.material()` owns
Principled creation; world art settings remain in `art_style.py`. Existing MCP
configuration is documented in README and mise task (`mcp-for-blender==2.1.3`,
localhost:9876); no session was connected to or mutated. Direct workers suffice.
Xvfb/xauth/glxinfo exist; `/dev/dri` presence alone does not prove a usable AMD GPU
or 16GB budget. Preview captures will use owned Xvfb/Mesa software OpenGL and
Dummy audio; actual renderer logged separately. No installation or cloud service.

The exploration preview later uses pixel-preserving native layout rather than the
game's canvas-items scaling, after its first 720px capture visibly shrank text.
This is an exploration-local comparison choice, not a game setting change; final
integration scaling requires explicit measurement (see `art-direction.md`).

Target sizes from `project.godot` and `ClientSettings.cs`: default 1100×820,
1280×720, 1600×900, 1920×1080; canvas-items/expand, monitor-dependent fullscreen
and arbitrary custom window sizes. First comparisons target the first two at
actual pixels; remaining responsive/input/state validation belongs to production.

## Decisions still open

Major UI direction (light ledger versus dark watch/slate), amount of original
Blender ornament, typography hierarchy versus current compact density. Need
artistic approval after owned rendered comparisons. Native default type first;
no font purchase/dependency. Proposed hierarchy sizes must be measured in real
compositions, not claimed universally accessible. Separately authorized game
label-removal work is pending; no permission to change the game and no restoration
of removed world labels. Pin migration evidence again before eventual integration.
See `art-direction.md`, `inventory.json`, `tasks.json`, `roadmap.md`,
`architecture.md`, `migration.json` for proposals and the approval gate.
