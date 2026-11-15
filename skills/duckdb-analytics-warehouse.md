---
name: duckdb-analytics-warehouse
description: Query 10 GB of CSV and Parquet on one laptop with DuckDB - partitioned files, fast joins, and a small warehouse that costs nothing to run.
version: 1.0.0
license: MIT
tags: [data, duckdb, analytics, sql, parquet]
---

# DuckDB Analytics Warehouse

Most teams do not have a 10 TB warehouse problem. They have 12 GB of exports, three CSVs that do not join cleanly, and a BI licence that costs more than the data is worth. DuckDB answers that class of question on a laptop in seconds, with no cluster, no ingestion job and no cost per query.

This skill builds the small warehouse: raw files landed once, Parquet partitioned by date, a set of views that model the tables, and a query layer that runs in under a second over millions of rows. It also covers the point where DuckDB stops being the right tool, because a 12 GB file is fine and a 400 GB one is not.

The number that decides the design: bytes scanned. Parquet plus a partition filter cuts a 12 GB scan to 300 MB, and that is the whole difference between 8 seconds and 200 ms.

## When to use this skill

- You have 1-50 GB of CSV, Parquet or JSON exports and no warehouse.
- A query in a spreadsheet or a pandas notebook takes minutes and dies on memory.
- You want a repeatable analysis that a colleague can re-run without your laptop.
- You are prototyping before committing to a managed warehouse.
- **Do NOT use for:** multi-user concurrent serving, real-time ingestion, or datasets that genuinely need a distributed engine - this is a single-node tool and it should stay that way.

## Stage 1 - Size the data and the question before choosing the tool

DuckDB is the wrong tool above roughly 100-200 GB of working set on a normal laptop. Measure first, then commit.

1.1 List every source file with its size and format, and total the bytes.

1.2 Note the row count and the column count of the largest table.

1.3 Write the three questions the analysis must answer, in SQL terms - filters, joins, aggregates.

1.4 Check the machine: RAM, free disk, and whether the data fits in memory or will spill.

1.5 Decide the output: a table, a chart, a CSV for someone else, or a repeatable script.

1.6 If the total exceeds 200 GB or needs concurrent users, stop and choose a managed warehouse instead.

| Data size | Working set | DuckDB verdict |
|---|---|---|
| Under 5 GB | Fits in RAM | Ideal, single file |
| 5-50 GB | Spills to disk | Good, with Parquet and partitions |
| 50-200 GB | Needs care | Workable on 32 GB RAM with column pruning |
| Above 200 GB | Does not fit | Use a warehouse with distributed compute |

Gate: total bytes, largest table size and RAM are recorded, and the tool decision follows from them.

## Stage 2 - Land raw data once and never edit it

A warehouse without an immutable raw layer cannot be debugged. Land the source files exactly as received, with the date and a checksum.

2.1 Store raw files in `data/raw/<source>/<yyyy-mm-dd>/` and never overwrite them.

2.2 Record a manifest: filename, size, row count, checksum, and the date received.

2.3 Load with `read_csv_auto` on a sample first, and print the inferred schema before trusting it.

2.4 Fix column types explicitly on load - a phone number read as an integer loses its leading zero.

2.5 Keep a `_loaded_at` column on every table, so a later question about timing has an answer.

2.6 Re-run the load from raw rather than patching a table; the raw layer is the only source of truth.

```sql
CREATE OR REPLACE TABLE orders AS
SELECT
  order_id::VARCHAR      AS order_id,
  customer_id::VARCHAR   AS customer_id,
  order_date::DATE       AS order_date,
  amount::DECIMAL(12,2)  AS amount,
  status::VARCHAR        AS status,
  now()                  AS _loaded_at
FROM read_csv_auto('data/raw/orders/2026-10-01/orders.csv', header = true);
```

Gate: the raw files are unmodified with a checksum manifest, and every loaded column has an explicit type.

## Stage 3 - Convert to Parquet, partitioned by the filter you actually use

Parquet is columnar, compressed and typed; a filter on a partition column skips whole files. This step is where the speed comes from.

3.1 Export each table to Parquet with `COPY ... TO ... (FORMAT PARQUET, COMPRESSION ZSTD)`.

3.2 Partition by the column your queries filter on most - usually the month or the day.

3.3 Keep files between 100 MB and 1 GB; thousands of tiny files cost more in open calls than they save.

