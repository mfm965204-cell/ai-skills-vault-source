---
name: pdf-document-automation
description: Turn piles of PDFs into structured data - classify, extract text and tables with OCR where needed, parse to schema, validate, review exceptions and export to Excel or a database, with an accuracy loop.
version: 1.0.0
license: MIT
tags: [pdf, ocr, extraction, documents, automation, invoices, contracts]
---

# PDF Document Automation

PDF is a container, not a format. The first job is always: is there a text layer, or is this a photo of paper?

## When to use this skill

- Extracting invoices, receipts, statements, contracts, forms or reports at volume.
- Reviewing documents against a checklist (clauses, dates, amounts, parties).
- Turning scanned archives into a searchable, structured dataset.
- Building a "drop a PDF, get a row" pipeline.

## Stage 1 - Classify before extracting

For each PDF, detect:

1. **Text layer present?** Extract with PyMuPDF; if a page yields under 50 characters, it needs OCR.
2. **Digital vs scanned vs hybrid.** Hybrid is common: a scanned signature page inside a digital contract.
3. **Layout family.** Invoices from 40 vendors are 40 layouts. Cluster them; one parser per family beats one parser for everything.
4. **Form fields** (`AcroForm`) - read them directly, it is free and exact.
5. **Encryption** - try an empty owner password; if it fails, ask for credentials, never brute force.
6. **Page count and size** - a 400-page file needs streaming and a time budget, not a bigger prompt.

Log a classification summary before writing any extraction logic.

## Stage 2 - Text and table extraction

```python
import fitz  # PyMuPDF
doc = fitz.open(path)
for page in doc:
    text = page.get_text("text")
    if len(text.strip()) < 50:
        pass  # route to OCR
    tables = page.find_tables()  # keep cell geometry, not just the text
```

- Use `get_text("dict")` when you need positions for key-value pairing (label left, value right).
- Tables: `pdfplumber` or `page.find_tables()`. Never reconstruct a table from a raw text dump - columns collapse and numbers land in the wrong field.
- Multi-column layouts: sort blocks by reading order (x, then y) or you will interleave two columns into nonsense.
- Preserve page numbers on every extracted element. Debugging without them is guesswork.

## Stage 3 - OCR when needed

- Render at 300 DPI, grayscale, deskew, then OCR (Tesseract, or a cloud OCR for handwriting).
- Set the language pack explicitly (`eng`, `hin`, `tam`). Multi-language documents need the combined pack.
- OCR confidence per word is your quality signal: below 0.8, flag the page for human review rather than guessing.
- Never OCR a page that already has a good text layer - it is slower and worse.
- Cache OCR output by page hash; re-runs must not re-OCR.

## Stage 4 - Schema and extraction strategy

Define the target first:

```python
class LineItem(BaseModel):
    description: str
    qty: float | None
    unit_price: float | None
    amount: float

class Invoice(BaseModel):
    vendor: str
    invoice_no: str
    invoice_date: date
    currency: str
    total: float
    tax: float | None
    line_items: list[LineItem]
    source_page: int
```

Strategy ladder, cheapest first:

1. **Regex / anchor rules** for stable layouts and form fields. Deterministic, free, auditable.
2. **Table parser + column mapping** for tabular documents.
3. **LLM extraction with the schema** for variable layouts and messy prose. Always with `temperature=0` and structured output.
4. **Hybrid**: rules for the fields that are always in the same place, LLM for the rest. This is the production answer.

For every extracted field, keep a `confidence` and the `source_quote` (the exact text it came from). Verify the quote exists in the page text - that single check catches most hallucinations.

## Stage 5 - Validation (the part that creates trust)

1. Schema validation, then business rules: dates in range, `total == sum(line_items) + tax` within 1%, currency in the allowlist, invoice number unique.
2. Cross-field: invoice date not after due date; line item sum not wildly off the stated total.
3. Duplicate detection by document hash and by `(vendor, invoice_no)`.
4. Arithmetic: recompute every total. A mismatch is a finding, not a rounding error.
5. Confidence gate: below threshold → human review queue, never auto-post.

## Stage 6 - The review loop

- Anything flagged goes to a side-by-side review UI: page image on the left, extracted fields on the right, each with its source quote highlighted.
- A reviewer correction is training data. Store `original`, `corrected`, `field`, `doc_family`. Re-run the parser against the corrected corpus weekly.
- Target: under 5% of documents need review before the pipeline is allowed to auto-post anything financial.

## Stage 7 - Output and delivery

- Excel: one row per document, one sheet per line-item table, a `_meta` sheet with run time, file count and failure list.
- Database: upsert on `(vendor, invoice_no)`; keep the file hash and the original path.
- Always output a `rejects.csv` with the reason per file. Silent drops are how people lose invoices.
- Never overwrite the source PDFs. Copy, then process.

## Stage 8 - Scale and operations

- Process in a queue, not a loop over 5,000 files in one process.
- Time budget per document (30 s), then move on and flag it.
- Cost: a 20-page PDF sent whole to a large model is expensive. Chunk by section, extract per page, merge.
- Monitor: documents per run, auto-extracted %, review %, top failure reasons, cost per document.
- Re-run the full corpus after any parser change and diff the outputs before promoting.

## Quality checklist

- [ ] Text layer detected before any OCR
- [ ] Layout families clustered, one parser per family
- [ ] Tables parsed with geometry, not from text dumps
- [ ] OCR only where needed, with confidence captured
- [ ] Every field has a source quote verified against the page
- [ ] Arithmetic recomputed, totals reconciled
- [ ] Review queue with side-by-side UI
- [ ] `rejects.csv` always produced
- [ ] Duplicate detection on hash and business key

## Copy-ready agent prompt

> Read the skill at the URL above. I will give you sample PDFs and the fields I need. First classify the documents (text layer, layout families, OCR need) and show me the summary. Then define the pydantic schema, write the extraction ladder (rules first, LLM only where needed) with source quotes and confidence, add the validation rules including arithmetic checks, and produce the Excel export plus a rejects CSV. Run it on my samples and report field-level accuracy honestly.
