# Repository cleanup and evidence retention

## Scope and measured baseline

Base and starting HEAD both `60ce86f04c02419d9c09d30c2e25931345bf2bf3`. Inventory preceded deletion;
all 6,669 base-tracked paths matched their Git blob identities and were present.
Tracked logical checkout payload **1,885,408,597 bytes**
(1798.066 MiB); Git tree blob-size sum agrees exactly.
Measurements count each checkout path, not allocated filesystem blocks or unique blobs.
The staged OpenSpec planning package is additional to that base, not an asset change.

Method: `git ls-tree -rlz <base>` enumerated base entries; installed Python read each
existing file, measured `len(bytes)`, calculated SHA-256 and independently verified
`SHA1("blob " + length + NUL + bytes)` against the base object. `git ls-files -z`
and porcelain status distinguished new/staged/untracked/ignored paths. No fetch,
installation, maintenance, source generation or native capture was used.
All 6,669 `git check-attr filter` results were `unspecified`; zero pointer headers
or missing payloads were found. Git LFS is not installed (`git lfs version` fails),
so remote LFS objects/quota and historical LFS use are **not measured**.

Raw path sizes/hashes, all exact image duplicate groups, candidate consumer matches,
and catalog/payload baseline are kept locally in ignored `.cache/repository-cleanup/`.
They are not another committed all-file hash dump. Regenerate measurements from the
pinned base with the method above; the committed removal manifest contains every
deleted identity and its surviving exact counterpart.

### Tracked directory bytes

| Top-level path | Bytes |
| --- | --- |
| docs | 899110283 |
| sources | 555411304 |
| exports | 425677632 |
| catalog | 2737196 |
| tools | 1084332 |
| ui | 917172 |
| .agents | 229358 |
| .pi | 180485 |
| README.md | 46878 |
| AGENTS.md | 5619 |
| .github | 4815 |
| mise.toml | 1946 |
| openspec | 922 |
| .gitignore | 565 |
| pyproject.toml | 76 |
| requirements-checks.txt | 14 |

### Tracked extension bytes

| Extension | Bytes |
| --- | --- |
| .png | 1139286112 |
| .blend | 361484865 |
| .glb | 339575228 |
| .json | 22070187 |
| .webm | 9199093 |
| .gif | 3480704 |
| .jpg | 2358368 |
| .js | 1875979 |
| .py | 1060103 |
| .html | 1035905 |
| .md | 948965 |
| .log | 946843 |
| .wasm | 785682 |
| .ttf | 380660 |
| .svg | 377010 |
| .gd | 210034 |
| .zip | 120301 |
| .import | 71812 |
| .tres | 50769 |
| (none) | 38253 |
| .txt | 22153 |
| .tscn | 13476 |
| .css | 5792 |
| .yml | 4815 |
| .toml | 2022 |
| .sh | 1469 |
| .yaml | 922 |
| .uid | 614 |
| .godot | 461 |

### Largest tracked files (all protected)

| Path | Bytes |
| --- | --- |
| exports/buildings/town_hall.glb | 20811552 |
| exports/environment/hex_lantern_bridge.glb | 19848216 |
| sources/environment/hex_glowing_mushrooms.blend | 18154275 |
| exports/buildings/archery_range.glb | 17619280 |
| sources/environment/hex_lantern_bridge.blend | 17303742 |
| sources/environment/hex_woodland_bridge.blend | 17200577 |
| sources/environment/hex_crystal_shrine.blend | 17075711 |
| sources/environment/hex_mystical_grove.blend | 17010844 |
| sources/environment/hex_crystal_grove.blend | 16988966 |
| sources/autobattler.blend | 16746368 |
| sources/environment/shared_forest_kit.blend | 16491085 |
| exports/buildings/magic_academy.glb | 16186332 |
| sources/environment/hex_rune_shrine.blend | 15958346 |
| sources/environment/hex_bioluminescent_grove.blend | 15826850 |
| sources/buildings/archery_range.blend | 14570870 |
| sources/environment/hex_dream_menagerie.blend | 14283124 |
| sources/environment/hex_hollow_watchers.blend | 13958233 |
| exports/environment/hex_woodland_bridge.glb | 13563028 |
| sources/environment/hex_butterfly_glade.blend | 12265531 |
| exports/buildings/barracks.glb | 12216796 |

### Approved candidate-root inventory (before deletion)

