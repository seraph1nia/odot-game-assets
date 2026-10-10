# Historical M0 artistic proposal — Ledger subsequently approved

Current approval is recorded verbatim in [decisions.md](decisions.md): Ledger,
only the small original menu seal initially. Current production evidence and
remaining acceptance: [production.md](production.md). The proposal/comparisons below
are preserved M0 evidence; pending statements refer to that earlier checkpoint.

**M0 recommendation: A / Ledger**, at the time not yet approved. B: Watch is a genuine dark alternative.
These are original, limited **approval explorations**, not production components.
Discovery preceded their creation; no gameplay feature was invented for the pictures.
All eight final images were actually opened and inspected at their native sizes.

## Exact comparison evidence

| Direction | HUD (real resource/upkeep role + selected producer) | Existing start-menu role |
|---|---|---|
| A / Ledger, 1100×820 | [HUD](previews/ledger-hud-1100x820.png) | [Menu](previews/ledger-menu-1100x820.png) |
| B / Watch, 1100×820 | [HUD](previews/watch-hud-1100x820.png) | [Menu](previews/watch-menu-1100x820.png) |
| A / Ledger, 1280×720 | [HUD](previews/ledger-hud-1280x720.png) | [Menu](previews/ledger-menu-1280x720.png) |
| B / Watch, 1280×720 | [HUD](previews/watch-hud-1280x720.png) | [Menu](previews/watch-menu-1280x720.png) |

Same composition, copy, layout and abstract context isolates light/dark value
hierarchy and warm/cool material relationships. The abstract hex field is original
layout context, **not a current game screenshot or a reference-fidelity claim**.
No full reference or game-source screenshot was newly copied for publication.
Actual renderer: Godot 4.7.2 .NET, GL Compatibility, Mesa llvmpipe; Blender seals
rendered in Cycles CPU. This proves local software renders, not AMD usability,
16GB VRAM headroom, physical desktop input or native FPS. Capture bindings are in
[previews/captures.json](previews/captures.json).

## A — Ledger: warm, quiet information surfaces

Cream ledger surfaces, charcoal-brown ink, restrained amber controls, teal outline
focus. This develops the **current code's** Cozy/parchment/amber relationship with
original native surfaces; it does not copy restricted kit SVGs. World compatibility
comes from cream masonry/warm joinery and deliberate rest areas in inspected
Weaver/Town hall art, not wooden picture frames around every number.

Default Godot font; 30px menu title, 18–20px section titles, 14px quantities/body,
12–13px contextual labels. Proposed 8/12/16/24 spacing family and 36px native
buttons in this exploration (game's menu currently uses 42px; production will
reassess target size). Thin edges and very shallow native rounding; no fake
parchment grain under small text. Right-aligned stocks/income, understated zeroes
and explicit upkeep boundary provide hierarchy without extra icon assets.

A small original face-on hex/gate seal brings a soft beveled material accent only
to the menu. It has no claimed historical heraldry or supplied-reference match.
192px render displayed in a 48px box; visible seal body is smaller because transparent
padding preserves edges. At that size it reads as a gold hex with gate relief,
not a detailed illustration. Do not add fine grain/runes the player cannot see.

## B — Watch: cool, low-key support

Deep blue-slate surfaces, warm cream text, desaturated blue controls and narrow gold
focus. Echoes blue roof/cloth and the cooperative watch identity without imposing
an enemy/red or luminous-forest motif. Same native layout; dark support remains
quieter than the tabletop. Cooler enamel seal, same warm relief and lighting.

B has strong quantity contrast and a distinct menu mood. In the inspected images,
its subtitle/disabled row/secondary controls are quieter; the overall menu looks
more reserved and conventional. It risks merging with dark forest contexts that
this abstract field does not establish. It is viable, not rejected as inferior.

## Evaluation (judgment, not machine aesthetic certification)

