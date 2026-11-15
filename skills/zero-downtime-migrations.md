---
name: zero-downtime-migrations
description: Change a Postgres schema on a live database without locking writes or dropping requests - lock analysis, expand and contract, concurrent index builds, batched backfills, NOT VALID constraints and a deploy order per app version.
version: 1.0.0
license: MIT
tags: [engineering, postgres, migrations, database, deployment, reliability]
---

# Zero-Downtime Migrations

The dangerous part of a migration is not the SQL, it is the lock. `ALTER TABLE ... ADD COLUMN x int NOT NULL DEFAULT 0` is instant on an empty table and a five-minute outage on a table with 40 million rows if the version or the default is wrong.

This skill gives you a lock table for every operation you are likely to run, the expand-contract pattern that makes app and schema changes independent, and a batched backfill with a monitor so you can stop mid-flight.

## When to use this skill

- A table you are altering is written to by production traffic, and a lock means dropped requests.
- You need to rename, retype or split a column without a maintenance window.
- A backfill over millions of rows must not block writes or bloat the table.
- You are adding an index to a table that takes inserts all day.

Do NOT use for: first-schema setup on an empty database (just run the migration), or data-loss operations that need a backup window regardless - dropping a column with live data is a decision, not a deploy step.

## Stage 1 - Classify every operation by its lock

1.1 Write the migration as a list of statements, then look up each one in the lock table before running anything. One `ALTER` per statement is easier to reason about than a combined one.

| Operation | Lock | Blocks writes | Rewrites table |
|---|---|---|---|
| ADD COLUMN, nullable, no default | ACCESS EXCLUSIVE, instant | briefly | no |
| ADD COLUMN with constant default (PG 11+) | ACCESS EXCLUSIVE, instant | briefly | no |
| ADD COLUMN with volatile default | ACCESS EXCLUSIVE | yes, whole time | yes |
| ALTER COLUMN TYPE int to bigint | ACCESS EXCLUSIVE | yes | yes |
| ALTER COLUMN TYPE varchar(50) to varchar(100) | ACCESS EXCLUSIVE | briefly | no |
| SET NOT NULL | ACCESS EXCLUSIVE | yes | full scan |
| ADD CONSTRAINT CHECK | ACCESS EXCLUSIVE | yes | full scan |
| CREATE INDEX | SHARE | no (blocks writes for DDL only) | no |
| CREATE INDEX CONCURRENTLY | SHARE UPDATE EXCLUSIVE | no | no |
| DROP COLUMN | ACCESS EXCLUSIVE, instant | briefly | no |
| VACUUM FULL | ACCESS EXCLUSIVE | yes | yes |

1.2 Set `lock_timeout` and `statement_timeout` on the migration session so a blocked DDL fails fast instead of queueing every query behind it:

```sql
SET lock_timeout = '3s';
SET statement_timeout = '30s';
```

1.3 Know the queue effect: one `ALTER TABLE` waiting for a lock blocks every query that arrives after it. A 30-second wait is a 30-second outage even if the ALTER itself is instant.

1.4 Check the table's size and write rate before deciding the approach: `SELECT pg_size_pretty(pg_total_relation_size('orders')), n_tup_ins FROM pg_stat_user_tables WHERE relname='orders';`

Gate: every statement mapped to a row in the lock table, with a decision written next to it.

## Stage 2 - Use expand and contract, always

2.1 Split every risky change into three deploys: expand (add the new shape), migrate (move the data, dual-write), contract (remove the old shape).

2.2 Expand adds the new column or table without touching the old one. Old code keeps working because nothing it reads has changed.

2.3 Migrate writes to both shapes from the app, backfills history, then reads from the new shape once it is verified.

2.4 Contract removes the old column in a separate deploy, at least one release after the last reader is gone.

| Change | Expand | Migrate | Contract |
|---|---|---|---|
| Rename column | add `new_col` | dual-write, backfill | drop `old_col` |
| Change type | add typed column | dual-write, convert | drop old |
| Split table | add new table | write both, backfill | drop old table |
| Add NOT NULL | add nullable | backfill, then constraint | - |
| New index | build concurrently | - | - |

2.5 Keep a feature flag for "read from new shape". It is the rollback: flip the flag, not the database.

Gate: a three-deploy plan written down before the first statement runs.

## Stage 3 - Add columns and constraints safely

3.1 Add columns nullable, with no default. Nullable is instant on every supported version and costs nothing.

