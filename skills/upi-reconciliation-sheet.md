---
name: upi-reconciliation-sheet
description: Match a month of UPI and bank credits to the invoices that caused them, and end with a short list of money that has no owner on either side.
version: 1.0.0
license: MIT
tags: [finance, reconciliation, upi, spreadsheet, small-business, india]
---

# UPI Reconciliation Sheet

A small business takes 300-2,000 UPI credits a month across three handles and one current account. The invoice list says ₹4,80,000 was billed; the bank says ₹4,41,200 came in. The gap is not fraud, it is 40 payments whose reference field says `UPI/DR/4021XXXX/PAYEE` and nothing else.

This skill builds a matching sheet where every credit is either tied to an invoice, tied to a customer with no invoice, or listed as unexplained. You end with a number you can act on and a list of 5-30 items a human must resolve, instead of an argument about whether the month closed.

## When to use this skill

- Your bank statement and your invoice register disagree by more than ₹500 and you cannot say which row is wrong.
- Customers pay a round figure, pay two invoices in one transfer, or pay in part, and nothing in the narration identifies which.
- You need a monthly closing file that a CA or auditor can check line by line.
- Refunds and reversals keep reappearing because nobody records them once.

Do NOT use for: GST filing, TDS, or deciding whether an invoice is legally valid - this is arithmetic on money that already moved. It also does not replace a CA's review of anything you intend to file.

## Stage 1 - Freeze both datasets before matching

1.1 Export the bank statement for the exact period, in CSV, with value date, amount, narration, and reference columns preserved. Never match against a PDF read by eye.

1.2 Export the invoice register with invoice number, date, customer, amount, and status.

1.3 Set the cut-off. Use the bank's value date for money and the invoice date for billing, and state both in the sheet header. A month that closes on the 5th of the next month is a different answer from one that closes on the 1st.

1.4 Strip currency symbols and thousand separators from every amount column in one pass, and assert the row counts did not change.

| Source | Required columns | Common defect |
|---|---|---|
| Bank CSV | value date, amount, narration, ref | narration truncated at 30 chars |
| Invoice register | number, date, customer, amount, status | duplicate invoice numbers after a reissue |
| UPI settlement report | UTR, amount, VPA, date | one row per batch, not per payment |

1.5 Check the export shape before anything else - one header row, no merged cells, no repeated header mid-file:

```csv
value_date,amount,narration,ref_no
2026-10-01,15000.00,UPI/DR/402112345678/PAYEE/OKHDFCBANK,402112345678
2026-10-01,4999.00,UPI/DR/402112345679/R SHARMA/OKSBI,402112345679
2026-10-02,-1200.00,REVERSAL/402112345670/PAYEE,402112345670
```

1.6 Assert the number of data rows equals the count your bank's own summary shows. A silently truncated export is the most common cause of a gap that cannot be explained.

Gate: both row counts recorded, and the bank credit total for the period written down as the control figure.

## Stage 2 - Normalise the narration into usable fields

2.1 UPI narrations carry a UTR, a handle, and sometimes a name. Split them into three columns rather than matching on the raw string.

2.2 Collapse every handle to one customer key: `okhdfcbank`, `oksbi`, `okaxis` are banks, not customers, so they must never be used as the customer key.

2.3 Lowercase, remove spaces and dots from any name fragment before comparing. `R. Sharma` and `rsharma` are the same payer.

2.4 Keep the raw narration untouched in its own column. Every disputed match gets checked against it, and a normalised column is not evidence.

2.5 Store the customer key as a separate `payer_key` column that a human can edit. Automated keys are a starting point, and the edits are the training data for next month.

2.6 Drop narration fragments under 3 characters before comparing - `UPI`, `DR` and single initials match everything and nothing.

```python
import re
def split_narration(s):
    utr = re.search(r"\b(\d{12})\b", s)
    vpa = re.search(r"([\w.\-]+@[\w\-]+)", s)   # note: handle only, not a mail address
    return {
        "utr": utr.group(1) if utr else "",
        "handle": vpa.group(1).split("@")[1].lower() if vpa else "",
        "raw": s,
    }
```

Gate: over 95% of credit rows have a non-empty UTR after normalisation. Below that, the export is the problem, not the matching.

## Stage 3 - Match in three passes, strictest first

3.1 Pass one, exact: an invoice number inside the narration and an amount equal to the invoice total. This should clear 20-40% of rows with zero ambiguity.

3.2 Pass two, amount and customer: a unique invoice for that customer with the identical amount inside a 45-day window.

3.3 Pass three, amount only: a unique unpaid invoice with the identical amount inside 30 days. Only accept this when exactly one invoice matches; two candidates means unresolved.

