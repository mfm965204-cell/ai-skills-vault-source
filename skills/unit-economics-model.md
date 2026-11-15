---
name: unit-economics-model
description: Build a per-customer unit economics model with real cohort data - CAC, contribution margin, payback and LTV - and the three numbers that decide whether growth is worth funding.
version: 1.0.0
license: MIT
tags: [finance, unit-economics, saas, growth, india]
---

# Unit Economics Model

Most unit economics decks are a marketing slide with arithmetic added afterwards: blended CAC from a spreadsheet, an LTV that assumes nobody ever leaves, and a payback period that ignores the discount you gave to close the deal. The model is wrong in a way that only shows up after the money is spent.

This skill builds the model from transaction rows instead: one row per customer, one column per cost that follows the customer, and three outputs - contribution margin per order, months to payback and LTV at the retention you actually observe. It ends in a sheet you can defend line by line and a decision about whether to spend the next ₹10,00,000 on acquisition.

The test of a unit economics model is not elegance. It is that a finance reviewer can trace any number in it back to a row in a source export.

## When to use this skill

- An investor asks for payback period and you have only a blended CAC.
- Growth is expensive and nobody can say whether the tenth customer in a month is profitable.
- You are choosing between two channels with very different order sizes.
- A discount scheme looks like it works in revenue and you suspect it does not in margin.
- **Do NOT use for:** building a cash runway forecast (that is a separate model), pricing a single product from scratch, or company-level P&L budgeting - this is per-customer only.

## Stage 1 - Define the customer and the period before any maths

A model built on the wrong unit is unrecoverable. Decide whether the customer is a person, a household or an account, and whether the period is a month, an order or a subscription cycle. Write both down at the top of the sheet.

1.1 Write the unit definition in one sentence: "a customer is one GSTIN for business accounts, one phone number for consumers".

1.2 Write the period definition: "a period is one calendar month from signup date".

1.3 Name the cohort key - signup month, not first-order month. First-order cohorts hide the customers who never ordered.

1.4 Fix the currency and tax basis now: all figures in ₹, net of GST, gross of discount.

1.5 Record the export date and the source system for every input file.

Gate: one unit, one period, one cohort key, one currency - written at the top of the sheet.

## Stage 2 - Pull one row per customer, not one row per order

Order-level exports double-count customers and make retention invisible. Aggregate to the customer level first, then attach cost.

2.1 Export orders with customer id, order date, gross value, discount, refunds and COGS.

2.2 Roll up to one row per customer with `first_order_date`, `orders`, `gross`, `discounts`, `refunds` and `cogs`.

2.3 Compute contribution margin per customer as `gross - discounts - refunds - cogs - payment_fee`. Payment fees are frequently 1.8-2.2% of gross on Indian gateways; take the actual rate from your settlement report.

2.4 Drop internal test accounts and anything with a null customer id, and log both counts.

2.5 Keep a `source_rows` count per customer so you can show that 1,840 orders became 612 customers.

```python
import pandas as pd

o = pd.read_csv("orders_2026-09.csv", parse_dates=["order_date"])
o = o[o["customer_id"].notna() & ~o["email"].str.contains("yourdomain", na=False)]
o["cm"] = o["gross"] - o["discount"] - o["refund"] - o["cogs"] - o["payment_fee"]
cust = o.groupby("customer_id").agg(
    first_order=("order_date", "min"), orders=("order_id", "count"),
    gross=("gross", "sum"), cm=("cm", "sum")).reset_index()
print(len(o), len(cust), round(cust["cm"].sum(), 2))
```

Gate: customer row count is smaller than order row count, and total contribution margin matches the finance P&L to within 1%.

## Stage 3 - Split acquisition cost by channel, not in total

Blended CAC hides the channel that is losing money. Every rupee of spend must land on a channel, and every channel must land on a customer.

3.1 Export ad spend, agency fees, sales salaries and tooling per channel per month.

3.2 Attribute customers to channels using your own rule - last click, first click, or self-reported on signup. Pick one and never mix rules within a run.

3.3 Divide channel spend by attributed customers to get channel CAC. Leave unattributed customers in a fifth bucket named `unattributed`; do not spread them.

3.4 Include the salaries of people who only do acquisition. Excluding them makes CAC look 30-40% better than it is.

