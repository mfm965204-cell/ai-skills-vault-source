---
name: webhook-retry-idempotency
description: Receive third-party webhooks without losing events or processing them twice, using signature checks, a durable queue, idempotency keys and a replay path.
version: 1.0.0
license: MIT
tags: [automation, webhooks, reliability, idempotency, engineering]
---

# Webhook Retry And Idempotency

A payment provider sends a `payment.succeeded` webhook, your endpoint times out at 8 seconds, and the provider retries. Meanwhile the first request finished anyway. Two credits, one payment, and a support ticket that takes a week to unwind.

This skill builds the receiving side correctly: verify the signature, acknowledge in under 500 ms, persist the raw event, process from a queue with an idempotency key, and keep a replay tool. You end with an endpoint that survives duplicate deliveries, out-of-order events and a 3-day outage at the sender.

## When to use this skill

- You receive webhooks from Stripe, Razorpay, Shopify, GitHub or a partner API and process them inline.
- A duplicate event created a duplicate record or a double credit.
- Events arrive out of order and the later one is overwritten by an earlier one.
- An outage lost events and there was no way to fetch them again.

Do NOT use for: sending webhooks, or general API retry design on the client side. It also does not cover queue infrastructure choices beyond what the receiver needs.

## Stage 1 - Write down the delivery contract

1.1 Ask each provider three things: retry schedule, timeout before they consider it failed, and whether events are ordered.

1.2 Most providers retry with exponential backoff for 1-3 days and treat any 2xx as success. Some stop at 5 attempts.

1.3 Ordering is usually per-object, not global. Two events for one order arrive in order; events for two orders do not.

1.4 Write the contract in the repo, per provider. A receiver built on an assumed contract breaks the first time a provider changes it.

| Provider behaviour | Typical value | What it forces |
|---|---|---|
| timeout | 5-30 s | acknowledge fast, process later |
| retries | 3-5, backoff hours | idempotency is mandatory |
| ordering | per object | version or timestamp check |
| at-least-once | yes | dedupe on event id |
| at-most-once | rare | reconciliation job needed |

Gate: retry schedule, timeout, ordering guarantee and delivery semantics documented per provider.

## Stage 2 - Verify the signature before reading the body

2.1 Compute the HMAC over the raw request body bytes, not the parsed JSON. Re-serialising JSON changes key order and the signature fails.

2.2 Compare with a constant-time function. A normal string comparison leaks timing and is a real vulnerability in a public endpoint.

2.3 Reject a timestamp older than 5 minutes to stop replays of an old, valid signature.

2.4 Read the secret from the environment, never from the repo, and support two active secrets during rotation.

```python
import hashlib, hmac, time
def verify(raw: bytes, header_sig: str, header_ts: str, secret: str) -> bool:
    if abs(time.time() - int(header_ts)) > 300:      # 5-minute window
        return False
    expected = hmac.new(secret.encode(), f"{header_ts}.".encode() + raw,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header_sig)
```

Gate: a tampered body, a replayed 10-minute-old signature and a wrong secret are all rejected with 401.

## Stage 3 - Acknowledge fast and process later

3.1 The endpoint does exactly three things: verify, insert the raw event into a table, return 200. Target under 200 ms.

3.2 Never call the provider's API, send an email, or run a database transaction with business logic inside the request.

3.3 Insert the raw payload as JSON plus headers, received-at timestamp and a unique constraint on the provider's event id.

3.4 If the insert fails, return 500 so the provider retries. A 200 on a failed insert loses the event permanently.

| Step in the request | Budget | Why |
|---|---|---|
| signature verify | under 5 ms | HMAC only |
| insert raw event | under 50 ms | one row, one index |
| return 200 | under 200 ms total | provider timeout |
| business processing | 0 ms | belongs in a worker |

Gate: p99 response time under 200 ms measured over 1,000 events.

## Stage 4 - Deduplicate on the event id, not the payload

4.1 Use the provider's event id as a unique key. Hashing the payload fails when the same event is re-sent with a different envelope timestamp.

