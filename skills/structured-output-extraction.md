---
name: structured-output-extraction
description: Extract structured records from messy text with a schema-constrained LLM call, validation, a repair loop and a measured accuracy number instead of a vibe.
version: 1.0.0
license: MIT
tags: [ai, llm, extraction, validation, json-schema]
---

# Structured Output Extraction

"Asking the model for JSON" fails in production for three reasons: it returns prose around the JSON, it invents a field that does not exist in your schema, and it silently drops a record rather than admit it could not read one. Each failure looks like success in a log line and becomes a null in your database.

This skill builds the extraction properly: a JSON schema that constrains the output, a prompt that treats the schema as the contract, a validation layer that rejects anything outside it, a bounded repair loop, and a labelled test set that produces one accuracy number you can defend. It ends with a measured pass rate per field, because "it works" is not a number a reviewer can check.

The number that decides the design: your tolerance per field. A 98% accurate date field and a 98% accurate amount field are different products, and the repair loop budget follows from that difference.

## When to use this skill

- You are pulling fields out of invoices, emails, forms, contracts or chat logs.
- The model returns JSON that fails to parse one time in twenty.
- A field is sometimes null and nobody knows whether that is a model failure or an absent value.
- You need an accuracy number before shipping, not after a complaint.
- **Do NOT use for:** free-form summarisation, classification with a handful of labels, or any extraction over personal data you are not authorised to process - this covers schema-constrained extraction and its evaluation.

## Stage 1 - Define the schema before writing a prompt

The schema is the product. A field you cannot define precisely is a field you will measure badly.

1.1 List the fields the downstream system actually consumes, and delete everything else.

1.2 For each field, write the type, whether it is required, and the allowed format: ISO date, decimal string, enum.

1.3 Decide the null policy explicitly: a missing value is `null`, never an empty string and never `"N/A"`.

1.4 Decide the unit and the currency for every money field, and normalise at extraction time.

1.5 Add a `confidence` field per extracted record only if a human will review the low-confidence ones.

1.6 Version the schema; a change to it invalidates every stored extraction from before.

```json
{
  "type": "object",
  "required": ["invoice_no", "invoice_date", "total", "currency"],
  "additionalProperties": false,
  "properties": {
    "invoice_no":   {"type": ["string", "null"], "maxLength": 32},
    "invoice_date": {"type": ["string", "null"], "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "total":        {"type": ["string", "null"], "pattern": "^\\d+\\.\\d{2}$"},
    "currency":     {"type": "string", "enum": ["INR", "USD", "EUR", "AED"]},
    "line_items":   {"type": "array", "maxItems": 60, "items": {"type": "object"}}
  }
}
```

Gate: a versioned schema with types, required fields, null policy and units, and no field without a consumer.

## Stage 2 - Build a labelled set before the first prompt

You cannot measure what you have not labelled. Fifty examples, labelled by hand, is enough to see the failure modes and cheap enough to finish today.

2.1 Collect 50-100 real inputs covering the shapes you see: clean, scanned, handwritten, multi-page, wrong document type.

2.2 Label every field by hand, including the nulls, and keep the labels in version control.

2.3 Include 10% adversarial cases: a different document type, a duplicate page, a rotated scan.

2.4 Record for each example which field is hardest and why, in one word.

2.5 Split into a development set and a held-out set, 70/30, and do not tune on the held-out set.

2.6 Freeze the labelled set. Adding examples later is a new version, with a new number.

| Slice | Count | Purpose |
|---|---|---|
| Clean digital PDFs | 40 | The easy majority |
| Scanned or photographed | 30 | Real-world degradation |
| Multi-page | 15 | Splitting and continuation |
| Wrong document type | 15 | Refusal behaviour |

Gate: 50 or more labelled examples with nulls labelled, split 70/30, frozen and versioned.

## Stage 3 - Constrain the call, do not request the format

Modern APIs accept a JSON schema and enforce it at decode time. Use that instead of asking politely in the prompt.

