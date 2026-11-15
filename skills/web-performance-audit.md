---
name: web-performance-audit
description: Take a site from 5-second loads to Core Web Vitals passing on a mid-range Android phone - field measurement, a per-route budget, LCP diagnosis, image and font pipelines, a JS budget, INP fixes and a CI regression gate.
version: 1.0.0
license: MIT
tags: [frontend, performance, core-web-vitals, lighthouse, images, caching]
---

# Web Performance Audit

A 5-second load on a ₹12,000 Android phone is not a hosting problem. It is 1.8 MB of JavaScript nobody reads, a 2.4 MB hero JPEG, three font files, and a third-party tag manager that blocks the first paint.

This skill measures on the device your users actually hold, sets a per-route budget, and fixes in the order that moves the number: images, fonts, JS, third parties. You finish with Core Web Vitals passing in the field, not just in a lab.

## When to use this skill

- Lighthouse says 40 and you do not know which of the 60 findings matter.
- Field LCP is 4.2 s on mobile while your laptop loads in 800 ms.
- Ad spend is rising and conversion is falling on mobile.
- A framework upgrade made the bundle 40% bigger and nobody noticed.

Do NOT use for: server-side capacity problems (that is TTFB and infrastructure), or image aesthetics - this is bytes and milliseconds.

## Stage 1 - Measure where your users are

1.1 Separate field data from lab data. Field (CrUX, your own RUM) is the truth; lab (Lighthouse) is a reproducible proxy. Optimising only the lab score is how sites get fast scores and slow pages.

1.2 Get field numbers for the 75th percentile, not the average. Core Web Vitals are defined at p75, and the average hides the slow third of your traffic.

1.3 Measure on the real device class: a mid-range Android on 4G with 1.6 Mbps down, 750 Kbps up, 150 ms RTT. Chrome DevTools "Slow 4G" plus 4x CPU throttling is the closest cheap approximation.

1.4 Record the baseline in a table before changing anything, per route:

| Route | LCP p75 | INP p75 | CLS p75 | Weight | Requests |
|---|---|---|---|---|---|
| / | record | record | record | record | record |
| /pricing | record | record | record | record | record |
| /blog/post | record | record | record | record | record |

1.5 Split traffic by device and network in your RUM. If 70% of Indian sessions are on 4G Android, an iPhone-only optimisation is decoration.

1.6 Sample enough sessions for the number to mean something: below about 500 sessions a week per route, your p75 is noise and you should read the whole-site p75 instead.

1.7 Record the device and network mix alongside the numbers, so a later improvement can be attributed to the change and not to a shift in traffic.

Gate: a baseline table with p75 numbers for the top 5 routes.

## Stage 2 - Set the budget you will be judged against

2.1 Use the official thresholds and hold every route to them at p75:

| Metric | Good | Needs work | Poor |
|---|---|---|---|
| LCP | under 2.5 s | 2.5-4.0 s | over 4.0 s |
| INP | under 200 ms | 200-500 ms | over 500 ms |
| CLS | under 0.1 | 0.1-0.25 | over 0.25 |
| TTFB | under 800 ms | 800-1800 ms | over 1800 ms |
| Total JS transferred | under 170 KB gzip | 170-350 KB | over 350 KB |
| Total page weight | under 1 MB | 1-2 MB | over 2 MB |
| Requests | under 50 | 50-80 | over 80 |

2.2 Convert the budget into per-route numbers. A landing page gets 120 KB of JS; an app shell gets 200 KB; a docs page gets 60 KB.

2.3 Put the budget in the repo as `budget.json` so CI can fail on it, and so the next developer inherits a limit instead of an opinion.

2.4 Write down what you will not do: dropping analytics, removing a payment widget, or shipping a spinner-only shell. A budget with no exceptions list dies in week two.

2.5 Map each symptom to the fix that actually moves it, so you do not spend a week on the wrong layer:

| Symptom | First thing to check | Usually the fix |
|---|---|---|
| LCP over 4 s | TTFB and the hero image | edge cache, AVIF, preload |
| CLS over 0.2 | images and fonts without dimensions | width/height, `size-adjust` |
| INP over 500 ms | long tasks on click | split work, Web Worker |
| High TTFB only | origin or missing cache | `s-maxage`, edge region |
| Slow only on mobile | JS execution, not bytes | bundle cut, partial hydration |
| Slow only on repeat visits | cache headers wrong | `max-age` and `immutable` on assets |
| Fast in lab, slow in field | throttling absent in lab | RUM plus 4x CPU throttle |
| Slow on first load only | render-blocking CSS and fonts | inline critical CSS |

