---
name: asset-art-direction
description: Author, refine or review Odot Blender assets against the supplied painted fantasy references. Use for visual standards, modeling/material/UV/rig refinements, shared-library edits and reference-led acceptance reviews.
---

# Asset art direction

Scope: authored 3D assets in this repository, not game camera/UI redesign.
This skill provides guidance, **not permission** to rebuild, render, export,
change shared defaults or start a quality pilot. Preserve manual source/map edits.
Use isolated workers for authorized operations; keep desktop Blender for review.

Resolve the selected canonical asset ID and intended picture through the
[reference index](references/index.md). Read the relevant family and procedure
below, then that procedure's primary design rule. Do not load every leaf.

| Task | Route |
|---|---|
| Make a building recognizable at small size | [Buildings](families/buildings.md) → [blockout/construction](blender/construction.md) |
| Grain runs across wood, UVs/maps look wrong | [UV/maps](blender/uv-maps.md) |
| Harsh edges, flattened crystal faces, mushroom smoothing | [Normals/topology](blender/normals.md); shared edit → [library ownership](blender/libraries.md) |
| Floating/repetitive vegetation or ground shading | [Environment](families/environment.md) → [contacts](blender/contacts.md) |
| Glow hides form or water looks detached | [Emission/water](blender/emission-water.md) |
| Unit proportions, crossbow grip, deformation or clips | [Units/equipment](families/units.md) → [rig/animation](blender/units.md) |
| Change a prototype rather than one composition | [Library edit](blender/libraries.md) |
| Set up comparable views | [Review scenes](blender/review-scenes.md) |
| Export/check a selected authored source | [Export/compatibility](blender/export.md) → [check selection](pipeline/index.md#checks) |
| Evaluate “better quality,” calibrate a rule or plan a pilot | [Review](review/index.md) → [acceptance](review/acceptance.md) |
| Add a prop/terrain variant | [Props/terrain](families/props.md) |
| Dream fauna claimed to match a supplied reference | [Authored-adaptation scope](families/environment.md#dreaming) |

For other questions, use the [design](design/index.md),
[Blender](blender/index.md) or [pipeline](pipeline/index.md) index.
Each design rule has one canonical owner. Family leaves add exceptions; recipes
own how-to. Executable settings remain in
[art_style.py](../../../tools/asset_pack/art_style.py), not copied into leaves.

Complete a refinement review with: selected ID and reference/crop, applicable
D-rule IDs, authorized mechanical-check evidence, matched target-view comparison,
resource deltas and limitations. Guidance installation improves no asset by itself.
Actual game occupied-pixel sizes and numeric art calibration remain provisional.

Pi discovers project `.agents/skills/` directories and advertises the entry's name
and description; it reads this body on demand. In Pi, `/skill:asset-art-direction`
can force loading. Supporting files are ordinary linked Markdown, **not nested
invocable skills**. No duplicate `.pi` entry is needed. Other harness discovery
must be verified separately; no universal slash-command promise is made.