| Root | PNGs | Bytes |
| --- | --- | --- |
| docs/whisperwood/evidence/before/ | 373 | 36901155 |
| docs/whisperwood/evidence/after/ | 369 | 36642229 |
| docs/quality-round-two/evidence/before/ | 17 | 2020984 |
| docs/quality-round-two/evidence/after/ | 17 | 2019563 |
| docs/vivid-palette/evidence/before/ | 368 | 36607645 |
| docs/vivid-palette/evidence/after/ | 368 | 37391797 |
| docs/vivid-palette/evidence/browser/ | 3 | 954550 |
| docs/ui/catalog/browser/ | 16 | 2484729 |
| docs/ui/catalog/mini-skill-tree-1/ | 13 | 400013 |
| docs/ui/catalog/mini-skill-tree-2/ | 13 | 400013 |
| docs/ui/catalog/mini-skill-tree-final/ | 13 | 400013 |
| docs/ui/catalog/native-5/ | 12 | 335318 |
| docs/ui/catalog/review-branch-artifacts-1/ | 13 | 400013 |
| docs/ui/catalog/vivid-palette-explicit/ | 14 | 1199569 |
| docs/ui/catalog/whisperwood-1/ | 14 | 1198322 |
| docs/ui/catalog/woodland-accepted/ | 13 | 813901 |
| docs/ui/catalog/woodland-final/ | 13 | 813643 |
| docs/ui/catalog/woodland-hover-refreshed/ | 13 | 813901 |
| docs/ui/catalog/woodland-live-resize-accepted/ | 13 | 813901 |
| docs/ui/catalog/woodland-reviewed/ | 13 | 813863 |
| docs/ui/catalog/worldtree-pre-review/ | 0 | 0 |
| docs/ui/catalog/worldtree-prior/ | 0 | 0 |
| docs/ui/catalog/worldtree-ready/ | 14 | 1199670 |
| docs/ui/catalog/worldtree-shipping-refresh/ | 14 | 1199670 |

The candidate union is **1,716 PNGs / 165,824,462 bytes**.
All non-PNG archives, GIF/video/JSON/log files and everything outside this union
remain unchanged, regardless of size. Required GLBs and authored Blender files
are not cleanup opportunities within this approval.

## Selection and protected dependency closure

**24 unbound duplicates / 1,135,052 bytes** qualify;
the exact pre-deletion dispositions are in [evidence-cleanup.json](evidence-cleanup.json).
Before = `docs/ui/catalog/whisperwood-1/`; after =
`docs/ui/catalog/vivid-palette-explicit/`. Every replacement was independently
compared byte-for-byte as well as by SHA-256. Preserve stage identity even where
before and after happen to match. No source/reference/export or receipt is removed.

`tools/asset_pack/vivid_review.py:134-155` copies native views into
`evidence/{before,after}/ui/` but stores the **original** views in inventory rows.
`make_ui_sheets()` reads those original paths, not the redundant copies;
`write_page()` uses only the hud/worldtree copies, which remain. The other 24
copies have no direct path/relative-link consumers in tracked JSON, Markdown,
HTML, code, scene or structured records; dynamic view/sheet logic confirms they
are not indirect inputs. No mutable image link needs repointing. The generator
stays byte-identical: rerunning it can recreate the redundant copies, and the
retention check will reject promoting them unintentionally. Do not run it here.

The other **1,692 candidates remain**:

- 1,684 have structured JSON/receipt references. Whisperwood `renders.json`,
  `completion.json`, `contact-sheets.json`, quality-round-two `renders.json` /
  `inventory.json`, and Vivid `renders.json` / `inventory.json` preserve the
  before/after and derivative chains. Copying a prior stage is not grounds to
  rewrite its immutable ledger. `woodland_report.py`, `woodland_review.py`,
  `quality_round_two_review.py` and `vivid_review.py` generate these paths/tiers.
- Four more have textual consumers; keep their diagnostic/story context.
- Four unreferenced Whisperwood before/decal images remain **uncertain**: no
  demonstrably superseded same-stage retained comparison was established.
- All historical UI run `previews.json` files retain their full image closure,
  including mini-skill-tree, woodland, native-5, worldtree and browser campaigns.
  Failures, revision labels and historical package/browser claims are unchanged.

Protected consumers checked:

- `tools/asset_pack/test_vivid_review.py` binds every model render and its two
  derivatives; `test_ambient_contract.py` chains Vivid exports. Preserve all.
- `tools/asset_pack/test_ai_textures.py` reads original/delivered/corrected PNGs,
  generated comparison names and predecessor contracts. Its entire tree remains.