3.4 Sort by the most common filter column inside each partition, so row-group statistics prune better.

3.5 Compare sizes: expect CSV to Parquet at roughly 5-10x compression on typical business data.

3.6 Verify the row counts match the source after conversion, before deleting anything.

```sql
COPY (SELECT * FROM orders)
TO 'data/parquet/orders' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (order_month));
```

Gate: Parquet row counts equal the source row counts, and a query filtering one partition touches only that directory.

## Stage 4 - Model with views, not copies

Views keep one physical copy of the data and give the analysis a stable vocabulary. Copies drift and cost disk.

4.1 Create one view per business entity over the Parquet files, with typed columns and clear names.

4.2 Create a `dim_customers` view and a `fct_orders` view, and keep joins out of the base views.

4.3 Put derived logic - margin, tenure, bucket - in a second layer of views, so base views stay close to raw.

4.4 Name views with a prefix by layer: `stg_`, `dim_`, `fct_`, `rpt_`.

4.5 Document each view in one line in a `models.md`, because a view nobody understands is a liability.

4.6 Never create a view that reads a CSV directly in production queries; the Parquet layer is the stable one.

```sql
CREATE OR REPLACE VIEW fct_orders AS
SELECT order_id, customer_id, order_date, amount, status
FROM read_parquet('data/parquet/orders/**/*.parquet', hive_partitioning = true);

CREATE OR REPLACE VIEW rpt_monthly_revenue AS
SELECT date_trunc('month', order_date) AS month,
       sum(amount) AS revenue,
       count(DISTINCT customer_id) AS buyers
FROM fct_orders
WHERE status = 'paid'
GROUP BY 1
ORDER BY 1;
```

Gate: every analysis reads from a view, and no view reads a CSV.

## Stage 5 - Write the joins so they do not multiply rows

DuckDB will happily produce a row explosion, and a wrong join is the most common cause of a number that is 3x too large.

5.1 Check cardinality before every join: `SELECT count(*), count(DISTINCT key) FROM each side`.

5.2 Join on typed keys, and cast both sides explicitly rather than relying on implicit conversion.

5.3 Aggregate before joining when the join is one-to-many and the target is a summary.

5.4 Use `LEFT JOIN` deliberately and check the null count it produces.

5.5 Assert the row count after each join in the script; a join that changes the count unexpectedly is a bug.

5.6 Prefer `QUALIFY` for window-filtered deduplication instead of a self-join.

```sql
-- dedupe to one row per order before joining, then assert the count
CREATE TEMP TABLE orders_dedup AS
SELECT * FROM fct_orders
QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY _loaded_at DESC) = 1;

SELECT count(*) AS before_rows FROM fct_orders;
SELECT count(*) AS after_rows FROM orders_dedup;
```

Gate: no join changes the row count without an explained reason, and every key is cast explicitly.

## Stage 6 - Measure a query before optimising it

DuckDB is fast enough that most slow queries are a modelling problem, not a tuning problem. Read the plan and the scan size first.

6.1 Run `EXPLAIN ANALYZE` and read the bytes scanned per operator, not the wall time alone.

6.2 Confirm the partition filter is pushed down: a query on one month should scan one directory.

6.3 Confirm column pruning: selecting 3 of 40 columns should scan roughly 3/40 of the bytes.

6.4 Look for a materialisation or a repeated scan of the same file, and replace it with a temp table.

6.5 Set a memory limit and a temp directory explicitly for large sorts, so a query spills instead of dying.

6.6 Record before and after bytes scanned for the query you changed.

```sql
SET memory_limit = '8GB';
SET temp_directory = '/tmp/duckdb_spill';
EXPLAIN ANALYZE
SELECT date_trunc('month', order_date) AS month, sum(amount)
FROM read_parquet('data/parquet/orders/order_month=2026-10/*.parquet')
GROUP BY 1;
```

Gate: the slowest query's bytes scanned drops by at least 5x after partitioning and pruning.

## Stage 7 - Package it so someone else can re-run it

An analysis that lives in a notebook cell is not repeatable. Package it as one command with its inputs declared.

7.1 Put the load, the views and the reports in numbered SQL files: `01_load.sql`, `02_views.sql`, `03_reports.sql`.

7.2 Add a `run.sh` that executes them in order against a database file, and fails on the first error.

