---
name: runway-cashflow-model
description: Build a 12-month cashflow model that shows the month you run out of money, with the drivers, the collection lag and the three levers that move the date.
version: 1.0.0
license: MIT
tags: [finance, cashflow, runway, spreadsheet, startup, india]
---

# Runway Cashflow Model

A profit-and-loss sheet can be positive while the bank account is empty, because revenue is booked when invoiced and cash arrives 30-75 days later. Founders who track only revenue discover the gap in the month the salary run fails.

This skill builds a 12-month cash model driven by five inputs - starting cash, monthly collections, monthly spend, the collection lag, and one-off items - and outputs the month cash goes negative, the buffer at each month end, and the three levers ranked by how many days they buy. You end with one page you update in 10 minutes a month.

## When to use this skill

- You know this month's bank balance but not the balance 5 months out.
- Revenue is growing and cash is shrinking and nobody can explain the difference.
- You are about to hire 2 people and need to know whether the hire pushes the zero month closer.
- An investor or lender asked for a runway number and you answered from memory.

Do NOT use for: statutory accounts, tax provisioning, or valuation work. This is a management model for decisions, it is not a filing, and it should be checked by an accountant before it supports a loan application.

## Stage 1 - Fix the opening balance to one number

1.1 Take the bank balance on a fixed date and reconcile it to the ledger. Opening cash is the one input you cannot estimate.

1.2 Add cash you can access this week: undrawn overdraft, a confirmed but undrawn loan tranche. Exclude receivables and anything not yet collected.

1.3 Subtract committed outflows already due in the next 30 days: salaries, rent, GST payable, card settlement, vendor dues.

1.4 Write the resulting number as `opening_cash`. It will be lower than the bank app shows, and it is the number that matters.

| Component | Include | Exclude |
|---|---|---|
| Bank balance | yes, reconciled | |
| Undrawn overdraft | yes, if sanctioned | |
| Confirmed loan tranche | yes, if signed | |
| Receivables | | not cash until collected |
| Pipeline | | not cash at all |
| Card dues next 30 days | | subtract |

Gate: `opening_cash` is within ₹1,000 of a statement you can print.

## Stage 2 - Model collections with the lag, not the invoice date

2.1 Take the last 6 months of invoices and the dates they were actually paid. Compute the median days-to-payment, not the mean - one 120-day outlier distorts a mean badly.

2.2 Split customers into 2 groups at most: those that pay under 30 days and those that do not. More groups is false precision on 20 invoices.

2.3 Convert invoiced revenue into collections by shifting each month's amount forward by the lag. A ₹10,00,000 month at a 45-day lag lands 1.5 months later.

2.4 Apply a collection rate: the fraction of invoiced value you historically actually collect within 120 days. Use your own last 12 months, not an industry number.

```python
import statistics
def lag_profile(pairs):
    days = [(paid - inv).days for inv, paid in pairs if paid]
    return {"median": statistics.median(days),
            "p75": sorted(days)[int(len(days) * 0.75)],
            "n": len(days)}

print(lag_profile([(d1, d2) for d1, d2 in invoice_pairs]))
```

2.5 Treat advance payments as negative lag: the cash arrives before the invoice. If 20% of your revenue is prepaid, that is a real runway advantage and it belongs in the model.

2.6 Recompute the lag every quarter. A lag that moved from 38 to 55 days is a 6-week cash event and it will not announce itself.

Gate: the lag you use sits inside the p25-p75 band of your own history, and you can name the customers that sit outside it.

## Stage 3 - Build spend as fixed, variable and lumpy

3.1 Fixed: salaries, rent, subscriptions, loan EMI. These do not move with revenue and they are the floor of the model.

3.2 Variable: cost of delivery, contractor payments, payment-gateway fees, ad spend. Model as a percentage of collections, so a slow month also spends less.

3.3 Lumpy: annual insurance, GST advance, equipment, hiring bonuses. Place each one in the month it actually leaves the account.

3.4 Add a 7-10% buffer line on top of fixed and variable. Every model built without a buffer has been wrong by roughly that much.

| Bucket | Driver | Test of correctness |
|---|---|---|
| Fixed | contract or schedule | matches last 3 bank debits |
| Variable | % of collections | within 5 points of last quarter |
| Lumpy | dated event | one row per event, with a date |
| Buffer | 7-10% of the above | never zero |

3.5 Put the model's monthly outflow next to last month's actual bank debits, line by line. Any line that differs by more than ₹2,000 is either a missing cost or a double count.

Gate: last month's actual spend is reproduced by the model within 5%.

## Stage 4 - Assemble the 12-month grid

