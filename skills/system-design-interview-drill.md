---
name: system-design-interview-drill
description: Run a timed 45-minute system design drill that ends with a scored answer, a written design doc and a list of the exact gaps that cost you the round.
version: 1.0.0
license: MIT
tags: [career, interview, system-design, practice, engineering]
---

# System Design Interview Drill

Most candidates prepare system design by reading other people's answers, which trains recognition and not production. In the room you get 45 minutes, a vague prompt, and a whiteboard; what is graded is whether you scope, estimate, draw and defend under time pressure.

This skill turns preparation into a repeatable drill: pick a prompt, run a 45-minute timer split into fixed blocks, write the answer as a design doc, then score it against a 12-point rubric that names what was missing. Ten drills with scoring beats forty hours of reading, and the score sheet is the only honest measure of progress.

## When to use this skill

- You have a system design round in 2-6 weeks and no structured practice.
- You have read 20 design answers and still freeze on the first question.
- You failed a round and the feedback was "not enough depth" with no specifics.
- You are interviewing at 3+ companies and want one practice format that covers all of them.

Do NOT use for: coding rounds, take-home assignments, or salary negotiation (separate skills). It also does not produce answers for a specific company's leaked question bank - practising on a real prompt you will be asked is a different exercise.

## Stage 1 - Set up the drill so it cannot be cheated

1.1 Choose a prompt from a fixed list of 10: URL shortener, rate limiter, news feed, chat, ride matching, file sync, notification service, payments ledger, search autocomplete, video upload.

1.2 Set a hard 45-minute timer with visible countdown. Untimed practice trains writing, not deciding.

1.3 Record the session if you can, screen and voice. The scoring step needs evidence, and memory flatters.

1.4 No notes, no browser, no prior answer open. The drill is a simulation; a simulated drill with references trains nothing.

1.5 Keep a log file with date, prompt, score and the two weakest rubric lines. That log is the progress curve.

```bash
# drill timer - one 45-minute block, announced at each phase boundary
python3 - <<'EOF'
import time
blocks = [("scope and numbers", 6), ("data model", 8), ("diagram", 10),
          ("deep dive", 12), ("reliability", 4), ("summary", 5)]
for name, minutes in blocks:
    print(f"--- {name}: {minutes} min ---", flush=True)
    time.sleep(minutes * 60)
print("STOP - close the answer")
EOF
```

| Prompt | Core difficulty | Good first question |
|---|---|---|
| URL shortener | read-heavy, ID generation | read/write ratio |
| Rate limiter | distributed state | per-user or per-IP |
| News feed | fan-out on write vs read | follower distribution |
| Chat | ordering and delivery | online vs offline delivery |
| Ride matching | geo indexing, state machine | matching latency target |
| File sync | conflict resolution | conflict policy |
| Notification service | retries and dedupe | delivery guarantee |
| Payments ledger | exactly-once, audit | double-spend window |
| Autocomplete | latency budget | freshness requirement |
| Video upload | large objects, resumability | max file size |

Gate: the prompt, the timer and the no-notes rule are set before you speak a word.

## Stage 2 - Spend the first 6 minutes on scope, not on boxes

2.1 Restate the prompt in one sentence with the user and the action: "a user shortens a URL and another user opens it".

2.2 Ask 4-6 clarifying questions and write the answers down. Functional scope first, then scale, then the one non-functional constraint that matters.

2.3 Write the out-of-scope list explicitly. Saying "no analytics, no custom domains" out loud is what senior candidates do, and it buys time.

2.4 Pick the two numbers you will design against: requests per second at peak, and data size per year. Estimate them out loud with round numbers.

```text
Assumptions (URL shortener, 2026)
  writes:   5% of traffic        100 M new links/month  -> ~40 writes/s
  reads:    95% of traffic      2 B redirects/month     -> ~800 reads/s peak 4x = 3.2k/s
  storage:  500 B/link * 100 M  -> 50 GB/month, 600 GB/year
  cache:    20% of daily reads  -> hot set fits in 2 GB
```

2.5 State the latency target in milliseconds. "Redirect p99 under 50 ms" changes the design more than any diagram.

Gate: four numbers on the board - peak QPS, storage per year, cache size, latency target - before any component is drawn.

## Stage 3 - Draw the data model before the architecture

3.1 Name the 3-5 entities and their keys. Most design failures are a missing key, not a missing service.

3.2 Decide the access patterns first: "get link by short code" is the hot path; everything else is secondary.

