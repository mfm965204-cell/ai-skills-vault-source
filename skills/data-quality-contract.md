---
name: data-quality-contract
description: Write executable data contracts - schema, nulls, ranges, uniqueness and freshness - and run them in CI so a broken pipeline fails before the dashboard does.
version: 1.0.0
license: MIT
tags: [data, quality, testing, pipelines, ci]
---

# Data Quality Contract

Every data team has the same incident: a dashboard reported revenue for six days with 40% of the orders missing, and nobody noticed because the pipeline exited 0. The pipeline was not broken by any definition it could check - it ran, it wrote rows, the job was green.

This skill writes the checks that make "green" mean something: a contract per table stating schema, null rules, ranges, uniqueness and freshness, executed on every run and in CI, with a failure that stops the pipeline instead of publishing bad numbers. It ends with a small set of checks that catch the failures you have actually had, plus an owner per check.

The design rule: a check nobody would act on is not a check. Every assertion has an owner and a stated action.

## When to use this skill

- A dashboard published wrong numbers and the pipeline reported success.
- A column changed type or name upstream and broke a downstream model silently.
- You cannot answer "how fresh is this table" without opening the warehouse.
- You are onboarding a new data source and want its assumptions written down.
- **Do NOT use for:** application-level unit tests, API contract testing, or full observability tooling - this covers table-level assertions and their CI wiring.

## Stage 1 - List the tables and who depends on them

A contract is only meaningful for a table someone consumes. Start from the consumers, not the schema.

1.1 List every table that feeds a dashboard, a report, a model or an external export.

1.2 For each, name the consumer and the decision it supports - "finance closes the month from this".

1.3 Rank by blast radius: how many people are wrong if this table is wrong for a day.

1.4 Record the upstream source and the load frequency for each table.

1.5 Identify the three tables where a silent failure would cost the most, and start there.

1.6 Skip tables nobody reads; a contract on an unused table is maintenance with no return.

| Table | Consumer | Frequency | Blast radius |
|---|---|---|---|
| fct_orders | Finance close, growth dashboard | Hourly | High |
| dim_customers | CRM sync, support tool | Daily | Medium |
| rpt_ads_spend | Marketing weekly | Daily | Low |
| stg_clicks | Nothing yet | Hourly | None |

Gate: every consumed table has a named consumer, a frequency and a blast-radius rank.

## Stage 2 - Write the schema part of the contract

The schema is the first assertion and the one that catches the most incidents: a renamed or retyped column breaks everything downstream.

2.1 Declare every column with its name, type and nullability.

2.2 Declare the primary key and the grain - one row per what - in one sentence.

2.3 Declare the accepted values for low-cardinality columns as an explicit set.

2.4 Declare the expected row count range per load, from the last 30 days of history.

2.5 Declare the freshness requirement: the maximum acceptable age of the newest row.

2.6 Version the contract file and keep it beside the pipeline code, not in a wiki.

```yaml
table: fct_orders
grain: one row per order_id
owner: data-platform
columns:
  order_id:    {type: string, nullable: false}
  customer_id: {type: string, nullable: false}
  order_date:  {type: date,   nullable: false}
  amount:      {type: decimal, nullable: false}
  status:      {type: string, nullable: false, enum: [paid, refunded, failed, pending]}
checks:
  unique: [order_id]
  row_count: {min: 800, max: 4000}
  freshness: {column: loaded_at, max_age_hours: 6}
```

Gate: a versioned contract file exists for each high-blast-radius table, with grain and owner named.

## Stage 3 - Turn each declaration into an executable check

A contract in prose is documentation. A contract in SQL is a check that runs. Convert every declaration into a query returning the number of violations.

3.1 Write one check per assertion, each returning a single number - the count of violating rows.

3.2 Pass a check only when the violation count is zero, and print the count when it is not.

3.3 Keep checks in one SQL file per table, named by table, so a failure points at one file.

