---
name: cron-monitoring
description: Keep scheduled jobs alive and honest - an inventory with owners and SLAs, idempotency with advisory locks, retries with backoff, heartbeat dead-man switches, duration and output checks, alert routing and a runbook per job.
version: 1.0.0
license: MIT
tags: [automation, cron, monitoring, reliability, systemd, ops]
---

# Cron Monitoring

A cron job fails silently. Nothing crashes, no page goes out, and the only signal is a customer asking three days later why the invoices stopped. The failure is never the schedule; it is that nobody was told.

This skill makes every job observable and re-runnable: an inventory with an owner, a lock so two runs cannot overlap, a heartbeat that alerts when a job does not run, and a runbook for the 3am version of you.

## When to use this skill

- You have more than 5 scheduled jobs and cannot list them all from memory.
- A job ran twice and sent 4,000 duplicate emails.
- A nightly job has been failing for a week and nobody noticed.
- Jobs run in three places: crontab, a container scheduler, and someone's laptop.

Do NOT use for: long-running services or event-driven workers (that is a queue and a supervisor), or workflows with complex dependencies - that is a real orchestrator, and pretending cron is one is how you get a 40-line shell script nobody can debug.

## Stage 1 - Inventory every job

1.1 List every scheduled job with nine fields: name, schedule, owner, what it writes, SLA, expected duration, timeout, retry policy, runbook link.

1.2 Find the ones you forgot: `crontab -l` on every host, `systemctl list-timers`, container scheduler config, and any `@reboot` entry.

1.3 Write the SLA as a consequence, not a duration: "invoices must be generated before 06:00 IST or the finance team cannot start".

1.4 Name one owner per job. A job with two owners has none.

| Field | Example | Why it matters |
|---|---|---|
| Name | `billing.generate_invoices` | greppable in logs |
| Schedule | `0 3 * * *` | in UTC, documented |
| Owner | finance-eng | who gets paged |
| Writes | invoices, invoice_items | blast radius |
| SLA | done by 06:00 IST | the real requirement |
| Duration | p50 40 s, p95 4 min | sets the timeout |
| Timeout | 15 min | kills a hung run |
| Retries | 3, backoff 5/25 min | transient failures |
| Runbook | link | 3am instructions |

1.5 Store the inventory in the repository, not in a wiki. It changes when the job changes, and a wiki does not.

| Where jobs hide | Command | What you find |
|---|---|---|
| User crontab | `crontab -l` | per-user entries |
| System crontab | `ls /etc/cron.*` | package-installed jobs |
| systemd timers | `systemctl list-timers --all` | newer jobs, often forgotten |
| Container scheduler | its own list command | jobs added by another team |
| App scheduler | the app's admin page | jobs inside the product |

Gate: every job in the inventory with an owner and an SLA, including the ones you found by accident.

## Stage 2 - Make every run idempotent

2.1 A job that runs twice must produce the same result as running once. This is the property that makes retries safe.

2.2 Use a natural key and an upsert instead of an insert: `INSERT ... ON CONFLICT (invoice_id) DO UPDATE`.

2.3 For a job that sends messages, record a send key per recipient per period and skip anything already sent.

2.4 For file outputs, write to a temp file and rename; a half-written file is worse than no file.

2.5 Test idempotency by running the job twice in staging and diffing the resulting rows. A non-zero diff means a retry can double-charge someone.

2.6 Make the job's period explicit in the data it writes (`period='2026-11-15'`), so a re-run updates the same rows instead of adding a second set.

Gate: running the job twice produces an identical end state, verified by diff.

## Stage 3 - Stop overlapping runs with a lock

3.1 Take a lock at the start and release it at the end. A job that takes longer than its interval will otherwise overlap with itself.

3.2 Use the database for the lock when the job writes to the database:

```sql
-- non-blocking: returns immediately if another run holds the lock
SELECT pg_try_advisory_lock(hashtext('billing.generate_invoices')) AS got;
-- ... do the work ...
SELECT pg_advisory_unlock(hashtext('billing.generate_invoices'));
```

3.3 For shell jobs use `flock -n /var/lock/job.lock` so a second invocation exits immediately instead of queueing.

3.4 Log a skipped run as a distinct outcome, not as success. A lock skip every night is a sign the job outgrew its schedule.

3.5 Release the lock in a trap or `finally`, so a crash does not leave it held forever.

3.6 Alert when a job skips the lock more than twice in a row. That is not contention, that is a schedule that no longer fits.

| Approach | Good for | Failure mode |
|---|---|---|
| `pg_try_advisory_lock` | DB jobs | session dies, lock released, fine |
| `flock -n` | shell and script jobs | stale lock file if not handled |
| Redis `SET NX PX` | distributed jobs | clock or eviction issues |
| Row flag with timestamp | audit-friendly jobs | forgotten release |

Gate: two simultaneous invocations result in one run and one logged skip.

