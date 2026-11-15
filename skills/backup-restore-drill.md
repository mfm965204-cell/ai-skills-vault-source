---
name: backup-restore-drill
description: Prove backups work by restoring them on a timer, with an RPO, an RTO, a checksum test and a written record that survives the person who set it up.
version: 1.0.0
license: MIT
tags: [automation, backup, restore, disaster-recovery, ops]
---

# Backup Restore Drill

Most teams have backups and no restores. The backup job has been green for 400 days, the bucket has 2 TB in it, and the first time anyone opens a restore they find the dump is truncated, the encryption key is in the server that died, or the restore takes 11 hours against an assumed 2.

This skill treats the restore as the product: define RPO and RTO, back up, then restore on a schedule into a clean environment and verify with checksums and row counts. You end with a drill that runs monthly, a record per run, and a number you can quote to a customer or an auditor.

## When to use this skill

- You have a backup job and have never restored from it.
- The backup script lives on the same server as the database.
- Nobody knows whether the restore takes 20 minutes or 8 hours.
- A compliance form asked for your RPO and RTO and you guessed.

Do NOT use for: designing the production database, or choosing a storage provider on price. It also does not cover application-level logical backups for a single table - this is the whole-system restore path.

## Stage 1 - Write the two numbers before touching a script

1.1 RPO - how much data you can afford to lose, in minutes. A nightly dump is an RPO of up to 24 hours, which is unacceptable for a payment ledger.

1.2 RTO - how long a restore may take, in hours. This is the number that decides the architecture, not the backup tool.

1.3 Get both agreed in writing with whoever owns the business risk, not decided by the person writing the script.

1.4 Derive the schedule from the RPO: 15 minutes needs continuous archiving (WAL or binlog), 24 hours allows a nightly dump.

| Data class | RPO | RTO | Method |
|---|---|---|---|
| payment ledger | 5 min | 1 h | continuous WAL archiving |
| customer database | 1 h | 4 h | hourly dump plus WAL |
| file uploads | 24 h | 8 h | versioned object storage |
| analytics warehouse | 24 h | 48 h | nightly export |

Gate: RPO and RTO written down per data class, signed off by the owner of the risk.

## Stage 2 - Move the backup off the machine it protects

2.1 Back up to a different provider or at minimum a different account and region. A script on the same host dies with the host.

2.2 Object storage with versioning and object lock, so ransomware or a bad script cannot delete the history.

2.3 Encrypt at rest with a key stored outside the backup account. A key in the same account is not a second copy.

2.4 Restrict delete permission on the bucket to a break-glass role used twice a year.

2.5 Keep 7 daily, 4 weekly and 12 monthly copies, and say where each tier lives.

| Tier | Retention | Storage class | Restore speed |
|---|---|---|---|
| daily | 7 days | standard | minutes |
| weekly | 4 weeks | standard or IA | minutes |
| monthly | 12 months | cold | hours |
| yearly | 3 years | archive | 12-48 h |

Gate: backups exist in a second account, versioned, encrypted with an externally stored key, with a documented retention tier per class.

## Stage 3 - Take the backup with a method that can be verified

3.1 For Postgres, use `pg_dump -Fc` for logical or `pg_basebackup` plus WAL for physical. Do not tar a live data directory.

3.2 Record a checksum at creation: `sha256sum` for a dump, the provider's ETag for an object.

3.3 Record the row count of the 5 most important tables at backup time. A restore without a count is a guess.

3.4 Log the backup's start, end, size, duration and checksum to a table or a file that is not on the backed-up host.

```bash
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="/tmp/db-$TS.dump"
pg_dump -Fc --no-owner --no-privileges "$DATABASE_URL" -f "$OUT"
SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
SIZE=$(stat -c%s "$OUT")
aws s3 cp "$OUT" "s3://backups-prod/postgres/$TS.dump" \
  --expected-size "$SIZE" --sse aws:kms
echo "$TS $SIZE $SHA" >> /var/log/backup-manifest.txt
```

Gate: every backup has a checksum, a size and a duration recorded off-host.

