---
name: spreadsheet-automation-agent
description: Turn a messy manual spreadsheet into a reliable automated workbook - structure audit, formula library, named ranges, validation, conditional formatting, pivots, Apps Script/Office Script automation and a handover note.
version: 1.0.0
license: MIT
tags: [excel, google-sheets, automation, formulas, pivot, operations]
---

# Spreadsheet Automation Agent

Most business spreadsheets are one person's memory written in cells. This skill converts that into a system that survives their holiday.

## When to use this skill

- A spreadsheet is doing work it should not be doing by hand (copy-paste, monthly rebuilds, manual reconciliation).
- Building an invoice, inventory, tracker, roster or report template.
- Fixing a workbook that breaks when rows are added.
- Writing Apps Script / Office Script / VBA automation.

## Stage 1 - Structure audit

Read the workbook and record:

1. **Sheets and their job** - input, calculation, output, reference, archive. Name them so (`01_Input`, `02_Calc`, `03_Report`).
2. **Row grain** - what is one row?
3. **Merged cells, blank rows/columns inside data, subtotal rows, two tables on one sheet.** All four break formulas and pivots. Remove them.
4. **Hard-coded values inside formulas** (`=A2*0.18` - the 18% should be a named cell).
5. **Circular references and volatile functions** (`NOW()`, `INDIRECT()`, `OFFSET()` used at scale).
6. **Colour coding** - is it meaningful (input vs calculated) or decorative?
7. **Who else opens this file, and do they need to edit?**

## Stage 2 - The three-layer architecture

| Layer | Sheet | Rule |
|---|---|---|
| Input | `01_Input` | Only raw data. No formulas. Formatted as a real Excel Table / named range. |
| Calculation | `02_Calc` | All logic. Formulas only. Never hand-edited. |
| Output | `03_Report` | Pivots, charts, dashboard. No raw data. |

Never mix layers. This single rule eliminates most spreadsheet bugs.

## Stage 3 - Formula library

Use dynamic arrays and structured references so formulas survive row growth.

```excel
Total row count        =ROWS(tblSales[ID])
Lookup (any column)    =XLOOKUP([@SKU], tblProducts[SKU], tblProducts[Price], "not found")
Conditional sum        =SUMIFS(tblSales[Amount], tblSales[Region], [@Region], tblSales[Date], ">="&start)
Distinct count         =COUNTA(UNIQUE(tblSales[Customer]))
Running total          =SUMIFS(tblSales[Amount], tblSales[Date], "<="&[@Date])
Rank within group      =COUNTIFS(tblSales[Region],[@Region],tblSales[Amount],">"&[@Amount])+1
Month bucket           =EOMONTH([@Date],0)
Text clean             =TRIM(CLEAN([@Raw]))
```

Rules: `XLOOKUP` over `VLOOKUP`; `SUMIFS` over `SUMPRODUCT` unless genuinely needed; no whole-column references (`A:A`) inside big tables; every constant lives in a named cell on a `00_Config` sheet; wrap fragile parses in `IFERROR` with a visible sentinel like `"CHECK"` rather than `""`.

## Stage 4 - Data integrity

- **Data validation** on every input column: dropdown lists from a reference range, date bounds, decimal ranges, custom formula for cross-field rules.
- **Conditional formatting** to flag exceptions (negative stock, overdue date, duplicate id) - red fill only, and only for things a human must act on.
- **Duplicate detection**: `=COUNTIF(tblSales[Invoice No],[@[Invoice No]])>1`.
- **Protected sheets**: lock calculation and output sheets, leave input cells unlocked, no password on structure (it creates false security and blocks recovery).
- **One row of headers, no merged cells in data.** Ever.

## Stage 5 - Reporting layer

- Pivot tables from the Table, not from a fixed range.
- Refresh strategy: manual button, on-open macro, or Apps Script trigger - state which and why.
- Charts: 3 maximum per report sheet, each answering one question. Number formats set once at the cell level.
- Add a `04_Readme` sheet: what the file does, where to paste data, what each output means, who to call.

## Stage 6 - Automation

**Google Sheets (Apps Script)** - `onEdit` for validation and stamping, time-driven triggers for nightly rollups, `UrlFetchApp` for API pulls.

```javascript
function onEdit(e) {
  const sh = e.range.getSheet();
  if (sh.getName() !== "01_Input" || e.range.getColumn() !== 1) return;
  sh.getRange(e.range.getRow(), 8).setValue(new Date()); // stamp
}
```

**Excel** - Office Scripts (cloud, preferred) or VBA (desktop only). Prefer Power Query for all ingestion and transformation: it is refreshable, auditable and no code.

```excel
Power Query: Folder -> combine CSVs -> clean types -> load to Table
```

Rules: every automation is idempotent (running twice changes nothing), logs to a `99_Log` sheet (timestamp, rows affected, outcome), and never deletes data - archive instead.

## Stage 7 - Performance

Under 20k rows formulas are fine. Above that:

- Replace whole-column `VLOOKUP` with `XLOOKUP` on a Table column.
- Move heavy logic to Power Query or a script, load values only.
- Turn off automatic calculation during bulk writes (`SpreadsheetApp.flush()` after).
- Avoid `INDIRECT`, `OFFSET`, `ARRAYFORMULA` over whole columns, and thousands of `IFERROR` wrappers.
- A file over 10 MB in Google Sheets will be slow no matter what - split it.

## Stage 8 - Handover

Deliver a one-page `README` covering: purpose, sheet map, where to paste data, how to refresh, what the exception colours mean, known limitations, and the change log. Test it by having someone else run the monthly process from the README alone. If they cannot, the file is not done.

## Quality checklist

- [ ] Three layers separated, no mixed sheets
- [ ] No merged cells or blank rows inside data
- [ ] Structured tables and named ranges, no magic numbers
- [ ] Formulas survive inserting a row anywhere
- [ ] Data validation on every input
- [ ] Conditional formatting only for actionable exceptions
- [ ] Automation idempotent and logged
- [ ] Readme tested by a second person
- [ ] File size and calc time acceptable

## Copy-ready agent prompt

> Read the skill at the URL above. I will attach my workbook (or describe it). First run the Stage 1 audit and list every structural problem with the sheet and cell range. Then propose the three-layer rebuild, write the formula library with named ranges, add validation and conditional formatting, automate the repetitive step, and produce the Readme. Give me exact formulas and script code I can paste - no pseudocode.
