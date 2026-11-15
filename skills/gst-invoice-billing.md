---
name: gst-invoice-billing
description: Build GST-compliant invoicing for an Indian business - registration thresholds, the mandatory invoice fields, HSN and SAC codes, intra-state versus inter-state tax, numbering, e-invoicing, credit notes, the return calendar and record retention.
version: 1.0.0
license: MIT
tags: [finance, gst, invoicing, india, compliance, billing]
---

# GST Invoice And Billing

An invoice is a legal document before it is a design object. One missing field, one wrong place of supply, or one inter-state invoice split into CGST and SGST is a mismatch in the buyer's input credit and a notice six months later.

This skill builds the invoice template, the numbering scheme, the tax logic and the filing calendar. Confirm every threshold against gst.gov.in before you file - rates and limits change by notification, and this file states the ones in force when it was written.

## When to use this skill

- You are registering for GST and need to issue your first invoice.
- You sell to businesses and their accountants keep rejecting your invoices.
- You sell across states and are not sure when to charge IGST.
- You are building billing software and need the rules in code.

Do NOT use for: income tax computation, TDS on professional fees, or customs duty on imports. Those are separate regimes with separate calendars.

## Stage 1 - Work out whether you must register

1.1 Registration is triggered by aggregate turnover in a financial year, not by profit.

| Category | Threshold (normal states) | Threshold (special category states) |
|---|---|---|
| Goods | ₹40 lakh | ₹20 lakh |
| Services | ₹20 lakh | ₹10 lakh |
| Both goods and services | higher of the two applies to the supply | check the state notification |

1.2 Special category states include the north-eastern states, Himachal Pradesh, Uttarakhand and Jammu and Kashmir. The lower thresholds apply there.

1.3 Some supplies require registration regardless of turnover: inter-state taxable supply of goods, e-commerce operators, reverse charge liability, and casual taxable persons.

1.4 Voluntary registration is worth it when your buyers are businesses that need input tax credit, or when you buy a lot of taxable inputs yourself.

1.5 Composition scheme limits: ₹1.5 crore for goods and ₹50 lakh for services, with a flat rate and no input credit. You cannot charge GST separately to customers under composition.

1.6 Re-check the threshold in the month you cross 80% of it. Registration has a 30-day window from the date you become liable.

Gate: a written answer on whether you must register, and why, with the source you checked.

## Stage 2 - Put every mandatory field on the invoice

2.1 Rule 46 of the CGST Rules lists the particulars a tax invoice must carry. A missing one is a defective invoice, and the buyer's credit can be questioned.

2.2 The sixteen particulars, as a checklist for the template:

| # | Field | Notes |
|---|---|---|
| 1 | Supplier name, address, GSTIN | exact legal name as registered |
| 2 | Consecutive serial number | unique, max 16 characters |
| 3 | Date of issue | dd/mm/yyyy |
| 4 | Recipient name, address, GSTIN | GSTIN required for B2B |
| 5 | HSN or SAC code | 4 digits under ₹5 crore turnover, 6 above |
| 6 | Description of goods or services | specific, not "consulting" |
| 7 | Quantity and unit | for goods; UQC codes |
| 8 | Total value of supply | before tax |
| 9 | Taxable value after discount | discount shown separately |
| 10 | Rate of tax per item | CGST, SGST, IGST, cess |
| 11 | Amount of tax | per head |
| 12 | Place of supply | state, for inter-state clarity |
| 13 | Address of delivery | if different from recipient |
| 14 | Whether reverse charge applies | yes or no, explicitly |
| 15 | Signature or digital signature | of the supplier or authorised person |
| 16 | QR code | required once e-invoicing applies |

2.3 Add what buyers ask for even though it is not mandatory: purchase order number, project name, bank details, payment terms and due date.

2.4 Do not invent a "tax invoice" heading on a document that is not a tax invoice. A bill of supply is a different document, used by composition dealers and for exempt supplies.

2.5 Keep the invoice readable at A5 as well as A4; half of your buyers will open it on a phone.

Gate: a template where all sixteen particulars are present and labelled.

## Stage 3 - Choose the right HSN or SAC code

3.1 Goods use HSN; services use SAC. Both are numeric and both decide the rate, so a wrong code is a wrong tax.

3.2 Digits required: 4 digits if aggregate turnover is up to ₹5 crore, 6 digits above that. B2C invoices can use 4 digits in most cases.

