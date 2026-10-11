# Woodland HUD diagnosis — retained failures, measured boundaries

These are bounded software/native-control investigations, not hardware/input
performance certification or final-source acceptance. Final normal receipts are
owned by `woodland.md`, `woodland-validation.json`, `payload.json` and catalog
owners. Failed campaigns and their PNG/result bytes remain unchanged.

## Information/footer overlap

`woodland-1`: 637 checks / 5 failures / 79 captures. `woodland-2`: 652 / 4 / 85.
At identical 1280×720 with the same 14px/12px font, slices and padding, actual
information minimums were:

| Projection | Ledger | Upkeep | Information | Footer top | End-to-footer gap |
|---|---:|---:|---:|---:|---:|
| Building / Producer | 203px | 160px | 367px | Y=444 | +17px |
| Combat / Producer | 226px | 122px | 352px | Y=444 | +32px |
| Preparation / Producer | 244px | 160px | 408px | Y=444 | −24px |
| Lost / Producer | 226px | 160px | 390px | Y=444 | −6px |

The first divergence is the ledger's added supplied context: Preparation adds
33px of actual 12px wrapped copy plus its separation; Lost adds 15px plus
separation. The independent fixed bottom anchor did not reserve space for it.
Construction's initial larger minimum was a separate pressure, not the initiator.
Changing viewport/font or shaving another arbitrary offset would only mask this.

One controlled native allocation counterfactual kept text/font/padding/content and
target rectangles intact: a VBox reserves the footer and 16px separation; an upper
ScrollContainer bounds stock/upkeep. The native gutter leaves 290px of content
instead of the old 280px, but measured heights/wraps stayed identical (367/352/408/
390px), so width did not conceal the cause. **44/0** bounds/transition checks;
additional supplied paragraphs increased native scroll extent without moving the
footer. Real wheel input reached the entire final upkeep line. Actual Preparation,
Lost and long-copy-scrolled PNGs were inspected. Logs/measurements:
`.cache/ui-woodland-diagnosis/{baseline,counterfactual}/`.

The correction is the existing host's native section/scroll contract, not a global
measurement/layout framework or deferred loop. Tests still assert visible occupied
information versus footer separation and now independently prove clipped overflow
is readable/reachable. No content/action is hidden, no font/readability minimum or
supported resolution is reduced, and no failed assertion is waived.

## Synthetic wheel versus pointer delivery

The first focused allocation run retained **362 checks / 20 failures / 6 captures**
(`production/woodland-layout-focused/`). Geometry, fonts, scroll and keyboard paths
passed; all twenty footer pointer actions failed after injected wheel events.

A bounded trace compared fresh Ready input, identical post-wheel clicks, keyboard,
one balanced-wheel counterfactual and owned X11/XTest. Native parser evidence:

- Fresh left press/release: Input masks **1 → 0**, events reach `gui/Ready`, exactly
  one down/pressed/up sequence; correct action intent.
- Unreleased wheel-down/up indices leave mask **24**. Subsequent left events enter
  the parser as **25 → 24** but never reach the hovered native Button. Hover path,
  enabled state and `[1022,553;230×36]` target rect stay unchanged. No decorative
  clip/overlay owns this hit region.
- Enter on the same target still works. Releasing wheel indices and using paired
  wheel pulses restores masks **1 → 0**, GUI events and exactly one pointer action,
  without changing content/geometry/input routing.
- Owned XTest uses real paired wheel/button events; Ready, Pause and Reconnect all
  receive native down/up/pressed and emit their expected intents. World count stays
  unchanged. **12/0** final trace checks. A fixture initially sent X11 button 4
  (wheel up) while checking downward motion; that failed history remains at
  `.cache/ui-footer-input/history-os-up/`, corrected X11 button 5 performs down.

The smallest owned `run_ui.gd::wheel_at` correction pairs each injected press and
release. It does not directly call actions, reset global input, substitute keyboard
for pointer or alter timing/bounds. Fresh focused result: **382/0, six captures**.
After ordinary rebase onto the separately landed tree, **382/0** woodland and
**126/0** compact-tree focused checks also passed. Raw parser/GUI/signal/ownership
trace: `.cache/ui-footer-input/input.json`; scoped driver/logs stay in that cache.

## Native category selection versus an active modal

The first post-rebase complete campaign retained **1145/1/92** at
`production/woodland-final/`: the ranged recruiter pointer action failed.
A fresh bounded category trace found a different first divergence, with mouse mask
**0** throughout: native TabBar does not reset on Home. The old fixture accumulated
Right presses (actual tabs 0,1,3,4), unintentionally opening Skill Tree. The modal
correctly blocked the later underlying recruiter click. The old group assertion
could pass from a stale prior Market intent.

One controlled native-arrow counterfactual used the actual current tab, selected
0/1/2/3, preserved the same ranged target `[290,642;231×36]`, and delivered the
Crossbowman pointer action without an active modal. No wheel or hit-region edit was
needed. `.cache/ui-category-input/category.json` and `probe.log` retain the trace.
The owned production fixture now uses actual native Left/Right navigation, asserts
the intended category and absent modal, and clears stale mock intent before each
real pointer activation. All existing category/recruiter assertions remain; no
production action is called directly and no UI key router/Home behavior is invented.
