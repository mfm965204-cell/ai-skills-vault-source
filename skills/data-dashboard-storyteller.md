---
name: data-dashboard-storyteller
description: Turn raw CSV/Excel/API data into a decision-ready dashboard or insight deck - audit, clean, define KPIs, choose the right chart for each question, design the layout, write the narrative and ship it.
version: 1.0.0
license: MIT
tags: [data, analytics, dashboard, charts, kpi, storytelling, python]
---

# Data Dashboard Storyteller

A dashboard is an argument made of numbers. Every chart must answer a question someone actually asked, or it should not exist.

## When to use this skill

- Given a spreadsheet or export and asked "what does this say?"
- Building an executive or operational dashboard.
- Producing a data-backed report, board update or analysis deck.
- Cleaning messy data before anyone draws conclusions from it.

## Stage 1 - Data audit (before any chart)

Answer these in writing:

1. **Rows, columns, date range, grain.** What does one row represent? (One order? One order line? One day?) Getting the grain wrong invalidates everything downstream.
2. **Completeness.** Null rate per column. Which columns are unusable (>40% null)?
3. **Duplicates.** Exact duplicates and duplicate business keys (`order_id` appearing twice with different values - a red flag, not something to `drop_duplicates` blindly).
4. **Types.** Dates stored as text, numbers stored as text with commas, currency mixed in one column, negative values where they should not exist.
5. **Outliers.** Compute z-scores or IQR. Investigate before removing - an outlier is often the story.
6. **Coverage gaps.** Missing days, missing regions, a month that stops mid-way.
7. **Definition conflicts.** Does "revenue" include tax, refunds, shipping? Ask. Two teams with different definitions is the most common cause of a wrong dashboard.

Never silently fix data. Produce a `DATA_NOTES.md` with every transformation, the count of affected rows, and the reason.

## Stage 2 - Cleaning protocol

- Work on a copy; keep `raw/` untouched.
- Parse dates explicitly with a format; never let the parser guess between DD/MM and MM/DD.
- Currency and percentages to numeric; strip symbols and separators by locale.
- Standardise categorical values with an explicit mapping table (do not fuzzy-match silently; log what merged).
- Handle missing values by column with a stated strategy: drop row, forward-fill (time series only), or leave null and exclude from that metric's denominator. Never zero-fill a metric - it fabricates performance.
- Record row counts at every step: `10000 -> 9870 (dropped 130 unparseable dates)`.

## Stage 3 - Define the KPIs

For each metric, write: name, definition (formula), grain, source column, owner, and what decision it informs. A KPI with no decision attached is decoration.

Standard traps:

- Averages of averages (Simpson's paradox) - recompute from raw totals.
- Rates without denominators - always show n.
- Cumulative totals compared across unequal periods.
- Percentage change off a tiny base ("up 400%" from 2 to 10).

## Stage 4 - Choose the chart by the question

| Question | Chart | Avoid |
|---|---|---|
| How has it changed over time? | Line (max 4 series) | Area with overlapping fills |
| How do categories compare? | Horizontal bar, sorted | Pie with more than 3 slices |
| What is the composition? | Stacked bar or treemap | 3D pie |
| How is it distributed? | Histogram, box plot | Bar of binned averages |
| Are two things related? | Scatter with trend line | Dual-axis line |
| Where is it happening? | Choropleth or ranked bar | Bubble maps without scale |
| How does a funnel flow? | Funnel or stage bar | Waterfall for non-additive |
| What is the share of total over time? | 100% stacked area (max 3) | Stacked area with 8 series |

Rules: sort bars by value unless the category has a natural order. Start line axes at zero unless the variation is the point - and if you do, label it. Never dual-axis to imply correlation. Colour: one accent for the point, grey for context. Label directly on the chart instead of a legend where possible.

## Stage 5 - Dashboard layout

1. **Row 1: the answer.** 3-5 headline numbers with period-over-period change and a one-line "so what".
2. **Row 2: the driver.** The one chart that explains why the headline moved.
3. **Row 3: segments.** Breakdown by the 2-3 dimensions that matter.
4. **Row 4: detail.** Table for the people who want rows.
5. Filters top-left, consistent across the page, with the current state always visible.

Design: max 6-8 visual elements per screen, one accent colour, grey for everything non-essential, no borders where a background tint will do, number formatting that a human reads instantly (`₹1.2 Cr`, not `12000000.00`).

## Stage 6 - The narrative

Structure the written readout as:

1. **Headline** - the single sentence conclusion, with the number.
2. **What changed** - the movement, versus the right comparison (last period, same period last year, target).
3. **Why** - the driver, decomposed (price x volume, mix shift, one segment).
4. **So what** - the decision this implies.
5. **What would change my mind** - the data that would falsify the conclusion.

Attribution discipline: correlation stated as correlation. Any causal claim needs a mechanism or a test.

## Stage 7 - Build it

- Python: pandas for prep, then matplotlib/plotly for a static or interactive output; or a single self-contained HTML with inline SVG and no CDN.
- Excel/Sheets: pivot + slicers for stakeholders who need to self-serve, plus a `README` sheet with definitions.
- BI tool: build the semantic layer once (metrics defined centrally), then dashboards read from it. Never re-implement a metric per chart.

## Stage 8 - Deliver and verify

- [ ] Every number traces to a query or a cell; no hand-typed figures
- [ ] Row counts reconcile with the source
- [ ] Definitions written down and visible in the dashboard
- [ ] Periods are comparable (equal days, equal scope)
- [ ] Charts readable at 1366x768 and on a phone
- [ ] Colour-blind safe palette, contrast checked
- [ ] Data refresh documented with its timestamp on screen

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Numbers do not add up | Mixed grain or double-counted join | Fix the join key, verify totals against source |
| Dashboard nobody opens | Metrics not tied to a decision | Cut to 5 metrics with owners |
| Wrong trend direction | Partial final period included | Exclude incomplete periods or mark them |
| Pretty but useless | Chart chosen by aesthetics | Re-derive from Stage 4 table |
| "Up 300%" | Tiny denominator | Show absolute numbers and n |

## Copy-ready agent prompt

> Read the skill at the URL above. I will attach a CSV/Excel. Run the Stage 1 audit and produce `DATA_NOTES.md` with row counts and every issue found, asking me about ambiguous definitions before cleaning. Then define the KPIs with formulas, pick charts using the Stage 4 table, build the dashboard, and write the Stage 6 narrative. Every number must be computed from the data - never estimate or invent one.
