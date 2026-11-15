---
name: capital-gains-workbook
description: Turn broker and registrar statements into a per-lot
capital-gains schedule with holding periods, FIFO matching, set-off
logic and a reconciliation against AIS.
version: 1.0.0
license: MIT
tags: [finance, tax, india, spreadsheet, reconciliation]
---

# Capital Gains Workbook

A broker's profit-and-loss statement gives one number per scrip and
hides the lot detail, the holding period and the corporate actions
that changed the cost. Filing from it produces a schedule nobody can
defend and a mismatch against AIS that arrives months later.

This workbook is arithmetic, not advice: every sale matched to a
purchase lot, holding period computed from dates, gains split into the
short and long buckets, losses set off within the rules, and the whole
schedule reconciled against AIS and the broker statement before it
goes to your accountant.

## When to use this skill

- You sold equity, mutual funds or property in the financial year and the broker statement is your only record.
- Two statements disagree: the broker P&L says one figure and AIS says another.
- You have bonuses, splits or dividend reinvestments that changed the cost basis.
- You carried a capital loss forward and need to know which year it can be used in.

Do NOT use for: filing the return itself, or deciding whether to sell
— this builds a schedule for a qualified professional to check. Tax
rules and rates change with each Finance Act; confirm every threshold
on the income-tax portal for the year you are filing.

## Stage 1 — Collect every record before computing anything

One missing contract note is a wrong number in every row it touches.

1.1 Gather four sources: broker contract notes or the annual P&L, the registrar's consolidated statement (CAMS or KFintech) for mutual funds, AIS from the income-tax portal, and bank statements for the credit dates.

1.2 Export each to a table with at least: scrip or scheme, ISIN, transaction date, units, price, amount, and the transaction type.

1.3 Record the statement's generation date; a P&L generated in April may exclude a March trade settled in April.

| Source | Covers | Use it for | Known gap |
|---|---|---|---|
| Broker P&L | listed equity, some funds | sale proceeds, charges | lot detail often missing |
| Registrar CAS | mutual funds | units, NAV, dates | no cost for transferred folios |
| AIS | everything reported | reconciliation | arrives after the year closes |
| Bank statement | cash | credit dates | no security detail |

Gate: all four sources collected, with the generation date recorded on
each.

## Stage 2 — Classify every instrument first

The rules depend on the class, and a fund misclassified produces a
wrong holding period and a wrong bucket.

2.1 Classify each line: listed equity share, equity-oriented mutual fund, debt or hybrid fund, unlisted share, property, or other.

2.2 Confirm equity orientation of a fund from the scheme's stated allocation, not from its name — a "balanced" fund can be either.

2.3 Keep the class in its own column and never infer it in a formula.

Gate: every line has a class, and no line has a class derived from the
scheme name alone.

## Stage 3 — Compute the holding period from the dates

The holding period decides the bucket, and the date used is the one in
the rules for that class, not the settlement date.

3.1 Compute months held between the acquisition date and the transfer date, then apply the class rule: listed equity and equity funds are long-term above 12 months, most other assets above 24 months, and the exact thresholds for each class must be confirmed for the year you file.

3.2 Use the actual dates, not month buckets; a purchase on 10 April and a sale on 9 April two years later is short of the threshold by one day.

3.3 Handle the 12-month edge explicitly with a column that shows days held, so a one-day error is visible.

```python
from datetime import date
def is_long_term(buy: date, sell: date, months: int) -> bool:
    # long-term when held strictly more than `months` months
    y, m = buy.year + (buy.month - 1 + months) // 12, (buy.month - 1 + months) % 12 + 1
    boundary = date(y, m, min(buy.day, 28))
    return sell > boundary
```

Gate: every row shows days held, and the rows within 30 days of a
threshold are reviewed by hand.

## Stage 4 — Match sales to lots by FIFO

Without lot matching, a sale of 100 units against three purchases
produces one gain and three wrong holding periods.

4.1 Match each sale against the earliest unmatched purchase for that ISIN, in date order — first in, first out.

4.2 Carry the acquisition date and cost forward from the matched lot, not from an average price.

4.3 Reconcile units: for each ISIN, purchases plus bonuses and splits minus sales must equal the closing balance, with a tolerance of zero.

```text
ISIN INE002A01018
 buys   100 @ 2,400.00 on 2024-05-10
         50 @ 2,700.00 on 2024-11-02
 bonus   25 on 2025-03-01 (cost allocated pro rata)
 sells   120 @ 3,100.00 on 2026-06-15
 match   100 from lot 1, 20 from lot 2 (FIFO)
 units check: 100 + 50 + 25 - 120 = 55 closing
```

Gate: the unit reconciliation balances for every ISIN with zero
tolerance.

## Stage 5 — Adjust cost for corporate actions

A split or bonus that is not applied turns a small gain into a large
fake one.

5.1 For a split, divide the cost per unit and multiply the units by the same ratio; total cost is unchanged.

5.2 For a bonus, add the units at zero cost and re-allocate the original cost across the total units.

5.3 For a dividend reinvestment, treat each reinvestment as a fresh purchase with its own date — it starts its own holding period.

| Event | Units | Total cost | Per-unit cost | Holding period |
|---|---|---|---|---|
| Split 1:2 | doubles | unchanged | halves | continues from original |
| Bonus 1:2 | increases | unchanged | falls | continues from original |
| Reinvestment | increases | increases | new price | restarts |

Gate: every corporate action is applied to the matched lot, and total
cost across the ISIN is unchanged by splits and bonuses.

## Stage 6 — Split into buckets and aggregate

Two totals per class: short-term and long-term. Nothing else on the
summary page.

6.1 Compute gain per lot as proceeds minus adjusted cost minus allowable charges, and keep charges in their own column so they can be removed if the rules differ.

