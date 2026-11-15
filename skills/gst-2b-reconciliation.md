---
name: gst-2b-reconciliation
description: Match GSTR-2B against your purchase register and ship a claim-ready ITC register where every exception has a rupee value and a named owner.
version: 1.0.0
license: MIT
tags: [gst, finance, reconciliation, india, spreadsheet]
---

# GST 2B Reconciliation

Two files decide your input tax credit: the purchase register your team keyed in, and GSTR-2B that the portal generated from your suppliers' filings. Neither is wrong on its own, and the gap between them is where credit is lost - a supplier who filed late, an invoice keyed with a transposed digit and a credit note sitting in an inbox all look identical in a total.

This skill turns that gap into a register with four exception classes, a rupee value per row, an owner per row and an evidence column, so the number you claim at filing is the number you can defend in a notice a year later.

The unit of work is one period: one month, two source files, one register, one claim number, one run log. A register spanning quarters is not a reconciliation, it is an archive.

## When to use this skill

- Month-end is three days away and the purchase register has never been matched to 2B.
- A GST notice asks you to justify input credit taken in a specific quarter.
- You switched accounting software and the first month's 2B does not tie out.
- Your credit claim dropped sharply and nobody can name the supplier who caused it.
- A vendor insists they filed and the portal says otherwise.

Do NOT use for: raising or formatting tax invoices, e-invoice IRN generation, GSTR-1 or GSTR-3B filing mechanics, or e-way bill work. This ends at a register and a claim list that your filing step consumes.

## Stage 1 - Freeze the period before you touch a file

A run is valid for exactly one period. Pull 2B for that month, export the register as a dated CSV, and write both filenames and hashes into a run log. Anything edited after the run log is a new run with a new log.

1.1 Download GSTR-2B for the period as JSON, not PDF. The JSON keeps GSTIN, invoice number, invoice date, taxable value, IGST, CGST, SGST and cess as separate fields; the PDF keeps them as a table you will parse badly.

1.2 Export the purchase register for the same month with those same seven fields plus your internal voucher number and supplier name.

1.3 Record both hashes in the run log so a later edit is provable:

    sha256sum gstr2b_2026-10.json purchases_2026-10.csv | tee runlog_2026-10.txt

1.4 Count rows on both sides and write both numbers down before reading any content. A register of 1,240 rows against a 2B of 1,196 rows sets the expectation: about 44 exceptions exist, and you have not yet found one of them.

1.5 Note the 2B generation date in the log. Invoices dated after it are next period's problem, not this run's.

Gate: both files are for the same month, both hashes are in the run log, and the two row counts are written down.

## Stage 2 - Normalise both files into one schema

Most mismatches are born here, not in the data. One file stores dates as `2026-10-03`, the other as `03-10-2026`; one pads GSTINs to 15 characters, the other leaves a trailing space. Normalise before you compare or you will spend the afternoon chasing phantoms.

2.1 Coerce both files into frames with the same nine columns and print the dtypes before going further:

```python
import pandas as pd

book = pd.read_csv("purchases_2026-10.csv").rename(columns={"supplier_gstin": "gstin"})
two_b = pd.read_json("gstr2b_2026-10.json")
for df in (book, two_b):
    df["gstin"] = df["gstin"].str.strip().str.upper()
    df["inv_no"] = df["inv_no"].str.strip().str.upper().str.replace(r"[/\-\s]", "", regex=True)
    df["inv_date"] = pd.to_datetime(df["inv_date"], dayfirst=True, errors="coerce")
    for c in ("taxable", "igst", "cgst", "sgst", "cess"):
        df[c] = pd.to_numeric(df[c], errors="coerce").round(2)
print(book.dtypes, len(book), len(two_b))
```

2.2 Drop rows where `inv_date` failed to parse and log the raw value beside them. An unparseable date is an exception, never a zero.

2.3 Round every tax column to 2 decimals on both sides. A one-paisa float difference accounts for a large share of false mismatches.

2.4 Assert that neither frame has a null GSTIN or a null invoice number, and count what the assertions removed.

2.5 Recompute `tax_total = igst + cgst + sgst + cess` on both sides instead of trusting a pre-summed column.

2.6 Save the normalised frames to `clean/` as CSV so a reviewer sees exactly what you compared, in the format you compared it.

Gate: both frames share nine columns, the dtypes match, and every dropped row is logged rather than swallowed.

## Stage 3 - Match on three keys, not one

Invoice numbers get re-typed, so a strict join loses pairs that are genuinely present. Match in three passes, most strict first, and tag each pair with the pass that found it.

3.1 Pass one: exact join on GSTIN plus normalised invoice number. This should carry most of the value.

3.2 Pass two: GSTIN, invoice date within a 3-day window and taxable value equal to the paisa. This catches re-typed invoice numbers.

3.3 Pass three: GSTIN, taxable value within ₹1.00 and total tax within ₹2.00, restricted to the same month. Cap this pass - fuzzy value matching at scale manufactures pairs that do not exist.