## Stage 4 - Restore into a clean environment, not over production

4.1 A restore drill creates a fresh instance, restores into it, verifies, then destroys it. Never test by restoring over live data.

4.2 Script the whole drill: provision, restore, verify, report, teardown. A manual drill happens once and never again.

4.3 Time every phase and record it: provision, download, restore, verify. The RTO is the sum, not the download time.

4.4 Run the drill from a machine that is not the database host, with credentials a different person holds.

```bash
# drill.sh - full restore into a throwaway database
export PGPASSWORD="$DRILL_PW"
createdb -h "$DRILL_HOST" drill_restore
time pg_restore -h "$DRILL_HOST" -d drill_restore --no-owner --jobs 4 "$DUMP"
psql -h "$DRILL_HOST" -d drill_restore -Atc \
  "SELECT 'orders', count(*) FROM orders UNION ALL SELECT 'users', count(*) FROM users;"
```

Gate: the drill completes end to end from a script, on a machine that is not the source.

## Stage 5 - Verify with numbers, not with a successful exit code

5.1 Compare row counts for the 5 critical tables against the counts recorded at backup time.

5.2 Run 3 real queries the application runs, and check they return plausible results - not just that they execute.

5.3 Check the newest row's timestamp is within the RPO window. A restore that ends 26 hours ago fails a 24-hour RPO.

5.4 Check that indexes, sequences, foreign keys and permissions came back. `pg_restore --no-owner` restores data without owners, which can break an app that relies on role permissions.

5.5 Spot-check 5 random rows against the source by primary key.

| Check | Pass condition | Fails when |
|---|---|---|
| row counts | equal to backup-time counts | a table is missing |
| newest row | within the RPO | archive lag |
| queries | 3 app queries return results | index or constraint missing |
| sequences | next value above max id | inserts collide |
| permissions | app role can read and write | restored without owners |

Gate: all five checks pass, and the newest row is inside the RPO window.

## Stage 6 - Set the drill schedule and make it boring

6.1 Monthly full restore drill. Weekly automated verification of the checksum and the row counts without a full restore.

6.2 The drill owner is named, and the person who wrote the script must be able to be on leave during a drill.

6.3 Rotate who runs the drill every quarter. A drill only one person can run is a single point of failure.

6.4 Any failed drill blocks the release train until it is fixed. A red drill that nobody fixes is a false sense of safety.

| Cadence | What runs | Who |
|---|---|---|
| daily | backup job plus checksum | automation |
| weekly | checksum plus row-count verification | automation |
| monthly | full restore into a clean instance | named owner |
| quarterly | drill run by a different person | rotated |

Gate: 3 consecutive monthly drills recorded, one of them run by someone other than the author.

## Stage 7 - Write the runbook for the real event

7.1 One page: how to find the latest good backup, how to restore, how to verify, how to point the app at the restored database.

7.2 Include the exact commands with placeholders clearly marked, and the names of the people who hold the credentials.

7.3 Include the decision: restore to a point in time, or restore the last nightly. Point-in-time needs the WAL archive, and the runbook must say where it is.

7.4 Practise reading the runbook aloud with someone who has never done it. Any step that needs explanation is a step that fails at 3am.

Gate: a person who has not done it before completes the drill using only the runbook.

## Stage 8 - Cover the parts people forget

8.1 Secrets and configuration: the app's environment variables, the TLS certificates and the encryption keys. A restored database with no keys is a pile of ciphertext.

8.2 File uploads and generated documents, backed up separately from the database with the same RPO discipline.

8.3 The backup system itself: its configuration and credentials in a sealed copy, because the person who knows the login may be unavailable.

8.4 DNS and provider access: the ability to repoint a domain, with credentials not stored only in one person's account.

| Asset | Backed up | Restore tested |
|---|---|---|
| database | yes | yes, monthly |
| object storage | yes, versioned | yes, quarterly |
| secrets and env | sealed copy | yes, quarterly |
| certificates | yes | yes, quarterly |
| DNS access | documented | annually |

