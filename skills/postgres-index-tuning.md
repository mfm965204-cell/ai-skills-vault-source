---
name: postgres-index-tuning
description: Turn a slow Postgres query into a fast one without locking writes - EXPLAIN with buffers, plan reading, composite and covering index design, partial indexes, concurrent builds, bloat checks and an unused-index audit.
version: 1.0.0
license: MIT
tags: [data, postgres, sql, performance, indexing, database]
---

# Postgres Index Tuning

A 4-second query is almost never a missing index. It is a sequential scan because the index exists on the wrong column order, or a sort that spills to disk because `work_mem` is 4 MB, or statistics so stale the planner thinks 40 rows match when 400,000 do.

This skill reads the plan before adding anything, then adds the smallest index that removes the work - and measures the buffers read, not just the wall clock.

## When to use this skill

- An endpoint got slow as the table grew past a few million rows.
- A dashboard query takes 8 seconds and someone suggested "add an index".
- The planner ignores an index you already built.
- Writes got slow and you suspect too many indexes.

Do NOT use for: hardware sizing, connection pooling problems (that is pgbouncer, not indexes), or a query that is slow because it returns 200,000 rows to the app - that is a product problem.

## Stage 1 - Capture the query and its parameters

1.1 Get the exact SQL, with the parameter values, from `pg_stat_statements` rather than from the application code. The code may have changed; the slow query is what ran.

1.2 Find the top offenders by total time, not by mean time:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT calls, round(total_exec_time) AS total_ms, round(mean_exec_time, 2) AS mean_ms,
       rows, round(100.0 * shared_blks_read / NULLIF(shared_blks_hit + shared_blks_read, 0), 1) AS miss_pct,
       left(query, 90) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

1.3 Note the parameters that make it slow. A query fast for one tenant and slow for another is a data-distribution problem, not a query problem.

1.4 Record the baseline: wall time, rows returned, and buffers read. Wall time alone is noisy; buffers read is the number that tells you whether the work changed.

1.5 Reset statistics after a change and let them accumulate for at least a day before judging.

| Metric | Where | Why it matters |
|---|---|---|
| Mean exec time | pg_stat_statements | the number users feel |
| Total exec time | pg_stat_statements | where the hours go |
| Shared blocks read | EXPLAIN BUFFERS | the real work done |
| Rows returned | EXPLAIN ANALYZE | whether the plan is honest |
| Calls | pg_stat_statements | frequency times cost |

Gate: the exact query, its parameters, and a baseline of time plus buffers.

## Stage 2 - Read the plan properly

2.1 Always `EXPLAIN (ANALYZE, BUFFERS)` with real parameters. `EXPLAIN` alone shows an estimate; `ANALYZE` shows what happened.

2.2 Read the plan bottom-up: the deepest node runs first, and its row count drives everything above it.

2.3 Look for four things in order: a sequential scan on a large table, a sort that spills, a nested loop with a high loop count, and an estimated-versus-actual row gap above 10x.

| Node | Healthy sign | Warning sign |
|---|---|---|
| Seq Scan | small table, under 10k rows | on a table with millions of rows |
| Index Scan | few rows, low buffers | high loop count in a nested loop |
| Sort | `Sort Method: quicksort, Memory: 512kB` | `external merge Disk: 40MB` |
| Hash Join | one hash, modest batches | `Batches: 32` means memory too small |
| Nested Loop | inner side 1-50 rows | inner side 50,000 rows, 10,000 loops |

2.4 Compare `rows=` (estimate) with `actual rows=`. A 100x gap means stale statistics or a correlated predicate, and no index fixes a bad estimate.

2.5 Check `Buffers: shared hit=... read=...`. A plan reading 400,000 buffers to return 20 rows is doing 20,000x more work than it needs.

Gate: a written list of the nodes doing the most work, with buffer counts.

## Stage 3 - Fix statistics before adding an index

3.1 Run `ANALYZE table_name;` first. It costs seconds and occasionally removes the problem entirely.

3.2 Increase the statistics target for skewed columns: `ALTER TABLE orders ALTER COLUMN status SET STATISTICS 500;` then `ANALYZE`.

3.3 For correlated columns (city and pincode, tenant and created_at), create extended statistics:

```sql
CREATE STATISTICS orders_tenant_created (dependencies, ndistinct)
  ON tenant_id, created_at FROM orders;
ANALYZE orders;
```

3.4 Check for a huge `n_dead_tup` in `pg_stat_user_tables`. Bloat makes the planner read more pages than the live data needs.

3.5 Only after statistics are fresh do you know whether an index is the answer.

Gate: `actual rows` within 3x of `rows=` on the main node.

## Stage 4 - Design the index

4.1 Equality columns first, then the range column, then the sort column. `(tenant_id, status, created_at)` serves `WHERE tenant_id=? AND status=? ORDER BY created_at DESC`.

4.2 Put the column used in the ORDER BY last, in the matching direction, so the sort disappears from the plan.

4.3 Add a covering `INCLUDE` for the two or three columns the query selects. It turns a heap fetch into an index-only scan:

