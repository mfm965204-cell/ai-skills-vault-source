---
name: agent-memory-design
description: Give an agent memory that helps: three tiers with a write
policy, retrieval that respects recency and importance, consolidation,
and a deletion path for personal data.
version: 1.0.0
license: MIT
tags: [ai, agents, memory, retrieval, privacy]
---

# Agent Memory Design

An agent without memory asks the same question every session. An agent
with naive memory repeats a stale preference forever, quotes a fact it
invented, and cannot forget a customer who asked to be deleted. Both
are failures of design, not of the model.

This skill defines memory as three tiers with different lifetimes:
working context, episodic history, and durable facts. Each tier has a
write rule, a retrieval rule and an expiry. The output is a schema, a
write policy, a retrieval query and a deletion path you can run.

## When to use this skill

- Your agent forgets a user's stated preference between sessions and asks again.
- The agent confidently repeats something the user said once, three months ago.
- You are storing whole conversations and retrieving them by cosine similarity, and the answers are irrelevant.
- Someone asked you to delete their data and you cannot find every copy.

Do NOT use for: retrieval over a document corpus the user uploaded
(that is a knowledge base with chunking and citations), or fine-tuning
a model on past interactions — different mechanism, different risk.

## Stage 1 — Split memory into three tiers

One store for everything makes every write a permanent decision. Three
tiers with different lifetimes make memory manageable.

1.1 Working memory: the current session's turns, capped at the last 20 messages or 8,000 tokens, summarised when it overflows.

1.2 Episodic memory: one row per session with a summary, the outcome and the timestamp — retrievable, not injected by default.

1.3 Durable facts: short statements about the user or entity with a source, a confidence and an expiry — injected only when relevant.

| Tier | Lifetime | Retrieval | Cost per session |
|---|---|---|---|
| Working | one session | always in context | tokens grow with the conversation |
| Episodic | 90 days | on demand by similarity plus recency | one query per turn at most |
| Durable | until expiry or deletion | injected when the entity is mentioned | small, a few hundred tokens |

Gate: each tier has a lifetime and a retrieval rule, and no tier is
"everything the user ever said".

## Stage 2 — Write to durable memory only on an explicit signal

Most bad memory comes from writing too much. A fact earns a row only
when the user states it as a preference or a constraint.

2.1 Write on explicit statements: "I always want amounts in lakh", "never call before 10 am", "my GSTIN is ...".

2.2 Never write an inference as a fact: "user seems price sensitive" is a guess, and it will be repeated as truth.

2.3 Store five fields per fact: entity, key, value, source turn id, confidence — and a sixth, `expires_at`, defaulting to 180 days.

```json
{
  "entity": "user:8412",
  "key": "currency_display",
  "value": "INR with lakh and crore suffixes",
  "source_turn": "turn_19f2",
  "confidence": 1.0,
  "created_at": "2026-11-15T09:12:00+05:30",
  "expires_at": "2027-05-14T09:12:00+05:30"
}
```

Gate: every durable fact traces to a specific turn, and no fact has a
confidence below 0.6.

## Stage 3 — Retrieve by entity and recency, not similarity alone

Embedding similarity over conversation history returns the most
similar-sounding sentence, which is rarely the most recent or the most
important.

3.1 Filter by entity first — the user id or the account in the current turn — then rank the filtered set.

3.2 Rank by a score that combines recency decay, stated importance and similarity: a 30-day half-life on recency, importance 1 to 3 set at write time.

3.3 Cap the injected memory at 10 facts or 600 tokens, whichever comes first, and log which facts were injected for each turn.

3.4 Score each candidate fact and take the top 10:

```python
def score(fact, now, similarity):
    age_days = (now - fact["created_at"]).days
    recency = 0.5 ** (age_days / 30)              # 30-day half-life
    importance = fact["importance"] / 3           # 1 to 3 at write time
    return 0.5 * similarity + 0.3 * recency + 0.2 * importance
```

Gate: a retrieval test set of 30 queries returns the right fact in the
top 3 for at least 27.

## Stage 4 — Summarise the session into episodic memory

Raw transcripts are expensive to retrieve and full of noise. A session
summary is the useful unit.

4.1 At session end, write one row: what the user wanted, what was decided, what is still open, and the entities touched.

4.2 Cap the summary at 120 words, because a summary that grows to 800 words is a transcript with extra steps.

4.3 Keep the raw transcript only if a legal or quality reason exists, and set its retention separately — 30 days is a working default.

Gate: each session produces one summary row, under 120 words, with
entities extracted.

## Stage 5 — Consolidate instead of accumulating

Two conflicting facts about the same key is the most common memory
bug, and the agent resolves it by guessing.

5.1 On write, look up the existing fact for the same entity and key: newer replaces older, and the old row is marked superseded rather than deleted.

5.2 Merge duplicates weekly: the same key with near-identical values collapses to one row with the latest source.

5.3 Keep a change history for the fact, so a wrong memory can be traced to the turn that introduced it.

Gate: no entity and key pair has two active rows, and every superseded
fact names its replacement.

## Stage 6 — Expire and decay

Memory that never expires becomes wrong by default. Expiry is a
feature.

6.1 Expire durable facts at 180 days unless re-confirmed; a preference stated once and never repeated is a candidate for removal.

6.2 Re-confirm by asking, once, when an expired fact is about to be used: "you asked for lakh format last time — still right?".