Gate: every row in the table has a tested restore path, not just a backup.

## Stage 9 - Report it in numbers

9.1 Per drill: duration, rows restored, checks passed, RPO achieved, RTO achieved.

9.2 Trend the RTO month over month. A restore that creeps from 40 minutes to 4 hours is a capacity problem before it is an outage.

9.3 Cost per month of storage and drill time, so the trade-off against the risk is visible.

9.4 Keep the last 12 drill records in one file. That file is what answers a compliance question and what stops an argument after an incident.

| Drill | Duration | Rows | RPO achieved | RTO achieved |
|---|---|---|---|---|
| 2026-09 | 38 min | 4.2 M | 20 min | 38 min |
| 2026-10 | 41 min | 4.4 M | 20 min | 41 min |
| 2026-11 | 44 min | 4.6 M | 20 min | 44 min |

Gate: 12 months of drill records exist, with both numbers per drill.

## Worked example

A 12-person SaaS on a single Postgres instance, 40 GB, nightly dumps to the same provider.

| Item | Before | After |
|---|---|---|
| RPO claimed | 24 h | 24 h (ledger 5 min) |
| RTO claimed | 2 h | 3 h, measured |
| Backup location | same account, same region | second account, versioned |
| Restore ever tested | no | monthly, 3 recorded |
| Encryption key | on the database host | sealed copy, external |
| Restore time measured | unknown | 38-44 min for 4.6 M rows |
| Drill owner | nobody | named, rotated quarterly |

The first drill failed: the dump restored but the sequences were not reset, so the app's next insert collided with an existing id. That failure had been sitting in production for 14 months and would have appeared on the worst possible day.

## Quality checklist

- [ ] RPO and RTO written per data class and signed off
- [ ] Backups stored in a second account or provider
- [ ] Object versioning and lock enabled
- [ ] Encryption key stored outside the backup account
- [ ] Delete permission restricted to a break-glass role
- [ ] Retention tiers defined: 7 daily, 4 weekly, 12 monthly
- [ ] Backup method is dump or base backup, never a live directory tar
- [ ] Checksum and size recorded off-host per backup
- [ ] Row counts of 5 critical tables recorded at backup time
- [ ] Drill restores into a clean instance, never over production
- [ ] Drill scripted end to end, including teardown
- [ ] Row counts compared against backup-time counts
- [ ] Newest row inside the RPO window
- [ ] Sequences, indexes, foreign keys and permissions verified
- [ ] Runbook usable by someone who has never done it
- [ ] Secrets, uploads, certificates and DNS in the tested set

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Backup green, restore impossible | Dump truncated by a full disk | Check size and checksum per backup |
| Restore works, inserts collide | Sequences not restored | Verify next value above max id |
| Cannot decrypt the backup | Key stored on the host that died | Sealed external copy of the key |
| Restore takes 11 hours | RTO never measured, cold tier download | Measure per phase, keep the last daily in standard |
| Backup deleted by a bad script | No versioning or object lock | Enable versioning and lock, restrict delete |
| Restore has stale data | Archive lag outside the RPO | Monitor WAL shipping, alert on lag |
| App cannot read restored tables | `--no-owner` restored without grants | Reapply grants in the drill script |
| Nobody can run the drill | Only one person knows the steps | Rotate the owner quarterly, test the runbook |
| Uploaded files missing after a restore | Only the database was backed up | Back up object storage on its own schedule |
| Compliance answer was a guess | No drill records | Keep 12 records with both numbers |

## Copy-ready agent prompt

> Read the skill at the URL above and set up a restore drill. Ask me: what I back up, where the backups live, whether they are in a second account, whether I have ever restored, and what my business can tolerate losing. Then give me the RPO and RTO table per data class, the off-host backup design with versioning, object lock and an external key, the backup command with checksum and row-count recording, the scripted drill that restores into a clean instance and tears it down, the five verification checks including sequences and permissions, the drill schedule with a rotated owner, the one-page runbook, and the table of assets beyond the database that need a tested restore path. Tell me the first thing that would fail if I restored today.
