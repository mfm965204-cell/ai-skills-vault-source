---
name: design-tokens-tailwind
description: Turn a visual style into one token source that drives Tailwind classes, CSS variables and dark mode, so a colour change is one edit and not a 200-file search.
version: 1.0.0
license: MIT
tags: [frontend, tailwind, design-tokens, css, dark-mode]
---

# Design Tokens For Tailwind

A Tailwind codebase drifts into 40 shades of grey and 6 near-identical blues because each component picks the nearest class that looks right. Two years in, a rebrand means a search across 200 files and a review that misses 30 of them.

This skill puts every visual decision in one token file that generates the Tailwind theme, the CSS variables and the dark-mode overrides. You end with a 3-layer token system, a build step that fails when a component hardcodes a hex, and a dark mode that switches by variable rather than by duplicated classes.

## When to use this skill

- Your `className` strings contain `text-[#1f2937]` and `bg-blue-500` in the same component.
- Dark mode is a second set of classes (`dark:bg-gray-900`) pasted beside every light class.
- Design hands you a Figma file and you translate colours by eye.
- You are about to rebrand and want a 1-file change, not a 200-file one.

Do NOT use for: choosing the palette itself (that is the brand identity job), component structure, or migrating away from Tailwind. It also does not cover native mobile token systems.

## Stage 1 - Separate the three token layers

1.1 Primitive tokens: raw values with no meaning - `grey-100`, `blue-600`. They never appear in components.

1.2 Semantic tokens: meaning mapped to a primitive - `surface`, `text-muted`, `border-strong`, `accent`. These are what components use.

1.3 Component tokens: only when a component needs a decision the semantic layer cannot express - `button-primary-bg`. Use sparingly; 5-10 at most.

1.4 Name primitives by scale, not by appearance. `grey-500` survives a palette change; `light-grey` does not.

| Layer | Example | Allowed in components |
|---|---|---|
| primitive | `--grey-900: #111827` | no |
| semantic | `--text: var(--grey-900)` | yes |
| component | `--btn-primary-bg: var(--accent)` | only in that component |

Gate: every colour in the app resolves to a semantic token, and no component references a primitive.

## Stage 2 - Author tokens as JSON, not as CSS

2.1 One file, `tokens.json`, with `primitive` and `semantic` groups, and dark values under a `dark` key on the semantic group only.

2.2 Primitives never change between themes. Only semantic values switch, which is why dark mode is one override block.

2.3 Include the non-colour tokens too: spacing scale, radius, font size, shadow, z-index. Colour-only token sets always leave the rest to drift.

2.4 Commit the JSON and the generated CSS. The JSON is the source; the CSS is the artefact a reviewer can diff.

```json
{
  "primitive": {
    "grey-50": "#f8fafc", "grey-500": "#64748b", "grey-900": "#0f172a",
    "blue-600": "#2563eb", "blue-400": "#60a5fa"
  },
  "semantic": {
    "surface":    { "value": "{primitive.grey-50}",  "dark": "{primitive.grey-900}" },
    "text":       { "value": "{primitive.grey-900}", "dark": "{primitive.grey-50}" },
    "text-muted": { "value": "{primitive.grey-500}", "dark": "{primitive.grey-500}" },
    "accent":     { "value": "{primitive.blue-600}", "dark": "{primitive.blue-400}" }
  }
}
```

Gate: `tokens.json` is valid JSON and every semantic value resolves to a primitive that exists.

## Stage 3 - Generate CSS variables for both themes

3.1 Emit `:root` with the light values and `[data-theme="dark"]` with the overrides. One attribute on `<html>` switches the whole app.

3.2 Emit semantic variables only. Primitives stay in the JSON and never reach the browser, which prevents someone using them directly.

3.3 Keep the generated file out of hand edits: a header comment saying `generated - do not edit` and a CI check that the file matches the JSON.

3.4 Add `color-scheme: light dark` on `:root` so native form controls and scrollbars follow the theme.

```css
/* generated from tokens.json - do not edit */
:root {
  color-scheme: light dark;
  --surface: #f8fafc;
  --text: #0f172a;
  --text-muted: #64748b;
  --accent: #2563eb;
  --radius-md: 10px;
  --space-4: 16px;
}
[data-theme="dark"] {
  --surface: #0f172a;
  --text: #f8fafc;
  --accent: #60a5fa;
}
```

