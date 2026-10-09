# The Common Watch UI project

**Start here when resuming UI work.** Current deliverable: discovery, two original
rendered directions, inventory/planning and an **artistic approval checkpoint**.
Not a finished kit and not migrated. Overall A–G scope continues after approval.

1. [State/backlog](tasks.json) and [roadmap](roadmap.md): current milestone,
   dependencies, acceptance and blocked decision.
2. [Discovery](discovery.md): pinned game evidence, keep/redesign/gap classification
   and uncertainties. Reuse these findings before investigating again.
3. [Artistic proposal](art-direction.md): exact owned previews, actual review,
   bounded revisions and precise approval questions.
4. [Inventory](inventory.json), [architecture](architecture.md) and
   [migration map](migration.json): justified assets, minimal separation, future
   portable namespace and integration risks.
5. [Validation](validation.md) and [exploration source bindings](exploration-assets.json):
   what really ran, what failed initially and what remains untested.

## Reproduce these explorations (inside assets only)

Requires existing Blender, Godot 4 and Xvfb/xauth/Mesa. Do not install anything,
connect to shared MCP scenes or run these commands in the game input checkout.
This project's detected Godot is the .NET build; it needs the existing SDK root
even though the scenes are GDScript. Set `GODOT` to an installed engine executable
and `DOTNET_ROOT` to the existing SDK root, then prepend that root to PATH if using
the .NET engine. These are command environment inputs, not runtime resource paths.

From the asset repository root:

```sh
# Overwrites only our two exploration sources/PNGs; preserve manual edits first.
python -m tools.asset_pack.worker tools/ui/explore_crest.py --label ui-exploration-seals
# The worker uses the existing Blender resolver and private log path.
# Refresh hashes in exploration-assets.json intentionally after regeneration.

# Isolate the preview's user-data/config/cache; never touches game preferences.
mkdir -p .cache/ui-explorations/{data,config,cache}
export XDG_DATA_HOME="$PWD/.cache/ui-explorations/data"
export XDG_CONFIG_HOME="$PWD/.cache/ui-explorations/config"
export XDG_CACHE_HOME="$PWD/.cache/ui-explorations/cache"
export PATH="$DOTNET_ROOT:$PATH"
"$GODOT" --headless --path ui/preview --editor --import
python tools/ui/capture_explorations.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT"
"$GODOT" --headless --path ui/preview --script res://explorations/check_images.gd
python tools/ui/test_plan.py
mise run check
```

Captures require **prior preview import**. They own disposable software X11 displays
and XDG paths, use Dummy audio, time out at 60s per image and terminate their owned
process group on failure. Full logs are `.cache/ui-explorations/`; only compact
renderer/path metadata and original images are tracked. No browser/desktop config
or network use. GUI review can open `ui/preview/project.godot` independently;
no game repository is needed. Directions/compositions select via Godot user args
`--direction=ledger|watch` and `--composition=hud|menu`. Menu/action buttons here
are render/native-state samples without game actions, not functional prototypes.

Do not rerender unchanged inputs as an artistic loop. Review actual images, record
a concrete issue, make at most a bounded targeted revision, capture again and
update evidence. Deterministic checks verify mechanics; they do not certify beauty.
