# Local catalog verification

## Mixed native UI catalog — 2026-10-10

The generated static artifact now contains **118 unchanged model entries plus 13
native UI resources/examples**. This task did not rebuild/export/render the 3D
artwork or change original Blender/PNG/runtime UI files. Both 2D Blender UI sources
remain excluded from implicit 3D selection; GLB thumbnail generation explicitly
selects only model records. Existing associations/export metadata formats remain
v1; the deliberately mixed generated index is v2.

[UI catalog evidence and authoring](../docs/ui/catalog/README.md) owns the scoped
native-preview, independent generated-package load, fresh 637-check UI regression,
source/render/image/identity bindings, retained failures and honest integration
limits. [Browser evidence](../docs/ui/catalog/browser-review.json) retains the
original Chrome full-suite results/screenshots and separately records the repaired
frontend's focused alias-search regression. See the
[presentation evidence owner](../docs/ui/catalog/README.md#checked-package-and-presentation)
for their distinct bindings, native/browser scope, visual limits and package checks.

The original `mise run check` run passed Python lint/syntax, JavaScript syntax and
unit checks; this historical result does not certify subsequent changes.
New generation/packaging tests execute real consumers and HTTP fetches, enforce
binding/path/dimension failures and every existing model ID, and exercise the
actual warm GLB thumbnail/export planners without sending native UI to Blender.
The generated ZIP's nine scenes, Theme and seal also loaded in an independent
Godot project; normal CI needs no new Godot installation because source-bound
native captures are committed and normal static generation validates bindings.

This is implementation acceptance, **not** a manual deployment, publication,
merge or game migration. Required delivery review/push/PR/CI belongs to the
configured same-worker no-mistakes handoff.

## Historical model-only verification

Verified with real repository exports in Chromium on 2026-10-04.
The catalog discovered all 40 exports present at the end of verification,
including 16 reusable kit components with links to their shared Blender source.
Every export in that verification snapshot had an explicitly generated thumbnail;
this is historical evidence, not thumbnail coverage for later additions.

## Automated discovery and merge checks

`python3 -m unittest tools.asset_catalog.test_catalog -v` passes eight tests:
recursive discovery, new categories and standalone props, GLB facts overriding
stale manifest counts, explicit clip policies, scoped pack defaults, reference
association and missing-file updates, cache invalidation and stable index writes,
corrupt exports, invalid metadata shapes, and repository path boundaries.

Python compilation, JavaScript syntax checks, and `git diff --check` also pass.

## Browser checks

[`tools/asset_catalog/browser_checks.js`](../tools/asset_catalog/browser_checks.js)
is an optional acceptance script for `chrome-devtools-axi eval`. Open the catalog
root URL with no filters before evaluating that file's function. It checks the
real bakery, knight, and standalone sword using their loaded viewer state:

- Every discovered export appears; search and category/animation filters work.
- Grid browsing creates no model viewers; full GLBs load on selection.
- Camera zoom and reset, actual reference crop, and rendered preview work.
- Clip choices equal `availableAnimations` from the loaded knight GLB.
- Looping/one-shot defaults, playback, pause, speed, and loop override work.
- Scrubbing pauses at the requested time, including at 2× speed and after a
  completed one shot. One shots finish at their last pose.
- Source links and absent-reference placeholders work for the standalone sword.
- Search/filter/asset state appears in the URL; no remote browser resources load.

Directly opening `/?q=sword&category=props&asset=props%2Fsword` restores the selected
model and both filters. Desktop (1440×1050) and mobile (390×844) viewports were
inspected; neither the page nor the detail dialog has horizontal overflow.

## Live changes and failure recovery

Without restarting the server, an isolated temporary copy of the real sword GLB
was added in a nested new category, then updated, corrupted, restored, and removed.
The category and card appeared automatically. Updating its GLB replaced the
viewer and changed its content-hashed URL. Unrelated open models stayed loaded.
Corruption produced an inspection error and viewer retry control while other
assets remained browsable. Restoring the GLB recovered automatically; removal
cleared the viewer and showed an unavailable-asset message.

Temporary associations and optional source/reference/preview files were also
added and removed. Metadata updated the selected title and links while retaining
the loaded viewer. Missing optional files showed placeholders. All verification
fixtures and temporary associations were removed afterward.

The selected-source Blender export command was run against `props/sword`.
Before/after hashes of the existing `.blend` files confirmed none changed during
that operation. The command updated the export, manifest entry, and index.

Explicit incremental thumbnail rendering regenerated the changed sword only.
After all current thumbnails were generated, running the full thumbnail command
with an intentionally nonexistent Blender executable rendered **zero** thumbnails
and succeeded, confirming an unchanged collection does not start Blender.

Screenshots and command logs from this run are in the ignored `scratch/` folder.
Other modeling work occurred concurrently in this shared workspace and was left
intact; its new exports were discovered by the running catalog.

## Static build and source-based CI pipeline

The GitHub Pages workflow was added and passes `actionlint`. The extended test
suite passes 18 tests, including static packaging and batch export planning.
`mise run catalog-build` produces a deployable artifact without editable sources.

The Blender export, incremental thumbnail rendering, and static packaging stages
were run against an isolated copy of the current authored sources, starting with
no GLBs. The pipeline generated 55 GLBs from 38 `.blend` files, including shared
library components and eight animated characters. All source hashes remained
unchanged, and the static artifact contains no `.blend` files.
A second complete source-export run produced identical GLB hashes and rendered
zero thumbnails, confirming that the warm thumbnail cache remains incremental.

That source-generated artifact was served by Python's ordinary static HTTP
server under `/odot-game-assets/`. All 28 browser acceptance checks passed there,
including building/character/prop loads, clip discovery, one-shot playback,
scrubbing, URL state, local dependencies, and exclusion of source downloads.

The workflow's GitHub-hosted dependency installation and Pages deployment have
not been run. Repository Pages settings must use GitHub Actions, and the workflow
and asset changes must be committed and pushed to `main` to trigger deployment.
