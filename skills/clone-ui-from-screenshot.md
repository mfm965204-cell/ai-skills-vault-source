---
name: clone-ui-from-screenshot
description: Reverse-engineer any app or website UI from screenshots into pixel-accurate, responsive, accessible HTML/CSS/React/Tailwind/Flutter code. Includes measurement extraction, design-token recovery and a pixel-diff verification loop.
version: 1.0.0
license: MIT
tags: [ui, frontend, reverse-engineering, design, screenshots, tailwind]
---

# Clone UI From Screenshot

Given one or more screenshots of an app or website, produce working front-end code that matches it - layout, spacing, type, colour, states and responsive behaviour.

## When to use this skill

- Rebuilding a UI you have screenshots of (your own app, a design handoff, a competitor pattern for study).
- Recreating a design in code because the Figma file is missing.
- Building a practice clone to learn a layout system.

**Ethics and law:** clone for learning, for migrating your own product, or for internal reference. Do not ship a pixel-identical clone of another company's brand, logos or copyrighted illustrations, and do not use it to impersonate a service or phish users. Reproduce layout and interaction patterns; replace brand assets, copy and imagery with your own.

## Stage 0 - Inventory the input before writing code

List what you actually have:

1. How many screens? One screenshot gives one state; a real UI has empty, loading, error, filled, hover, focus, disabled.
2. What resolution? A 1170x2532 iPhone screenshot is 3x - divide measured pixels by 3 for CSS pixels.
3. Is it light or dark only? You must derive the other theme or explicitly ship one.
4. Which platform idioms? iOS tab bar vs Android bottom nav vs web header change the shell.

If the user gave only one screenshot, say plainly which states you are inventing.

## Stage 1 - Extract measurements (do this before designing)

Work at a fixed reference width: 390 CSS px for mobile, 1440 for desktop. Convert every measurement to that width.

Extract and write down:

- **Grid and margins** - left/right content margin (commonly 16 or 20 px on mobile), gutter between cards (12-16 px).
- **Type scale** - measure cap height of each text style, estimate px size, note weight. Typical mobile scale: 32/28 hero, 22 section, 17 body, 15 secondary, 13 caption. Line height 1.2 for display, 1.45 for body.
- **Colour** - sample the background, surface/card, primary action, text primary, text secondary, border, and any accent. Convert to hex, then to HSL to see if they share a hue.
- **Radius** - card corner, button corner, avatar (full circle), input corner. One radius family is normal: e.g. 8 / 12 / 16 / full.
- **Elevation** - is separation done with shadow, border, or a lighter surface? Most modern UIs use surface tint, not shadow.
- **Iconography** - stroke width (1.5 or 2 px), size (20 or 24), filled vs outline.

Record all of it as CSS custom properties. This token block is the contract the rest of the build obeys.

```css
:root {
  --bg: #0B0B0F;
  --surface: #15151C;
  --surface-2: #1D1D26;
  --text: #F5F5F7;
  --text-muted: #9A9AA8;
  --border: #26262F;
  --primary: #5B5BF5;
  --on-primary: #FFFFFF;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-5: 24px; --space-6: 32px;
  --font: -apple-system, "Segoe UI", Roboto, sans-serif;
  --shadow-card: 0 1px 2px rgba(0,0,0,.06), 0 8px 24px rgba(0,0,0,.08);
}
```

## Stage 2 - Build the component inventory

Walk the screenshot top to bottom and name every element as a component with its variants:

`AppHeader`, `SearchBar`, `CategoryChip (default/selected)`, `ProductCard (default/sale/sold-out)`, `TabBar (4 items)`, `EmptyState`, `Skeleton`.

For each: props (data in), states, and whether it is shared. Anything appearing twice becomes a component. Anything appearing once stays inline until it repeats.

## Stage 3 - Skeleton first, colour later

Build the whole screen in grey boxes at correct sizes. Screenshot it next to the original at the same width. Fix layout and spacing while it is still grey - this is where 80% of "it looks off" actually lives.

Only after the grey skeleton matches: apply tokens, then type, then icons, then imagery.

## Stage 4 - Responsive behaviour

Decide, do not guess:

- Mobile-first single column below 640 px.
- 640-1024: 2 columns, sidebar collapses to a drawer.
- 1024+: fixed sidebar or max-width container (1120-1280 px), 3-4 columns.
- Fluid rules: `clamp()` for headings, `minmax()` for grids, `aspect-ratio` for media, `gap` in place of margins between siblings.

Never fix a height on a text container. Never use a fixed `px` width on a card grid.

## Stage 5 - The verification loop (this is the skill)

1. Screenshot your build at exactly the reference width, same device pixel ratio.
2. Compare side by side at 100% zoom. Check in this order: **vertical rhythm, then horizontal alignment, then type size, then colour, then radius/shadow.**
3. Overlay at 50% opacity if you can - misalignment jumps out instantly.
4. Log every delta as a number ("card gap 16 vs 12", "heading 24 vs 28"). Fix in one batch.
5. Repeat until no visible delta remains at 100% zoom.

Do at least two loops. One loop always leaves 5-10 small errors that a user notices as "cheap".

## Stage 6 - States and interaction

For each interactive element: hover (web), focus-visible (always), active, disabled, loading. Focus rings are not optional - use `outline: 2px solid var(--primary); outline-offset: 2px`.

Add the states the screenshot did not show but the product needs: empty list, error banner, skeleton loading, long-text truncation, offline. Say explicitly which ones you added.

## Stage 7 - Accessibility pass

- Semantic HTML: `button` for actions, `a` for navigation, `nav`/`main`/`header` landmarks.
- Contrast: 4.5:1 for body, 3:1 for large text and UI borders.
- Touch targets at least 44x44 px with 8 px separation.
- Alt text on every meaningful image; `alt=""` on decoration.
- Respect `prefers-reduced-motion` for every transition.
- Keyboard: full tab order, no traps, Esc closes overlays.

## Output format

Deliver in this order:

1. `tokens.css` - the variable block.
2. Components - one file per component, Tailwind or plain CSS, matching the user's stack (ask if unknown; default to Tailwind + React).
3. The composed screen/page.
4. A short `NOTES.md` listing what was measured, what was invented, and what is still off by design.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Everything looks 10% too big | Measured at 3x without dividing | Divide by DPR |
| Spacing feels tight/loose | Margins used instead of gap | Switch to gap and one spacing scale |
| Colours look muddy | Sampled a compressed JPEG | Sample flat areas, round to nearest 5% |
| Text wraps differently | Font substitution | Match the metric-compatible font or set letter-spacing |
| Looks flat | Missing subtle border/shadow layer | Add 1px border at 8% or a 2-layer shadow |
| Responsive breaks | Fixed widths | Fluid units and minmax grids |

## Quality checklist

- [ ] Grey skeleton matched before colour
- [ ] Every measurement traced to a token, no magic numbers
- [ ] Two verification loops done
- [ ] All five interactive states present
- [ ] Empty, loading and error states exist
- [ ] Contrast and touch targets pass
- [ ] No horizontal scroll at 320 px

## Copy-ready agent prompt

> Read the skill at the URL above and follow it exactly. I will attach screenshots. Stage 0: tell me what is missing (states, breakpoints, dark mode). Stage 1: output the measured token block. Then build the grey skeleton, then components, then the page. Do two pixel-diff verification loops and report every delta as a number before you call it done.
