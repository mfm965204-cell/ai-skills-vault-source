---
name: flaky-test-triage
description: Find flaky tests from rerun data, quarantine them with an owner
and expiry, and fix each one by cause so the suite becomes a signal you can
gate deploys on.
version: 1.0.0
license: MIT
tags: [testing, ci, reliability, debugging, engineering]
---

# Flaky Test Triage

A test that fails one run in fifty teaches the team to re-run instead of read.
Within a month the suite is background noise and a real regression merges
because the failure looked familiar. The cost is not the reruns; it is that
the gate stopped meaning anything.

This skill replaces re-running with a measured process: flakiness detected
from rerun data, a quarantine with an owner and a 14-day expiry, five cause
buckets, and a fix per bucket. The end state is a suite whose failure rate is
under 0.1% and whose failures are read.

## When to use this skill

- The team says "just re-run it" more than once a week.
- Your CI suite fails on main at least twice a day with no code change between runs.
- A deploy gate was made non-blocking because it was too noisy to keep blocking.
- You cannot name which of your 200 tests is the flaky one.

Do NOT use for: a suite that is slow but deterministic (that is test-suite
parallelisation and fixture design), or a single failing test with a
reproducible error — that is a normal bug, not flakiness.

## Stage 1 — Detect flakiness from data, not memory

Flakiness is a rate, and a rate needs reruns. Get the numbers before touching
any test.

1.1 Turn on automatic reruns of failed tests, capped at 3 attempts, and record per-test outcome per attempt in CI output.

1.2 Compute a per-test flake rate over the last 500 runs: failures that passed on retry divided by total runs.

1.3 Rank and publish the top 10 by flake rate; a test above 2% is quarantined, above 0.1% gets a ticket.

Gate: you hold a table of test id, runs, retry-passes and flake rate, and the
top 10 are named.

## Stage 2 — Quarantine without losing the gate

Deleting a flaky test hides a real bug; leaving it blocking trains the team to
ignore red. Quarantine is the middle path with an expiry.

2.1 Move the test to a quarantine suite that runs on a schedule but does not block merges, and tag it `@quarantine` in the source.

2.2 Create a ticket per quarantined test with the flake rate, the first failing log link and an owner — a quarantine with no owner is a deletion with extra steps.

2.3 Record the quarantine date in the test file itself, so the age is visible without querying a dashboard.

2.4 Set the expiry at 14 days. On expiry the test is either fixed or deleted with a note in the ticket; a second extension needs a reason in writing.

Gate: the blocking suite contains no `@quarantine` tests, and every
quarantined test has an owner and a date.

## Stage 3 — Classify the cause into one of five buckets

Almost every flake is one of five mechanisms. Naming the bucket tells you the
fix before you read the code.

| Bucket | Signature in the log | Typical fix |
|---|---|---|
| Timing | assertion ran before an async update landed | wait on a condition, not a sleep |
| Order dependence | passes alone, fails in the full suite | isolate shared state per test |
| Shared state | second test sees the first test's rows | transactional rollback or unique fixtures |
| Nondeterminism | random, uuid or hash ordering | seed the generator, sort before comparing |
| Environment | passes locally, fails in CI | pin timezone, locale, clock and network |

3.1 Read the last 5 failures of the test and match the stack and the log lines against the table.

3.2 Write the bucket in the quarantine ticket; if two buckets fit, the test is doing two jobs and should be split.

3.3 Confirm the bucket by reproducing locally: run the test 50 times in a loop and count failures — a 2% flake fails roughly once in 50.

Gate: every quarantined test carries one bucket label, and the label was
confirmed by local repetition.

## Stage 4 — Fix timing with conditions, not sleeps

A `sleep(500)` converts a fast failure into a slow one and moves the flake to
a loaded machine.

4.1 Replace fixed sleeps with a poll on the actual condition, with a 5-second ceiling and a 100 ms interval.

```javascript
// before: await sleep(500); expect(el).toHaveText('Saved')
await expect(el).toHaveText('Saved', { timeout: 5000 });
```

4.2 For backend async work, expose a readiness signal — a job status field or a queue drain — and poll that instead of the database.

4.3 Cap the whole test at 30 seconds so a hung dependency fails as a timeout with a message rather than blocking the runner for 10 minutes.

4.4 Fail loudly on timeout with the observed state attached, so the next failure is diagnosable from the log alone.

Gate: the test contains no `sleep` call, and 50 consecutive local runs pass.

## Stage 5 — Isolate shared state and order

A test that depends on another test's data is a sequence, not a test.

