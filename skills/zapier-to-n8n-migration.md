---
name: zapier-to-n8n-migration
description: Move automations off a per-task billing tool onto a self-hosted workflow runner, one workflow at a time, with a parity test and a rollback path.
version: 1.0.0
license: MIT
tags: [automation, n8n, zapier, migration, self-hosted]
---

# Zapier To n8n Migration

A 40-workflow Zapier account costs a fixed monthly bill that grows with every task, and the bill is largest exactly when the automations are busiest. Self-hosting a runner removes the per-task cost but replaces it with a migration that can quietly break 20 business processes.

This skill migrates one workflow at a time: inventory and rank, rebuild, run both in parallel for a week, compare outputs, then cut over with a documented rollback. You end with a task-count reduction you can put a number on, and no workflow migrated without a parity check.

## When to use this skill

- Your automation bill crossed a number that is hard to justify per month.
- You have 15+ Zaps and no list of what they do.
- A Zap with a 5-step chain is hitting task limits or timing out.
- You want code-level control - loops, retries, custom functions - that the current tool does not give.

Do NOT use for: choosing between tools on features alone, or migrating CRM data. It also does not cover hosting hardening beyond the minimum needed to run workflows safely.

## Stage 1 - Inventory and price every workflow

1.1 Export the workflow list with trigger, actions, run count in the last 30 days, and tasks consumed.

1.2 Compute tasks per run: a 5-action Zap costs 5 tasks per trigger event. The expensive ones are not the frequent ones, they are the long ones.

1.3 Rank by monthly task cost, not by importance. Migrating the top 10 usually removes 70-80% of the bill.

1.4 Mark each workflow: keep, rebuild, retire. Retiring a workflow that runs twice a year is the cheapest migration there is.

| Workflow | Runs/month | Actions | Tasks/month | Decision |
|---|---|---|---|---|
| lead to CRM + sheet + slack | 1,200 | 4 | 4,800 | rebuild |
| invoice PDF to email | 300 | 3 | 900 | rebuild |
| weekly report | 4 | 6 | 24 | keep |
| birthday message | 60 | 2 | 120 | rebuild |

Gate: every workflow has runs, actions, tasks per month and a keep/rebuild/retire decision.

## Stage 2 - Stand up the runner before migrating anything

2.1 One small instance: 2 vCPU and 4 GB RAM handles a few thousand executions a day comfortably.

2.2 Postgres for the workflow database, not the default SQLite, if you plan more than one worker or want reliable backups.

2.3 Set `N8N_ENCRYPTION_KEY` and back it up separately. Losing it makes every stored credential unreadable.

2.4 Put it behind HTTPS with a real certificate, and set `N8N_HOST` and `WEBHOOK_URL` to the public hostname or webhooks will be generated with the wrong base.

2.5 Pin the image tag (`n8nio/n8n:1.x.y`), never `latest`. An unattended major upgrade has broken more instances than any workflow bug.

```yaml
services:
  n8n:
    image: n8nio/n8n:1.68.0
    restart: unless-stopped
    ports: ["127.0.0.1:5678:5678"]
    environment:
      - N8N_HOST=n8n.internal.example.org
      - WEBHOOK_URL=https://n8n.internal.example.org/
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=db
      - DB_POSTGRESDB_DATABASE=n8n
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=336
    volumes: ["./data:/home/node/.n8n"]
```

Gate: the instance is reachable over HTTPS, a test webhook fires, and the encryption key is stored outside the server.

## Stage 3 - Rebuild the simplest workflow first, end to end

3.1 Pick a 2-step workflow with low volume. The goal of the first migration is to prove the pattern, not to save money.

3.2 Map each Zapier step to a node: trigger, HTTP request, transform, branch, error path.

3.3 Recreate credentials in the new tool rather than copying tokens where the provider allows OAuth. Copied tokens expire without warning.

3.4 Add an error branch to every workflow from the start. Zapier hides failures in a task history; a self-hosted runner will happily retry forever.

3.5 Run it manually 10 times with real payloads and inspect each execution's input and output.

