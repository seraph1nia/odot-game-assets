# Units and equipment

Use for the eight authored hero/evil units and their removable equipment.
Read [rig/animation](../blender/units.md), whose primary visual owner is
[D01](../design/silhouette.md#d01), and the selected
[reference](../references/index.md). Never infer timing/rig structure from pictures.

## Role/faction exceptions

- V5/V6/V7: helmet+sword/shield, bent hat+staff, hood+bow/quiver.
- A3: broad fur shoulders/orange beard/hair and dual axes; not a knight recolor.
- E1: skull/helmet, dark shield/red emblem and sword.
- E2: horned violet hood/dark aperture, red eyes/flame staff/hand flame.
- E3: skull hood/red scarf/cape and crossbow.
- E4: horned skull helmet, broad bare arms and dual axes.

These qualify [D03](../design/palette.md#d03) and
[D07](../design/consistency.md#d07) faction/material relationships; they do not
justify a different photoreal shader family. D02's selective organic softness
retains sharp armor/blade/hair planes. Do not smooth every skull/helmet face or
use eyes alone as a role cue. Current older no-map materials are not automatically
invalid under [D04](../design/surfaces.md#d04).

## Existing owners and attachments

[characters.py](../../../../tools/asset_pack/characters.py) owns shared skeleton,
weights, sockets, equipment parenting and clips. The
[berserker](../../../../tools/asset_pack/berserker.py) and
[evil units](../../../../tools/asset_pack/evil_units.py) reuse it.
[art_style.UNITS/CLIP_FRAMES](../../../../tools/asset_pack/art_style.py) own
mechanical counts/timing; this leaf does not declare alternative values.

Weapons retain grip-local pivots and authored scale, including offhand versions.
Use the selected `weapon_socket.L/R`, not a copied hand attachment convention from
the current game's third-party rigs. Anatomical bones remain deforming; used
weapon sockets are non-deforming. Keep armature modifiers and `EQUIPMENT` selection
through [export](../blender/export.md). Export includes equipped props; portable
standalone weapons have their own catalog IDs.

## Review limitations

Normalize body landmarks excluding hats/plumes/base/equipment. Existing knight
preview has an older saved presentation than painted buildings/forest: don't
score an unmatched studio contrast as a modeling improvement. Full six-clip
normal-speed review is needed for grip/contact/cape/foot problems when animation
work is authorized; still references set neither attack timing nor motion appeal.
This route grants no rig/clip migration or game integration work.
