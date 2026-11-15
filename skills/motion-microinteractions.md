---
name: motion-microinteractions
description: Specify UI motion with durations, easing curves,
reduced-motion fallbacks and a token set, so transitions feel
consistent instead of collected from tutorials.
version: 1.0.0
license: MIT
tags: [design, motion, css, accessibility, frontend]
---

# Motion Microinteractions

Motion in most interfaces is a pile of durations copied from
tutorials: 300 ms here, 400 ms there, three different easing curves,
and a bounce on the one thing that should be instant. The result reads
as unpolished without anyone being able to say why.

This skill produces a motion spec you can hand to an engineer: five
duration tokens, three easing curves with their cubic-bezier values, a
rule for which element uses which, a reduced-motion fallback for each,
and a checklist that catches the two failures users actually notice —
motion that blocks input and motion that makes them ill.

## When to use this skill

- A modal takes 600 ms to open and the button feels unresponsive.
- Hover, focus and press states each animate differently across the app.
- You are adding page transitions and want them to feel like one product.
- Someone on the team turned on reduced motion and half the UI broke.

Do NOT use for: video or animated illustration, or a marketing landing
page where a scroll-driven narrative is the point — different medium
and different budget.

## Stage 1 — Decide what motion is for

Motion has four jobs. Anything that does none of them is decoration
and should be cut.

1.1 Continuity: show where a new surface came from — a modal scaling from the button that opened it.

1.2 Feedback: confirm the input registered — a press state within 100 ms, a spinner after 400 ms.

1.3 Attention: move the eye to a change — a row briefly highlighted after an edit.

1.4 Progress: show that something is happening over time — a determinate bar for a known duration.

| Job | Typical duration | Easing | Example |
|---|---|---|---|
| Feedback | 80 to 120 ms | ease-out | button press, checkbox tick |
| Continuity | 200 to 300 ms | standard curve | modal open, sheet slide |
| Attention | 400 to 600 ms | ease-out then hold | row highlight, toast |
| Progress | tied to the task | linear | upload bar, skeleton shimmer |

Gate: every animation in the product names one of the four jobs, and
decoration is removed.

## Stage 2 — Set five duration tokens and stop adding more

Durations should be a small set. Five covers a product; twelve means
nobody is choosing.

2.1 Define: `--dur-1: 100ms`, `--dur-2: 160ms`, `--dur-3: 220ms`, `--dur-4: 320ms`, `--dur-5: 480ms`.

2.2 Map them to the jobs: feedback uses 1 and 2, continuity uses 3, attention uses 4, progress is task-bound and uses 5 only for a full-page skeleton.

2.3 Anything above 480 ms needs a written reason in the spec, because long motion is felt as lag.

Gate: exactly five duration tokens exist, and every transition in the
codebase uses one of them.

## Stage 3 — Choose three easing curves with real values

Easing is where motion gets its character, and a linear curve on a UI
transition reads as broken.

3.1 Standard curve for elements that stay on screen: `cubic-bezier(0.2, 0, 0, 1)` — quick out, gentle settle.

3.2 Enter curve for surfaces appearing: `cubic-bezier(0.05, 0.7, 0.1, 1)` — fast start, soft landing.

3.3 Exit curve for surfaces leaving: `cubic-bezier(0.3, 0, 0.8, 0.15)` — slow start, quick out, and exits run 25% faster than enters.

```css
:root {
  --dur-1: 100ms;  --dur-2: 160ms;  --dur-3: 220ms;
  --dur-4: 320ms;  --dur-5: 480ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter:    cubic-bezier(0.05, 0.7, 0.1, 1);
  --ease-exit:     cubic-bezier(0.3, 0, 0.8, 0.15);
}
.sheet { transition: transform var(--dur-3) var(--ease-enter); }
.sheet[data-closing] { transition: transform var(--dur-2) var(--ease-exit); }
```

Gate: three curves exist, exits are shorter than enters, and no
component defines its own `cubic-bezier`.

## Stage 4 — Animate the two cheap properties only

Layout-triggering properties cost frames. Transform and opacity do
not.

4.1 Animate `transform` and `opacity`; avoid `width`, `height`, `top`, `left` and `box-shadow` for anything that runs during interaction.

4.2 When a size change is unavoidable, animate a wrapper's `transform: scale()` and counter-scale the content, or use a CSS grid row transition with a fixed end state.

4.3 Add `will-change: transform` only for the duration of the animation and remove it after, because a permanent hint costs memory on long lists.

Gate: a performance profile of each interaction shows no layout shift
and frames under 16 ms on a mid-range Android device.

## Stage 5 — Keep motion out of the input path

The interaction the user is waiting on must not wait for the
animation.

5.1 Feedback within 100 ms of the press, even if the resulting state arrives later — an optimistic press state is what makes a slow action feel fast.

5.2 Never block input during a transition; a modal that ignores taps for 300 ms is felt as broken.

5.3 For anything over 400 ms, show a progress state rather than a longer animation.

Gate: every interaction accepts input during its transition, and press
feedback lands within 100 ms.

## Stage 6 — Respect reduced motion properly

The `prefers-reduced-motion` query is not a request to remove all
feedback; it is a request to remove movement.

6.1 Replace transform and parallax motion with opacity or instant state changes, and keep the state change itself.

6.2 Set durations to 1 ms rather than `animation: none`, so `transitionend` handlers still fire.

