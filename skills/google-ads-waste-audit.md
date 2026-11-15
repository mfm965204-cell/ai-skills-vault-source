---
name: google-ads-waste-audit
description: Find the money leaking out of a Google Ads account in one afternoon - search terms with no conversion, broad match without negatives, and bids on queries the business cannot serve.
version: 1.0.0
license: MIT
tags: [marketing, google-ads, audit, ppc, india]
---

# Google Ads Waste Audit

Most small accounts waste 25-45% of spend on searches that will never convert: job seekers, competitors' brand names, "free" queries, and locations the business cannot serve. The waste is invisible in the dashboard because it hides inside a keyword that looks correct.

This skill runs a fixed audit - search terms, match types, negatives, geography, device, and time of day - and produces a ranked list of waste in rupees per month with the exact change that stops each one. You end with a working negative keyword list and a before/after number, not a slide of opinions.

## When to use this skill

- An account spends ₹50,000-₹10,00,000 a month and nobody has opened the search terms report in 60 days.
- Cost per lead rose and conversion volume did not.
- An agency reports clicks and impressions but not the search terms behind them.
- You are about to increase budget and want the leaks closed first.

Do NOT use for: account structure from scratch, creative strategy, or bidding algorithms. It also does not replace reading the business's actual lead quality - a cheap lead that never buys is not a saving.

## Stage 1 - Pull the six reports before forming an opinion

1.1 Search terms report, last 30 days, with cost, clicks, conversions, and conversion value per term.

1.2 Campaign and keyword report with match type, quality score, and impression share lost to budget and to rank.

1.3 Geographic report by location, with cost and conversions.

1.4 Device and time-of-day segments for the same period.

1.5 The conversion actions list with their counting settings - a "conversion" that fires on page view makes every number below meaningless.

| Report | Window | What it answers |
|---|---|---|
| search terms | 30 days | what people actually typed |
| keywords | 30 days | which of your keywords matched |
| geo | 30 days | where the money went |
| devices | 30 days | phone vs desktop behaviour |
| conversion actions | settings | is a conversion real |
| change history | 90 days | what broke it |

Gate: all six pulled, and the conversion actions list reviewed before any number is quoted.

## Stage 2 - Verify the conversion tracking first

2.1 Count the conversion actions that are "primary". Every extra primary action double-counts: a form submit plus a thank-you page view is two conversions for one lead.

2.2 Check the counting setting: "every" inflates a repeat visitor into 4 conversions, "one" is right for lead generation.

2.3 Check the conversion window against the real sales cycle. A 7-day window on a 45-day decision understates the true cost per lead by a wide margin.

2.4 Check for internal traffic: office IP exclusion, and whether the team's own test submissions are firing.

2.5 If tracking is broken, stop the audit and fix it. Every optimisation below is measured against a number that does not exist yet.

| Setting | Correct for lead gen | Symptom when wrong |
|---|---|---|
| primary actions | 1 | conversions 2x leads |
| count | one | same lead counted 4 times |
| window | 30-90 days | inflated cost per lead |
| internal IPs | excluded | phantom conversions |
| values | set per action | value-based bidding misled |

Gate: one primary conversion action, "one" counting, a window matching the sales cycle, internal IPs excluded.

## Stage 3 - Read the search terms report for the four waste patterns

3.1 Irrelevant intent: queries containing free, cheap, download, torrent, jobs, salary, course, pdf, meaning, wikipedia.

3.2 Wrong service: a dentist bidding on "orthodontist course", a B2B tool bidding on "free template".

3.3 Competitor and brand confusion: queries with a competitor name, unless you have a deliberate conquesting campaign with its own budget.

3.4 Location mismatch: queries naming a city you do not serve, common for businesses with a delivery radius.

3.5 Sort by cost, not by impressions. The waste is in the 20-40 terms that each cost more than ₹500 in the period.

| Pattern | Example query | Action |
|---|---|---|
| irrelevant intent | "free invoice template download" | negative phrase, campaign level |
| wrong service | "gst course online" | negative exact on the noun |
| competitor | "competitor name pricing" | separate campaign or negative |
| location | "service in another city" | geo exclusion plus negative |
| job seeker | "accountant jobs near me" | negative phrase "jobs" |

Gate: the top 40 terms by cost are each classified into one of the five patterns or marked as valid.

## Stage 4 - Build the negative keyword list in three tiers