3.1 Use the provider's structured-output or tool-calling mode with the schema attached, not a prompt instruction.

3.2 Set temperature to 0 or the lowest available value for extraction.

3.3 Send the document text or image, and nothing else in the message - no chat history.

3.4 Cap output tokens to roughly the size of the largest expected record, so a runaway generation cannot occur.

3.5 Ask for a refusal explicitly: if the document is not the expected type, return `{"error": "wrong_type"}`.

3.6 Log the raw response beside the parsed one for the first 200 calls, so parsing failures are diagnosable.

```python
resp = client.responses.create(
    model="<your-model>",
    temperature=0,
    max_output_tokens=1200,
    response_format={"type": "json_schema", "json_schema": {"name": "invoice", "schema": SCHEMA, "strict": True}},
    input=[{"role": "user", "content": [{"type": "input_text", "text": doc_text}]}],
)
raw = resp.output_text
```

Gate: the schema is enforced by the API, temperature is 0, and the wrong-type refusal path exists.

## Stage 4 - Validate, then repair once

A schema-valid response can still be wrong: a date in the wrong century, a total that does not equal the line items. Validation is business logic, not schema logic.

4.1 Validate types and formats again locally - never trust the transport to be the only check.

4.2 Validate business rules: date within the last 10 years, total equals the sum of line items within ₹1, currency matches the supplier country.

4.3 On a validation failure, send one repair request containing the failing value and the specific rule.

4.4 Cap repair at one attempt; a second failure is a rejection, not another loop.

4.5 Record the repair attempt and its outcome per record, so the repair rate is a visible metric.

4.6 Route rejections to a human queue rather than a null, and count them.

Gate: every record is either valid, repaired, or rejected with a reason - and no record is silently null.

## Stage 5 - Handle the failure modes that are not parse errors

Most production failures are semantic. A model that returns a confident wrong date is worse than one that returns null.

5.1 Detect hallucinated identifiers: an invoice number that does not match any pattern in the document text.

5.2 Detect field swaps: a date in the amount field, or the supplier name in the customer field.

5.3 Detect silent truncation: a line-item array shorter than the number of rows visible in the document.

5.4 Detect unit errors: a total in paise stored as rupees, or a total in thousands.

5.5 Detect refusal drift: the model returning a record for a document it should have refused.

5.6 For each detector, record whether the fix is a prompt change, a validation rule or a rejection.

| Failure | Signal | Detector |
|---|---|---|
| Hallucinated invoice number | Value absent from the document text | Substring check against the source |
| Field swap | Date parses in an amount field | Type and range validation |
| Truncated line items | Fewer items than rows in the document | Row count heuristic from the text |
| Unit error | Total 100x the expected range | Range check against history |
| Refusal drift | A record for a wrong-type document | Ground-truth label comparison |

Gate: each failure mode has a detector, and every detector is exercised by at least one labelled example.

## Stage 6 - Measure per field, not per record

A record is either fully right or not, and that hides which field is failing. Report per-field precision and recall.

6.1 Run the full pipeline over the held-out set and compare field by field against the labels.

6.2 Report per-field accuracy, plus the null accuracy separately - correct nulls matter.

6.3 Report the repair rate and the rejection rate as their own numbers.

6.4 Report a record-level exact match rate for the fields the downstream system requires.

6.5 Slice the results by input type: clean, scanned, multi-page. The average hides the scanned failures.

6.6 Set the shipping threshold per field before looking at the results, and hold to it.

```python
from collections import defaultdict
hits, total = defaultdict(int), defaultdict(int)
for label, pred in zip(labels, preds):
    for field in REQUIRED:
        total[field] += 1
        hits[field] += int(label.get(field) == pred.get(field))
print({f: f"{hits[f]/total[f]:.1%}" for f in REQUIRED})
```

Gate: per-field accuracy on the held-out set, with nulls scored separately and slices reported.

## Stage 7 - Iterate on the weakest field only

