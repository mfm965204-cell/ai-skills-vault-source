---
name: chart-design-system
description: Set chart rules that make dashboards readable: chart type
by question, axis and colour standards, direct labels, Indian number
formatting and an accessible table alternative.
version: 1.0.0
license: MIT
tags: [design, dataviz, charts, accessibility, dashboards]
---

# Chart Design System

A dashboard with 14 charts where every one is a different shade of the
same blue is not a design; it is a data dump with rounded corners.
Readers cannot tell which number matters, and the chart that would
have answered the question is on a tab nobody opened.

This skill produces a chart spec: which chart answers which question,
when the axis starts at zero, how many colours are allowed and what
each means, how numbers are formatted for an Indian audience, and what
a chart must carry to be accessible. It ends as a linted set of rules
in code.

## When to use this skill

- Your dashboard has more than 8 charts and the team cannot say which one to look at first.
- Two charts on one screen use the same colour for different series.
- Numbers are formatted three ways across the product: `1,00,000`, `100000`, `1L`.
- You are adding a chart library and need rules before the first pull request lands.

Do NOT use for: the narrative structure of a report (that is data
storytelling), or choosing a BI tool.

## Stage 1 — List the questions, not the charts

A chart exists to answer a question someone asks weekly. Start from
the questions.

1.1 Write every question the dashboard must answer, in the words the team uses: "is revenue growing faster than last quarter".

1.2 Cap the dashboard at 6 questions; anything beyond that is a report, not a dashboard.

1.3 Delete every chart that answers no question on the list, however pretty it is.

| Question shape | Chart | Why |
|---|---|---|
| How does it change over time | line | slope is the message |
| How do categories compare | horizontal bar | length is easy to compare |
| What is the composition | stacked bar | parts of a whole, ordered |
| How is it distributed | histogram | shape of the spread |
| Are two measures related | scatter | correlation, with a trend line |

Gate: at most 6 questions, each with one chart, and no chart without a
question.

## Stage 2 — Choose the type from the question

The chart type is decided by the comparison the reader has to make,
not by the library's gallery.

2.1 Trends over time get a line; use bars only when the periods are discrete events, not continuous time.

2.2 Comparison across categories gets a horizontal bar sorted by value, because sorted length is read faster than colour or position.

2.3 Composition gets a stacked bar; avoid a pie beyond 3 slices, and never use a donut for more than 2.

Gate: every chart's type matches its question shape in the table, and
no pie has more than 3 slices.

## Stage 3 — Fix the axes

Axis mistakes create false impressions more often than colour
mistakes.

3.1 Bars start at zero, always; a bar chart with a truncated axis overstates differences by the ratio of the truncation.

3.2 Lines may start away from zero when the variation is small, and the axis must then be labelled clearly with the range.

3.3 Never use a dual y-axis: two scales on one plot let you imply any correlation you like.

| Chart | Baseline | Allowed truncation |
|---|---|---|
| Bar, column | 0 | none |
| Line | 0 by default | yes, if range is labelled |
| Area | 0 | none, area implies magnitude |
| Scatter | not applicable | axis range labelled |

Gate: every bar chart starts at zero and no chart on the dashboard has
two y-axes.

## Stage 4 — Limit the palette and give colours meaning

Colour is a limited resource. Eight series is the maximum a reader can
match to a legend.

4.1 Categorical palette of 6 to 8 colours, used in a fixed order, so series 1 is always the same colour across the product.

4.2 Semantic colours reserved: red for negative or breach, green for positive or within target, amber for warning, grey for context or baseline.

4.3 Beyond 8 series, group the tail into "Other" rather than adding colours; and check the palette with a colour-blindness simulator, since red and green must not be the only difference.

Gate: no chart uses more than 8 colours, semantic colours appear only
with their meaning, and the palette passes a deuteranopia check.

## Stage 5 — Label directly and format numbers once

A legend forces the eye to travel. A direct label does not.

5.1 Label series at their end point rather than in a legend where space allows; keep the legend only when lines cross repeatedly.

5.2 Format numbers by one rule: below ₹1 lakh show the full number with Indian grouping (`₹84,500`), from ₹1 lakh use `₹1.25 lakh`, from ₹1 crore use `₹2.4 crore`.

5.3 Always state the unit and the period: `₹ lakh, monthly`, not just `Revenue`.

```python
def inr(n: float) -> str:
    if abs(n) >= 1e7:
        return f"₹{n/1e7:.2f} crore"
    if abs(n) >= 1e5:
        return f"₹{n/1e5:.2f} lakh"
    return f"₹{n:,.0f}"          # Indian grouping applied by the formatter
```

Gate: every chart carries a unit and a period, and all numbers use the
same formatter.

## Stage 6 — Remove ink that carries no information

Gridlines, borders, gradients and 3D effects compete with the data.

6.1 Remove chart borders and background fills; keep one horizontal gridline set at most, light enough to ignore.

6.2 No 3D, no drop shadows on data marks, no gradient fills that imply a value change that is not there.

