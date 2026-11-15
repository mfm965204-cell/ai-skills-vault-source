---
name: receipt-ocr-pipeline
description: Turn a folder of photographed receipts into a validated expense table, with confidence thresholds, a human queue and an audit trail per field.
version: 1.0.0
license: MIT
tags: [data, ocr, receipts, expenses, automation]
---

# Receipt OCR Pipeline

Receipts arrive as phone photos at an angle, in bad light, with a GST number printed in 6 pt. An OCR pass that reports "97% confidence" still gets the total wrong on the 3 receipts that matter, and a wrong total in an expense claim is a compliance problem, not a rounding error.

This skill builds a pipeline with three outcomes per receipt: auto-accepted, needs a human, or rejected. Each field carries a confidence, totals are cross-checked against line items, and every accepted value has the crop that produced it. You end with a table that survives an audit and a review queue that stays small.

## When to use this skill

- 50-5,000 receipts a month arrive as photos or scans and someone retypes them.
- Your OCR output goes straight into accounting with no confidence gate.
- Receipts in 2-3 languages or scripts break the extractor.
- An auditor asked how a number was captured and nobody could show the source.

Do NOT use for: invoice generation, tax filing decisions, or handwriting-heavy documents where OCR is the wrong tool. Handle personal and financial data lawfully: receipts contain names, card fragments and GST numbers, so store the minimum, restrict access, and delete images on a defined schedule.

## Stage 1 - Define what a valid receipt is before parsing

1.1 Required fields: merchant, date, total, currency, and a payment method. Everything else is optional.

1.2 Conditional fields: GST number and tax amount for a business claim, item lines for a category-based claim.

1.3 Define the accepted date window - typically 90 days before the claim - and reject anything outside it with a reason.

1.4 Define currency handling: one currency per receipt, with an exchange rate and its source date stored for foreign receipts.

| Field | Required | Validation |
|---|---|---|
| merchant | yes | non-empty, under 60 chars |
| date | yes | ISO date, within 90 days |
| total | yes | positive, 2 decimals, under a cap |
| currency | yes | ISO 4217 code |
| tax id | for business claims | format check per country |
| line items | optional | sum equals total within 1% |

Gate: every field has a rule, and every rule has a failure reason that a reviewer can read.

## Stage 2 - Preprocess the image before OCR

2.1 Deskew by more than 2 degrees. A 5-degree tilt costs several points of character accuracy.

2.2 Convert to grayscale and apply adaptive thresholding. A photo of a thermal receipt in daylight has a bright spot that a global threshold loses.

2.3 Downscale to 1,500-2,000 px on the long edge. Larger does not improve accuracy and slows the run; smaller loses 6 pt text.

2.4 Crop to the document if a detector finds the quadrilateral, but keep 5% margin so edge characters are not cut.

2.5 Reject images under 800 px on the long edge with a reason, rather than parsing a blur into plausible garbage.

```python
import cv2
def prep(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if max(img.shape) < 800:
        raise ValueError("image too small for reliable OCR")
    scale = 1800 / max(img.shape)
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 15)
    return img
```

Gate: 20 sample receipts pass preprocessing with no clipped characters and no images under 800 px accepted.

## Stage 3 - Extract fields with confidence, not just text

3.1 Run OCR with word-level boxes and per-word confidence. Field confidence is the minimum word confidence in that field, not the average.

3.2 Extract the total with a labelled regex over the text near "total", "amount", "grand total" and their local-language equivalents, then take the rightmost currency value on that line.

3.3 Extract the date by trying 4 formats explicitly: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, and a month-name form. Do not let a library guess.

3.4 Keep the bounding box of every extracted field. The crop is the evidence a reviewer checks.

3.5 Store the raw OCR text per receipt. Re-parsing is cheap; re-OCR of a deleted image is impossible.

| Field | Method | Confidence source |
|---|---|---|
| merchant | top 3 lines, largest font | min word confidence |
| date | 4 explicit formats | regex match quality |
| total | labelled regex, rightmost | min word confidence |
| tax id | format-specific regex | min word confidence |
| line items | row pattern with amount on the right | count matched |