| Channel | Spend | New customers | CAC | CM per customer | CAC/CM |
|---|---|---|---|---|---|
| Meta ads | ₹4,80,000 | 1,200 | ₹400 | ₹620 | 0.65 |
| Google search | ₹3,20,000 | 640 | ₹500 | ₹620 | 0.81 |
| Referral | ₹60,000 | 400 | ₹150 | ₹620 | 0.24 |
| Sales-led | ₹6,50,000 | 210 | ₹3,095 | ₹4,800 | 0.64 |

3.5 Recompute CAC monthly for the last 6 months. A CAC that is flat while spend triples is a sign the attribution is broken.

Gate: channel spend sums to total acquisition spend, and attributed customers plus unattributed equals total new customers.

## Stage 4 - Measure retention on cohorts, not on averages

An average retention curve is a fiction produced by mixing old and new customers. Use cohorts and read the curve at months 1, 3, 6 and 12.

4.1 Build a cohort table: rows are signup months, columns are months since signup, values are active customers.

4.2 Compute the month-1 retention first. If it is below 25% for a consumer subscription or below 85% for a B2B retainer, LTV is not worth computing yet - fix the product.

4.3 Fit a simple retention decay by taking the observed curve at 3, 6 and 12 months. Do not fit an exponential and extrapolate to 60 months.

4.4 Cap the LTV horizon at the longest observed cohort plus 6 months. Beyond that you are forecasting, not measuring.

4.5 Write the retention source beside the table: which system, which definition of active, which date.

4.6 Report the cohort size beside every retention percentage. A 92% retention on 11 customers is not a finding.

Gate: retention is reported per cohort at 4 checkpoints, and no LTV uses a horizon longer than the observed data plus 6 months.

## Stage 5 - Compute payback in months, not in multiples

Payback is the number a cash-constrained business actually runs on. It is cumulative contribution margin divided by CAC, expressed in months.

5.1 For each channel, take monthly contribution margin per customer from the retention curve and accumulate it month by month.

5.2 Payback month is the first month where cumulative contribution margin is greater than or equal to CAC.

5.3 Report payback for each channel separately, plus a blended figure that finance can tie to the bank statement.

5.4 Set the internal limit before you look at results - for most Indian SMB and D2C businesses 6 months is healthy, 12 is a stretch, beyond 18 needs outside capital.

```python
import numpy as np

def payback(cac, monthly_cm):
    cum = np.cumsum(monthly_cm)
    hit = np.where(cum >= cac)[0]
    return int(hit[0]) + 1 if len(hit) else None

print(payback(400, [620, 310, 210, 160, 130, 110]))
```

5.5 Show payback as a cumulative table, not only as a single month, so a reviewer can see the shape of the curve.

| Month | Monthly CM | Cumulative CM | CAC | Paid back |
|---|---|---|---|---|
| 1 | ₹620 | ₹620 | ₹400 | Yes |
| 2 | ₹310 | ₹930 | ₹400 | Yes |
| 3 | ₹210 | ₹1,140 | ₹400 | Yes |
| 6 | ₹110 | ₹1,610 | ₹400 | Yes |

Gate: every channel has a payback month or an explicit "not within 24 months" verdict.

## Stage 6 - Compute LTV on contribution margin, never on revenue

LTV on revenue flatters every business. Use contribution margin, discounted at your cost of capital, and cap the horizon.

6.1 Sum monthly contribution margin per customer over the capped horizon.

6.2 Discount at your actual cost of borrowing or the return you would need on equity - 12% annual is a common internal floor; use your own number and label it.

6.3 Report LTV as a range from the observed curve, not a single figure.

6.4 Compute LTV to CAC per channel and flag anything below 3 as under-funded, anything below 1 as loss-making.

6.5 Publish the LTV range with its two ends named - low end from the worst cohort, high end from the best - so nobody quotes the top of the range as the number.

Gate: LTV is expressed in contribution margin, discounted, horizon-capped, and reported as a range.

## Stage 7 - Stress the model with the three cases that matter

A model that only works at plan is not a model. Run three cases and see which channel survives.

7.1 Base case: current CAC, current retention, current margin.

7.2 Cost case: CAC up 30%, which is what happens when you double spend in one channel.

7.3 Margin case: contribution margin down 15% from a discount campaign or a supplier price rise.

7.4 Record which channels still pay back inside your limit in all three cases. Those are the ones you can scale.

7.5 Add a fourth case only if it is a real risk you can name - a gateway fee change, a supplier price rise, a platform policy change - never a generic "worst case".

