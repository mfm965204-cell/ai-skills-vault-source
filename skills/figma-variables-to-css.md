---
name: figma-variables-to-css
description: Export Figma variables into the same JSON the frontend already uses, so design and code share one token file and handover stops being a translation job.
version: 1.0.0
license: MIT
tags: [design, figma, tokens, handover, css]
---

# Figma Variables To CSS

Design updates a colour in Figma and the frontend finds out at review, three weeks later, when someone notices the button is the old blue. The gap exists because design values live in a file nobody can diff and code values live in a stylesheet nobody in design opens.

This skill pulls Figma variables through the plugin API into a JSON token file, diffs it against the code's tokens on every build, and fails the PR when the two disagree. You end with a one-way pipeline: Figma is the source for primitives, code owns the semantic mapping, and a divergence is a build error rather than a comment.

## When to use this skill

- Design and code disagree on a hex value and neither side is sure which is current.
- You export a Figma file manually and paste hex values into a stylesheet every sprint.
- Your variables have modes (light/dark, brand A/brand B) that code does not model.
- A rebrand is coming and you want the value changes to arrive as a diff, not a document.

Do NOT use for: designing the system, choosing typography, or component behaviour. It is the pipeline between a Figma file and a token file, nothing more.

## Stage 1 - Audit the Figma variable structure first

1.1 List collections: usually `Primitives`, `Semantic`, and one collection per mode set (`Theme`, `Brand`, `Density`).

1.2 Check the naming convention. `color/surface/default` maps to `surface-default`; `Surface Default` does not map to anything stable.

1.3 Find variables that are aliases of other variables. Aliases become references in JSON, not duplicated hex values.

1.4 Find the orphans: variables used in no component and no style. Delete them before export, or they arrive as dead tokens in code.

| Figma shape | Token JSON shape | Note |
|---|---|---|
| `color/blue/600` | `primitive.blue-600` | literal value |
| `color/surface` alias `color/grey/50` | `semantic.surface = {primitive.grey-50}` | reference, not value |
| mode `Theme: Dark` | `semantic.surface.dark` | one override per mode |
| `spacing/4` | `space.4 = 16` | number, not string |

Gate: every variable maps to a token path or is deleted, and there are zero unnamed or orphan variables.

## Stage 2 - Choose the export route

2.1 Preferred: a Figma plugin (local or published) using the plugin API, run on demand, writing JSON to disk.

2.2 Alternative: the Figma REST API for variables, authenticated with a personal access token stored in the environment - never in the repo.

2.3 Last resort: a manual export from a paid tool, run monthly. It works until the first emergency colour change.

2.4 Whatever the route, the output is one JSON file in the repo, so the diff is reviewable and the history is in git.

| Route | Auth | Frequency | Failure mode |
|---|---|---|---|
| local plugin | none | per change | someone forgets to run it |
| REST API | token in env | nightly in CI | token expiry, rate limits |
| paid tool | licence | monthly | drifts between runs |

Gate: one documented command produces `tokens.figma.json` from the current Figma file.

## Stage 3 - Read variables through the plugin API

3.1 Get the local collections with `figma.variables.getLocalVariableCollectionsAsync()` and the variables with `figma.variables.getLocalVariablesAsync()`.

3.2 Resolve each variable per mode: `variable.valuesByMode[modeId]` returns either a literal or an alias `{type: "VARIABLE_ALIAS", id}`.

3.3 Convert to hex only at the last step, from the `r,g,b` floats, and clamp to 0-255. Skipping the clamp produces `rgb(256,0,0)`.

3.4 Write the JSON sorted by key, so an unchanged export produces an empty diff.

```js
// code.ts in the Figma plugin sandbox
const collections = await figma.variables.getLocalVariableCollectionsAsync();
const vars = await figma.variables.getLocalVariablesAsync();
const hex = (c) => "#" + [c.r, c.g, c.b].map(v =>
  Math.round(Math.min(1, Math.max(0, v)) * 255).toString(16).padStart(2, "0")).join("");

const out = { primitive: {}, semantic: {} };
for (const v of vars) {
  const path = v.name.toLowerCase().replace(/[/ ]+/g, "-");
  for (const modeId of Object.keys(v.valuesByMode)) {
    const val = v.valuesByMode[modeId];
    out.primitive[path] = typeof val === "object" ? val.id : hex(val);
  }
}
figma.showUI(__html__, { width: 320, height: 200 });
```

