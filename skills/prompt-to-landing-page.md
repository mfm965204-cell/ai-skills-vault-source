---
name: prompt-to-landing-page
description: Turn a one-line product idea into a complete, conversion-optimised landing page - positioning, copy, design system, sections, proof, CTA, SEO and performance - shipped as a single deployable file.
version: 1.0.0
license: MIT
tags: [landing-page, copywriting, conversion, html, marketing, cro]
---

# Prompt To Landing Page

One prompt in, one deployed landing page out. This skill covers the thinking that makes pages convert, not just the markup.

## When to use this skill

- Launching a product, waitlist, app, service or event and needing a page today.
- Replacing a weak page that gets traffic but no signups.
- Producing several landing variants for an ad test.

## Stage 1 - Extract the brief (ask only what you cannot infer)

1. What is it, in one sentence a stranger understands?
2. Who exactly is it for - role, situation, current workaround?
3. What action counts as success: signup, purchase, call booked, download?
4. What is the single strongest proof? (number, customer, demo, guarantee)
5. Price or pricing model, if shown.
6. Brand: colours, font, logo, tone.
7. Traffic source: cold ads, SEO, referral, email list. Cold traffic needs more proof; warm traffic needs less explanation.

Missing answers become explicit assumptions listed at the top of the page source as an HTML comment.

## Stage 2 - Positioning before copy

Fill this sentence and do not write a word until it is sharp:

> For **[specific person]** who **[specific painful situation]**, **[product]** is a **[category]** that **[single differentiated outcome]**, unlike **[the alternative they use today]**.

Weak: "AI-powered productivity platform for teams."
Strong: "For freelance designers who lose 6 hours a week chasing invoices, Ledgerly is a one-tap invoice chaser that gets you paid 11 days faster - unlike spreadsheets and polite reminder emails."

The differentiation must be a claim you can prove on the page.

## Stage 3 - Page architecture (in this order)

1. **Hero** - headline, subhead, primary CTA, one visual, one trust line. Above the fold on a 390x844 phone.
2. **Problem** - three specific pains in the customer's own words.
3. **How it works** - three steps, each a verb, each with a visual.
4. **Features as outcomes** - not "AI engine", but "Answers in 4 seconds, not 4 days".
5. **Proof** - logos, numbers, testimonials with name + role + photo, screenshots, case snippet.
6. **Objection handling / FAQ** - the 5 real reasons people do not buy: price, trust, effort, switching cost, "will it work for me".
7. **Pricing** (if applicable) - 2-3 tiers, one recommended, annual/monthly toggle, what is included, guarantee.
8. **Final CTA** - restate the outcome, remove risk, one button.
9. **Footer** - contact, privacy, terms, social.

Total: 7-10 sections. Long pages are fine if every section earns its scroll.

## Stage 4 - Copy rules

- Headline: outcome + specificity, under 10 words. Test it by asking "would a competitor be unable to say this?"
- Subhead: how it works in one line, under 25 words.
- CTA button: verb + object. "Start free trial" beats "Submit". One primary CTA repeated 3-4 times down the page, identical wording.
- Body: second person, present tense, active voice. Short sentences. No "revolutionary", "seamless", "cutting-edge", "empower".
- Numbers beat adjectives: "11 days faster", "4,200 invoices", "under 3 minutes".
- Every section answers: so what? and what do I do next?

## Stage 5 - Design system in 20 lines

```css
:root{
  --bg:#0A0A0C; --surface:#14141A; --text:#F4F4F6; --muted:#A0A0AE;
  --brand:#5B5BF5; --brand-2:#8B5CF6; --accent:#22D3A6;
  --radius:14px; --maxw:1120px;
  --fs-h1:clamp(2.1rem,6vw,4rem); --fs-h2:clamp(1.5rem,3.5vw,2.4rem);
  --fs-body:1.0625rem; --lh:1.55;
}
```

Layout rules: 1120 px max width, 24 px side padding on mobile, section padding `clamp(56px,9vw,120px)`, 8 px spacing scale, one accent colour used only for CTAs and highlights, no more than two font families, headline weight 700+ with tight tracking.

Visual hierarchy rule: exactly one element per screen should be the loudest. If everything is bold, nothing is.

## Stage 6 - Mobile-first build

- Design at 390 px first; check 320 px for no horizontal scroll.
- Hero must show headline + CTA without scrolling.
- Buttons: 48 px min height, full width on mobile.
- Sticky bottom CTA bar on mobile after 40% scroll.
- Font size 16 px minimum on inputs (stops iOS zoom).
- Tap targets 44 px, 8 px apart.

## Stage 7 - Conversion mechanics

- Form: fewest possible fields. Email only beats name+email+company by 20-40% in most tests. Show a privacy line under the button.
- Above the fold: outcome + who it is for + CTA + one proof element.
- Reduce risk: free tier, no card, cancel anytime, money-back, "2-minute setup".
- Social proof placement: one logo strip directly under the hero, testimonials beside each claim they support.
- Friction log: list every click and every field; cut the ones that do not increase trust.
- Add a secondary CTA for the not-ready: "See a 2-minute demo" instead of nothing.

## Stage 8 - SEO and metadata

```html
<title>Primary keyword + outcome (under 60 chars)</title>
<meta name="description" content="Benefit + proof + CTA, 150-160 chars">
<meta property="og:title" content="..."><meta property="og:image" content="1200x630">
<link rel="canonical" href="https://example.com/">
```

Plus: one `h1`, ordered `h2`s, descriptive alt text, JSON-LD (`Organization`, `Product` or `FAQPage`), sitemap, favicon set, `lang` attribute.

## Stage 9 - Performance

Single self-contained HTML file where possible: inline critical CSS, no framework, system fonts or one preloaded variable font, images as WebP/AVIF with `width`/`height`, `loading="lazy"` below the fold, total page under 500 KB, LCP under 2 s on 4G.

## Stage 10 - Ship and measure

Deploy, then verify: no console errors, links resolve, form posts and confirms, 404 page, analytics event on CTA click, mobile Lighthouse 90+. Set up one conversion event before sending traffic - a page you cannot measure is a page you cannot improve.

## Quality checklist

- [ ] Positioning sentence written before copy
- [ ] Hero passes the 5-second test with a stranger
- [ ] One CTA wording, repeated, one accent colour
- [ ] Real proof, no invented testimonials or logos
- [ ] Every objection in the FAQ is one a buyer actually has
- [ ] Mobile: CTA above fold, no horizontal scroll, 48 px buttons
- [ ] Meta tags, OG image, JSON-LD present
- [ ] Page weight under 500 KB

## Copy-ready agent prompt

> Read the skill at the URL above and follow all 10 stages. Ask me the 7 brief questions in one message. Write the positioning sentence and show it to me before any copy. Then produce a single self-contained `index.html` with inline CSS, real copy (no lorem ipsum), mobile-first layout, meta tags and JSON-LD. End with the quality checklist filled in honestly.
