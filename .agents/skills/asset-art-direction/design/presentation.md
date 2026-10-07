<a id="d08"></a>
# D08 — Presentation and target-size readability

## Evidence and observation

[Supplied pictures](../references/index.md) use bounded dioramas, a neutral dark
backdrop, elevated three-quarter framing and soft contact light. V0's labels/icons
are reference-board presentation, not text required on models. Close-up detail
can disappear in a small preview; no supplied still establishes the current game
camera or occupied-object pixel size.

## Standard and rationale

Evaluate source art view, portable GLB view and an approved target-view profile.
Compare like poses/cameras, occupied height, lighting/color management and glow
state. Keep full-size diagnostic views but never accept from close-up complexity
alone. Asset-source aesthetics and game framing/UI integration are separate
concerns; beautiful studio lighting is not proof of game fidelity.

## Scope and exceptions

All exported families. A tiny prop may legitimately reduce to a functional color/
silhouette cue. Static dream butterflies are scenery, not units needing six clips.
Older saved sources keep their presentation until explicitly migrated; don't
change current audit exemptions to make all previews look alike.

## Qualitative examples

- **Pass anchor:** B2's dome/telescope differs from B1's lookout without relying
  on a role label; when tested at a real target view that separation must survive.
- **Fail criterion:** declaring improvement solely from a zoomed view, or comparing
  bright new studio material to an older differently posed/lighted preview as if
  it measures modeling quality.

## Provisional inspection tiers and uncertainty

Use **96, 192 and 480-pixel image boxes only as provisional inspection tiers**;
these are recommended diagnostics, not extracted reference measurements, actual
occupied-object sizes or a guaranteed game contract. Record both image dimensions
and occupied height. Replace/augment tiers with existing game-view evidence when
provided by authorized integration work; missing evidence is a stated limitation,
not permission to run/change the engine or another worker's checkout.
No native GPU or animation appeal claim follows from stills.

How: [review scenes](../blender/review-scenes.md).
Evidence/camera recording: [acceptance](../review/acceptance.md).
Saved source and thumbnail profile owners:
[pipeline preview contract](../pipeline/index.md#preview).
