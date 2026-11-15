---
name: i18n-localization-pass
description: Take a working web app to a second language properly - extract every string, use ICU plurals, handle RTL and locale formats, and ship without hardcoded English.
version: 1.0.0
license: MIT
tags: [frontend, i18n, localization, react, accessibility]
---

# i18n Localization Pass

Adding a second language is not a translation task, it is a refactor. Strings are scattered across components, dates are formatted with `toLocaleDateString()` and no locale, currency is a rupee sign glued to a number, and one sentence assumes English plurals. Translation arrives, and the layout breaks because German is 30% longer and Hindi is not.

This skill does the engineering part: extract every user-visible string into message files, replace concatenation with ICU message syntax, handle right-to-left layout and locale-aware numbers, dates and currency, and add a pseudo-locale that proves the coverage before a translator is paid. It ends with a build that fails when an untranslated string reaches production.

The test of a finished pass: switch the locale and nothing is in English except the brand name, and no layout overflows.

## When to use this skill

- You are launching in a second language and the app has strings inside JSX.
- A translator returned files and half the UI is still English.
- Plurals read wrong in a language with more than two forms.
- An Arabic or Urdu build has broken alignment and numbers in the wrong direction.
- **Do NOT use for:** writing the translations themselves, marketing copy localisation, or backend-only locale handling - this covers the client-side pass and its checks.

## Stage 1 - Inventory every user-visible string

You cannot translate what you cannot find. Before choosing a library, count the strings and the places they live.

1.1 Search the codebase for text nodes in components, `placeholder`, `title`, `aria-label`, `alt` and validation messages.

1.2 Count matches per area - screens, forms, errors, emails - so the work is scoped, not estimated.

1.3 List the strings that are concatenated, templated or built with `+`, because those break in every language with different word order.

1.4 List the dynamic values that need formatting: dates, times, numbers, currency, percentages, file sizes.

1.5 Note strings that must not be translated: brand names, product codes, API error codes shown raw.

1.6 Write the count into the plan: "412 strings, 38 concatenated, 26 formatted values".

```bash
rg -n --glob '*.{tsx,jsx,ts,js}' '>[A-Z][a-z]|placeholder=|aria-label=|title=' src | wc -l
rg -n 'toLocale(Date|Time)?String\(\)|toFixed\(|₹' src | wc -l
```

Gate: a string count, a concatenation list and a formatted-value list exist before any library is installed.

## Stage 2 - Choose the library and the message format by constraint

The library choice is decided by framework, by whether translators can use a CAT tool, and by ICU support. Not by stars.

2.1 If the framework is React or Next.js, use a message library that supports ICU syntax and lazy loading per locale.

2.2 Confirm the format is JSON with ICU placeholders, because translators' tools parse ICU and choke on ad-hoc templates.

2.3 Check plural support: languages such as Hindi, Marathi and Bengali use two forms; Arabic uses six; Russian uses four.

2.4 Check that the library can load a locale bundle on demand, so the second language does not double the first paint.

2.5 Check the fallback behaviour: a missing key should fall back to the default locale and log, never render the raw key.

2.6 Write the decision and the rejected alternative into the repository's docs.

| Constraint | Choice | Why |
|---|---|---|
| ICU plurals and gender | ICU message format | One syntax translators' tools parse |
| Bundle size matters | Per-locale lazy loading | Second language does not grow first paint |
| Many small screens | Namespaced files per screen | Translators see context, not 900 keys |
| Server-rendered pages | Locale in the route prefix | Cacheable and crawlable per language |

Gate: the library, the format and the fallback rule are written down with the rejected alternative.

## Stage 3 - Extract strings without changing behaviour

Extraction is mechanical and must not alter the UI. Move strings out, keep the rendered output identical, and verify with a screenshot diff.

3.1 Create one message file per locale per namespace: `locales/en/common.json`, `locales/en/checkout.json`.

3.2 Key by meaning, not by English text: `checkout.submit`, not `checkout.submit_your_order_now`.

3.3 Replace text nodes with the translation call, one screen per commit, so a regression is easy to isolate.

3.4 Keep whitespace and punctuation inside the message, never beside the call, or translators cannot see them.

3.5 Run the app in the default locale after each screen and confirm the output is byte-identical.

