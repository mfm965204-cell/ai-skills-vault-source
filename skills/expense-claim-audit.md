---
name: expense-claim-audit
description: Audit a month of employee expense claims against written policy and produce a flagged register with the rupee amount, the rule broken and the person to ask.
version: 1.0.0
license: MIT
tags: [finance, audit, expenses, compliance, india]
---

# Expense Claim Audit

Expense fraud is rarely dramatic. It is the same cab bill submitted twice, a hotel rate that quietly grew by ₹400, and a "team lunch" for nine people at a company where the team has six. Each one is small enough to pass an eyeball review and large enough that 40 of them a month pay somebody's salary.

This skill audits a month of claims against a written policy, mechanically and reproducibly, and produces a register where every flagged row has three things: the rupee amount, the rule it breaks and the person who can answer for it. It also produces the policy gaps that made the flags possible, because an audit that only punishes people teaches them to hide better.

## When to use this skill

- You are the finance person in a 20-200 person company and nobody reviews claims properly.
- A reimbursement run is about to be paid and the total jumped 40% with no headcount change.
- You are writing expense policy and want to know which rules the current data actually needs.
- A statutory audit or investor diligence asked for expense controls.
- **Do NOT use for:** investigating suspected fraud with legal consequences, forensic accounting, or payroll and salary processing - suspected fraud goes to a person, not to a script.

## Stage 1 - Write the policy down before auditing against it

You cannot flag a rule that was never written. If there is no policy document, produce a one-page version first and get it approved; an audit against an unwritten rule is an argument, not a finding.

1.1 List the categories you will audit this month: travel, meals, accommodation, local conveyance, internet and phone, software, client entertainment.

1.2 For each category write the limit, the evidence required and the approval level. "Meals ₹1,000 per person, itemised bill, manager approval" is a rule; "reasonable meals" is not.

1.3 Write the duplicate rule explicitly: one expense, one claim, one receipt, no re-submission across two months.

1.4 Write the escalation rule: what happens on a first, second and third flag.

1.5 Version the policy with a date. Claims are judged against the version in force on the claim date, not today.

1.6 Keep the policy as a machine-readable block beside the readable page, so the audit reads limits from one source:

```yaml
version: 2026-04-01
meals:      {limit: 1000, unit: per_person, evidence: itemised_bill, approver: manager}
accommodation: {limit: 4500, unit: per_night, evidence: itemised_bill, approver: manager}
conveyance: {limit: 1500, unit: per_trip, evidence: receipt, approver: self}
software:   {limit: 5000, unit: per_month, evidence: invoice, approver: manager}
```

Gate: every category has a number, an evidence requirement and an approver, all versioned with a date.

## Stage 2 - Pull the claims and the policy into comparable shapes

The export from an expense tool is not audit-ready: amounts are strings, dates are in three formats and categories are free text. Normalise before you judge anything.

2.1 Export claims for the month with employee id, claim date, expense date, category, amount, GST amount, receipt link, approver and status.

2.2 Map free-text categories onto your policy categories with an explicit mapping table, and count what did not map.

2.3 Coerce amounts to numeric and dates to a single format, logging every failure rather than dropping it.

```python
import pandas as pd

CATS = {"cab": "conveyance", "uber": "conveyance", "ola": "conveyance",
        "hotel": "accommodation", "stay": "accommodation",
        "lunch": "meals", "dinner": "meals", "team lunch": "meals"}
c = pd.read_csv("claims_2026-10.csv")
c["category"] = c["category"].str.strip().str.lower().map(CATS).fillna("unmapped")
c["amount"] = pd.to_numeric(c["amount"].str.replace(r"[₹,\s]", "", regex=True), errors="coerce")
c["expense_date"] = pd.to_datetime(c["expense_date"], dayfirst=True, errors="coerce")
print(c["category"].value_counts(), c["amount"].isna().sum())
```

2.4 Count claims with no receipt link. A missing receipt is a flag, not a data problem.

2.5 Record the month's totals: claim count, employee count, gross amount and amount with GST.

2.6 Snapshot the raw export beside the normalised frame. When an employee disputes a flag, the raw row is the evidence and the normalised row is only your reading of it.

Gate: every claim has a policy category or is explicitly unmapped, and every amount parses.

## Stage 3 - Run the duplicate check first, because it is the biggest

Duplicates are the most common leak and the easiest to detect mechanically. Three checks catch almost all of them.