Gate: `budget.json` committed with per-route limits.

## Stage 3 - Diagnose LCP before touching code

3.1 Find the LCP element first. It is usually the hero image, sometimes an H1 with a web font, occasionally a background video. Guessing wastes a week.

3.2 Break LCP into its four parts: TTFB, resource load delay, resource load time, render delay. Each has a different fix and a different owner.

| Part of LCP | Healthy | Typical cause | Fix |
|---|---|---|---|
| TTFB | under 800 ms | uncached HTML, slow DB | cache HTML at the edge |
| Load delay | under 200 ms | image discovered late by JS | `<link rel=preload>` or plain `<img>` in HTML |
| Load time | under 600 ms | 2 MB JPEG | AVIF or WebP, correct `srcset` |
| Render delay | under 300 ms | blocking font or JS | font swap, defer JS |

3.3 Check whether the hero is in the initial HTML. A hero rendered by client-side JS cannot start loading until the bundle runs - that alone is often 1.5 s of load delay.

3.4 Preload exactly one image: the LCP element. Preloading four images competes for bandwidth and makes LCP worse.

3.5 Check the HTML is cached. `Cache-Control: public, max-age=0, s-maxage=300, stale-while-revalidate=60` at the edge turns a 900 ms TTFB into 80 ms.

Gate: the LCP element named, and its four parts measured with numbers.

## Stage 4 - Fix the image pipeline

4.1 Serve AVIF with a WebP fallback and JPEG last. AVIF is typically 40-60% smaller than JPEG at the same visual quality (estimate; check your own images).

4.2 Always set width and height on every `<img>` to stop layout shift, and `loading="lazy"` on everything except the LCP image.

4.3 Use `srcset` and `sizes` so a 360 px phone does not download a 2000 px image:

```html
<img src="/hero-800.jpg"
     srcset="/hero-400.avif 400w, /hero-800.avif 800w, /hero-1600.avif 1600w"
     sizes="(max-width: 600px) 100vw, 800px"
     width="800" height="450" alt="..." fetchpriority="high" decoding="async">
```

4.4 Set `fetchpriority="high"` on the LCP image and nothing else. It is a hint that costs one attribute and often saves 200-400 ms.

4.5 Do not lazy-load above-the-fold images. `loading="lazy"` on the hero delays the exact element the metric measures.

4.6 Generate the variants at build time, not at request time. On-the-fly resizing burns CPU and adds 100-300 ms of TTFB on the first hit.

Gate: LCP image under 120 KB at 800 px wide, with `srcset`, dimensions and priority set.

## Stage 5 - Cut JavaScript

5.1 Measure the bundle before optimising it: `npx source-map-explorer dist/assets/*.js` or `vite build --report`. Find the 3 largest packages and their gzip sizes.

5.2 Apply the four fixes that actually move the number: delete unused dependencies, replace heavy libraries with 2-5 KB alternatives, split by route, and defer everything below the fold.

5.3 Set a hard per-route limit and fail the build above it:

```json
{
  "ci": { "collect": { "url": ["http://localhost:4321/", "http://localhost:4321/pricing"] },
          "assert": { "assertions": {
            "categories:performance": ["error", { "minScore": 0.9 }],
            "total-byte-weight": ["error", { "maxNumericValue": 1000000 }],
            "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
            "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
          } } }
}
```

5.4 Check what ships that nobody imports: polyfills for browsers you do not support, a whole icon library for 6 icons, a date library for one format call, `lodash` imported as a namespace.

5.5 Prefer native browser APIs: `Intl.DateTimeFormat` instead of a date library, `<dialog>` instead of a modal library, CSS `:has()` instead of a layout library, `fetch` instead of axios.

5.6 Use `module`/`nomodule` or modern-only output. Shipping ES5 to modern phones costs 15-30% of the bundle for nothing.

| Page type | JS budget (gzip) | Common offender |
|---|---|---|
| Marketing landing | 120 KB | tag manager, chat widget |
| Blog article | 60 KB | syntax highlighter loaded eagerly |
| App shell | 200 KB | UI kit imported wholesale |
| Checkout | 150 KB | three payment SDKs |

5.7 Check what the framework ships by default. A meta-framework includes a router, a hydration runtime and often a CSS-in-JS layer before you write a line of app code; measure the empty page first.

5.8 Load below-the-fold widgets on interaction, not on mount. A comments section, a map and a video embed cost 300-700 KB between them and nobody needs them before scrolling.