4.1 Account-level negatives: words that are never valid for the business - free, jobs, salary, course, pdf, wikipedia, torrent.

4.2 Campaign-level negatives: words invalid for that service - "repair" for a sales campaign, "buy" for a service campaign.

4.3 Ad-group-level negatives: close variants that should go to a different ad group, not be excluded outright.

4.4 Use phrase and exact negatives; broad negatives block too much. A broad negative "design" blocks "design consultation" as well as "design course".

4.5 Cap the list at 200-300 terms. Beyond that, the problem is keyword targeting, not negatives.

```text
Account-level (phrase): "free" "jobs" "salary" "course" "pdf" "download"
                        "wikipedia" "meaning" "tutorial" "torrent"
Campaign "gst-filing" (exact): [gst course] [gst classes] [gst certification]
Campaign "gst-filing" (phrase): "how to file gst myself"
Ad group "delhi" (exact): [gst filing mumbai] [gst filing chennai]
```

Gate: the list is applied at the right level, and a 7-day watch shows no valid traffic lost.

## Stage 5 - Check match types and the queries they let through

5.1 Broad match without a mature negative list is the largest single source of waste in small accounts. It matches intent, not words.

5.2 Compare cost per conversion by match type. If broad is 3x the cost of phrase with the same volume, the negatives are missing.

5.3 Check close-variant settings: "include close variants" on exact match can pull in plurals and misspellings that change intent.

5.4 Check whether the account uses broad match modifier syntax - it was retired, and accounts still using it are running plain broad.

| Match type | Control | Typical use |
|---|---|---|
| exact | highest | money keywords |
| phrase | medium | expansion with guardrails |
| broad | lowest | discovery only, with negatives |
| smart bidding + broad | none | needs 30+ conversions/month to learn |

Gate: broad match appears only in campaigns with a maintained negative list, or is paused.

## Stage 6 - Cut the geographic and device waste

6.1 Set location targeting to "presence" rather than "presence or interest". Interest targeting spends money on people searching about a city from elsewhere.

6.2 Exclude locations with cost and zero conversions over 60 days. Two or three cities usually carry most of the waste.

6.3 Check device splits for a service business: calls convert on mobile, form fills on desktop. Bidding the same for both wastes one of them.

6.4 Check ad schedule against the hours the business answers the phone. A lead at 23:00 that nobody calls back for 11 hours is a lost lead with a paid click.

| Segment | Check | Common finding |
|---|---|---|
| location setting | presence only | 15-30% of spend from interest |
| city-level geo | cost with 0 conversions | 2-3 cities dominate waste |
| mobile vs desktop | conversion rate split | 3-5x difference is normal |
| ad schedule | business hours | 20-40% of spend out of hours |

Gate: location targeting set to presence, and every excluded location has 60 days of data behind it.

## Stage 7 - Quantify the waste in rupees per month

7.1 For each waste pattern, add the 30-day cost of the terms in it. That is the monthly leak for that pattern.

7.2 Add the recoverable share: not all of it becomes profit, because some of those clicks would have gone to a valid term. Use 60-80% of the cost as the realistic recovery.

7.3 Rank by recoverable rupees, not by number of terms. Ten ₹200 terms matter less than one ₹9,000 term.

7.4 Convert to a comparable unit: cost per lead before and after, using the verified conversion count.

```python
rows = [("irrelevant", 18400, 0.70), ("competitor", 9100, 0.70),
        ("location", 22600, 0.70), ("out-of-hours", 6300, 0.70)]
recoverable = [(n, c, round(c * r)) for n, c, r in rows]
print(sorted(recoverable, key=lambda x: -x[2]))
print("total", sum(c for _, c, _ in recoverable),
      "recoverable", sum(r for _, _, r in recoverable))
```

| Pattern | 30-day cost | Recoverable at 70% |
|---|---|---|
| irrelevant intent | ₹18,400 | ₹12,880 |
| competitor queries | ₹9,100 | ₹6,370 |
| location mismatch | ₹22,600 | ₹15,820 |
| out-of-hours calls | ₹6,300 | ₹4,410 |
| total | ₹56,400 | ₹39,480 |

Gate: a ranked table in rupees with a total, and the total is 15-60% of the period spend or the audit is incomplete.

## Stage 8 - Apply in one change window and measure for 14 days

8.1 Apply all negative keywords in one session and log the change in the account's change history with a note.

8.2 Do not change bids, budgets or creative in the same window. Two changes at once makes the result unreadable.