3.4 Never match on amount alone across different customers. Two customers paying ₹15,000 in the same week is normal, and a wrong match is worse than an unmatched row.

| Pass | Key used | Window | Auto-accept rule |
|---|---|---|---|
| 1 | invoice number in narration | any | always |
| 2 | customer + exact amount | 45 days | one candidate only |
| 3 | exact amount | 30 days | one candidate only |
| 4 | manual | human judgement | never automatic |

Gate: matched value plus unexplained value equals the bank credit total, to the rupee.

## Stage 4 - Handle part payments and one payment for many invoices

4.1 A part payment leaves a balance: record `amount_matched`, keep the invoice open, and carry the remainder forward instead of closing it.

4.2 One transfer covering several invoices needs an allocation table with one row per invoice and a total that equals the credit.

4.3 Allocate oldest invoice first unless the customer says otherwise, and record the rule used in the row. An allocation rule that changes silently makes next month unreconcilable.

4.4 Round-off differences under ₹1 go to a named `rounding` bucket, not to an invoice.

4.5 When a single transfer covers invoices for two different customers, split the allocation by customer and flag the row. One payer settling another's bill is a real pattern and it hides bad debt.

Gate: every invoice's matched total is at or below its invoice amount, and no allocation row exceeds the credit it belongs to.

## Stage 5 - Chase the unexplained, in order of money

5.1 Sort unexplained credits by amount, descending. A ₹40,000 unknown is a customer problem; forty ₹100 unknowns are a rounding or fee pattern.

5.2 Classify each one: customer paid without an invoice, duplicate payment, refund received, or unknown. Each class has a different next action.

5.3 For "paid without invoice", the action is to raise the invoice, not to book the money as income - the tax position differs.

5.4 For "duplicate", refund it and record the refund against the same customer, so next month's statement does not create a second mystery.

5.5 Send the customer one message listing the credit date, amount and UTR, and ask which invoice it settles. Store the answer in a `resolved_note` column.

| Class | Signal | Next action | Owner |
|---|---|---|---|
| paid without invoice | credit above the open balance | raise the invoice, do not book income | accounts |
| duplicate | same customer, same amount, 2 credits | refund and log the refund | accounts |
| part payment | credit below the invoice total | carry the balance, chase the rest | sales |
| vendor refund | payer is a supplier | match to the purchase, not a sale | accounts |
| unknown | none of the above | ask the customer, 7-day follow-up | founder |

Gate: every unexplained row has a class, an owner and a next action.

## Stage 6 - Catch the fees, reversals and holds

6.1 Compare the settlement report total against the bank credit total per day. The difference is MDR or a failed settlement, and it must be booked as an expense line, not lost.

6.2 Reversals appear as a debit after a credit. Match them by UTR to the original credit and net them out on the same row.

6.3 Holds and pending settlements belong in an `in_transit` bucket that carries into the next month, not in unexplained.

6.4 Record the fee rate you are actually paying as a percentage of collections. A 0.4-point surprise on ₹4,00,000 a month is ₹1,600 a month, worth a call to your provider.

Gate: fee total plus net credits equals gross collections for the period.

## Stage 7 - Build the closing sheet a reviewer can follow

7.1 Sheet one, `credits`: one row per bank credit with matched invoice, matched amount, class, owner and note.

7.2 Sheet two, `open_invoices`: unpaid and part-paid invoices with the balance and days overdue.

7.3 Sheet three, `summary`: billed, collected, fees, unexplained, in-transit, and the closing gap.

7.4 Put the control figures in the header, not the footer: bank total, invoice total, and the two row counts.

7.5 Add a `check` cell that subtracts the parts from the bank total and shows 0. If it shows anything else, the sheet is not finished.

| Sheet | Rows | Purpose |
|---|---|---|
| credits | one per bank credit | the match and its evidence |
| open_invoices | one per unpaid invoice | what to chase |
| summary | fixed 8 lines | the closing number |
| log | one per run | reproducibility |

Gate: the check cell reads 0 and the summary prints the same three totals as the header.

## Stage 8 - Run it monthly with the same inputs, in under 10 minutes

8.1 Keep the period as a parameter in one cell or one CLI flag. Two places to type a date is one place to get it wrong.

8.2 Archive each month's raw exports next to the closing sheet. An auditor asking in month 9 needs the source, not a re-download that no longer matches.

8.3 Keep the matching script deterministic: no random sampling, no fuzzy threshold that changes between runs.

8.4 Log run date, row counts, matched value and unexplained value to a `log` sheet. Drift shows up here before it shows up in the bank.

```bash
python3 reconcile.py --period 2026-10 --bank oct-bank.csv \
  --invoices oct-invoices.csv --settle oct-upi.csv --out closing-2026-10.xlsx
```