7.3 Pin the DuckDB version in a requirements file; query syntax and functions do change.

7.4 Keep the output of each report as a dated CSV in `out/<yyyy-mm-dd>/`.

7.5 Print the row counts and the loaded timestamps at the end of a run, so a silent partial load is visible.

7.6 Commit the SQL and the manifest, never the data, unless the data is small and shareable.

```bash
set -euo pipefail
DB=data/warehouse.duckdb
rm -f "$DB"
for f in sql/01_load.sql sql/02_views.sql sql/03_reports.sql; do
  echo "running $f"
  duckdb "$DB" < "$f"
done
duckdb "$DB" -c "SELECT count(*) FROM fct_orders;"
```

Gate: one command rebuilds the database from raw files and produces the same numbers as the last run.

## Stage 8 - Validate the numbers against a second source

A fast query that returns the wrong number is worse than a slow one. Tie the warehouse to a number someone already trusts.

8.1 Pick one month and reconcile total revenue against the finance system or the payment gateway.

8.2 Check the row count of the largest table against the source system's count.

8.3 Check that no status filter is silently excluding refunds or failed payments.

8.4 Check the null rate in each key column; a null key silently drops rows in an inner join.

8.5 Record the reconciliation in the repo: the two numbers, the difference and the explanation.

8.6 Add the reconciliation as a query in the report run, so a drift is caught the day it appears.

Gate: one month reconciles to an external source within an agreed tolerance, and the check runs with every report.

## Stage 9 - Know when to leave DuckDB

The tool is right until it is not. Recognise the signals before a team builds on it and hits a wall.

9.1 If more than two people need concurrent query access, move to a server-based warehouse.

9.2 If ingestion must be real-time or streaming, DuckDB is the wrong layer.

9.3 If the working set passes roughly 200 GB, the laptop stops being the machine.

9.4 If the data needs row-level security or audit trails per user, that is a server feature.

9.5 Keep the SQL portable - avoid exotic functions - so the migration is a rewrite of the connection, not of the logic.

9.6 Write the exit note: what would trigger a move, and what the migration would touch.

Gate: the exit conditions are written down, and the SQL stays within portable constructs.

## Quality checklist

- [ ] Total data size and machine RAM are recorded before the tool decision.
- [ ] Raw files are stored unmodified with a checksum manifest.
- [ ] Every loaded column has an explicit type.
- [ ] Parquet row counts equal the source row counts.
- [ ] Partitions follow the column most queries filter on.
- [ ] Parquet files sit between 100 MB and 1 GB each.
- [ ] All analysis reads from views, and no view reads a CSV.
- [ ] Join cardinality is checked before every join.
- [ ] No join changes the row count without an explained reason.
- [ ] `EXPLAIN ANALYZE` was read for the slowest query.
- [ ] The partition filter is pushed down in the plan.
- [ ] Bytes scanned dropped at least 5x after partitioning.
- [ ] One command rebuilds the database from raw files.
- [ ] One month reconciles to an external source within tolerance.
- [ ] Exit conditions for leaving DuckDB are written down.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Revenue is 3x too high | A one-to-many join fanned out the order rows | Aggregate before joining and assert the row count |
| Query scans all 12 GB for one month | Partition column missing from the filter path | Filter on the hive partition column and confirm in the plan |
| Phone numbers lost their leading zero | Type inferred as integer on CSV load | Cast to `VARCHAR` explicitly at load time |
| Query dies on a large sort | Memory limit unset, so it tried to keep everything | Set `memory_limit` and `temp_directory` to spill |
| Numbers differ from finance | Refunds excluded by a status filter nobody noticed | Reconcile one month and add the check to the report run |
| Someone edited a source CSV | Raw layer was treated as editable | Keep raw immutable and reload from it |

## Copy-ready agent prompt

> Read the skill at the URL above and build me a small DuckDB warehouse. Ask me for the file list with sizes, my machine's RAM and the three questions the analysis must answer, then decide whether DuckDB fits. Produce the load SQL with explicit types, the Parquet conversion with partitioning on my main filter column, the view layers, and the report queries with a row-count assertion per join. Finish with `EXPLAIN ANALYZE` on the slowest query showing bytes scanned, a one-command rebuild script, and a reconciliation query against one month of an external source. Tell me plainly if the data is too large for this tool.