Gate: total JS under the route budget and the build fails above it.

## Stage 6 - Fix fonts and CSS

6.1 Self-host fonts. A third-party font host adds a DNS lookup, a TLS handshake and 100-300 ms of render delay on Indian mobile networks.

6.2 Subset to the scripts you need: Latin plus Devanagari is a different subset than Latin alone, and shipping all of it is 3x the bytes.

6.3 `font-display: swap` so text renders immediately in a fallback, and `size-adjust` on the fallback to keep CLS near zero when the real font arrives.

6.4 Preload exactly one font file - the one used above the fold in the first heading. Preloading four weights is the same mistake as preloading four images.

6.5 Inline critical CSS under 14 KB and defer the rest. One blocking stylesheet from a CDN costs a full round trip before first paint.

6.6 Remove unused CSS at build time and check the result visually; automated purging breaks dynamic class names, and the breakage ships to production.

Gate: one preloaded font, `font-display: swap` on all, CLS from fonts under 0.02.

## Stage 7 - Audit third parties

7.1 List every third-party script with its size, its blocking behaviour and what it is for. Most sites carry 8-20 and can name the purpose of 4.

7.2 Load all of them after interaction or on idle: `requestIdleCallback`, `loading="lazy"` on iframes, and a click-to-load for chat widgets.

7.3 Move tag manager to load after `DOMContentLoaded` and audit the tags inside it - the container is often 300 KB because someone added a heatmap, a survey and two pixels.

7.4 Measure each one's cost by removing it for a week, not by reading its documentation. Vendors understate; your RUM does not.

| Third party | Typical cost | Treatment |
|---|---|---|
| Tag manager | 80-200 KB | defer, audit tags |
| Chat widget | 150-400 KB | click to load |
| Heatmap | 100-250 KB | sample 10% of sessions |
| A/B testing | 60-150 KB | server-side if possible |
| Video embed | 500 KB+ | facade image, load on click |

7.5 Set a rule: no new third-party script without a measured cost and an owner's name.

Gate: no third-party script blocks first paint, and each has a named owner.

## Stage 8 - Fix INP and long tasks

8.1 INP is about interaction latency, not load. Find long tasks over 50 ms in the Performance panel with 4x CPU throttling, and note which handler blocks.

8.2 Break work into chunks: yield to the main thread with `await new Promise(r => setTimeout(r, 0))` between batches, or `scheduler.yield()` where supported.

8.3 Move heavy work off the main thread: parsing, sorting, image processing and diffing belong in a Web Worker.

8.4 Debounce input handlers at 150-250 ms and never do synchronous layout reads in a scroll or resize handler.

8.5 Avoid layout thrash: batch reads (`offsetHeight`) before writes (`style.width`). Interleaving them forces a synchronous layout per element.

8.6 Check hydration cost on framework apps. Hydrating a 3,000-node page takes 400-900 ms on a mid-range phone; island hydration or partial hydration is the fix.

8.7 Profile on the real interaction, not on page load. Open the Performance panel, click the slow button, and read the longest task in the flame chart.

8.8 Cap DOM size per route. Above roughly 1,500 nodes, style recalculation alone costs 50-150 ms per interaction on a mid-range phone.

Gate: no task over 200 ms on the main thread during a typical interaction.

## Stage 9 - Verify in CI and keep it fixed

9.1 Run Lighthouse CI on every pull request against 3 routes, with budgets as assertions, and fail the build rather than warn.

9.2 Track field data weekly from your RUM or Search Console, per route and per device class. Lab scores drift from field reality within a month.

9.3 Add a bundle-size check to the PR (`size-limit`, `bundlesize`) with a 5% delta threshold so a slow creep is visible in review.

9.4 Keep a `perf.md` log: date, change, LCP before and after, who measured. Six months later this is the only reason anyone remembers why a library was removed.

9.5 Re-audit quarterly. Performance is a leak: every feature adds a script, and nobody removes one.

9.6 Keep a canary route with the previous release so a regression can be measured against the version users had yesterday.

9.7 Review the 5 slowest sessions weekly in RUM. One broken interaction in a common flow costs more than 40 small optimisations.

Gate: CI blocks on the budget, field data reviewed weekly.

## Stage 10 - Handle the India-specific realities

10.1 Assume 4G with variable latency, not fibre. Test with 150-250 ms RTT, because that is what a Tier-2 city connection looks like on a bad day.

10.2 Optimise for 2-3 GB RAM devices. A 40 MB heap and a 3,000-node DOM will not survive there, and your iPhone test will never show it.

