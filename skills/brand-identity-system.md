---
name: brand-identity-system
description: Build a complete, usable brand identity - positioning, name check, logo system, colour, type, spacing, voice, asset kit and a one-page guideline that a team can actually follow.
version: 1.0.0
license: MIT
tags: [branding, design, logo, typography, identity, guidelines]
---

# Brand Identity System

A logo is one file. A brand is a system of decisions that make every future asset look like it came from the same place.

## When to use this skill

- Naming and branding a new product or company.
- Rebranding something that looks improvised.
- Producing a guideline so contractors stop inventing colours.
- Building a personal or creator brand.

## Stage 1 - Positioning before visuals

Fill in and sharpen:

> **[Brand]** is a **[category]** for **[audience]** who **[situation]**. Unlike **[alternative]**, we **[differentiator]** because **[proof]**.

Then three attributes, each a single adjective with a consequence: "Precise" means tight grid, few colours, mono numerals. "Warm" means rounded corners, human photography, generous whitespace. If an attribute has no visual consequence, it is decoration.

Also decide the **anti-brand**: three things you will never look like. This prevents drift better than any mood board.

## Stage 2 - Naming (if needed)

1. Generate 40 candidates across four buckets: descriptive, evocative, invented, compound.
2. Filter for: pronounceable in one try, spellable after hearing it once, under 3 syllables, no negative meaning in the target languages (check Hindi, Tamil, Bengali transliterations if selling in India).
3. Check domain (`.com`, `.in`, `.ai`), handle availability on the two platforms you will actually use, trademark database (ipindia.gov.in / USPTO), and a plain web search for conflicts.
4. Test with 5 strangers: "What do you think this company does?" A name that needs explaining is a name you will explain forever.
5. Never launch on a name you have not searched. Rebranding after a cease-and-desist costs 50x more than the search.

## Stage 3 - Logo system

Build three tiers, not one file:

1. **Primary lockup** - mark + wordmark, horizontal.
2. **Stacked lockup** - for square and vertical placements.
3. **Mark alone** - favicon, app icon, avatar, embroidery.

Rules: design in one colour first (it must work in pure black at 16 px). Then add colour. Then check it at 16, 32, 64, 256 px. A mark that dies at 32 px is a mark for a poster, not a product.

Clear space: the height of the mark's counter, on all sides. Minimum sizes: 24 px digital for the mark, 96 px for the lockup. State them.

Deliver as SVG (all tiers), plus PNG at 512/1024, favicon set, and a monochrome variant.

## Stage 4 - Colour

- **One primary**, one accent, 3-4 neutrals. That is the whole palette. More colours is not a brand, it is indecision.
- Build the primary at 9 steps (50-900) so UI has hover, pressed and disabled states without inventing shades.
- Check contrast: body text 4.5:1, large text and UI 3:1. Verify every text-on-colour pairing you intend to ship.
- Test the palette in greyscale - if the hierarchy disappears, the palette is doing work that layout should do.
- Give every colour a name and a hex, and forbid "close enough" variants.

## Stage 5 - Typography

- Two families maximum: one display (personality), one text (legibility). A single family in multiple weights is a legitimate and often better choice.
- Licence check: Google Fonts (free), Fontshare (free), or a paid licence with the correct web/desktop scope. Never ship a desktop-licensed font as a webfont.
- Set the scale: 12 / 14 / 16 / 20 / 24 / 32 / 40 / 56, line heights 1.2 display and 1.5 body, tracking -2% at display sizes.
- Specify fallbacks so the brand survives a blocked font load: `"Inter", -apple-system, Segoe UI, Roboto, sans-serif`.

## Stage 6 - Voice

Write five rules with a good/bad example each. Example set:

1. Short sentences. "It works offline." Not "Our solution enables offline functionality."
2. Say the number. "Saves 4 hours a week", not "saves time".
3. Second person. Address the reader as "you".
4. No hype words: revolutionary, seamless, cutting-edge, world-class, empower.
5. One idea per paragraph. If a sentence needs a second comma clause to survive, split it.

Plus a banned-words list and a capitalisation rule (sentence case almost always).

## Stage 7 - Asset kit

Produce, in one folder: logo tiers (SVG + PNG), favicon set, app icon, colour tokens as CSS variables and a JSON, font files with the licence text, 3 social templates (square, 9:16, 16:9), email signature, presentation cover, and a document header.

Every template must be editable by a non-designer. If it needs Figma skills to change a headline, it is not an asset, it is a hostage.

## Stage 8 - The one-page guideline

Exactly one page: logo usage and clear space, the palette with hex, the type scale with two examples, the five voice rules, the anti-brand list, and where the files live. Anything longer is not read.

## Quality checklist

- [ ] Positioning sentence written before visuals
- [ ] Mark works in one colour at 16 px
- [ ] Clear space and minimum sizes stated
- [ ] Palette limited and contrast-verified
- [ ] Fonts licensed for web and desktop
- [ ] Voice rules have good/bad examples
- [ ] Templates editable by a non-designer
- [ ] Guideline is one page
- [ ] Every file named consistently and versioned

## Copy-ready agent prompt

> Read the skill at the URL above. Ask me the positioning inputs, the three attributes and the anti-brand. Then propose three distinct directions (each with a rationale tied to an attribute), build out the chosen one into a full system - logo tiers, colour ramp with contrast checks, type scale, voice rules with examples - and output the CSS token file, the asset list and the one-page guideline. Do not use a word from the banned list in any of the copy.
