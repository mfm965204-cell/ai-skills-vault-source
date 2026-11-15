---
name: emi-prepayment-planner
description: Build a loan amortisation schedule you can reconcile to the lender's statement, then price a prepayment as a guaranteed return before you commit the money.
version: 1.0.0
license: MIT
tags: [finance, loans, amortisation, india, spreadsheet]
---

# EMI Prepayment Planner

Every lender will tell you a prepayment "saves ₹18 lakh in interest". That number is true and useless, because it compares a rupee paid today against interest that would have been paid across 15 years, with no discounting and no mention of what else the money could have done.

This skill builds the amortisation schedule from the loan's own terms, reconciles it to the lender's statement, then prices the prepayment as what it actually is: a guaranteed, tax-adjusted return on the amount you hand over. You end with a schedule you trust, a comparison against the alternative use of the money, and a calendar of payments that does not depend on remembering.

The number that decides everything is the difference between your loan's effective rate and the after-tax return you can earn elsewhere. Everything else is detail.

## When to use this skill

- You have a home, car, personal or education loan and are considering a part-prepayment.
- A lender's foreclosure quote does not match your own arithmetic.
- You are choosing between a shorter tenure and a lower EMI after a windfall.
- You are about to invest a lump sum and want to compare it honestly against prepaying.
- **Do NOT use for:** choosing a lender or negotiating a rate before disbursal, mutual fund or equity selection, or tax filing - this models one existing loan and the decision to prepay it.

## Stage 1 - Fix the loan facts, including the ones lenders hide

An amortisation schedule is only as good as its inputs. Three inputs cause almost every mismatch: the rate basis, the reset date and whether the EMI is a round-number approximation.

1.1 Write down principal outstanding as of a specific date, not the original sanctioned amount.

1.2 Write the annual rate and the basis - monthly reducing, daily reducing, or fixed - because a daily-reducing loan accrues interest on the outstanding balance each day, and that changes the schedule.

1.3 Note the reset clause: floating-rate loans reset on a schedule, and the lender usually keeps the EMI and changes the tenure. A schedule built on the original rate will drift.

1.4 Record the EMI actually debited, including the paise. If the lender rounds the EMI to the nearest rupee, the final payment differs and your schedule must absorb it.

1.5 Note the foreclosure terms: floating-rate home loans typically carry no charge, fixed-rate loans often do. Read the sanction letter, not the marketing page.

1.6 Note the insurance or processing fee bundled into the loan, if any - it is part of the cost, not a separate expense.

Gate: principal, rate, basis, reset date, exact EMI and foreclosure terms are written on one line of the sheet.

## Stage 2 - Build the schedule from first principles

Build it yourself once. A schedule you generated is a schedule you can check, and the lender's statement then becomes a test of your model rather than a black box.

2.1 Start with the outstanding principal and the monthly rate `r = annual / 12 / 100`.

2.2 Each month: interest = outstanding × r, principal repaid = EMI − interest, new outstanding = outstanding − principal repaid.

2.3 Stop when outstanding reaches zero, and let the last payment be the residual rather than the full EMI.

2.4 Write the schedule with one row per month and a running total of interest, because the interest total is the number the decision turns on.

```python
def schedule(principal, annual_pct, emi, extra=0.0, max_months=480):
    r = annual_pct / 12 / 100
    bal, rows, total_int = principal, [], 0.0
    for m in range(1, max_months + 1):
        interest = round(bal * r, 2)
        pay = emi + extra
        principal_paid = round(pay - interest, 2)
        if principal_paid >= bal:
            pay, principal_paid = round(bal + interest, 2), bal
        bal = round(bal - principal_paid, 2)
        total_int += interest
        rows.append((m, pay, interest, principal_paid, bal))
        if bal <= 0:
            break
    return rows, total_int

rows, interest = schedule(48_00_000, 8.6, 41_900)
print(len(rows), "months", round(interest))
```

2.5 Round to paise at every step, exactly as the lender does. Rounding only at the end produces a schedule that drifts by thousands over 20 years.

Gate: the schedule's final balance is zero, the term is a whole number of months, and the interest total is recorded.

## Stage 3 - Reconcile against the lender's statement

Your model is not correct because it looks right. It is correct when it reproduces the lender's own numbers to the rupee.

3.1 Take the lender's latest statement showing opening balance, EMI, interest component and principal component for the last 3 months.

3.2 Compare your schedule's outstanding balance on that date with theirs. A difference under ₹100 is rounding; anything larger is a wrong input.

3.3 If the balances differ, test the four usual causes in order: rate basis, reset date, an EMI that changed, or a part-payment already made and not recorded.

3.4 Check the interest component for one month against theirs to the paisa. That single row validates the rate and the basis at once.