6.3 Test with the OS setting on, on both platforms, and check that no component relies on an animation callback to finish its logic.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 1ms !important;
    scroll-behavior: auto !important;
  }
}
```

Gate: with reduced motion on, every flow completes and no
`transitionend` handler stalls.

## Stage 7 — Specify the five interactions that matter

A spec is a table, not an adjective. Write the five interactions users
touch most.

7.1 Button press: scale to 0.98 over 100 ms, standard curve, no bounce.

7.2 Modal open: opacity 0 to 1 and scale 0.96 to 1 over 220 ms with the enter curve; the backdrop fades over 160 ms.

7.3 Toast: slide in from 12 px below over 220 ms, hold 4 seconds, exit over 160 ms with the exit curve.

7.4 Accordion: height from 0 to content over 220 ms; content opacity over the last 120 ms.

7.5 List item after edit: background highlight fading from 12% accent to transparent over 480 ms.

| Interaction | Duration | Curve | Property | Reduced motion |
|---|---|---|---|---|
| Button press | 100 ms | standard | transform scale | instant state |
| Modal open | 220 ms | enter | opacity, scale | opacity only |
| Modal close | 160 ms | exit | opacity, scale | opacity only |
| Toast in / out | 220 / 160 ms | enter / exit | transform, opacity | opacity only |
| Row highlight | 480 ms | standard | background-color | no highlight |

Gate: five interactions specified with duration, curve, property and
reduced-motion behaviour.

## Stage 8 — Encode the tokens, not the values

Values copied into components drift within a sprint. Tokens keep them
together.

8.1 Define the duration and easing tokens once, in the design system's CSS layer or Tailwind config.

8.2 Ban literal milliseconds in component code with a lint rule, and allow the token names only.

8.3 Export the same tokens to the design tool so the prototype and the build use identical curves.

Gate: a grep for `ms` in component styles returns only token
definitions, and the design file uses the same values.

## Stage 9 — Review motion against three questions

Review is what keeps a motion system from growing a special case per
feature.

9.1 Does it do one of the four jobs, and is it the cheapest way to do that job?

9.2 Would removing it make the interface harder to understand? If not, remove it.

9.3 Does it hold at 60 fps on a mid-range device with the network throttled?

Gate: every animation passes all three questions in review, and none
is justified by taste alone.

## Worked example - 11 durations down to 5

A dashboard app with 11 durations, 6 easing curves and three different
modal timings.

| Measurement | Before | After | Change |
|---|---|---|---|
| Duration values in code | 11 | 5 | tokens only, lint rule |
| Easing curves | 6 | 3 | standard, enter, exit |
| Modal open | 600 ms | 220 ms | enter curve |
| Press feedback | 0 ms, none | 100 ms scale | optimistic press state |
| Frames dropped on open | 9 of 36 | 0 | transform and opacity only |
| Reduced-motion flows broken | 3 of 7 | 0 | 1 ms durations, no callback reliance |

The 600 ms modal was the change users felt. It had been set to 600 ms
to feel "smooth", and it made every dialog feel heavy; 220 ms with the
enter curve reads as faster and calmer at the same time.

The three broken reduced-motion flows were all the same bug: a
component set `animation: none` under the media query and then waited
for `animationend` to move to the next step. Setting duration to 1 ms
kept the event and fixed all three.

The lint rule banning literal milliseconds was what kept it clean.
Without it, two new durations appeared within a month of the refactor.

## Quality checklist

- [ ] Every animation names one of the four jobs.
- [ ] Exactly five duration tokens defined.
- [ ] Three easing curves with written cubic-bezier values.
- [ ] Exits run shorter than enters.
- [ ] Only transform and opacity animated during interaction.
- [ ] No layout shift measured in a profile of each interaction.
- [ ] Press feedback within 100 ms.
- [ ] Input accepted during every transition.
- [ ] Reduced motion tested with the OS setting on.
- [ ] Durations set to 1 ms under reduced motion, not `none`.
- [ ] Five key interactions specified in a table.
- [ ] Tokens exported to the design tool.
- [ ] Lint rule bans literal milliseconds in components.
- [ ] Every animation passes the three review questions.
- [ ] 60 fps verified on a mid-range device with throttling.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Interface feels laggy but timings look small | Width or height is animated, forcing layout each frame | Animate transform and opacity only |
| Modal ignores the first tap | Input blocked for the transition duration | Accept input immediately and animate the surface |
| Motion feels different on every screen | Components carry their own durations | Move to five tokens and lint literal values |
| Flow hangs with reduced motion enabled | Logic waits on `animationend` that never fires after `animation: none` | Set duration to 1 ms so the event still fires |
| Animation janks on a mid-range phone only | Permanent `will-change` and many layers | Add the hint during the animation and remove it after |
| Two elements enter at different speeds | Enter and exit curves swapped between components | One enter curve, one exit curve, named in the spec |
| Long animation used to hide a slow request | Motion used as a progress substitute | Show a real progress state after 400 ms |

## Copy-ready agent prompt

> Read the skill at the URL above and write a motion spec for my product. Classify every animation by its job, define five duration tokens and three easing curves with cubic-bezier values, restrict interaction motion to transform and opacity, set press feedback at 100 ms, and specify the five most-used interactions with duration, curve, property and reduced-motion behaviour in a table. Encode the tokens once, add a lint rule banning literal milliseconds, and add a reduced-motion block that uses 1 ms durations rather than none. Report frames dropped and the reduced-motion test result per flow. Stop and show me any animation that fails the three review questions.
