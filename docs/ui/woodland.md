# Woodland Ledger — HUD/menu adaptation

The supplied [hud.png](references/hud.png) is retained unchanged, with
[source/hash provenance](references/README.md). This redo extends the **existing
native Ledger kit** and authoring hosts. It does not introduce a second UI
framework, gameplay/economy, terrain, service adapters or a new skill tree.
The previous light Ledger milestones remain historical evidence, not acceptance
for the changed resources. Current acceptance and exact source/image/tool/package
bindings are in [woodland-validation.json](woodland-validation.json); [production.md](production.md)
preserves the earlier Ledger record.

## Visual rules and editable ownership

- Quiet ink/charcoal content wells (`#11131c`–`#22222c`), warm cream serif copy,
  related brown branch planes with thin bark highlights and olive leaves.
- Original shaded SVG branch frame, nine-sliced with **40px protected corners**;
  content stays 16px inside. Do not stretch a screenshot or corner illustrations.
  These are lightweight broad-plane illustrations, not photographic paint or 3D art.
- Original parchment/amber gradient cards/primaries; horizontal corners 24px,
  vertical corners 16px, card padding 14px horizontally / 6px vertically. Buttons keep native 36px hit heights.
  This avoids flattening a 48px corner slice onto a 36px control. Native generic
  and Primary buttons use 4px horizontal content insets so the landed compact
  tree's unchanged 124px nodes retain complete Available/Unfunded labels at 14px.
  Disabled Primary labels are cream on distinctly muted dark amber, not low-contrast
  dark text on a darkened texture. Native font metrics cover all node titles and
  cost/state lines in both funded and unfunded projections.
- Violet mushrooms and blue/violet flat-facet crystals are border accents, not
  luminous content backgrounds. The separate transparent owl/branch/lantern
  vignette is fixed-aspect and pointer/focus inert. It appears beside Settings and
  in the menu; the optional panel corner binding hides it if there is not 52px
  of spare space. It never takes space from a control or paints over one.
- The original editable Blender menu seal and its exact PNG bytes remain intact,
  displayed at the original 48px. No identity-art replacement or Blender rebuild.
- DejaVu Serif is an **unmodified installed redistributable font**, copied with its
  license into `UI/fonts/`; no font purchase/install/global configuration. Native
  14px body/buttons, 12px context/reasons and 18px headings retain actual text,
  quantity alignment, wrapping and tooltip semantics. Not baked image labels.
- Six original resource atlas cells are paired with names. Unknown names/icons
  fall back to text. Build quote icon keys are optional presentation hints, never
  inferred affordability. Costs, disabled reasons and selected/focus states remain
  textual and native. Blue 2px focus, lighter hover, depressed pressed, muted
  disabled, amber active tabs, green Ready and violet shared Pause are distinct.

All four SVGs have editable originals in `sources/ui/woodland/`, with byte-identical
runtime copies in `ui/preview/UI/art/woodland/`. [woodland-art.json](woodland-art.json)
binds those sources/outputs, font/license and supplied reference independently of
the old seal provenance. Edit an SVG manually, sync its runtime copy and update
bindings; import with the existing engine. Do not regenerate unrelated artwork.
`tools/ui/build_theme.gd` remains the sole intentional Theme authoring owner.

## Native composition and API preservation