3.5 Record the reconciliation result in the sheet with the statement date, so a later reader knows the model was tested.

| Difference | Most likely cause | What to check |
|---|---|---|
| Under ₹100 | Rounding on the EMI | Nothing, accept it |
| ₹500-5,000 | EMI changed at a rate reset | Sanction letter revision date |
| ₹10,000+ | Unrecorded part-payment or prepayment | Statement's transaction list |
| Interest row off by a few hundred | Daily reducing basis, not monthly | Loan agreement clause on interest |

Gate: the outstanding balance matches the lender's statement within ₹100 on the statement date.

## Stage 4 - Model the prepayment in both forms

Lenders offer two treatments after a prepayment: keep the EMI and shorten the tenure, or keep the tenure and reduce the EMI. They are not equivalent, and the difference is the whole point.

4.1 Tenure reduction: same EMI, new outstanding. Recompute the schedule and note the new term and the new interest total.

4.2 EMI reduction: same remaining term, recomputed EMI on the lower outstanding. Note the new EMI and interest total.

4.3 Compute interest saved for both, and the monthly cash freed for the second option.

4.4 Compare against the option of not prepaying at all - the baseline interest total from Stage 2.

4.5 Record the lender's own prepayment quote beside your figure. A gap above ₹1,000 means a charge or a different accrual basis.

| Option | New EMI | Term left | Total interest | Interest saved | Monthly cash freed |
|---|---|---|---|---|---|
| Do nothing | ₹41,900 | 178 months | ₹26,58,000 | ₹0 | ₹0 |
| Prepay ₹5,00,000, tenure cut | ₹41,900 | 141 months | ₹20,94,000 | ₹5,64,000 | ₹0 |
| Prepay ₹5,00,000, EMI cut | ₹37,540 | 178 months | ₹23,42,000 | ₹3,16,000 | ₹4,360 |

Gate: both forms are modelled, and each has an interest-saved figure and a term in months.

## Stage 5 - Price the prepayment as a return

Interest saved is not a return until you divide it by the money you handed over and annualise it. That division is what makes it comparable to anything else you could do with ₹5,00,000.

5.1 Take the cash flows: outflow of the prepayment today, then the monthly difference in payments against the do-nothing schedule.

5.2 Compute the internal rate of return on those cash flows. For a loan at rate `R` with no charges, the return on prepaying is exactly `R` before tax - that is the anchor to check your model against.

5.3 Add any foreclosure charge to the outflow. A 2% charge on ₹5,00,000 is ₹10,000 and drops the return immediately.

5.4 If the loan carries a tax deduction on interest, compute the after-tax return: the return falls because the interest you no longer pay was partly subsidised. Use your own slab, and confirm the current deduction limits before relying on them.

5.5 State the return as a single number with its tax basis: "8.6% pre-tax, 6.0% after tax at a 30% slab".

5.6 Compute the IRR by bisection so the check needs no extra library, and confirm it lands on the loan rate when there is no charge:

```python
def irr(flows, lo=-0.5, hi=0.5):
    def npv(r):
        return sum(cf / (1 + r) ** i for i, cf in enumerate(flows))
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return round(mid * 12 * 100, 2)

flows = [-5_00_000] + [0] * 177 + [41_900]  # simplified shape
print(irr(flows))
```

Gate: the prepayment has an annualised return, pre-tax and after-tax, with any charge included in the outflow.

## Stage 6 - Compare against the honest alternative

The alternative to prepaying is not "spending it". It is a specific instrument with a specific after-tax return and a specific risk.

6.1 Write the alternative down concretely: a debt fund at 7.1% pre-tax, a fixed deposit at 6.8%, an index fund with no promised return.

6.2 Convert the alternative to after-tax: interest income is taxed at your slab, so a 7.1% debt fund at a 30% slab is about 4.97% net.

6.3 Compare like with like: after-tax return of prepaying against after-tax return of investing, with risk named. Prepayment is a guaranteed return; equity is not.

6.4 Add liquidity to the comparison. Prepaid money is gone and cannot be recalled without a new loan; invested money is available, at market price.

6.5 Write the decision rule before seeing the numbers, then apply it. A common rule: prepay when the after-tax loan rate exceeds the after-tax alternative by at least 1.5 percentage points.

6.6 Record the alternative's lock-in and exit load. A three-year debt fund at 7.1% is not liquid money in month two, and the comparison should say so.

| Use of ₹5,00,000 | Pre-tax return | After-tax at 30% slab | Risk | Liquidity |
|---|---|---|---|---|
| Prepay the loan | 8.6% | 6.02% | None | None |
| Debt fund | 7.1% | 4.97% | Low | High |
| Fixed deposit | 6.8% | 4.76% | None | Medium |
| Index fund | Not promised | Not promised | High | High |

