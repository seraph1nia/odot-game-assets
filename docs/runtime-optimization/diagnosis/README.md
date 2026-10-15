# Independent fidelity diagnosis — no blanket waiver

The failed academy pilot, input bytes and comparisons were preserved in the
worktree's `.cache/runtime-optimization/diagnosis/` before investigation. The
tracked JSON here records exact affected triangle identities, indices, local and
transformed positions/areas, counterfactual counts, normal measurements and the
source SHA. Failed log tails are retained alongside it. No authoring source was
saved, edited or rebuilt.

## 62 exact zero-area faces, five materials

The discrepancy is **not** a near-zero-area threshold and not missing visible
geometry. Every affected triangle has exactly repeated transformed positions and
area exactly `0`, in both the original landed and optimized binary buffers:

| Material | Source objects | Serialized triangles | Exact zero area | Failed optimized Blender reimport |
| --- | --- | ---: | ---: | ---: |
| `purple_light` | `Academy purple crystal` | 20 | 10 | 10 |
| `magic` | `Academy purple crystal` | 12 | 10 | 2 |
| `window` | `Candle flame` | 185 | 14 | 171 |
| `wood_edge` | `Banner hanging rod` | 3,132 | 24 | 3,108 |
| `wall` | `Front limestone block.012` | 3,892 | 4 | 3,888 |

See [every affected triangle](triangle-diagnosis.json) and the compact
[per-material/stage counts](summary.json). Material names that disappear elsewhere
in that diagnostic reflect **exactly equivalent material deduplication**, not
missing surfaces: the one-to-one comparison uses full material contracts rather
than names or averages.

The independent reader decoded real glTF index/attribute buffers, applied the
node transforms, and measured these areas without Blender reimport or the
optimizer's transform implementation. Findings:

- Detailed source, landed GLB, an **unmodified load/export** counterfactual and its
  Blender reimport each contain 248,974 triangles, including those 62 faces.
- The deliberate runtime moss/bevel profile contains 160,886 triangles, still
  including all 62 exact-zero faces. Its **unbatched export/reimport** retains all
  62. This isolates approved simplification from the discrepancy.
- The failed optimized GLB also serializes 160,886 triangles and all 62 exact-zero
  faces. Its full-attribute weld changed distinct coincident corner indices into
  repeated indices; Blender's importer discarded those 62 repeated-index faces.
- [One-to-one serialized comparisons](serialized-comparisons.json) verify every
  transformed triangle and its normals/UVs, **including every degenerate and every
  duplicate face**, between unbatched and failed/corrected optimized buffers.
  They also compare landed GLB to the unmodified export counterfactual.

**Exporter correction:** preserve the original distinct coincident corner splits
when welding would create a new repeated-index triangle. Do not delete faces,
threshold areas, or silently deduplicate legitimate coplanar faces. The final
GLBs retain the source multiplicity, even in Blender reimport. This small
compatibility correction costs a few additional vertex records, not mesh nodes.

## Normals: measure the serialized contract, not an importer artifact

A second independent [normal counterfactual](normal-counterfactual.json) compares
nonzero-area source corners to actual serialized floats and imported corners:

- Source → landed buffer max component error: **0.000141174**.
- Runtime-profile source → unbatched buffer: **0.000141174**.
- Source → **unmodified landed Blender reimport**: **0.011347869**.
- Runtime-profile unbatched reimport and optimized reimport have that same maximum
  perturbation at the same real corner. Positions, UVs and material triangle
  multiplicities agree. This predates optimization and comes from Blender's
  imported corner-normal representation; it is not a changed GLB normal.

The checker does **not** increase its GLB-normal tolerance to 0.01135. Blender
reimport supplies geometry, UV, material/multiplicity and pose coverage; its normal
differences are diagnostics, not a replacement for actual-buffer normal assertions.

The final checker includes **every** source/serialized triangle corner, including
zero-area faces. Areas are diagnostics, never acceptance filters: even exact-zero
classification can change under float transform arithmetic (the separate
[Archery counterfactual](archery-counterfactual.json) records that pre-existing
conversion effect). Full material triangle multiplicities and all serialized
attributes remain checked without filtering. Source zero normals use the pinned
exporter's documented local +Z fallback, not an invented geometric normal. Real
tiny nonzero triangles and legitimate coincident faces are explicit fixtures.

## Local normal rounding before nonuniform transforms

The Archery rollout initially compared an authored world normal directly against
a serialized world normal and failed at **0.0002067089** component difference,
**0.0122943°** angular difference, position error **1.33e-7m** and exact UVs.
[The exact corner/candidates](archery-normal-point.json) are retained. Do not
increase 0.0002 to fit that observation.

