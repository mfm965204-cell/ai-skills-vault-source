---
name: xirr-sip-tracker
description: Turn a pile of SIP and lump-sum entries into one XIRR number per folio, with the cashflow export, the script and the monthly statement that prove it.
version: 1.0.0
license: MIT
tags: [finance, xirr, sip, python, spreadsheet, india]
---

# XIRR SIP Tracker

A portfolio app shows a return percentage and hides the cashflow table behind it, so you cannot tell whether the number is XIRR, CAGR or a simple gain on invested capital. Those three differ by 2-6 percentage points on a 5-year SIP, which is enough to change whether you keep the plan.

This skill builds the one artefact that settles it: a dated cashflow table (outflows negative, current value positive), an XIRR calculation you can re-run in 40 lines of Python, and a monthly statement with the same three numbers every time. It works for mutual fund SIPs, recurring deposits, and a friend's business loan.

## When to use this skill

- You have 30-200 SIP instalments across 4-12 folios and no single return number you trust.
- Two apps report different returns for the same portfolio and you need to know which one is lying.
- You are comparing a SIP against a one-time lump sum and need both on the same XIRR basis.
- A statement download gives you units and NAV but not the cashflow dates you need.

Do NOT use for: tax computation, capital-gains statements (that is Form 26AS and your CA's job), or picking funds. This is arithmetic on cashflows you already made, nothing more.

## Stage 1 - Collect the raw cashflows before any calculation

1.1 Export the transaction statement from each folio's registrar (CAMS or KFintech consolidated statement covers most Indian folios in one file).

1.2 Keep exactly four columns: date, folio, amount, direction. Do not merge purchase and redemption rows into one signed column yet - you will get a sign wrong.

1.3 Record the debit date from the bank statement, not the allotment date from the registrar. XIRR measures when money left your account; a 2-day NAV lag silently flatters the return.

1.4 Keep failed and reversed instalments in the sheet with a `status` column instead of deleting them. A reversed auto-debit is a real event and a deleted row makes the next reconciliation impossible.

| Column | Example | Why it must be exact |
|---|---|---|
| date | 2024-04-05 | XIRR is date-sensitive, not period-sensitive |
| folio | 1234567/89 | groups cashflows per scheme |
| amount | 5000.00 | rupees, two decimals, no commas |
| direction | out / in | sign is derived, never typed |
| status | done / reversed | excludes failed debits |

Gate: the count of `out` rows equals the number of instalments you can see in the bank statement.

## Stage 2 - Add the terminal value as a dated cashflow

2.1 Pick the valuation date. Use today's date for a live view, or a fixed month-end for a report that must reproduce.

2.2 Get the current value per folio: units multiplied by that day's NAV. Take NAV from the AMFI published file, never from a screenshot.

2.3 Enter it as a single positive cashflow on the valuation date. An XIRR without a terminal value is a number with no meaning.

2.4 If a folio is fully redeemed, the redemption proceeds are the terminal value and the folio has no current holding - do not add both.

```python
# value.py - terminal value per folio from units and NAV
import csv
nav = {}
with open("NAVAll.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(";")
        if len(parts) >= 6 and parts[0].isdigit():
            nav[parts[0]] = float(parts[4])   # scheme code -> latest NAV

units = {"1234567/89": 412.873, "1234567/90": 88.004}
scheme = {"1234567/89": "119551", "1234567/90": "120503"}
for folio, u in units.items():
    print(folio, round(u * nav[scheme[folio]], 2))
```

Gate: total terminal value within ₹1 of the value shown by the registrar's own app on the same date.

## Stage 3 - Compute XIRR with the right solver settings

3.1 XIRR solves for the rate where the sum of discounted cashflows is zero. Discount by actual days over 365, not by month count.

3.2 Seed the solver at 0.1 and bisect between -0.99 and 10.0. Newton's method alone diverges on portfolios with a large early outflow and a long gap.

3.3 Refuse to print a number when the cashflow set has no sign change - all outflows means there is nothing to annualise.

```python
from datetime import date
def xnpv(rate, flows):
    d0 = flows[0][0]
    return sum(a / (1 + rate) ** ((d - d0).days / 365.0) for d, a in flows)

def xirr(flows):
    lo, hi = -0.99, 10.0
    if xnpv(lo, flows) * xnpv(hi, flows) > 0:
        raise ValueError("no sign change: cannot annualise")
    for _ in range(200):
        mid = (lo + hi) / 2
        if xnpv(lo, flows) * xnpv(mid, flows) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2
```

3.4 Round only at the display step. Rounding the rate inside the loop shifts the answer by up to 0.03 percentage points on a 10-year series.

Gate: recomputing with the flows reversed in date order returns the same rate to 6 decimal places.

## Stage 4 - Separate the three numbers people confuse

4.1 Absolute return is (value - invested) / invested. It ignores time entirely and is the number that flatters a young portfolio.

4.2 CAGR needs a single start and end date. It is wrong for a SIP, and every app that shows it for a SIP is showing you a number that improves as the market rises this month.

4.3 XIRR is the only one that survives irregular dates, which is why every additional purchase breaks the other two.

| Measure | Needs | SIP-safe | Typical gap vs XIRR |
|---|---|---|---|
| Absolute return | total in, total out | no | +2 to +6 points |
| CAGR | one start, one end | no | +1 to +4 points |
| XIRR | dated cashflows | yes | reference |

4.4 Print all three in the statement, labelled, with XIRR marked as the decision number. Showing one number invites the reader to assume it is the flattering one.

Gate: the statement names each measure and none of them appears without its label.

## Stage 5 - Reconcile against the registrar before trusting anything

5.1 Sum the `out` rows per folio and compare to the registrar's "total invested" figure.

5.2 A mismatch under ₹100 is usually a stamp duty or a rounding row. A mismatch over ₹1,000 is a missing or duplicated instalment.

5.3 Check the number of instalments, not just the total: 12 missed months of ₹5,000 can hide inside a total that also has 12 double entries.

5.4 Log every reconciliation run with date, folio, both totals and the delta, so a later drift has a baseline.

Gate: per-folio delta at or below ₹100, and instalment counts equal.

## Stage 6 - Build the monthly statement

6.1 One row per folio, one total row, and a footer with the valuation date and NAV source.

6.2 Show invested, current value, XIRR, and the change in XIRR from last month in percentage points.

6.3 Cap the statement at one page. A statement nobody reads is not monitoring.

6.4 Write the file to a dated name (`statement-2026-11.csv`) and keep the last 24, so a year of history is available without a database.

| Section | Contents | Reader's question answered |
|---|---|---|
| Header | valuation date, NAV file date | is this current |
| Per-folio rows | invested, value, XIRR | which folio is behind |
| Delta column | XIRR change in points | what moved this month |
| Footer | source, script version | can I reproduce it |

Gate: the statement reproduces byte-identically when re-run on the same inputs.

## Stage 7 - Handle the cases that break the maths

7.1 A folio younger than 90 days has an XIRR dominated by the short window - annualising 3 weeks of returns produces 60% numbers. Show "too new" instead of a rate.

7.2 A switch between two schemes is one outflow and one inflow on the same date. Counting the switch as a fresh investment double-counts your capital.

7.3 Dividends reinvested are not new money. Only include them if the money actually left your bank account.

7.4 A partial redemption leaves the folio alive: the redemption is a positive cashflow and the remaining units stay in the terminal value.

7.5 Foreign or NRI folios in another currency need one currency per run - mixing currencies into one XIRR produces a meaningless blend.

7.6 A systematic withdrawal plan reverses the flow direction: instalments are inflows and the terminal value is the remaining corpus. Run it as its own series, never merged with the accumulation folios.

7.7 A bonus or dividend payout that you spent is an inflow on the payout date. Leaving it out overstates the return by exactly the amount you took out.

Gate: every special case is either handled by a rule above or excluded with a printed reason.

## Stage 8 - Automate the refresh without lying to yourself

8.1 Run the refresh on a fixed day each month, not on a day the market looks good. The schedule is part of the honesty.

8.2 Cache the NAV file and its date. If the NAV file is older than 3 days, print a warning instead of silently using stale prices.

8.3 Fail loudly when a folio in the register has no matching units row - that is a new folio nobody added to the config.

8.4 Keep the script under 200 lines and dependency-free except the standard library. A tracker with a pandas pin breaks in a year.

8.5 Keep the folio register in a separate JSON file, so adding a folio never means editing code:

```json
{
  "valuation_day": "month-end",
  "nav_max_age_days": 3,
  "min_history_days": 90,
  "folios": [
    {"id": "1234567/89", "scheme_code": "119551", "units": 412.873, "status": "active"},
    {"id": "1234567/90", "scheme_code": "120503", "units": 88.004, "status": "active"},
    {"id": "1234567/91", "scheme_code": "118989", "units": 0.0, "status": "redeemed"}
  ]
}
```

8.6 Run the refresh with `--dry-run` first, which prints the cashflow count and the valuation date without writing the statement file.

Gate: a dry run on last month's inputs returns last month's numbers.

## Stage 9 - Decide what the number is for

9.1 Compare XIRR against one benchmark you would actually have bought: a Nifty 50 index fund over the same dated cashflows, computed with the same function.

9.2 A 3-point underperformance over 5 years is a decision to change funds; a 0.4-point gap is noise and does not justify churn.

9.3 Re-run the comparison only at review points (quarterly), because monthly comparisons produce action on noise.

9.4 Record the decision and the date in the log. The value of the tracker is the audit trail, not the percentage.

9.5 Set the review cadence once and keep it. A tracker read daily turns a 5-year plan into 60 small panics.

| XIRR gap vs benchmark | Holding period | Action |
|---|---|---|
| under 1 point | any | none, this is tracking error |
| 1-3 points | under 3 years | re-check next quarter only |
| 1-3 points | over 3 years | review expense ratio and category |
| over 3 points | over 3 years | change the fund, log the reason |

Gate: the benchmark comparison uses the identical function and the identical dates.

## Worked example

A 4-folio portfolio, ₹5,000 monthly across two funds plus one ₹1,00,000 lump sum, valued on 2026-10-31.

| Measure | Value | What it hides |
|---|---|---|
| Total invested | ₹4,60,000 | 60 SIP rows plus one lump sum |
| Current value | ₹5,84,300 | one day's NAV |
| Absolute return | 27.0% | ignores that half the money is 8 months old |
| CAGR | not computable | no single start date |
| XIRR | 15.8% | the number to act on |
| Benchmark XIRR | 14.1% | same dates, index fund cashflows |

The reconciliation step caught 2 duplicate rows worth ₹10,000 that the registrar export had repeated across a folio merge; without it the XIRR read 16.4% instead of 15.8%.

## Quality checklist

- [ ] Cashflow table has date, folio, amount, direction, status per row
- [ ] Dates come from the bank debit, not the allotment date
- [ ] Reversed or failed instalments kept with a status, not deleted
- [ ] Exactly one terminal value per live folio, dated
- [ ] NAV taken from the AMFI file with its date recorded
- [ ] XIRR uses actual days over 365, not month counts
- [ ] Solver refuses to return a rate with no sign change
- [ ] Per-folio invested total reconciles within ₹100
- [ ] Instalment count reconciles, not just the total
- [ ] Absolute return, CAGR and XIRR are each labelled
- [ ] Folios younger than 90 days show "too new", not a rate
- [ ] Switch transactions are not counted as new money
- [ ] Statement is one page and names its valuation date
- [ ] Re-running on the same inputs reproduces the same numbers
- [ ] Benchmark comparison uses the same function and dates
- [ ] Script is standard-library only and under 200 lines

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| XIRR of 62% on a new folio | Annualising 3 weeks of returns | Suppress rates under 90 days of history |
| Two apps disagree by 4 points | One shows absolute return, the other XIRR | Print all three, labelled |
| Invested total is ₹10,000 too high | Duplicate rows after a folio merge | Deduplicate on date, folio, amount |
| XIRR jumps 3 points with no trade | Terminal value came from a stale NAV | Record the NAV file date, warn past 3 days |
| Solver returns -0.99 | No sign change in the cashflow set | Guard before solving, exclude incomplete folios |
| Return looks better than the bank shows | Allotment date used instead of debit date | Take dates from the statement |
| A switch shows as a fresh ₹50,000 investment | Switch treated as two unrelated rows | Net same-date in and out within one folio pair |
| Statement changed after a code edit | Rounding applied inside the loop | Round only at display |
| Missing folio in the total | Units config not updated | Fail on register/config mismatch |
| Same script gives different numbers next month | Config edited without a log | Version the config and log every run |

## Copy-ready agent prompt

> Read the skill at the URL above and build me a working XIRR tracker. Ask me first: how many folios, where the transaction statements come from, the currency, and which date I want the valuation on. Then produce the cashflow CSV schema with date, folio, amount, direction and status, a standard-library Python script that computes XIRR by bisection with a sign-change guard, the reconciliation step that compares my per-folio invested totals and instalment counts against the registrar, and a one-page monthly statement that shows invested, current value, XIRR and the change from last month. Handle folios younger than 90 days and switch transactions explicitly. Stop and tell me which folios do not reconcile before printing any return number.