3.1 Exact duplicate: same employee, same amount, same expense date, submitted twice.

3.2 Near duplicate: same employee, same amount within ₹1, expense dates within 3 days, different claim ids.

3.3 Cross-employee duplicate: same receipt link or same invoice number appearing under two employees - usually a shared cab or a shared meal claimed twice.

3.4 Report duplicates with both claim ids so the reviewer sees the pair, not a single row.

| Check | Key | Tolerance | Typical hit rate |
|---|---|---|---|
| Exact duplicate | employee + amount + date | none | 1-3% of claims |
| Near duplicate | employee + amount + date | ₹1, 3 days | 2-5% |
| Cross-employee | receipt link or invoice no | none | under 1% |
| Split claim | employee + date | two rows under limit | 1-2% |

3.5 Add a split-claim check: two claims on the same date that individually sit just under the limit and together exceed it.

3.6 Report the duplicate total as both count and rupees. Twelve duplicates worth ₹4,200 and two worth ₹41,000 need different conversations.

Gate: all four duplicate checks have run and every hit is listed with its pair.

## Stage 4 - Check each category against its limit

Limits only mean something when the unit is right. A meal limit is per person, an accommodation limit is per night, a conveyance limit is per trip. Extract the unit before comparing.

4.1 For meals, require a headcount field; without it, flag the claim as unverifiable rather than assuming one person.

4.2 For accommodation, compute nights from check-in and check-out dates and divide the amount by nights.

4.3 For conveyance, flag any single trip above ₹1,500 without a stated reason and any airport transfer without a boarding pass.

4.4 Compare the unit amount against the limit in force on the expense date, not the current limit.

4.5 Record the excess amount, not just the flag - "₹1,840 over limit" drives the conversation, "flag" does not.

4.6 Group breaches by employee and by category. One employee with 14 breaches is a training issue; 14 employees with one breach each is a policy issue.

Gate: every limit breach carries an excess amount in rupees and the unit it was measured in.

## Stage 5 - Check the evidence, not only the arithmetic

A claim can be within limit, correctly categorised and still unsupported. Evidence is the part reviewers skip.

5.1 Require an itemised bill for meals and accommodation; a card slip alone does not show what was bought.

5.2 Check that the receipt date matches the expense date within 2 days, and flag anything else.

5.3 Check GSTIN on bills above ₹5,000 for business expenses - without it the company cannot claim the credit.

5.4 Flag claims where the receipt is a photograph of a screen, a forwarded email with no attachment, or a link that returns nothing.

5.5 Note the evidence status per claim as `complete`, `partial` or `missing`, so the register can be filtered by it.

| Evidence state | Definition | Treatment |
|---|---|---|
| complete | Itemised bill, date matches, GSTIN where required | Approved if within limit |
| partial | Bill present, one field missing | Approved with a note, flagged for training |
| missing | No bill, or a link that returns nothing | Held, never approved |
| unverifiable | Headcount or nights not stated | Question sent before any approval |

5.6 Count the missing-evidence rows per category. A category where 40% of claims lack a bill needs a form change, not 40 questions.

Gate: every claim has an evidence status, and no claim with `missing` evidence is approved.

## Stage 6 - Score and band the flags so the review is proportionate

A register with 300 flags is useless: nobody reviews 300 rows. Band them by rupee value and confidence.

6.1 Compute a flag amount per row - the excess over limit, or the full amount for duplicates and missing evidence.

6.2 Sort descending by flag amount and take the top 20 rows as the review set; they usually hold 70-80% of the value.

6.3 Band the rest: `high` above ₹5,000, `medium` ₹1,000-5,000, `low` below ₹1,000.

6.4 Report the count and value in each band, so the reader sees that 240 low flags are worth ₹18,000 while 12 high flags are worth ₹1,40,000.

6.5 Write the sampling rule down: 10% of low-band rows, chosen by claim id modulo 10, so the sample is reproducible and not hand-picked.

| Band | Rows | Value | Review treatment |
|---|---|---|---|
| High (above ₹5,000) | 12 | ₹1,40,200 | Reviewed line by line |
| Medium (₹1,000-5,000) | 48 | ₹1,12,600 | Reviewed by exception type |
| Low (below ₹1,000) | 240 | ₹18,400 | Sampled 10%, rest recorded |

Gate: the bands sum to the full flagged value and the review set is at most 20 rows.

## Stage 7 - Ask the employee, with the specific question

"Please explain this claim" gets a defensive answer. A specific question gets a fact.

