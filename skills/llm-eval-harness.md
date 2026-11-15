---
name: llm-eval-harness
description: Build an evaluation harness for an LLM feature - a labelled set, deterministic scorers, a regression gate in CI and a report that says whether the change helped.
version: 1.0.0
license: MIT
tags: [ai, evaluation, llm, testing, ci]
---

# LLM Eval Harness

Shipping an LLM feature without an eval is shipping on vibes. Someone tweaks the system prompt, three examples look better, and a different set of twenty got quietly worse. Nobody notices until a user does, and by then the change is three deploys old and un-revertable by memory.

This skill builds the harness that replaces the vibes: a small labelled set that covers the real inputs, deterministic scorers wherever a rule can decide, a model-graded scorer only where it cannot, a regression gate that fails CI on a drop, and a report that answers one question - did this change help, and by how much.

The number that decides the design: how much a regression may cost. A support-answer feature tolerates a 2% drop in helpfulness; a field extraction feeding invoices tolerates zero.

## When to use this skill

- You are about to change a prompt and cannot say whether it will help.
- Two prompts feel similar and you need to pick one.
- A model upgrade is available and you need a go or no-go.
- Someone asks "how accurate is it" and the answer is currently a shrug.
- **Do NOT use for:** training or fine-tuning a model, benchmarking a model against public leaderboards, or evaluating a feature with no defined output format - this covers your own feature's regression harness.

## Stage 1 - Write the decision the eval supports

An eval with no decision attached grows into a museum. State what a run will decide before you write a scorer.

1.1 Write the question in one line: "does prompt B beat prompt A on our support queries".

1.2 Write the decision rule: ship if exact-match rises by 3 points and no slice drops by more than 1.

1.3 Write the cost of a false pass: what breaks if the eval says yes and the change is bad.

1.4 Write the cost of a false fail: what is lost by rejecting a good change.

1.5 Decide the cadence: every pull request, every model change, or weekly.

1.6 Name the owner who reads the report and can block a release.

Gate: one question, one decision rule, two costs and one named owner.

## Stage 2 - Build the set from real inputs, not from imagination

An eval set written by the person who wrote the prompt tests the prompt's assumptions. Sample from production, or from the source the feature will see.

2.1 Collect 100-300 real inputs, sampled across time and across user segments.

2.2 Label the expected output for each, by hand, with the format the feature actually returns.

2.3 Include the ugly cases: empty input, very long input, wrong language, off-topic, and an adversarial one.

2.4 Add 10% of cases where the correct behaviour is a refusal.

2.5 Split into development and held-out sets, 70/30, and only tune on the development set.

2.6 Freeze the set with a version and a date; adding cases later creates a new baseline.

| Slice | Share | Why it exists |
|---|---|---|
| Common requests | 50% | The average case that must not regress |
| Long or messy input | 20% | Real inputs are not clean |
| Off-topic | 15% | Refusal behaviour |
| Multilingual | 10% | Hindi-English mixed input is common |
| Adversarial | 5% | Prompt injection attempts |

Gate: 100 or more labelled cases, split 70/30, frozen with a version, with every slice populated.

## Stage 3 - Prefer a rule over a judge whenever a rule can decide

Model-graded scoring is noisy, slow and expensive. Use it only where no deterministic check exists, and prove it agrees with a human first.

3.1 Write deterministic scorers for everything checkable: exact match, JSON validity, required keys, numeric tolerance, forbidden strings.

3.2 Use regex or a parser for structured outputs instead of asking a model whether the output is valid.

3.3 Use string similarity only with a threshold you have calibrated on labelled pairs.

3.4 Reserve the model-graded scorer for qualities like helpfulness or tone, with a fixed rubric and a fixed model version.

3.5 Calibrate the judge against 30 human-labelled examples and report the agreement rate.

3.6 Never use the same model that generates the answer as the judge, if you can avoid it.

```python
import json, re

def score_format(out: str) -> float:
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return 0.0
    required = {"answer", "sources", "confidence"}
    return 1.0 if required <= data.keys() else 0.5

def score_refusal(out: str, should_refuse: bool) -> float:
    refused = bool(re.search(r"\b(cannot|unable|not able)\b", out, re.I))
    return 1.0 if refused == should_refuse else 0.0
```

Gate: at least 70% of the cases are scored by a rule, and any model judge has a measured human agreement rate.

## Stage 4 - Make each run reproducible

An eval you cannot reproduce is an anecdote. Pin everything that can change between two runs.

4.1 Pin the model name and version, the temperature, the top-p and the max tokens.

4.2 Pin the prompt version by hash, and store the prompt text with the run.

4.3 Pin the eval set version and the scorer versions.

4.4 Cache model responses per (prompt hash, input hash) so a re-run does not re-spend on unchanged cases.

4.5 Record wall-clock time, token counts and cost per run.

4.6 Store every run as a JSON file with a run id, so two runs can be diffed mechanically.

```json
{
  "run_id": "2026-11-15T09-20-a1",
  "model": "<model>@<version>",
  "temperature": 0,
  "prompt_hash": "8f2c1e",
  "eval_set": "v3",
  "scorers": {"format": "v1", "exact": "v1", "judge": "v2"},
  "cases": 180,
  "metrics": {"exact_match": 0.812, "format_valid": 0.994, "refusal_correct": 0.93},
  "cost_usd": 1.42
}
```

Gate: every run file records model version, prompt hash, eval set version and scorer versions.

## Stage 5 - Report per slice, never only the average

An average hides the slice that broke. The average can rise while the multilingual slice collapses, and that is a ship-blocking change.

5.1 Report each metric overall and per slice, with the case count beside each number.