4.1 Rows: opening cash, collections, other inflows, fixed, variable, lumpy, buffer, net movement, closing cash.

4.2 Columns: 12 months, one column each, with the month label as text (`Nov-26`) not a date, so sorting never reorders the year.

4.3 Closing cash of month N is opening cash of month N+1. One formula, copied across; a hardcoded chain breaks the first time a column is inserted.

4.4 Add a `runway_months` row: the count of months until closing cash goes below zero, computed with a formula, not by eye.

```excel
B10: =B4-B5-B6-B7-B8-B9        net movement
B11: =B3+B10                   closing cash
C3 : =B11                      next month opening
B12: =MATCH(TRUE, B11:M11<0, 0) month index of first negative
```

Gate: the closing cash of month 12 equals opening cash plus the sum of net movements, to the rupee.

## Stage 5 - Read the zero month, not the runway headline

5.1 Find the first month where closing cash is below zero. That month is the decision point, and everything else is context.

5.2 Compute the buffer at each month end as closing cash divided by that month's total outflow. Under 1.0 means you cannot cover one month of spend.

5.3 Distinguish `runway` (months to zero at current burn) from `zero_month` (the calendar month). A runway of 7 months starting in November ends in June, and June has a GST payment in it.

5.4 Note the two months with the worst buffer, not just the first negative one. Seasonal businesses usually break in the second-worst month.

| Metric | Formula | Red flag |
|---|---|---|
| Zero month | first closing cash below 0 | within 6 months |
| Runway | months to zero | under 6 |
| Buffer | closing cash / monthly outflow | under 1.0 |
| Collection lag | median days to payment | over 45 |

Gate: you can state the zero month and the buffer in that month without opening the model.

## Stage 6 - Test the three levers that actually move the date

6.1 Lever one, collect faster: cut the lag by 15 days. Model the effect on the zero month - for most service businesses this is the largest single lever.

6.2 Lever two, cut spend: reduce fixed cost by 10%. Model it as a step change from a chosen month, not from month one.

6.3 Lever three, raise revenue: a 20% collection increase is the slowest lever, because it arrives after the lag and usually costs cash first.

6.4 Rank the levers by days of runway gained per rupee of effort. Faster collection is almost always first and is almost always the one nobody has tried.

| Lever | Model change | Typical runway gain | Cash cost |
|---|---|---|---|
| Lag -15 days | shift collections earlier | 2-4 weeks | none |
| Fixed -10% | step change | 2-6 weeks | severance risk |
| Revenue +20% | collections up, lagged | 3-8 weeks | delivery cost first |
| Delay a hire by 1 quarter | remove a lumpy row | 4-10 weeks | capacity risk |

6.5 Test the levers in combination, not only alone. Cutting the lag by 15 days and deferring one hire usually beats any single lever by a wide margin.

6.6 Write the rejected levers down with the reason. "We will not cut the delivery team" is a decision, and it stops the same debate every month.

Gate: each lever has a modelled number, and the ranked list fits on one line each.

## Stage 7 - Add the stress cases that decide survival

7.1 Case A: the two largest customers pay 30 days late. Model it by shifting their collections one month.

7.2 Case B: collections fall 25% for 3 months, spend unchanged. This is the case that kills businesses that look fine.

7.3 Case C: a lumpy cost lands early - GST, an annual premium, a security deposit.

7.4 Keep the base case visible next to each stress case. A stress number without a base to compare against is unreadable.

7.5 Set the action for each stress case now, while it is hypothetical: which cost stops, on what date, who decides. A stress case with no pre-agreed action is entertainment.

Gate: in the base case you survive 12 months, and in Case B you can name the month you would act.

## Stage 8 - Wire the model to monthly actuals

8.1 Each month, paste the actual collections, actual spend and actual closing cash into an `actuals` block beside the forecast.

8.2 Show forecast versus actual for the last 3 months and the variance in rupees. A model that is never compared to reality is a story.

8.3 If variance exceeds 15% for 2 months running, rebuild the driver that is wrong rather than nudging the output.

8.4 Keep a version per month (`model-2026-11.xlsx`). Overwriting the old one removes the only evidence of what you believed.

8.5 Print the model to one page for anyone who will not open a spreadsheet: opening cash, zero month, buffer, and the ranked levers.

```python
# grid.py - rebuild the 12-month grid from five drivers
months = 12
cash = opening_cash
rows = []
for m in range(months):
    collected = collections[m] * collection_rate
    outflow = fixed + collected * variable_pct + lumpy.get(m, 0)
    outflow *= 1 + buffer_pct
    cash += collected - outflow
    rows.append({"month": m + 1, "collected": round(collected),
                 "outflow": round(outflow), "closing": round(cash),
                 "buffer": round(cash / outflow, 2)})
zero = next((r["month"] for r in rows if r["closing"] < 0), None)
print(zero, rows)
```