3.2 On Postgres 11 and later a constant default is stored in the catalog and does not rewrite the table. A volatile default (`now()`, `gen_random_uuid()`) does rewrite it - add the column without the default, set the default, then backfill.

3.3 Add constraints in two steps so the validation does not hold a long lock:

```sql
-- step 1: instant, no scan, new rows are checked
ALTER TABLE orders ADD CONSTRAINT orders_total_pos CHECK (total >= 0) NOT VALID;
-- step 2: separate transaction, SHARE UPDATE EXCLUSIVE, does not block writes
ALTER TABLE orders VALIDATE CONSTRAINT orders_total_pos;
```

3.4 `SET NOT NULL` scans the table under ACCESS EXCLUSIVE. Use the workaround: add a `NOT VALID` check constraint `col IS NOT NULL`, validate it, then `SET NOT NULL` - the scan is skipped because the constraint proves it.

3.5 Never combine several ALTERs in one statement on a hot table; each one queues for the same exclusive lock and they serialise badly under load.

3.6 Defaults on a new column: set the default in a separate statement after the add, so a volatile default never rewrites the table under a lock you did not plan for.

3.7 Foreign keys need the same two-step treatment: `ADD CONSTRAINT ... NOT VALID` then `VALIDATE`, or the reference check scans both tables under an exclusive lock.

Gate: no statement on a hot table takes ACCESS EXCLUSIVE for more than a second.

## Stage 4 - Build indexes without blocking writes

4.1 Always `CREATE INDEX CONCURRENTLY` on a table that takes writes. The plain version blocks writes for the whole build.

4.2 Run it outside a transaction - `CONCURRENTLY` fails inside one. In most migration tools that means marking the migration non-transactional.

4.3 Expect two scans of the table plus waiting on old snapshots. A 10 GB table might take 5-20 minutes (estimate; depends on I/O).

4.4 Watch for an invalid index. A failed concurrent build leaves an `INVALID` index that is ignored by the planner but still maintained on writes:

```sql
SELECT c.relname, i.indisvalid FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid
WHERE NOT i.indisvalid;
-- fix: DROP INDEX CONCURRENTLY <name>; then rebuild
```

4.5 Set `maintenance_work_mem` to 256MB-1GB for the session, and lower `max_parallel_maintenance_workers` to 1 during peak hours if the build is starving the app.

4.6 Drop unused indexes before adding new ones. Every index costs write throughput; check `pg_stat_user_indexes.idx_scan` and drop anything with 0 scans and a non-unique definition after 30 days.

4.7 On a very large table, build the index during the quietest window even with CONCURRENTLY. The build still competes for I/O, and a 40-minute build during peak traffic is a latency incident with no lock to blame.

Gate: zero invalid indexes after the migration, and index count not increased without a dropped index to match.

## Stage 5 - Backfill in batches, with a stop button

5.1 Never backfill with one `UPDATE` over millions of rows. It holds row locks, bloats the table, and can fill the WAL.

5.2 Batch by primary key with keyset pagination, 1,000-5,000 rows per batch, and a short sleep between batches:

```sql
WITH batch AS (
  SELECT id FROM orders
  WHERE new_total IS NULL
  ORDER BY id
  LIMIT 2000
  FOR UPDATE SKIP LOCKED
)
UPDATE orders o SET new_total = o.total
FROM batch WHERE o.id = batch.id;
```

5.3 Sleep 50-200 ms between batches so autovacuum and replication keep up. A backfill that saturates the replica lag is an incident even though the primary is fine.

5.4 Track progress with a count of remaining rows, not a percentage you computed by hand: `SELECT count(*) FROM orders WHERE new_total IS NULL;`

5.5 Make the batch idempotent - `WHERE new_total IS NULL` means re-running is safe and a crash mid-way costs nothing.

5.6 Run it from a job, not from your laptop, with a timeout and a kill switch, and log batch number, rows updated and elapsed time.

| Table size | Batch size | Sleep | Approx duration |
|---|---|---|---|
| 100k rows | 2,000 | 50 ms | 2-4 min |
| 1M rows | 2,000 | 100 ms | 25-45 min |
| 10M rows | 5,000 | 100 ms | 2-4 h |
| 100M rows | 5,000 | 200 ms | 1-2 days |

5.7 Backfill a second, independent column in the same pass when you are already scanning the table; two backfills in one month is two rounds of bloat and two replica lag windows.

5.8 Keep a kill switch: a row in a `migration_control` table the batch job reads each loop, so you can stop it without killing the process and losing the progress log.

