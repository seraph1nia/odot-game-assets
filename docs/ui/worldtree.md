# Living Worldtree — original modular artwork and standalone presentation

## Whisperwood selective refresh

Current [vivid color recovery](../vivid-palette/README.md) supersedes the greyed
ornament bodies: alive foliage/root greens and selected parchment/violet trim
recover their original colorful hues. Small luminous accents, SVG geometry/alpha,
24-node/23-edge topology, animation/state API and hit geometry are unchanged.
The [first overhaul ledger](../whisperwood/README.md) remains historical.
[worldtree-validation.json](worldtree-validation.json) owns the current full
standalone campaign selection, measured counts, capture hashes, payload and
package bindings. Its package receipt records a direct independent native load;
no historical archive continuity or static distribution-copy equality is claimed.
Current catalog HUD/Worldtree captures were inspected for color recovery and
retained readability. Full stage/size/gallery/transition artistic judgment is
not claimed; historical image reviews do not transfer to changed pixels. The older qualification narrative below remains historical.
No actual-game, native-GPU or artist acceptance claim.

This additive component does not replace the accepted 10-node `skill_tree`, its
allocation API/tests, or the woodland Theme. No main-game process, adapters,
abilities, economy, authority, networking or Blender work is part of this asset.
[API](api.md#living-worldtree-presentation-additive) owns snapshot/input semantics.

## Direction and original ownership

The supplied `~/Downloads/worldtree_reference_pack.zip` was read without mutation;
SHA256 `fb729dfc4e6f4c879fe0d7d25dcd39ff4b94e33c3f36fd920343e8ef290b2cf3`.
A safely relative, task-owned isolated extraction is retained in
`sources/ui/worldtree/reference/`. Its README attributes the six concept boards
to AI generation for the supplied conversation and canonical JSON/diagrams/starter
vectors to programmatic original handoff authorship; no third-party paid pack or
proprietary models are claimed. Supplied scripts were not executed. The manifest,
README, prompt, contact sheet, diagrams and all art boards remain source-only.

Reviewed directions: dormant/awakened modular boards, icon library and in-game
style board; canonical diagram/JSON owns structure, not inaccurate generated
board counts. The adaptation uses a gloomy blue-green forest, narrow brown trunk,
organically curved wooden connections, shallow dark bark joints, sparse dry olive
leaves, black-blue sockets, distinct muted versus available icons, warm amber sap,
fresh olive leaves, cream flowers and small cool mushrooms. Quiet original forest
silhouettes are decorative atmosphere, not a hidden background skill graph.

All runtime illustrations are original editable SVGs authored here, not cropped
reference sheets. `sources/ui/worldtree/` owns byte-identical runtime originals
for `ui/preview/UI/art/worldtree/`: 23 uniquely identified wooden branch SVGs,
separate root art/living-root detail, dormant/alive foliage, socket, halo, terminal
twig and atmospheric forest. Thirty separate icon SVGs have genuinely distinct
motifs and no baked ring: World Seed, shield, spark, leaf, flame, crossed swords,
heart, book, spiral, bow, paw, crystal, mushroom, moon, lantern, water, roots,
thorn vine, antlers, eye, acorn, feather, tower, rune, snowflake, poison, stone,
boot, owl and squirrel. Icon state tinting is presentation only.

`tools/ui/build_worldtree_art.py` is the explicit original authoring procedure,
not a runtime dependency or automatic rebuild. Preserve manual SVG edits before
rerunning; sync edited originals/runtime and reimport/check. Shared foliage/halo
textures may be reused but mutable alpha/sap routes/tweens live per instance.
The runtime uses no mutable shared shader/material. Sap follows the same sampled
Bezier as each wooden connection, beneath sockets and above wood. Foliage is owned
by that incoming edge only; root living details are independent root-owned art.

## Canonical shape and demonstration

`topology.json` is the authoritative supplied canonical JSON, preserving exact
IDs, parents, edge IDs and positions. `modules.json` binds each branch image's
crop/origin and exact parent/child route endpoints. The layout is built once;
A/B/C/D only replace visual state, not physical anchors or native controls.

- A: root only, **1** acquired.
- B: root and both consecutive trunk nodes, **3** acquired.
- C: root, trunk and all three primaries, **6** acquired.
- D: root, trunk, left primary, its two secondaries and four terminals, **10** acquired.
  Center/right families stay dormant (their first sockets may be externally available).

Choose **worldtree** in the existing standalone showcase. Native stage picker
supplies these complete snapshots. **Demonstrate one child awakening** supplies
Stage C then one newly acquired left secondary; it is a demo driver, not the
component's action handler. The actual action button only reports an intent.
Points stay top-left; there is no Owned count or upper-right title. Selected-node
information and request control form a compact footer.

## Reproduce in assets only

Use the installed pinned engine/SDK, private user settings and owned Xvfb display;
no tool installs or upgrades. Run native graphical commands serially.

```sh
python -m unittest tools.ui.test_worldtree
python tools/ui/validate.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --only worldtree --label worldtree-new
# Complete existing regression plus the additive Worldtree probe:
python tools/ui/validate.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --label worldtree-full-new
python tools/ui/audit_payload.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --label worldtree-payload-new
python tools/ui/capture_catalog.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --label worldtree-catalog-new
mise run catalog-build
python tools/ui/check_catalog_package.py --godot "$GODOT" --dotnet-root "$DOTNET_ROOT" \
  --label worldtree-package-new
mise run check
```

The pure validator enforces 24 unique nodes, 23 unique connections, canonical
parents/edges, 1/2/3/6/12 roles, expected child degrees, connectedness/no cycles and
exact A/B/C/D fixtures, with negative duplicate/cycle/parent witnesses. Original
SVG/XML, icon uniqueness/source equality and wood-route endpoints are checked.
Native tests use production Controls, pointer press/release, native Tab/Enter,
signals, intent-only points/acquired witnesses, malformed snapshot atomicity,
all 30 imported replaceable icons, pre/post independent sibling state and real
sap-before-leaves transition assertions. Fresh actual viewport captures cover
A/B/C/D at **all four requested sizes**, transition before/in-flight/after at
1280×720 and a native icon gallery. The existing compact tree tests are retained.

Current measured bindings and visual-review limits are selected in
[the Whisperwood qualification](#whisperwood-selective-refresh). Earlier campaign
failures/intermediates and historical woodland accepted evidence are preserved,
not rebound onto changed source. Historical re-encoded private image-review copies
were only for inspection transport; original native screenshots retain their exact hashes.

## Review-fix qualification boundary

This section describes the historical pre-Whisperwood review fixes and shipping
campaign, not the current campaign selection. Current-source qualification is
owned by [the Whisperwood refresh](#whisperwood-selective-refresh).

The review fixes preserve the actual underlying showcase screen on dialog closure
and implement the [API's non-modal native traversal contract](api.md#living-worldtree-presentation-additive).
The focused executable checks exercise escape and re-entry in both directions in
the actual showcase, enabled→disabled footer changes,
direct and switch-to Worldtree Settings closure, native Close/Escape, invoker
restoration and dialog replacement. Snapshot, pointer, icon, animation and render
coverage remains in the same focused campaign.

The submitted receipts below qualify their recorded pre-fix inputs only, not the
changed runtime or host. Fresh review-focused results use
`production/worldtree-review-fixes-2/results.json`, separately from prior failures
and accepted evidence. The first review-focused attempt is preserved at
`production/worldtree-review-fixes/` with its four disabled-footer forward-escape
failures and measured failing-input hashes in `failure-binding.json`. Its native
Tab sequence exposed that disabling a Button does not remove `FOCUS_ALL`; the
footer now also loses native focusability while disabled and regains it when
available. The retained shipping campaign is in
`catalog/worldtree-shipping-refresh/shipping-check.json`: UI-only loading,
14 native catalog views, the real catalog build and direct loading of its recorded
ZIP passed. Its original direct-load receipt is preserved unchanged alongside it
at `catalog/worldtree-shipping-refresh/package-check.json`. The recorded archive
and then-published static copy were entirely byte-identical. All 14 catalog PNGs
match the pre-review images; the Worldtree, HUD and menu images were also reopened.
The retained pre-Whisperwood binding in
[`../whisperwood/ui-before-validation.json`](../whisperwood/ui-before-validation.json)
selects that focused campaign and its later docs-only package continuity;
neither certifies the changed Whisperwood artwork. The original full-campaign
binding, payload, previews and package receipt remain unchanged under
`catalog/worldtree-pre-review/`.

## Submitted measured acceptance (before review fixes)

`production/worldtree-ready/results.json`: **3220 checks / zero failures / 121
actual captures** = the retained 1395-check/100-frame standalone regression plus
1825 additive Worldtree checks/21 frames. All 16 A/B/C/D × requested-size images,
three meaningful transition frames, the 30-icon gallery and the fixed-caption
showcase were opened/inspected at native size through validated private RGB PNG
review copies. Twenty final image files are measured byte-identical to already
inspected image bytes; the final timed in-flight frame was newly inspected.
This is image-only review reuse, not old source/test/package qualification.
Three actual decoded RGB crop comparisons independently show unchanged center/
right families, the unrelated left secondary and the root/trunk in before,
in-flight and after frames. Production per-module state witnesses also pass.

Fresh independent **UI-only** and **actual newly generated ZIP** loads both check
11 ready scenes, the preserved compact-tree guards and Worldtree snapshot/intent/
unknown-icon/30-texture contracts, including a real headless child animation and
unchanged incoming trunk sibling. The headless probe is resource/state evidence;
the actual owned windowed images above qualify appearance. No older package load
was relabeled. The catalog contains 15 entries (11 native components, Theme,
original seal and two authoring examples), with 14 fresh native previews. Existing
generator/static HTTP/package consumer tests pass; no new browser campaign is
claimed. The browser driver's former pre-compact-tree counts are updated to the
actual 15 total/11 component entries, without UI frontend changes.

The original legacy serialized **200KB** ceiling is preserved (168,922 bytes
excluding the unchanged font/license). Explicitly authorized Worldtree source/
import/UID files are separately measured and bounded to **200KB**: 189,981 bytes
across 129 runtime members, including 112,924 bytes of original SVG/JSON art.
The full UI payload has 175 files / 715,087 bytes; the shared unmodified font and
license account for 389,476 bytes. This is a scoped original-art addition, not a
blanket allowance for unrelated files; all actual package members/hashes and the
entire generated ZIP are bound in the preserved
[`catalog/worldtree-pre-review/worldtree-validation.json`](catalog/worldtree-pre-review/worldtree-validation.json).

Preserved failures/diagnosis are independent of final acceptance: the first
keyboard-route campaign exposed Godot's geometric fallback from an explicitly
disabled focus target (two assertions). The submitted enabled/disabled routes remained
explicit, with real available-footer Tab/Enter and disabled-wrap witnesses. Those
wrap assertions described the old confined component, not host escape; the review
fix replaces them with actual showcase boundary traversal in both directions. An
earlier mechanically passing showcase image had a stale A caption while showing
D; inspection caught it, the stage picker was synchronized, and both stage/D and
demo/C assertions plus a fresh correct-caption picture now pass. The original
failure result/log and diagnosis image are retained beside the final results.
Superseded task-only campaigns and their full logs/captures remain under
`.cache/ui/worldtree-intermediates/`; prior historical accepted woodland evidence
was not altered. Image API transport interruptions were handled by retrying only
the unfinished validated image inspection, never rerunning acceptance for a
transport error.

## Qualification limits

Windowed Godot on owned Xvfb/Mesa llvmpipe proves actual software-rendered asset
appearance and native Controls in this standalone fixture. It does not certify
native GPU performance/FPS/VRAM, physical desktop input, game integration,
localization/RTL/HiDPI or arbitrary small windows. Future Godot exports must include
the entire UI resource set and the two runtime JSON files in the non-resource
export filter; selective-scene/PCK export is not qualified by raw-project loading.
The retained UI-only and generated-ZIP loaders qualify their recorded inputs;
the current package and visual-review scope are described in
[the Whisperwood qualification](#whisperwood-selective-refresh).
Headless loading/input never substitutes for native rendered image inspection. References, authoring
sources, prototypes, tests and caches are never portable runtime dependencies.
