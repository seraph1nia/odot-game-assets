# Saved-source serialization diagnosis (resolved)

The strict pilot guard failed on the mushroom source, then on gold mine. Broad
authoring stopped. MAIN authorized bounded diagnosis, not a preservation waiver.
Original bytes remain in `.cache/vivid-palette/before/`; every partial changed
source and the initial receipt/script were copied byte-for-byte into
`.cache/vivid-palette/diagnosis/partial-output/`. `partial-hashes.json` binds that
archive. Nothing in that archive or either original backup was overwritten.

## Counterfactuals under the same installed Blender 5.2.2

`differences.json` contains exact expected/observed fields for both an untouched
baseline load/save/reload and the earlier color-modified save. Scratch files and
full snapshots are local under `.cache/vivid-palette/diagnosis/`.

- **Gold mine:** untouched serialization alone removes exactly two zero-user,
  non-fake-user, unlinked prototype objects: `Woodland shared curved ivy leaf`
  and `Woodland shared moss cushion`. Their collection memberships were empty;
  live growth instances still used their shared mesh data. Both missing object
  fingerprint fields are identical in the palette-modified failure. No live
  vertex/UV/root/instance/rig/animation change caused this failure.
- **Mushrooms:** untouched serialization alone removes 24 zero-user material
  variants (including `forest_leaf.001`, `crystal_blue.001`, `stone.001`), along
  with orphan images. Their exact names, user/fake-user state and image channel
  fingerprints are in the difference record. Palette-modified differences also
  include intended replacement color maps. This is not evidence that unused
  authored material variants are disposable.
- Existing authoring scripts call ordinary `save_as_mainfile` without retaining
  orphan data. Blender's save-time lifetime policy, not color recovery, explains
  both observed losses. This is disconfirming evidence against attributing them
  to geometry authoring or allowing a tolerance in the shape guard.

The first attempted guard correction to inspect only used-material data channels
was **insufficient**. It hid unused authored material loss and has been reversed:
current verification again includes every material's Non-Color map pixels and
every object, including unlinked prototypes. Color authoring remains scoped to
materials owned by existing object slots, not arbitrary unused alternatives.
Unused material variants are preserved unchanged, not silently recolored/deleted.

## Smallest effective correction

Give otherwise-zero-user authored IDs Blender fake users before serialization,
and again after replacing color images. This changes persistence only: no scene
collection, visible hierarchy, mesh pointer, coordinate, socket or export selector
is changed. `protected-roundtrip.json` proves that both untouched counterfactuals
now retain all original object/mesh/material/image names, exact all-object
structure fingerprints and all-material Non-Color channel fingerprints.

The same protected path then passed actual color-modified gold-mine and mushroom
round trips. Sources are now authored from hash-gated preserved landed bytes into
scratch, reopened and strictly checked before atomic replacement of the live
source. The one-time repair option accepts only recorded exact partial outputs;
it does not discard the partial archive or permit unrecorded manual edits. All
67 owners subsequently passed the restored strict guard. `authored.json` records
which orphan IDs were protected, structural/data-channel fingerprints and current
source hashes. Focused Blender fixtures reproduce unlinked prototype/shared-mesh
and unused-material-map retention; exported resource counts independently compare
live geometry. No protection or acceptance check is waived.
