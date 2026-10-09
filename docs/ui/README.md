# The Common Watch UI workspace

**Resume here:** intended standalone Ledger **E–G is complete and checked**:
**637/0, 79 image bytes with visual-review coverage**, fresh serial OS Settings/modal and independent
payload audit. Accepted M0/M1/representative milestones are preserved.
[coverage.md](coverage.md) defines finished standalone scope and separate external
integration requirements. **No game integration/mutation, migration or publication.**
MAIN owns the coordinated delivery handoff; no competing pipeline.

| Need | Read |
|---|---|
| Current work / outstanding acceptance | [tasks.json](tasks.json), [production.md](production.md), [roadmap](roadmap.md) |
| Exact approved direction and scope | [decisions](decisions.md); [M0 artistic evidence](art-direction.md) |
| Avoid rediscovering game behavior | [discovery](discovery.md), [inventory](inventory.json) |
| Reuse components / prepare migration | [API](api.md), [architecture](architecture.md), [migration mapping](migration.json), [payload audit](payload.json) |
| Actual checks / final pictures | [validation](validation.md), [current results](production/review-dialog-close/results.json), [visual bindings](visual-review-dialog-close.json) |
| Retained acceptance byte contracts | [preservation manifest](preservation.json), [submitted visual binding](visual-review.json) |
| Why modal is not a Window | [causal diagnosis](settings-diagnosis.md), [contrary ownership result](modal-alternatives.md) |
| Original Blender/PNG provenance | [source bindings](exploration-assets.json) |

## Reproduce checks in assets only

Use existing Godot/Xvfb/xauth/Mesa; no install/upgrade. Never run these in the game
checkout or use shared MCP/GUI Blender scenes. Set `GODOT` to the installed engine
executable and `DOTNET_ROOT` to the existing SDK root when using the .NET engine.
These command inputs are not runtime resource paths. The drivers own private XDG
state/displays, Dummy audio and bounded process groups; full logs stay in `.cache/`.

```sh
python tools/ui/test_plan.py
# Use a new label so earlier failed logs/pictures remain intact.
python tools/ui/diagnose_settings.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --case full --input os --label review-new
python tools/ui/diagnose_settings.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --case modal --input os --label review-new
python tools/ui/validate.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" --label review-new
python tools/ui/audit_payload.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" --label review-new
mise run check
git diff --check
```

Run graphical drivers **serially**: concurrent xvfb-run auto-number startup raced
in retained evidence. `validate.py --only production` is the bounded new-input route
(no captures); omit `--only` for full regression/capture acceptance.

`validate.py` imports fresh, performs actual native events/state/layout assertions,
binds source hashes, and writes 79 captures/results under `docs/ui/production/<label>/`.
It rejects source changes during the run. `diagnose_settings.py` uses the same exact
Settings sequence with synthetic input or owned X11/XTest, plus isolated cases and
modal lifecycle checks; it does not directly cancel/refocus to make tests pass.
The historical `--counterfactual=focus` option is old Window diagnosis only, not an
acceptance route. `audit_payload.py` copies only UI/ into a new private project and
fails rather than overwriting its run directory. Plan tests certify metadata, not art.

Open `ui/preview/project.godot` independently for review. Main scene is
`prototypes/showcase.tscn`; screen/state selectors use mocks, no services. Final
reviewed pictures/results are in `production/review-dialog-close/`;
all 79 current PNGs match the reviewed `production/review-fixes/` bytes exactly;
`production/standalone-final/` and `visual-review.json` retain submitted acceptance bytes;
`production/m1-tab-scope/` and `production/production-package-reviewed/` preserve
accepted historical evidence, not proof of changed views. Other folders preserve failed/intermediate states. Review actual images,
record concrete issues and make bounded targeted changes; generated pictures alone
are not behavior or aesthetic acceptance. See `production.md` and `coverage.md`
for final checks, visual judgment and the external integration boundary.

## Authoring versus validation

The approved original seal was moved unchanged to `sources/ui/menu_seal.blend` and
`ui/preview/UI/art/menu_seal.png`. Its 192px RGBA source is displayed at fixed 48px;
no slice margins or additional initial Blender art. Do not rebuild merely to validate.
`tools/ui/explore_crest.py` rebuilds **both** original studies through the existing
isolated asset worker; preserve manual edits and obtain explicit regeneration scope
before running it. Saved sources are editable; source/output hashes are recorded.
The two 2D seal sources are excluded from implicit 3D discovery at `plan_exports()`;
other nested 3D sources and explicit catalog mappings retain their export behavior.
Historical result/source-binding and visual-review bytes are frozen in
`preservation.json`; ordinary preservation checks need no pre-rebase Git objects.
They do not independently reconstruct historical source checkouts. Portability
behavior is established by the private UI-only Godot loader, not source-text scans.

The native Theme authoring script is `tools/ui/build_theme.gd`; preserve manual
Theme edits before intentionally regenerating through a private headless engine:
`"$GODOT" --headless --path ui/preview --script "$PWD/tools/ui/build_theme.gd"` with
private XDG variables and the existing SDK environment. This writes the Theme, not
new artwork. Authoring tools/Blender are never runtime payload dependencies.

Coordinate a checked milestone handoff with MAIN. Configured no-mistakes owns the
later delivery review/fixes/tests/docs/lint/push/PR/CI; do not launch an independent
pipeline/push or confuse this standalone check with game integration acceptance.
