# Compact native skill-tree extension: acceptance and limits

This extends Ledger's portable native library, not the main game. The existing
`research-node` alias, all nine previous components, Theme, menu seal and model
catalog remain intact. No renderer, forest, mesh or source-model changes.

## Behavior checked

- One visible middle/Foundation, cost **exactly 1 skill point**. All outward nodes
  require it first. Root purchase exposes **three** choices: Vanguard/Guard,
  Wayfinder/Aim and Arcanist/Spark.
- Three meaningful illustrative steps per branch (10 nodes total), each requiring
  its preceding parent. All three complete chains are exercised, not just the
  first branch. Definitions, costs, initial ownership and points are caller data.
- Native pointer root purchase and keyboard parent purchase change points once,
  owned/available/locked/unfunded labels, selected quote and connector states.
  Already-owned, missing-parent, unknown and insufficient-point requests do not
  spend; signals carry exact node ids/remaining points. Invalid root cost,
  cross-branch parent and incomplete initial ownership leave the snapshot intact.
- Native Tab/Enter inspection/activation, focus-following two-axis scroll, wheel
  and reverse wheel tested at **420×700**, with clipped graph nodes reachable and
  selected description/cost/reason outside the graph. Existing modal focus/input
  and original four-size Ledger regression stay in the same harness.

## Branch-index review follow-up

Heading identity now uses branch array indices rather than display titles. The
native regression exercises all three duplicate-title pairings and all-equal
Foundation titles, checking three positioned headings and every selected quote.
The earlier evidence below predates this follow-up and does not certify its
changed inputs. The outer pipeline must refresh full native evidence, inspect
current tree images, refresh payload/catalog captures and load the final generated
ZIP before updating current provenance, count and budget bindings. Historical
and failed evidence, including browser receipts, must remain unchanged.

## Fresh evidence before the branch-index follow-up

[`production/mini-skill-tree-final/results.json`](production/mini-skill-tree-final/results.json):
**706 checks, zero failures, 85 native viewport captures**. This is the existing
637-check campaign plus 69 skill-tree checks/captures, not a browser recreation.
The focused `--only skill-tree` run (`mini-skill-tree-focused-final`) passed 69/0
before the full campaign, without increasing the supported timeout or dimensions.
Godot 4.7.2 .NET / Compatibility / owned Xvfb / Mesa llvmpipe / Dummy audio. No
personal desktop, application Window screenshot or browser session accessed.

[`skill-tree-validation.json`](skill-tree-validation.json) binds the seven actual
inspected images (six campaign states plus the current catalog tree preview),
source hashes in the result, and validation/capture/package tools. The catalog
preview has its own complete resource/host/generator/image/dimension binding in
[`catalog/previews.json`](catalog/previews.json), currently
`catalog/mini-skill-tree-final/`. The final implementation commit containing these
bindings qualifies the evidence; any later changed input needs refreshed checks,
not these earlier receipts. Head is reported at committed delivery, rather than a
self-referential commit hash inside its own content.

Fresh `audit_payload.py` loads **35 UI-only files / ten scenes**, Theme and seal
in a private independent project. `check_catalog_package.py` separately extracts
the **actual generated ZIP**, imports and instantiates all ten scenes and exercises
skill root/prerequisite/duplicate/funding guards with no prototypes or fixture
imports. [`catalog/package-check.json`](catalog/package-check.json) binds exact
ZIP/member hashes and engine/logs. Static catalog build includes `ui/skill-tree`
in the existing component category/shared package; unchanged native aliases and
all model IDs pass the existing generator/link/package tests. No new browser UI
framework or fake interactive screenshot is added.