3.3 For services the SAC usually starts with 99. Software development, consulting, design and maintenance sit in different SAC heads - pick the one that describes what you actually did.

3.4 A mixed invoice needs a line per code, with its own rate. One invoice with one rate covering three different services is the most common filing error.

3.5 Keep a `hsn-sac.md` in your repo or drive: code, description, rate, and one example of what you sold under it. When your accountant asks in March, you will have the answer.

3.6 If a rate changed in the September 2025 rationalisation, note both the old and new rate against the code and the date of change, so historical invoices still reconcile.

Gate: every line item has a code and a rate, with a written mapping table.

## Stage 4 - Charge the right tax for the place of supply

4.1 Two questions decide the tax: where is the supplier, and where is the place of supply.

4.2 Intra-state (place of supply in your own state): split the rate equally into CGST and SGST. An 18% service becomes 9% CGST plus 9% SGST.

4.3 Inter-state (place of supply in another state): charge IGST at the full rate, 18% in the same example.

4.4 For services to a registered business, the place of supply is generally the recipient's location. For services to an unregistered consumer, it is generally the supplier's location - which is why an Indian freelancer billing an unregistered overseas client treats it as export.

4.5 Export of services is zero-rated with a refund path, but only if the conditions are met: supplier in India, recipient outside, place of supply outside, payment in convertible foreign exchange, and neither party a mere establishment of the other.

| Scenario | Supplier state | Place of supply | Tax |
|---|---|---|---|
| Local client, registered | Karnataka | Karnataka | CGST 9% + SGST 9% |
| Client in another state | Karnataka | Maharashtra | IGST 18% |
| Unregistered consumer, same state | Karnataka | Karnataka | CGST + SGST |
| Client outside India | Karnataka | Outside India | zero-rated export, with LUT |
| Goods moving inter-state | Karnataka | delivery state | IGST |

4.6 Never split one invoice across two tax treatments. If half the work is in one state and half in another, issue two invoices with two places of supply.

Gate: the template computes tax from place of supply, not from a hardcoded split.

## Stage 5 - Number invoices so they reconcile

5.1 One continuous series per financial year, per registration, with no gaps. A gap is the first thing an auditor asks about.

5.2 Maximum 16 characters, and only letters, digits, slash and hyphen are allowed in the serial number.

5.3 A workable scheme: `INV/2026-27/0001`, where the middle segment is the financial year and the last is a zero-padded counter.

5.4 Credit notes get their own series: `CRN/2026-27/0001`, and must reference the original invoice number and date.

5.5 A cancelled invoice keeps its number, marked cancelled, with the reason recorded. Deleting the row creates a gap you cannot explain.

5.6 Never renumber after the fact, even to fix a mistake. Issue a credit note and a fresh invoice.

```sql
CREATE TABLE invoices (
  id            BIGSERIAL PRIMARY KEY,
  series        TEXT NOT NULL,                 -- INV/2026-27
  serial        INTEGER NOT NULL,
  invoice_no    TEXT GENERATED ALWAYS AS (series || '/' || lpad(serial::text, 4, '0')) STORED,
  issued_on     DATE NOT NULL,
  supplier_gstin TEXT NOT NULL,
  buyer_gstin   TEXT,
  place_of_supply CHAR(2) NOT NULL,            -- state code, e.g. 29 for Karnataka
  is_export     BOOLEAN NOT NULL DEFAULT FALSE,
  taxable_value NUMERIC(14,2) NOT NULL,
  cgst          NUMERIC(14,2) NOT NULL DEFAULT 0,
  sgst          NUMERIC(14,2) NOT NULL DEFAULT 0,
  igst          NUMERIC(14,2) NOT NULL DEFAULT 0,
  status        TEXT NOT NULL DEFAULT 'issued', -- issued | cancelled
  cancel_reason TEXT,
  UNIQUE (series, serial)
);
```

Gate: a numbering function that cannot produce a duplicate or a gap, tested with a concurrent insert.

## Stage 6 - Handle e-invoicing when it applies

6.1 E-invoicing is mandatory for B2B supplies above the notified aggregate turnover threshold, currently ₹5 crore. Below it, you issue a normal tax invoice.

6.2 E-invoicing means reporting the invoice to the Invoice Registration Portal, which returns an IRN and a signed QR code. The invoice is not valid without them once you are in scope.

6.3 The IRN is a 64-character hash. Store it, and print the QR code on the invoice - a buyer's system will look for it.