## Stage 4 - Retry with backoff, then give up loudly

4.1 Retry only transient failures: timeouts, 429s, 503s, connection resets. A 400 or a validation error will fail identically three times.

4.2 Use 3 attempts with 5 and 25 minute waits, and jitter, so a dependency recovering does not get hit by every job at once.

4.3 After the final failure, alert and exit non-zero. A silent final failure is the same as no monitoring.

4.4 Make the retry state visible: attempt number in the log line, and a metric per attempt.

4.5 Do not retry a job whose partial work is unsafe. Fix idempotency first; retries on a non-idempotent job double the damage.

4.6 Record the attempt count in the run log, so a job that needs 3 attempts every night shows up as a trend rather than an incident.

| Error | Retry | Note |
|---|---|---|
| Timeout | yes, 3x | with backoff |
| 429 rate limited | yes | respect `Retry-After` |
| 503 unavailable | yes | dependency restart |
| 400 bad request | no | fix the input |
| Auth 401 | no | token expired, alert a human |
| Disk full | no | alert, do not spin |

Gate: a forced failure retries 3 times, alerts, and exits non-zero.

## Stage 5 - Heartbeat so silence becomes an alert

5.1 The critical alert is not "the job failed", it is "the job did not run". A cron entry deleted by a deploy fails silently forever.

5.2 Ping an external endpoint at the end of every successful run, with the job name and duration. The monitor alerts if no ping arrives within 1.5x the interval.

5.3 Use a hosted dead-man's-switch service or your own endpoint plus a scheduled check. Either way, the alert must come from outside the machine that runs the job.

5.4 Send a start ping as well as an end ping, so a hung job is distinguishable from a job that never started.

5.5 Set the grace period deliberately: a daily job gets 2 hours of grace, an hourly job 15 minutes.

```bash
#!/usr/bin/env bash
set -euo pipefail
JOB=billing.generate_invoices
curl -fsS -m 5 "https://hc.example.com/ping/$HC_UUID/start" >/dev/null || true
trap 'curl -fsS -m 5 "https://hc.example.com/ping/$HC_UUID/fail" >/dev/null || true' ERR
python -m billing.generate_invoices
curl -fsS -m 5 "https://hc.example.com/ping/$HC_UUID" >/dev/null || true
```

5.6 Never let the heartbeat call fail the job. Wrap it so a monitor outage does not become a production outage.

Gate: deleting the cron entry produces an alert within 1.5 intervals.

## Stage 6 - Watch duration and output, not just exit codes

6.1 A job that exits 0 after processing 0 rows has failed in every way that matters. Assert on output counts.

6.2 Record rows written, files produced, or messages sent, and compare against the trailing 7-day median. Alert outside plus or minus 50%.

6.3 Track duration and alert when p95 doubles. A job creeping from 4 minutes to 40 is a table growing without an index.

6.4 Write one structured log line per run: job, start, end, duration, rows, status, attempt. Parseable, not prose.

6.5 Keep the last 30 run records per job for trend comparison.

| Check | Threshold | Alert |
|---|---|---|
| Exit code | non-zero | immediate |
| Rows written | under 50% of 7-day median | warning |
| Duration | p95 above 2x baseline | warning |
| Heartbeat | missing 1.5x interval | page |
| Output file | missing or 0 bytes | page |

Gate: a zero-row run alerts even though it exits 0.

## Stage 7 - Handle timezones and catch-up

7.1 Write every cron schedule in UTC and document the IST equivalent in the inventory. A schedule written in local time breaks on the day the server's timezone changes.

7.2 India has no daylight saving, which makes IST schedules stable - but a job for a US-facing process will drift by an hour twice a year if it is written in local time.

7.3 Decide the catch-up policy: should a missed run execute on the next boot? For a daily invoice job, yes; for an hourly sync, skipping is usually correct.

7.4 On a missed run, backfill deliberately with a bounded loop, not by letting the scheduler fire 12 times at once.

7.5 For month-end jobs, verify the schedule on a 31-day month and a 28-day month before trusting it.

7.6 Log the effective timezone in the run record; "ran at 03:00" is meaningless without it.

7.7 Test the schedule arithmetic on the shortest month, in a staging environment, once a year.

| Job type | Catch-up | Why |
|---|---|---|
| Daily billing | run once on recovery | money depends on it |
| Hourly sync | skip missed hours | the next run supersedes |
| Weekly report | run if the day is missed | nobody notices a late report |
| Month-end close | manual trigger only | side effects are large |

Gate: schedules in UTC, catch-up policy written per job, month-end tested.

## Stage 8 - Put guardrails around the run

8.1 Set a hard timeout on every job. A hung job holds a lock and blocks the next run forever.

8.2 Cap memory and CPU where the platform allows it, so one runaway job cannot take the host down.

