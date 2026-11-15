---
name: feature-flag-rollout
description: Ship a change behind a flag and ramp it 1 to 100 percent with
guardrail metrics, a kill switch that needs no deploy, and a removal date so
flags do not pile up.
version: 1.0.0
license: MIT
tags: [release, feature-flags, rollout, observability, risk]
---

# Feature Flag Rollout

A deploy and a release are two different events. Deploying puts code on
servers; releasing exposes it to users. Bundling them means every release
needs a deploy window and every bad change needs a rollback. A flag separates
them: the code ships dark, the release becomes a percentage you can move in 30
seconds, and the rollback is a toggle rather than a revert.

The output is a change that reached 100% of traffic with two metrics watched
at each step, a documented kill switch, and a flag with a removal date rather
than a permanent branch.

## When to use this skill

- A change touches a payment, login, checkout or notification path and you cannot test it on real traffic safely.
- You need to release to 10 internal accounts before customers see anything.
- A previous rollback took 40 minutes because it meant a revert, a build and a deploy.
- You have more than 10 boolean flags in the codebase and cannot say which are still live.

Do NOT use for: database schema changes that cannot be run with both code
paths active (that is a two-phase migration), or permission and billing rules
that must be enforced server-side at all times — those are policy, not flags.

## Stage 1 — Inventory the flags you already have

A rollout discipline starts with knowing the current set. Untracked flags are
permanent branches with extra steps.

1.1 Export every flag key from the flag service and grep the codebase for each one: `rg -c 'flags\.(get|isEnabled)\(' src/ | sort -t: -k2 -rn`.

1.2 Record five fields per flag: key, owner, type, creation date, planned removal date. Anything without an owner is dead and should be deleted this week.

1.3 Find flags that no longer branch: a key referenced once, or referenced only in tests, is already removable.

Gate: every flag has an owner and a removal date, and the count of ownerless
flags is zero.

## Stage 2 — Pick the flag type before writing code

The type decides the lifetime and the defaults. Four types cover everything a
product ships.

| Type | Lifetime | Default | Example |
|---|---|---|---|
| Release | days to 2 weeks | off | new checkout flow |
| Ops | permanent, few | on | disable a slow third-party call |
| Permission | permanent | off per account | beta feature for paid plans |
| Experiment | one test cycle | off, bucketed | new pricing copy, A/B |

2.1 Write the type in the flag's description field, because the type is what tells the next engineer whether the flag may ever be removed.

2.2 For a release flag, set the removal date at creation — 14 days from the ramp start is the working default.

2.3 For an ops flag, name the exact failure it guards against in the description: "on = call the old pricing service when v2 returns 5xx above 1%".

Gate: the flag exists in the service with a type, an owner and a removal date
before any code references it.

## Stage 3 — Default off, evaluated at one boundary

A flag read in nine places is nine chances to get the default wrong. Evaluate
once and pass the result down.

3.1 Create the flag with `default: false` and no targeting rules, so a missing config or a flag-service outage fails closed to the old path.

3.2 Wrap at the request or job boundary and pass a boolean into the domain layer; the domain code should not import the flag client at all.

```python
# one read per request, at the edge
ctx.flags = {"new_checkout": flags.is_enabled(
    "checkout.v2", user_id=user.id, default=False)}
```

3.3 Add a startup assertion that the flag client resolved within 500 ms, and a fallback map for the 3 flags whose failure would break checkout.

Gate: `rg 'is_enabled|isEnabled' src/` shows one call site per flag, all
inside the request boundary.

## Stage 4 — Build the kill switch first

The kill switch is the flag set to off with no deploy. Test it before you need
it.

4.1 Add an ops console action or a documented CLI that flips the flag, and record who ran it and when.

4.2 Flip it off in staging while a load test runs and confirm the old path serves within 5 seconds — flag propagation delay, not code, is the number that matters.

4.3 Make the off path keep working for in-flight requests: anything written by the new path must still be readable by the old one, or the switch causes worse damage than the bug.

Gate: flipping off during a live test returns the old behaviour within 5
seconds and leaves no orphaned records.

## Stage 5 — Ramp in five steps with a hold at each

Percentages are chosen so a bad change is visible while the blast radius is
small.

5.1 Ramp 1% → 5% → 25% → 50% → 100%, holding at least 15 minutes at each step and one full business cycle (24 hours) at 25%.

5.2 Bucket by a hash of the account id, not the request, so one user sees one experience: `bucket = crc32(account_id + flag_key) % 100`.

