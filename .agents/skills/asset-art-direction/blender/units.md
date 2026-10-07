# Unit proportions, sockets, deformation and starter clips

Use for compact proportions, crossbow grip/scale, skinning or clip correctness.
Primary visual owner: [D01](../design/silhouette.md#d01).
Pipeline owners: [characters.py](../../../../tools/asset_pack/characters.py)
(`create_rig`, `equip`, `pose`, `animate`),
[art_style.UNITS/CLIP_FRAMES](../../../../tools/asset_pack/art_style.py),
[attachment fixtures](../../../../tools/asset_pack/test_attachments_blender.py) and
[round-trip verifier](../../../../tools/asset_pack/verify_pack.py).

## Preconditions

Selected [unit/reference](../families/units.md), source/equipment IDs, pose/frame,
existing weight/modifier/bone structure and authorized source/rig/clip scope.
Preserve hand edits and source/weapon/maps before changing proportions.
Pictures establish appearance, not rig topology, timing or deformation correctness.
This procedure does not authorize a rig/animation quality pass.

## Model and weight procedure

1. Compare body landmarks excluding hat/plume/horns/base/equipment; identify the
   intended compactness/face/weapon cue before rescaling parts. Preserve root and
   source forward convention. A shorter torso can require changed joint placement,
   not merely a globally scaled armature or normalized prop.
2. Reuse the existing skeleton definitions and family builders. `create_rig()`
   initially weights modeled parts to named anatomical bones (rigid-part weighting)
   and adds the Armature modifier after applying modeling modifiers. Do **not**
   rerun it indiscriminately on a loaded already-rigged source: it creates a rig,
   weights and modifiers; it is not a safe automatic rig repair.
3. For an authorized new deforming mesh, inspect shoulders/elbows/knees/cloth in
   actual poses before assigning joint loops/blended weights. Existing rigid-part
   fixtures are not proof a new soft-skinned surface deforms attractively. Keep
   anatomical attachment bones deforming; don't disable hand deformation to avoid
   fixing an exported equipment problem.
4. Apply only approved modeling modifiers at the correct pre-rig stage. Keep the
   Armature modifier for export. Blanket Apply All or mesh joining across differently
   weighted parts can destroy rig behavior and is not an optimization recipe.

## Grip and attachment procedure

1. Inspect the standalone equipment's grip-local origin, authored scale and
   transforms, plus the selected `weapon_socket.L/R` and actual hand stance.
   Used weapon sockets are non-deforming; anatomical hands remain deforming.
2. Use `equip(prop,rig,bone,location,rotation)` semantics, not a copied game
   `handslot.r` convention. It preserves `prop.scale` in the desired matrix,
   updates the view layer and sets an explicit parent inverse. Blender bone
   parenting uses the **bone tail** origin; ignoring it creates an offset.
3. In a loaded source, inspect current `parent_type`, `parent_bone`, parent inverse,
   local basis and pose before repairing attachment. Don't apply the prop's scale
   or center it by world bounds: an asymmetrical crossbow/axe's bounding center
   is not the grip. Don't edit shared weapon mesh geometry just to correct one
   instance attachment.
4. Scrub idle/aim/attack and opposite-hand poses; confirm hands contact grip and
   weapons remain correctly scaled/oriented. Dual axes need both sockets/stances.
   Equipment collection inclusion must survive [export selection](export.md).

## Animation and validation procedure

1. Preserve the shared clips `idle`, `walk`, `run`, `attack`, `hit`, `death`;
   FPS/frame extents/loop set come from the live style symbols, not a new leaf
   timing table. Locomotion stays in place. Changing appeal/timing is separate
   animation/design scope; still pictures cannot prescribe it.
2. `animate()` bakes dense pose rotation/location keys, includes loop endpoints,
   records action frame ranges and NLA strips, then restores idle/reset pose.
   Preserve action-slot assignment on the current Blender runtime; don't rename
   clips merely to accommodate a viewer. Rebuilding animation can erase manual
   curves; protect them before deciding whether generation applies.
3. For approved motion review, play each clip at normal speed, then inspect selected
   frames for cape/armor clipping, grip slips, foot contact, hit/death readability
   and loop endpoints. A static action pose or finite bounds is not appeal evidence.
4. Use attachment/style fixtures when changing shared implementation, selected
   source-style audit and source→GLB round-trip verification after authorized export.
   Verifier samples representative pose bounds/loop endpoints; it does not certify
   every vertex trajectory, all joint orientations or complete animation appeal.

## Output and failure recovery

Expected: coherent compact role, preserved anatomical rig/socket/scale contracts,
portable clips and visually intact grip/contact. On source/export divergence,
inspect weights/modifier/order/parent matrices and action-slot selection; don't
apply the armature or relax tests. On unpreserved manual animation or required
hierarchy changes, stop and scope a migration. Runtime action/NLA behavior is
version-dependent; no tool/runtime upgrade is implied.
