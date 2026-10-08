# Effective material export correction

**Accepted-source fidelity, not a global palette or geometry migration.** Seven
executed selected-export fixtures and the 24-test combined Blender style suite
pass. Existing selected round-trip, bounds, rig, style and packed-channel checks
pass for the six corrected IDs. All original source/library bytes are preserved
through this export correction; baseline and superseded GLBs remain separate.

## Actual earliest loss and supported-option decision

[Executed boundary evidence](material-loss-boundary.json): with modifiers and
`export_apply=True`, installed Blender 5.2.2's glTF `nodes.__gather_mesh` takes
materials from evaluated `to_mesh()`. Both the original **and evaluated object**
retain effective blue OBJECT slots, but evaluated mesh DATA still has red.
The primitive serializes red. The authoritative catalog planner/selector is correct.

Turning off modifier application is not compatible: the actual fixture preserves
blue but drops the authored Bevel result from 216 to 24 triangles. The existing
route therefore retains applied modifiers, skins/actions/selection/axis options.
Its private context manager normalizes **only modified meshes with divergent
effective slots**, including reachable collection-instance prototypes, onto
transient mesh variants keyed by original mesh and exact effective material tuple.
Equal tuples reuse a variant, different tuples remain distinct. Unmodified meshes
keep the supported exporter's ordinary object-slot handling. Finally restores
original DATA, slot links/order/materials and deletes transient variants, including
serializer failure; the existing atomic-output staging remains unchanged.

No shared source mesh/material, image, UV, skeleton, weight, curve, parent,
origin or canonical selector was rewritten. No new exporter, renderer or schema.

## Genuine regression and exact closure

[Before](checks/quality-material-before-confirmed.log): the actual selected exporter
finishes and emits a red primitive for the fixture's blue override; the assertion
fails on material semantics, not setup. [After](checks/quality-material-after.log):
the same fixture and six additional cases pass: multiple DATA/OBJECT/null slots,
equal/different tuple sharing, no-modifier handling, red-over-blue collar,
collection-instance prototype and injected serializer failure/source/target cleanup.
These tests are part of `mise run style-tests`.

[105-ID read-only closure](material-closure.json) traces effective/evaluated/DATA
slots, used polygon indices, semantic shader graphs, actual GLB nodes, parents,
shared-prototype tags and collection instances. No unmatched override nodes or
production collection instances remain. The exact affected closure is:

- `buildings/weaver`: four blue canopy stripes were red.
- `characters/evil_berserker_unit`: bare skin/gloves and steel tunic panels were
  incorrectly common blue/leather.
- `characters/evil_mage_unit`: dark aperture/gloves and faction-purple cloth used
  common human skin/face-purple materials.
- `characters/evil_melee_unit`: steel cloth/armor, black neck and shield steel/edge
  used common blue/skin/gold.
- `characters/evil_ranged_unit`: steel body/black neck and source red collar used
  common blue/skin/old purple.
- `props/evil_shield`: matching steel field and dark edge instead of blue/gold.

Only these six were re-exported; the exporter fingerprint change did **not** start
an all-105 export/render campaign. [Selected after audit](material-closure-after.json)
finds every effective override's exported material semantics correct.

## Exact fields versus semantic UV and scene-label differences

[Old→new mapping](material-only-mapping.json) binds six superseded/current GLBs to
unchanged source hashes. Geometry positions/indices/normals, morph/skin/joint/weight
and animation bytes, node/parent transforms and extras remain exact.
Four unit motion observations can therefore carry forward as **geometry continuity**,
not as movies of the new binary/material appearance.

Weaver is **not** claimed bit-exact UV or strict material-only binary diff: 131
TEXCOORD_0 accessor byte hashes differ, all coordinates are finite and every actual
numeric delta is at most 1.1920928955078125e-7. Layout/type/count/order/correspondence
and the authored source UVs remain unchanged. Firstmate 008 accepts this disclosed
float32-scale serialization under the existing semantic contract; no canonical
epsilon, ULP-count inference, validator relaxation or source-UV rewrite was made.

[UV context](weaver-uv-context.json) records embedded PNG sizes and sampler state:
512 px painted maps, LINEAR magnification (9729), trilinear minification (9987),
omitted wrap fields meaning default REPEAT, and no KHR texture transform. Existing
`verify_painted_blender.py` requires an active source UV layer, finite coordinates,
embedded PNG channels and exported TEXCOORD_0/NORMAL—not bit-exact UV reserialization.
Matched portable texture review remains the visual counterpart to those checks.

Evil shield has one separately declared **scene display label** change from legacy
`evil_melee_unit` to `evil_shield`, exactly the unchanged authoritative saved source
scene name. Root/node names, parents, extras, pivots and geometry are exact. Do not
claim the whole scene document is byte-identical or erase this historical mismatch.

## Evidence ownership

Old 23 portable profiles, 60 motion bindings, 23 resource bindings and superseded
wrong-palette current crops/videos remain in
[history/before-material-fix](history/before-material-fix/README.md); translations
bind original public paths to preserved copies. Original 473 baseline hashes,
18 saved-source profiles and old partial-render failure history remain unchanged.
Current source/GLB hashes and cost deltas are in [resources](resources.json).
Portable bloom remains unavailable in the existing viewer: emission/body-state
comparisons are not halo-on/off or a game integration claim.