3.5 Emit numbers for spacing, radius and font size as numbers, not strings. A string `"16"` breaks arithmetic in the generator.

Gate: the export is deterministic - running it twice on an unchanged file produces byte-identical output.

## Stage 4 - Map Figma names to code names once

4.1 Keep an explicit mapping file, `token-map.json`, from Figma path to code path. Automatic transformation covers 90% and the remaining 10% is where bugs live.

4.2 Do not rename tokens in code to match Figma if that breaks consumers. Map instead, and rename in a versioned migration later.

4.3 Fail the build when a Figma variable has no mapping and no `ignore` entry. A silent skip is how a new colour disappears.

4.4 Record the reason for each ignore: `"color/debug/outline": "internal to design only"`.

| Figma path | Code token | Rule |
|---|---|---|
| `color/surface` | `surface` | direct |
| `color/text/muted` | `text-muted` | direct with hyphen |
| `color/brand/primary` | `accent` | renamed, mapped explicitly |
| `color/debug/outline` | ignored | design-only |

Gate: every Figma variable is either mapped or explicitly ignored, enforced by the build.

## Stage 5 - Generate CSS from the merged tokens

5.1 Merge order: Figma primitives, then code-owned semantic mapping, then code-owned component tokens. Code owns meaning; Figma owns values.

5.2 Emit `:root` for the base mode and one selector per additional mode: `[data-theme="dark"]`, `[data-brand="b"]`.

5.3 Emit only semantic tokens to CSS. Primitives stay in JSON so nobody uses `--blue-600` in a component.

5.4 Write a header with the source file version, the export timestamp and a do-not-edit line.

```css
/* generated from tokens.figma.json v14 on 2026-11-15 - do not edit */
:root {
  --surface: #f8fafc;
  --text: #0f172a;
  --text-muted: #64748b;
  --accent: #2563eb;
}
[data-theme="dark"] {
  --surface: #0f172a;
  --text: #f8fafc;
  --accent: #60a5fa;
}
```

Gate: a mode switch changes every surface and text token with no class changes.

## Stage 6 - Diff Figma against code on every build

6.1 Compare the generated CSS with the committed CSS. Any difference fails the build with the changed token names, not a wall of diff.

6.2 Report three categories separately: added, changed, removed. A removed token is a breaking change and needs a migration note.

6.3 Keep the last exported JSON in the repo so a reviewer sees the value change and its source.

6.4 Allow an escape hatch for one release: a `token-drift-allow` file with an expiry date, so a mid-sprint change can land deliberately.

```bash
node scripts/export-figma.js --out tokens.figma.json
node scripts/build-css.js --in tokens.figma.json --out src/styles/tokens.css
if ! git diff --quiet src/styles/tokens.css; then
  echo "token drift detected - commit the regenerated tokens.css"
  git diff --unified=0 src/styles/tokens.css | grep -E '^[+-]\s+--' || true
  exit 1
fi
```

Gate: an intentional Figma change fails the build once, then passes after the regenerated CSS is committed.

## Stage 7 - Handle a rename without breaking consumers

7.1 A rename is two steps: add the new token alongside the old, then remove the old after one release.

7.2 Keep the alias in CSS (`--new-name: var(--old-name)`) for exactly one version, then delete both the alias and the old name.

7.3 Write a codemod for the class rename. Ten minutes of codemod beats a 40-file manual edit with 4 missed files.

7.4 Announce the rename in the changelog with the version it lands in.

| Step | Change | Consumer impact |
|---|---|---|
| 1 | add new token, old still present | none |
| 2 | codemod classes to new token | none |
| 3 | deprecate old token in docs | warning |
| 4 | remove old token | breaking, next major |

Gate: no consumer references a removed token, verified by the inventory command.