Gate: re-running the same period produces an identical closing file, byte for byte.

## Stage 9 - Decide what to fix in the business

9.1 If more than 15% of credits are unexplained, the problem is collection hygiene, not the sheet: add a payment reference to every invoice.

9.2 If part payments exceed 10% of invoices, change terms - a 50% advance removes most of the chasing.

9.3 If one customer accounts for most duplicate payments, they are paying from two systems; agree one handle with them.

9.4 Put the three numbers - unexplained value, unexplained count, fee percentage - on a single line you read at the start of each month.

Gate: the three numbers are recorded for the last 3 months, so a trend exists rather than a snapshot.

## Stage 10 - Close the month in one page

10.1 Print the summary sheet to one page: billed, collected, fees, unexplained, in transit, and the check cell.

10.2 Sign and date it. A closing file with no date is a draft, and the next run will overwrite it without a trace.

10.3 Send the unexplained list to the person who owns each row the same day. A list discovered on the 20th of the next month is a write-off by then.

10.4 Archive the closing file and its three source exports under one folder name: `closing/2026-10/`.

10.5 Open the next month with the in-transit and part-payment balances carried in, not re-derived.

Gate: one page, one date, one owner per open item, and the carried balances equal last month's closing balances.

## Worked example

A design studio, October 2026, 412 UPI credits across two handles.

| Item | Amount | Rows |
|---|---|---|
| Bank credits | ₹4,41,200 | 412 |
| Invoices raised | ₹4,80,000 | 63 |
| Matched by invoice number | ₹1,86,400 | 71 |
| Matched by customer and amount | ₹1,94,800 | 288 |
| Matched by amount only | ₹31,500 | 21 |
| Fees and reversals netted | ₹2,100 | 9 |
| Unexplained | ₹26,400 | 23 |

Of the 23 unexplained rows, 14 were one client paying three invoices in a single transfer of ₹18,000, 6 were duplicate payments of ₹1,200 each, and 3 were a refund from a vendor. All 23 were classified in 40 minutes; the sheet's check cell read 0 at the end.

## Quality checklist

- [ ] Bank total, invoice total and both row counts are in the header
- [ ] Amounts stripped of symbols and separators, row counts unchanged
- [ ] Narration split into UTR, handle and raw, raw never overwritten
- [ ] UTR present on more than 95% of credit rows
- [ ] Pass 1 matches on invoice number only
- [ ] Pass 2 and 3 refuse to auto-accept when two candidates exist
- [ ] No match made on amount across different customers
- [ ] Part payments carry a balance and leave the invoice open
- [ ] Multi-invoice transfers have an allocation table that sums to the credit
- [ ] Fees and reversals netted by UTR, not guessed
- [ ] In-transit settlements carried forward, not classed as unexplained
- [ ] Every unexplained row has class, owner and next action
- [ ] Check cell reads 0
- [ ] Re-run of the same period produces an identical file
- [ ] Raw exports archived beside the closing sheet
- [ ] Three trend numbers recorded monthly

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Gap of a few thousand rupees that will not close | MDR and settlement fees never booked | Net fees by UTR, book as an expense line |
| Same payment matched twice | Two passes both accepted the row | Remove a matched row from the candidate pool |
| Wrong customer credited | Matched on amount alone across customers | Restrict amount-only matching to a unique invoice |
| Invoice stays open after full payment | Part-payment rows never summed | Compare invoice total to sum of allocations |
| Unexplained count grows every month | No payment reference on invoices | Add invoice number to the payment link or note |
| Reversal shows as new income | Reversal not linked to its original credit | Match reversal debit by UTR |
| Month closes on different numbers each run | Fuzzy threshold or sampling in the matcher | Make matching deterministic and log the rules |
| Auditor cannot reproduce the sheet | Raw exports not archived | Store source files beside each closing sheet |
| Rounding rows mistaken for unpaid invoices | ₹1 differences booked to invoices | Route differences under ₹1 to a rounding bucket |
| Fee surprise at year end | Rate never measured monthly | Track fees as a percentage of collections |

## Copy-ready agent prompt

> Read the skill at the URL above and build my monthly UPI reconciliation. Ask me: how many credits a month, how many UPI handles, what my bank CSV columns are, and whether I bill with invoice numbers in the payment note. Then produce the three-sheet closing workbook with a credits sheet, an open-invoices sheet and an 8-line summary, the deterministic matcher that runs exact-invoice, then customer-and-amount, then unique-amount passes, the allocation table for part payments and multi-invoice transfers, and a check cell that must read 0 before I close the month. Give me the list of unexplained credits sorted by amount with a class and a next action for each. Do not book any unexplained credit as income.