| Case | Meta payback | Google payback | Referral payback | Verdict |
|---|---|---|---|---|
| Base | 1 month | 1 month | 1 month | All viable |
| CAC +30% | 2 months | 2 months | 1 month | All viable |
| Margin -15% | 2 months | 3 months | 2 months | All viable |
| CAC +30% and margin -15% | 3 months | 4 months | 2 months | Scale referral first |

Gate: every channel has a payback figure under all three cases, and the worst case is still inside your limit for at least one channel.

## Stage 8 - Hand the sheet to finance with its assumptions listed

Finance will not trust a model whose assumptions are buried in formulas. Put every assumption on one visible block with its source.

8.1 List each assumption with a value, a source and an owner: payment fee 2%, refund rate 4%, COGS 38%, discount 6%, cost of capital 12%.

8.2 Mark every cell that is an assumption in a single colour, and every cell that is a formula in another. Two colours, no more.

8.3 Protect the formula cells so a reviewer cannot overwrite a calculation while checking a number.

8.4 Add a reconciliation tab that ties total contribution margin to the P&L and total spend to the bank statement.

8.5 Publish the assumption block as a small text file beside the sheet, so a later run diffs assumptions instead of eyeballing them:

```yaml
payment_fee_pct: 2.0
refund_rate_pct: 4.0
cogs_pct: 38.0
discount_pct: 6.0
cost_of_capital_pct: 12.0
source: settlement_report_2026-09 + pnl_2026-09
```

Gate: every assumption is on one block with a source, and both reconciliations show zero difference.

## Stage 9 - Write the decision the model supports

The deliverable is a decision, not a spreadsheet. One page, three numbers, one recommendation.

9.1 State the three numbers: blended CAC, blended payback in months, LTV to CAC.

9.2 Name the channel to scale, the channel to pause and the channel to fix, with the payback that justifies each.

9.3 Give the spend that follows: "₹10,00,000 into referral at ₹150 CAC buys about 6,600 customers, recovered in month 2".

9.4 State what would change the decision: a CAC rise past ₹250 on referral, or month-1 retention falling below 20%.

9.5 Date the model and note the next refresh - a monthly refresh for anything spending above ₹5,00,000 a month, quarterly below that.

Gate: one page, three numbers, one recommendation, one stated condition that would reverse it.

## Quality checklist

- [ ] The customer unit, period and cohort key are written at the top of the sheet.
- [ ] Orders are aggregated to one row per customer before any cost is attached.
- [ ] Contribution margin subtracts discounts, refunds, COGS and payment fees.
- [ ] Channel spend sums to total acquisition spend with nothing left over.
- [ ] Unattributed customers sit in their own bucket and are not spread.
- [ ] Acquisition salaries are included in CAC.
- [ ] Retention is reported per cohort at months 1, 3, 6 and 12.
- [ ] No LTV horizon exceeds the observed data plus 6 months.
- [ ] Payback is computed per channel and blended.
- [ ] LTV uses contribution margin, discounted, as a range.
- [ ] All three stress cases are run and recorded.
- [ ] Every assumption has a value, a source and an owner on one block.
- [ ] Contribution margin reconciles to the P&L within 1%.
- [ ] The one-page decision names a channel to scale and one to pause.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| CAC looks impossibly low | Acquisition salaries excluded from spend | Add salary cost for acquisition-only roles to the channel |
| LTV to CAC above 10 | LTV computed on revenue and extrapolated 60 months | Recompute on contribution margin, cap the horizon at observed plus 6 |
| Every channel looks identical | Spend spread evenly across channels instead of attributed | Attribute per channel, keep unattributed as its own bucket |
| Payback improves when spend doubles | CAC taken as a constant while spend scaled | Recompute CAC per month and stress it at plus 30% |
| Finance cannot tie the sheet to the P&L | Margin computed before payment fees and refunds | Add both to the contribution margin line and reconcile |
| Retention curve looks flat and too good | Active defined as "has an account", not "ordered this month" | Define active as a transaction in the period |

## Copy-ready agent prompt

> Read the skill at the URL above and build my unit economics model. Ask me for the orders export, the channel spend export and my retention definition, then produce one customer-level sheet with contribution margin, channel CAC, cohort retention at months 1, 3, 6 and 12, payback per channel and a discounted LTV range. Run the base, CAC plus 30% and margin minus 15% cases, list every assumption with its source, and finish with a one-page decision naming the channel to scale and the condition that would reverse it.