- `tools/ui/test_worldtree_qualification.py` follows worldtree-validation's
  results, package check, historical binding, capture hashes and static ZIP copy.
  `tools/asset_catalog/test_ui_assets.py` also binds historical browser frames
  and ZIP; neither source nor transitive receipt/image closure is changed.
- `tools/asset_catalog/ui_assets.py` selects current previews, generator and
  native source bindings, 175 payload members and seal source/output identities.
  `CatalogIndex` baseline records 133 IDs and 118 model identities. Catalog
  manifest/associations and reference index need no path changes.
  `build_site.py` copies selected resource/preview/reference/export records,
  not arbitrary historical evidence. All selected paths remain intact.
- All `sources/`, `exports/` base entries, native `ui/`, supplied references,
  companion textures, font/license files, tools/generators and immutable JSON
  are hash-preserved. No orphan purge, texture recompression or model rebuild.

## Duplicate potential is not deletion authority

Across PNG/JPG/JPEG/WebP files there are **991 exact
SHA-256 duplicate groups**, with **345,758,054**
redundant per-path logical bytes if hypothetically retaining one per group.
This is deduplicated group accounting (`size × (paths − 1)`), **not** an approved
saving. Useful receipt-bound stages dominate many groups; near matches are never
treated as duplicates. Git already stores identical blob content once.
The complete local group list is `duplicate-images.json` in the ignored inventory;
the removal manifest publishes the selected exact hashes and counterpart paths.

## Storage outside the checkout denominator

