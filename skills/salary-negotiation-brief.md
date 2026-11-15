---
name: salary-negotiation-brief
description: Build the one-page brief that turns an offer conversation into a number you can defend, with the market band, your evidence and the exact sentences to say.
version: 1.0.0
license: MIT
tags: [career, negotiation, salary, offer, india]
---

# Salary Negotiation Brief

Most offers are accepted or rejected inside 20 minutes of conversation, with no written band, no evidence and no fallback number. The result is a fixed-cost decision made on feeling: a ₹2,00,000 gap compounds across every future revision because most raises are percentage-based.

This skill produces a one-page brief before you reply: the market band with its sources, your evidence column, the three numbers (target, acceptable, walk-away), and the sentences for each of the four things a recruiter will say. You end with a document you can read from during the call and a written counter you can send in 90 seconds.

## When to use this skill

- An offer is on the table and you have 48 hours to respond.
- You are entering a review cycle and want the number ready before the meeting.
- You have two offers and need to compare them on total compensation, not base.
- A recruiter asked "what are your expectations" and you have no band to quote.

Do NOT use for: legal advice on a contract, equity valuation of a private company, or fabricating competing offers. Inventing a rival offer is a lie that gets checked, and the reputational cost is permanent.

## Stage 1 - Build the band before the call

1.1 Collect 5-8 data points from at least 3 source types: a public salary survey, 2-3 job postings that publish a range, and 2 people in the role at similar companies.

1.2 Normalise everything to fixed annual cash first. Convert variable, bonus and equity into a separate column so you compare like with like.

1.3 Cut the top and bottom outliers, then take the median and the 75th percentile. Your target sits at the 75th, your walk-away at the median.

1.4 Write the band with its date and sources. A band without a date is a guess, and bands move 8-12% a year in hot roles.

| Source type | Weight | Weakness |
|---|---|---|
| Published job range | high | often the full band, not the offer |
| Employee-reported survey | medium | self-reported, skews high |
| Recruiter statement | low | verbal, unverifiable |
| Peer in the role | high | one data point only |
| Your current salary | zero | it is not market data |

Gate: 5+ data points, a median, a 75th percentile, and a source line with a date.

## Stage 2 - Write the evidence column, not the wish

2.1 List 4-6 things you did that map to the role's stated outcomes. Each line: action, number, outcome.

2.2 Use the number the business cares about - revenue, cost, latency, tickets, retention - not effort or tenure.

2.3 Drop anything you cannot state in one sentence with a figure. "Improved the dashboard" is not evidence; "cut report load from 40 s to 3 s, used by 60 people daily" is.

2.4 Put the two strongest lines first. The recruiter will read the first two and skim the rest.

| Weak line | Evidence line |
|---|---|
| Handled a big migration | Moved 40 services to ECS over 6 weeks, zero downtime |
| Improved hiring | Hired 6 engineers in 2 quarters, 4 still here at 18 months |
| Worked on performance | Cut p95 API latency from 900 ms to 180 ms |
| Managed a team | Led 7 people across 2 time zones, on-call rotation of 3 |

Gate: 4 lines, each with one number and one outcome, no adjectives.

## Stage 3 - Fix the three numbers before you speak

3.1 Target: the number you ask for first. Set it at the 75th percentile of the band plus the cost of anything you are giving up.

3.2 Acceptable: the number you will say yes to without a second call. Write it down; deciding it mid-call is how people accept less.

3.3 Walk-away: the number below which you decline, including the non-cash conditions that would change it (remote days, notice period, title).

3.4 Write all three on the brief in rupees and in annual fixed cash. Never carry a monthly figure into the conversation; it invites a monthly counter.

3.5 Add the non-cash asks in priority order: 3 things you would trade money for, and 1 you would not.

Gate: three numbers written down before the call, with a non-cash priority list.

## Stage 4 - Compute total compensation, not base

4.1 Build a 4-year table: base, variable at target, employer PF contribution, gratuity, equity value per year, joining bonus, relocation.

4.2 Value equity conservatively. For a listed company use the current price; for a private company assume a 50% haircut and a 4-year vest with a 1-year cliff.

4.3 Discount a joining bonus that has a 12-month clawback. It is a loan against your stay, not compensation.

4.4 Compare offers on year-1 cash, year-1 total, and 4-year total. The ranking often differs between those three columns.