3.3 Choose the storage type from the access pattern, and say why: key-value for a single-key lookup, relational for a ledger, search index for text.

3.4 Write the sharding key and the reason. A design that never mentions the partition key is incomplete at every level.

| Access pattern | Store | Why |
|---|---|---|
| point lookup by short code | KV or wide-column | single key, sub-10 ms |
| range by time | wide-column or time-series | ordered scan |
| multi-attribute filter | search index | inverted index |
| money movement | relational with constraints | transactions and audit |
| large blobs | object store | cheap, immutable |

Gate: every entity has a key, and every hot path has a named store.

## Stage 4 - Draw one diagram, top to bottom

4.1 Draw left to right: client, edge, load balancer, service, cache, store. One diagram, 8-12 boxes maximum.

4.2 Label each arrow with the protocol and the payload size. An unlabelled arrow is a guess.

4.3 Mark the synchronous calls. A design where everything is synchronous will fail the latency question later.

4.4 Show where the cache sits and what happens on a miss. The cache path is where most follow-up questions land.

4.5 Leave a third of the board empty. You will need it for the deep-dive and for corrections.

Gate: one diagram, every arrow labelled, cache path drawn including the miss.

## Stage 5 - Do the deep dive on the part you were asked about

5.1 Pick the component with the hardest constraint - usually ID generation, ordering, or fan-out - and go two levels deeper than the rest.

5.2 For ID generation, name the scheme and the collision story: base62 of a counter, a random 7-character code with a uniqueness check, or a snowflake ID.

5.3 For fan-out, name the threshold: below 10,000 followers fan out on write, above it fan out on read, and say how a mixed feed merges the two.

5.4 For a ledger, name the idempotency key and the double-entry rule. "Exactly once" without an idempotency key is a claim, not a design.

5.5 Draw the failure path, not only the happy path: what the user sees when the cache is cold and the primary is down.

Gate: the deep-dive component has 2 levels of detail and one failure path.

## Stage 6 - Answer the scale question with arithmetic

6.1 Compute the peak QPS from the assumptions, showing the multiplication. Interviewers check the arithmetic, not the vocabulary.

6.2 Size the storage for one year, then say when you would shard: usually past 1 TB per node or past 10,000 writes/s on one primary.

6.3 Name the bottleneck explicitly: "the write path saturates the primary at about 4,000 writes/s, so we shard by user id at 2,000".

6.4 State what you would measure in production to know the design is holding: p99 latency, cache hit rate, replication lag.

| Metric | Target | Alarm threshold |
|---|---|---|
| p99 read latency | under 50 ms | 120 ms |
| cache hit rate | above 90% | below 75% |
| replication lag | under 1 s | 5 s |
| write error rate | under 0.1% | 1% |
| queue depth | under 1,000 | 10,000 |

Gate: one bottleneck named with a number at which it breaks.

## Stage 7 - Cover reliability in 4 sentences, not 4 minutes

7.1 Name the single point of failure and what happens when it dies.

7.2 Name the retry and idempotency story for the write path.

7.3 Name the data-loss window: how many seconds of writes you would lose in a primary failure.

7.4 Name one monitoring signal per critical path. Four sentences total; spend the remaining time on the deep dive.

Gate: SPOF, retry policy, data-loss window and one alert are each stated in one sentence.

## Stage 8 - Close the loop yourself before time runs out

8.1 At minute 40, stop adding and summarise: what you designed, the two trade-offs you made, and what you would do with another week.

8.2 Say the trade-off out loud with both sides: "fan-out on write gives a 20 ms feed read and a slow post for a celebrity; fan-out on read is the reverse".

8.3 Name what you deliberately did not design, and why. Leaving something out on purpose reads as judgement; leaving it out silently reads as a gap.

8.4 Ask one question back about their actual constraints. It signals that you design against requirements, not templates.

Gate: a 60-second closing summary delivered before the timer ends.

## Stage 9 - Score the answer against the rubric

9.1 Score 12 binary lines within 10 minutes of finishing, while the recording is fresh. Each line is pass or fail, no partial credit.

9.2 For each fail, write the missing sentence verbatim. "I never stated the partition key" is fixable; "not enough depth" is not.

9.3 Mark the two weakest lines and make them the only focus of the next drill.

9.4 Re-drill the same prompt after 3 other drills. Repeating it immediately trains recall, not skill.