Gate: three months of forecast-versus-actual are visible in the same file.

## Stage 9 - Turn the model into a weekly decision habit

9.1 Once a week, check two numbers: bank balance and the collections expected in the next 14 days.

9.2 If the 14-day expected collections are below the 14-day committed outflows, act that week, not at month end.

9.3 Keep a written trigger: "if closing cash forecast for month N drops below ₹X, we cut Y within 7 days". A trigger agreed in advance is executed; one invented under pressure is argued about.

9.4 Review the zero month only when a driver changes. Watching it daily produces decisions on noise.

Gate: a trigger exists in writing, with a rupee threshold and an action.

## Worked example

A 9-person agency, opening cash ₹18,00,000, invoicing ₹12,00,000 a month with a 50-day collection lag.

| Month | Collections | Total outflow | Closing cash | Buffer |
|---|---|---|---|---|
| Nov-26 | ₹9,50,000 | ₹14,20,000 | ₹13,30,000 | 0.94 |
| Dec-26 | ₹10,80,000 | ₹14,60,000 | ₹9,50,000 | 0.65 |
| Jan-27 | ₹11,60,000 | ₹15,10,000 | ₹6,00,000 | 0.40 |
| Feb-27 | ₹12,20,000 | ₹15,40,000 | ₹2,80,000 | 0.18 |
| Mar-27 | ₹12,40,000 | ₹16,20,000 | -₹1,00,000 | negative |

The zero month was March 2027 at a 50-day lag. Cutting the lag to 35 days moved it to May and added 9 weeks of runway; a 10% fixed-cost cut moved it to April. The lag lever was free.

## Quality checklist

- [ ] Opening cash reconciled to a printable statement
- [ ] Only accessible cash counted, receivables excluded
- [ ] Collection lag is the median of 6+ months of your own data
- [ ] Collection rate based on 12 months of your own collections
- [ ] Spend split into fixed, variable and lumpy
- [ ] A 7-10% buffer line exists and is not zero
- [ ] Closing cash of month N is opening cash of month N+1 by formula
- [ ] Zero month identified by formula, not by eye
- [ ] Buffer computed for every month, worst two named
- [ ] Three levers modelled with runway gained in weeks
- [ ] Three stress cases modelled beside the base case
- [ ] Forecast versus actual shown for the last 3 months
- [ ] A version of the model saved each month
- [ ] A written trigger with a rupee threshold and an action
- [ ] Model reproduces last month's actual spend within 5%
- [ ] Owner named for the weekly 14-day check

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Model says fine, bank says empty | Revenue booked on invoice date, not collection date | Shift collections by the measured lag |
| Runway changes wildly each month | Lag and collection rate re-estimated from memory | Fix both drivers to trailing 6-12 month data |
| Closing cash jumps at a column insert | Hardcoded cash chain | One formula per row, copied across |
| Zero month missed by a month | Lumpy costs left out | One row per dated event, in its real month |
| Forecast always 15% optimistic | No buffer line | Add 7-10% buffer and compare to actuals |
| Stress case unreadable | Only the bad case shown | Base case beside every stress case |
| Nobody acts until it is too late | No pre-agreed trigger | Written threshold with a named action and owner |
| Investor number disagrees with model | Runway quoted from memory | Quote the zero month and buffer from the file |
| Model rebuilt every quarter | Drivers too fragile to maintain | Five drivers only, everything else derived |
| Two people get two answers | Two files, two versions | One file per month, dated, single owner |
| Zero month moves a month earlier every review | Lag growing and never re-measured | Recompute the lag quarterly from paid dates |
| Model shows cash you cannot spend | Undrawn facilities counted as cash | Only count sanctioned and drawable amounts |
| Lever list never acted on | No owner, no date on the action | One owner and one date per lever |

## Copy-ready agent prompt

> Read the skill at the URL above and build me a 12-month cashflow model as a spreadsheet. Ask me: current reconciled bank balance, monthly invoiced revenue for the last 6 months with payment dates, monthly spend split into fixed and variable, any lumpy costs with dates, and the collection lag I actually see. Then build the grid with opening cash, collections, fixed, variable, lumpy, buffer and closing cash, a formula-driven zero month and runway, buffer per month, three levers ranked by weeks of runway gained, and three stress cases beside the base case. Finish with the weekly 14-day check and a written trigger with a rupee threshold. Show me the zero month and the two worst buffer months in the first line of your answer.