Gate: every field has a value, a confidence and a bounding box, or an explicit null with a reason.

## Stage 4 - Cross-check the arithmetic

4.1 Sum the line items and compare to the total. A difference over 1% or over ₹2 fails the receipt.

4.2 Check tax: subtotal plus tax equals total within the same tolerance.

4.3 Check the date against the claim window and against the file's own EXIF date. A receipt dated after the photo was taken is suspicious.

4.4 Check the currency symbol against the country of the merchant text. A ₹ symbol with a US address is a misparse.

4.5 Cap the total at a plausible maximum per category. A ₹4,80,000 "coffee" is a decimal error, and the cap catches it before a human does.

Gate: every auto-accepted receipt passes all five arithmetic checks.

## Stage 5 - Set the confidence gate

5.1 Auto-accept only when every required field has confidence at least 0.90 and all arithmetic checks pass.

5.2 Send to review when any required field is 0.60-0.90, or when an arithmetic check fails by less than 5%.

5.3 Reject outright below 0.60 on any required field, or when arithmetic fails by more than 5%, or when the image is unreadable.

5.4 Tune the thresholds on 100 labelled receipts. A 0.90 gate on a noisy scanner queue produces a review queue nobody clears.

| Confidence | Arithmetic | Outcome |
|---|---|---|
| 0.90+ all fields | passes | auto-accept |
| 0.60-0.90 any field | passes or under 5% off | human review |
| under 0.60 any field | any | reject with reason |
| any | over 5% off | reject with reason |

Gate: 100 labelled receipts run through the gate, with the auto-accept rate between 55% and 85%.

## Stage 6 - Build the review queue so a human can go fast

6.1 One receipt per card: the cropped image beside the extracted fields, with the failing field highlighted.

6.2 Pre-fill every field with the extracted value so the reviewer corrects instead of typing.

6.3 Show the reason for review in one line: "total confidence 0.71" beats a red border.

6.4 Keyboard-only operation: Tab between fields, Enter to accept, one key to reject with a reason from a short list.

6.5 Target 20-30 seconds per receipt. Above 60 seconds, the queue will be abandoned and the pipeline is worse than retyping.

| Queue feature | Target | Why |
|---|---|---|
| fields pre-filled | 100% | correct, do not type |
| failing field highlighted | yes | one look |
| keyboard only | yes | speed |
| reject reasons | 5 or fewer | consistency |
| time per item | 20-30 s | keeps the queue alive |

Gate: a reviewer clears 50 queued receipts in under 25 minutes with keyboard only.

## Stage 7 - Store the audit trail

7.1 One row per receipt with the image path, the raw OCR text, each field's value, confidence and bounding box, and the final accepted value.

7.2 One row per correction: who changed what, from what, to what, and when. A correction without an author is not an audit trail.

7.3 Keep the image for the retention period the policy states, then delete it and keep the extracted data and the hash.

7.4 Store a hash of the original image so a later re-upload can be matched to the same record.

```sql
CREATE TABLE receipt_fields (
  receipt_id   uuid NOT NULL,
  field        text NOT NULL,
  raw_value    text,
  confidence   numeric(4,3),
  bbox         jsonb,
  final_value  text,
  corrected_by text,
  corrected_at timestamptz,
  PRIMARY KEY (receipt_id, field)
);
```

Gate: for any accepted value, the system can show the crop, the OCR text and the person who confirmed it.

## Stage 8 - Handle the languages and formats that break it

8.1 Run language detection on the merchant block, not the whole image, and route to the right model or script pack.

8.2 Thermal receipts fade; a photographed faded receipt needs a contrast stretch before thresholding.

8.3 Handwritten totals: send to review always, regardless of confidence. Handwriting confidence is not comparable to print.

8.4 Multi-page invoices: parse each page and join on the invoice number, then run arithmetic checks on the joined document.

| Case | Handling | Auto-accept |
|---|---|---|
| printed, good light | standard path | yes |
| thermal, faded | contrast stretch | if confidence holds |
| handwritten total | review queue | never |
| multi-page | join then check | yes if all pages parse |
| non-Latin script | language-specific pack | yes if confidence holds |

Gate: each case type has 5 test receipts and a recorded outcome.