| Rubric line | Pass condition |
|---|---|
| Scope stated | one sentence with user and action |
| 4+ clarifying questions | written down before design |
| Out of scope named | at least 2 items |
| Numbers estimated | peak QPS and storage/year |
| Latency target | in ms, one number |
| Data model | entities with keys |
| Partition key | named with reason |
| Diagram | under 12 boxes, arrows labelled |
| Cache path | hit and miss both drawn |
| Deep dive | 2 levels, one failure path |
| Bottleneck | named with a break-point number |
| Closing summary | 60 seconds, trade-offs stated |

Gate: 12 lines scored, and the 2 weakest written as verbatim missing sentences.

## Stage 10 - Convert scores into a preparation plan

10.1 Track the score per drill in the log. A flat score over 3 drills means the practice format is wrong, not the effort.

10.2 Target 9 of 12 before the interview, with no fail on data model, partition key or numbers.

10.3 Drill 3 prompts in the same family (all read-heavy, all write-heavy) before moving family. Depth in one family transfers; breadth without depth does not.

10.4 Do one drill aloud with a friend who interrupts. Interruption handling is half the round and cannot be practised alone.

10.5 Stop drilling 48 hours before the interview and re-read only your own score sheets.

Gate: 6+ drills logged, trend visible, and the two weakest lines closed twice in a row.

## Worked example

Candidate preparing for 3 rounds, 12 days out, drilling one prompt a day.

| Drill | Prompt | Score | Two weakest lines |
|---|---|---|---|
| 1 | URL shortener | 6/12 | partition key, bottleneck |
| 2 | rate limiter | 7/12 | numbers, cache path |
| 3 | news feed | 8/12 | deep dive, closing summary |
| 4 | chat | 9/12 | closing summary, out of scope |
| 5 | payments ledger | 10/12 | none repeated twice |

The score moved 6 to 10 in 5 drills, and every fail became a sentence the candidate now says without prompting: "the partition key is the user id because the hot read is per-user".

## Quality checklist

- [ ] Prompt drawn from a fixed list of 10, not chosen to be easy
- [ ] 45-minute timer visible and respected
- [ ] Session recorded, or at minimum timed notes kept
- [ ] No notes, browser or prior answer open during the drill
- [ ] Scope sentence written in the first 2 minutes
- [ ] 4-6 clarifying questions written before any diagram
- [ ] Out-of-scope list stated aloud
- [ ] Peak QPS, storage per year, cache size and latency target on the board
- [ ] Every entity has a key and every hot path a named store
- [ ] Diagram under 12 boxes with labelled arrows
- [ ] Cache hit and miss paths both drawn
- [ ] Deep dive covers 2 levels and one failure path
- [ ] One bottleneck named with the number at which it breaks
- [ ] Closing summary delivered before the timer
- [ ] 12 rubric lines scored within 10 minutes of finishing
- [ ] Two weakest lines written as verbatim missing sentences

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Runs out of time every drill | Started drawing before scoping | Force 6 minutes on scope and numbers |
| Score stuck at 6-7 for a week | Practising different families each time | Three drills in one family before switching |
| Feedback says "no depth" | Deep dive spread across all components | One component, two levels, one failure path |
| Cannot answer the scale follow-up | Numbers never estimated, only assumed | Put QPS and storage on the board first |
| Design collapses under a follow-up | Partition key never chosen | Name the shard key and the reason in stage 3 |
| Sounds senior but scores low | Vocabulary replacing arithmetic | Show the multiplication out loud |
| Freezes when interrupted | Only practised alone | One drill aloud with a friend who interrupts |
| Improvement feels real but score is flat | No written score sheet | Score 12 lines within 10 minutes of each drill |
| Same prompt repeated until it feels easy | Recall training, not skill | Re-drill after 3 other prompts |
| Diagram unreadable in review | 20 boxes and unlabelled arrows | 12 boxes maximum, every arrow labelled |

## Copy-ready agent prompt

> Read the skill at the URL above and run a system design drill with me today. Pick a prompt from the fixed list of 10, or use the one I name, and act as the interviewer: give me the prompt, then keep me to the 45-minute block structure - 6 minutes of scope and numbers, data model, one diagram, deep dive, reliability in 4 sentences, and a 60-second closing summary. Interrupt me twice with follow-ups the way a real interviewer would. When the timer ends, score me on the 12 rubric lines as pass or fail, and for every fail write the exact sentence I failed to say. Then tell me the two lines to focus on in the next drill and log the score with the date.