Gate: the alternative is a named instrument with an after-tax figure, and the decision rule was written before the comparison.

## Stage 7 - Sequence multiple prepayments

Most people prepay more than once. Each prepayment changes the schedule for the next one, and the sequence matters more than any single payment.

7.1 Build the plan as a dated list: amount, date, and treatment - tenure cut or EMI cut.

7.2 Apply each prepayment to the schedule at its date, then continue the schedule from the new balance.

7.3 Prefer tenure cut while the EMI is comfortable and the emergency fund is intact; prefer EMI cut when cash flow is tight.

7.4 Keep 6 months of expenses in liquid funds before any prepayment. A prepayment that empties the emergency fund usually ends in a personal loan at 14-18%, which undoes the saving.

7.5 Recompute the plan after each actual payment, and note the difference between plan and reality - it is usually an extra month of interest.

Gate: every planned payment has a date and a treatment, and the emergency fund stays above 6 months of expenses.

## Stage 8 - Stress the plan before you commit

A plan that only works if nothing changes is a plan for a good year. Test the three things that actually happen.

8.1 Rate reset: raise the rate by 100 basis points and recompute. On a ₹48,00,000 loan the EMI rises roughly ₹2,700 a month at that step.

8.2 Income shock: model 6 months with no income and check the emergency fund covers the EMI without a new loan.

8.3 Liquidity test: after the prepayment, how many months of expenses remain liquid? Below 3, do not prepay.

8.4 Write the fallback: which payment is skipped first if income stops, and what it costs in interest.

Gate: all three stresses are modelled, and the plan survives the rate reset without a new borrowing.

## Stage 9 - Produce the one-page plan and the calendar

The deliverable is a page someone can follow in a bad month, and a set of dated reminders so the plan happens without willpower.

9.1 One page: loan facts, current outstanding, planned prepayments with dates, expected term and interest saved.

9.2 One line for the decision: "prepay ₹5,00,000 in March, tenure cut, term falls from 178 to 141 months, interest saved ₹5,64,000".

9.3 Calendar reminders 7 days before each payment date, and one on the date to verify the lender applied it as instructed.

9.4 Verify after each payment: the lender must confirm the treatment. A tenure cut applied as an EMI cut silently costs lakhs.

9.5 Store the schedule file with the loan documents so a later run starts from the real numbers.

Gate: one page, one decision line, reminders set, and a verification step after every payment.

## Quality checklist

- [ ] Principal, rate, basis, reset date and exact EMI are recorded on one line.
- [ ] The schedule rounds to paise at every step.
- [ ] The final balance reaches zero and the term is a whole number of months.
- [ ] One month's interest matches the lender's statement to the paisa.
- [ ] Outstanding balance matches the statement within ₹100.
- [ ] Both tenure-cut and EMI-cut options are modelled.
- [ ] The lender's prepayment quote is compared with your figure.
- [ ] The prepayment has an annualised return, pre-tax and after-tax.
- [ ] Any foreclosure charge is included in the outflow.
- [ ] The alternative is a named instrument with an after-tax return.
- [ ] The decision rule was written before the comparison.
- [ ] The emergency fund stays above 6 months of expenses after prepaying.
- [ ] Rate reset, income shock and liquidity are all modelled.
- [ ] Reminders exist 7 days before each payment date.
- [ ] Each payment's treatment is verified with the lender afterwards.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Schedule drifts from the statement by thousands | Interest computed on the original principal instead of the reducing balance | Recompute interest on outstanding at the start of each month |
| Interest saved looks like ₹18 lakh on a ₹5 lakh payment | Undiscounted comparison across the full remaining term | Annualise the return on the actual cash flows |
| Lender applied EMI cut instead of tenure cut | The instruction was verbal or defaulted in the portal | Send the instruction in writing and verify the treatment afterwards |
| After-tax return overstated | Tax deduction on interest ignored | Reduce the return by the slab rate on the deducted interest |
| Plan collapsed in month 4 | Emergency fund spent on the prepayment | Hold 6 months of expenses liquid before prepaying |
| Two prepayments double-counted | Each modelled from the original schedule | Apply each payment to the running balance at its date |

## Copy-ready agent prompt

> Read the skill at the URL above and build my loan prepayment plan. Ask me for the sanction letter details, the latest statement and my slab, then produce an amortisation schedule reconciled to the statement within ₹100, both prepayment treatments with interest saved, the annualised pre-tax and after-tax return on the prepayment, and a comparison against one named alternative instrument. Finish with a one-page plan, the decision line, a dated reminder list and the verification step after each payment. Do not recommend an investment product.