5.2 Report the confidence interval for each slice, so a 3-case slice is not read as a trend.

5.3 Report the delta against the baseline, with the direction and the magnitude.

5.4 Report the failure list, not only the count - the first five failing cases by id.

5.5 Report cost and latency per case, because a better answer that costs 4x is a different decision.

5.6 Write the one-line verdict at the top: ship, hold, or reject, with the number that decided it.

Gate: every metric has a per-slice breakdown with counts and a delta against the baseline.

## Stage 6 - Set the regression gate

The gate is what makes the harness worth building. Without it, the eval is a dashboard nobody is required to read.

6.1 Set a floor per metric from the current baseline minus an allowed tolerance.

6.2 Set a floor per critical slice, because the average is not the product.

6.3 Fail the build when any floor is breached, and print the failing cases in the CI log.

6.4 Allow an explicit override with a written reason and a named approver, recorded in the commit.

6.5 Keep the gate fast: run a 40-case smoke subset on every pull request, the full set nightly.

6.6 Re-baseline deliberately, with a dated commit, when an intended change moves the numbers.

| Metric | Baseline | Gate floor | Tolerance |
|---|---|---|---|
| Exact match | 0.812 | 0.792 | -2 points |
| Format valid | 0.994 | 0.990 | -0.4 points |
| Refusal correct | 0.930 | 0.910 | -2 points |
| Latency p95 | 1.9 s | 2.3 s | +400 ms |
| Cost per case | $0.0079 | $0.0095 | +20% |

Gate: the gate fails on a breach, the smoke subset runs on every pull request, and the override path is recorded.

## Stage 7 - Compare two changes properly

The comparison is where most eval work goes wrong: two runs on different sets, or a prompt change plus a model change in one run, proves nothing.

7.1 Change one variable per run: prompt, model, retrieval or scorer - never two.

7.2 Run both variants on the same frozen set, same versions, same temperature.

7.3 Run each variant twice and check the variance; a difference smaller than the variance is noise.

7.4 Look at the failing cases that flipped, not only the totals - a flip from wrong to differently wrong is not a win.

7.5 Report the win as a range, not a point estimate, when the case count is under 200.

7.6 Keep the losing variant's run file; the next change often needs it.

Gate: one variable per comparison, the same frozen set, and the variance between repeat runs reported.

## Stage 8 - Wire it into the workflow

The harness has to run where changes happen, not in a notebook someone remembers.

8.1 Add the smoke eval as a CI job on every pull request that touches prompts, model config or retrieval.

8.2 Post the report as a comment on the pull request, with the verdict line at the top.

8.3 Run the full set nightly and store the run file, so drift is visible without a pull request.

8.4 Alert when the nightly metric drops two nights in a row, not on a single night.

8.5 Keep the eval data out of the product database; a separate store with its own versioning.

8.6 Give the owner a one-command way to re-run the full set locally.

Gate: CI runs the smoke set on every prompt change and the nightly full run is stored and alerting.

## Stage 9 - Grow the set from production failures

The set starts at 100 cases and should grow from the failures users actually hit, or it stops representing the product.

9.1 Sample production outputs weekly and label the ones that look wrong.

9.2 Add each real failure to the development set with its label and a note on where it came from.

9.3 Re-baseline after adding cases, in a dated commit, so old and new numbers are not compared blindly.

9.4 Retire cases that no longer reflect the product, but keep them in an archive.

9.5 Track the failure taxonomy - format, factuality, refusal, tone - and the share of each per month.

9.6 Review the taxonomy quarterly and rewrite the rubric if one category dominates.

Gate: at least 5 production failures are added per month, and the set is re-baselined with a dated commit.

## Quality checklist

- [ ] The eval has one written question and one decision rule.
- [ ] The cost of a false pass and a false fail are both written down.
- [ ] The set has 100 or more labelled cases sampled from real inputs.
- [ ] The set is split 70/30 and frozen with a version.
- [ ] Every slice in the plan is populated.
- [ ] At least 70% of cases are scored by a deterministic rule.
- [ ] Any model judge has a measured human agreement rate.
- [ ] Model version, prompt hash and scorer versions are recorded per run.
- [ ] Responses are cached per prompt and input hash.
- [ ] Every metric is reported per slice with case counts.
- [ ] The verdict line names the number that decided it.
- [ ] A gate floor exists per metric and per critical slice.
- [ ] The smoke subset runs on every pull request.
- [ ] One variable changes per comparison run.
- [ ] Production failures are added to the set monthly.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Eval says better, users say worse | Set built from imagined inputs, not production | Resample the set from real traffic and re-baseline |
| Score jumps 10 points between runs | Temperature above 0, or an unpinned model version | Pin the model and set temperature to 0 |
| Two changes landed, no idea which helped | Prompt and model changed in one run | One variable per run, same frozen set |
| Multilingual broke, average looked fine | Only the overall number was reported | Report every metric per slice with counts |
| Judge score disagrees with humans | Judge rubric never calibrated | Calibrate against 30 human labels and publish agreement |
| Eval rots after three months | Set never grew from production failures | Add 5 real failures a month and re-baseline |

## Copy-ready agent prompt

> Read the skill at the URL above and build an eval harness for my LLM feature. Ask me for the feature's output format, a sample of real inputs and the decision the eval must support, then produce the labelled set plan with slices, the deterministic scorers with code, a model judge only where a rule cannot decide, and a run file schema that pins model, prompt hash and set version. Add per-slice reporting with case counts, gate floors per metric and a CI job that runs a smoke subset on every pull request. Finish with the one-line verdict format and the rule for adding production failures. Do not report a metric without its slice and case count.