| Criterion | A / Ledger | B / Watch |
|---|---|---|
| Game compatibility | Closest to existing shared theme; warmth agrees with settlement materials | Blue/cream agrees with roofs/cloth, but larger mood change |
| Readability | Six quantities, income and two food lines readily separable; dark focused text now consistent | Strong cream quantities; darker controls revised to retain text contrast |
| Distinctiveness | Familiar ledger warmth; tiny seal provides specific watch/hex accent | Stronger night-watch mood, though slate UI alone is generic |
| Visual quality | Quiet planes and thin edges; large light footer draws attention | Less bright footer, cohesive cool plane; somewhat austere |
| Blender feasibility | Small fixed seal uses broad beveled geometry and soft area lighting | Same editable family; no extra render complexity |
| Reproduction | Native surfaces + one deterministic geometry recipe; no copied art dependencies | Same |
| Cost | No texture panels; one 192² RGBA ornament (147,456 decoded bytes before engine overhead/mips) | Same; two exploration PNGs together 294,912 decoded bytes |
| Scalability | Native panel corners do not distort; fixed ornament independent of resize | Same; not proof for dense future dialogs |
| HUD and menu suitability | Both inspected; recommend warm menu/HUD unity rather than unrelated menu art | Both inspected; credible unified dark option |

Recommendation prioritizes continuity and legible information over material
spectacle. Neither direction establishes full accessibility or production polish.
Current backgrounds, dense actions, real dialogs, statuses, long messages and all
interaction states need Phase D–F evaluation. No baked directional light under
runtime data; no shader glow or texture-heavy border family is proposed initially.

## Bounded iterations and observed corrections

1. Revision 0 captured all eight. Inspection found light-button focused text using
   engine-default white on amber, and 720px canvas scaling shrinking 14px text to
   roughly 12px; a mock-context note could sit behind the menu. Preserved samples:
   `previews/revision-0/ledger-menu-1100x820.png`,
   `previews/revision-0/ledger-menu-1280x720.png`,
   `previews/revision-0/ledger-hud-1280x720.png`.
2. Revision 1 explicitly preserved ink on focus, moved diagnostics above content,
   used actual `GameBrand.Positioning` instead of exploratory slogan, and made
   preview layout pixel-preserving (`stretch=disabled`). This is **not a game
   configuration change**: game's canvas-items/expand policy is a future integration
   risk to measure. Original 1100×820 menu scale is now identical at 1280×720.
3. Revision 2 darkened Watch controls from `#527382` to `#385764`: simple sRGB text
   contrast improved from 4.21 to 6.41 for cream normal text, with calculated hover
   contrast 4.69. Ledger dark ink on panel 10.63 / amber 8.40. These limited pair
   calculations are not a complete accessibility check. Preserved previous dark
   menu: `previews/revision-1/watch-menu-1100x820.png`.

Final eight images inspected: no visible clipping in these short mock strings,
ledger title/columns/food boundary clear, footer hierarchy coherent, focused text
readable, 48px seals crisp enough as simple relief, and menu diagnostic no longer
occluded. Known remaining quality issue: all actions share similar emphasis;
production should distinguish primary versus secondary/destructive using native
control variants, not icon proliferation. Upkeep lines currently use spaced text
in the exploration, **not the final reusable grid API**. No runtime interactions
are claimed beyond native rendered focus/disabled states; production buttons need
actual signal/input/state tests. Two targeted revision rounds are consumed; no
unbounded regeneration.

## Proposed approved-system behavior (future, not implemented)

Use native hover/pressed/disabled/focus states; explicit reason copy for unavailable
and read-only actions. Preserve shape/text with status color. No mandatory UI
animation now; later restrained opacity/position transitions only if they improve
feedback, never delay authoritative commands, and allow reduced motion. Keep
world effects/sounds in the game adapters. Typography and spacing live in one
approved theme, not in independently invented asset styles. Additional font,
painted border or icons requires demonstrated benefit and provenance.

## Precise artistic approval questions

1. Approve **A / Ledger** as the production direction, choose **B / Watch**, or
   request a specific bounded change to one of these comparisons?
2. Approve **only the small original watch seal in the menu** as initial Blender
   decoration, or proceed native-only? No elaborate frame/icon family is implied.

Approval authorizes M1's dependent style work, not migration, third-party kit
publication, a font/dependency purchase, world palette changes or game mutation.
The same worker will continue D–G once the required direction decision is routed.