Gate: toggling `data-theme` on `<html>` changes every surface and text colour with no class changes.

## Stage 4 - Wire the tokens into the Tailwind theme

4.1 Map semantic tokens to Tailwind colour names in `tailwind.config.js` using `var(--token)`, not hex values.

4.2 Extend, do not replace, `colors`. Replacing removes the default palette and breaks every existing `bg-red-500` in one commit.

4.3 Turn off the default palette once the migration is complete, and only then. The order matters: migrate first, remove second.

4.4 Add the spacing and radius tokens to `theme.extend` so `p-4` and `rounded-md` come from the same source as colours.

```js
// tailwind.config.js
module.exports = {
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        surface: "var(--surface)",
        text: { DEFAULT: "var(--text)", muted: "var(--text-muted)" },
        accent: "var(--accent)",
      },
      borderRadius: { md: "var(--radius-md)" },
      spacing: { 4: "var(--space-4)" },
    },
  },
};
```

Gate: `bg-surface text-text` renders the light value with no theme attribute and the dark value with it.

## Stage 5 - Migrate components in one pass per token

5.1 Inventory the classes in use: `rg -o "(bg|text|border)-\[#[0-9a-fA-F]{3,8}\]" src | sort | uniq -c | sort -rn`.

5.2 Map each raw value to its nearest semantic token. Values within 2% lightness of an existing token map to it; do not create a token for a one-off.

5.3 Migrate one token per pull request. A 200-file PR mixing 12 tokens cannot be reviewed and will be reverted.

5.4 Delete the raw values from the code as you go, so the inventory shrinks and the remaining work is visible.

| Raw class | Semantic replacement | Why |
|---|---|---|
| `bg-[#f8fafc]` | `bg-surface` | the page background |
| `text-[#0f172a]` | `text-text` | primary copy |
| `text-[#64748b]` | `text-text-muted` | secondary copy |
| `border-[#e2e8f0]` | `border-border` | dividers |
| `bg-[#2563eb]` | `bg-accent` | primary action |

Gate: the inventory command returns 0 results, and `grep -c "dark:"` is 0 in migrated files.

## Stage 6 - Delete the dark: duplication

6.1 Every `dark:bg-gray-900` that exists only because the light class was hardcoded becomes unnecessary once the semantic token switches.

6.2 Keep `dark:` only for genuine layout differences between themes - an inverted image, a different shadow.

6.3 Verify by toggling the attribute with the CSS forced: remove the `dark:` variants, switch theme, and confirm nothing loses contrast.

6.4 Check contrast in both themes with a ratio, not by eye: 4.5:1 for body text, 3:1 for large text and UI borders.

| Element | Minimum ratio | Tool |
|---|---|---|
| body text | 4.5:1 | browser devtools contrast picker |
| large text (18px+) | 3:1 | same |
| input border | 3:1 | same |
| focus ring | 3:1 against adjacent colour | same |

Gate: zero contrast failures in both themes, checked on 10 representative components.

## Stage 7 - Enforce the tokens in CI

7.1 Add a lint rule that fails on arbitrary colour values: `(bg|text|border|ring)-\[#` inside `src/`.

7.2 Fail the build when `tokens.css` differs from a fresh generation. A hand-edited generated file is the failure this prevents.

7.3 Fail when a semantic token in `tokens.json` is unused for 30 days. Dead tokens accumulate and confuse the next reader.

7.4 Report the count of remaining raw values per PR, so migration progress is a number, not a feeling.

```bash
# CI guard: no arbitrary colours in components
if rg -q '(bg|text|border|ring)-\[#' src/; then
  echo "hardcoded colour found - use a semantic token"; exit 1
fi
# CI guard: generated css is current
node scripts/build-tokens.js
git diff --exit-code src/styles/tokens.css || { echo "tokens.css is stale"; exit 1; }
```

Gate: both guards run on every PR and fail on a deliberately introduced raw hex.

## Stage 8 - Hand the system to design

8.1 Publish the token list as a page: name, light value, dark value, and a swatch. Designers stop inventing values when the list is visible.

8.2 Map Figma variables to the same names, one to one. A mismatch between Figma names and code names costs a translation step on every handover.