## Stage 9 - Measure accuracy, not throughput

9.1 Per field accuracy on the auto-accepted set, measured monthly on a 50-receipt human-checked sample. A 99% total accuracy with 92% merchant accuracy is a problem.

9.2 Review queue rate and average handling time, week over week.

9.3 Correction rate per field. The field with the highest correction rate is where to spend the next hour.

9.4 Track the cost per receipt: OCR calls plus review minutes. A pipeline that costs more than retyping is not a pipeline.

| Metric | Target | Alarm |
|---|---|---|
| total field accuracy (accepted) | 99%+ | under 97% |
| merchant accuracy | 95%+ | under 90% |
| auto-accept rate | 55-85% | under 40% |
| review time per receipt | 20-30 s | over 60 s |
| correction rate per field | under 5% | over 10% |

Gate: 3 months of per-field accuracy recorded from human-checked samples.

## Worked example

A 40-person company processing 900 receipts a month from phone photos.

| Item | Before | After |
|---|---|---|
| Method | manual retyping | OCR with confidence gate |
| Auto-accepted | 0 | 690 of 900 (77%) |
| Human review | 900 | 168 |
| Rejected | 0 | 42, with reasons |
| Total field accuracy | 100% by definition | 99.4% on accepted |
| Merchant accuracy | 100% | 96% |
| Time per receipt | 95 s | 24 s in review |
| Audit trail | spreadsheet, no author | per-field corrections with author |

The rejected 42 were mostly images under 800 px and two duplicate uploads caught by the image hash. The merchant field was the weakest at 96% because logos replace the merchant name on 1 in 8 receipts.

## Quality checklist

- [ ] Required and conditional fields defined with rules
- [ ] Date window and currency handling defined
- [ ] Images under 800 px rejected before OCR
- [ ] Deskew, grayscale, adaptive threshold applied
- [ ] Long edge scaled to 1,500-2,000 px
- [ ] Word-level confidence captured per field
- [ ] Total extracted from a labelled line, not the largest number
- [ ] Date parsed with 4 explicit formats
- [ ] Bounding box stored for every field
- [ ] Raw OCR text stored per receipt
- [ ] Line items summed and compared to the total, tax cross-checked
- [ ] Per-category cap catches decimal errors
- [ ] Confidence gate at 0.90 auto, 0.60-0.90 review, below 0.60 reject
- [ ] Review queue is keyboard-only and pre-filled
- [ ] Every correction records who, what and when
- [ ] Retention policy applied to images, hash kept after deletion

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Total off by a factor of 10 | Decimal separator misread on a labelled line | Cross-check line items and apply a category cap |
| Date parsed as the expiry date | Library guessed the format | Try 4 explicit formats, prefer the labelled date |
| Plausible garbage accepted | Blurred image parsed instead of rejected | Reject under 800 px and low field confidence |
| Review queue never clears | Gate too strict for the input quality | Tune thresholds on 100 labelled receipts |
| Merchant is the logo text | OCR read the logo, not the name | Take the top 3 lines by font size, then review |
| Reviewer takes 90 s per item | Empty fields, mouse only | Pre-fill and support keyboard only |
| Auditor cannot verify a number | No bounding box or raw text kept | Store crop and raw OCR per field |
| Duplicate expense claimed twice | Same image uploaded twice | Hash the image, block duplicates |
| Faded thermal receipt fails | No contrast stretch | Stretch before thresholding |
| Non-Latin receipts fail entirely | Wrong script pack | Detect language on the merchant block |

## Copy-ready agent prompt

> Read the skill at the URL above and build my receipt pipeline. Ask me: how many receipts a month, how they arrive, which languages, what my expense categories and caps are, and what my retention policy says. Then give me the field schema with required and conditional rules, the preprocessing steps with the 800 px rejection, the extraction approach per field with confidence and bounding boxes, the five arithmetic cross-checks, the confidence gate at 0.90 and 0.60 with the review and reject outcomes, the keyboard-only review queue design with a 20-30 second target, the audit table that records every correction with an author, and the metrics table with per-field accuracy targets. Tell me the auto-accept rate to expect on my volume and the field most likely to need review.
