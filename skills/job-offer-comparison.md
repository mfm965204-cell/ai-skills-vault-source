---
name: job-offer-comparison
description: Compare two or more job offers on take-home cash, equity that may never vest, and the non-cash terms that decide the first year, then commit to one.
version: 1.0.0
license: MIT
tags: [career, offers, compensation, negotiation, india]
---

# Job Offer Comparison

Two offers that both say "₹28 lakh" are rarely the same offer. One is ₹24 lakh fixed plus a 15% variable that pays at 80%, the other is ₹20 lakh fixed plus ESOPs valued at a paper number by the company that issued them. One has a 90-day notice period, the other 30. One has a manager you have met, the other a manager who started last month.

This skill converts offers into comparable cash, prices the equity honestly, and puts the non-cash terms on the same page as the money. It ends with a ranked list, the reasoning written down, and the questions to ask before signing - because the best time to find out about a clawback clause is before you resign.

The output is not a score. It is a table where every assumption is visible, so you can see which assumption would have to be wrong for the answer to change.

## When to use this skill

- You hold two or more offers and they are not comparable on the number you were quoted.
- One offer includes ESOPs and you cannot tell what they are worth.
- You are comparing a raise at the current employer against an external offer.
- A recruiter is pushing a decision deadline and you need the comparison done today.
- **Do NOT use for:** negotiating the number itself (that is a separate brief), evaluating whether to change careers, or any tax filing - this ends at a ranked comparison and a question list.

## Stage 1 - Get every offer in writing before comparing

Verbal numbers change between conversations and memory is generous. Ask each recruiter for the full break-up in writing, and say you need it to compare fairly.

1.1 Ask for fixed pay, variable pay with its target and its historical payout, and any joining bonus with its clawback terms.

1.2 Ask for the equity grant: number of units, the current valuation and its date, the vesting schedule, the exercise price and the cliff.

1.3 Ask for benefits in rupees: insurance, provident fund contribution, gratuity, phone and internet allowance, learning budget.

1.4 Ask for the location, the working pattern and any relocation support.

1.5 Ask for the notice period and the probation terms, both of which bind you after you join.

1.6 Record the date each offer was received. Offers expire, and a comparison of a live and a dead offer is theatre.

Gate: every offer has a written break-up with fixed, variable, bonus, equity, benefits and notice period.

## Stage 2 - Compute take-home cash, not CTC

CTC is a marketing number. It includes the employer's provident fund contribution, gratuity that you cannot touch for 5 years, and insurance you may never claim. Take-home is what pays rent.

2.1 Start from fixed pay and add only what lands in your account monthly.

2.2 Add variable at its realistic payout, not its target. If the last two years paid 80%, use 80%.

2.3 Add the joining bonus in year one only, and subtract the clawback if you leave inside the stated window.

2.4 Subtract employee provident fund contribution if you are comparing monthly cash, and note that the employer contribution is real money you will see later.

2.5 Compute tax at your slab on the taxable components and record the slab you used.

2.6 Produce two numbers per offer: monthly take-home and annual take-home including variable.

```python
def take_home(fixed, variable_payout, bonus, tax_rate=0.30, pf_employee=0.12):
    gross = fixed + variable_payout + bonus
    pf = fixed * pf_employee
    taxable = gross - pf
    return round((taxable * (1 - tax_rate)) / 12), round(gross - taxable * tax_rate)

print(take_home(24_00_000, 2_88_000, 0))     # offer A
print(take_home(20_00_000, 1_60_000, 1_50_000))  # offer B
```

Gate: every offer has a monthly and annual take-home figure with the tax slab and payout assumption written beside it.

## Stage 3 - Price the equity as a bet, not a number

ESOPs are an option on a future event: a liquidity event at a price above your exercise price, after your vesting, before the company's fortunes change. Treat the quoted value as a ceiling and compute three cases.

3.1 Compute the grant's value at the current valuation, then discount it for vesting: a 4-year vest with a 1-year cliff means you own nothing for 12 months and 25% at month 12.

3.2 Subtract the exercise price per unit, which is often not mentioned in the offer letter headline.