```sql
CREATE INDEX CONCURRENTLY idx_orders_tenant_status_created
  ON orders (tenant_id, status, created_at DESC)
  INCLUDE (total, currency)
  WHERE deleted_at IS NULL;
```

4.4 Use a partial index when the query always filters one way: `WHERE deleted_at IS NULL` keeps the index small and hot.

4.5 Use an expression index for a computed predicate: `CREATE INDEX ON users (lower(email));` for case-insensitive lookups.

4.6 One index serves many queries; two overlapping indexes serve none well. Check `pg_indexes` for prefixes of your new index before creating it.

| Query shape | Index |
|---|---|
| `WHERE a=? AND b=? ORDER BY c DESC` | `(a, b, c DESC)` |
| `WHERE a=? AND c > now()-'7 days'` | `(a, c)` partial on the status filter |
| `WHERE lower(email)=?` | `(lower(email))` |
| `WHERE a=? ORDER BY c LIMIT 20` | `(a, c) INCLUDE (selected cols)` |
| `WHERE a=? AND b IN (...)` | `(a, b)` with the planner choosing a bitmap scan |

Gate: one index proposed, with the query it serves named.

## Stage 5 - Build it without locking writes

5.1 `CREATE INDEX CONCURRENTLY` on any table taking writes. The plain form blocks writes for the whole build.

5.2 Run it outside a transaction block; `CONCURRENTLY` fails inside one.

5.3 Expect two table scans and a wait on old snapshots. Set `lock_timeout = '5s'` so a stuck build fails instead of blocking.

5.4 Verify it is valid afterwards; a failed concurrent build leaves an invalid index that still costs write time:

```sql
SELECT c.relname FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

5.5 Drop any invalid index with `DROP INDEX CONCURRENTLY` before retrying.

5.6 Raise `maintenance_work_mem` to 256 MB-1 GB for the session and keep `max_parallel_maintenance_workers` at 1-2 during peak.

Gate: index valid, no write stall longer than 2 seconds during the build.

## Stage 6 - Verify the plan actually changed

6.1 Re-run `EXPLAIN (ANALYZE, BUFFERS)` with the same parameters. Same query, same data, different plan.

6.2 Compare buffers read, not just time. A drop from 400,000 to 900 buffers is the proof; a time drop on a warm cache is not.

6.3 Confirm the sort node is gone, and that the scan is `Index Scan` or `Index Only Scan` rather than a bitmap scan with a large recheck.

6.4 Measure at the 95th percentile of data size: a tenant with 10 rows proves nothing. Test with the biggest tenant you have.

6.5 Keep the before and after plans in the PR. The next person needs to know why the index exists.

| Check | Before | Target |
|---|---|---|
| Plan node | Seq Scan | Index Scan |
| Buffers read | record | 90% lower |
| Sort | external merge | none |
| Wall time | record | 10x faster or under 50 ms |
| Rows rechecked | n/a | under 10% of scanned |

Gate: before and after plans attached, buffers down 90%.

## Stage 7 - Watch the write cost

7.1 Every index is a write. Five indexes on a table taking 500 inserts a second is five extra B-tree updates per row.

7.2 Measure insert latency before and after on a table with real write volume. If p95 insert latency rose more than 10%, the index needs to earn its place.

7.3 Audit unused indexes monthly:

```sql
SELECT s.relname AS table, s.indexrelname AS index, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0 AND NOT i.indisunique AND s.relname NOT LIKE 'pg_%'
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

7.4 Drop indexes with zero scans after 30 days, unless they back a constraint or a quarterly report.

7.5 Beware duplicate indexes: `(a)` and `(a, b)` are different, but `(a, b)` and `(a, b)` from two migrations are not - check before you add.

Gate: index count and write latency recorded together.

## Stage 8 - Handle the query shapes that resist indexing

8.1 `LIKE '%term%'` cannot use a B-tree. Use a trigram index (`pg_trgm`) or a real search index.

8.2 `OR` across different columns often defeats a single index. Rewrite as a `UNION ALL` of two indexed queries.

8.3 `OFFSET 100000 LIMIT 20` reads and discards 100,000 rows. Use keyset pagination: `WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT 20`.

8.4 A function on the column kills the index: `WHERE date(created_at) = '2026-11-15'` needs a range predicate instead.

8.5 `COUNT(*)` on a filtered set is a scan by definition. Keep a counter table if the UI needs the number.

8.6 A join with no index on the foreign key is a nested loop with a seq scan per row. Index every foreign key.

Gate: each resistant shape has a written workaround or an accepted cost.

## Stage 9 - Tune the settings that show up in plans

9.1 `work_mem` is per sort or hash node, not per connection. A 4 MB default spills any sort over about 20,000 rows. Raise it to 16-32 MB for the reporting role, not globally.

9.2 `random_page_cost` at 4.0 is a spinning-disk default. On SSD, 1.1 tells the planner that random reads are cheap, and it starts choosing index scans it should have chosen already.

9.3 `effective_cache_size` should be about 60-75% of total RAM, so the planner knows what the OS will cache.