Gate: replica lag stays under 10 seconds throughout the backfill.

## Stage 6 - Sequence the deploy against app versions

6.1 Deploy the expand migration first, then the app that writes both shapes, then the backfill, then the app that reads the new shape, then the contract migration.

6.2 Never deploy code that reads a column in the same release that creates it. Rolling deploys mean old pods run for minutes after the new schema exists.

6.3 Make every migration backward compatible for at least one release. A migration that drops a column an old pod still selects crashes that pod on restart.

6.4 Check for long-running queries before the contract step - an analytics query holding a snapshot can keep the old column alive and block the drop:

```sql
SELECT pid, now()-query_start AS age, left(query,60)
FROM pg_stat_activity
WHERE state <> 'idle' AND now()-query_start > interval '5 minutes';
```

6.5 Cancel analytics queries during the DDL window, or run the contract at the quietest hour for your traffic (for Indian B2B traffic that is usually 02:00-05:00 IST).

6.6 Pin the migration to the same transaction boundary as the deploy. A migration that runs after the app pods start is a race you will lose once and then spend a night on.

Gate: a written five-step deploy order, with the rollback step named at each point.

## Stage 7 - Monitor locks and have a rollback

7.1 Open a second session before the migration and watch for blocked queries:

```sql
SELECT a.pid, a.wait_event_type, a.wait_event, now()-a.query_start AS wait,
       left(a.query,50) AS blocked, left(b.query,50) AS blocker
FROM pg_stat_activity a
JOIN pg_locks l ON l.pid=a.pid AND NOT l.granted
LEFT JOIN pg_locks bl ON bl.locktype=l.locktype AND bl.granted
  AND bl.relation IS NOT DISTINCT FROM l.relation AND bl.pid<>a.pid
LEFT JOIN pg_stat_activity b ON b.pid=bl.pid;
```

7.2 Alert if any query waits more than 2 seconds on a lock. That is the earliest signal of a migration going wrong.

7.3 Write the rollback before you run the forward migration: which statements undo it, in what order, and what data is lost if any.

7.4 Roll back the code first, then the schema. A schema rollback under a running new app version is a second incident.

7.5 Set `idle_in_transaction_session_timeout` to 60 seconds on the database. One forgotten open transaction holds a lock and blocks your DDL for hours.

7.6 Announce the window in the team channel with the exact start time in IST and the expected duration, even for a migration you believe is instant.

Gate: rollback script tested on a staging copy, and a lock alert live.

## Stage 8 - Test on a production-sized copy

8.1 Restore a recent backup into staging at production size. A migration tested on 10,000 rows tells you nothing about lock duration.

8.2 Run the full sequence under a write load - `pgbench` at 20 clients for 10 minutes is enough to expose lock queueing.

8.3 Measure three things: total wall time, longest lock wait, and peak replica lag.

8.4 Record the numbers in the migration PR. The next person altering this table will thank you, and the reviewer can judge risk from data.

| Test | Pass condition |
|---|---|
| Wall time | under the maintenance budget you set |
| Longest lock wait | under 2 seconds |
| Replica lag | under 10 seconds |
| App error rate during test | no increase |

8.5 Compare the plan before and after on the staging copy (`EXPLAIN (ANALYZE, BUFFERS)`), not just the timing - a migration that changes the query plan for the hottest endpoint is a performance incident waiting for load.

8.6 Run the rollback on the staging copy too, and time it. An untested rollback is a plan, not a capability.

Gate: all four numbers recorded in the PR.

## Stage 9 - Handle the special cases

9.1 Dropping a column does not reclaim disk; the space is reused over time. Plan a `pg_repack` or a maintenance window for the real reclaim, not `VACUUM FULL` on a hot table.

9.2 Renaming a table or column breaks every query by name. Prefer expand-contract even when a rename looks trivial.

9.3 Changing a primary key type from int to bigint on a large table is a rewrite plus a lock: use the expand pattern with a new column and a new unique index.

9.4 Partitioned tables: attach and detach partitions instead of deleting rows. `DETACH PARTITION CONCURRENTLY` exists on recent versions and avoids the lock.

9.5 Logical replication target: DDL does not replicate. Run the schema change on both sides in the right order, or pause the subscription.

9.6 MySQL or SQLite in the same stack: the lock semantics differ entirely, so redo the classification for those engines rather than copying this table.

Gate: a written note for whichever special case applies, or "none apply".

## Stage 10 - Clean up and record

