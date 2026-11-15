---
name: cohort-retention-analysis
description: Build a cohort retention table in SQL, separate churn
from dormancy, compare cohorts without maturity bias, and pick the
single leak worth fixing.
version: 1.0.0
license: MIT
tags: [data, analytics, retention, sql, product]
---

# Cohort Retention Analysis

A single retention percentage hides everything that matters: whether
new users are better or worse than the ones before them, whether the
drop happens on day one or day thirty, and whether people left or
simply stopped. Teams act on the average and wonder why nothing moves.

The output is a cohort table you can defend: an activation event and a
retention event defined in words, weekly cohorts in SQL, a decay curve
per cohort, dormancy separated from churn, and one named leak with the
change that addresses it.

## When to use this skill

- Growth is up but the active user count is flat, and nobody can say which cohort is leaking.
- A dashboard shows "retention 38%" and you cannot tell what counts as retained.
- You are about to compare last month's cohort with this month's and draw a conclusion.
- Support says people come back after two weeks, and your churn definition says they left.

Do NOT use for: churn prediction modelling (that comes after the table
exists), or subscription revenue retention — that is a billing and MRR
job with its own definitions.

## Stage 1 — Define two events in words before writing SQL

Retention is undefined until both events are named, with the exact
condition that counts.

1.1 Activation: the first action that predicts a second visit — created a workspace, imported data, sent a first message. Not "signed up".

1.2 Retention: the action that means the product delivered value this week — the same action as activation, repeated, or a narrower one.

1.3 Write both as sentences with the table and filter: "activated = a row in `workspaces` with `created_at` within 24 hours of `users.created_at`".

| Definition | Wrong version | Right version | Why it matters |
|---|---|---|---|
| Activation | signed up | created a workspace | signup is a form, not a habit |
| Retention | logged in | sent at least 1 message | login can be an accidental email click |
| Churn | no login in 30 days | no core action in 30 days | dormant users are not gone |
| Reactivation | any return | return plus one core action | a return without value is a bounce |

Gate: both events are written as sentences a new analyst could
implement without asking you.

## Stage 2 — Build the cohort table in SQL

One query, weekly cohorts, weeks since activation as columns. Window
functions do the arithmetic.

2.1 Assign each user to the ISO week of their activation date, and never to signup week.

2.2 Join activity to the cohort and compute `weeks_since = floor(days_between(activity_week, cohort_week) / 7)`.

2.3 Pivot to a triangle where each row is a cohort and each column is weeks since activation.

```sql
WITH activated AS (
  SELECT u.id AS user_id,
         date_trunc('week', MIN(w.created_at))::date AS cohort_week
  FROM users u
  JOIN workspaces w ON w.owner_id = u.id
  GROUP BY u.id
),
activity AS (
  SELECT m.user_id, date_trunc('week', m.sent_at)::date AS active_week
  FROM messages m
  GROUP BY 1, 2
)
SELECT a.cohort_week,
       floor((extract(epoch FROM (act.active_week - a.cohort_week)) / 604800))::int AS week_n,
       count(DISTINCT a.user_id) AS active_users
FROM activated a
JOIN activity act ON act.user_id = a.user_id
WHERE act.active_week >= a.cohort_week
GROUP BY 1, 2
ORDER BY 1, 2;
```

Gate: the week-0 column equals the cohort size for every row, which
proves the join is right.

## Stage 3 — Choose the windows you will report

Reporting every week creates noise. Three windows carry the decisions.

3.1 Day 1 or week 1 for the first-session experience, day 7 or week 4 for the habit, and day 30 or week 12 for the durable core.

3.2 Pick windows that match the product's natural cycle: a weekly-use tool reports weeks, a monthly billing tool reports months, an event tool reports per event.

3.3 Report the same windows every time; a changed window is a changed metric and cannot be compared with history.

Gate: three windows are named, each tied to a decision someone will
make.

## Stage 4 — Separate dormancy from churn

Most "churn" in a product with a seasonal use case is dormancy, and
calling it churn sends you to fix the wrong thing.

4.1 Define dormant as no core action for 30 days but a return within 90, and churned as no core action for 90 days.

4.2 Measure reactivation as its own number: of users dormant at week 4, how many acted by week 12.

4.3 Report churn, dormancy and reactivation side by side, because a flat retention curve is often high dormancy plus high reactivation.

4.4 Compute reactivation with two cohort sets rather than a new definition:

```sql
WITH w4 AS (SELECT user_id FROM weekly_activity WHERE week_n = 4),
     later AS (SELECT DISTINCT user_id FROM weekly_activity
               WHERE week_n BETWEEN 5 AND 12)
SELECT count(*) AS dormant_at_w4,
       count(l.user_id) AS reactivated_by_w12
FROM w4 LEFT JOIN later l USING (user_id);
```

Gate: the three numbers exist per cohort and the reactivation count is
not folded into retention.

## Stage 5 — Compare cohorts only at equal maturity

A three-week-old cohort has no week-12 data. Comparing it to a mature
cohort is the most common error in retention analysis.

5.1 Compare week 4 across cohorts only for cohorts at least 4 weeks old, and never read an empty cell as zero.

5.2 When comparing a recent cohort, use the longest window all cohorts share, and state the window in the title.

5.3 Look for the shape change, not the level change: a cohort that starts higher and decays faster is a different problem from one that starts lower and holds.