6.3 Keep the title as the finding, not the label: "Revenue up 18% in October" beats "Monthly revenue".

Gate: a chart passes the squint test — at arm's length, the pattern is
visible without reading any label.

## Stage 7 — Specify interaction and tooltips

A tooltip is where precision lives; the chart carries the shape.

7.1 Tooltip content: series name, exact value, period, and the comparison if the chart shows one.

7.2 Hover targets at least 24 px, keyboard reachable, and the same data available in the table alternative.

7.3 No hover-only information that changes a decision — if it matters, it belongs on the chart.

Gate: every chart is fully readable by keyboard, and no
decision-critical value exists only in a hover state.

## Stage 8 — Make every chart accessible

Colour and position are not available to every reader. A table
alternative is the baseline.

8.1 Ship a data table behind a disclosure on every chart, with the same numbers as the visual.

8.2 Give each chart a one-sentence description in the markup that states the finding, not the chart type.

8.3 Ensure text and data marks meet a 3:1 contrast against the background, and 4.5:1 for labels.

Gate: every chart has a table alternative, a finding sentence and
passing contrast values.

## Stage 9 — Encode the rules and lint them

Rules in a document get ignored; rules in the component get followed.

9.1 Build a chart wrapper that takes the data, the question type and the unit, and applies axis, palette and formatting automatically.

9.2 Lint for the failures that recur: a bar with a non-zero baseline, more than 8 colours, a dual axis, a missing unit.

9.3 Keep one page of examples — correct and incorrect — beside the wrapper, because reviewers need to see the rule.

9.4 Call the wrapper with the question type, and let it apply the rules:

```javascript
<Chart
  question="trend"                 // trend | compare | composition | distribution
  data={revenue}
  unit="INR lakh, monthly"
  title="Revenue up 18% in October"
/>
```

Gate: the wrapper is the only way charts are built, and lint fails a
build that violates a rule.

## Worked example - 14 charts to 6

A SaaS revenue dashboard rebuilt against these rules.

| Measurement | Before | After | Change |
|---|---|---|---|
| Charts on the page | 14 | 6 | one per question |
| Distinct colours used | 19 | 7 | fixed categorical order |
| Number formats | 3 | 1 | single formatter |
| Bar charts with truncated axis | 5 | 0 | zero baseline enforced |
| Dual-axis charts | 2 | 0 | split into two charts |
| Time to answer "are we growing" | 40 s | 6 s | direct labels, finding titles |

The biggest win was deleting eight charts. Three of them showed the
same revenue series at different granularities, and one showed a
metric that had been deprecated two quarters earlier.

The dual-axis charts were the ones that misled. One plotted revenue
against churn on independent scales and appeared to show them moving
together; on separate charts, the relationship was not visible at all,
which was the honest answer.

The formatting change was the cheapest improvement. Every number now
runs through one formatter, so a card reading `₹1.25 lakh` and a chart
axis reading `₹1,25,000` are the same value in two contexts a reader
can reconcile.

## Quality checklist

- [ ] At most 6 questions on a dashboard, one chart each.
- [ ] Every chart's type matches its question shape.
- [ ] All bar charts start at zero.
- [ ] No dual y-axis anywhere.
- [ ] Truncated line axes are labelled with the range.
- [ ] Palette has 8 colours or fewer, in a fixed order.
- [ ] Semantic colours used only with their meaning.
- [ ] Palette checked for deuteranopia.
- [ ] Series labelled directly where space allows.
- [ ] One number formatter, with lakh and crore above the thresholds.
- [ ] Every chart states a unit and a period.
- [ ] Titles state the finding, not the metric name.
- [ ] No 3D, gradients or shadows on data marks.
- [ ] Table alternative and a finding sentence on every chart.
- [ ] Chart wrapper is the only construction path, with lint.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Two series look identical | Palette extended past 8 colours with near-neighbours | Group the tail into Other and keep the fixed order |
| Reader misreads a small difference as large | Bar axis truncated to the data range | Force a zero baseline on bars |
| Chart implies a correlation that is not there | Two y-axes on one plot | Split into two charts with their own scales |
| Numbers cannot be reconciled across cards | Three formatters in the codebase | One formatter, applied by the wrapper |
| Chart unreadable for a colour-blind reader | Red and green carry the only distinction | Add shape or direct labels as a second channel |
| Dashboard nobody uses | 14 charts and no named question | Cut to 6 questions, one chart each |
| Screen-reader user gets nothing | Canvas with no table or description | Ship a data table and a finding sentence |

## Copy-ready agent prompt

> Read the skill at the URL above and rebuild my dashboard against a chart system. Start by listing the questions it must answer and cap them at 6, then pick a chart type per question, enforce zero baselines on bars, ban dual axes, define an 8-colour categorical palette with semantic colours, add direct labels and one Indian number formatter with lakh and crore thresholds, and give every chart a table alternative and a finding sentence. Wrap the rules in a single chart component with lint for the recurring failures, then report chart count, colour count, formats and time to answer the top question before and after. Stop and show me any chart that fails a rule.
