---
name: svg-icon-set
description: Draw and ship a consistent icon set on a 24 px grid with one stroke weight, correct optical sizes and a build that produces inline React components and a sprite.
version: 1.0.0
license: MIT
tags: [design, svg, icons, frontend, consistency]
---

# SVG Icon Set

Icons assembled from three free packs look wrong together even when each one is well drawn: stroke weights differ by 0.5 px, corners are 1 px in one and 3 px in another, and the set has no optical sizes, so a 16 px icon is a shrunken 24 px drawing with a 0.4 px stroke that disappears.

This skill fixes the geometry first - a 24 px grid, one stroke, one corner radius, a 2 px live area - then produces the three sizes and a build that emits optimised SVG, inline components and a sprite. You end with a set that looks like one hand drew it, and a lint step that rejects the next icon that does not.

## When to use this skill

- You have 40-200 icons from mixed sources and they do not look related.
- Icons blur or vanish at 16 px in a table or a nav rail.
- Every icon is an `<img>` and you cannot colour it with `currentColor`.
- You need a set for a product and a brand, and want one source for both.

Do NOT use for: illustration, logo design, or animation of icons beyond a simple state change. It also does not cover icon fonts, which break accessibility and text rendering.

## Stage 1 - Set the geometry rules before drawing

1.1 Grid: 24x24 viewBox, with a 2 px live area, so drawing space is 20x20. Nothing touches the edge except intentional full-bleed shapes.

1.2 Stroke: 1.5 px at 24 px, with `stroke-linecap="round"` and `stroke-linejoin="round"`. Consistency here is most of the "same family" feeling.

1.3 Corner radius: one value, 2 px on joins. Mixing 1 px and 3 px is visible at 32 px even if nobody can name it.

1.4 Alignment: use whole and half pixels only. A path at 13.37 px renders blurry at 1x and worse at 1.5x.

1.5 Optical corrections: a circle looks smaller than a square of the same box, so circles get 0.5-1 px extra. Do this per icon, never by scaling the group.

| Rule | Value | Fails when |
|---|---|---|
| viewBox | 0 0 24 24 | icons are 20 or 32 |
| live area | 20x20, 2 px inset | icon touches the edge |
| stroke | 1.5 px | mixed 1 and 2 px |
| linecap / linejoin | round | butt caps beside round |
| corner radius | 2 px | 1 px next to 3 px |
| coordinates | .0 or .5 | 13.37 in a path |

Gate: a lint pass finds no coordinate off the half-pixel grid and no stroke other than 1.5.

## Stage 2 - Draw the anchor set of 8 first

2.1 Draw the 8 icons every interface needs: home, search, user, settings, chevron, close, check, plus. These calibrate the rest.

2.2 Draw them together in one frame at the same zoom. Drawing icons one at a time in isolation is how a set drifts.

2.3 Compare at actual size: view at 100% next to the text they will sit with. A 24 px icon beside 16 px text needs visual weight matching, not mathematical.

2.4 Lock the anchor set and treat it as the reference. Every new icon is drawn beside one of the 8, never alone.

Gate: the 8 anchors look consistent at 16, 20 and 24 px side by side.

## Stage 3 - Build the 3 optical sizes

3.1 Ship 24 px as the default, 20 px for dense UI, 16 px for tables and inline text.

3.2 Do not scale. Redraw at each size: at 16 px the stroke stays visually 1.5 but the live area shrinks to 14 px, and detail must be removed.

3.3 Drop detail by rule: at 16 px, remove inner detail, merge shapes closer than 2 px, and drop anything that becomes a smudge.

3.4 Keep the same file stem with a size suffix (`search-16`, `search-24`) so the build can group them.

| Size | Stroke (visual) | Live area | Detail rule |
|---|---|---|---|
| 16 | 1.5 px | 14x14 | one shape, no inner detail |
| 20 | 1.5 px | 18x18 | two shapes maximum |
| 24 | 1.5 px | 20x20 | full detail |

Gate: at 16 px every icon is legible at 100% zoom on a 1x display.

## Stage 4 - Draw with `currentColor` and no fills