6.4 A reported invoice cannot be edited. Corrections happen through a credit note, or by cancelling within 24 hours of generation.

6.5 The e-way bill is separate: needed for movement of goods above ₹50,000, generated on the e-way bill portal, and tied to the invoice number.

6.6 Build the JSON payload once and keep it in version control; the schema changes and a rejected payload at 23:00 on the 10th is a bad evening.

```json
{
  "Version": "1.1",
  "TranDtls": { "TaxSch": "GST", "SupTyp": "B2B", "RegRev": "N" },
  "DocDtls":  { "Typ": "INV", "No": "INV/2026-27/0001", "Dt": "15/11/2026" },
  "SellerDtls": { "Gstin": "<supplier-gstin>", "LglNm": "<legal name>", "Loc": "Bengaluru", "Pin": 560001, "Stcd": "29" },
  "BuyerDtls":  { "Gstin": "<buyer-gstin>", "LglNm": "<buyer name>", "Loc": "Mumbai", "Pin": 400001, "Stcd": "27", "Pos": "27" },
  "ItemList": [
    { "SlNo": "1", "IsServc": "Y", "HsnCd": "<sac>", "Qty": 1, "UnitPrice": 100000,
      "TotAmt": 100000, "AssAmt": 100000, "GstRt": 18, "IgstAmt": 18000, "TotItemVal": 118000 }
  ],
  "ValDtls": { "AssVal": 100000, "IgstAmt": 18000, "TotInvVal": 118000 }
}
```

Gate: one test invoice accepted by the sandbox portal, IRN stored and QR printed.

## Stage 7 - Correct mistakes with credit notes

7.1 A credit note reduces the value of a supply already invoiced: a discount after the fact, a return, or an overcharge.

7.2 It must reference the original invoice number and date, carry its own series, and state the reason.

7.3 A credit note affects the return period in which it is issued, not the original period. Timing matters for the GSTR-3B you file.

7.4 Time limit: a credit note for a financial year must be issued by 30 November of the following year, or the date of the annual return, whichever is earlier.

7.5 A debit note works the other way, for an undercharge. Same discipline: series, reference, reason.

7.6 Never edit a sent invoice to fix an amount. The buyer has already booked it, and the mismatch surfaces in their reconciliation.

Gate: one credit note issued end to end against a real invoice, with the reference field filled.

## Stage 8 - File on the calendar

8.1 Two returns do most of the work: GSTR-1 (outward supplies) and GSTR-3B (summary and payment).

| Return | Covers | Due date | Frequency |
|---|---|---|---|
| GSTR-1 | outward supplies | 11th of the next month | monthly, or quarterly under QRMP |
| GSTR-1 (QRMP) | outward supplies | 13th after the quarter | quarterly |
| GSTR-3B | summary and tax payment | 20th of the next month | monthly |
| GSTR-3B (QRMP) | summary and payment | 22nd or 24th after the quarter, by state group | quarterly |
| GSTR-9 | annual return | 31 December after the financial year | yearly, above the notified turnover |
| CMP-08 | composition | 18th after the quarter | quarterly |

8.2 File even with zero turnover. A nil return is a filing; skipping it accrues a late fee per day.

8.3 Pay by the due date; interest on late payment runs at 18% per annum.

8.4 Reconcile GSTR-2B (your input credit statement) against your purchase register every month. Credit you never claimed is money you donated.

8.5 Keep a calendar with the 11th and 20th recurring, plus a reminder 3 days before each, and one person named as responsible.

8.6 Under the QRMP scheme you pay monthly through a PMT-06 challan by the 25th and file quarterly - a different rhythm that catches people out.

Gate: a calendar with every due date for the year, and an owner.

## Stage 9 - Keep records that survive an audit

9.1 Retain records for 72 months (6 years) from the due date of the annual return for that year.

9.2 Keep the invoice, the e-way bill, the proof of payment, the credit notes and the return filings together, per financial year.

9.3 Store the IRN, the signed QR and the acknowledgement number alongside each e-invoice; the portal will not give them back on demand.

9.4 Back up monthly to storage you control, not only to the billing tool's database. A tool shutting down is not an acceptable reason to lose six years of records.

9.5 Reconcile once a quarter: turnover per your books, per GSTR-1, and per GSTR-3B. Three numbers that disagree is a notice waiting to happen.

