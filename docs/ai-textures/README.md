# AI-generated texture POC — actual assets, not a concept mockup

**Current bounded ground correction:** open [`seams/review.html`](seams/review.html)
for **original → initially delivered → corrected** GLBs, all five repeated-family
and mixed grids, and connected path/river comparisons. [Its report](seams/README.md)
records the retained actual-game regression, source-only correction, costs and
pending successor GPU acceptance. The five base-ground color maps supersede the
initial floor treatment described below; foundation, overlays and Archery remain
unchanged. The correction does not treat the earlier game regression as accepted.

**Original/current pairs:** open [`review.html`](review.html) directly in a browser. It is an offline,
side-by-side gallery of the original and changed **GLBs**, with close-ups, 96px
representative views, shared-foundation detail, mixed floors, paths and connected
river scenes. No server, download, image model or game checkout is needed.
The existing catalog still loads the changed canonical exports normally:
`mise run catalog`, then select the same asset IDs. The gallery reuses the reference
library's dark olive/parchment colors and serif hierarchy rather than introducing
another catalog or review service.

**Status: partial assets-first milestone, not completion of the end-to-end POC.**
The [main-only game handoff](#main-only-game-handoff-and-rollback) owns the delivery
order and pending **`odot-ai-textures-game`** acceptance requirements. **The overall
request remains incomplete until that game work lands with acceptance evidence.**
CPU Blender renders do not prove game-camera improvement,
GPU timings or production art approval. No game checkout was modified or used as
a private import path.

## Scope and safety

Baseline: `133c7cdeb368cada408d1c95c9414e08488371a9`, also the inspected game's
existing authored-asset pin. [`baseline.json`](baseline.json) binds all fourteen
original `.blend` and `.glb` hashes/bytes. Baseline bytes are retained locally in
`.cache/ai-textures/before/{sources,exports}/`; recover them from that immutable
Git revision if the disposable cache is unavailable. Initial effective-slot,
mesh-user, image and UV audits are retained in `.cache/ai-textures/audit/`.
[`validation.json`](validation.json) includes independent original packed-image
proofs and source/serialized-GLB preservation results for every changed asset.

Both real Downloads archives were found (including a filename search rather than
assuming absence), bounded-inspected for traversal, symlink and expansion hazards,
then extracted only into `.cache/ai-textures/input/`. Original ZIP and member SHA-256
hashes are in [`inputs.json`](inputs.json). The archive instructions were read as
untrusted input, not authority to broaden the task. Their swatches, recipes and
README files are preserved under:

- `sources/environment/textures/ai_ground/input/` — 24 original maps, eight families.
- `sources/buildings/textures/ai_archery/input/` — 36 original map entries plus RGBA target. **The supplied `dirt_ground_normal.png` is an empty, invalid file** (SHA-256 `e3b0c442…b855`). It is preserved only for input provenance, never decoded, packed or exported; no replacement normal is fabricated.

Only explicit current-source material edits were made. No old builder was run,
no geometry generated, no source UV reprojected, no shared prototype changed, and
no unrelated source rewritten. Original source materials and packed maps remain
in the files, including unused authored variants. New color images have separate
content-derived names, ownership tags and category-local PNG companions in
`managed/`. All source images are packed; GLB dependencies are embedded.
These are user-supplied generated-art experiments; no CC0, third-party reference
license, production certification or new redistribution right is invented here.

## What changed

### Phases 1–2: floors and foundation (initial delivery, superseded for five bases)

The following two paragraphs describe the historical first painted delivery.
Current floors instead use the [bounded smaller-feature/luminance-preserving
edge recipe](seams/README.md#small-source-preserving-fix). Historical first-delivery
maps and PNGs are preserved; this text is not a claim that the dark outline passed.

The moss-only trial was exported, checked and visually inspected before expanding
to `hex_ground_{moss,grass,dirt,leaf_litter,pine_duff}` and `floor_foundation`.
The existing active Base Color image nodes now point at reproducibly prepared
color maps: 75% supplied linear color / 25% original painted color. The source
Principled defaults, material names, slot link modes, opacity/culling, metallic,
roughness, normal, emission and alpha behavior are unchanged.

A narrow `.18m` smoothstep transition to one shared olive/humus color is baked
at the hex perimeter. It uses the existing planar UVs and the shared `HEX`
footprint, not extra geometry, a shader trick or game-neighbor metadata. It
reduces cross-family high-contrast fragments at contacts but **does not make
whole tiles visually identical or remove all material boundaries**. The original
flat-top radius `2.55`, top `Z=0`, bottom `Z=-.36`, placement root and scale survive.
The foundation samples one shallow course from the supplied masonry atlas rather
than squeezing multiple square rows into the sidewall. All five sources share the
same prepared foundation; the underside retains that original material assignment.

### Phase 3: all eight ribbon overlays

`floor_path` and `floor_river` use supplied detail in their interiors. **Existing
transverse U / arc-length V UVs are byte-for-byte preserved**; no ordinary planar
mapping is substituted. The original symmetric paint is retained at connector
approaches and endcaps. River detail fades inside the original water region
(`U≈.09375–.90625`); authored banks/lips are retained to avoid stretched AI foliage
on turns. Channel width, profiles, positive overlay clearances, every connector,
root, topology and the independent moving shimmer remain unchanged.

`Roughness` and `Normal` are intentionally **retained originals on every asset**.
The supplied companions are approximations of already shaded illustrations, not
measured relief. In this POC, added color gives the useful visible benefit without
introducing shiny soil, stone-height water or double-modeled masonry/shingle relief.
The original shallow tangent-space Normal Map nodes remain connected. Supplied
companions are versioned for experimentation but are not misrepresented as used.
Base Color is sRGB; active Roughness/Normal maps remain Non-Color.

### Phase 4: actual portable comparisons and mixed placement

All five families, foundation and eight overlays have matched original/new views.
Every canonical ribbon additionally has a connected-neighbor scene; the mixed
six-cell scene includes all five floor families plus two connected path/water
chains. Identical cameras, frame 1, Area lights, world, AgX/Medium High Contrast,
CPU Cycles, 24 samples and four threads are recorded in each image's profile.
Full/close views are 400px square; neighbor scenes are 640×440. The 96px companions
are diagnostics, **not invented actual-game captures**. Revisions are labeled by
baseline commit and immutable GLB content hashes; every pair retains both full
asset/hash sets and the camera/light/color profile in [`renders.json`](renders.json).
The foundation detail is an explicitly recorded pixel crop of those same renders.

### Phase 5: Archery Range

The saved source was audited before editing: 4,957 selected mesh objects including
shared leaf/moss users, existing individual shingles, effective DATA/OBJECT material
slots, authored UVs, packed images and the `ambient` clip. Exact per-material
assignments, source input hashes and crop coordinates are in `validation.json`.
Recipe candidates were not treated as the actual inventory.

| Supplied family | Actual treatment |
| --- | --- |
| Warm wood | `wood`, `wood.003`, `wood_light`, `wood_light.001`: single-plank strip, grain along existing V/beam length. |
| Aged wood | Three `wood_dark` variants, retaining shade hierarchy; no repaint of growing vine bark. |
| Horizontal planks | `wood_edge`: crop one plank, transpose image so input U-grain follows source V; no UV changes. |
| Blue roof | Three existing blue shingle materials sample one tile interior, not multiple rows over each geometrically modeled shingle. |
| Pale plaster | `wall`: related restrained variation; this material also has some limestone users, so no unsupported slot split was invented. |
| Mossy stone | `wall_light`, `wall_light.001`, `stone_light`: single-stone crop avoids overlaying a second mortar grid on individual blocks. |
| Cobalt cloth | `blue` pennant/banner: woven color; original arrow emblem, cream work canopy, faction blue and gold borders retained. Its already-authored UVs are now exported for the first time and independently checked against the source. |
| Foliage/moss | Existing individual leaves/cushions borrow only subtle color-value variation; original root/tip colors and shared meshes survive. Not an ivy atlas pasted wholesale onto every leaf. |
| Draped blue cloth | Retained as input only: its baked folds do not correspond to the actual narrow banner; the cream canopy is a different authored role. |
| Patinated metal | Retained as input only: a trial was rejected for tiny metal details; original metallic scalars/colors preserve readable rivets, chain, hoops and arrows. |
| Grass/dirt ground | No such receiving material exists in the exported building selection. Presentation ground is excluded and was not silently added to the building. The terrain suite supplies actual game ground. |
| RGBA target | Audited but not projected: the target is separately modeled rings with unsuitable shared per-ring UVs, not a unified decal receiver. Preserving these readable rings avoids alpha halos, new geometry, UV edits or an incorrect bullseye repeated on each ring. |

No silhouette, root, overgrown detail, component reuse, action keys, NLA ownership,
ambient target or source physical rendering property changed. Building color blends
retain original role means and shade relationships. At small scale the benefit is
subtle; the plentiful authored growth still dominates the silhouette.

## Initial-delivery visual review — historical, provisional

The five floor judgments below predate the game-discovered regression. Current
correction judgments and three-revision evidence are in [seams/README.md](seams/README.md#image-inspection--acceptance-conclusions).
No historical praise waives actual-game acceptance.

Implementation-worker inspection of actual full/close sheets and mixed/neighbor
renders, against D03 palette, D04 surfaces, D05 contacts and D09 resource restraint:

| Surface | Judgment and limitations |
| --- | --- |
| Moss | More readable painted moss/rock/seed-leaf structure at tile size than the old sparse cushion stamps. The illustrated stones are broad color marks on a flat occupation plane, not new collision geometry. Soft and visibly upsampled at close range. |
| Grass | Clear grass strokes/flowers improve surface richness. Large daisies repeat if the same orientation is reused; repeated identical tiles are still recognizable. |
| Dirt | More convincing compacted earth/pebbles; warmer and busier than the baseline. Strong pebble highlights are part of the small supplied illustration, not actual relief. |
| Leaf litter | Distinct overlapping leaves read better than sparse old marks; the close view exposes low native swatch resolution. |
| Pine duff | Richer surface, but **needs refinement for pine-specific identity**: the supplied map derives from the same leaf-litter art, and needles/ferns are less dominant than before. Do not call the two families production-distinct. |
| Foundation | One shallow stone course is more coherent than the plain old sidewall. Corners still repeat because existing per-face UVs repeat; geometry/UV preservation takes precedence over a terrain rebuild. |
| Paths | Interior pebble/wear detail is visible on straights and both bends. Quiet connector/endcap areas are noticeably smoother than the interior, particularly close up; this is a retained seam compromise, not a seamless-texture claim. |
| River | Interior shallow-water color is richer, original banks remain readable, and all joins retain the same profile. Illustrated stones/highlights are static color; actual animated water appearance still needs the game's existing renderer and camera. |
| Archery Range | Longitudinal wood, woven blue cloth and stone variation improve close-view material readability without duplicating shingles or removing growth. Small-view change is modest. Endgrain remains limited by the preexisting face UVs; don't promise a new endgrain unwrap. |

The ground source swatches are only about **135–171 native pixels enlarged to 1024**;
resizing does not create 1K detail. The Archery inputs also include enlarged crops.
No assignment-only or automated-check-only visual success claim is made. This is
an implemented POC with retained defects, not final artist approval, nor evidence
of the most important final criterion: improvement in the actual game.

## Validation and observed costs

[`validation.json`](validation.json), [`ground-verification.json`](ground-verification.json)
and [`resources.json`](resources.json) bind the current sources/exports.
Report packaging requires the ground receipt to cover all thirteen ground IDs
exactly once and match every current source and GLB hash before writing outputs.
The superseded pre-final-save ground receipt remains available in Git at
`69d1e6eda5122c11a2e75665300da9f0fd6379e2:docs/ai-textures/ground-verification.json`;
its earlier run is historical, not evidence for the final saved source bytes.
Final-source verification is recorded separately in [`checks.json`](checks.json).

- All fourteen selected source-preserving exports and GLB round trips pass.
- All fourteen source-style and packed-image/UV/embedded-channel audits pass.
- Full-source second-application idempotence passed for all fourteen: no datablock
  growth or semantic changes. Content identity includes prepared values; foreign
  named images, stale external/packed bytes and unsaved image edits fail closed.
- Independent audit proves every original packed PNG unchanged, all source
  geometry/UVs/slots/hierarchy/actions/collection ownership/defaults/render state
  unchanged except declared color bindings, and all serialized GLB triangle
  corners/normals/UVs unchanged. Newly exported blue-cloth UVs match their source.
  Protected embedded data maps and exact animation targets/samples/loop extras match.
- The ground verifier exhausts source and imported-GLB rotated interfaces, matching
  neighbors, 48 real imported-root rotations and all 40 base/overlay stacks.
  Its previous image-name-based channel detection and pre-ambient omission of the
  separate two-channel shimmer were corrected; no geometry/UV/seam thresholds relaxed.
- Fast tests preserve historical art/runtime receipts as immutable predecessors
  and require independently audited, hash-bound current successors. They reject
  changed source/export bytes and broken predecessor identities, and honor shared
  component source-owner mappings. Old Godot costs/renders are not relabeled current.

Exact commands/logs/results are in [`checks.json`](checks.json). The optional
browser-bridge structural inspection was **unexecuted**: two attempts returned
`BRIDGE_NOT_READY` because the attached CDP target was gone. No browser pass is
claimed and no browser infrastructure was changed. Static HTML/local-link/image,
PNG metadata/hash, comparison-profile freshness and handoff consistency are instead
executably checked with the existing fast-test infrastructure. Actual rendered
asset images were inspected directly; actual-game acceptance remains separate. GLB triangle,
material and mesh counts are unchanged, including the Archery Range's optimized
45 meshes / 42 materials / 122,408 primitive triangles. New source PNGs coexist
with preserved originals, increasing editable `.blend` storage intentionally.
The initial delivery increased fourteen GLBs from **27,115,592 to 30,266,832**
(+3,151,240, about 3.01 MiB); this is historical, not the corrected total.
Current source/export costs and exact changes from that delivered predecessor
are in [`seams/comparisons.json`](seams/comparisons.json) and [`resources.json`](resources.json). Summed embedded RGBA8 estimates increase from
**149,946,368 to 152,043,520 bytes** (+2 MiB), entirely in Archery Range: its
embedded images increase from 36 to 38. Previously scalar blue cloth now has a
color map, and prepared material variations no longer share every old color image.
Existing active map resolutions are otherwise retained. The 61 supplied map/decal
entries occupy 29,288,460 input bytes and about 204 MiB decoded RGBA8 (excluding
the empty normal). Input-map decoded memory is **not** runtime allocation: unused
companions are not embedded in GLBs.

Resource JSON lists exact before/after bytes, embedded images, input-map dimensions,
source sizes and decoded RGBA8 estimates. Estimates exclude mipmaps, driver formats,
compression, allocation overhead and cross-asset deduplication. No draw-call/FPS or
GPU-memory measurement is invented; unchanged geometry/material counts do not prove
identical GPU time. Final game-worker measurements and actual RX6800 identity belong
to the later owned graphical game acceptance, not these CPU image renders.

## Reproduce without rebuilding geometry

Use the installed pinned **Blender 5.2.2 LTS** and existing workers. No installs,
GUI scene mutations, broad rebuilds, or legacy `build_pack.py` / `ground_tiles.py`
are needed. Run in an isolated copy, never over someone else's uncommitted sources.

```sh
# Optional: re-inspect original Downloads archives into a fresh private destination.
python3 -m tools.asset_pack.ai_texture_inputs ~/Downloads/odot_ground_tiles_poc.zip .cache/ai-textures/reextract-ground
python3 -m tools.asset_pack.ai_texture_inputs ~/Downloads/odot_archery_range_texture_poc.zip .cache/ai-textures/reextract-archery

# In an isolated POC checkout/copy (with these tools and input maps), preserve
# all14 baseline source/GLB bytes in .cache/ai-textures/before/{sources,exports}/
# using baseline.json hashes first. Restore those baseline sources into sources/.
# Then audit BEFORE authoring. Never replace an existing baseline audit with new bytes.
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_blender.py --label ai-audit audit
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_blender.py --label ai-apply apply
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_blender.py --label ai-idempotence idempotence
IDS="$(python3 -c 'from tools.asset_pack.hex_ground import IDS; print(" ".join(IDS), "buildings/archery_range")')"
python3 -m tools.asset_pack.check $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/verify_style_blender.py --label ai-style $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/verify_painted_blender.py --label ai-painted $IDS
python3 -m tools.asset_pack.worker tools/asset_pack/verify_ai_textures_blender.py --label ai-preservation
python3 -m tools.asset_pack.worker tools/asset_pack/verify_ground_blender.py --label ai-ground --output docs/ai-textures/ground-verification.json
python3 -m tools.asset_pack.worker tools/asset_pack/test_ai_textures_blender.py --label ai-fixtures
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_review.py --label ai-before before $IDS mixed neighbors
python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_review.py --label ai-after after $IDS mixed neighbors
python3 -m tools.asset_pack.ai_texture_report
mise run check
```

If starting from the delivered POC rather than baseline, restore the baseline bytes
into a **separate private comparison cache**, restore baseline audit JSON from the
retained local cache (or produce audits by opening baseline copies), and retain
current sources. `audit-baseline` reads the preserved baseline source copies directly:
`python3 -m tools.asset_pack.worker tools/asset_pack/ai_texture_blender.py --label ai-audit audit-baseline`.
Both audit routes require the recorded original source hashes and refuse to overwrite
the original audit with already changed source bytes.
Before opening or mutating the source, `apply` requires its exact SHA-256 to match
the audited baseline or last-applied receipt. The local `.cache/ai-textures/applied/`
receipt takes precedence; without it, the committed `validation.json` source-after
hash is the delivered receipt. Unrecognized source changes, including later manual
color bindings, original-image metadata and packed-image edits, are refused without
saving. Preserve those edits separately rather than relabeling them as applied.
The original geometry/physical signature is also required, and the original color
image is retained for deterministic reapplication. Recognized sources can accept
updated input textures; `idempotence` validates an unchanged second apply.
Original and previously delivered managed maps remain source-only predecessors.
The five rejected unpublished edge trials were separately archived with exact
packed-source copies before their authorized exclusion from delivery; see the
[cleanup receipt](seams/review-r1-cleanup.json). Reapplication retains predecessors
and never performs a broad orphan purge.
The independent verifier checks current owned bindings separately from these
unreferenced predecessors: explicit owner/content-key/input provenance, canonical
managed companion paths, sRGB state and exact packed/companion bytes are required.
Unexplained additions and predecessors with real users are rejected; every baseline
image must still exist unchanged. Retained images are reported separately in
`source_preservation.retained_owned_image_proofs` and included in `new_image_count`.
Every application saves the isolated source and can change its file hash; rerun
selected export, audit and comparisons afterwards. Do not relabel stale renders.
The report command uses installed ImageMagick only to label/assemble real renders;
it does not generate asset geometry or substitute an export pipeline.

## Main-only game handoff and rollback

[`handoff.json`](handoff.json) lists every changed GLB, exact bytes/SHA-256, embedded
image hashes/dimensions, source hash and clip names, with a content-set identity.
It deliberately does not contain a guessed future merge SHA. **After the asset PR
merges**, resolve the immutable commit on assets `main` that contains this exact
handoff, verify it is an ancestor of `origin/main`, and pin that full revision in
the game. Recheck each file and every extracted embedded-image dependency with the
existing game import tools; update all revision/hash/derived metadata together.
Never copy private-branch models into the game while retaining stale pin metadata.

The already-filed dependent game ship **`odot-ai-textures-game`** owns the pending
pin/manifest update and actual-GPU acceptance in settlement, forest, path and
connected river views, including tile connections, water motion, placement and
loading. It must also test Archery Range in the settlement if the material stage
is visually acceptable. This assets-first PR is only a partial milestone: the
overall end-to-end request remains incomplete until that game work lands with
acceptance evidence. Existing old recessed river versus shallow surface-stream
incompatibility remains; this POC adds no new transition and changes no
renderer/gameplay contract. No release/deployment is requested.

For rollback, revert this asset change as one coherent Git change (sources, prepared
maps, exports, manifest/validation and successor receipts), retaining any later user
edits rather than force-resetting. The game worker separately restores its prior
asset pin `133c7cdeb368cada408d1c95c9414e08488371a9` and its matching manifest/dependencies.
The baseline cache and committed before PNGs preserve original review evidence.
No cleanup command should delete original source images or overwrite a manual edit.