| Component | Include | Discount |
|---|---|---|
| Base | yes | none |
| Variable at target | yes | 30% if paid annually and discretionary |
| Employer PF | yes | none |
| Equity, listed | yes | none |
| Equity, private | yes | 50% |
| Joining bonus with clawback | yes | amortise over 12 months |
| "Unlimited" benefits | no | unquantifiable |

4.5 Compute the table in code, so a change in one offer re-ranks both automatically:

```python
def four_year(base, variable_pct, pf, equity_yr, joining, clawback_months=12):
    year1 = base + base * variable_pct + pf + equity_yr + joining
    rest = (base + base * variable_pct + pf + equity_yr) * 3
    return {"year1_cash": base + joining, "year1_total": year1, "four_year": year1 + rest}

offer_a = four_year(36_00_000, 0.10, 1_80_000, 0, 2_00_000)
offer_b = four_year(33_00_000, 0.06, 1_65_000, 4_00_000, 0)
print(offer_a, offer_b)
```

Gate: three columns computed - year-1 cash, year-1 total, 4-year total.

## Stage 5 - Rehearse the four replies a recruiter gives

5.1 "That is above our band for this level" - answer with the level, not the number: ask what the band is for the next level and what evidence closes the gap.

5.2 "What is your current salary" - answer with the band for the role and your target, not your history. In India this question is common; answer it as a market statement.

5.3 "We can revisit in 6 months" - ask for the review in writing with the criteria, and for the joining bonus to cover the gap until then.

5.4 "This is our final offer" - ask one question: is there flexibility in any component. If no, decide from the brief, not from the pressure.

| They say | You say | What you do not do |
|---|---|---|
| Above our band | "What band applies at the next level?" | Do not lower your number on the call |
| Current salary | "My expectation for this role is ₹X" | Do not quote history |
| Revisit in 6 months | "Happy to - can we put the criteria in writing?" | Do not accept verbally |
| Final offer | "Is there flexibility in any component?" | Do not decide live |

Gate: each of the four replies has a rehearsed sentence you can say without reading.

## Stage 6 - Put the counter in writing

6.1 Send the counter as a short message: thanks, one line of enthusiasm, the number, the evidence line, one non-cash ask.

6.2 Keep it under 150 words. A long counter reads as anxiety and invites a long delay.

6.3 Never counter twice with a higher number than your first. One counter, one revised offer, then a decision.

6.4 Attach nothing. The evidence column stays on your brief; the message stays human.

```text
Thanks for the offer - I am keen to join and the team is exactly the
work I want to do next.

On compensation: based on the market band for this role at this level
(₹38-46 LPA fixed) and my record on [specific outcome], I am looking
for ₹44 LPA fixed. If the base is fixed at the band, I would value
3 additional remote days and a January review with written criteria.

Happy to sign today if we can land there.
```

Gate: the message is under 150 words, contains one number and one non-cash ask.

## Stage 7 - Handle the bargaining power you actually have

7.1 A live competing offer is real bargaining power only if you can name the company and would take it. Otherwise it is a bluff.

7.2 Internal bargaining power is different: a written offer from another team, a documented retention risk, or a skill that blocks a launch.

7.3 Time is bargaining power. An offer with a 7-day deadline is often extendable by one week if you ask plainly.

7.4 Never negotiate with two employers by forwarding one's offer document to the other. It gets traced, and it burns both.

Gate: every piece of bargaining power you plan to mention is something you can prove if asked.

## Stage 8 - Decide, then document

8.1 Compare the final offers against the brief's three columns, not against the last thing said on the call.

8.2 Write the decision and the reasons in 5 lines the same day. It becomes the baseline for the next review and stops the "what if" loop.

8.3 Get the final number in the offer letter before resigning. A verbal revision is not an offer.

8.4 Note the two things you would ask for next time. Negotiation skill compounds per cycle, not per year.

Gate: offer letter in hand with the agreed number, and a 5-line decision note.

## Stage 9 - Set up the next cycle on day one

9.1 Record the band you were given, the level, and the review date in a personal file.

9.2 Write the 3 outcomes that would justify the next jump, and share them with your manager in the first month.

9.3 Diarise the review 8 weeks before the date so evidence is collected while it is fresh.

9.4 Rebuild the band from fresh sources at that point. A 2-year-old band understates by roughly 15%.

9.5 Note the level you were hired at and the level whose band you were quoted. A mismatch between them is the single most common cause of a below-band offer.

Gate: next review date, its criteria and its evidence plan are written down.