Independent diagnosis found the actual causal operation in the installed pinned
Blender glTF exporter: local `float32` corner normals are rounded to **four decimal
places**, normalized (zero becomes local +Z), and then axis-converted. The normal
accessor itself remains **FLOAT / 5126**, not 8/16-bit quantized data. Normal
transformation is inverse-transpose followed by normalization; mirrored transforms
reverse winding and tangent handedness without negating normal directions.

The corrected source reference models that known local conversion *before*
inverse-transpose. It does not modify sources, normal maps or exported normals,
and does not enlarge a world-space tolerance. Source-to-serialized and independent
prebatch-to-runtime normal comparisons are now fixed at **0.00002**, ten times
**tighter** than the original experimental check. UVs/positions/materials/animation
contracts retain their independent strict checks.

[Minimal actual-export counterfactuals](normal-quantization.json) use unrelated
synthetic geometric normals, rotations, nonuniform scale through condition 64 and
mirrored winding. The four-decimal prediction matches actual float accessors within
**1.20e-7**; the unconverted prediction differs by as much as **0.0013876**
(**0.0898843°**). The test changes a real, still-unit serialized normal by 0.001
and requires rejection under the **same transforms**, even though that change can
be inside a conservative rounding-error envelope. This demonstrates the envelope
is not an error allowance. A condition-1,000,000 transform is rejected.

The independent analytical bound is derived from the quantizer, not the failing
sample. For a unit local normal `u`, four-decimal rounding plus conservative float32
roundoff gives `||delta||₂ <= sqrt(3) * (0.5e-4 + 2^-22) = epsilon`. For invertible
normal transform `N`, `rho = condition(N) * epsilon` bounds relative transformed
error. Normalizing gives chord error at most `2*rho/(1-rho)` and angular error at
most `2*asin(chord/2)`. Local normalization cancels algebraically when the final
world normal is normalized. The helper checks measured conversion deltas against
this bound, but compares predicted versus actual serialized attributes using the
fixed 0.00002 threshold, **not** the envelope.

Supported transform conditioning is explicitly capped at **64**, a bounded FP32
class (`gamma_3 * 64 ~= 1.15e-5`, below the fixed comparison budget); it never
creates arbitrarily large allowances. The full [actual-source inventory](normal-conditions.json)
has maximum condition **32.7766**, with most sources near 1. Current per-asset
measured component/angular deltas are in `../validation.json`. The Archery runtime
profile's maximum original-to-rounded world delta is about **0.0002153 / 0.012846°**;
these are small, existing exporter-conversion effects, not a new runtime normal
regression or a reason to assert pixel-perfect authored normals.

All25 actual profile measurements reach at most **0.00110417** original-to-rounded
world-normal component delta and **0.0674135°** angular delta (conservative
conditioning bounds are reported separately, never used as acceptance tolerances).
After correctly modeling conversion, source-to-actual-runtime normal error is at
most **2.921e-6**, positions/pose point clouds **1.221e-6m** and UVs **6.557e-7**.
The larger original-to-rounded figures are small pre-existing exporter rounding
under nonuniform scale, not a batching regression. [Preserved input hashes](preservation.json)
bind the task-local failed/unmodified binaries and failure logs; published text
log tails remain alongside these receipts.

[Unmodified landed/source/export checks](normal-baseline-exports.json) establish
that the same conversion is already present without optimization in both Archery
and academy. All25 current selections retain independent one-to-one actual
prebatch/runtime position, normal, UV, material and clip checks. Matched small-scale
renders show retained appearance; no rendered game-performance or artist approval
is claimed.

## Negative controls and repeatability

`test_runtime_blender.py` executes controls that remove a real visible triangle,
change its material, UV, normal or position, and require rejection; coincident
legitimate faces retain their multiplicity. A truly tiny nonzero triangle remains
in the audit. `test_runtime_glb.py` proves the coincident-corner compatibility fix
and failure-closed unsupported deformation behavior. Existing encoded-image
negative controls remain strict and unchanged.

The bounded pilot diagnosis can be repeated with:

```sh
python3 -m tools.asset_pack.worker tools/asset_pack/diagnose_runtime_blender.py --label runtime-independent-diagnosis
python3 -m tools.asset_pack.worker tools/asset_pack/test_runtime_blender.py --label runtime-fixtures
```

The diagnosis expects the preserved failed pilot at its task-local path; it does
not overwrite production exports or source files. The normal and serialized
counterfactual JSON bind that pilot investigation; current **all25** acceptance is
owned by `../validation.json`, exact current GLB hashes and the official verifier.
No normal-map image float hashing, color-space waiver or map-binding fallback was
introduced.
