---
name: dark-mode-palette
description: Build a dark theme that passes contrast - separate surface tiers, desaturated accents, image and chart handling, and a token set that swaps without a second stylesheet.
version: 1.0.0
license: MIT
tags: [design, dark-mode, accessibility, colour, tokens]
---

# Dark Mode Palette

Dark mode is not an inverted light theme. Invert a light palette and you get pure white text on pure black, which vibrates on OLED, halos around every glyph, saturated accent colours that glow, and shadows that do nothing because black on black has no depth.

This skill builds a dark theme from the surface up: three or four surface tiers instead of one, text at 87-100% opacity rather than pure white, accents desaturated and lightened to hold contrast, elevation expressed as lighter surfaces rather than shadow, and images and charts handled explicitly. It ends with a token set that swaps by attribute, so the codebase has one stylesheet and two palettes.

The number that decides every choice: contrast ratio. Body text at 4.5:1 minimum, large text at 3:1, and a target of 7:1 for the text people read longest.

## When to use this skill

- You are adding a dark theme to an existing light product.
- The dark theme exists but text looks blurry, accents glow, or shadows are invisible.
- Charts and images look broken when the theme switches.
- You need one token set that supports both themes without duplicating styles.
- **Do NOT use for:** choosing a brand palette, building a design token pipeline from a design tool, or light-theme accessibility work - this covers the dark palette and its swap mechanism.

## Stage 1 - Audit the light palette before translating it

You cannot translate a palette you have not measured. Half of a light theme's colours exist only to fix contrast problems that disappear in the dark.

1.1 List every colour in the light theme with its role: surface, surface-raised, text, muted text, border, accent, danger, success, warning.

1.2 Measure the contrast of each text-on-surface pair in the light theme and record the ratio.

1.3 Identify colours that exist only as decoration - the ones with no role - and delete them before translating.

1.4 Identify the brand colours that must stay recognisable, and note their exact hex.

1.5 Count how many colours the product actually uses; more than 30 means the palette needs pruning first.

1.6 Write the role list down; the dark palette is built per role, not per hex.

| Role | Light value | Dark value | Contrast target |
|---|---|---|---|
| Page surface | #FFFFFF | #121212 | - |
| Raised surface | #F8FAFC | #1E1E1E | - |
| Body text | #0F172A | #E6E6E6 | 7:1 |
| Muted text | #64748B | #A1A1AA | 4.5:1 |
| Border | #E2E8F0 | #2E2E2E | 3:1 vs surface |
| Accent | #2563EB | #7AA2F7 | 4.5:1 on surface |
| Danger | #DC2626 | #F87171 | 4.5:1 on surface |

Gate: every colour has a role, and the light theme's contrast ratios are recorded as the baseline.

## Stage 2 - Build surface tiers before choosing any text colour

Dark interfaces need depth, and depth comes from surfaces that get lighter as they come forward. Pure black leaves no room to go up.

2.1 Set the page surface to a very dark grey, not pure black - around #121212 - so elevation has somewhere to go.

2.2 Add two or three raised tiers, each 4-8% lighter than the one below.

2.3 Use surfaces for elevation instead of shadows; shadows are invisible on dark backgrounds.

2.4 Keep one shadow token for overlays only, at higher opacity and a larger blur than in light mode.

2.5 Set borders one step lighter than their surface, not darker - a darker border disappears.

2.6 Check the tiers on an OLED screen in a dark room, where banding is most visible.

```css
:root[data-theme="dark"] {
  --surface-0: #121212;   /* page */
  --surface-1: #1a1a1a;   /* cards */
  --surface-2: #222222;   /* menus, popovers */
  --surface-3: #2a2a2a;   /* modals */
  --border-subtle: #2e2e2e;
  --shadow-overlay: 0 8px 32px rgba(0, 0, 0, 0.72);
}
```

Gate: at least three surface tiers exist, each visibly distinct on an OLED screen, with no pure black page.

## Stage 3 - Set text colours by opacity and role

Pure white on dark vibrates and haloes. Use off-white and reduce opacity by hierarchy rather than inventing greys.

3.1 Set primary text to #E6E6E6 or white at 87% opacity, never #FFFFFF at 100%.

3.2 Set secondary text at about 70% and disabled text at about 38% of the same base colour.

3.3 Keep the text base one colour and vary opacity, so the hierarchy stays consistent across surfaces.