3.4 Carry the pass number into a `match_pass` column so a reviewer can see how each pair was made:

```python
m1 = book.merge(two_b, on=["gstin", "inv_no"], how="inner", suffixes=("_bk", "_2b"))
m1["match_pass"] = 1
matched_vouchers = set(m1["voucher"])
print(m1.groupby("match_pass")["tax_total_bk"].sum())
```

3.5 Never match on supplier name. Two suppliers trading under the same name with different GSTINs is common, and a name join silently merges their credit.

3.6 Log the row count from each pass in the run log. A pass two that finds zero rows means the date window is wrong, not that your suppliers suddenly type correctly.

Gate: the three passes together explain at least 92% of register rows by count. Below that, Stage 2 normalisation is broken - fix it before blaming a supplier.

## Stage 4 - Classify every exception into one of four buckets

An exception is only actionable once it has a name. Four classes cover nearly everything, and each maps to a different person and a different fix.

| Class | What you see | Who acts | Value at stake |
|---|---|---|---|
| In books, not in 2B | Supplier has not filed, or filed late | Buyer chases supplier | Full tax on the invoice |
| In 2B, not in books | Invoice received but never keyed | Accounts payable | Full tax on the invoice |
| Value mismatch | Taxable differs by more than ₹1.00 | Accounts plus supplier | The delta only |
| Tax mismatch | Taxable agrees, IGST/CGST/SGST split does not | Accounts | The tax delta |

4.1 Compute `delta = taxable_bk - taxable_2b` and route anything with `abs(delta) > 1.00` to the value-mismatch bucket.

4.2 Route rows where taxable agrees but the tax split differs to the tax-mismatch bucket. Usually an inter-state invoice booked as intra-state, or the reverse.

4.3 Route unmatched rows by which side they came from, never by guessing which side is right.

4.4 Count rows per bucket and print the count beside the rupee total. A bucket with 40 rows and ₹900 is noise; a bucket with 2 rows and ₹4,80,000 is the month.

4.5 Reject a fifth class. A row fitting none of the four is malformed - send it back to Stage 2.

| Bucket | Rows | Tax at stake | Owner |
|---|---|---|---|
| In books, not in 2B | 12 | ₹1,86,400 | Purchase desk |
| In 2B, not in books | 9 | ₹2,14,900 | Accounts payable |
| Value mismatch | 15 | ₹38,700 | Accounts |
| Tax mismatch | 8 | ₹22,150 | Accounts |

Gate: every unmatched row carries exactly one class, and the four bucket totals plus the matched rows equal the register total to the paisa.

## Stage 5 - Chase the supplier-side gap with a deadline

"In books, not in 2B" is not a paperwork problem, it is a credit problem, and the statute puts a date on it: credit for a financial year is normally availed by 30 November following that year. A supplier who never files quietly deletes your claim. Confirm the current text of the rule before you rely on that date.

5.1 Group the missing-in-2B rows by GSTIN and total the tax per supplier, largest first.

5.2 Send one message per supplier naming the exact invoice numbers and the tax amount. A bulk reminder gets ignored; a message with five invoice numbers gets answered.

5.3 Set a follow-up at 7 days, a second at 14 and a vendor block at 21, recording each date against the row.

5.4 Park the row as `defer` with that date. Do not mark it claimable in the hope that it lands.

5.5 Keep the sent message text in the evidence column so the chase is auditable without reading email.

5.6 Escalate any supplier holding more than ₹1,00,000 of deferred tax to the vendor owner on the same day the first reminder goes out.

Gate: every missing-in-2B row has a supplier contact and a follow-up date, and the total deferred tax sits on one line of the summary.

## Stage 6 - Recover the book-side gap from the document

"In 2B, not in books" usually means the invoice is in a courier envelope, an email inbox or a chat thread. The fix is a document hunt with an owner, not a journal entry.

6.1 Sort these rows by tax value and take the top 20 first - they usually hold most of the value.

6.2 For each, record where the document was found: portal, email, physical, or not found.

6.3 Key the invoice using the 2B values exactly. Do not "correct" the supplier's tax split on the way in; a split argument belongs to Stage 4, not to data entry.

6.4 Mark rows still undocumented after 5 working days as `block` and exclude them from the claim list.

6.5 Re-run Stage 3 after keying. A recovered invoice often pulls a second row out of the value-mismatch bucket with it.

| Where the invoice hides | Where to look | What it recovers |
|---|---|---|
| Courier envelope | Reception or stores inward register | Full tax on the invoice |
| Email attachment | Search the GSTIN in the finance mailbox | Full tax on the invoice |
| Chat thread | Supplier's sales contact, not accounts | Full tax, after a delay |
| Never issued | Supplier's billing system | Nothing - treat as unclaimed |

Gate: no row in this bucket reaches `claim` without a source document named in the evidence column.

## Stage 7 - Build the register the filing step consumes