3.4 Make every check cheap: a count over a partition, not a full table scan on 200 GB.

3.5 Run the checks on the newly loaded partition, not the whole history.

3.6 Keep a fixed check name per assertion so the failure history is comparable over months.

```sql
-- checks/fct_orders.sql : each query returns the violation count
SELECT count(*) AS null_order_id FROM fct_orders WHERE order_id IS NULL;

SELECT count(*) AS dup_order_id FROM (
  SELECT order_id FROM fct_orders GROUP BY order_id HAVING count(*) > 1
);

SELECT count(*) AS bad_status FROM fct_orders
WHERE status NOT IN ('paid','refunded','failed','pending');

SELECT count(*) AS negative_amount FROM fct_orders WHERE amount < 0;
```

Gate: every contract declaration has a corresponding query returning a violation count.

## Stage 4 - Set thresholds from history, not from opinion

A threshold invented at a whiteboard either fires constantly or never fires. Derive the range from the data you already have.

4.1 Compute the last 30 days of daily row counts and take the 5th and 95th percentile as the acceptable range.

4.2 Set the null-rate ceiling per column from its historical maximum plus a margin.

4.3 Set the freshness limit at twice the load frequency - hourly load, 2-hour limit.

4.4 For monetary columns, set a range from the observed 1st and 99th percentile, and treat anything outside as suspicious rather than wrong.

4.5 Write the threshold and its derivation beside each check.

4.6 Review the thresholds quarterly; a growing business changes the ranges and a stale threshold becomes noise.

| Check | Threshold | Derived from |
|---|---|---|
| Daily row count | 800-4,000 | 5th and 95th percentile, last 30 days |
| Null customer_id | 0 | Always required for the join |
| Null city | under 2% | Historical max 1.4% |
| Freshness | 6 hours | Twice the 3-hour load interval |
| Amount range | 1-250,000 | 1st and 99th percentile |

Gate: every threshold carries its derivation, and no threshold is a round number chosen by feel.

## Stage 5 - Fail the pipeline, not just the log

A check that writes a warning nobody reads is decoration. The pipeline must stop before publishing.

5.1 Run the checks after the load and before any downstream model or export.

5.2 Exit non-zero on a blocking check failure, so the orchestrator marks the task failed.

5.3 Distinguish blocking from warning checks: schema, keys and freshness block; range anomalies warn.

5.4 On a blocking failure, leave the previous good partition in place rather than writing a partial one.

5.5 Write the failure into a `dq_results` table with the check name, the count and the run id.

5.6 Send the failure to the owning team's channel with the check name and a sample of violating rows.

```bash
set -euo pipefail
duckdb "$DB" < sql/load_orders.sql
out=$(duckdb "$DB" -csv -noheader < checks/fct_orders.sql)
if echo "$out" | awk '$1 > 0 {exit 1}'; then
  echo "all checks passed"
else
  echo "data quality failure: $(echo "$out" | tr '\n' ' ')"
  exit 1
fi
```

Gate: a deliberately broken load fails the pipeline and no downstream model runs.

## Stage 6 - Add freshness and volume, the two silent killers

Schema checks pass happily while a table is three days stale or half empty. These two catch the incidents that schema checks miss.

6.1 Check `max(loaded_at)` against the current time and compare with the freshness limit.

6.2 Check the row count of the new partition against the 30-day range.

6.3 Check the count of distinct keys against yesterday; a 30% drop is a signal even inside the range.

6.4 Check that the newest partition is not empty - an empty load is the most common silent failure.

6.5 Check for a sudden null spike in any required column compared with the trailing 7-day average.

6.6 Run these first, because a stale or empty table makes every other check meaningless.

Gate: a stale partition and an empty partition both fail the pipeline with a named check.

## Stage 7 - Test the checks themselves

A check that always passes is indistinguishable from no check. Prove each one can fail.