## Stage 8 - Keep design and code in the same room

8.1 Agree who owns what: design owns primitive values and modes, code owns semantic names and component tokens.

8.2 Publish the token list with a swatch per token, generated from the JSON. A designer should never need to open the repo.

8.3 Review Figma changes that alter values in a short weekly pass, not per edit. Ten small changes reviewed together cost less than ten interruptions.

8.4 Put the token count on a dashboard. A number that only grows means nobody is deleting anything.

Gate: the published token page is generated from the same JSON, and the counts match.

## Stage 9 - Test the modes, not just the default

9.1 For each mode, screenshot 5 representative components: button, input, card, table row, alert.

9.2 Check contrast per mode: 4.5:1 body text, 3:1 large text and borders.

9.3 Check that a component built only from tokens changes correctly, and that a component with a hardcoded colour is flagged by the lint rule.

9.4 Run the check in CI on a preview build so a broken mode never reaches production.

Gate: 5 components, every mode, contrast measured, screenshots stored.

## Worked example

A 60-component product with 2 themes and 2 brands, migrating to a Figma-driven pipeline.

| Item | Before | After |
|---|---|---|
| Token source | Figma file plus a stylesheet | `tokens.figma.json` |
| Handover | screenshot plus a list of hex values | one JSON diff |
| Colour changes per quarter | 14 | 22 |
| Time per change | 2-3 days | 30 minutes |
| Drift incidents | 6 in a quarter | 1, caught in CI |
| Modes modelled in code | 1 | 4 |
| Dead tokens | 38 | 4 |

The drift incidents dropped because the build now fails on a difference, which converts a discovery in review into a failure at push time.

## Quality checklist

- [ ] Collections, modes and naming audited before export
- [ ] Orphan variables deleted, not exported
- [ ] Export route documented as one command
- [ ] Values read per mode, aliases preserved as references
- [ ] Hex conversion clamped to 0-255
- [ ] Export is deterministic, byte-identical on re-run
- [ ] Numbers emitted as numbers, not strings
- [ ] Explicit map from Figma path to code token
- [ ] Unmapped and unignored variables fail the build
- [ ] Code owns semantic names, Figma owns primitive values
- [ ] Only semantic tokens emitted to CSS
- [ ] Generated CSS carries version, timestamp and do-not-edit
- [ ] CI diff reports added, changed and removed separately
- [ ] Renames done as add, migrate, deprecate, remove
- [ ] Contrast checked in every mode, not just the default
- [ ] Token count tracked so dead tokens are visible

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Colour changed in code, not in Figma | Two sources of truth | Figma owns primitives, CI enforces the diff |
| Export produces a diff on every run | Unordered keys or float noise | Sort keys, round before writing |
| `rgb(256,0,0)` in the output | Float values not clamped | Clamp 0-1 before multiplying by 255 |
| New Figma colour never reaches code | Unmapped variable silently skipped | Fail on unmapped and unignored |
| Component broke after a rename | Old token removed in the same release | Add, migrate, deprecate, remove |
| Mode looks wrong only in production | Modes tested on the default only | Screenshot 5 components per mode in CI |
| Designer cannot see current tokens | Token list maintained by hand | Generate the page from the same JSON |
| Token file grows every sprint | No deletion policy | Track count, review orphans monthly |
| API export fails nightly | Expired personal access token | Rotate the token, alert on auth failure |
| Diff unreadable in review | Full stylesheet diff | Report added, changed, removed only |

## Copy-ready agent prompt

> Read the skill at the URL above and set up a Figma-to-CSS token pipeline. Ask me: how my Figma variables are named, which collections and modes exist, whether I can run a plugin or must use the REST API, and where my CSS tokens currently live. Then give me the plugin code that reads local variables per mode and writes a sorted `tokens.figma.json` with clamped hex values and alias references, the explicit `token-map.json` with ignore reasons, the generator that emits `:root` and one selector per mode with semantic tokens only, and the CI step that fails on drift and prints added, changed and removed tokens separately. Include the rename sequence and the per-mode contrast and screenshot checks. Tell me which of my current variables are orphans or unmapped.