5.3 Announce each ramp step in the deploy channel with the percentage, the two guardrail numbers and the time of the next step, so the on-call engineer is never surprised by traffic shifting.

5.4 Log the bucket decision once per request with the flag key, so a support ticket can be answered without guessing which variant the user saw.

Gate: at each step the error rate stays inside the guardrail and the bucketing
is stable for repeat requests from the same account.

## Stage 6 — Attach two guardrail metrics and one auto-rollback

A ramp without a guardrail is a gamble with extra steps.

6.1 Pick two metrics that would move if the change were bad — error rate on the affected endpoint and p99 latency are the default pair.

6.2 Compare the flagged cohort against the unflagged cohort on the same dashboard, not against last week, so traffic mix changes do not look like regressions.

6.3 Set the guardrail threshold as an absolute difference, not a ratio: a 1 percentage point gap in error rate is actionable at any traffic level, while "20% worse" is noise on a 0.2% base.

6.4 Wire an automatic rollback: if the flagged cohort's error rate exceeds the control by 1 percentage point for 5 minutes, the flag returns to the previous percentage and the on-call channel gets a message.

Gate: the guardrail dashboard shows both cohorts, and a simulated error spike
triggers the rollback without human action.

## Stage 7 — Keep targeting rules simple enough to audit

Every targeting rule is a code path you cannot read in the repo. Fewer is
better.

7.1 Allow exactly four rule kinds: percentage, account id list, plan tier, and internal staff. Reject everything else in review.

7.2 Cap the account id list at 50 entries; a list of 400 is a percentage with extra maintenance.

7.3 Export the rules nightly to a file in the repo, so a diff shows when targeting changed and by whom.

Gate: the exported rules file matches the service, and no flag has a rule kind
outside the four.

## Stage 8 — Record changes and limit who can flip

The audit log is what turns an incident into a five-minute explanation.

8.1 Require a change reason on every percentage change; the field is one line and saves an hour of archaeology.

8.2 Post the flag's current state in the deploy channel at the start of every ramp, so the percentage is never a guess during an incident.

8.3 Limit production flips to the on-call engineer and the feature owner; everyone else gets staging.

8.4 Review the audit log at the retro for every incident that involved a flag change, and note whether the change was the cause, the fix, or noise.

8.5 Send flag changes to the same channel as deploys, so the timeline of an incident has one source.

Gate: the audit log answers who changed which flag, from what to what, and
why, for every change in the last 30 days.

## Stage 9 — Remove the flag, then remove the old path

A flag at 100% for 30 days is dead code with a config entry. Both halves must
go.

9.1 Delete the flag from the service, then delete the branch from the code in the same week — leaving the flag wired but constant is how a codebase grows two of everything.

9.2 Search for the key one more time after removal: `rg 'checkout.v2' .` should return only the changelog entry.

9.3 Run a monthly sweep for flags whose removal date has passed: `rg 'flags\.is_enabled' src/ -A1 | rg 'checkout\.v2|pricing\.v3'` finds the stragglers by name.

9.4 Add the removal to the release notes so the support team knows the old path is gone.

Gate: the flag key returns no code references, and the flag service shows the
flag archived.

## Worked example — a checkout rewrite at 100% in six days

A payments team replaced a checkout service and needed to release without a
deploy window.

| Day | Percentage | Guardrail: payment errors | Guardrail: p99 checkout | Decision |
|---|---|---|---|---|
| 1 | 1% | 0.4% versus 0.4% control | 210 ms versus 205 ms | hold |
| 1 | 5% | 0.4% versus 0.4% | 212 ms versus 205 ms | hold 24 h |
| 2 | 25% | 0.5% versus 0.4% | 240 ms versus 205 ms | hold, investigate |
| 3 | 25% | 0.4% versus 0.4% | 214 ms versus 205 ms | cause found, resume |
| 4 | 50% | 0.4% versus 0.4% | 216 ms versus 206 ms | hold 24 h |
| 6 | 100% | 0.4% versus 0.4% | 218 ms versus 207 ms | flag removed |

The day-2 pause was the useful part. p99 rose 35 ms at 25% and the error rate
moved 0.1 of a point. The cause was a per-request call to the old pricing
service that the new path made twice — visible only because the dashboard
compared flagged against control on the same minute window, not against last
week.

Two things went wrong and both are worth copying the fix for.

The kill switch took 3 minutes to take effect. The flag client polled every 60
seconds and the console change only applied on the next poll. Fix: streaming
updates for ops flags, and a 5-second poll as the fallback. The target is 5
seconds end to end.

