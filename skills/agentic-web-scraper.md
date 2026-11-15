---
name: agentic-web-scraper
description: Build a resilient web data pipeline that an AI agent can run unsupervised - discovery, extraction, anti-brittleness, pagination, dedupe, validation, storage, scheduling and monitoring, with legality checks first.
version: 1.0.0
license: MIT
tags: [scraping, data, automation, agents, python, pipeline]
---

# Agentic Web Scraper

A scraper that runs once is a script. A scraper that runs daily for a year without you touching it is a system. This skill builds the second one.

## When to use this skill

- Collecting structured data from a site you have permission to read, repeatedly.
- Monitoring prices, listings, jobs, releases, tenders or news.
- Feeding an AI agent a reliable, validated dataset instead of ad-hoc fetches.

## Stage 0 - Legality and permission (do not skip)

1. Read the site's Terms of Service and `robots.txt`. Disallowed paths are disallowed, including for "just testing".
2. Prefer an official API, RSS feed, sitemap or bulk export if one exists. Say so if it does.
3. Never bypass logins, CAPTCHAs, paywalls, rate limits or bot protection. If the data is gated, ask the user to obtain access legitimately.
4. Do not collect personal data (names, emails, phone numbers, profiles) without a lawful basis. Prefer aggregate or non-personal fields.
5. Respect `Crawl-delay`. If absent, default to 1 request per 2 seconds per host.
6. Record the legal basis, source URL, terms link and date checked in the pipeline's `SOURCE.md`.

If the request is to scrape a site that forbids it, or to defeat protections, say so plainly and offer the legitimate alternative (API, licensed dataset, manual export).

## Stage 1 - Define the output schema first

Write the target table before you look at any HTML. The schema is the contract; the scraper is disposable.

```python
from pydantic import BaseModel, Field
from datetime import datetime

class Listing(BaseModel):
    source_id: str = Field(description="Stable id from the site, not a row number")
    title: str
    price: float | None
    currency: str | None
    location: str | None
    posted_at: datetime | None
    url: str
    scraped_at: datetime
```

Rules: every field either has a stable source or is nullable. `source_id` + `source` is the dedupe key. Never invent a value to fill a gap - null is information.

## Stage 2 - Choose the extraction layer (cheapest first)

| Situation | Method | Why |
|---|---|---|
| Server-rendered HTML | `httpx` + `selectolax`/`BeautifulSoup` | Fast, cheap, no browser |
| JSON embedded in the page (`__NEXT_DATA__`, `window.__INITIAL_STATE__`) | Parse the JSON blob | Most robust - it is the site's own data |
| Documented/undocumented JSON endpoint | Call it directly | Far more stable than DOM |
| Content requires JS execution | Playwright (headless) | Last resort: slow, heavy |
| Layout changes constantly, low volume | LLM extraction over cleaned text | Flexible but non-deterministic, so validate |

Check for the JSON blob before writing a single CSS selector. It removes 80% of future breakage.

## Stage 3 - Discovery and pagination

Handle all four, because sites mix them:

1. **URL pattern** - `?page=n` until an empty result.
2. **Cursor / next-token** - follow `next_cursor` until null.
3. **Infinite scroll** - Playwright, scroll until the item count stops growing for 3 rounds.
4. **Sitemap** - fetch `sitemap.xml`, follow nested sitemaps, filter by `lastmod`.

Always set a hard stop: max pages, max items, max runtime. An unsupervised crawler without a stop condition will eat the host's bandwidth and your budget.

## Stage 4 - Anti-brittleness rules

- **Never** select on generated class names (`.css-1x9f2a`). Select on stable structure: `article[data-id] h2 a`, or text-anchored selectors.
- Provide **selector fallbacks**: a list of candidate selectors per field, first match wins.
- Parse **numbers and dates defensively**: strip currency symbols and thousands separators by locale (`1.234,56` vs `1,234.56`), parse relative dates ("2 days ago") against `scraped_at`.
- Fail **loudly on structure change**: if the item count drops more than 60% versus the 7-day median, stop and alert instead of writing 0 rows.
- Version the parser. Keep the raw HTML of 3 sample pages in `fixtures/` and run the parser against them in CI.

## Stage 5 - Fetching etiquette and retries

```python
HEADERS = {"User-Agent": "MyDataBot/1.0 (+https://example.com/bot; contact@example.com)"}
```

- Exponential backoff with jitter on 429/5xx: 1s, 2s, 4s, 8s, cap 3 attempts.
- Honour `Retry-After`.
- Timeouts: 15 s connect, 30 s read.
- Concurrency: 2-3 per host maximum. Politeness beats speed.
- Cache raw responses to disk keyed by URL hash, so re-parsing costs nothing.

## Stage 6 - Storage and dedupe

- Raw layer: append-only JSONL of untouched responses, one file per run. Never lose the raw data - it lets you re-parse history after a fix.
- Clean layer: SQLite or Postgres/Parquet with the schema above.
- Upsert on `(source, source_id)`. Keep `first_seen` and `last_seen`; treat disappearance as a soft delete, not a row delete.
- Idempotent runs: running twice on the same day must not duplicate rows.

## Stage 7 - Validation gates before the data is used

1. Schema validation on every row (pydantic). Reject, log, continue.
2. Field-level sanity: price > 0, price < 100x median, URL matches host, date not in the future.
3. Completeness report per run: rows, null rate per field, distinct `source_id` count.
4. Drift report: field-level null rate versus the last 7 runs.
5. Emit a `run_report.json`. An agent should be able to read it and decide whether the data is trustworthy.

## Stage 8 - Scheduling and monitoring

- Run on a schedule that matches the site's update rate, not every minute.
- Alert only on actionable conditions: zero rows, completeness below threshold, 3 consecutive failures, schema drift.
- Log a one-line summary per run: `2026-11-15 ok rows=842 nulls(price)=3 dur=96s`.
- Store a screenshot or HTML snapshot on parse failure so debugging does not require a re-crawl.

## Stage 9 - Agent operating instructions

When an AI agent runs this pipeline unsupervised:

1. Read `SOURCE.md` and confirm the legal basis is still valid.
2. Run in `--dry-run` first: fetch 1 page, parse, print 3 rows.
3. Compare the row count to the previous run before committing to the database.
4. On a structure-change alert: stop, save the fixture, report the diff, do not guess new selectors and push them live.
5. Never escalate to a headless browser or a proxy pool to get around a block - report the block instead.

## Quality checklist

- [ ] Terms and robots checked and recorded
- [ ] Official API ruled out with a reason
- [ ] Schema defined before extraction
- [ ] Selector fallbacks and raw HTML fixtures in place
- [ ] Pagination handles all 4 patterns with hard stops
- [ ] Backoff, jitter and `Retry-After` honoured
- [ ] Idempotent upsert, raw layer preserved
- [ ] Validation and drift report per run
- [ ] Alerting on the 4 actionable conditions only

## Copy-ready agent prompt

> Read the skill at the URL above. First, check `robots.txt` and the terms for the site I name and tell me plainly whether this is permitted and what the polite crawl rate is. If permitted, define the pydantic schema, write the fetcher with backoff and caching, parse with selector fallbacks, validate, upsert idempotently, and output a `run_report.json`. Do not use a headless browser unless server HTML has no data. Stop and report rather than inventing selectors after a structure change.
