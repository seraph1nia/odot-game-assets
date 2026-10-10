# Historical Settings Esc causal investigation — failed Window checkpoint

This record describes the pre-Control-modal source, not a current blocker or a
reproduction using today's probe. See [modal lifecycle](api.md#local-modal-lifecycle)
for the implemented contract and [production.md](production.md) for acceptance.

Bounded investigation authorized by inbox 003, 2026-10-09. No broad acceptance
retry or assertion change. The requested `diagnostic-reasoning` skill was not in
the advertised/project/shared skill locations searched; followed the explicit
causal protocol in that instruction. No dependency installation.

## Hypotheses and falsifiers

Initial hypothesis: keyboard slider editing consumes Esc. Falsifier: slider-only
editing followed by Esc cancels the dialog normally. **Falsified** in a fresh process.
Dropdown-history and Fullscreen-selection hypotheses were likewise falsified by
separate successful cases. The actual trigger is the outside click.

Leading causal boundary: outside click removes **embedded Window** focus even
though its focused **Control** remains the slider/Close button. Esc reaches only
the root Window, not Settings; neither cancellation nor close-request fires.
Falsifier: restore Window focus without changing the Esc event and still fail to
cancel. The small diagnostic counterfactual instead **succeeded**: native
`window.grab_focus()` restores Window focus, then the unchanged Esc emits Settings
`canceled` and hides it. This is a masking condition, not an accepted production fix
and is not applied as a global router or test assertion bypass.

## Fresh-process probes and actual outcomes

All use the same current source, Godot 4.7.2 Compatibility/llvmpipe, private Xvfb
and Dummy audio. Probe: `ui/preview/tests/diagnose_settings.gd`; launcher:
`tools/ui/diagnose_settings.py`. Observations include Window/control focus,
root/Settings/dropdown Window Esc delivery, control GUI delivery, cancellation,
close-request and world-action count.

| Case | Input | Settings after final Esc | Cancellation | Full log |
|---|---|---|---:|---|
| Focused baseline | Synthetic native input | Hidden | 1 | `.cache/ui-diagnosis/baseline-synthetic/probe.log` |
| Dropdown open/Esc history only | Synthetic | Hidden | 1 | `.cache/ui-diagnosis/dropdown-synthetic/probe.log` |
| Fullscreen selection only | Synthetic | Hidden | 1 | `.cache/ui-diagnosis/fullscreen-synthetic/probe.log` |
| Slider focus only | Synthetic | Hidden | 1 | `.cache/ui-diagnosis/slider-focus-synthetic/probe.log` |
| Slider arrow edit only | Synthetic | Hidden | 1 | `.cache/ui-diagnosis/slider-synthetic/probe.log` |
| Outside click only | Synthetic | **Visible** | 0 | `.cache/ui-diagnosis/outside-synthetic/probe.log` |
| Same full intended sequence | Synthetic | **Visible** | 0 | `.cache/ui-diagnosis/full-synthetic/probe.log` |
| Outside click only | OS XTest | **Visible** | 0 | `.cache/ui-diagnosis/outside-os/probe.log` |
| Same full intended sequence | OS XTest | **Visible** | 0 | `.cache/ui-diagnosis/full-os/probe.log` |
| Full + diagnostic focus restoration | Synthetic | Hidden | 1 | `.cache/ui-diagnosis/full-synthetic-focus/probe.log` |
| Full + native popup candidate | Synthetic | **Visible** | 0 | `.cache/ui-diagnosis/full-synthetic-none/probe.log` |

All eleven processes retained logs. **Zero leaked world actions**, including fresh
checks of the explicit local-input guard added during the earlier full run. This
establishes the guard's bounded Settings sequence evidence, not full acceptance.

The OS path uses existing libX11/libXtst through Python ctypes, only inside an
owned Xvfb launched by this tool. Focus is set only on the engine's reported owned
X11 window handle. Enter/Esc/Down/Right and the outside pointer click arrive through
X11/XTest, not `Input.parse_input_event`. The full OS log shows Settings Window focus
true after slider editing, then false immediately after outside click, retained
slider Control focus, Esc delivered only to root, no cancellation, visible dialog.
This confirms the failing keyboard/pointer route represents ordinary X11 events
on this backend. It is not physical keyboard, desktop compositor or native GPU proof.

## Minimal native candidate and contrary result

Inspected the installed engine's version-matched API documentation:
`GodotSharp/Api/Debug/GodotSharp.xml`, `Window.PopupWindow` says outside close
requests are suppressed when Exclusive is enabled; `Window.Exclusive` requires
Transient. Actual probe properties before the candidate were:
`embedded=true, transient=true, exclusive=true, popup_window=false`.

One minimal component candidate added `dialog.popup_window = true` before display,
retaining transient/exclusive. It was predicted to preserve modal input/focus.
**Contrary observation:** the exact full fresh sequence still loses Window focus
at the outside click with all four flags true; final Esc still reaches only root,
Settings stays visible and cancellation count remains zero. The candidate is NOT
an accepted remedy. This source flag remains preserved as tested contrary work;
no reset/discard, no additional broad speculative patch or next full acceptance run.

Visible symptom: final Settings remains open. Trigger: outside embedded-window
click. Masking condition: restoring Window focus manually. Earliest divergence:
Window focus drops, while Control focus does not. Unknown: why this embedded native
modal setup permits the focus drop despite documented flags, and the appropriate
minimal native ownership/parenting fix. Current evidence does **not** justify an
Escape-swallowing handler, test reordering, forced refocus in the acceptance sequence,
removal of world blocking or replacement input-routing framework.

Stopped at the instruction's next-focused-check failure boundary. Await further
guidance before additional investigation/fix. No milestone, production readiness,
publication or migration accepted. All 27 prior full-run captures remain unaccepted
pending final-source success and actual bounded visual review.
