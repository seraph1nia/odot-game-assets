# Repository cleanup investigation — qualitative evidence

Assignment base: `60ce86f04c02419d9c09d30c2e25931345bf2bf3`.
Only planning files in this change have been written. No assets or source files have been changed or removed.

## Measurement limitations and retained resolution

Explore permits native read/glob/grep, but restricts shell execution to relevant agent-browser interaction. These native repository tools expose content and paths, not Git tracking, file byte sizes, Git object storage, or independently calculated hashes. Browser interaction is neither necessary for this initial investigation nor an appropriate workaround for repository command restrictions.

Supervisor question `tracked-size-inventory` requests a read-only, base-bound inventory containing tracked paths and byte sizes, directory/extension totals, largest files, exact duplicate image groups, total tracked logical payload and Git/LFS storage information. Distinguish LFS pointers from resolved payload and missing payload. Distinguish tracked files from ignored/untracked files. Store output here or return it as retained evidence. This is prerequisite evidence for a concrete removal manifest and honest expected reduction; file counts, filenames and previously reported per-asset runtime metrics are not substitutes.

Retained supervisor answer to `tracked-size-inventory` says controller tools also cannot obtain these measurements. It explicitly permits completing a qualified qualitative plan, moves the inventory to the first Apply task after human plan approval, requires bounded candidate rules and preservation of uncertain files, and requires renewed approval for any broader scope. It authorizes no deletion or checkpoint. Accordingly this is no longer a planning blocker; measurements remain unknown, not guessed. See `design.md` for the final conservative selection rules, which supersede exploratory candidate strategies below. Controller strict validation has not been run by this worker.

## Confirmed structure and preservation boundaries

| Content | Initial disposition | Evidence and reason |
| --- | --- | --- |
| `sources/**/*.blend`, adjacent textures, source UI artwork | Keep | AGENTS.md and README preserve manual mesh/material/UV/rig work, packed maps and historical assemblies. Zero-user authored variants can be deliberately persistent (`docs/vivid-palette/README.md`, serialization diagnosis). No orphan purge or builder-based replacement. |
| `exports/**/*.glb`, runtime decals, native `ui/preview/UI/` resources | Keep | Catalog and consumer payloads. Runtime batching intentionally trades larger GLBs for fewer scene nodes (`docs/runtime-optimization/README.md:70-101`); size alone is not grounds to revert this accepted tradeoff. |
| `sources/reference/`, `docs/ui/references/hud.png`, manifests, provenance and licenses | Keep | Art authority index preserves supplied originals, framing and rights caveats. References must not be mistaken for generated evidence. |
| `exports/previews/`, `exports/thumbnails/` | Keep initially | Live catalog preview/thumbnail routes; generated does not mean unnecessary. Metadata associations and manifest precedence must be inspected before considering any specific file. |
| `docs/ui/catalog/` selected images | Protect selected dependency closure | `previews.json` binds current images, source identities and dimensions; package generation fails closed on changed/missing inputs (`docs/ui/catalog/README.md:55-90`). Not safe to delete this entire directory. |
| Historical `docs/**/evidence/`, `renders/`, comparison images and capture campaigns | Investigate for selective pruning/consolidation | Many before/after tiers and superseded iterations exist. Must identify actual consumers and useful retained comparisons before choosing individual removals. |
| JSON/Markdown/HTML receipts and ledgers | Retain provenance; update consumers explicitly if approved | Successor identities and some tests depend on historical ledgers. Small text is usually worth retaining even when redundant binary screenshots are retired. Do not falsify a prior acceptance record. |
| `catalog/vendor/`, tools, skills, CI and UI hosts | Keep | Bundled offline dependencies, licensing and active authoring/test/deployment workflows; not evidence bloat. |
| `.cache/`, `.lavish/`, `scratch/`, `dist/`, generated index and UI ZIP | Already ignored; no cleanup authorization | `.gitignore` already excludes these. They are not a tracked-tree saving unless inventory proves accidental tracking. Do not clean personal resources or caches. |

## Concrete evidence families and dependent references

