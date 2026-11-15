---
name: api-rate-limiting
description: Rate-limit an HTTP API with cost-weighted token buckets in Redis,
correct 429 headers, per-plan tiers and a limiter you have load-tested before
it protects anything.
version: 1.0.0
license: MIT
tags: [api, rate-limiting, redis, reliability, backend]
---

# API Rate Limiting

A rate limit has one job: keep one caller's traffic from becoming every
caller's outage. Most implementations fail at that job because they count
requests instead of cost, return a bare 429 with no guidance, and are
themselves slower than the endpoint they protect.

The result here is a limiter with cost units per route, atomic counters in
Redis, headers that tell a client exactly when to retry, per-plan tiers, and a
load test that proves the limiter adds under 5 ms at the 99th percentile.

## When to use this skill

- One integration is sending 60% of your traffic and starving other customers.
- Your API is public or partner-facing and a single key can exhaust a database connection pool.
- You return 429 responses today but clients retry immediately and make it worse.
- An expensive endpoint (report generation, search, export) shares a quota with cheap reads.

Do NOT use for: DDoS absorption at the network edge (that is a CDN and WAF
job), or queue-based backpressure inside a worker fleet — different mechanism,
different numbers.

## Stage 1 — Classify routes and assign a cost

Counting requests rewards cheap endpoints and punishes expensive ones. Count
cost instead.

1.1 Export the top 20 routes by database time from your access log and rank them by p95 latency and rows read.

1.2 Assign a cost unit per route: a cache hit read is 1, a primary-key read is 2, a list with pagination is 5, an export or report is 50.

1.3 Write the table into code so the limit is derived, not remembered:

| Route class | Cost | Limit at 60 units/min | Rationale |
|---|---|---|---|
| `GET /v1/items/{id}` cached | 1 | 60 requests | in-memory read |
| `GET /v1/items` list | 5 | 12 requests | index scan plus serialise |
| `POST /v1/orders` | 10 | 6 requests | write plus downstream call |
| `POST /v1/exports` | 50 | 1 request | background job per call |
| `POST /v1/auth/token` | 20 | 3 requests | bcrypt is deliberately slow |

Gate: every route in the top 20 has a cost unit, and no route costs 0.

## Stage 2 — Choose the algorithm by burst behaviour

The algorithm decides whether a client that has been idle gets a burst. That
is a product decision, not a library choice.

2.1 Use a token bucket when idle clients should be allowed a burst: capacity 60, refill 1 per second, so a quiet client can send 60 at once and then settles to 1 per second.

2.2 Use a sliding window when fairness matters more than burst — partner billing, per-tenant quotas — because a fixed window lets a client send the full quota at 59 seconds and again at 61.

2.3 Avoid a fixed window counter unless the endpoint is cheap; the boundary burst doubles the real rate at the seam.

| Algorithm | State per key | Burst allowed | Use when |
|---|---|---|---|
| Fixed window | 1 integer | up to 2x at the seam | cheap, internal routes |
| Sliding window log | 1 sorted set | no | strict quotas, billing |
| Token bucket | 2 integers | yes, up to capacity | general API default |
| Leaky bucket queue | queue length | no, smooths | protecting a fixed-rate backend |

Gate: the chosen algorithm is written in the route config with its capacity
and refill numbers, and you can say what an idle client's first burst looks
like.

## Stage 3 — Make the counter atomic

A read-then-write counter in application code lets a client exceed the limit
under concurrency, which is exactly when the limit matters.

3.1 Keep the counter in Redis with a Lua script so the read, refill and decrement happen in one atomic step:

```lua
-- KEYS[1] = bucket key, ARGV = now_ms, capacity, refill_per_ms, cost
local b = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(b[1]) or tonumber(ARGV[2])
local ts = tonumber(b[2]) or tonumber(ARGV[1])
local elapsed = math.max(0, tonumber(ARGV[1]) - ts)
tokens = math.min(tonumber(ARGV[2]), tokens + elapsed * tonumber(ARGV[3]))
local allowed = tokens >= tonumber(ARGV[4])
if allowed then tokens = tokens - tonumber(ARGV[4]) end
redis.call('HMSET', KEYS[1], 'tokens', tokens, 'ts', ARGV[1])
redis.call('PEXPIRE', KEYS[1], 120000)
return {allowed and 1 or 0, math.floor(tokens)}
```

3.2 Derive the key from the credential, not the IP: `rl:{plan}:{api_key_id}:{route_class}`, so a customer behind a shared NAT is not throttled by a neighbour.

3.3 Set the key TTL to twice the refill horizon — 120 seconds for a 60-second bucket — so idle keys expire without a sweeper.