Git common directory: `/home/bart/projects/personal/opencrew/.abracode/repositories/odot-game-assets/checkout/.git` (shared worktree storage).
`git count-objects -v` at baseline: 6 loose objects / 36 KiB, 7,194 packed objects,
one pack / 2,087,960 KiB (Git's reported pack storage, not checkout payload).
It warned of one zero-size garbage entry at the worktree's `refs` path; no repair
or maintenance was attempted. Local common-dir `lfs/objects` payload: 0 bytes.
Historical/remote LFS storage cannot be inferred from that absence.
Initial untracked and ignored listings contained zero existing files; inventory
outputs themselves were created afterwards under ignored cache. Subsequent test,
static-build and cache outputs are **excluded** from tracked-checkout accounting
and are not deleted by this change.

Ordinary deletion leaves old image blobs reachable in Git history. No history
rewrite, Git GC, LFS migration, full-clone reduction, remote reclamation or cache
cleanup is performed or promised.

## Persistent evidence policy

[evidence-retention.json](evidence-retention.json) enumerates **4,510**
retained PNGs with initial aggregate cap **830,546,281 bytes**.
Each group's `root` plus each exact relative key in `files` is a retained path;
its positive integer value is the per-path byte cap. Initial individual caps equal
actual retained bytes and the aggregate equals their sum. Group purpose and
provenance are shared, avoiding thousands of repeated rationale strings.

| Concrete monitored root | Retained PNGs | Cap bytes |
| --- | --- | --- |
| docs/ai-textures/comparisons | 38 | 15055082 |
| docs/ai-textures/renders | 76 | 20042262 |
| docs/ai-textures/seams | 59 | 26965147 |
| docs/ambient-motion/evidence | 153 | 32395160 |
| docs/dreamlike-forest/evidence | 63 | 42909247 |
| docs/quality-round-two/evidence | 34 | 4040547 |
| docs/quality-round/evidence | 83 | 35661536 |
| docs/quality-round/history/before-material-fix/evidence | 2 | 127321 |
| docs/runtime-optimization/evidence | 49 | 5964559 |
| docs/ui/catalog | 201 | 13286539 |
| docs/ui/previews | 12 | 735015 |
| docs/ui/production | 2257 | 454617839 |
| docs/vivid-palette/evidence | 726 | 77954455 |
| docs/whisperwood/evidence | 757 | 100791572 |

These concrete roots cover the approved candidates, all existing
`docs/**/evidence/` trees and the named AI-texture/native-preview trees, not
`docs/ui/references/` or authored source/export trees. The validator discovers
new `docs/**/evidence/` trees too and rejects unlisted ones. New diagnostic roots
outside this naming convention require explicitly extending the discovery contract
and policy in review, not choosing an unmonitored name to bypass retention.

Run `python3 -m tools.evidence_retention` or `mise run check` (the latter discovers
`tools/test_evidence_retention.py`). Missing retained files, unlisted captures,
invalid/duplicate/traversing paths, missing purpose/provenance and exceeded
individual/aggregate caps fail with paths and corrective guidance. This is **not**
a freshness validator: the existing image/generator/hash tests remain authoritative.

### Disposable captures and reviewed exceptions

- Default exploratory output: existing ignored `scratch/` or `.cache/`;
  for example `scratch/evidence/<task>/` or `.cache/evidence/<task>/`.
  Task-owned browser screenshots use the controller-assigned scratch directory.
  Do not globally ignore PNGs or docs and do not clean someone else's caches.
- Hash-bound capture/report scripts stay unchanged and may intentionally target
  docs. Stage explicit runs in an isolated disposable checkout, inspect output,
  then promote only necessary evidence **and its genuine binding records**.
  Do not bulk-copy a whole capture campaign or change a generator hash to hide it.
- A reviewed retention exception edits the appropriate group (or adds a newly
  monitored root), supplies nonblank purpose/provenance, lists each exact relative
  PNG path and measured byte cap, and explicitly adjusts the aggregate cap.
  Example entry: `"new-run/focal.png": 12345` with purpose explaining the retained
  comparison and provenance identifying its real run/receipt. Submit the cap delta
  and rationale for review; never automatically regenerate the baseline on checks.
- Historical bound evidence cannot be automatically retired, even if an unchanged
  duplicate survives. Retention promotion is **not** authoring/recapture or game
  acceptance authorization; existing approvals and freshness contracts still apply.

## Validation and final accounting

Pre-deletion estimate: gross removal 1,135,052 bytes;
retention JSON 280,698 bytes.
At pre-deletion preparation, added/report/test/planning bytes total 360,163;
estimated net reduction is 774,889 bytes (0.739 MiB, 0.0411% of baseline),
before final navigation, validation notes and this estimate's own prose.
Final bytes and net reduction are measured below after checks.
Guardrails reduce the gross saving; no minimum saving was promised.
Validation results:

- `python3 -m unittest tools.asset_pack.test_vivid_review tools.asset_pack.test_ai_textures tools.ui.test_worldtree_qualification tools.asset_catalog.test_ui_assets`:
  **30 tests passed**, immediately after pruning.
- `python3 -m tools.evidence_retention`: passed. The focused retention fixtures
  passed, and `mise run check` passed Ruff, Python/JS syntax, worker guards,
  **159 tests** and two inline JavaScript programs.
- `mise run catalog-build`: **133 assets built** using existing sources/exports,
  without Blender, Godot or capture. Only ignored package/index/static/cache
  output was generated. No source-style/Blender fixture runs were necessary for
  this documentation-only PNG pruning; those would not replace visual acceptance.
- Compared the live index/payload to the pre-pruning baseline: **133 catalog IDs,
  118 model records, every selected native preview hash and 175 runtime payload
  members** unchanged. All **6,643** surviving base paths outside README/AGENTS
  navigation are byte-identical; those two navigation edits are the only changed
  base-tracked text files.
  Protected source/export/reference, generator and immutable receipt hashes remain
  unchanged. Actual deleted paths equal the 24 manifest entries exactly.
- Served the actual static output at `/` and `/odot-game-assets/` and fetched
  **388 image URLs**, comparing fetched bytes to repository inputs. Existing UI
  tests additionally exercise published resource/API/package URLs at both mounts.
  No existing review page, image link or native selection changed, so there is
  no changed visual review surface requiring a browser recapture. No screenshots
  were created. All four new policy/navigation local links and their anchors resolve.

The initial protected-file error on AGENTS.md was resolved by the single native
patch retry requested in retained answer `agents-retention-navigation-permission`.
The already-planned navigation-only edit succeeded under current enforcement;
no shell bypass, permission change or scope expansion was used.

Final accounting, including this report and the staged planning package:
tracked payload **1884638515 bytes**; additions/text growth **364970 bytes**;
net checkout reduction **770082 bytes** (**0.734407 MiB**, **0.040844%** of
the 1,885,408,597-byte base). Method: union base/index and nonignored new paths,
omit exactly the manifest deletions, sum current per-path bytes; subtract from
base. This is 24 removed PNGs, 1,692 retained candidate PNGs and 4,510 retained
monitored PNGs, across 6,656 final tracked/intended-to-track paths. Gross removal
is **1,135,052 bytes**; subtracting all additions/text growth gives the net above.
Pending tracked deletions and all 11 new files are included, regardless of staging.
No protected authored/export/reference bytes, immutable receipt, bound generator
or out-of-bound removal changed. Git history and ignored caches remain separate
from this checkout calculation; no history rewrite was performed.

Rollback is an ordinary corrective revision restoring only the manifest paths
from their recorded base and this cleanup's policy/navigation edits. No reset,
history rewrite, removal of unrelated work or archive mutation is necessary.