3.4 Raise text opacity on raised surfaces, because a lighter background reduces perceived contrast.

3.5 Never use opacity for text over an image or a gradient; use a solid colour from a scrim.

3.6 Check the lowest-opacity text you ship - a 38% disabled label still needs to be legible enough to read once.

Gate: body text measures at least 7:1 on its surface, and muted text at least 4.5:1.

## Stage 4 - Desaturate and lighten the accents

A saturated accent that works on white glows on dark. Every accent needs its own dark value, not the light one reused.

4.1 Take each accent and reduce saturation by roughly 10-20 points in HSL.

4.2 Lighten the accent so it holds 4.5:1 against the surface it sits on.

4.3 Keep the hue close to the brand's; a shift of more than 10 degrees reads as a different brand.

4.4 Create a pressed and a hover variant per accent, each a step in lightness rather than opacity.

4.5 For accent-filled buttons, check the label contrast against the accent fill, not the page.

4.6 Check colour-blind separation: danger and success must differ in lightness, not only in hue.

| Accent | Light | Dark | Why |
|---|---|---|---|
| Primary | #2563EB | #7AA2F7 | Lighter and less saturated, holds 4.5:1 |
| Success | #16A34A | #4ADE80 | Lightness gap from danger |
| Danger | #DC2626 | #F87171 | Distinguishable without hue |
| Warning | #D97706 | #FBBF24 | Legible on dark surfaces |

Gate: every accent has a dark value with 4.5:1 on its surface and a lightness gap from its neighbours.

## Stage 5 - Handle images, charts and code blocks

The parts that break most often are the ones nobody thinks of as colour: photographs, charts and code.

5.1 Dim large photographs slightly - 5-10% brightness reduction - so they do not glare against a dark page.

5.2 Do not invert or dim product images, logos or anything where colour is information.

5.3 Give charts their own dark palette: gridlines at low opacity, axis labels at the muted text colour.

5.4 Rebuild series colours for the dark surface rather than reusing the light ones; a light-theme series palette usually fails contrast.

5.5 Use a dark syntax-highlighting theme for code blocks and check the comment colour, which is the usual contrast failure.

5.6 Provide a light-background frame for images with transparency, so a logo does not vanish on a dark card.

```css
:root[data-theme="dark"] img:not(.no-dim) { filter: brightness(0.9); }
:root[data-theme="dark"] .logo { filter: none; background: var(--surface-2); padding: 8px; border-radius: 8px; }
:root[data-theme="dark"] .chart-grid line { stroke: rgba(255, 255, 255, 0.08); }
:root[data-theme="dark"] .chart-axis text { fill: var(--text-muted); }
```

Gate: photographs, logos and charts each have a stated dark-mode treatment, and none is inverted blindly.

## Stage 6 - Swap by attribute, not by a second stylesheet

Two stylesheets drift. One token set with two values and an attribute switch cannot drift.

6.1 Define every colour as a semantic token, never a raw hex, in the components.

6.2 Set the light values on `:root` and override them under `[data-theme="dark"]`.

6.3 Switch the attribute on the `html` element, so nothing below needs to know about the theme.

6.4 Respect `prefers-color-scheme` for the default, and let an explicit user choice override it and persist.

6.5 Set `color-scheme: dark` on the root so native form controls and scrollbars follow.

6.6 Check that no component reads a raw hex from a design tool export; one hardcoded colour breaks the swap.

```css
:root { color-scheme: light dark; --surface-0: #ffffff; --text-primary: #0f172a; }
:root[data-theme="dark"] { color-scheme: dark; --surface-0: #121212; --text-primary: #e6e6e6; }

/* components never reference a hex */
.card { background: var(--surface-1); color: var(--text-primary); }
```

Gate: no component contains a raw colour value, and switching the attribute changes every surface.

## Stage 7 - Test contrast systematically, not by eye

Every pair must be measured. Eyeballing dark themes is unreliable because perceived contrast changes with ambient light and screen type.

7.1 Write every foreground-background pair the product can produce into a table, and measure each.

7.2 Fail the build on a body-text pair below 4.5:1 and a large-text pair below 3:1.

7.3 Test the four states per pair: default, hover, focus and disabled.

7.4 Test on a real OLED phone at low brightness, where dark themes are most used.

