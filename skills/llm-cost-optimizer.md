---
name: llm-cost-optimizer
description: Cut the cost of an LLM feature by 40-80% without a quality drop - measure tokens per request, attribute the waste, trim prompts, route by difficulty, cache, and gate every change behind an eval.
version: 1.0.0
license: MIT
tags: [ai, cost, tokens, caching, routing, evals]
---

# LLM Cost Optimizer

Most LLM bills are not a pricing problem, they are a token problem: a 1,200-token system prompt re-sent on every turn, six turns of history where two mattered, 8 retrieved chunks when the answer lived in the first, and an output that rambles for 400 tokens to say 60.

This skill turns the bill into a number you control. You finish with a cost sheet showing cost per request before and after, the eval score on both sides, and a rollback switch for each change.

## When to use this skill

- The monthly LLM bill grew faster than usage, and nobody can say which endpoint caused it.
- A feature is profitable at 1,000 requests a day and unprofitable at 20,000.
- You are about to raise prices or drop a feature because of inference cost.
- You inherited a prompt nobody has trimmed since launch.

Do NOT use for: choosing a provider on price alone (run a quality eval first), or hiding cost by silently shortening answers users rely on. Cost work that degrades quality is a loss, not a saving.

## Stage 1 - Measure the real cost per request

1.1 Instrument every call with five fields: route name, model, input tokens, output tokens, latency. Write one row per call to a table or a log line, never to memory.

1.2 Compute cost per request with your own rate card, not from the dashboard:

```
cost = (input_tokens / 1_000_000) * input_rate + (output_tokens / 1_000_000) * output_rate
```

1.3 Use the rate card table below and fill the middle column from your provider's current page. The worked example in this skill uses $0.50 per 1M input and $1.50 per 1M output purely as arithmetic - substitute your real numbers.

| Line item | Your rate | Used in examples |
|---|---|---|
| Input tokens per 1M | fill in | $0.50 |
| Output tokens per 1M | fill in | $1.50 |
| Cached input per 1M | fill in | $0.05 |
| Embedding per 1M | fill in | $0.02 |
| Per-request floor (min billed) | fill in | 0 |

1.4 Report three numbers per route, not one: cost per request at p50, at p95, and daily total. The p95 request is usually 3-6x the p50 and it is where the budget dies.