6.3 Decay retrieval scores with the same half-life, so an old fact is available but never outranks a recent one.

Gate: expired facts are excluded from injection and appear in a weekly
re-confirmation list.

## Stage 7 — Make deletion real

A deletion request that leaves copies in three stores is a compliance
failure, not a bug.

7.1 Tag every memory row with the subject id, so deletion is one indexed query per store rather than a search.

7.2 Delete from durable and episodic stores, invalidate the retrieval cache, and write a deletion record with the date and the count.

7.3 Never keep "anonymised" conversation logs that still contain the subject id or a free-text name.

Gate: a deletion request removes every row for the subject within 7
days, proven by a query returning zero.

## Stage 8 — Guard against memory poisoning

Anything the agent reads can become a fact if the write policy is
loose, including a web page or a document the user pasted.

8.1 Only write facts from turns authored by the user, never from tool output, retrieved pages or model output.

8.2 Mark any fact derived from third-party content as untrusted and exclude it from injection until a user confirms it.

8.3 Log every write with the source type, and alert on a spike in writes from one session — a sign of an injection attempt.

Gate: no fact from tool output can reach injection without a user turn
that confirms it.

## Stage 9 — Measure memory quality

Memory is a feature with a precision problem: a wrong fact is worse
than no fact.

9.1 Track three numbers: facts injected per turn, facts used correctly (by spot check of 30 turns a week), and contradiction rate.

9.2 Contradiction rate above 1% means the consolidation rule is not running; below that, the write policy is too loose.

9.3 Review the 20 most-injected facts monthly — they shape more answers than any prompt change.

Gate: precision spot check above 90%, contradiction rate under 1%, and
the top 20 facts reviewed monthly.

## Worked example - a support agent that stopped asking twice

A B2B support agent handling 900 conversations a week for an Indian
SaaS.

| Measurement | Before | After | Change |
|---|---|---|---|
| Turns asking for a known detail | 31% | 4% | durable facts injected by entity |
| Facts in store after 4 weeks | 41,000 | 3,100 | explicit-signal write policy |
| Wrong-fact incidents per week | 22 | 2 | supersede on write, expiry at 180 days |
| Injected tokens per turn | 3,800 | 540 | 10-fact cap |
| Deletion requests honoured in 7 days | 40% | 100% | subject id on every row |

The 41,000 facts came from writing an inference after every turn:
"user is on the Pro plan", "user prefers email". Most were wrong
within a month, and the agent repeated them.

The change that fixed both the volume and the accuracy was the write
policy: only explicit user statements, only with a source turn, only
above 0.6 confidence. Fact count fell by 92% and wrong-fact incidents
fell with it.

The retrieval change mattered as much. Similarity-only retrieval kept
surfacing the longest, most detailed conversation rather than the
relevant one; filtering by entity first, then ranking on recency and
importance, cut injected tokens by 86% and improved the answers.

## Quality checklist

- [ ] Three tiers defined with lifetimes and retrieval rules.
- [ ] Working memory capped by messages and tokens.
- [ ] Durable facts written only on explicit user statements.
- [ ] Every fact carries entity, key, value, source turn, confidence, expiry.
- [ ] No fact below 0.6 confidence is stored.
- [ ] Retrieval filters by entity before ranking.
- [ ] Ranking combines recency, importance and similarity.
- [ ] Injection capped at 10 facts or 600 tokens.
- [ ] One session summary row under 120 words.
- [ ] No two active rows for the same entity and key.
- [ ] Facts expire at 180 days with one re-confirmation.
- [ ] Deletion by subject id across every store, logged.
- [ ] Facts from tool output marked untrusted and not injected.
- [ ] Precision spot check above 90% weekly.
- [ ] Top 20 injected facts reviewed monthly.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Agent repeats a preference the user changed | New fact written, old fact still active | Supersede on write and keep one active row per key |
| Agent invents a preference | An inference was written as a fact | Only write explicit user statements with a source turn |
| Retrieved memory is irrelevant | Similarity-only ranking over long transcripts | Filter by entity, then rank on recency and importance |
| Context blows the token budget | Whole conversations injected | Cap injection at 10 facts or 600 tokens |
| Deletion request leaves traces | No subject id on memory rows | Index by subject id and delete per store |
| Agent obeys text found on a web page | Tool output treated as a user turn | Write only from user-authored turns, mark the rest untrusted |
| Memory quality drifts down over months | No expiry, so stale facts accumulate | Expire at 180 days with re-confirmation |
| Agent forgets a fact the user stated twice | A later inference superseded the explicit statement | Only explicit statements write facts, and keep the source turn |
| Fact count grows without bound per account | The expiry job is not running | Schedule expiry at 180 days and alert on fact count per account |

## Copy-ready agent prompt

> Read the skill at the URL above and design memory for my agent. Define working, episodic and durable tiers with lifetimes, write durable facts only from explicit user statements with a source turn and confidence above 0.6, retrieve by entity then rank on recency and importance with a 10-fact cap, summarise each session to under 120 words, and consolidate so one active row exists per entity and key. Add 180-day expiry with re-confirmation, a deletion path by subject id across every store, and untrusted-content marking for anything not authored by the user. Report facts injected per turn, precision spot check and contradiction rate. Stop and show me the schema if any fact lacks a source turn.