1. **Whisperwood:** `docs/whisperwood/evidence/before/` contains per-asset full, `-192` and `-96` PNGs across building, character, prop and forest/component groups; `evidence/sheets/` has compact family sheets. `README.md:94-115`, `actual-review.html`, `renders.json`, `contact-sheets.json`, `completion.json` and report producers own the historical story. The record explicitly retains 118 matched model pairs and original export identities. Candidate strategy: keep selected useful sheets/focals and retire explicitly approved redundant per-asset tiers, not a directory-wide deletion.
2. **Second quality round:** `docs/quality-round-two/README.md` describes five changed buildings and retained first-round-after images as its baseline. The first round cannot simply be removed/rebound as current. Inventory, renders, review HTML and grayscale evidence must be mapped together.
3. **Vivid palette:** `docs/vivid-palette/evidence/` includes repeated `before` tiers, sheets and browser captures. `actual-review.html`, `renders.json`, inventory and README refer to them. `tools/asset_pack/test_vivid_review.py:34-46` reads and hashes real image paths/derivatives from the landed ledger; blanket deletion breaks fast tests. Historical grey imagery can remain useful as contrast with the current colorful direction, even though it is not the acceptance target.
4. **Native UI:** `docs/ui/catalog/` includes `native-5`, mini-skill-tree iterations, many `woodland-*`, `whisperwood-1`, `worldtree-*`, `vivid-palette-explicit`, browser and review-branch directories. These are candidates for a current-selection versus obsolete-run analysis, not confirmed disposable runs. Selected `previews.json`, `package-check.json`, `docs/ui/worldtree-validation.json`, validation prose and `tools/asset_catalog/test_ui_assets.py` / `tools/ui/test_worldtree_qualification.py` need dependency tracing. Historical ZIP in `docs/ui/catalog/browser/ledger-ui-historical.zip` is explicitly bound to earlier browser receipts; removal requires retiring those download claims honestly.
5. **AI texture POC/current seam correction:** protect pending handoff and three-revision comparison inputs initially. `docs/ai-textures/README.md` records unresolved end-to-end game acceptance and retained original inputs. `tools/asset_pack/test_ai_textures.py:217-244,273-306` checks PNG bytes, comparison profiles and predecessor identities. Original, initially delivered and corrected views have distinct purposes; do not treat different revisions as duplicates. Source-input archives/maps are preserved for provenance, including an intentionally empty invalid normal; unused or zero-byte is not sufficient justification for deletion.
6. **Other families:** inventory `docs/runtime-optimization/`, `docs/ambient-motion/`, `docs/detailed-ground/`, `docs/dreamlike-forest/` and `docs/quality-round/` along with root hidden directories. Runtime's matched-sheet and eight before/after pairs have demonstrated fidelity purposes. Check tracked backup/archive/video/large JSON/HTML files outside evidence roots too; do not assume images are the largest category without measurements.

## Recurrence paths already identified

- `tools/ui/capture_catalog.py:18-23` requires a fresh label and writes directly to `docs/ui/catalog/<label>`; its docstring promises all historical evidence is preserved. Private staging plus explicit promotion of selected evidence would avoid indefinite checked-in run accumulation. Final design leaves this hash-bound generator unchanged and uses retention checks and isolated staging guidance instead.
- `tools/asset_pack/woodland_review.py:28-39` writes directly to `docs/whisperwood/evidence/<stage>` and its render receipt. Historical producers must not silently refill retired evidence. Consider explicit scratch output/promotion and retirement guidance, with retained report reproduction remaining usable.
- `.gitignore` currently ignores local cache/build output but does not establish a curated evidence policy. Do not globally ignore PNGs or all docs images: source references and catalog dependencies are essential.
- Integrate a small manifest-based evidence policy into existing `mise run check`, with regression tests for accidental new run folders, byte-budget growth, missing retained images, and explicit approved exceptions. Choose concrete bounds from measured baseline, not arbitrary guessed totals.

## Measurement and implementation handoff

1. Receive read-only inventory; derive category/size distribution and verify exact duplicate groups. A matching filename or similar picture is not proof of byte duplication. Identical Git blobs may already be deduplicated in object storage despite occupying multiple checkout paths.
2. Enumerate exact approved-candidate paths, hashes, individual/group bytes, rationale, retained substitute and all consumer changes. Use conservative defaults for ambiguous content. Validate no overlap with authored/reference/runtime/current-preview closures.
3. For historical evidence retired from checkout, retain honest provenance and, if appropriate, immutable commit/path recovery instructions; don't leave broken live image links or make normal CI/network-free builds depend on fetching history.
4. Compute gross removed logical bytes minus any retained/new artifact bytes; report MiB and percentage of tracked checkout, distinct from Git object/LFS history. Ordinary deletions leave historical blobs reachable; no promised full-clone savings or history rewriting/GC/LFS migration.
5. Controller performs strict validation and obtains human approval of the bounded plan before Apply. If measurements reveal no safe candidates, report zero eligible savings instead of widening scope; broader pruning returns for a scope decision and renewed approval.

## Proposed validation scope (not executed)

- Read-only before/after tracked size/hash and catalog/payload inventory; protected sources/exports/references remain byte-identical.
- `mise run check`, focused evidence/retention tests, catalog index/static packaging and local-link/image resolution at root and repository subpath. Do not weaken freshness/predecessor negative controls or drop checks to make pruning pass.
- Browser check of changed review surfaces/catalog only if implementation changes their references, using task-owned browser/scratch evidence. Do not add tracked screenshots as a side effect of validation.
- No Blender rebuild/re-export or expensive full art acceptance solely for deleting documentation images. If a change unexpectedly requires authored/runtime byte changes, stop for scope review.