9.6 If you handle customer personal data for billing, note where it is stored and how long you keep it - the DPDP Act applies to that data separately from GST.

Gate: six years of records in one folder per year, with a backup that has been restored once.

## Stage 10 - Build it into your software

10.1 Compute tax from (supplier state, place of supply, is_export) and never from a per-customer flag someone set once.

10.2 Validate GSTIN format before saving: 15 characters, state code in the first two, checksum valid. A wrong GSTIN produces a mismatch in the buyer's return.

10.3 Make invoice numbers come from the database, not from the application clock. Two servers generating `INV-2026-001` at once is a duplicate you cannot delete.

10.4 Render the invoice server-side to PDF, and keep the exact PDF you sent. A re-render after a template change is not the document the buyer holds.

10.5 Round off correctly: tax amounts to two decimals, and the total must equal the sum of the parts. Off-by-one-paisa totals are rejected by buyer systems.

10.6 Log every state change on an invoice: issued, sent, cancelled, credit-noted, with a timestamp and a user.

Gate: a test suite covering intra-state, inter-state, export, credit note and cancellation.

## Worked example

A Bengaluru consultancy billing three clients in one month.

| Client | State | Service | Taxable | Tax | Invoice |
|---|---|---|---|---|---|
| Local manufacturer | Karnataka | audit | ₹80,000 | CGST 7,200 + SGST 7,200 | INV/2026-27/0001 |
| Mumbai startup | Maharashtra | development | ₹1,50,000 | IGST 27,000 | INV/2026-27/0002 |
| US client | outside India | retainer | ₹2,00,000 | zero-rated, LUT on file | INV/2026-27/0003 |

The mistakes this table prevents: charging IGST to the local client, splitting the Mumbai invoice into CGST and SGST, and charging 18% on the export because "it is a service". Each of those three is a common filing error and each is visible in the buyer's input credit statement.

## Quality checklist

- [ ] Registration obligation checked against the correct threshold
- [ ] Special category state rule checked if relevant
- [ ] All sixteen invoice particulars present in the template
- [ ] HSN or SAC code per line, digits correct for turnover
- [ ] Place of supply recorded on every invoice
- [ ] CGST plus SGST intra-state, IGST inter-state, never mixed
- [ ] Export invoices marked zero-rated with LUT on file
- [ ] One continuous numbering series per financial year
- [ ] Cancelled invoices marked, never deleted
- [ ] Credit notes in their own series, referencing the original
- [ ] E-invoicing enabled above the notified threshold with IRN stored
- [ ] GSTR-1 and GSTR-3B dates in a calendar with an owner
- [ ] Nil returns filed, not skipped
- [ ] GSTR-2B reconciled against purchases monthly
- [ ] Records retained for 72 months with a tested backup
- [ ] GSTIN checksum validated before saving a buyer
- [ ] Invoice PDF archived as sent, not re-rendered

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Buyer's accountant rejects the invoice | Missing place of supply or GSTIN | Add all sixteen particulars, print place of supply |
| Input credit mismatch in the buyer's return | IGST charged on an intra-state supply | Derive tax from supplier state versus place of supply |
| Notice for a gap in invoice numbers | Cancelled invoice deleted from the table | Keep the row, mark cancelled with a reason |
| Duplicate invoice numbers | Numbers generated in the app, two instances running | Generate from a database sequence, unique constraint |
| Credit note rejected | No reference to the original invoice | Fill the original invoice number and date |
| Late fee every month | Nil months not filed | File nil returns on the 11th and 20th regardless |
| Interest charged on payment | Tax paid after the 20th | Pay by the due date, calendar with a 3-day warning |
| E-invoice not accepted at 23:00 | Payload schema changed, hardcoded version | Version the JSON payload and validate against the schema |
| Off-by-one-paisa total rejected | Rounding per line instead of on the total | Round at the tax-head level, then total |

## Copy-ready agent prompt

> Read the skill at the URL above and set up GST invoicing for my business. Ask me: my state, my turnover, whether I am registered and my GSTIN, what I sell, and whether I sell to businesses in other states or outside India. Then tell me whether registration is required and why, build an invoice template with all sixteen particulars, map my services to SAC codes with rates, and write the tax logic as a function of supplier state, place of supply and export status. Then give me the numbering scheme with the database constraint, the credit note flow, the e-invoicing payload for my case, and a filing calendar with due dates. Tell me which thresholds I must confirm on gst.gov.in before filing.