7.5 Check the focus ring against every surface tier; a ring that disappears on one tier is an accessibility bug.

7.6 Test with a colour-blindness simulation for danger, success and warning against surfaces.

| Pair | Surface | Measured | Required |
|---|---|---|---|
| Body text / page | surface-0 | 12.6:1 | 4.5:1 |
| Muted text / card | surface-1 | 5.4:1 | 4.5:1 |
| Accent / card | surface-1 | 5.1:1 | 4.5:1 |
| Border / page | surface-0 | 1.6:1 | 1.4:1 (non-text) |
| Focus ring / page | surface-0 | 4.8:1 | 3:1 |

Gate: every pair is measured and recorded, and the build fails below the thresholds.

## Stage 8 - Ship with a preference, a default and a flash guard

The theme switch fails in the first 200 milliseconds: a light flash before the dark theme applies, on every page load.

8.1 Read the stored preference in an inline script in the head, before any stylesheet paints.

8.2 Fall back to `prefers-color-scheme` when there is no stored preference.

8.3 Set the attribute on `html` in that script, so the first paint is already correct.

8.4 Persist the user's explicit choice separately from the system preference, and never overwrite it on a system change.

8.5 Give the toggle three states - system, light, dark - not two, so the user can return to following the system.

8.6 Announce the theme change politely for screen readers, without stealing focus.

```html
<script>
  (function () {
    var stored = localStorage.getItem("theme");
    var system = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    document.documentElement.dataset.theme = stored || system;
  })();
</script>
```

Gate: no light flash on reload in dark mode, and the three-state toggle persists correctly.

## Stage 9 - Document the palette and keep it honest

A dark palette decays when a new component ships with a raw hex. Make the rules visible and enforced.

9.1 Publish the token table with roles, values and measured contrast ratios.

9.2 Document the rules: no pure black, no pure white, no raw hex in components, accents desaturated.

9.3 Add a lint rule or a review checklist item that fails on a raw colour literal in a component.

9.4 Re-measure the pairs whenever a token changes, in the same pull request.

9.5 Keep the light and dark values side by side in one file, so a change to one is visibly a change to a pair.

9.6 Review the palette when a new surface tier or accent is added, since both need a dark value.

Gate: the token table is published with ratios, and a lint or review rule blocks raw colour literals.

## Quality checklist

- [ ] Every colour in the light theme has a named role.
- [ ] Light-theme contrast ratios are recorded as the baseline.
- [ ] At least three dark surface tiers exist and are distinct on OLED.
- [ ] The page surface is not pure black.
- [ ] Elevation uses lighter surfaces, not shadows.
- [ ] Body text is off-white, not pure white.
- [ ] Text hierarchy uses opacity on one base colour.
- [ ] Body text measures at least 7:1 on its surface.
- [ ] Every accent has a desaturated, lightened dark value.
- [ ] Danger and success differ in lightness, not only hue.
- [ ] Photographs, logos and charts each have a stated treatment.
- [ ] Components contain no raw hex values.
- [ ] The theme swaps by attribute on the html element.
- [ ] Contrast is measured for default, hover, focus and disabled states.
- [ ] No light flash appears on reload in dark mode.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Text looks like it is glowing | Pure white at 100% on a dark surface | Use #E6E6E6 or 87% opacity |
| Cards float with no depth | Shadows used for elevation on a dark background | Use lighter surface tiers instead |
| Accents look neon | Light-theme saturated values reused on dark | Desaturate 10-20 points and lighten to 4.5:1 |
| White flash on every reload | Theme applied by JavaScript after first paint | Set the attribute in an inline head script |
| Logo disappears on a dark card | Transparent PNG on a dark surface | Give images a light frame or leave them undimmed |
| One component stays light | A raw hex in that component instead of a token | Replace with a semantic token and lint for raw hex |

## Copy-ready agent prompt

> Read the skill at the URL above and build a dark theme for my product. Ask me for my current palette with its roles and brand colours, then produce surface tiers, text colours by opacity, desaturated dark values for every accent with measured contrast, treatments for images, charts and code blocks, and a token set that swaps by a data attribute on the html element. Give me the inline head script that prevents the light flash, a three-state toggle, and a contrast table for every foreground-background pair with default, hover, focus and disabled states. Flag any pair below 4.5:1 and do not invent a colour without a measured ratio.