3.6 Delete the old literals in the same commit - leaving them invites someone to re-add one.

```json
{
  "cart": {
    "items": "{count, plural, =0 {Your cart is empty} one {# item in your cart} other {# items in your cart}}",
    "total": "Total: {amount, number, ::currency/INR}",
    "deliveryBy": "Delivery by {date, date, ::EEE, d MMM}"
  }
}
```

Gate: the default-locale output is unchanged and no hardcoded user-visible string remains in the touched screens.

## Stage 4 - Replace concatenation with ICU messages

Concatenation is the bug that survives translation. Word order differs, gender agreement differs, and a sentence assembled from pieces cannot be translated correctly at all.

4.1 Find every string built with `+`, template literals or array joins and convert it to one ICU message with named arguments.

4.2 Pass values as arguments, not as pre-formatted strings - pass the number, not the number with a rupee sign attached.

4.3 Handle plurals with ICU `plural` and the correct categories for each locale, never with `count > 1 ?`.

4.4 Handle gender agreement with `select` where the language needs it, and give translators the variable names.

4.5 Keep interpolation names semantic: `{itemCount}`, not `{0}`.

4.6 Test each converted message with 0, 1, 2 and 11 as the count, because the boundaries are where plurals break.

```tsx
// before - untranslatable
<p>{count} item{count > 1 ? "s" : ""} added to {listName}</p>

// after - translatable, one message per locale
<p>{t("cart.added", { count, listName })}</p>
```

Gate: no user-visible string is assembled from fragments, and every plural has been tested at 0, 1, 2 and 11.

## Stage 5 - Format numbers, dates and currency by locale

Formatting is not translation. A date shown as 03/04/2026 is a different day in two locales, and a price formatted with the wrong separator is a support ticket.

5.1 Use `Intl.NumberFormat` with the active locale for every number, including percentages and file sizes.

5.2 Use `Intl.DateTimeFormat` with an explicit style, never a hand-built string.

5.3 Use `Intl.DisplayNames` and `Intl.RelativeTimeFormat` for language names and "2 days ago", so they follow the locale.

5.4 Keep the currency from the data, not from the locale - a price in rupees stays rupees when the UI is in German.

5.5 Set the time zone explicitly for anything that is a deadline or a delivery date.

5.6 Check the two-digit-day trap: en-GB and en-IN read 03/04 as 3 April, en-US as 4 March, so never show a numeric-only date.

```ts
const fmt = (locale: string, value: number, currency = "INR") =>
  new Intl.NumberFormat(locale, { style: "currency", currency }).format(value);

fmt("en-IN", 125000); // ₹1,25,000.00 - Indian digit grouping
fmt("de-DE", 125000); // 1.250,00 ₹
```

Gate: no numeric-only dates anywhere, and every number and price goes through an `Intl` formatter.

## Stage 6 - Handle right-to-left without a second codebase

RTL is a layout mode, not a translation. Doing it with logical properties costs a day; doing it with a mirrored stylesheet costs a rewrite.

6.1 Set `dir` on the document from the active locale, and set `lang` too - screen readers depend on both.

6.2 Replace `margin-left` and `padding-right` with logical properties: `margin-inline-start`, `padding-inline-end`.

6.3 Use `flex` and `grid` with logical directions, and avoid `float: left` entirely.

6.4 Mirror icons that carry direction - arrows, back buttons, progress chevrons - and leave icons that do not - clocks, logos.

6.5 Keep numbers and code samples LTR inside RTL text with `dir="ltr"` on the element, or the digits reorder.

6.6 Check forms: labels, inputs and validation messages must align to the start edge, and the caret must move the right way.

6.7 Test at 320 px width in RTL; the mirrored layout is where overflow appears first.

| Element | Mirror in RTL | Why |
|---|---|---|
| Back arrow | Yes | Direction is part of the meaning |
| Progress chevrons | Yes | Reading direction |
| Clock icon | No | Universal |
| Brand logo | No | Identity, not direction |
| Phone numbers | No | Keep LTR digits |

Gate: the RTL build has no hardcoded left/right margins, mirrored directional icons, and LTR digits inside RTL text.

## Stage 7 - Prove coverage with a pseudo-locale