10.3 Serve from an Indian edge region or CDN PoP. A round trip to a US origin adds 200-400 ms to TTFB for every user in the country.

10.4 Budget data cost as well as time: 1 MB of page is real money on a metered plan, and users on 1.5 GB daily caps notice.

10.5 Test on a real ₹10,000-15,000 Android over a hotspot, once per release. Emulation is close; a real device on a real network is the last word.

Gate: one real mid-range Android test per release, recorded.

## Worked example

A marketing site, 4 routes, 3.1 MB per page, LCP 4.8 s at p75 on mobile.

| Change | Bytes saved | LCP |
|---|---|---|
| Baseline | - | 4.8 s |
| Hero JPEG 2.4 MB to AVIF 380 KB with srcset | 2.0 MB | 3.1 s |
| HTML cached at edge, TTFB 900 to 90 ms | - | 2.6 s |
| Self-hosted 1 font, preloaded, subset | 240 KB | 2.4 s |
| JS 620 to 140 KB, tag manager deferred | 480 KB | 2.3 s |
| Chat widget click-to-load | 380 KB | 2.3 s |

Field LCP at p75 went to 2.2 s over three weeks, and conversion on mobile rose 11% (a measured result on this site, not a general claim). Total page weight fell from 3.1 MB to 620 KB.

## Second worked example - a framework app shell

A dashboard behind login, 1.9 MB of JS, INP 680 ms on a mid-range phone.

| Change | Effect | INP |
|---|---|---|
| Baseline | - | 680 ms |
| Icon library replaced with 6 inline SVGs | -180 KB | 610 ms |
| Chart library loaded on tab open, not on mount | -240 KB | 520 ms |
| Table virtualised to 30 rows in the DOM | 1,400 fewer nodes | 240 ms |
| Search input debounced at 200 ms | -1 handler per keystroke | 190 ms |
| Filtering moved to a Web Worker | -1 long task of 310 ms | 150 ms |

The bundle barely moved after the first two fixes; the interaction number moved when the DOM shrank. INP is a rendering problem more often than a download problem.

## Quality checklist

- [ ] Field p75 baseline recorded per route
- [ ] Measured on a mid-range Android with 4x CPU throttle
- [ ] `budget.json` committed with per-route limits
- [ ] LCP element identified, four parts measured
- [ ] HTML cached at the edge, TTFB under 800 ms
- [ ] One preload, for the LCP image only
- [ ] AVIF or WebP with `srcset`, width and height set
- [ ] No `loading="lazy"` above the fold
- [ ] JS under the route budget, build fails above it
- [ ] One self-hosted subset font, `font-display: swap`
- [ ] Critical CSS inlined under 14 KB
- [ ] No third-party script blocks first paint
- [ ] Long tasks over 200 ms eliminated on interaction
- [ ] Lighthouse CI asserts budgets on every PR
- [ ] Bundle-size check with a 5% threshold in CI
- [ ] Real device test on a mid-range Android each release

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Lighthouse 98, field LCP 4.5 s | Lab measured an unthrottled desktop on localhost | Measure with RUM and 4x CPU throttle, fix what field data names |
| Hero loads late even with a preload | Image URL is built by JS at runtime, so the preload misses | Render the `<img>` in the HTML with a static URL |
| LCP got worse after adding preloads | Four images preloaded, competing for bandwidth | Preload only the LCP element |
| CLS spikes on every page | Images without width and height | Set intrinsic dimensions on every image and iframe |
| Bundle grew 40% in one release | A whole icon or UI library imported for 6 icons | Import per-icon, or switch to inline SVG |
| Site slow only on Android | 3,000-node DOM plus hydration on a 2 GB device | Partial hydration, virtualise long lists |
| Font swap causes visible jump | Fallback metrics differ from the web font | `size-adjust` and `ascent-override` on the fallback |
| Numbers improve then regress in a month | No CI gate, budgets live in a document | Assert budgets in CI and fail the build |

## Copy-ready agent prompt

> Read the skill at the URL above and audit my site's performance. Ask me for the URL, the framework, the top 3 routes and whether I have field data. Then produce a baseline table with p75 LCP, INP, CLS and total weight per route measured on a throttled mid-range Android, identify the LCP element and break its time into TTFB, load delay, load time and render delay. Then fix in this order: images, HTML caching, fonts, JS, third parties, INP. Give me the exact code changes and a `budget.json` with per-route limits, plus a Lighthouse CI config that fails the build. Finish with the re-measurement table and the three things most likely to regress.