The deliverable is one sheet with fixed columns, one status per row, and no free-text statuses. Free text is what makes next month's run start from zero.

7.1 Write these columns in this order: `gstin, supplier, inv_no, inv_date, taxable, tax_total, class, delta, status, owner, followup_date, evidence`.

7.2 Allow exactly four statuses: `claim`, `defer`, `block`, `drop`. Anything else is a data-entry error, and the validation cell should refuse it.

7.3 Make the claim number a formula over the status column, never a typed figure:

```python
summary = reg.groupby("status")["tax_total"].agg(["count", "sum"]).round(2)
summary.loc["TOTAL"] = [len(reg), reg["tax_total"].sum()]
print(summary)
assert summary.loc["TOTAL", "sum"] == round(reg["tax_total"].sum(), 2)
```

7.4 Freeze the header row and filter on `status`. Reviewers work one status at a time, never the whole sheet.

7.5 Add a `run_id` column carrying the period, so two months of registers stack without ambiguity.

7.6 Export the register as CSV with a UTF-8 BOM so the rupee sign and any regional supplier names open correctly in Excel.

Gate: status totals reconcile to the register total, and the `claim` sum is the number that goes on the return.

## Stage 8 - Review with the person who owns the number

A register reviewed only by the person who built it hides its own assumptions. Walk two reviewers through the four buckets in 20 minutes, not through the sheet.

8.1 Show the matched count and the four bucket totals. Nothing else on screen.

8.2 Read out every `claim` row above ₹50,000 individually and confirm the document exists.

8.3 Ask the accounts reviewer to confirm that every `drop` row has a reason in the evidence column.

8.4 Ask the tax reviewer to confirm the `defer` list is acceptable against the availment deadline.

8.5 Sign off in the run log with two names and a timestamp. An unsigned register is a draft.

Gate: two named reviewers, every row above ₹50,000 read out, and the sign-off line filled.

## Stage 9 - Close the loop so next month starts ahead

The only durable improvement is upstream: stop the same exception being born again. Pick the two largest buckets and change one process for each.

9.1 If "in 2B, not in books" dominates, require the invoice number at goods receipt rather than at payment.

9.2 If "in books, not in 2B" dominates, add a filing check to vendor onboarding for your top 10 vendors by spend.

9.3 If value mismatches dominate, add a PO-to-invoice tolerance of ₹1.00 in the AP workflow and block anything above it.

9.4 If tax-split mismatches dominate, make place of supply a mandatory field on the purchase entry screen.

9.5 Carry the deferred total and its follow-up dates into next month's opening balance so nothing is re-discovered.

Gate: one process change is named with an owner and a date, and the deferred total is carried forward in the run log.

## Quality checklist

- [ ] Both source files are for the same period and their hashes are in the run log.
- [ ] Register and 2B row counts were recorded before matching started.
- [ ] Dates, GSTINs and invoice numbers are normalised on both sides.
- [ ] All amounts are rounded to 2 decimals before any comparison.
- [ ] Three match passes are recorded with a `match_pass` column.
- [ ] No match was made on supplier name alone.
- [ ] Every unmatched row carries exactly one of the four classes.
- [ ] Bucket totals plus matched rows equal the register total to the paisa.
- [ ] Every deferred row has a supplier contact and a follow-up date.
- [ ] Every blocked row is excluded from the claim list.
- [ ] The claim total is a formula over the status column, not a typed number.
- [ ] Two named reviewers signed off in the run log with a timestamp.
- [ ] Every claim row above ₹50,000 was read out and its document confirmed.
- [ ] One upstream process change is named with an owner and a date.
- [ ] The deferred tax total is carried into next month's opening balance.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| 30% of rows unmatched | Dates parsed month-first, so the 3-day window never fires | Pass `dayfirst=True` and log unparsed dates as exceptions |
| Hundreds of one-paisa mismatches | Unrounded floats compared across two files | Round both sides to 2 decimals before the join |
| One invoice appears twice in the claim | Two vouchers keyed for one invoice, both matched | De-duplicate on GSTIN plus invoice number, keep the earliest voucher |
| Claim total does not tie to the return | The summary cell was typed instead of summed | Replace it with a SUMIFS over the status column |
| Credit lost after the availment date | Deferred rows never escalated past the first reminder | Escalate at 7 and 14 days, block the vendor at 21 |
| Next month repeats this month | Statuses kept as free text, so months are not comparable | Restrict the status column to the four allowed values |
| Supplier says they filed, 2B disagrees | The filing landed after the 2B generation date | Regenerate 2B before escalating, then chase if still missing |

## Copy-ready agent prompt

> Read the skill at the URL above and run one reconciliation for my GST period. Ask me for the GSTR-2B JSON and the purchase register CSV, normalise both, match in three passes, and classify every exception into the four buckets. Give me one register sheet with the fixed columns and four statuses, a bucket summary with rupee totals, and a chase list per supplier with follow-up dates. Stop before filing anything and show me the claim total with both review sign-off lines empty.