Rolling back at 25% left 4,000 orders written by the new path that the old
reader could not parse. Fix: the new path wrote both the old and new shape for
one release, so a rollback was a reader change rather than a data migration.

The flag config that shipped, in the service's own syntax:

```yaml
key: checkout.v2
type: release
owner: payments-team
default: false
created: 2026-11-01
remove_by: 2026-11-15
bucketing: crc32(account_id + key) % 100
guardrails:
  - metric: payment_error_rate
    compare: control_cohort
    threshold_pct: 1.0
    window_minutes: 5
    action: revert_to_previous_percentage
```

## Second example — an ops flag that stopped a cascade

A search service depended on a recommendations API that degraded every
evening. The flag was not a release; it was a switch to a cheaper local
fallback.

| Field | Value |
|---|---|
| Key | `recs.fallback_local` |
| Type | ops |
| Default | off |
| Flip condition | recommendations p99 above 800 ms for 5 minutes |
| Effect | serve cached recommendations for 10 minutes |
| Owner | search on-call |
| Review | quarterly, because the dependency may be fixed |

The flag was flipped 4 times in the first month and never needed a deploy.
Each flip took under 5 seconds because ops flags used the streaming path
rather than the 60-second poll.

Two rules made it safe. The fallback path had to be tested under load before
the flag was created, because a fallback nobody has exercised is a second
outage. And the flag was reviewed quarterly rather than removed, since the
dependency could regress at any time — an ops flag with a review date is not
the same thing as a stale release flag.

The failure it prevented, measured: the evening degradation used to push
search p99 from 180 ms to 3,400 ms and time out 8% of queries. With the switch
flipped at the 5-minute mark, search held at 240 ms with 0.3% errors while
recommendations recovered.

## Quality checklist

- [ ] Every flag has an owner, a type and a removal date.
- [ ] Release flags default to off in the flag service.
- [ ] One flag read per request, at the request boundary.
- [ ] Flag client failure falls back to the old path within 500 ms.
- [ ] Kill switch tested during a live staging test.
- [ ] Bucketing keyed on account id, not request id.
- [ ] Two guardrail metrics with a flagged-versus-control comparison.
- [ ] Automatic rollback triggers on a simulated error spike.
- [ ] Targeting limited to four rule kinds.
- [ ] Nightly rules export committed to the repo.
- [ ] Change reason required and audit log queryable.
- [ ] Removal date enforced by a ticket or a linter warning.
- [ ] Old code path deleted in the same week as the flag.
- [ ] No flag key remains in the code after removal.
- [ ] Ops flags reviewed quarterly, not removed.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Users see both variants in one session | Bucket computed per request from a request id | Bucket on account id and cache the decision for the session |
| Flipping the flag does nothing for 3 minutes | Client polls the flag service on a 5-minute interval | Push updates over streaming, or cut the poll to 5 seconds for ops flags |
| Error rate looks fine during the ramp | Dashboard compares against last week, not against the control cohort | Plot both cohorts from the same minute window |
| Old path breaks after rollback | New path wrote rows the old code cannot parse | Write both shapes for one release, then drop the old reader |
| Flag count doubled in a quarter | No removal date and no owner on release flags | Linter warning at 14 days, build failure at 30 |
| Targeting rule changed and nobody knows why | Console changes bypass the repo | Export rules nightly and diff them in CI |
| Guardrail fired but traffic kept coming | Rollback changed the percentage but caches served the new path | Add a cache-busting version key to the flagged response |
| Flag read inside a retry loop | The flag call sits in the domain layer rather than the request boundary | Read once per request and pass the boolean down |
| Percentage moved but a cohort is unchanged | Targeting rule for plan tier evaluated before the percentage | Order rules as percentage, then id list, then tier |
| Removal broke an integration test | The test asserted on the old path through the flag | Assert on the flag-off path only, and delete the flag-on test with the flag |
| Stale flag found in a hot path | No owner, so nobody removed it when the feature shipped | Delete the flag and the branch in one PR, and log the removal |

## Copy-ready agent prompt

> Read the skill at the URL above and put my change behind a flag. Inventory the existing flags with owner, type and removal date, create the new flag default-off with a 14-day removal date, wire one read at the request boundary, and build the kill switch. Then walk the ramp 1, 5, 25, 50, 100 with the two guardrail metrics and the automatic rollback configured, and show me the audit log entry for each step. Stop before the first ramp step if the kill switch has not been tested in staging.