Reproduction uses the commands in [catalog/README.md](catalog/README.md) and
[README.md](README.md#reproduce-checks-in-assets-only), with unique labels and the
already installed engine/SDK. Full process logs are retained privately in `.cache/`.

## Concrete visual inspection

Opened the current authored `native-5/action-quote.png` and `native-5/theme.png`
before designing. Final six campaign images and `mini-skill-tree-final/skill-tree.png`
were opened at actual native resolution. The full layout has cream planes,
ink copy, restrained amber availability/selection and teal focus/owned links.
Three named spokes visibly start from the center; secondary steps remain legible,
with descriptions and costs in the existing quoted-action owner. No copied PoE
art, bloom or new textures. Owned/available are also explicit words, not color-only.
The narrow image deliberately shows a scrolled slice, not an alleged full graph;
its focused Beacon and full prerequisite description are readable.

Retained iteration history:

1. `production/mini-skill-tree-1/`: 340/0 production subset, six captures. Mechanical
   success but **visual failure**: unthemed Panel/host had dark backgrounds and
   low-contrast copy. Fixed by using the existing InsetPanel style and teal host.
2. `production/mini-skill-tree-2/`: 677/0 full suite, 85 captures. Opened and found
   the long `Insufficient` node label clipped. Shortened the node state to
   `Unfunded`, retaining full insufficient-point text in the quote; added complete
   three-chain/signal/root-funding/wheel checks. Earlier source-bound captures and
   first catalog run remain intermediate evidence, not final certification.
3. `tools/ui/test_plan.py` first run rejected the changed fixture source against
   the old 637-check accepted package. Kept its historical image/preservation
   contract and added fresh current-source binding to this extension instead of
   rebinding the historical receipt or claiming old screenshots prove new code.
4. The fast catalog test then correctly rejected the old browser receipt's ZIP
   hash against the enlarged payload. Reconstructed the **exact original ZIP**
   with the existing deterministic packager and baseline Git resource/API bytes;
   its hash matches every retained browser acceptance result. Stored it only in
   `catalog/browser/ledger-ui-historical.zip`, excluded from publication. The
   browser test still binds its original frontend, frames and exact historical
   ZIP; the new package has fresh native loading/member/hash checks. No stale
   browser receipt is relabeled as testing the new package and no browser/tool
   download or replacement was attempted.

5. `mini-skill-tree-root-before` and `mini-skill-tree-4` retain the initial narrow
   root-offscreen failure and first unsuccessful deferred-control correction.
   Earlier 690/0 images **do not certify these changed inputs**. Controlled native
   geometry diagnosis (`.cache/ui/skill-root-diagnosis/rebuild.log`) showed the
   deferred ensure ran while the old width/page was 1052/960; after the narrow
   sort it was 372/366, with horizontal value still zero. Rapid snapshots also
   left queued arguments pointing at retired, unparented buttons. A fresh narrow
   open passed (falsifying "all narrow layouts fail"); only same-frame resize/
   rebuild exposed the ordering. Moving ensure to native `sort_children` and
   looking up only the current live descendant made horizontal value 176 at the
   actual narrow sort and the root visible, with no stale ancestry errors
   (`rebuild-fixed.log`). No timer, repeated deferred scroll, input framework or
   unrelated widget change was added. Remove-before-sort, reattachment and rapid
   open/close/reopen are covered by the final focused regression.
6. Focused `mini-skill-tree-layout-fixed`, `mini-skill-tree-narrow-input-diagnosis`
   and `mini-skill-tree-target-trace` preserve the distinct pointer failure. The
   root/quote were enabled, live and inside the clip, but that did **not** prove
   click delivery. Actual GUI/button traces found unreleased synthetic wheel
   presses left mouse mask **24** and GUI capture held: hovered root changed,
   but neither root nor purchase received left-button down/up. Allocation itself
   passed normal pointer and reopened narrow keyboard paths. The sole controlled
   counterfactual was pairing the local test helper's wheel press with release;
   `mini-skill-tree-wheel-counterfactual` passed 67/0 with mask **0**, real root and
   purchase GUI down/up/pressed, and points **6 → 5**. No component routing change,
   direct purchase substitution or extra delay was needed. Final regression also
   asserts the exact two native pointer target sequences and released mask, and
   retains all budget/prerequisite/duplicate/keyboard/lifecycle checks (69/0).

## Limits

The component performs local guarded allocation, not server authority or
persistence; illustrative effects/costs are not game balance. No respec, new
currencies, cross-branch dependencies or economy. The fixed small topology has
three 1–3-step paths and short graph titles; arbitrary graphs, localization/RTL,
controller/mobile/native GPU and target-game integration are untested. The
frontend is unchanged and existing browser evidence remains historical: **no fresh
live-browser acceptance** is claimed for changed ZIP/native inputs. Native/static
checks do not imply deployment, release or merge permission.