8.3 Rate-limit outbound calls inside the job; a loop over 5,000 API calls with no pacing is a self-inflicted outage.

8.4 Never run a job as root. Use a dedicated user with access to exactly what it needs.

8.5 Keep secrets in the environment or a secret manager, never in the crontab line where `ps` can read them.

8.6 Set `MAILTO` or the equivalent so a bare cron failure at least produces an email, even before full monitoring exists.

Gate: timeout, resource cap and non-root user set on every job.

## Stage 9 - Write a runbook per job

9.1 One page per job: what it does, when it runs, what it writes, how to run it by hand, how to check it worked, who to call.

9.2 Include the exact command to run it manually, and the exact query to verify the output.

9.3 Include the safe-stop procedure: how to disable the schedule without deleting it.

9.4 Include the three most likely failures and the first check for each.

9.5 Link the runbook from the alert. An alert without a link is a puzzle at 3am.

9.6 Keep the runbook in the same repository as the job, so the two are reviewed together and the link never rots.

Gate: every job has a runbook, and every alert links to one.

## Stage 10 - Review monthly

10.1 Review the inventory monthly: jobs that never run, jobs whose owner left, jobs with no SLA.

10.2 Delete jobs nobody claims. A dead job with an alert is a page nobody understands.

10.3 Re-check the trailing durations and adjust timeouts; a timeout set 3 years ago is either useless or dangerous.

10.4 Review alert noise: any job that pages more than twice a month is either broken or mis-thresholded.

10.5 Add new jobs to the inventory in the same PR that adds them. A job without an inventory row is invisible by design.

Gate: monthly review done, inventory current, no unowned jobs.

## Worked example

A 14-job billing pipeline, one host, before and after.

| Problem | Before | After |
|---|---|---|
| Overlapping runs | two invoice runs on the 1st | advisory lock, skip logged |
| Silent failure | 6 days of no invoices | heartbeat page in 2 hours |
| Duplicate emails | 4,000 sent twice | send key per recipient per day |
| Unknown duration | "it takes a while" | p50 40 s, p95 4 min, alert at 8 min |
| Zero-row success | exit 0 with 0 rows | rows check alerts below 50% of median |
| Ownership | nobody | one owner per job in the inventory |

The heartbeat was the change that mattered: it turned a class of failure that lasted days into one that lasts two hours.

## Quality checklist

- [ ] Inventory with owner, SLA, timeout and runbook per job
- [ ] Jobs found from every scheduler, not just one crontab
- [ ] Idempotent: two runs produce an identical end state
- [ ] Lock taken at start, released in a trap or finally
- [ ] Skipped runs logged as skipped, not success
- [ ] Retries only on transient errors, 3 attempts with backoff
- [ ] Final failure alerts and exits non-zero
- [ ] Start and end heartbeat pings sent
- [ ] Heartbeat alerts within 1.5 intervals
- [ ] Rows or output count checked against the 7-day median
- [ ] Duration tracked, alert at 2x p95
- [ ] Schedules in UTC with IST documented
- [ ] Catch-up policy decided per job
- [ ] Hard timeout and resource caps set
- [ ] Job runs as a non-root user, secrets not in the crontab
- [ ] Runbook per job, linked from the alert
- [ ] Monthly review of the inventory and alert noise

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Invoices missing for a week | Cron entry removed by a deploy, no heartbeat | External dead-man switch with a grace period |
| 4,000 duplicate emails | Job ran twice, sends not keyed | Send key per recipient per period, upsert |
| Two runs overlapping at midnight | Job duration exceeded the interval | Advisory lock plus a skip log |
| Job exits 0 and does nothing | Empty input treated as success | Assert on row count against the median |
| Alert storm every night | Threshold set from a single bad run | Baseline from the trailing 7-day median |
| Job hangs until the next day | No timeout | `statement_timeout` and a hard job timeout |
| Runs at the wrong hour after a server change | Schedule in local time | Write the schedule in UTC |
| Nobody knows what to do at 3am | No runbook | One page per job, linked from the alert |
| Month-end job ran twice in a 31-day month | Schedule written for a 30-day month | Test on 28 and 31 day months |
| Job skipped every night | Lock held by a crashed previous run | Release in a trap, and alert on repeated skips |
| Nobody can find the job that broke | Jobs outside the inventory | Inventory from every scheduler, updated in the same PR |

## Copy-ready agent prompt

> Read the skill at the URL above and audit my scheduled jobs. Ask me: where the jobs run, how many there are, which one failing would hurt most, and whether I have any monitoring. Then build the inventory table with owner, SLA, duration, timeout and runbook for every job, and tell me which jobs are not idempotent and what would break on a retry. Then give me the advisory lock or flock pattern, the retry policy with backoff, the heartbeat script with start and end pings and a grace period, the output-count check, and the guardrails for timeout and user. Finish with the runbook template and the monthly review checklist. Do not assume a job is fine because it exits 0.