Prompt changes have side effects. Change one thing at a time, re-measure on the development set, and keep a log.

7.1 Rank fields by accuracy and take the worst one.

7.2 Look at five failing examples of that field and name the shared cause.

7.3 Change one thing: the schema description, the prompt instruction, a validation rule, or the model.

7.4 Re-measure the development set, then the held-out set once, and record both numbers.

7.5 Revert anything that improves one field and degrades another by more than 1 point.

7.6 Stop when the weakest required field clears your threshold; further tuning is overfitting.

Gate: a change log with one change per row, its before and after accuracy, and no unreverted regression.

## Stage 8 - Ship with a human path and a drift check

Extraction in production decays: suppliers change formats, scanners change, the model version changes.

8.1 Store the raw input, the raw response and the parsed record for every extraction, with the schema version.

8.2 Route rejections and low-confidence records to a review queue with the source document beside them.

8.3 Re-run the held-out set whenever the model version or the prompt changes, and compare with the last run.

8.4 Sample 50 production records a week and label them, to catch drift before a complaint does.

8.5 Alert when the repair rate or the rejection rate moves by more than 20% week over week.

8.6 Keep a rollback: the previous prompt and schema version, deployable in one command.

Gate: raw inputs and responses are stored with the schema version, and drift is sampled weekly.

## Stage 9 - Document the limits for the people downstream

The team consuming the data needs to know what it can and cannot assume. Write that down, in numbers.

9.1 Publish the per-field accuracy and the slices it was measured on.

9.2 Publish the known failure modes and the detectors that catch them.

9.3 Publish the null policy, so a null is read as "absent in the document" rather than "model failed".

9.4 Publish the review-queue path and its expected latency.

9.5 Publish the schema version and what a version change means for stored records.

9.6 Name the owner and the process for reporting a wrong extraction.

Gate: a one-page limits document exists with accuracy numbers, failure modes and the review path.

## Quality checklist

- [ ] Every schema field has a downstream consumer.
- [ ] Null policy is explicit and consistent across fields.
- [ ] Money fields declare unit and currency and are normalised at extraction.
- [ ] The schema is versioned.
- [ ] At least 50 labelled examples exist, split 70/30 and frozen.
- [ ] The labelled set includes wrong-type and degraded inputs.
- [ ] The schema is enforced by the API, not requested in the prompt.
- [ ] Temperature is 0 and output tokens are capped.
- [ ] A wrong-type refusal path exists and is tested.
- [ ] Business rules are validated after schema validation.
- [ ] Repair is capped at one attempt per record.
- [ ] Rejections go to a human queue and are counted.
- [ ] Accuracy is reported per field, with nulls scored separately.
- [ ] Results are sliced by input type.
- [ ] Raw input and raw response are stored with the schema version.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| JSON fails to parse one in twenty | Format requested in the prompt instead of enforced by the API | Use structured output with the schema attached |
| A field is null for 30% of records | Null used for both "absent" and "failed" | Split into null and rejected, and count each |
| Accuracy looks high, downstream still wrong | Record-level scoring hides one failing field | Report per-field accuracy and slice by input type |
| Numbers off by 100x | Unit not normalised at extraction | Declare unit and currency, normalise in the pipeline |
| Repair loop runs five times | No cap, so a bad record burns tokens and time | Cap at one attempt and reject after that |
| Accuracy dropped after a quiet upgrade | Model version changed under the same prompt | Pin the version and re-run the held-out set on change |

## Copy-ready agent prompt

> Read the skill at the URL above and build a structured extraction pipeline for my documents. Ask me for the fields the downstream system consumes and a sample of inputs, then produce a versioned JSON schema with types, null policy and units, a labelling sheet for 50 examples, and the API call using schema-enforced structured output at temperature 0. Add local validation with business rules, a one-attempt repair loop and a rejection queue, then measure per-field accuracy on a held-out split with slices by input type. Finish with the change log and the one-page limits document. Do not claim an accuracy number you have not measured on labelled data.