7.1 Write one line per flagged claim: the date, the amount, the rule and the exact question.

7.2 Send the employee their own rows only - never the whole register.

7.3 Give a 5-working-day window and state what happens if there is no reply: the amount is recovered from the next reimbursement.

7.4 Record the reply verbatim against the claim. Do not paraphrase, because the paraphrase is what gets disputed later.

7.5 Re-run the flag after the reply: a headcount correction can clear a meal flag entirely.

7.6 Track response rate. Below 70% replies, the process is not landing and the reminder, not the employee, is the problem.

Gate: every reviewed row has a question sent, a date and a recorded reply or a no-reply marker.

## Stage 8 - Decide, recover and record

Every flag ends in one of four outcomes. Anything unresolved stays open with an owner, never silently closed.

8.1 `approved` - evidence supplied, within policy, paid.
8.2 `recovered` - paid but deducted from the next reimbursement, with the deduction referenced in payroll.
8.3 `rejected` - not paid, and the employee is told the rule in writing.
8.4 `open` - awaiting evidence, with an owner and a date.

8.5 Post the recovered total as a single journal entry with a reference to the register, so the audit trail survives staff changes.

8.6 Write the outcome back to the expense tool, not only to your sheet. A decision that lives in one person's spreadsheet is lost at the next handover.

Gate: no row is left without an outcome, and the recovered total reconciles to the deduction entries.

## Stage 9 - Fix the two policy gaps the data exposed

The audit's second output is a policy change list. Rank the flag types by value and fix the top two.

9.1 If duplicates dominate, add a duplicate check at submission in the expense tool, before approval.
9.2 If limit breaches dominate, make the limit a hard field in the form rather than a rule in a document.
9.3 If missing evidence dominates, block submission without an attachment for categories above ₹2,000.
9.4 If unverifiable headcount dominates, make headcount a required numeric field for meals.
9.5 Publish the change with a date, and audit the same two checks next month to prove the fix worked.

9.6 Set the target: duplicate flags below 1% of claims and missing evidence below 5% within two months, measured the same way.

Gate: two policy or tooling changes are named with owners and dates, and the same checks are scheduled for next month.

## Quality checklist

- [ ] The policy version used for the audit is dated and stored with the register.
- [ ] Every claim carries one policy category or is explicitly unmapped.
- [ ] All amounts parse as numbers and all dates are in one format.
- [ ] All four duplicate checks have run.
- [ ] Every duplicate is reported as a pair with both claim ids.
- [ ] Limit breaches are measured in the correct unit and carry an excess amount.
- [ ] Every claim has an evidence status of complete, partial or missing.
- [ ] No claim with missing evidence is approved.
- [ ] Flags are banded by value with counts and totals per band.
- [ ] The review set is at most 20 rows.
- [ ] Every reviewed row has a specific question, a date and a recorded reply.
- [ ] Every flag ends in approved, recovered, rejected or open.
- [ ] The recovered total reconciles to the deduction entries.
- [ ] Two policy or tooling fixes are named with owners and dates.
- [ ] The raw export is snapshotted beside the normalised frame.
- [ ] The low-band sampling rule is written down and reproducible.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| 300 flags, none reviewed | Every deviation treated as equal instead of banded by value | Sort by flag amount and cap the review set at 20 rows |
| Duplicate check misses obvious pairs | Amount compared as text with a currency symbol attached | Strip symbols, parse to numeric, then compare |
| Meal limits flag every team lunch | Limit applied per claim instead of per person | Require headcount and divide before comparing |
| Employees say the rule was never told | Audit ran against an unwritten or newer policy | Version the policy, judge by the version in force on the claim date |
| Same person flagged monthly | No escalation ladder, so nothing changes | Define first, second and third flag consequences in the policy |
| Recovered amounts never hit the books | Deductions made informally from the next claim | Post one journal entry referencing the register |
| Audit repeats every month with the same flags | No target set, so the fix is never measured | Set a 1% duplicate target and re-measure the same check |

## Copy-ready agent prompt

> Read the skill at the URL above and audit one month of expense claims for my company. Ask me for the claims export and my expense policy, normalise the categories and amounts, then run the duplicate, limit, split-claim and evidence checks. Give me a flagged register with the rupee amount, the rule broken and the owner per row, banded into high, medium and low, a 20-row review set with one specific question per row, and a list of the two policy or tooling fixes the data justifies. Do not contact anyone; I will send the questions.