Settings is top-left; stock/income and independently supplied upkeep are top-right.
Separate bottom branch panes hold selected-building illustration/layout data,
observed-city/detail/invitation controls, context/build quotes and match controls.
The selected-building summary is a separate fixed **illustrative projection**;
choosing a construction group is not a simulated selection/economy update.
The authoring host defaults to the existing Empty plot construction projection so
Production/Army/Defense/Trade/**Skill Tree** and six build cards can be compared
with the reference. Native selectors still expose all prior contexts/states.
The three-column default/two-column narrow grid and real scroll viewport preserve
long quotes/reasons rather than shrinking text. A native vertical section container
reserves the footer and a 16px separation; stock/upkeep scroll inside the remaining
upper viewport when supplied copy grows. All information remains wheel-reachable.
Extra upper projection lines also reduce only the construction scroll viewport at
720px, leaving stable controls and gaps.

Skill Tree binds the separately landed `skill_tree` authoring host and reusable
compact component. Re-selecting its tab reopens that same modal and closure returns
focus to the native tab. This task adds no competing one-point/three-path tree.
Its root/branch/cost/prerequisite/link/local-allocation semantics and native
focus/pointer/scroll lifecycle stay intact, with fresh inherited-skin captures.
The historical Research entry and canonical row alias remain independently intact.

`match_controls` optionally displays a supplied native progress projection:
`progress_value`, `progress_max`, `progress_text`; old dictionaries omit it and
retain their previous behavior. The demo uses fixed 2/3, not wave/turn arithmetic.
All canonical paths, ids/aliases and existing action/city/unit signals remain.
The Control hierarchy, visible-only modal lifecycle, dropdown-first Esc, local
world-input guard, ButtonGroup, ancestor scroll ownership and opaque cost/id
semantics are not replaced by decorative controls. Menu/dialogs inherit the same
Theme without new navigation flows. See [API](api.md).

## Current acceptance and visual review

`production/woodland-accepted/results.json`: **1193 checks / zero failures / 92
native captures**, including all prior Ledger and 126 landed compact-tree checks.
The focused woodland/font/input/layout slice passes **422/0 with six captures**.
Serial owned XTest Settings/modal probes pass **11/0** and **64/0**, with zero world
clicks. Independent UI-only loading checks ten scenes and 46 files, including the
woodland art/font/license, original seal and skill purchase guards. The final
catalog has 13 freshly bound native previews. The UI-only payload is 525106 file
bytes; the deterministic ZIP is 554641 bytes, including 389476 bytes for the exact
unmodified font/license. Its remaining 165165 bytes retain the original 200KB
code/art/metadata budget; no arbitrary extra-art allowance is added. Decoded
textures/glyph caches and GPU allocation are not measured. The actual generated ZIP is loaded
separately and its exact member/package hashes remain in `catalog/package-check.json`.

Reviewed the complete 92-frame set as reduced layout/color contact sheets, not
as proof of small-text legibility. Opened default/narrow HUD/construction/menu,
preparation/lost, focus/hover and all seven inherited-tree state images at native
resolution, plus all 13 catalog previews (four current images opened directly;
nine verified exact-byte matches to the immediately prior native-resolution review,
not reused old-source certification). Those actual images show quiet dark wells,
cream readable headings, parchment controls, original woodland accents and
separate green Ready/violet Pause. Narrow construction intentionally shows two
columns and a scroll-reachable continuation. The tree retains one middle root,
three indexed spokes, exact point/state words and a readable disabled purchase.
`woodland-validation.json` distinguishes native-resolution reviews from overview
coverage and binds every image; no old screenshots certify changed resources.

Layout and pointer failures are retained in [woodland-diagnosis.md](woodland-diagnosis.md).
The additional pre-acceptance `woodland-final-2` (1153/0) and `woodland-reviewed`
(1173/0) campaigns passed mechanically but actual image review found clipping of
Available/Unfunded and disabled-label contrast inherited from the shared Theme.
They remain intermediate, not final visual acceptance. Only shared Theme insets
and disabled colors changed; the landed component's node rectangles/topology,
allocation guards and focus/pointer/scroll lifecycle were not edited.

## Evidence methods and limits

Use the existing owned `validate.py`, serial `diagnose_settings.py`, UI-only audit,
focused catalog capture/build and independent generated-ZIP loader. Keep each
failed run and its exact result; use a fresh label after any resource/host change.
Review actual native PNGs, not software render success as art acceptance. Final
source/image/package bindings are refreshed after changes; old receipts are not
rebound onto new bytes. The browser frontend/model catalog is not reskinned.

Default 1280×720 and narrow 1100×820 are desktop sizes, not mobile claims. Longer
English supplied projections, multi-resource quotes, native focus/wheel, disabled,
modal and tab states are covered. Full localization/RTL/HiDPI, arbitrary tiny
windows, physical desktop input, hardware GPU/FPS/VRAM and actual game integration
remain unestablished. Xvfb/Mesa llvmpipe and headless independent package loading
are explicitly software/native-control evidence. No full-desktop capture or
personal browser/profile access is needed. The abstract hex context is not game
art or an adaptation of the reference's forest background.