7.1 For each blocking check, construct a small fixture that violates it and confirm the check fails.

7.2 Confirm each check passes on a clean fixture, so the query itself is not broken.

7.3 Add both fixtures to CI so a future edit to a check is tested.

7.4 Test the threshold boundary: a value exactly at the limit should pass, one beyond should fail.

7.5 Check the runtime of the full check suite; above 60 seconds, move it to the partition level.

7.6 Record the last time each check actually fired; a check that has never fired in a year may be dead.

Gate: every blocking check has a failing fixture and a passing fixture, both in CI.

## Stage 8 - Wire it into CI and the orchestrator

The contract has to run in two places: before merge, on a sample, and after every load, on the real partition.

8.1 In CI, run the checks against a small fixture or a sampled partition on every pull request that touches the pipeline.

8.2 In the orchestrator, run the full checks after every load and before any consumer task.

8.3 Make the check suite a single command so both environments run the same code.

8.4 Store results per run so a trend of failures is visible, not just the latest state.

8.5 Add a dashboard of check pass rate and the oldest failing check, reviewed weekly.

8.6 Alert on the second consecutive failure, not the first, to avoid noise from a transient load.

Gate: the same command runs in CI and after every load, and results are stored per run.

## Stage 9 - Assign an owner and review the contract

Every failing check needs a person. A check without an owner gets muted within a month.

9.1 Name one owner per table in the contract file.

9.2 Route failures to the owner's channel, not a general alerts channel.

9.3 Review the contract quarterly: add checks for incidents that happened, retire checks that never fire.

9.4 Write a postmortem for each blocking failure: what the check missed and what was added.

9.5 Keep a log of incidents that passed all checks, and turn each one into a new check.

9.6 Version the contract with the pipeline, so a rollback restores the checks too.

Gate: every table has a named owner, and every past incident has produced a check.

## Quality checklist

- [ ] Every consumed table has a named consumer and a blast-radius rank.
- [ ] Each high-blast-radius table has a versioned contract file.
- [ ] The grain is stated in one sentence per table.
- [ ] Every column declares a type and a nullability.
- [ ] Low-cardinality columns declare an explicit enum.
- [ ] Every declaration has a query returning a violation count.
- [ ] Thresholds are derived from 30 days of history.
- [ ] Freshness and row-count checks run before all others.
- [ ] Blocking and warning checks are distinguished.
- [ ] A blocking failure exits non-zero and stops downstream tasks.
- [ ] The previous good partition is preserved on failure.
- [ ] Results are written per run with the check name and count.
- [ ] Every blocking check has a failing fixture and a passing fixture in CI.
- [ ] The same command runs in CI and after every load.
- [ ] Every table has a named owner receiving its failures.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Dashboard wrong for days, pipeline green | Checks logged warnings instead of exiting non-zero | Make schema, key and freshness checks blocking |
| Alert fatigue, checks muted | Thresholds set by feel, so they fire constantly | Derive ranges from 30 days of history |
| Downstream model ran on a partial load | Checks ran after the model, not before | Order the checks between load and consumers |
| Empty partition published | No volume check, and an empty load passes schema checks | Add a non-empty and row-count-range check first |
| A check has never failed | The query is wrong and always returns zero | Add a failing fixture and test the check itself |
| Nobody fixes a failing check | No owner, alerts in a general channel | Name an owner per table and route failures to them |

## Copy-ready agent prompt

> Read the skill at the URL above and write data contracts for my pipeline. Ask me for the tables, their consumers and 30 days of daily row counts, then produce a versioned contract file per high-blast-radius table with grain, columns, enums, thresholds and freshness, and the SQL check for each declaration. Order the checks with freshness and volume first, wire them between load and consumers so a failure exits non-zero, and give me a failing and a passing fixture per blocking check for CI. Finish with the owner per table and the alert routing. Do not invent a threshold; derive each from the history I give you.