8.3 Watch for 14 days: impressions should fall, cost should fall, conversions should hold. A conversion drop over 20% means a negative was too broad.

8.4 Keep a 7-day and a 14-day snapshot of cost, clicks, conversions and cost per lead.

8.5 Roll back a single negative at a time if leads drop, starting with the phrase-level ones.

Gate: 14 days of data showing cost down and cost per lead down, with conversions within 20% of the baseline.

## Stage 9 - Make the audit a monthly 20-minute routine

9.1 Every month, export search terms, sort by cost, and classify the top 30. That is the whole routine.

9.2 Add new negatives to the right tier and log the date.

9.3 Review the negative list quarterly and remove terms that block valid traffic.

9.4 Track one number month to month: wasted spend as a share of total spend. Below 10% is a maintained account.

9.5 Review the negative list against the business, not just the data. A term blocked last quarter may be a service you launched since.

9.6 Record who applied the changes and when. An account with three people editing it and no log cannot be diagnosed after a bad month.

Gate: the routine is scheduled, and the waste share is recorded for 3 consecutive months.

## Worked example

A dental clinic in Pune, ₹1,80,000 a month, 3 campaigns, before and after a single audit.

| Item | Before | After 14 days | After 30 days |
|---|---|---|---|
| Spend | ₹1,80,000 | ₹1,52,000 | ₹1,49,000 |
| Clicks | 4,120 | 3,180 | 3,090 |
| Conversions | 96 | 92 | 104 |
| Cost per lead | ₹1,875 | ₹1,652 | ₹1,433 |
| Wasted share | 34% | 14% | 11% |
| Negatives added | 0 | 78 | 96 |

The largest single find was ₹31,000 a month on queries naming a city 180 km away, caused by location targeting set to "presence or interest" rather than presence.

## Quality checklist

- [ ] Six reports pulled for the same 30-day window
- [ ] Conversion actions reviewed before any number is used
- [ ] Exactly one primary conversion action
- [ ] Counting set to "one" for lead generation
- [ ] Conversion window matches the real sales cycle
- [ ] Internal IPs excluded
- [ ] Top 40 terms by cost each classified
- [ ] Negatives built in three tiers with phrase and exact only
- [ ] Negative list between 200 and 300 terms
- [ ] Broad match only in campaigns with maintained negatives
- [ ] Location targeting set to presence, not interest
- [ ] Locations with 60 days and zero conversions excluded
- [ ] Device and hour splits reviewed against the sales process
- [ ] Waste quantified in rupees with a recoverable share
- [ ] Changes applied in one window, bids untouched
- [ ] 14-day result measured before any second change

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Cost per lead looks great, sales say leads are junk | Two primary conversion actions double-counting | One primary action, "one" counting |
| Negative list did not reduce spend | Negatives added at ad-group level only | Apply account-level for universal words |
| Conversions collapsed after the audit | Broad negatives blocking valid intent | Use phrase and exact, roll back one at a time |
| Waste reappears every month | No routine, one-off cleanup | Monthly 20-minute search terms pass |
| Spend from cities you do not serve | Location targeting set to interest | Switch to presence, then exclude |
| Leads arrive at midnight | No ad schedule | Schedule to answering hours |
| Broad match spend exploded | No negatives and low conversion volume | Pause broad or maintain the list |
| Numbers do not reconcile with analytics | Conversion window differs between tools | Align windows before comparing |
| Report shows 40% waste every month | Audit run without applying changes | Apply in a change window, measure 14 days |
| Agency reports clicks only | Search terms never shared | Require the export as part of the report |
| A new service gets no traffic | Old negatives still blocking it | Review the list quarterly against the offer |
| Nobody can explain a bad month | Three editors, no change log | Log who changed what, with a note |

## Copy-ready agent prompt

> Read the skill at the URL above and audit my Google Ads account for waste. Ask me: monthly spend, the services I actually sell, the locations I serve, my sales cycle length, and how many primary conversion actions I have. Then walk me through the six reports, verify conversion tracking before using any number, classify my top 40 search terms by cost into the five waste patterns, build the three-tier negative keyword list using phrase and exact only, check match types, location targeting mode, device and hour splits, and quantify the waste in rupees per month with a realistic recoverable share. Finish with the single change window, the 14-day measurement plan and the monthly 20-minute routine. Tell me the total monthly leak and the top three changes by rupees recovered.