9.4 `shared_buffers` at 25% of RAM is the standard starting point; past 8-16 GB the returns flatten.

9.5 `autovacuum_vacuum_scale_factor` at 0.2 is too lazy for a 50M-row table. Set 0.01 per table for the big ones.

9.6 Set `jit = off` on OLTP workloads if plans show JIT compilation overhead on short queries; it helps analytical scans and hurts 2 ms point lookups.

9.7 Change one setting at a time and keep the plan that justified it in the PR. Two settings changed together cannot be attributed.

| Setting | Default | Common fix |
|---|---|---|
| work_mem | 4 MB | 16-32 MB per reporting role |
| random_page_cost | 4.0 | 1.1 on SSD |
| effective_cache_size | 4 GB | 60-75% of RAM |
| shared_buffers | 128 MB | 25% of RAM |
| autovacuum scale factor | 0.2 | 0.01 on large tables |

Gate: any setting change recorded with the plan that justified it.

## Stage 10 - Keep it fast

10.1 Add the query to a weekly check that logs the top 10 by total time, so a regression is visible before a user reports it.

10.2 Alert when any single query's mean time doubles week over week.

10.3 Re-`ANALYZE` after a bulk load or a backfill, before judging any plan.

10.4 Keep a `perf-queries.md` with each tuned query, its index, and the buffer counts before and after.

10.5 Re-check plans after a Postgres major upgrade; the planner changes and an index that was ignored may become the chosen path.

Gate: weekly report running, `perf-queries.md` current.

## Worked example

An orders list endpoint, 12M rows, 4.1 seconds.

| Step | Plan | Buffers | Time |
|---|---|---|---|
| Baseline | Seq Scan + external merge sort | 412,000 | 4.1 s |
| After ANALYZE | Seq Scan, better estimate | 412,000 | 3.9 s |
| Composite index (tenant, status, created_at DESC) | Index Scan + Sort | 31,000 | 420 ms |
| Add INCLUDE (total, currency) | Index Only Scan | 2,400 | 38 ms |
| Partial WHERE deleted_at IS NULL | Index Only Scan, smaller index | 900 | 21 ms |

The first index removed 92% of the buffers; the covering change removed 92% of what was left. The `ANALYZE` step changed nothing on its own, which is why it comes before the index and not instead of it.

## Quality checklist

- [ ] Query and parameters taken from pg_stat_statements
- [ ] Baseline recorded: time, rows, buffers
- [ ] `EXPLAIN (ANALYZE, BUFFERS)` with real parameters
- [ ] Estimate within 3x of actual rows
- [ ] `ANALYZE` run, and statistics target raised on skewed columns
- [ ] Extended statistics for correlated columns
- [ ] Index column order: equality, range, sort
- [ ] Covering INCLUDE for selected columns where it helps
- [ ] Partial index for the always-present filter
- [ ] Built with CONCURRENTLY, verified valid
- [ ] Buffers read down 90% or more
- [ ] Sort node gone from the plan
- [ ] Tested with the largest tenant, not a small one
- [ ] Insert latency unchanged within 10%
- [ ] Zero-scan indexes audited and dropped
- [ ] work_mem and random_page_cost reviewed
- [ ] Before and after plans kept in the PR

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Index exists, planner still seq scans | Estimate says most rows match, so a scan is cheaper | Fix statistics, or use a partial index matching the real filter |
| Query slower after adding an index | Planner switched to a nested loop with a bad estimate | `ANALYZE`, raise statistics target on the join column |
| Sort still spills to disk | `work_mem` 4 MB for a 200,000-row sort | Raise work_mem for the role running the report |
| Writes slowed 30% after tuning | Four indexes on a hot insert path | Drop unused indexes, keep one composite |
| Index build blocked writes for 6 minutes | `CREATE INDEX` without CONCURRENTLY | Rebuild with CONCURRENTLY outside a transaction |
| Index invalid after a failed build | Concurrent build cancelled midway | Drop CONCURRENTLY, rebuild, verify `indisvalid` |
| `LIKE '%x%'` never uses the index | B-tree cannot serve a leading wildcard | `pg_trgm` GIN index, or a search engine |
| Page 4,000 of results is slow | OFFSET reads and discards every row | Keyset pagination on `(created_at, id)` |
| Fast for one tenant, slow for another | Data skew, one tenant has 100x the rows | Test with the largest tenant, consider per-tenant statistics |

## Copy-ready agent prompt

> Read the skill at the URL above and tune a slow Postgres query for me. Ask me for the exact query with its parameters, the table sizes, the Postgres version and whether the table takes writes. Then ask me to paste `EXPLAIN (ANALYZE, BUFFERS)` output and read it back to me: which node does the most work, where the estimate is wrong, and how many buffers it reads to return how many rows. Then give me the statistics fixes first, and one index with the exact column order, INCLUDE list and WHERE clause, built CONCURRENTLY. Finish with the before and after buffer counts to expect, the write-cost check, and the unused-index query. Do not add an index before the statistics are fresh.