4.2 A second delivery hits the unique constraint and is recorded as a duplicate, then returns 200. That is the correct outcome, not an error.

4.3 For providers without a stable event id, build a key from type, object id and the object's updated timestamp, and document the risk.

4.4 Log duplicates with a count. A provider sending the same event 4 times usually means your endpoint is timing out.

```sql
CREATE TABLE webhook_events (
  id            bigserial PRIMARY KEY,
  provider      text NOT NULL,
  event_id      text NOT NULL,
  event_type    text NOT NULL,
  payload       jsonb NOT NULL,
  received_at   timestamptz NOT NULL DEFAULT now(),
  processed_at  timestamptz,
  attempts      int NOT NULL DEFAULT 0,
  last_error    text,
  UNIQUE (provider, event_id)
);
```

Gate: sending the same event 5 times creates 1 row and 4 duplicate log lines, with no business side effect.

## Stage 5 - Make the handler idempotent as well as the endpoint

5.1 The endpoint dedupes deliveries; the handler must also be safe if the same business operation runs twice for two different events.

5.2 Use a natural key and an upsert: `INSERT ... ON CONFLICT (payment_id) DO NOTHING` for a credit, or a state check before a transition.

5.3 For money, write a ledger entry keyed by the event id. The key is the receipt that stops the second credit.

5.4 For emails and messages, record a send key per recipient per event before sending.

5.5 Test by running the handler twice on the same event and diffing the tables. A non-empty diff means a retry can double-charge someone.

| Operation | Idempotency mechanism |
|---|---|
| create order | unique order id from payload |
| credit wallet | ledger row keyed by event id |
| send email | send key per recipient per event |
| update status | compare and set with expected current state |
| file write | temp file then atomic rename |

Gate: running the handler twice produces an identical database state.

## Stage 6 - Handle out-of-order events with a version

6.1 Every object event carries a version, `updated_at` or a monotonic sequence. Store the last applied version per object.

6.2 Apply an update only when the incoming version is greater. A late `created` arriving after an `updated` must not overwrite the newer state.

6.3 When a version is missing, fall back to fetching the current object from the provider's API and applying that.

6.4 For events that must be applied in order (ledger, inventory), buffer per object id and process sequentially.

Gate: replaying events in reverse order leaves the object in the same final state as in-order delivery.

## Stage 7 - Retry the processing, not the delivery

7.1 A worker pulls unprocessed rows, marks attempts, and calls the handler.

7.2 Retry on transient errors only: timeouts, 429, 5xx. A 400 or a validation failure is permanent - park it, do not retry it 8 times.

7.3 Backoff 5 s, 25 s, 2 min, 10 min, 1 hour. After 6 attempts, move to a dead-letter state and alert.

7.4 Keep a dead-letter view with the payload, the error and the attempt count, and a one-click replay.

| Attempt | Delay | Then |
|---|---|---|
| 1 | 5 s | retry |
| 2 | 25 s | retry |
| 3 | 2 min | retry |
| 4 | 10 min | retry |
| 5 | 1 hour | retry |
| 6 | - | dead letter and alert |

Gate: a permanently failing event lands in dead letter after 6 attempts with one alert, not 600 log lines.

## Stage 8 - Build the replay tool before you need it

8.1 A CLI or an admin action: replay by event id, by type and date range, or all dead-lettered events.

8.2 Replay resets `processed_at` and `attempts` and enqueues again. It never deletes the row.

8.3 Replays are safe because the handler is idempotent - that is the whole reason stage 5 exists.

8.4 Record who replayed what and when. A replay that changes customer balances needs an audit trail.

```bash
# replay dead-lettered events for one provider since a date
python3 tools/replay.py --provider razorpay --state dead --since 2026-11-01 \
  --dry-run            # prints the count and ids, changes nothing
python3 tools/replay.py --provider razorpay --state dead --since 2026-11-01
```

Gate: replaying 20 dead events ends with 20 processed rows and zero duplicates.