| Zapier step | n8n node | Note |
|---|---|---|
| trigger (form, webhook) | Webhook / Form Trigger | keep the same payload shape |
| filter | IF / Switch | explicit branches |
| formatter | Set / Code | code for anything non-trivial |
| lookup row | Postgres / Sheets | parameterised, never concatenated |
| delay | Wait | check the plan's queue behaviour |

Gate: the first workflow runs 10 real payloads with identical output to the original.

## Stage 4 - Run both in parallel before cutting over

4.1 For 5-7 days, send the same trigger to both systems. Keep the old one as the source of truth and mark the new one as shadow.

4.2 Compare outputs per run: rows written, messages sent, records updated. A 99% match on 500 runs is 5 wrong records.

4.3 Log a comparison row per execution: timestamp, trigger id, old output hash, new output hash.

4.4 Only then disable the old workflow, and keep it disabled rather than deleted for 30 days.

```sql
-- parity check for a week of parallel running
SELECT date_trunc('day', created_at) AS day,
       count(*) AS runs,
       count(*) FILTER (WHERE old_hash <> new_hash) AS mismatches
FROM parity_log
WHERE created_at > now() - interval '7 days'
GROUP BY 1 ORDER BY 1;
```

Gate: 7 days of parallel runs, zero unexplained mismatches, and a written note for each explained one.

## Stage 5 - Handle the three features that do not port directly

5.1 Paths and filters become IF and Switch nodes. Draw the branch explicitly; a nested filter chain in the old tool hides its logic.

5.2 Formatter steps become a Code node. Keep it under 20 lines and return the same object shape the next node expects.

5.3 Storage steps become HTTP requests to the provider's API. Test with the smallest possible file before wiring the real one.

5.4 Multi-step delays: a Wait node over 5 minutes needs a queue mode worker, not the default single-process setup.

5.5 Loops: replace per-item Zapier steps with one Loop Over Items node and a single API call per batch where the provider supports batching.

Gate: each ported workflow has its branch logic visible as nodes, and no Code node exceeds 20 lines.

## Stage 6 - Recreate the error handling the old tool did for you

6.1 Every workflow gets a settings-level error workflow that posts to one channel with the workflow name, execution id and the failing node.

6.2 Set retry-on-fail for network nodes: 3 attempts, exponential backoff starting at 5 seconds. Do not retry a node that writes money or sends a message without an idempotency key.

6.3 Set `EXECUTIONS_DATA_MAX_AGE` to 14 days. Unbounded execution history fills a small disk in weeks.

6.4 Add a dead-man check: if a workflow has not run in 2x its expected interval, alert. Silence is the failure mode of every automation.

6.5 Keep an audit of which workflows are active, with an owner, in the repository - not only in the UI.

| Control | Setting | Why |
|---|---|---|
| error workflow | one per instance | single alert path |
| retries | 3, backoff 5 s | transient network errors |
| execution retention | 14 days | disk space |
| dead-man alert | 2x interval | catches silent failure |
| owner | per workflow | someone to call |

Gate: a deliberately broken workflow produces one alert naming the failing node.

## Stage 7 - Cut over with a rollback you have tested

7.1 Cut over one workflow per day at most, in the morning, never on a Friday.

7.2 Keep the old workflow disabled but intact for 30 days, with its credentials untouched.

7.3 Write the rollback in 3 lines: enable old, disable new, replay the failed window from the source. Test the replay once.

7.4 Announce the cutover in the channel where the outputs land, so a silent change does not look like a bug.

Gate: rollback tested once on a real workflow, and the 30-day retention is on the calendar.

## Stage 8 - Measure the migration, not the effort

8.1 Tasks per month before and after, and the monthly bill before and after, including hosting.

8.2 Execution success rate per workflow for the first 30 days. Anything below 99% needs attention before the next migration.

8.3 Manual interventions per week. A migration that needs a human twice a week has moved the cost, not removed it.

8.4 Hosting cost is real: a ₹1,500-3,000 a month instance plus your time. Compare honestly against the bill.