3.3 Compute three cases: zero (company fails or never lists), a flat exit at the current valuation, and a 2x exit.

3.4 Multiply each case by the probability you assign, and write the probability down so the assumption is visible.

3.5 Add the tax treatment: ESOPs are typically taxed as perquisite at exercise and as capital gains at sale, and the exercise tax is due whether or not you can sell. Confirm the current rules with a professional.

3.6 Compare against the cash you gave up to take the equity - the fixed-pay difference between the offers.

3.7 Compute the value per year of vesting, not the headline grant, because the number that matters is what you actually keep if you leave in year 3:

```python
def vest_value(grant_units, price_now, strike, schedule=(0.25, 0.25, 0.25, 0.25)):
    per_unit = max(price_now - strike, 0)
    return [round(grant_units * s * per_unit) for s in schedule]

print(vest_value(4_000, 300, 30))   # value received at each anniversary
```

| Case | Probability (write yours) | Value at exit | Exercise cost | Net to you |
|---|---|---|---|---|
| Company fails | 30% | ₹0 | ₹0 | ₹0 |
| Flat exit at current valuation | 50% | ₹8,00,000 | ₹1,20,000 | ₹6,80,000 |
| 2x exit | 20% | ₹16,00,000 | ₹1,20,000 | ₹14,80,000 |
| Expected value | - | - | - | ₹6,36,000 over 4 years |

Gate: every equity offer has three cases, an expected value and the cash given up to take it.

## Stage 4 - Put the non-cash terms on the same page

The first year is decided by things that never appear in a CTC: who you report to, whether the role exists as described, and how long you are locked in.

4.1 Write the manager's name, their tenure and whether you have spoken to them.

4.2 Write the notice period and the probation terms; a 90-day notice period is a real cost when the next offer needs you in 30.

4.3 Write the working pattern - days in office, on-call rotation, travel expectation - and whether it is policy or habit.

4.4 Write what the role is measured on in the first 6 months, as stated by the hiring manager.

4.5 Write the commute in minutes door to door, and multiply by 2 for the daily cost.

4.6 Write the two things you would lose by leaving your current role: a specific project, a specific person, a specific flexibility.

Gate: five non-cash lines per offer, each with a fact rather than an impression.

## Stage 5 - Weight the criteria before scoring

Weights chosen after scoring are a rationalisation. Set them first, in writing, and make them sum to 100.

5.1 List the six criteria that actually matter to you this year: cash, equity, learning, manager, stability, flexibility.

5.2 Assign weights that sum to 100, and be honest about cash being 40-50 for most people with a mortgage.

5.3 Score each offer 1-5 per criterion against the same rubric.

5.4 Multiply, sum, and look at the ranking. Then look at which single weight would have to move to change the answer.

5.5 If the ranking contradicts your gut, find the criterion you left out. It is usually the manager or the commute.

| Criterion | Weight | Offer A (1-5) | Offer B (1-5) |
|---|---|---|---|
| Take-home cash | 40 | 4 | 3 |
| Equity expected value | 10 | 2 | 4 |
| Learning and scope | 20 | 4 | 5 |
| Manager quality | 15 | 5 | 3 |
| Stability | 10 | 4 | 2 |
| Flexibility and commute | 5 | 3 | 4 |

Gate: weights sum to 100, both offers are scored on the same rubric, and the swing weight is identified.

## Stage 6 - Stress the comparison on the assumptions that matter

A comparison is only as good as its weakest assumption. Test the three that change most often.

6.1 Variable at 50% payout instead of 80% - does the ranking hold?

6.2 Equity at zero - does the offer still win?

6.3 Probation not confirmed, or a role change in month 3 - what is your fallback?

6.4 Commute doubling after a return-to-office change - what does that do to the flexibility score?

6.5 Write the answer for each: ranking holds, or ranking flips. A ranking that flips on one assumption is not a ranking, it is a coin toss.

Gate: all three stresses are recorded with a holds-or-flips verdict.

## Stage 7 - Ask the questions that the offer letter avoids