10.1 After the contract deploy, delete the feature flag and the dual-write code in the next release - leftover dual-write paths become bugs.

10.2 Record the migration in `migrations.md`: date, table, operation, lock, duration, outcome. Six months later this file answers "why is this column nullable".

10.3 Re-check statistics after a big backfill: `ANALYZE orders;` so the planner is not working from pre-backfill estimates.

10.4 Review index bloat monthly and drop what nothing scans.

10.5 Add the new column to whatever data dictionary or ORM model you maintain in the same PR as the contract step; a column nobody documents is dropped by the next person to tidy the schema.

10.6 Keep the migration files immutable once applied. Editing an applied migration means environments diverge silently.

Gate: `migrations.md` updated, statistics refreshed, flag removed.

## Worked example

Splitting `orders.customer_name` into `customer_id` plus a join, on a 12M-row table with 300 writes a second.

| Step | Deploy | Statement | Lock | Duration |
|---|---|---|---|---|
| 1 | expand | ADD COLUMN customer_id bigint NULL | instant | under 1 s |
| 2 | expand | CREATE INDEX CONCURRENTLY on customer_id | none on writes | 6 min |
| 3 | app | dual-write both columns | - | - |
| 4 | job | backfill in 2,000-row batches, 100 ms sleep | row locks only | 38 min |
| 5 | app | read from customer_id, keep writing both | - | - |
| 6 | contract | DROP COLUMN customer_name | instant | under 1 s |

Replica lag peaked at 4 seconds during the backfill. No request waited more than 300 ms on a lock. Total downtime: zero.

## Quality checklist

- [ ] Every statement classified in the lock table
- [ ] `lock_timeout` set to 3s on the migration session
- [ ] Expand-contract plan written before the first statement
- [ ] New columns added nullable, defaults applied separately
- [ ] Constraints added NOT VALID then validated
- [ ] Indexes built CONCURRENTLY outside a transaction
- [ ] No invalid indexes left after the build
- [ ] Backfill batched, idempotent and resumable
- [ ] Replica lag monitored during the backfill
- [ ] Deploy order written with the rollback at each step
- [ ] No release reads a column it also creates
- [ ] Tested on a production-sized copy under load
- [ ] Longest lock wait under 2 seconds in the test
- [ ] Lock-wait alert live at 2 seconds
- [ ] Statistics refreshed after a large backfill
- [ ] `migrations.md` updated with duration and outcome
- [ ] Dual-write code removed one release after contract
- [ ] `idle_in_transaction_session_timeout` set to 60 s, rollback timed on the staging copy

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Site stalls for 40 s during deploy | ALTER queued behind a long-running SELECT holding a snapshot | Set `lock_timeout`, and kill or reschedule analytics queries |
| Table doubled in size after a backfill | Single UPDATE rewrote every row and dead tuples were never reclaimed | Batched backfill plus autovacuum tuning, then `pg_repack` |
| Planner ignores the new index | Index left INVALID by a failed concurrent build | Drop it CONCURRENTLY and rebuild |
| Replica 5 minutes behind | Backfill with no sleep, one transaction per 100k rows | 2,000-row batches with a 100 ms sleep |
| New pods crash after deploy | Migration dropped a column the old version still selects | Contract in a separate release, after the last reader is gone |
| `SET NOT NULL` locks for 3 minutes | Full table scan under ACCESS EXCLUSIVE | Add a NOT VALID check, validate, then SET NOT NULL |
| Migration succeeded but writes are slow | Four new indexes on a write-heavy table | Drop unused indexes and re-check `idx_scan` |
| CONCURRENTLY failed with "cannot run inside a transaction block" | Migration tool wraps every file in a transaction | Mark that migration non-transactional |
| DDL blocked for hours by an idle session | A forgotten `BEGIN` holds the lock | Set `idle_in_transaction_session_timeout` to 60 s |
| Foreign key add locked both tables | Plain `ADD CONSTRAINT` validates under exclusive locks | `NOT VALID`, then `VALIDATE CONSTRAINT` |

## Copy-ready agent prompt

> Read the skill at the URL above and plan a zero-downtime migration for my Postgres database. Ask me: the exact change I want, the table size, the write rate, the Postgres version and my deploy process. Then give me a lock classification for every statement, an expand-contract plan with the deploy order, and the SQL with `lock_timeout` set. For any backfill, give me the batched keyset query, the batch size and sleep, and the progress query. Then give me the lock-monitoring query, the rollback script and the production-sized test plan with pass conditions. Tell me plainly which step is the risky one and why.