## Stage 10 - Keep the brief reusable

10.1 Keep one file per cycle: `negotiation-2026-11.md`, with the band, the evidence, the three numbers and the outcome.

10.2 Refresh the band and the evidence lines each cycle, and delete nothing. The old evidence lines are what you mine when a promotion case needs examples.

10.3 Re-read the previous brief before the next call. The reply that failed last time is usually the one you have forgotten.

10.4 Keep a two-line summary of what moved the number: the evidence line, or the non-cash ask, or the timing.

| Cycle | Band used | Asked | Landed | What moved it |
|---|---|---|---|---|
| 2024 | ₹28-34 LPA | ₹33 LPA | ₹32 LPA | written counter, one evidence line |
| 2026 | ₹38-46 LPA | ₹44 LPA | ₹38.5 LPA | level mismatch, no next-level band |

Gate: the file is saved, dated, and the next review date is in the calendar.

## Worked example

A senior engineer with 2 offers, one at ₹36 LPA fixed and one at ₹33 LPA fixed plus ₹8 LPA of private equity.

| Component | Offer A | Offer B |
|---|---|---|
| Base | ₹36,00,000 | ₹33,00,000 |
| Variable at target | ₹3,60,000 | ₹2,00,000 |
| Employer PF | ₹1,80,000 | ₹1,65,000 |
| Equity per year (discounted) | 0 | ₹4,00,000 |
| Joining bonus (clawback 12 m) | ₹2,00,000 | 0 |
| Year-1 total | ₹43,40,000 | ₹40,65,000 |
| 4-year total | ₹1,65,20,000 | ₹1,60,60,000 |

Offer A won on every column, so the candidate countered A for ₹40 LPA fixed with the 75th-percentile band and one evidence line. A revised to ₹38.5 LPA fixed, and the candidate accepted with a written January review.

## Quality checklist

- [ ] 5+ data points from 3+ source types, with a date on each
- [ ] Band expressed as median and 75th percentile in fixed annual cash
- [ ] Current salary excluded from the band calculation
- [ ] 4-6 evidence lines, each with a number and an outcome
- [ ] Target, acceptable and walk-away all written down before the call
- [ ] Non-cash asks ranked, with one that is not negotiable
- [ ] Four-year table built, not just year one
- [ ] Private equity discounted and clawback amortised
- [ ] All four recruiter replies rehearsed as sentences
- [ ] Counter message under 150 words with one number
- [ ] No second counter above the first
- [ ] Every bargaining-power claim is provable if challenged
- [ ] Final number confirmed in the offer letter before resigning
- [ ] Decision note written within 24 hours
- [ ] Next review date, criteria and evidence plan recorded
- [ ] No invented competing offer anywhere in the process

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Accepted less than intended | Acceptable number never written down | Fix all three numbers before the call |
| Recruiter anchors on current salary | History quoted instead of market band | Answer with the role's band and your target |
| Offer revised down after a counter | Second counter above the first | One counter, then decide |
| Bluff called | Competing offer that could not be named | Only mention power you can prove |
| 4-year value lower than expected | Only base compared | Build the 4-year total column |
| Private equity valued at face | No haircut applied | Discount 50% and apply the cliff |
| "We will revisit in 6 months" then nothing | Verbal only | Ask for criteria in writing before signing |
| Resigned before the letter arrived | Verbal revision treated as an offer | Wait for the document |
| Same gap next year | No band rebuilt for the review | Rebuild the band 8 weeks before the review |
| Negotiation felt personal | Evidence column empty | Lead with 2 numbered outcomes |
| Offer landed at the bottom of the band | Hired at a lower level than the band quoted | Ask for the band at the next level |
| Counter answered with a delay | Long message, no clear number | Under 150 words, one number |
| Same negotiation repeated next cycle | No record of what moved the number | One file per cycle, with the outcome |

## Copy-ready agent prompt

> Read the skill at the URL above and build my negotiation brief before I reply to this offer. Ask me: the role and level, the offer components, my location, and any competing process I can actually name. Then give me the market band as median and 75th percentile in fixed annual cash with dated sources, a 4-6 line evidence column where every line has a number and an outcome, my target, acceptable and walk-away numbers, a 4-year total compensation table with private equity discounted and clawbacks amortised, the four recruiter replies written as sentences I can say, and a counter message under 150 words. Tell me which column the offer actually wins on. Do not invent a competing offer or a salary figure you cannot source.