Gate: 50 concurrent requests against a capacity of 10 allow exactly 10, proven
by a test rather than by reading the script.

## Stage 4 — Return a 429 a client can act on

A bare 429 causes retry storms. The headers are the contract.

4.1 Return `429` with `Retry-After` in seconds, `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`, on the same response as the error body.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 7
RateLimit-Limit: 60
RateLimit-Remaining: 0
RateLimit-Reset: 7
Content-Type: application/problem+json

{"type":"https://api.yourdomain.in/errors/rate-limited","title":"Rate limit exceeded",
 "detail":"Route class: write. Cost 10 of 60 units per minute. Retry after 7s."}
```

4.2 Name the route class and the cost in the body, so a partner's engineer can fix their client without opening a ticket.

4.3 Send the headers on successful responses too, so a client can pace itself before it is rejected — `RateLimit-Remaining` on a 200 is what makes a good client stay under the limit.

4.4 Never return 200 with an error field, and never return 503 for a rate limit — 503 tells clients the server is broken and triggers their circuit breaker.

Gate: a curl loop shows the three headers on the first 429 and `Retry-After`
counts down correctly on retries.

## Stage 5 — Tier the limits by plan

One global number either throttles your biggest customer or fails to protect
you.

5.1 Set tiers as multiples of a base unit: free 60 units/min, starter 600, business 6,000, enterprise negotiated in a contract field rather than code.

5.2 Read the tier from the API key record with a 60-second cache, so a plan change takes effect within a minute without a deploy.

5.3 Put the tier and the numeric limits in the same key record, so a support engineer can answer "what is my limit" without reading code.

5.4 Give each tier its own burst capacity — 60 units of headroom for business, 10 for free — because the burst is what makes an integration feel fast.

Gate: a key upgraded from free to business shows the new limit within 60
seconds with no restart.

## Stage 6 — Protect the origin with concurrency, not just rate

Rate limits bound throughput per second. A concurrency limit bounds work in
flight, which is what actually protects a database.

6.1 Cap in-flight requests per route class at the worker count times 2 — 40 for a 20-worker service — and queue up to 200 with a 2-second deadline.

6.2 Shed load above the deadline with a 429 and `Retry-After: 2` rather than letting the queue grow; a growing queue turns a slow endpoint into a dead service.

6.3 Log the shed count per route class, because a silent shed and a working limit look identical in latency charts.

6.4 Give health and auth-token routes their own pool, so a saturated export route cannot block logins.

Gate: a 300-request burst against a 40-concurrency limit keeps p99 under 800
ms and rejects rather than queues past 2 seconds.

## Stage 7 — Count once across the edge and the app

Double counting is the most common production bug in rate limiting: the CDN
enforces 60 and the app enforces 60 against a different key.

7.1 Choose one enforcement point for correctness. Use the edge for volumetric protection and the app for cost-based limits, and make the edge limit at least 2x the app limit.

7.2 Pass the client identity from the edge in a signed header, and have the app trust only that header — never a client-supplied one.

7.3 Reconcile the two in a weekly check: count 429s from the edge log and the app log; a large gap means the limits disagree.

Gate: the edge limit is at least twice the app limit, and the app ignores
unsigned identity headers.

## Stage 8 — Instrument the limiter itself

A limiter you cannot see is a limiter you will disable during an incident and
never re-enable.

8.1 Emit three metrics: allowed, rejected and limiter latency, each labelled by plan and route class.

8.2 Alert when the rejection rate for a single plan exceeds 5% of its traffic for 10 minutes — that is usually a broken client, not an attack.

8.3 Watch the Redis dependency: if limiter calls exceed 5 ms at p99 or Redis errors rise, fail open for read routes and closed for writes, and log the decision.

Gate: the dashboard separates legitimate throttling from a failing Redis, and
the fail-open path is tested.

## Stage 9 — Load-test the limiter before trusting it

The limiter runs on every request. If it costs 20 ms, it is the outage.

9.1 Run 10x expected peak through the limiter with a fixed key set and record p50, p95 and p99 added latency.

9.2 Confirm the rejection count matches the arithmetic: 1,000 requests at 100 units/min with cost 1 should allow 100 and reject 900 in the first minute.

9.3 Compare limiter cost against endpoint cost: on a 12 ms cached read, a 5 ms limiter is 40% of the latency and worth a local counter cache; on a 400 ms export it is noise.

9.4 Re-run with Redis at 30% packet loss to prove the fail-open path returns responses instead of hanging.

Gate: limiter adds under 5 ms at p99 and the allowed count matches the
arithmetic within 1%.

## Worked example — a partner integration eating the API

A B2B API with 40 partners and 900 requests per second at peak. One partner's
nightly sync was sending 61% of traffic and pushing p99 for everyone else from
90 ms to 1,400 ms.

| Measurement | Before | After | Change |
|---|---|---|---|
| Peak requests per second | 900 | 900 | unchanged |
| Largest single key share | 61% | 18% | cost-weighted bucket |
| p99 latency, all partners | 1,400 ms | 110 ms | pool no longer saturated |
| 429 responses per hour | 0 | 340 | limiter active and honest |
| Added latency at p99 | — | 1.8 ms | one Lua call per request |
| Partner tickets per week | 6 | 1 | Retry-After respected |

Three decisions carried the result.

Counting cost rather than requests was the first. The sync was calling the
list endpoint, cost 5, 300 times a minute; at 60 units per minute it was over
budget by 25x, and a request counter would have called that within a
300-per-minute limit.

Returning `Retry-After` was the second. The partner's client had a fixed 100
ms retry, which turned every rejection into 10 more requests. After the
header, their library backed off correctly and the rejection count fell by 70%
without any change on their side beyond upgrading the SDK.

The concurrency cap was the third. Rate limiting alone still let 6 export jobs
run at once, each holding a database connection for 4 seconds. Capping exports
at 2 concurrent with a 2-second queue deadline removed the last of the latency
spikes.

The verification that mattered most was the arithmetic check, because it
catches the classic off-by-one in a token bucket:

```bash
# capacity 60, refill 1/s, cost 1, run 200 requests as fast as possible
seq 200 | xargs -P 20 -I{} curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $KEY" https://api.yourdomain.in/v1/items/1 | sort | uniq -c
# expect 60 x 200 and 140 x 429 on the first second
```

## Quality checklist

- [ ] Every top-20 route has a non-zero cost unit.
- [ ] Algorithm, capacity and refill numbers written in route config.
- [ ] Counter updated atomically in one Redis round trip.
- [ ] Key derived from credential id, not IP address.
- [ ] Key TTL set to twice the refill horizon.
- [ ] 429 carries Retry-After and both RateLimit headers.
- [ ] Error body names the route class and cost.
- [ ] Plan tiers read from a cached key record, 60-second TTL.
- [ ] Concurrency limit and queue deadline configured per route class.
- [ ] Edge limit at least 2x the app limit.
- [ ] Allowed, rejected and latency metrics exported by plan.
- [ ] Fail-open for reads and fail-closed for writes tested.
- [ ] Load test shows under 5 ms added at p99.
- [ ] Arithmetic check of allowed count passes within 1%.
- [ ] `RateLimit-*` headers present on 200 responses as well as 429.
- [ ] Plan and limits visible in the key record for support.
## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Client exceeds the limit under load | Read-then-write in application code, not atomic | Move refill and decrement into one Lua script |
| One office is throttled, other customers fine | Key built from IP address behind a shared NAT | Key on API key id and plan |
| Retry storm after the first 429 | No `Retry-After` header, so clients use a 100 ms backoff | Emit `Retry-After` and document it in the error body |
| Limits look right but the database still saturates | Request rate bounded, concurrent expensive work not bounded | Add a concurrency cap and queue deadline per route class |
| Rejections stop after a Redis restart | Counters lost and the fallback allowed everything | Persist nothing, but fail closed for writes and log the event |
| Same key limited twice as fast | Edge and app both counting against different windows | Set edge limit to 2x app limit and pick one enforcement point per rule |
| p99 doubles after enabling the limiter | One Redis round trip per request with no pipelining | Use a single script call, co-locate Redis, cache decisions for 1 second |
| Partner says they never get a 200 | Bucket key includes the route class but the limit is per route | Key on credential plus class, and document the class of each route |
| Limits reset at odd times | Key TTL expires mid-window and the bucket refills to capacity | Set TTL to twice the window and never reset the timestamp on read |
| Two keys share a bucket | Key template omits the credential id for one route class | Assert the key shape in a unit test for every route class |
| 429 on the first request after a deploy | Redis flushed, bucket started empty with cost charged before refill | Seed capacity on miss from the configured capacity, not from zero |

## Copy-ready agent prompt

> Read the skill at the URL above and add rate limiting to my API. Start by ranking the top 20 routes by p95 latency and assigning cost units, then implement a token bucket in a single Redis Lua script keyed on API key id, return 429 with Retry-After and RateLimit headers, and add per-plan tiers cached for 60 seconds. Finish with a concurrency cap per route class and a load test that proves under 5 ms added at p99 and an allowed count within 1% of the arithmetic. Stop and show me the numbers if the limiter adds more than 5 ms.