Every offer letter is silent on the things that hurt later. Ask them in writing before you sign, and keep the replies.

7.1 What is the variable payout for the last two years, by percentage?

7.2 What is the vesting schedule, the cliff and the exercise price per unit, in writing?

7.3 Is the joining bonus clawed back, over what period and on what terms?

7.4 What is the notice period during probation, and after confirmation?

7.5 What happens to unvested equity on resignation, and is there a buyback window?

7.6 Who will I report to, and has that person been in the role for more than 6 months?

7.7 Send all seven as one numbered list in a single email, so the replies are comparable and quotable.

Gate: written answers to all six questions, or an explicit note that the employer declined to answer.

## Stage 8 - Decide, and tell the other side properly

The decision has a deadline and the decline has a cost. Handle both with the same care.

8.1 Write the decision in one sentence with the two reasons that carried it.

8.2 Tell the losing offer first, thank them specifically and name the reason honestly - the recruiter you decline today may hire you in three years.

8.3 Negotiate only on the criterion you can evidence: a competing written offer, a specific scope, a specific title.

8.4 Get the final terms in writing before resigning, including the revised number.

8.5 Resign in the order your contract requires, and check the notice period against the new joining date before you sign anything.

8.6 Confirm the offer's validity window in writing. An offer accepted after expiry is a favour, not a contract.

Gate: the decision is written with reasons, the other side is informed, and the final terms are in writing before any resignation.

## Stage 9 - Record what happened, for the next time

The comparison you build today is the template for the one in 3 years. Keep the file and add the outcome.

9.1 Note which assumptions were right: variable payout, equity case, commute.

9.2 Note what the first 6 months actually measured you on, against what was stated.

9.3 Keep the question list; it is the reusable part.

9.4 Note the negotiation outcome and what moved it.

9.5 Archive the file with a date, and re-read it before the next search.

9.6 Note the one question whose answer would have changed the decision, and ask it first next time.

Gate: the file is archived with the outcome recorded against each assumption.

## Quality checklist

- [ ] Every offer has a written break-up covering fixed, variable, bonus, equity, benefits and notice.
- [ ] Take-home is computed monthly and annually for each offer.
- [ ] Variable pay uses the historical payout, not the target.
- [ ] The tax slab used is stated on the sheet.
- [ ] Equity is valued in three cases with exercise cost subtracted.
- [ ] The cash given up for equity is stated.
- [ ] Notice period and probation terms are recorded for each offer.
- [ ] The manager's name and tenure are recorded.
- [ ] Weights are set before scoring and sum to 100.
- [ ] Both offers are scored on the same rubric.
- [ ] The swing weight is identified.
- [ ] Three stress cases are run with a holds-or-flips verdict.
- [ ] The six written questions are answered or noted as declined.
- [ ] The decision is written in one sentence with two reasons.
- [ ] Final terms are in writing before any resignation.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Ranking flips after you sign | Variable compared at target instead of historical payout | Use the last two years' actual payout percentages |
| Equity turned out worthless | Quoted valuation used as if it were cash | Value at three cases and subtract the exercise cost |
| Monthly cash short in month 2 | CTC used as take-home, ignoring employer PF and gratuity | Compute take-home from fixed pay and actual deductions |
| Stuck for 90 days | Notice period not checked against the joining date | Record notice and probation for every offer before deciding |
| Joined a team that no longer exists | Role scope taken from the recruiter, not the hiring manager | Ask the hiring manager what you are measured on in 6 months |
| Bonus clawed back on leaving | Clawback terms never read | Ask for clawback terms in writing and subtract them in year one |

## Copy-ready agent prompt

> Read the skill at the URL above and compare my job offers. Ask me for each written break-up, my tax slab, and the two or three criteria that matter most this year. Produce a take-home calculation per offer with the payout assumption stated, an equity valuation in three cases with the exercise cost subtracted, a weighted comparison where I set the weights first, and three stress cases with a holds-or-flips verdict. Finish with the six questions to send each recruiter and a one-sentence decision with its two reasons. Do not tell me which offer to take; show me the assumptions that decide it.
