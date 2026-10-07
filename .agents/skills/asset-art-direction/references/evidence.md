# Evidence routes and crop anchors

Read to find the visible evidence for a rule. [Image IDs and original links](index.md)
own reference navigation; [design owners](../design/index.md) own visual criteria.
These crop anchors are inspection coordinates only: no cropped images are added.
Coordinates `[x,y,w,h]` use natural pixels, approximate framing, not segmentation
or numeric style thresholds. Existing V1–V7 association crops stay unchanged.

<a id="crops"></a>
## Crop anchors

| Crop alias | Image / suggested region | Observation route |
|---|---|---|
| C-JOINT | A2 `[290,390,530,370]` | Projecting timbers, sword shield and recessed arch → [D02](../design/shape-edges.md#d02) |
| C-ROOF | B1 `[240,260,640,370]` | Layered broad shingles, framing/sign → [D01](../design/silhouette.md#d01), [D04](../design/surfaces.md#d04) |
| C-WOOD | A7 `[680,760,340,240]` | Longitudinal plank grain, substantial table joints → [D04](../design/surfaces.md#d04) |
| C-MAGIC | F1 `[500,90,320,650]` | Shaded blue/violet body, cyan edge, facet hierarchy → [D06](../design/emission.md#d06) |
| C-CONTACT | F3 `[180,630,860,420]` | Attached rock/leaf/steps, dark roots, open route → [D05](../design/contacts.md#d05) |
| C-WATER | F5 `[500,500,500,500]` | Arch opening, waterfall/channel and contact foam → [D06](../design/emission.md#d06) |
| C-FACE | E3 `[330,220,410,390]` | Hood aperture, skull/eyes, gloved crossbow grip → [D01](../design/silhouette.md#d01) |
| C-CAP | F6 `[180,60,750,470]` | Broad cap silhouette, visible facets, underside glow → [D02](../design/shape-edges.md#d02) |

## Task to evidence

- Architecture role: V1–V4/A1/A4/B1/B2/B5; inspect whole mass before C-ROOF.
- Compact units and weapons: V5/V6/V7/A3/E1–E4; distinguish body landmarks from
  plume/hat/horns/base/weapon. Single-view perspective prevents exact ratios.
- Color relationships: V0/A2/B4/E2/F1–F8; compare surface families, not one
  light-contaminated sampled pixel → [D03](../design/palette.md#d03).
- Planting/contact: F1/F3/F5/F8; whole composition plus C-CONTACT.
- Magic: F1/F4/F6/E2; shaded body versus luminous locations, not halo alone.
- Thematic inheritance: village/E-series/F-series lineup →
  [D07](../design/consistency.md#d07). Dreaming has no supplied picture.
- Presentation/cost: whole supplied views establish composition only →
  [D08](../design/presentation.md#d08), [D09](../design/evidence-cost.md#d09).
  Stills contain no GPU/poly/animation/license measurement.

## Handling derived evidence later

If separately authorized to annotate/crop, preserve the original hash and record
image ID/path, source hash, rectangle, resampling, annotations, output hash and
standard revision. Never overwrite originals or publish derivative reference
copies on the assumption that user supply grants redistribution rights.
Existing asset previews are comparison inputs, not pass exemplars automatically;
bind them to source/GLB hashes and profile settings through
[acceptance](../review/acceptance.md). No numeric calibration or asset improvement
is claimed by this evidence index.