| Metric | Before | After | Note |
|---|---|---|---|
| tasks/month | 42,000 | 0 billed | self-hosted |
| tool bill | ₹18,000/mo | ₹0 | |
| hosting | ₹0 | ₹2,400/mo | 2 vCPU, 4 GB |
| workflows migrated | 0 | 18 of 24 | 6 retired |
| success rate | not visible | 99.4% | error workflow |
| manual fixes/week | 2 | 1 | dead-man alerts |

Gate: three months of the four metrics recorded, including hosting cost.

## Stage 9 - Retire the old account without losing history

9.1 Export the run history you need for audit before closing anything.

9.2 Rebuild the 2-3 workflows that stayed on the old tool as documented exceptions with a reason.

9.3 Cancel only after 30 days of stable cutover on every migrated workflow.

9.4 Keep the old credentials revoked, not deleted, for 30 days so a rollback still works.

Gate: history exported, exceptions documented, and the account closed with a written date.

## Worked example

A 24-workflow agency account, ₹18,000 a month, migrated over 5 weeks.

| Week | Action | Workflows moved | Tasks removed |
|---|---|---|---|
| 1 | instance up, simplest workflow | 1 | 120 |
| 2 | top 4 by task cost | 5 | 21,400 |
| 3 | 6 mid-size, parallel runs | 11 | 33,900 |
| 4 | 4 long chains rebuilt with loops | 15 | 40,200 |
| 5 | cutover, 6 retired | 18 of 24 | 42,000 |

Two workflows stayed on the old tool: one needed a provider app with no API and one was used by a client who insisted on it. Both were documented as exceptions, and the account moved to the cheapest plan instead of being closed.

## Quality checklist

- [ ] Every workflow inventoried with runs, actions and tasks per month
- [ ] Ranked by task cost, not importance
- [ ] Keep, rebuild or retire decided per workflow
- [ ] Instance pinned to an image tag, never latest
- [ ] Postgres as the workflow database
- [ ] Encryption key stored outside the server and backed up
- [ ] HTTPS with a correct webhook base URL
- [ ] First workflow rebuilt and run 10 times with real payloads
- [ ] Error branch on every workflow from day one
- [ ] 5-7 days of parallel running with a parity log
- [ ] Every mismatch explained in writing
- [ ] Retries set to 3 with backoff, idempotency where money moves
- [ ] Execution retention set to 14 days
- [ ] Dead-man alert at 2x the expected interval
- [ ] Rollback written and tested once
- [ ] Hosting cost included in the before/after comparison

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Webhooks point at localhost | `WEBHOOK_URL` not set to the public host | Set host and webhook base, restart |
| Every credential unreadable after a restore | Encryption key not backed up | Store the key separately, restore it first |
| Instance broke after a restart | Image tag was `latest` | Pin the version, upgrade deliberately |
| Workflow retries a payment 8 times | No idempotency key, retry on a write node | Key the write, disable retry on it |
| Nobody noticed a workflow stopped | No dead-man check | Alert at 2x the expected interval |
| Disk full in 3 weeks | Execution history never pruned | Prune at 14 days |
| Parity looked fine, 5 records wrong | Compared counts, not per-run output | Hash and compare per execution |
| Long workflow stalls | Wait node on single-process mode | Queue mode with a worker |
| Migration cost more than the bill | Hosting plus maintenance not counted | Include both in the comparison |
| Old and new both sending messages | Old workflow not disabled at cutover | Disable, do not delete, for 30 days |

## Copy-ready agent prompt

> Read the skill at the URL above and plan my migration off a per-task automation tool onto a self-hosted runner. Ask me: how many workflows, the monthly bill, my busiest workflows, which providers they touch, and whether I can run a small server. Then give me the inventory table with runs, actions, tasks per month and a keep/rebuild/retire decision, the instance setup with pinned image, Postgres, encryption key handling and the correct webhook base URL, the node mapping for each step type, the parallel-run parity plan with a per-execution hash comparison, the error workflow, retry and dead-man settings, the cutover order with a tested rollback, and the before/after table including hosting cost. Tell me which workflows I should retire rather than migrate.