5.1 Give every test its own fixture namespace — a unique account id per test — so parallel runs cannot collide.

5.2 Wrap database tests in a transaction that rolls back, or truncate the affected tables in a teardown that runs even on failure.

5.3 Prove order independence: run the suite with a random seed 3 times and with the test alone once; all four runs must pass.

Gate: the test passes alone, passes in the full suite, and passes with a
shuffled order.

## Stage 6 — Seed randomness and freeze the clock

Random ids, unordered maps and the wall clock are three deterministic inputs
you left unset.

6.1 Seed every random generator from a fixed value in tests, and sort any collection before asserting on it.

6.2 Inject a clock and set it to a fixed instant — 2026-01-15T09:30:00+05:30 is a working choice for an India-first suite — and pin the timezone to `Asia/Kolkata` in CI.

6.3 Assert on shape and ordering rather than on generated ids, or generate the id from the seed so it is predictable.

Gate: the test produces byte-identical output across 20 runs, diffs included.

## Stage 7 — Stub the network at the boundary

A test that calls a third party is a test of that third party's uptime.

7.1 Intercept HTTP at the client boundary and return recorded responses, with an explicit failure mode for unexpected calls.

7.2 Keep 3 recorded fixtures per external call: success, 429 with `Retry-After`, and 5xx — the 429 case catches the retry logic most suites skip.

7.3 Make the stub fail on an unexpected call rather than returning an empty 200, so a new outbound call shows up as a test failure instead of a silent gap.

7.4 Run the real integration in a separate nightly suite with a 10-minute timeout, so the stub cannot drift from reality unnoticed.

Gate: the blocking suite makes no outbound network calls, verified by running
it with networking disabled.

## Stage 8 — Keep the quarantine honest

Quarantine rots without a clock. Make the expiry mechanical.

8.1 A weekly job lists quarantined tests past their date and posts them to the team channel with the owner tagged.

8.2 A test quarantined twice for the same bucket is deleted, not fixed a third time — a third attempt is a design problem in the test harness.

8.3 Track the quarantine count as a metric; above 5 open quarantines, stop new test work until it drops.

Gate: zero quarantined tests past their expiry date at the end of any week.

## Stage 9 — Report the flake rate and gate on it

The number that matters is the suite's failure rate on unchanged code,
measured weekly.

9.1 Publish weekly: suite runs, failures, retry-passes, flake rate, open quarantines.

9.2 Post the weekly number with the three worst tests named, because a rate without names does not get fixed.

9.3 Gate deploys on flake rate under 0.1% for the blocking suite, not just on pass or fail.

9.4 Keep a 30-day history of the rate, because a suite that drifts from 0.05% to 0.4% over a quarter is heading back to the state this skill exists to fix.

9.5 When a real regression merges, check whether a flaky test covered it — that is the failure this whole process exists to prevent.

Gate: the weekly report shows the flake rate, and the deploy gate reads it.

## Worked example — 14 flaky tests in a 212-test suite

A backend suite failed 3 to 5 times a day on main with no code change. The
first measurement was the useful one.

| Bucket | Tests | Share | Fix applied |
|---|---|---|---|
| Timing | 6 | 43% | condition polling, 5-second ceiling |
| Shared state | 4 | 29% | per-test account namespace, rollback teardown |
| Nondeterminism | 2 | 14% | seeded generator, sorted comparison |
| Environment | 1 | 7% | pinned `TZ=Asia/Kolkata`, injected clock |
| Order dependence | 1 | 7% | fixture split into two tests |

Before: 212 tests, 4.1 failures per 100 runs, flake rate 3.4%, 22 minutes of
reruns per day across the team.

After: 219 tests, 0.6 failures per 100 runs, flake rate 0.07%, and the merge
gate restored to blocking.

The timing fix is the one to copy. The original test looked like this:

```javascript
await page.click('#save');
await sleep(500);                       // tuned on a laptop
expect(await page.textContent('#status')).toBe('Saved');
```

It passed locally and failed on the 4-vCPU runner roughly 1 run in 20. The
replacement removed the sleep entirely and polled the DOM condition with a
5-second ceiling, so a slow runner waits and a broken build fails with the
observed text attached.

The shared-state fix was smaller than expected: the failing tests all inserted
a customer with the fixed id `cust_1`, so parallel workers overwrote each
other. Deriving the id from the test name took four lines and removed 3 of the
4 failures in that bucket immediately.

Run the measurement yourself before and after:

```bash
# per-test flake rate from CI history
python3 flake.py --runs 500 --min-rate 0.02 --top 10
# reproduce locally, 50 attempts
pytest tests/test_checkout.py::test_saves -q --count=50
```

## Second example — a single test that was three tests

One test, `test_order_flow`, had a 9% flake rate and the highest rerun cost in
the suite. Reading it explained the rate: 140 lines, a browser, a database and
a payment stub, asserting on 11 outcomes.

| Attempt | Change | Flake rate | Suite time |
|---|---|---|---|
| 0 | as written | 9.0% | 41 s |
| 1 | quarantine and split into 3 tests | 9.0% | 43 s |
| 2 | stubbed the payment call at the client | 2.1% | 12 s |
| 3 | per-test account fixture, no shared rows | 0.4% | 11 s |
| 4 | condition polling instead of 2 sleeps | 0.0% | 9 s |

Splitting first did not change the rate, which is the point: the split made
the causes visible, and the causes were a live third-party call, shared rows
and two fixed sleeps. Four changes, each removing one mechanism, took it from
9% to zero across 300 runs.

The 41-second test was also the reason the suite took 10 minutes: it dominated
the critical path, and every rerun cost 41 more seconds. The final 9-second
version made the whole suite fit in 6 minutes.

## Quality checklist

- [ ] Automatic reruns enabled with per-attempt outcome recorded.
- [ ] Per-test flake rate computed over at least 500 runs.
- [ ] Top 10 flaky tests named and published.
- [ ] Quarantine suite excluded from the merge gate.
- [ ] Every quarantined test has an owner and a 14-day expiry.
- [ ] Each quarantined test carries one of the five bucket labels.
- [ ] No `sleep` call in any fixed test.
- [ ] Fixtures namespaced per test.
- [ ] Order independence proven with a shuffled run.
- [ ] Random seeds fixed and collections sorted before comparison.
- [ ] Clock and timezone injected and pinned.
- [ ] Network stubbed at the client boundary, with a 429 fixture.
- [ ] Quarantine count below 5 open items.
- [ ] Weekly flake rate published and read by the deploy gate.
- [ ] Local reproduction ran under the CI CPU limit.
- [ ] Module-level state reset between tests.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Test passes 40 runs then fails once | A fixed sleep shorter than the async write on a loaded runner | Poll the condition with a 5-second ceiling |
| Test passes alone, fails in the suite | Shared fixture rows left by an earlier test | Unique namespace per test plus rollback teardown |
| Same test flakes on different assertions | Random ordering in an unordered collection comparison | Sort before asserting, seed the generator |
| Flake rate is 0% in reports but CI is red daily | Only the final attempt is recorded, so retry-passes are invisible | Record every attempt, not just the last outcome |
| Fixing one test creates two more | The test asserts on 3 behaviours and the harness is shared | Split the test and give it its own fixture |
| Quarantine list grows every sprint | No expiry enforcement, no owner | Weekly job that names overdue tests and their owners |
| Test passes in CI, fails on a laptop | Timezone or locale differs from the pinned CI value | Pin `TZ` and locale in both, inject the clock |
| Quarantined test still blocks a merge | The tag excludes it from the report but not from the gate script | Filter the gate on the tag, and assert the gate's test count in CI |
| Flake rate jumps after a dependency upgrade | A library changed its default timeout or ordering | Pin the version and re-run the top 10 flaky tests before merging the bump |
| New test is flaky on the first day | It was written against a live staging environment | Move it to stubs before it enters the blocking suite |
| Suite time doubled after quarantine | Quarantined tests still run in the blocking job under a different name | Check the gate script's collected test count, not its exit code |
| Fix works locally, flake returns in CI | The local loop ran on 8 cores and CI on 2 | Reproduce with the CI container's CPU limit, not the laptop |
| Two tests fail only when run together | A module-level cache shared across the file | Reset the cache in `beforeEach`, or move the cache behind the fixture |
| Retry passes hide a real bug | The rerun masks a genuine race in production code, not the test | Read the retry-pass logs monthly for the same stack trace |

## Copy-ready agent prompt

> Read the skill at the URL above and triage my flaky tests. Compute the per-test flake rate from rerun data over the last 500 runs, quarantine anything above 2% with an owner and a 14-day expiry, label each one with a cause bucket, then fix them in bucket order: conditions instead of sleeps, per-test fixtures, seeded randomness, pinned clock and stubbed network. Re-run the suite 3 times with a shuffled order and report the before and after flake rate. Stop and show me the log if a fix cannot reproduce the failure locally.