4.1 Use `stroke="currentColor"` and `fill="none"` on outlines, so one component takes the text colour of its context.

4.2 For solid icons, `fill="currentColor"` and no stroke. Never mix a stroked and a filled version in the same role.

4.3 Remove `width`, `height` and `fill="#000"` from the source. A hardcoded black icon cannot be recoloured in dark mode.

4.4 Keep `fill-rule="evenodd"` only where a hole is intended, and say so in the file.

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
     aria-hidden="true">
  <circle cx="11" cy="11" r="7" />
  <path d="M16.5 16.5 21 21" />
</svg>
```

Gate: no icon in the set contains a literal colour, a width or a height attribute.

## Stage 5 - Optimise without changing the drawing

5.1 Run SVGO with a fixed config committed to the repo: remove metadata, comments, editor namespaces and unused groups.

5.2 Turn off path simplification that changes geometry (`convertPathData` with aggressive precision) until you have visually diffed the result.

5.3 Round coordinates to 2 decimals at most. More precision is invisible and doubles file size.

5.4 Keep `viewBox`. Removing it is the single most common way an optimised icon breaks on resize.

```yaml
# svgo.config.yml
plugins:
  - name: preset-default
    params:
      overrides:
        convertPathData: { floatPrecision: 2, transformPrecision: 2 }
        removeViewBox: false
        removeDimensions: true
  - name: removeAttrs
    params: { attrs: ["fill", "stroke", "width", "height"] }