1.5 Convert to rupees for the invoice owner: at ₹88 to the dollar (use today's rate), $0.012 per request at 30,000 requests a day is ₹31,680 a month. A number in ₹ gets acted on; a number in tokens does not.

1.6 Wrap the client once so instrumentation cannot be forgotten. One decorator, applied at the call site, is the difference between a cost sheet and a guess:

```python
import time, logging
from functools import wraps

log = logging.getLogger("llmcost")
IN_RATE, OUT_RATE = 0.50, 1.50  # dollars per 1M tokens - your card

def metered(route):
    def deco(fn):
        @wraps(fn)
        def inner(prompt, **kw):
            t0 = time.perf_counter()
            resp = fn(prompt, **kw)
            u = resp.usage
            cost = u.input_tokens / 1e6 * IN_RATE + u.output_tokens / 1e6 * OUT_RATE
            log.info("route=%s model=%s in=%d out=%d ms=%d usd=%.6f",
                     route, resp.model, u.input_tokens, u.output_tokens,
                     int((time.perf_counter() - t0) * 1000), cost)
            return resp
        return inner
    return deco
```

1.7 Log the route name as a string constant, never as a f-string built at runtime, so you can group by route in one query.

1.8 Backfill a week of history from provider logs if instrumentation arrives late; a baseline you cannot compare against makes every later claim unverifiable.

Gate: you can name the top 3 routes by daily spend and the cost of one average request on each.

## Stage 2 - Attribute the tokens

2.1 Break each request into four buckets and log the token count of each separately: system prompt, conversation history, retrieved context, user message. Do this for 50 real requests before changing anything.

2.2 Sum the buckets. A typical untuned chat route looks like this - if your numbers are close, the fixes are known:

| Bucket | Untuned | Healthy target | Share of waste |
|---|---|---|---|
| System prompt | 1,200 | 300-500 | 40-60% |
| History | 2,400 | 600-900 | 20-35% |
| Retrieved context | 2,000 | 500-800 | 15-30% |
| User message | 60 | 60 | 0% |
| Output | 380 | 120-200 | 20-40% |

2.3 Rank the buckets by absolute tokens, not by percentage. A 90% cut on a 60-token bucket saves nothing.

2.4 Write the finding as one sentence with numbers: "the system prompt is 1,200 of 5,660 input tokens on every one of 30,000 daily requests, which is $0.018 per request or ₹47,520 a month".

Gate: a table of buckets with token counts and a ranked list of the three largest.

## Stage 3 - Trim the static prompt

3.1 Count the sections of the system prompt and their token cost. Measure with a tokeniser, not by counting words - code and JSON tokenise 30-60% denser than prose.

3.2 Delete anything the model already knows: "you are a helpful assistant", politeness instructions, restatements of the task, and examples of behaviour the schema already enforces.

3.3 Move rules that apply to one tool into that tool's description instead of the global prompt. Tool descriptions are only paid for when tools are attached, and they sit after the cacheable prefix.

3.4 Convert prose policy into a short list. A 300-word paragraph of tone rules becomes 8 bullets of 12 words each, at roughly 40% of the tokens.

3.5 Keep the few-shot examples only if removing them costs more than 3 points on your eval. Test removal one example at a time; the third example usually earns nothing.

3.6 Merge duplicated rules. A prompt that says "be concise" in the intro, the middle and the footer pays three times for one instruction.

3.7 Compress the style guide into a table row per rule. Tables tokenise well and the model follows them more reliably than paragraphs.

3.8 Re-measure. A prompt cut from 1,200 to 420 tokens saves 780 tokens per call, which on 30,000 calls a day is 23.4M tokens a month.

Gate: prompt under 500 tokens, eval score within 2 points of baseline.

## Stage 4 - Cap the history window

4.1 Stop sending the whole conversation. Send the last N turns plus a rolling summary of everything older.

4.2 Use the window table as the starting point and tune against your eval set:

| Route | Turns kept verbatim | Summary budget | Hard cap |
|---|---|---|---|
| Support chat | 4 | 150 tokens | 1,200 |
| Coding assistant | 6 | 300 tokens | 2,000 |
| Document Q&A | 2 | 0 | 800 |
| Long-running agent | 8 | 500 tokens | 3,000 |

4.3 Truncate by dropping the oldest turn first, and never drop the turn that contains the user's original constraint. Pin messages marked as constraints.

4.4 Compress tool results before they enter history: a 2,000-token API response becomes a 200-token extract of the fields the next step needs.

4.5 Summarise every 6 turns with the cheapest model that passes your eval, and store the summary, not the transcript.

Gate: history bucket under 900 tokens on the support route at turn 10.

## Stage 5 - Trim retrieval before it enters the prompt

5.1 Measure the hit rate of your top-k: for 50 answered questions, record whether the answer sentence was in chunk 1, 2, 3 or later. If 80% of answers sit in the first 2 chunks, k=3 is enough.

5.2 Set k by route and never above 5. Each 500-token chunk costs 0.5k tokens on every request; k=8 versus k=3 is 2,500 wasted tokens per call.

5.3 Deduplicate chunks with a similarity threshold of 0.95 and drop chunks below a relevance score you set from the same 50-question set.

5.4 Pass the chunk's title and one metadata line, not the whole header block. Keep the citation id, drop the boilerplate.

5.5 If the answer needs the whole document, do a two-step call: cheap model picks the page, second call reads only that page.

5.6 Cache the embedding of each chunk, not the query, and re-embed only when the source document changes. Re-embedding a 20,000-chunk corpus weekly is a cost line nobody budgets for.

5.7 If a route answers from a fixed corpus of under 50 pages, embed the whole corpus once and let the model read a 4,000-token extract instead of retrieving - fewer moving parts and often cheaper than five round trips.

Gate: average retrieved context under 800 tokens with no drop in answer correctness on the 50-question set.

## Stage 6 - Route by difficulty

6.1 Classify each request into one of three tiers before the main call. Use a 10-token classifier prompt or a keyword rule - not a second large model.

| Tier | Share of traffic | Model class | Example jobs |
|---|---|---|---|
| T1 | 55-70% | small, fast | classification, extraction, formatting, short answers |
| T2 | 25-35% | mid | multi-step reasoning over one document |
| T3 | 5-10% | large | planning, code generation, ambiguous requests |

6.2 Write the router as configuration so it can be changed without a deploy:

```json
{
  "routes": {
    "classify":  {"tier": "T1", "max_output_tokens": 40, "temperature": 0},
    "extract":   {"tier": "T1", "max_output_tokens": 300, "temperature": 0},
    "support":   {"tier": "T2", "max_output_tokens": 250, "temperature": 0.3},
    "plan":      {"tier": "T3", "max_output_tokens": 900, "temperature": 0.2}
  },
  "escalate_to_T3_if": ["tool_calls > 3", "user_says_complaint", "tier2_confidence < 0.6"]
}
```

6.3 Log the tier on every call so you can audit misroutes weekly. A T3 route that is 30% of traffic means the classifier is lazy.

6.4 Add one escalation path: if the T1 answer fails a schema check, retry once on T2 rather than sending T1 three times.

6.5 Measure the tier boundary monthly on 200 labelled samples. A classifier that drifts 5 points toward T3 costs more than the prompt bloat you removed.

6.6 Never route on the length of the user message alone; a 12-word question about tax law needs T3 more than a 400-word pasted email needs T1.

Gate: T1 share above 50% and eval score unchanged.

## Stage 7 - Cache at three levels

7.1 Exact cache: hash the normalised prompt (lowercase, whitespace collapsed, volatile ids stripped) and store the response with a 24-hour TTL. Typical hit rate on support traffic is 8-25% (estimate, measure yours).

7.2 Prefix cache: put everything static first - system prompt, tool schemas, style guide - and the volatile part last. Providers bill cached input at 10-25% of the normal rate; a stable 800-token prefix is the cheapest 800 tokens you own.

7.3 Semantic cache: embed the user message, look up the nearest stored question, and serve the cached answer only above a 0.95 cosine threshold. Below 0.95 the answer drifts into wrong territory; keep a 0.90-0.95 band that logs but does not serve.

| Cache | Key | TTL | Serve threshold | Expected hit rate |
|---|---|---|---|---|
| Exact | hash of prompt | 24 h | exact match | 8-25% |
| Prefix | static block order | provider-managed | n/a | 60-90% of input |
| Semantic | embedding | 7 days | 0.95 cosine | 5-15% |
| Negative | hash of failed call | 10 min | exact match | 1-3% |

7.4 Never cache personalised answers across users. Key the cache on user id when the answer contains account data.

Gate: measured hit rate recorded per cache layer, and no cache key that mixes two users.

## Stage 8 - Control the output

8.1 Set max_output_tokens per route from the p95 of your good answers, not from the provider default. A support reply that averages 140 tokens gets a cap of 220.

8.2 Add stop sequences for formats: `\n\n`, `</answer>`, `###`. Output tokens cost 3-5x input tokens at most providers, so the output is where a small cut pays most.

8.3 Ask for JSON with a schema and short keys. Rename `customer_complaint_summary` to `sum` in the schema and the model follows; on 30,000 calls a day that is 8 tokens per call.

8.4 Ban preamble in the instruction ("no greeting, no restating the question") - it removes 20-60 tokens per call for free.

8.5 Batch classification jobs: 200 short items in one call cost far less than 200 calls, provided the schema stays parseable.

8.6 Turn on structured decoding where the provider supports it. Constrained JSON cuts both invalid retries and trailing commentary, and retries are the hidden 15-30% of a naive bill.

8.7 Log the truncation rate per route. More than 2% of responses hitting `max_output_tokens` means the cap is too tight and users are getting cut answers - a quality bug that looks like a saving.

8.8 Measure tokens per resolved task, not tokens per call. A cheap call that fails and gets retried costs more than an expensive call that works first time.

Gate: average output tokens down 30% or more with the eval unchanged.

## Stage 9 - Prove it with an eval, then ship

9.1 Freeze a 60-item eval set: 20 easy, 30 typical, 10 adversarial, each with an expected answer or a rubric. Keep it in a file next to the code.

9.2 Score every change with the same judge: exact match for extraction, rubric 1-5 for free text, and a human read of 10 items per change.

9.3 Ship one lever at a time. Two changes in one deploy and you cannot attribute the 4-point regression.

9.4 Put the cost number in CI: fail the build if cost per request rises more than 10% against the last main branch run.

9.5 Keep a `cost.md` with a row per change: date, lever, cost before, cost after, eval before, eval after, who approved.

Gate: all shipped levers have a row in `cost.md` and an eval delta of 2 points or better.

## Stage 10 - Monitor and set a budget alarm

10.1 Alert on cost per request, not on total spend - total spend tracks traffic and hides regressions.

10.2 Set three alarms: daily spend above 1.3x the 7-day average, cost per request up 20% week over week, and any route whose p95 input tokens doubled.

10.3 Review the top 20 most expensive requests every Friday. They are usually one bug: a retry loop, a document pasted twice, or a tool result echoed back into the prompt.

10.4 Re-run this skill quarterly; prompts grow back.

Gate: three alarms live and one named owner.

## Worked example

A support assistant on 30,000 requests a day. Baseline: 5,660 input tokens, 380 output tokens, $0.008 per request, ₹21,120 a month.

| Lever | Input after | Output after | $ per request | Monthly ₹ |
|---|---|---|---|---|
| Baseline | 5,660 | 380 | 0.0085 | 21,120 |
| Prompt 1,200 to 420 | 4,880 | 380 | 0.0078 | 19,400 |
| History cap 900 | 3,380 | 380 | 0.0063 | 15,600 |
| Retrieval k=3 | 2,180 | 380 | 0.0052 | 13,000 |
| Output cap 220 | 2,180 | 190 | 0.0040 | 9,900 |
| Prefix cache on 800 tokens | 2,180 | 190 | 0.0029 | 7,300 |
| T1 routing on 60% of traffic | 2,180 | 190 | 0.0018 | 4,400 |

Result: ₹4,400 a month, a 79% cut, with the eval moving from 84 to 82 out of 100. Every number above is arithmetic on the rates in Stage 1, not a benchmark.

## Second worked example - a coding assistant

A different shape, same levers. 8,000 requests a day, 14,000 input tokens per request because the whole repository context is attached.

| Lever | Effect | Monthly ₹ (at ₹88/$) |
|---|---|---|
| Baseline 14,000 in / 900 out | - | ₹1,05,600 |
| Send the diff plus 3 related files, not 40 | 14,000 to 5,200 | ₹39,200 |
| Cache the repo map as a static prefix | 5,200 to 4,100 billed | ₹31,000 |
| Cap output at 500 tokens with a stop token | 900 to 480 | ₹24,900 |
| T1 model for single-file edits (45% of traffic) | - | ₹14,700 |

Two things matter here: the repository context is the whole cost, and the cache only works if the repo map sits at the very top of the prompt with nothing volatile above it.

## Quality checklist

- [ ] Every route logs input tokens, output tokens, model and latency
- [ ] Cost per request computed from your own rate card
- [ ] Token buckets measured on 50 real requests before any change
- [ ] System prompt under 500 tokens
- [ ] History window capped with a summary budget
- [ ] Retrieval k set from a hit-rate measurement, never above 5
- [ ] Router config lives outside the code
- [ ] Static prompt prefix comes first for prefix caching
- [ ] Semantic cache threshold at 0.95, keyed per user when personal
- [ ] Output caps set from p95 of good answers
- [ ] 60-item eval set frozen and re-run per change
- [ ] One lever per deploy, with a row in cost.md
- [ ] CI fails on a 10% cost regression
- [ ] Alarms on cost per request, not only total spend
- [ ] Monthly ₹ figure reported to whoever owns the invoice
- [ ] Truncation rate under 2% per route
- [ ] Tokens per resolved task tracked, not only per call

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Bill dropped 40% and complaints rose | Quality was never measured, so the regression is invisible | Restore the last good prompt from cost.md and re-cut with the eval running |
| Cache hit rate stuck under 2% | Cache key includes a timestamp or request id | Strip volatile fields before hashing |
| Prefix cache never hits | A dynamic date or user name sits at the top of the prompt | Move all volatile text after the static block |
| Cost per request fine, total spend up 3x | Traffic doubled from a retry loop, not from growth | Cap retries at 2 and log retry reason |
| T1 routing at 5% of traffic | Classifier prompt too cautious, everything escalates | Lower the escalation threshold and re-measure on 200 samples |
| Output tokens unchanged after the cap | The cap is on the wrong route, or the model emits a long preamble first | Set max_output_tokens on the route actually called, and ban preamble |
| Semantic cache serves wrong answers | Threshold at 0.85 | Raise to 0.95 and add the 0.90-0.95 log-only band |
| Eval score stable, users complain | Eval set is too easy and no adversarial items | Add 10 adversarial items from real bad sessions |
| p95 cost 6x p50 | One route receives pasted documents with no length guard | Reject or chunk inputs over 8,000 tokens |
| Spend falls but retries rise | Tighter output caps produce invalid JSON, so the caller retries | Raise the cap on that route or enable structured decoding |
| Two teams, one budget, no owner | Cost is measured per provider key, not per route | Split keys per product and report per route weekly |

## Copy-ready agent prompt

> Read the skill at the URL above and run it on my LLM feature. Start by asking me for my rate card, my daily request count and the routes I have. Then build the token-bucket measurement from 50 real requests, rank the waste, and apply the levers one at a time in this order: prompt trim, history cap, retrieval trim, output cap, prefix cache, routing. After each lever give me cost per request before and after in dollars and rupees, plus the eval delta. Finish with a `cost.md` table, the alarm thresholds, and the CI check that fails on a 10% regression. Never change two levers in one step, and never quote a provider price you have not been given.
