# Woodland Ledger — HUD/menu adaptation

The supplied [hud.png](references/hud.png) is retained unchanged, with
[source/hash provenance](references/README.md). This redo extends the **existing
native Ledger kit** and authoring hosts. It does not introduce a second UI
framework, gameplay/economy, terrain, service adapters or a new skill tree.
The previous light Ledger milestones remain historical evidence, not acceptance
for the changed resources. Retained woodland acceptance and exact
source/image/tool/package bindings are in
[woodland-validation.json](woodland-validation.json); [production.md](production.md)
preserves the earlier Ledger record. Current shipping qualification is linked below.

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

The woodland-only acceptance below is preserved at its tested revision, not
rebound onto the additive Worldtree source.
[Worldtree qualification](worldtree.md#review-fix-qualification-boundary) owns
current-source and shipping evidence and its limits; exact bindings are in
[worldtree-validation.json](worldtree-validation.json). Historical source/tool/package continuity
statements below describe the retained woodland revision. The woodland Theme,
original seal and compact 10-node component bytes are unchanged by Worldtree.

`production/woodland-live-resize-accepted/results.json`: **1395 checks / zero failures /
100 native captures**, including all prior Ledger and 126 landed compact-tree
checks. The focused woodland/font/input/layout slice at
`production/woodland-live-resize-accepted-focused/results.json` passes **624/0 with
14 captures**. Same-window resize checks cover wide→narrow→wide and independent
width/height transitions, retained construction category/control identities,
native scroll clamping and tail reachability, keyboard/pointer actions, modal
focus/invoker continuity, and preparation/lost projections. A single viewport
resize update changes only existing grid columns and quote viewport minimums;
context creation uses the same update. No resize rebuilds the HUD or resets
selection, category, focus or scroll. The retained hover checks discover the supplied progress description in
an actual native tooltip at 1280×720 and 1100×820, observe pointer propagation
through MatchControls to the enclosing HUD panel, and assert unchanged keyboard
focus, world-click counts and action requests. Progress keeps its rendering and
uses native MOUSE_FILTER_PASS; footer/category/skill-tree and scroll assertions
are unchanged.
Serial owned XTest Settings/modal probes pass **11/0** and **64/0**, with zero world
clicks. The retained independent UI-only native load checked ten scenes and 46
runtime files, including the woodland art/font/license, original seal and skill
purchase guards. The final catalog retains 13 source-bound native previews.
The later compact-tree API focus correction changed only the ZIP's `api.md`;
all runtime scenes/scripts/UIDs, Theme, fonts/license, art/import recipes,
manifest and extraction/import guidance are measured byte-identical to that
previously loaded package. Member names, order and entry metadata also match.
The previous deterministic ZIP was reconstructed from its retained native-load
extraction through the existing package owner, and its entire archive hash matched
the original native receipt before comparing every member with the actual final ZIP.
Native runtime qualification is therefore **reused by unchanged relevant inputs**,
not a claim that the documentation-only final ZIP was independently loaded again.
Current container/doc hashes, sizes, changed-member list and continuity measurements
are owned by [the preserved woodland package selection](catalog/worldtree-prior/package-check.json), which points
to the preserved original native-load receipt. The remaining code/art/metadata
bytes, excluding only the exact unmodified font/license, stay below the original
200KB budget; no arbitrary extra-art allowance is added. Decoded textures/glyph
caches and GPU allocation are not measured. Current source/test-driver, evidence
owner and recorded native tool-binary bindings also match the retained campaigns;
no new native captures, test counts or environment execution are claimed for this
documentation-only correction. Required final pipeline lint/CI remains separate.

The refreshed native-resolution review covers the two progress tooltip frames,
same-window Production/Army and modal resize frames, default/narrow construction,
preparation/lost, focus/hover and the HUD skill-tree modal, plus the affected
catalog HUD image. Remaining images
are fresh executable captures, not a claim of new visual inspection of every
frame. Exact-byte image-only review reuse is recorded separately in
`woodland-validation.json`; it does not certify old source. These images show quiet dark wells,
cream readable headings, parchment controls, original woodland accents and
separate green Ready/violet Pause. Narrow construction intentionally shows two
columns and a scroll-reachable continuation. The tree retains one middle root,
three indexed spokes, exact point/state words and a readable disabled purchase.
`woodland-validation.json` distinguishes native-resolution reviews from overview
coverage and binds every image; no old screenshots certify changed resources.
The previous 1193/0/92 full campaign, 422/0/6 focused campaign, catalog run,
payload and package receipts remain untouched as history. Their original
validation selection is retained at `production/woodland-accepted/validation.json`.
The later 1203/0/94 and 432/0/8 hover campaigns and their catalog/payload/package
receipts also remain historical, selected by the untouched
`production/woodland-hover-refreshed/validation.json`.
The first two live-resize focused attempts are also preserved at
`production/woodland-live-resize-focused/` and
`production/woodland-live-resize-focused-2/`. They exposed incorrect new-test
assumptions about intermediate native scroll clamping and the number of wheel
pulses needed for the longer lost-state content. The accepted checks allow native
clamping without a scroll reset and traverse the complete tail reason; no existing
assertions, font/card minima, dimensions or timeout targets were reduced.
The same final native test driver was also run in an isolated worktree-local copy
with only the pre-fix showcase restored: 19 expected failures included stale live
breakpoints and pane overflow. That negative reproduction is retained at
`production/woodland-live-resize-before-fix/`, not counted as current acceptance.
The pre-documentation package selection is preserved at
`production/woodland-live-resize-accepted/validation.json`; its original native
package receipt remains at `catalog/woodland-live-resize-accepted/package-check.json`.

The first refresh attempt could not start Godot because PATH exposed inactive mise
shims; its log remains at `.cache/ui/woodland-progress-hover/import.log`. A later
supplemental OS import crashed before checks; that log remains at
`.cache/ui-diagnosis/full-os-none-woodland-hover-refreshed/import.log`. The OS
owner's import was aligned with the existing Dummy-audio UI commands, then new
serial OS runs at `woodland-hover-refreshed-2` passed without world leaks. The new
runs use the exact existing Godot 4.7.2 .NET and .NET 10.0.401 binaries named in the
submitted plan, with path/version/binary hashes recorded in the validation binding.
No tools were installed or swapped and no global trust/configuration was changed.
The initial local Ruff limitation remains historical; this native UI refresh does
not claim to execute or waive the outer pipeline's required lint/CI phases.

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