8.3 Version the token file. A token rename is a breaking change and belongs in a minor version with a codemod.

8.4 Agree the process for a new token: who proposes, what evidence, and the maximum number of semantic tokens (usually 24-30).

| Token decision | Owner | Rule |
|---|---|---|
| new semantic token | design + frontend | must be used in 2+ places |
| rename | frontend | minor version plus codemod |
| dark value | design | contrast checked before merge |
| component token | frontend | maximum 10 in total |

Gate: the published token page matches the JSON exactly, checked by a script.

## Stage 9 - Test the theme switch

9.1 Test with 3 states: no attribute, `data-theme="dark"`, and system preference. The third is the one that breaks.

9.2 Assert in a component test that `bg-surface` resolves to different computed values in the two themes.

9.3 Check the first paint: a theme flash is caused by reading the preference after hydration. Set the attribute in an inline script in `<head>`.

9.4 Check images and charts. A chart with hardcoded series colours is the most common theme failure.

Gate: no flash on reload in either theme, and one chart renders with token colours in both.

## Worked example

A 140-component dashboard, before and after the token migration.

| Item | Before | After |
|---|---|---|
| Distinct raw hex values | 47 | 0 in components |
| Semantic tokens | 0 | 22 |
| `dark:` variants | 610 | 34 |
| Files touched for a colour change | 180 (estimated) | 1 (`tokens.json`) |
| Rebrand effort | 3 weeks | 2 hours plus review |
| CI guards | none | 2 |

The `dark:` count dropped 95% because most of those classes existed only to undo a hardcoded light colour. The 34 that remain are inverted logos and shadow adjustments.

## Quality checklist

- [ ] Three layers defined: primitive, semantic, component
- [ ] Components reference semantic tokens only
- [ ] Primitives named by scale, not appearance
- [ ] `tokens.json` is the single source, committed
- [ ] Non-colour tokens included: spacing, radius, shadow, z-index
- [ ] Generated CSS marked do-not-edit and diffed in CI
- [ ] `:root` and `[data-theme="dark"]` carry the two themes
- [ ] `color-scheme` set so native controls follow the theme
- [ ] Tailwind maps to `var(--token)`, not hex
- [ ] Default palette removed only after migration completes
- [ ] Migration done one token per pull request
- [ ] `dark:` duplication reduced, not multiplied
- [ ] Contrast checked at 4.5:1 body and 3:1 large text in both themes
- [ ] CI fails on arbitrary colour values in components
- [ ] CI fails when generated CSS is stale
- [ ] Theme applied in an inline head script, no flash

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Rebrand still touches 40 files | Components referencing primitives | Ban primitives outside the token file |
| Dark mode looks washed out | Dark values mapped to the same primitives | Define separate dark primitives for surfaces |
| Tailwind classes stopped working | Default palette replaced instead of extended | Migrate first, remove the palette later |
| Theme flashes on load | Preference read after hydration | Inline script in `<head>` sets the attribute |
| Charts stay light in dark mode | Series colours hardcoded in JS | Read the CSS variable at render time |
| Generated CSS edited by hand | No CI check on the diff | Regenerate and fail on any diff |
| 60 semantic tokens and nobody knows which to use | Tokens created per component | Cap at 24-30, require 2+ uses |
| Contrast failure found in review | Checked by eye | Measure 4.5:1 and 3:1 in both themes |
| Rename broke 30 files silently | Token renamed without a codemod | Minor version plus a codemod in the same PR |
| Two sources of truth | Figma names differ from code names | One-to-one mapping, published list |

## Copy-ready agent prompt

> Read the skill at the URL above and set up a token system for my Tailwind app. Ask me: the current colour usage, whether dark mode exists, and how many components I have. Then give me the three-layer `tokens.json` with primitives, semantic tokens and a capped component layer, a generation script that emits `:root` and `[data-theme="dark"]` CSS variables, the `tailwind.config.js` mapping to `var(--token)` with `darkMode` set to the selector, the `rg` inventory command and a raw-to-semantic mapping table for my actual values, the two CI guards that fail on arbitrary hex values and on stale generated CSS, and a migration plan of one token per pull request. Finish with the contrast checks and the no-flash head script. Tell me how many raw hex values remain after the first pass.