## Stage 9 - Monitor the receiver like a service

9.1 Metrics: events received per minute, duplicates, processing latency p95, dead-letter count, oldest unprocessed age.

9.2 Alert when the oldest unprocessed event is older than 15 minutes, or when dead-letter count rises by 5 in an hour.

9.3 Alert when no events arrive for 2x the usual interval - the sender may have disabled the endpoint.

9.4 Reconcile weekly against the provider's event list or settlement report. Missing events show up there first.

| Signal | Threshold | Meaning |
|---|---|---|
| oldest unprocessed | over 15 min | worker stalled |
| dead letter increase | 5 per hour | a real bug |
| duplicates | over 5% of events | your endpoint is slow |
| no events | 2x normal gap | endpoint disabled or misconfigured |
| reconciliation gap | any | events lost |

Gate: all five signals exist on a dashboard, and one alert has fired in a test.

## Worked example

A Razorpay payment endpoint processing 60,000 events a month inline.

| Item | Before | After |
|---|---|---|
| p99 response time | 4.8 s | 140 ms |
| Provider timeouts per month | 1,900 | 3 |
| Duplicate credits | 22 | 0 |
| Lost events during a 4-hour outage | 340 | 0 |
| Retry storm duration | 2 days | 25 minutes |
| Replay capability | none | by id, type and date |
| Dead letter view | none | with one-click replay |

The 22 duplicate credits all came from the same cause: the endpoint processed inline, the provider timed out at 5 seconds, and the retry ran the credit again. A 140 ms acknowledgement plus a ledger keyed by event id removed the entire class.

## Quality checklist

- [ ] Delivery contract documented per provider
- [ ] HMAC computed over raw bytes, not re-serialised JSON
- [ ] Constant-time comparison used
- [ ] Timestamp window of 5 minutes enforced
- [ ] Two secrets supported for rotation
- [ ] Endpoint does verify, insert and 200 only
- [ ] p99 acknowledgement under 200 ms
- [ ] Unique constraint on provider plus event id
- [ ] Duplicate delivery returns 200 and is logged
- [ ] Handler idempotent with a natural key or ledger row
- [ ] Out-of-order updates guarded by a version
- [ ] Retries on transient errors only, 6 attempts with backoff
- [ ] Dead-letter state with payload and error
- [ ] Replay tool with a dry run and an audit trail
- [ ] Oldest-unprocessed and dead-letter alerts
- [ ] Weekly reconciliation against the provider's list

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Same payment credited twice | Inline processing plus provider retry | Acknowledge fast, ledger keyed by event id |
| Signature valid on a tampered body | HMAC over parsed JSON, not raw bytes | Verify the raw body before parsing |
| Old signature replayed | No timestamp window | Reject anything older than 5 minutes |
| Provider retries for hours | Endpoint slower than the timeout | Move work to a worker, return 200 fast |
| Event lost after a 500 | 200 returned when the insert failed | Return 500 so the provider retries |
| Late event overwrites newer state | No version check | Compare version before applying |
| Retry loop on a validation error | Retrying permanent failures | Classify errors, park 4xx in dead letter |
| Nobody notices a stalled worker | No oldest-unprocessed metric | Alert past 15 minutes |
| Endpoint silently disabled by the provider | No arrival-rate alert | Alert when no events arrive for 2x the gap |
| Replay double-processes | Handler not idempotent | Fix idempotency before enabling replay |

## Copy-ready agent prompt

> Read the skill at the URL above and build a correct webhook receiver. Ask me: which providers send me webhooks, whether they sign requests, my current response time, and whether processing happens inline. Then give me the delivery contract table, the signature verification code over raw bytes with a constant-time compare and a 5-minute window, the fast endpoint that verifies, inserts the raw event and returns 200, the table with a unique constraint on provider and event id, the idempotent handler patterns for money and messages, the version check for out-of-order events, the retry schedule with a dead-letter state, the replay tool with a dry run, and the five monitoring signals with thresholds. Tell me where my current endpoint can double-process and what to change first.