| Comparison | Valid | Why |
|---|---|---|
| Week 4 of cohort A vs cohort B, both 4+ weeks old | yes | equal maturity |
| Week 12 of a 5-week-old cohort vs a 20-week-old one | no | missing cells are not churn |
| Day 1 across all cohorts | yes | every cohort has day 1 |
| Total active users month over month | weak | mixes cohort quality with volume |

Gate: every comparison states the window and only uses cohorts old
enough to have it.

## Stage 6 — Segment the leak, not the whole table

An average curve tells you the product is average. Segments tell you
where to work.

6.1 Split by acquisition channel, plan tier and city; three splits is enough to find a leak.

6.2 Compute week-4 retention per segment with the segment size beside it, and ignore segments under 100 users.

6.3 Rank segments by the gap from the best segment, not by absolute retention, because the gap is the addressable amount.

Gate: the worst meaningful segment is named with its size and its gap
in percentage points.

## Stage 7 — Find the step in the curve

Retention curves drop in steps, and each step has a cause on a
specific day.

7.1 Plot the daily curve for the first 14 days and find the largest single-day drop; that day is the leak.

7.2 Segment that day by action taken: users who completed the setup step versus those who did not.

7.3 Convert the finding into a comparison: "users who imported data in week 1 retain 3x at week 4" — a statement about a behaviour, not a cohort.

Gate: one drop-off day is named with a supporting behaviour comparison
and a segment size.

## Stage 8 — Run one change and re-measure the same window

Retention work fails when five changes ship at once. One change, one
window, one comparison.

8.1 Pick the change that addresses the leak — a shorter setup, a first-value email, a template — and ship it to a subset.

8.2 Re-measure the same window on the post-change cohort, at equal maturity, with the same definitions.

8.3 Treat a 2 to 5 percentage point move at week 4 as the realistic range for one change; anything larger usually means a definition changed.

Gate: before and after numbers exist for the same window, cohort age
and definition.

## Stage 9 — Publish the table and its definitions

A retention table without definitions is a chart people argue about in
meetings.

9.1 Publish the table with the two definitions, the three windows and the cohort cutoff date in the same view.

9.2 Note the sample size per cell and grey out cells under 50 users.

9.3 Keep a change log of definition changes beside the table, because a redefined activation resets history.

Gate: the view carries definitions, windows, cohort cutoff and cell
sizes, and a definition change is logged with a date.

## Worked example - finding the day-6 leak

A weekly-use B2B tool with 14,000 activated users over 12 weeks.

| Cohort | Week 0 | Week 1 | Week 4 | Week 8 | Week 12 |
|---|---|---|---|---|---|
| Weeks 1-4 | 4,120 | 58% | 31% | 24% | 21% |
| Weeks 5-8 | 4,680 | 57% | 30% | 23% | — |
| Weeks 9-12 | 5,200 | 61% | 38% | — | — |

The weeks 9-12 cohort looked better at week 4 (38% against 30%), and
it was, but only after the split by behaviour: users who imported data
in week 1 retained at 52% at week 4 against 19% for those who did not.
The change that shipped in week 9 was a sample-data import, and it
moved the number it was designed to move.

The leak was on day 6, not day 1. The daily curve held 71% through day
5 and dropped to 44% on day 6, which was the day the free trial's
guided checklist ended. Users who finished the checklist retained at
week 4 at 46%; those who did not, at 12%.

Dormancy mattered: of the users counted as churned at week 4, 34%
returned by week 12 with at least one core action. Calling that churn
would have sent the team to build win-back emails for people who were
simply between projects.

## Quality checklist

- [ ] Activation defined in one sentence with table and filter.
- [ ] Retention defined as a core action, not a login.
- [ ] Cohort assigned by activation week, not signup week.
- [ ] Week-0 column equals cohort size for every row.
- [ ] Three reporting windows, tied to decisions.
- [ ] Dormant, churned and reactivated reported separately.
- [ ] Comparisons use equal maturity only.
- [ ] Empty cells never read as zero.
- [ ] Segments under 100 users excluded from ranking.
- [ ] Largest single-day drop identified with a cause.
- [ ] One change shipped and re-measured on the same window.
- [ ] Before and after at equal maturity.
- [ ] Definitions, windows and cutoff published with the table.
- [ ] Cell sizes shown, small cells greyed out.
- [ ] Definition changes logged with a date.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Retention looks flat while active users grow | Growth in new cohorts masks decay in old ones | Read the cohort table by row, not the total |
| Week-4 number jumps after a change | The new cohort is younger than 4 weeks, so cells are partly empty | Compare only cohorts old enough for the window |
| Retention 38% but nobody agrees it is bad | No written definition of the retention event | Write both definitions and publish them with the table |
| Churn looks high in a seasonal product | Dormancy is counted as churn | Split dormant at 30 days from churned at 90 |
| Week-0 column larger than the cohort | The join multiplied rows on multiple workspaces | Count distinct users and deduplicate the activation CTE |
| Every change moves retention | Definition changed between measurements | Log definition changes and re-baseline history |

## Copy-ready agent prompt

> Read the skill at the URL above and build my cohort retention analysis. Write the activation and retention events as sentences, build the weekly cohort table in SQL with weeks since activation, verify the week-0 column equals cohort size, report day 1, week 4 and week 12 with equal-maturity comparisons, and split dormant from churned from reactivated. Then segment by channel, plan and city, name the largest single-day drop with a behaviour comparison, and propose one change with the re-measurement window. Stop and show me the SQL if any cell mixes cohorts of different ages.