A pseudo-locale makes every untranslated string obvious before a translator is paid, and it stresses the layout at the same time.

7.1 Generate a pseudo-locale that wraps every string: `[!!! Ŝubmît ôrder !!!]`.

7.2 Add 30-40% length padding in the pseudo-locale to simulate German, and test the tightest layout.

7.3 Run the app in the pseudo-locale and screenshot every screen; anything still in plain English is a missed string.

7.4 Add a test that fails when a message key is missing from the default locale.

7.5 Add a CI check that fails when a new key is added to one locale and not the others, with an allowlist for deliberate gaps.

7.6 Keep the pseudo-locale in the repository permanently; it is a development tool, not a launch step.

Gate: zero plain-English strings survive in the pseudo-locale, and CI fails on a missing key.

## Stage 8 - Ship the second locale with a locale-aware build

The last mile is routing, caching and the browser's own preference. Most bugs here are configuration, not code.

8.1 Put the locale in the URL path or subdomain, so each language is cacheable and indexable separately.

8.2 Set `hreflang` links between the language versions, and a self-referencing one per page.

8.3 Detect the browser's `Accept-Language` on first visit, then store the choice and never override it again.

8.4 Lazy-load the locale bundle after the default, and show the default for the first paint rather than a blank screen.

8.5 Add a language switcher that keeps the current page, not the home page.

8.6 Check the fallback path: a missing key in the second locale must render the default-language string and log once, not crash.

Gate: each locale has its own URL, `hreflang` is set, and a missing key falls back rather than breaking the page.

## Stage 9 - Keep it translated after launch

The second language decays the moment a developer adds a string in English and moves on. Make the decay visible.

9.1 Add the key-coverage check to CI, with a fail threshold - for example, fail below 98% coverage for shipped locales.

9.2 Send translators a file per release, not per commit, and keep the file diffable.

9.3 Keep a glossary of terms that must not be translated, and give it to every translator.

9.4 Add a screenshot of the new screen to the translation ticket; context halves the review cycle.

9.5 Review one screen per locale per release with a native speaker, and log what was wrong.

9.6 Track the two metrics that matter: keys missing per locale, and layout overflow bugs per release.

Gate: CI enforces a coverage threshold, and a native speaker reviews at least one screen per locale per release.

## Quality checklist

- [ ] A string inventory with counts exists before any library is installed.
- [ ] Concatenated strings are listed and later converted.
- [ ] Every formatted value is identified by type.
- [ ] The message format is ICU and translators' tools can parse it.
- [ ] Fallback behaviour is defined: default language plus a logged warning.
- [ ] Keys are semantic, not English text.
- [ ] Default-locale output is unchanged after extraction.
- [ ] No user-visible string is built by concatenation.
- [ ] Every plural is tested at 0, 1, 2 and 11.
- [ ] Every number and price uses an `Intl` formatter.
- [ ] No numeric-only dates are rendered.
- [ ] RTL uses logical properties with no hardcoded left or right.
- [ ] Directional icons are mirrored and universal ones are not.
- [ ] The pseudo-locale shows zero plain-English strings.
- [ ] CI fails when a key is missing from a shipped locale.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Half the UI still English after translation | Strings inside attributes were never extracted | Include `placeholder`, `title`, `aria-label` and `alt` in the extraction pass |
| Sentence reads wrong in the second language | The message was concatenated from fragments | Convert to one ICU message with named arguments |
| "1 items" in English, wrong plural in Hindi | Plural handled with a boolean check | Use ICU `plural` with the locale's categories |
| German layout overflows | Pseudo-locale had no length padding | Test at 130-140% string length before translating |
| RTL screen mirrors the logo | Every icon flipped with the layout | Mirror only directional icons |
| New English strings appear after launch | No CI coverage check | Fail the build below a coverage threshold |

## Copy-ready agent prompt

> Read the skill at the URL above and run an i18n pass on my app. Start by inventorying every user-visible string, including attributes, and count the concatenated strings and formatted values. Then recommend a message library with ICU support and a per-locale file structure, convert the concatenations to ICU messages, replace date, number and currency formatting with `Intl`, and set up RTL with logical properties. Finish with a pseudo-locale setup, a CI coverage check with a threshold, and the list of screens to screenshot in the pseudo-locale. Do not write the translations.