6.2 Sum by class and bucket, and keep the lot-level sheet as the evidence behind each total.

6.3 Round only at the summary, to two decimals, never at the lot level.

Gate: the sum of lot-level gains equals each bucket total exactly, and
the lot sheet is retained.

## Stage 7 — Apply set-off and carry-forward correctly

Losses have their own rules, and applying them wrongly overstates the
tax and the refund later.

7.1 Set off a short-term capital loss against short-term and long-term gains; set off a long-term loss only against long-term gains.

7.2 Carry forward an unused capital loss for the number of years the rules allow — currently 8 assessment years — and only against capital gains, never against salary or other income.

7.3 Keep a carry-forward register with the year of origin, the amount and the amount used, because the portal asks for it year after year.

| Loss type | Against STCG | Against LTCG | Against other income | Carry forward |
|---|---|---|---|---|
| Short-term | yes | yes | no | yes |
| Long-term | no | yes | no | yes |
| Speculative business | no | no | own head only | yes |

Gate: every loss is used in the correct order, and the carry-forward
register reconciles with the amounts claimed.

## Stage 8 — Reconcile against AIS before filing

AIS is what the department already knows. A mismatch is a notice
waiting to happen.

8.1 Match AIS sale values to your schedule by ISIN and total proceeds; investigate any difference above 1% or ₹1,000, whichever is smaller.

8.2 The usual causes are a sale reported in a different year, a transfer between brokers, and a sale of units bought through an older folio.

8.3 Write down the explanation for each unresolved difference, so the question, when it comes, has an answer already.

Gate: every AIS line is matched or explained, and the unexplained
total is zero.

## Stage 9 — Hand off a schedule your accountant can check

The deliverable is a workbook with a summary page and an evidence
sheet, not a number in an email.

9.1 Summary page: totals by class and bucket, set-off applied, carry-forward carried, and the rates left as input cells to be filled from the current Finance Act.

9.2 Evidence page: every lot with dates, units, cost, proceeds, charges and the source document name.

9.3 A one-page note listing the assumptions, the rules version used, and the three largest items by value.

Gate: a reviewer can trace every summary figure to lot rows and to a
named source document.

## Worked example - a mismatched AIS resolved in one evening

A salaried investor with 240 transactions across 3 brokers and 2
registrars.

| Step | Finding | Effect |
|---|---|---|
| Unit reconciliation | 2 ISINs did not balance | a 2024 bonus was never recorded |
| FIFO matching | 61 of 240 sales crossed lots | 18 rows changed bucket |
| Holding period | 4 rows within 30 days of the threshold | 1 row flipped to long-term |
| AIS match | ₹4,20,000 unexplained | a transfer between brokers |
| Set-off | short-term loss ₹38,000 | applied to short-term gain |
| Carry forward | ₹0 remaining | register closed for the year |

The unit imbalance was the whole story. A 1:1 bonus in 2024 had never
been recorded, so 120 units had no acquisition date and the broker had
treated them as zero-cost sales in the short-term bucket. Adding the
bonus at the correct date moved those units to long-term and reduced
the schedule's short-term total by more than a third of the original
figure.

The AIS mismatch was a share transfer between two brokers in the same
year: one broker reported the sale, the other reported the purchase,
and AIS showed only the sale. The explanation was a single line with
both contract note numbers.

The four rows near the threshold were checked by hand and one was a
genuine one-day error, because the acquisition date had been taken
from the settlement date rather than the trade date.

## Quality checklist

- [ ] All four source documents collected with generation dates.
- [ ] Every line classified by instrument class.
- [ ] Equity orientation confirmed from allocation, not the fund name.
- [ ] Days held computed for every row.
- [ ] Thresholds confirmed for the year being filed.
- [ ] Rows within 30 days of a threshold reviewed by hand.
- [ ] FIFO matching applied per ISIN.
- [ ] Unit reconciliation balances with zero tolerance.
- [ ] Splits and bonuses applied without changing total cost.
- [ ] Reinvestments treated as fresh purchases with their own date.
- [ ] Lot-level gains sum exactly to bucket totals.
- [ ] Losses set off in the permitted order only.
- [ ] Carry-forward register with year of origin and amount used.
- [ ] Every AIS line matched or explained.
- [ ] Summary and evidence pages ready for a professional to check.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Short-term total far larger than expected | A bonus or split never recorded, so units appear as zero-cost sales | Add the corporate action and re-run FIFO matching |
| Two brokers give different totals | One uses average cost and the other FIFO | Rebuild from lot level for both and compare units, not totals |
| A one-day holding period error | Acquisition date taken from settlement rather than trade | Use the trade date from the contract note |
| AIS shows more proceeds than the schedule | A transfer between brokers reported as a sale | Match by ISIN and document the transfer with both notes |
| Loss set off against salary | A capital loss treated as a general loss | Restrict set-off to capital gains and carry the rest forward |
| Rates hardcoded in the sheet | A previous year's workbook reused | Keep rates as input cells filled from the current Finance Act |
| Schedule cannot be traced | Only the summary page kept | Retain the lot-level evidence sheet with source document names |

## Copy-ready agent prompt

> Read the skill at the URL above and build my capital-gains workbook. Collect broker P&L, registrar CAS, AIS and bank records with their generation dates, classify every instrument, compute days held per row, match sales to purchase lots by FIFO, apply splits, bonuses and reinvestments, and produce lot-level gains split into short and long buckets with losses set off in the permitted order and a carry-forward register. Reconcile every AIS line and explain each difference. Deliver a summary page and an evidence page, with tax rates left as input cells for my accountant to fill from the current Finance Act. Stop and show me any ISIN whose unit reconciliation does not balance.
