# UI validation and limitations

## Current M1 foundation/local modal — 2026-10-09

- Fresh final-source Godot 4.7.2 .NET import and owned software acceptance:
  **271 checks, zero failures, 27 actual captures**, `.cache/ui/m1-tab-scope/tests.log`.
  Source hashes/results: `production/m1-tab-scope/results.json`.
- OS XTest: **11 unchanged full Settings-sequence checks**, **64 modal-scope checks**,
  zero leaked world actions. Active dropdown/modal Esc does not reach an underlying
  unhandled-input spy; hidden-modal Esc does. Application focus loss/return, native
  pointer/Enter/Tab/Shift-Tab, slider, focus return, hide/reopen and confirmations
  exercised on a private display, including Tab reachability of native internal
  category TabBar and keyboard Right/Left navigation. Logs `*-os-none-m1-tab-scope/` in `.cache/ui-diagnosis/`.
- Isolated baseline/dropdown/Fullscreen/slider-focus/slider/outside cases passed on
  both synthetic and OS routes. Window candidates and original failed gates remain
  failed; `production.md`/diagnosis records preserve the contrasts.
- All 27 final captures actually inspected at native dimensions; SHA-256 proves
  equality with reviewed frames. One targeted 12px spacing correction preserved
  text/coverage. Visual judgment and remaining dense-scroll issues: `production.md`;
  frame bindings: `visual-review.json`. No machine aesthetic certification.
- UI-only private independent project loaded **nine scenes, Theme and seal** with
  no prototypes/game/tooling copied. Relative dependencies/hash and texture budgets:
  `payload.json`; full log `.cache/ui-payload/m1-tab-scope/load.log`.
- Metadata/source/image contracts: **7 passed**, `.cache/ui/m1-tab-scope/plan.log`.
  Existing fast route: **56 tests and 2 inline JavaScript programs passed**, Python
  lint/syntax/guardrails, `.cache/ui/m1-tab-scope/repo-check.log`. Offline execution;
  one unused import was corrected after `.cache/ui/m1-final/repo-check.log` failed.
  No dependency installed. `git diff --check` passed.
- Original source/PNG bytes retained from M0 after rename. Source RGBA/alpha checks
  remain valid for the same 192px seal, displayed 48px. No nine-slice surfaces.

Complete E–G composition/state/scroll acceptance is **not established**. See current
`tasks.json`/`api.md` for coverage and service adapter boundaries. No game integration,
physical keyboard/audio, native GPU/compositor/VRAM/FPS, older engine, localization/
RTL/HiDPI/small-window certification. No delivery pipeline/publication/migration.

## Historical M0 validation

Date: 2026-10-09. Scope: **A–C intake/artistic exploration**, not production UI.
The pending statements below describe M0 only, superseded by the current record.

## Successful checks

- `no-mistakes doctor`: configured daemon and gate validator available. No pipeline
  run/push started; artistic approval is a separate prior gate.
- Existing isolated Blender worker executed `tools/ui/explore_crest.py` with factory
  startup: two editable `.blend` sources and transparent original 192px PNGs.
  Full log `.cache/asset-check/logs/ui-exploration-seals.log`.
- Standalone Godot preview headless import succeeded under existing 4.7.2 .NET.
  No C# gameplay build or game import. `.cache/ui-explorations/import.log`.
- Eight final captures: two directions × real HUD/menu roles × 1100×820/1280×720.
  Actual OpenGL renderer is Mesa llvmpipe (LLVM 23.1.1, 256 bits), not AMD.
  [Capture metadata](previews/captures.json); final driver summary
  `.cache/ui-explorations/capture-r2.log`. Renderer warning about unavailable V-Sync
  is retained, not called a missing-resource error.
- All eight final PNGs actually inspected with image understanding; comparison,
  remaining issues and two targeted rounds are in [art-direction.md](art-direction.md).
- `python tools/ui/test_plan.py`: **5 passed**. Inventory/task fields, unique ids,
  declared and acyclic dependencies, pending approval/production state, original
  source/output hashes, PNG dimensions/RGBA headers, eight actual capture sizes
  and portable exploration resource paths. These are narrow mechanical checks.
- Godot `--headless --path ui/preview --script res://explorations/check_images.gd`:
  **passed**, two source PNGs 192px, alpha present, transparent corner and opaque
  center. `.cache/ui-explorations/image-check-r1.log`.
- `mise run check`: **54 tests and 2 inline JavaScript programs passed**, Python
  lint/syntax and existing guardrails. `.cache/ui-explorations/repo-check.log`.
- `git diff --check`: passed. Game revision remained
  `d7e697710e15addade9ce82d28d6de94c05aacab` and its Git status stayed clean.

## Earlier failures/corrections retained

- Unconfigured `godot` shim did not run in assets. Used detected installed engine
  directly without installing or changing mise configuration.
- First capture failed to initialize .NET host because dotnet shim was unconfigured;
  command timed out. Explicit existing `DOTNET_ROOT`/PATH solved it. The exact owned
  engine/Xvfb processes were stopped; capture runner now terminates its owned
  process group on error/timeout. `.cache/ui-explorations/capture.log` retains failure.
- First image checker called nonexistent `Image.has_alpha()` and timed out;
  corrected to actual `Image.detect_alpha()`, bounded rerun succeeded. Earlier
  `.cache/ui-explorations/image-check.log` remains failed evidence. It was not
  relabeled a pass. Image file loading now globalizes local source paths to avoid
  a misleading export warning: this checks source PNGs, not packed-game exports.
- Pillow was not present; no dependency was added. PNG headers use Python stdlib,
  image content uses Godot's existing Image API.

## Not yet established

No direction approval. No production theme/components, full HUD/menu behavior,
mouse/keyboard/focus traversal/scroll/modal assertions, 1600×900/1920×1080 acceptance,
custom-small-window/localized-text tests, full dependency payload audit or real
migration. Rendered native focus and disabled examples are **not input tests**.
No original-game current-theme capture (checked-in screenshots are older).
No native GPU/compositor/VRAM/FPS or physical audio evidence. No full 3D export,
style fixture suite or all-asset rebuild needed: existing world inputs are unchanged.
No PR/push/merge/release or game mutation.

Native flat surfaces use no nine-slice textures, so slice-margin validation is
not applicable to M0. Fixed seals have transparent padding and stay 48px; no
ornament stretching. Two PNGs total 67,642 physical bytes, 294,912 decoded RGBA bytes
before engine/mip/import overhead, not measured GPU memory or draw costs. The
approved direction will ship at most one seal initially if accepted.

Next gate is artistic decision, then M1's actual source/export/import/component
and interaction validation. Planning task completion certifies planning output,
not the future implementation described by that output.