```

Gate: total set size under 30 KB for 100 icons, with a visual diff showing no geometry change.

## Stage 6 - Build the components and the sprite

6.1 One build step reads `icons/*.svg` and emits: an inline React component per icon, a JSON manifest, and one sprite with `<symbol>` per icon.

6.2 The React component spreads props and sets `aria-hidden` by default; an icon is decorative unless it is the only label.

6.3 The sprite is for legacy pages and email-adjacent contexts where a component cannot run.

6.4 Name the component from the file stem in PascalCase (`chevron-down` becomes `ChevronDown`) and never hand-edit the generated files.

```js
// scripts/build-icons.mjs
import fs from "node:fs";
const files = fs.readdirSync("icons").filter(f => f.endsWith(".svg"));
const rows = files.map(f => {
  const body = fs.readFileSync(`icons/${f}`, "utf8")
    .replace(/<svg[^>]*>/, "").replace("</svg>", "").trim();
  const name = f.replace(".svg", "").split("-").map(s => s[0].toUpperCase() + s.slice(1)).join("");
  return { name, body };
});
fs.writeFileSync("src/icons/index.jsx", rows.map(r =>
  `export const ${r.name} = (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ` +
  `stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden {...p}>${r.body}</svg>);`
).join("\n"));
```

Gate: the build produces one component per SVG, and the count in the manifest equals the file count.

## Stage 7 - Lint the set in CI

7.1 Fail when an icon has a literal colour, a `width`/`height`, or a viewBox other than `0 0 24 24`.

7.2 Fail when a coordinate is off the 0.5 grid, using a regex over path `d` attributes.

7.3 Fail when a stroke width other than 1.5 appears.

7.4 Fail when a new icon is added without its 16 px variant, once the set has passed 20 icons.

| Check | Rule | Message |
|---|---|---|
| viewBox | exactly `0 0 24 24` | "resize to the 24 grid" |
| colour | no `#` in the file | "use currentColor" |
| dimensions | no width or height | "dimensions come from props" |
| stroke | 1.5 only | "wrong stroke weight" |
| grid | coordinates on .0/.5 | "off-grid coordinate" |

Gate: the lint fails on a deliberately broken icon and passes on the full set.

## Stage 8 - Ship the set with documentation

8.1 One page: every icon, its name, its three sizes, and a copy button for the component name.

8.2 Include a do-not-use list: deprecated names mapped to replacements, so old imports get migrated rather than kept.

8.3 Show the icon beside 14 px, 16 px and 18 px text so the optical size choice is visible, not guessed.

8.4 Version the set. A rename or a removed icon is a breaking change for consumers.

Gate: the docs page is generated from the manifest and matches the build output exactly.

## Stage 9 - Add icons without breaking the family

9.1 New icon: draw beside an anchor, at all three sizes, then run lint.

9.2 Review at 100% zoom next to 5 existing icons, not alone on a canvas.

9.3 If it needs a new stroke or a new corner, the answer is to redraw it, not to add a rule.

9.4 Delete unused icons quarterly, with the manifest count as the trigger for the review.

9.5 Keep one icon per concept. Two icons that mean the same thing in different places costs a review argument every time a new page is built.

9.6 When a product team asks for a custom icon, ask what it replaces first. Most requests are for a concept the set already covers under a different name.

Gate: the set count is recorded, and unused icons are removed or justified each quarter.

## Worked example

A dashboard with 74 icons from 3 packs, rebuilt on one grid.

| Item | Before | After |
|---|---|---|
| Stroke weights in use | 1, 1.5, 2 px | 1.5 px |
| viewBoxes | 20, 24, 32 | 24 only |
| Sizes shipped | 1 (scaled) | 3 (redrawn) |
| Icons with hardcoded black | 74 | 0 |
| Total SVG size | 212 KB | 24 KB |
| Lint checks | none | 5 |
| Time to add an icon | 20 minutes, unclear rules | 6 minutes, lint-guided |

The size reduction came mostly from removing editor metadata and rounding coordinates; the legibility gain came from redrawing the 16 px variants rather than scaling.

## Quality checklist

- [ ] Every icon uses a 24x24 viewBox with a 2 px inset live area
- [ ] One stroke weight, 1.5 px, with round caps and joins
- [ ] One corner radius across the set
- [ ] Coordinates only on the 0.5 grid
- [ ] Anchor set of 8 drawn together and locked as reference
- [ ] Three optical sizes redrawn, not scaled
- [ ] 16 px variants simplified by rule
- [ ] `currentColor` used, no literal colours
- [ ] No width or height attributes in source
- [ ] SVGO config committed, viewBox preserved
- [ ] Coordinates rounded to 2 decimals
- [ ] Build emits components, manifest and sprite
- [ ] Generated files never hand-edited
- [ ] Lint fails on colour, viewBox, stroke and grid violations
- [ ] Docs page generated from the manifest
- [ ] Unused icons reviewed and removed quarterly

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Icons look unrelated | Mixed stroke weights and radii | One stroke, one radius, lint enforced |
| 16 px icons look muddy | 24 px drawing scaled down | Redraw at 16 with reduced detail |
| Icon cannot be recoloured | Literal `fill="#000"` in source | `fill="none"` and `stroke="currentColor"` |
| Icon breaks when resized | `viewBox` removed by optimiser | `removeViewBox: false` in the SVGO config |
| Blurry edges at 1.5x | Off-grid coordinates | Round to the 0.5 grid, re-export |
| File sizes huge for a small set | Editor metadata and float precision | SVGO with 2-decimal rounding |
| Sprite and components disagree | Hand edits to generated files | Regenerate from source, never edit output |
| New icon rejected in review twice | No written geometry rules | Publish the 6 rules and the anchor set |
| Screen reader announces icon names | `aria-hidden` missing on decorative icons | Hide by default, label only when it is the sole label |
| Renamed icon breaks consumers | Rename without a deprecation map | Keep old name as an alias for one version |
| Two icons mean the same thing | No concept list, only a file list | Map one concept to one icon, delete the duplicate |
| Set grows without review | No count or owner | Publish the count, review quarterly |

## Copy-ready agent prompt

> Read the skill at the URL above and audit my icon set. Ask me: how many icons, where they come from, which sizes I ship, and whether they are SVG components or images. Then give me the geometry rules as a short table, the 8-icon anchor set to calibrate against, the redraw rules for 16, 20 and 24 px, the SVGO config with viewBox preserved and coordinates rounded, the build script that emits React components plus a sprite plus a manifest, and the five CI lint checks for viewBox, colour, dimensions, stroke and grid. Finish with the generated docs page and the quarterly unused-icon review. Tell me how many of my icons fail each of the five checks right now.
