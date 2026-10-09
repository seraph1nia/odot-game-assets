# Evidence-led UI workspace

This layout is additive. World art catalog, exports, workers and MCP remain intact.
Current files are **approval explorations**, not the production library.

| Location | Responsibility | Current or future |
|---|---|---|
| `docs/ui/` | Discovery, art proposal, inventory, task state, roadmap, migration | Current |
| `docs/ui/previews/` | Owned actual Godot captures and capture metadata | Current |
| `sources/ui/explorations/` | Two editable original seal `.blend` sources | Current |
| `tools/ui/explore_crest.py` | Limited source/render generator; uses existing geometry materials | Current |
| `tools/ui/capture_explorations.py` | Owned-display capture of comparison scene | Current |
| `tools/ui/test_plan.py` | Cheap plan/source/PNG contracts | Current |
| `ui/preview/project.godot` | Self-contained Godot project; GL Compatibility | Current |
| `ui/preview/explorations/` | Temporary comparison Controls and theme construction | Current, not migration payload |
| `ui/preview/art/explorations/` | Transparent PNGs imported by comparisons | Current, one copy only |
| `ui/preview/UI/theme/` | Approved reusable Theme and tokens | Future after approval |
| `ui/preview/UI/art/` | Approved game-ready render output | Future after approval |
| `ui/preview/UI/components/` | Data-only reusable scenes/scripts | Future after approval |
| `ui/preview/prototypes/` | Mocked full HUD/menu/dialog compositions | Future after approval |
| `sources/ui/` | Approved editable Blender sources and parameters | Future production files |
| `tools/ui/` | Only UI-specific generation/capture/validation glue | Grow as needed, not generic framework |
| `.cache/ui-explorations/`, `.cache/asset-check/logs/` | Private full logs, owned runtime/XDG state | Ignored |

Do not create empty future directories. Runtime PNG output is rendered directly
into the project art directory: separate source, rendered artwork and native
component files **without duplicating rendered textures in another exports tree**.
No dynamic text is baked. Production `res://UI/...` paths are proposed so `UI/`
can eventually copy into a game root as a coherent namespace; preview compositions
will live outside it. Exploration paths are intentionally not final API promises.

## Smallest implementation strategy

Use native Theme/StyleBoxFlat for stretchable surfaces and native Button, Label,
GridContainer, ScrollContainer, OptionButton, HSlider and dialogs. Native vector-like
surfaces preserve corners without nine-slice textures. Only fixed ornaments merit
Blender at first. Keep seal at 48px, do not stretch it with panel size. A later
painted border is justified only by visible benefit; then record all slice margins,
minimum size and alpha checks. No whole-menu image or custom control framework.

Keep typed data/opaque ids in component properties and action intent in signals.
Game adapters keep `Game.Core` rules, quotes, generations/stage serials, session,
Steam, prefs, audio, unit picking/model playback and authority timing. The preview
has no sockets, credentials, download service, C# gameplay reference or external
runtime paths. GDScript preview reduces build dependencies; eventual C# consumers
can connect the same scene signals. Game runtime architecture is reused at the
boundary, not cloned into the asset package.

## Traceability and constraints

Each approved Blender export will get source-relative `.blend`/generator/parameters,
shared-material/render dependencies, output dimensions/color/alpha and hash entries.
Current exploration parameters are in `explore_crest.py` and saved scene properties;
Cycles CPU, 32 samples, orthographic 192px transparent RGBA, AgX/Medium High Contrast,
large Area key, intended 48px. These UI render settings are deliberately separate
from world studio defaults and do not modify `art_style.py`.

Sources are saved before render; image output paths in saved Blender scenes are
worker-local regeneration state, **not runtime Godot dependencies**. Generator
resolves repo-relative output paths. `.godot` caches and Blender backup files stay
ignored; original sources, Godot script UIDs and PNG import descriptions can track.
Full supplied references and game-source screenshots remain in their original
locations, not copied into public deliverables. Only original exploration pictures
are new publication candidates.

No source `AGENTS.md`/`CLAUDE.md` edits, disruptive convention migration, shared
MCP scene access or other worker dependencies. D–G establish tested portability;
this phase establishes only a self-contained exploration project.
