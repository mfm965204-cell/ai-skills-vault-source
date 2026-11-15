---
name: seo-content-engine
description: Build a repeatable SEO content system - keyword clustering by intent, SERP-informed outlines, entity coverage, internal linking, schema markup, and a refresh loop that compounds rankings instead of chasing one-off posts.
version: 1.0.0
license: MIT
tags: [seo, content, keywords, strategy, writing, growth]
---

# SEO Content Engine

Publish in clusters, not in singles. One well-linked cluster of 8 pages outranks 8 unrelated posts every time.

## When to use this skill

- Building a content plan from zero.
- Turning a keyword list into an editorial calendar with structure.
- Diagnosing a site that publishes consistently but does not rank.
- Refreshing decaying pages.

## Stage 1 - Seed and intent map

Start with 5-10 seed topics from the business's actual offering, not from imagination. For each seed, expand with: people also ask, autocomplete, related searches, competitor headings, and forum language (Reddit/Quora phrasing).

Then classify every keyword into one of four intents:

| Intent | Query shape | Page type |
|---|---|---|
| Informational | how, what, why, guide | Article / tutorial |
| Commercial | best, vs, review, alternatives | Comparison / listicle |
| Transactional | buy, price, download, near me | Product / service page |
| Navigational | brand, login, docs | Docs / support |

Rule: never target two different intents on one page. It splits relevance and ranks for neither.

## Stage 2 - Cluster into a hub-and-spoke model

- **Pillar (hub)** - the broad head term, 2,500-4,000 words, links to every spoke.
- **Spokes** - 6-12 long-tail pages, each answering exactly one sub-question, each linking back to the pillar and to 2 sibling spokes.
- **One page, one primary keyword.** Secondary variants go in H2s and body, never in a competing page.

Cluster record for each page:

```
id | primary_kw | volume | difficulty | intent | url | parent | status | last_updated
```

## Stage 3 - SERP-informed outline

Before writing, read the top 5 results for the primary keyword and record:

1. Which subtopics all 5 cover (table stakes - you must cover them).
2. What none of them cover well (your opening).
3. The dominant format (listicle, tutorial, comparison table) - match the format, beat the depth.
4. Questions in People Also Ask - each becomes an H2 or FAQ entry.
5. Freshness signals - are results from this year? If yes, include current-year data.

An outline that ignores the SERP is a guess. An outline that copies it is a rewrite. Match the skeleton, add a section nobody has.

## Stage 4 - Writing rules

- Answer the query in the first 60 words, before any preamble.
- One idea per H2. Every H2 should be readable as a standalone answer.
- Short paragraphs: 2-4 sentences. Mobile reading is the default.
- Include specifics: numbers, versions, prices, dates, named tools. Vague content does not get cited by AI search or linked by humans.
- Original assets per page: one table, one checklist, one diagram or one worked example. This is what earns links.
- Show first-hand experience: what you tried, what failed, what the numbers were. This is the "E" in E-E-A-T and it cannot be faked.
- Keyword placement: title, H1, first 100 words, one H2, URL, meta description, image alt. Nowhere else needs forcing.
- Readability: grade 7-8, active voice, no filler intros ("In today's digital landscape...").
- Never invent statistics, quotes, studies or authors. If a number is needed, cite a real source or omit the claim.

## Stage 5 - On-page technical checklist

- [ ] Title under 60 chars, primary keyword near the front
- [ ] Meta description 150-160 chars with a benefit and a verb
- [ ] One H1, logical H2/H3 nesting
- [ ] Descriptive URL slug, 3-5 words, no dates
- [ ] Internal links: 3-6 contextual, descriptive anchor text (never "click here")
- [ ] External links: 1-3 to authoritative sources
- [ ] Images: WebP, `width`/`height`, descriptive alt, compressed under 150 KB
- [ ] Table of contents for pages over 1,500 words
- [ ] Canonical tag, OG tags, `lang`
- [ ] Schema: `Article` + `FAQPage` where FAQs exist, `HowTo` for tutorials
- [ ] Author box with real credentials and a link

## Stage 6 - Schema examples

```json
{"@context":"https://schema.org","@type":"Article",
 "headline":"...","datePublished":"2026-11-15","dateModified":"2026-11-15",
 "author":{"@type":"Person","name":"...","url":"..."},
 "publisher":{"@type":"Organization","name":"..."}}
```

Only mark up what is visibly on the page. Fake FAQ schema is a manual-action risk.

## Stage 7 - Internal linking engine

1. Every new page links up to its pillar and sideways to 2 siblings - on publish, not later.
2. Every pillar links down to all its spokes within the first 800 words.
3. Update the 2 most relevant existing pages to link to the new one. This is the step everyone skips and it is worth the most.
4. Anchor text should describe the target page's topic, varied across links.
5. Cap links per 1,000 words at ~10 internal. More dilutes.

## Stage 8 - Refresh loop (where compounding happens)

Monthly, sort pages by impressions (from Search Console) and check position:

| Position | Action |
|---|---|
| 4-10 with decent impressions | Highest ROI. Expand depth, add a section, improve title, add internal links |
| 11-20 | Add a missing subtopic from the SERP, add original data, earn 2-3 links |
| 1-3 | Protect: refresh stats, update dates, add internal links from new posts |
| Falling | Check for cannibalisation, merge or redirect |
| Zero impressions after 90 days | Wrong intent or no authority - rewrite or delete |

Track `last_updated` on every page. Content that never updates decays.

## Stage 9 - Measurement

Report per cluster, not per post: total impressions, clicks, average position, and conversions attributed to the cluster. A cluster of 10 pages at position 5 can be worth more than one page at position 1 - optimise the cluster's aggregate.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Ranks then drops | Thin content, no internal links | Expand to cover the SERP subtopics, add links |
| Two pages compete | Intent overlap | Merge, redirect, or re-scope one to a different intent |
| Traffic but no conversions | Informational page with no next step | Add a contextual CTA matching the reader's stage |
| No rankings at all | No authority / no links | Build linkable assets: original data, tools, templates |
| AI search cites competitors | Vague, undated, unattributed claims | Add specifics, dates, named sources, structured answers |

## Copy-ready agent prompt

> Read the skill at the URL above. I will give you a business and a niche. Build a hub-and-spoke cluster: one pillar plus 8 spokes, each with primary keyword, intent, volume estimate, and a SERP-informed outline. Then write the pillar in full with tables, an FAQ block, internal links to the spokes, schema JSON-LD, and meta tags. Flag anything you could not verify instead of inventing numbers.
