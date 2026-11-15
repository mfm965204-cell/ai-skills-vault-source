---
name: ab-test-analysis
description: Read an A/B test correctly and ship the right decision - hypothesis and one metric, sample size from MDE, randomisation unit and guardrails, a sample-ratio-mismatch check, the statistics, peeking rules, segment analysis and a written decision.
version: 1.0.0
license: MIT
tags: [data, experimentation, statistics, product, analytics, decision]
---

# A/B Test Analysis

Most A/B tests are decided by whoever is loudest in the meeting, using a lift number that was computed after three looks at the data and a sample that was never big enough to detect the effect it was looking for.

This skill makes the decision arithmetic before the test starts: sample size from the minimum detectable effect, a primary metric and guardrails, an SRM check, a fixed analysis point, and a written decision with a confidence interval.

## When to use this skill

- A test ended and the lift is 2% with a p-value of 0.08 and everyone wants to ship it.
- You need to know how long a test must run before you start it.
- Two tests disagree and you suspect one of them was broken.
- A stakeholder wants to stop a test early because it "looks like a winner".

Do NOT use for: observational analysis, cohort studies, or a multivariate test with 12 variants - each of those needs its own design, and a 12-arm test almost always under-powers.

## Stage 1 - Write the hypothesis and pick one metric

1.1 One sentence: "Changing X will move Y by Z for audience A, because W." If you cannot fill in the because, the test is a fishing trip.

1.2 One primary metric, chosen before the test. Two primary metrics means you will report whichever won.

1.3 Guardrail metrics that must not degrade: latency, error rate, refund rate, unsubscribes. A win on the primary with a guardrail breach is a loss.

1.4 State the decision rule in advance: "ship if the primary metric improves with the lower bound of the 95% interval above zero and no guardrail degrades".

1.5 Write down what you expect, with a number. A pre-registered expectation is what stops the post-hoc story.

| Element | Example | Why |
|---|---|---|
| Hypothesis | "A 3-field signup moves activation +5pp because friction is the drop" | testable |
| Primary metric | activation within 24 h | one number |
| Guardrails | signup error rate, p95 latency | protect the business |
| Audience | new users, mobile, India | limits the population |
| MDE | 3 percentage points | sets the sample size |
| Decision rule | CI lower bound above 0 | removes debate |

1.6 Do not test a change you must ship anyway (a legal notice, a bug fix). Use a holdout only if you genuinely need the number.

Gate: a one-page test brief with hypothesis, metric, guardrails and decision rule.

## Stage 2 - Size the sample before you start

2.1 You need four inputs: baseline rate, minimum detectable effect, alpha (0.05) and power (0.80).

2.2 For a proportion, the sample per arm is roughly:

```
n = 16 * p * (1 - p) / (mde)^2        # alpha 0.05, power 0.80, two-sided
```

2.3 Worked: baseline 20%, MDE 2 percentage points absolute, so 16 x 0.2 x 0.8 / 0.0004 = 64,000 per arm.

2.4 The same test at MDE 5 points needs only about 10,000 per arm. A smaller effect costs quadratically more traffic - this is the single most useful fact in experimentation.

| Baseline | MDE (absolute) | Per arm | Total |
|---|---|---|---|
| 5% | 1 pp | 30,400 | 60,800 |
| 5% | 2 pp | 7,600 | 15,200 |
| 20% | 2 pp | 64,000 | 128,000 |
| 20% | 5 pp | 10,240 | 20,480 |
| 40% | 5 pp | 15,360 | 30,720 |

2.5 Convert to duration with your real traffic: 128,000 visitors at 4,000 a day is 32 days, which is probably too long - so either test a bigger change or accept a directional result and say so.

2.6 Use a calculator or a library, not mental arithmetic, for the final number: `statsmodels.stats.power.NormalIndPower` or `proportion_power`.

Gate: sample size per arm computed and the end date written down.

## Stage 3 - Choose the randomisation unit and the assignment

3.1 Randomise the unit that matches the decision: user for retention, session for a page-level change, order for a pricing test.

3.2 Never randomise by request for anything a user can see twice. A user who sees two variants is contaminated and the comparison is broken.

3.3 Keep assignment sticky with a hash of `user_id` and the experiment key, so the same user always lands in the same arm.

3.4 Log the assignment at exposure time, not at analysis time. Recomputing assignment later changes the population.

3.5 If the metric is network-affected (marketplace liquidity, social), use a cluster or switchback design and expect much wider intervals.

3.6 Record the assignment in the same event as the exposure, so the analysis joins on one table rather than reconstructing who saw what.

3.7 Check the assignment hash for bias with a quick uniformity test before trusting a 50/50 split.

| Metric type | Unit | Note |
|---|---|---|
| Click, page view | session | fine, low contamination |
| Signup, activation | user | sticky assignment required |
| Revenue per user | user | watch heavy-tailed outliers |
| Marketplace fill rate | city or time cluster | switchback design |
| Retention | user | needs weeks, not days |

Gate: assignment unit documented, sticky, and logged at exposure.

## Stage 4 - Check the experiment is not broken

4.1 Sample ratio mismatch first: if the split is 50.4/49.6 on 500,000 users, that is not noise, it is a bug.

4.2 Run a chi-square test on the counts. A p-value below 0.001 means SRM; do not analyse the result, find the bug.

4.3 Look for the usual causes: a redirect that drops one arm, a bot filter applied after assignment, an SDK that fails on one variant, a caching layer serving one version.

4.4 Check that the pre-period metrics are balanced: last week's sessions, device mix, country mix. A difference there means assignment is not random.

4.5 Check the metric definition did not change mid-test. A dashboard edit on day 4 invalidates days 1-3.

| Pre-period check | Pass condition | Typical bug if it fails |
|---|---|---|
| Users per arm | within 1% | assignment hash or a redirect |
| Sessions per user | within 2% | one arm loads slower |
| Device mix | within 1 pp | mobile redirect differs |
| Country mix | within 1 pp | geo routing |
| Baseline conversion | within 0.5 pp | bot filtering after assignment |
| Error rate | equal | variant throws on old clients |

```python
from scipy.stats import chisquare
n_a, n_b = 249_120, 250_880
chi2, p = chisquare([n_a, n_b])
print(f"SRM p={p:.2e}")   # p < 0.001 means the split is broken, not unlucky
```

Gate: SRM p above 0.001, pre-period metrics balanced within 1%.

## Stage 5 - Run long enough

5.1 Run at least 7 full days, and at least 2 full weeks for anything involving weekly behaviour. Day-of-week effects are real and large.

5.2 Do not stop when significance appears. Peeking inflates false positives; a test checked daily at alpha 0.05 can hit 20-30% false positive rates.

5.3 If you must look early, use a sequential test or an alpha-spending plan, and say which one in the brief.

5.4 Finish on a pre-committed date, not on a feeling. Write the end date in the brief on day one.

5.5 Novelty effects are real: a new colour gets attention for a week. Two weeks separates a novelty bump from a behaviour change.

5.6 Check the daily series, not just the total: a lift that decays from +8% to +1% across 14 days is a novelty effect, and the total will still look positive.

5.7 If the daily series is unstable, look for an external event - a sale, an outage, a holiday - before concluding anything about the variant.

Gate: ran to the planned date, no early stopping without a sequential plan.

## Stage 6 - Compute the result

6.1 Report the absolute difference, the relative lift, the 95% confidence interval and the p-value. A lift without an interval is an opinion.

6.2 For a proportion, use a two-proportion z-test with an unpooled variance for the interval:

```python
import math
from scipy.stats import norm
def two_prop(a_succ, a_n, b_succ, b_n, alpha=0.05):
    pa, pb = a_succ / a_n, b_succ / b_n
    diff = pb - pa
    se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
    z = diff / se
    p = 2 * (1 - norm.cdf(abs(z)))
    zc = norm.ppf(1 - alpha / 2)
    return {"abs_diff": diff, "rel_lift": diff / pa, "ci": (diff - zc * se, diff + zc * se),
            "z": z, "p": p}
print(two_prop(9_400, 50_000, 9_900, 50_000))
```

6.3 For a continuous metric like revenue, use a t-test on the mean, and check for outliers - one ₹5 lakh order can move a revenue test.

6.4 For a ratio metric (clicks per session), use a delta method or bootstrap; a naive ratio test understates the variance.

6.5 Report the number of users, not the number of events, in the denominator. Events per user is not a sample size.

Gate: a result table with absolute effect, relative lift, 95% interval and p-value.

## Stage 7 - Decide without fooling yourself

7.1 Judge on the interval, not the p-value. If the interval spans both a meaningful gain and a meaningful loss, the test is inconclusive and that is a legitimate answer.

7.2 A p-value of 0.06 on a well-run test with a pre-registered metric is not a licence to ship, and it is not proof of nothing either - report the interval and the decision you are making with it.

7.3 Distinguish statistical significance from practical significance. A 0.2% lift at 2 million users is real and probably not worth the maintenance cost.

7.4 Check guardrails before shipping, even on a clear win.

7.5 Write the decision down: ship, do not ship, or run a bigger test, with the number that drove it.

| Result | Interval | Decision |
|---|---|---|
| Lift +4%, CI [+2%, +6%] | excludes zero, meaningful | ship |
| Lift +1%, CI [-1%, +3%] | spans zero | inconclusive, do not ship on this evidence |
| Lift 0%, CI [-0.5%, +0.5%] | tight around zero | confidently no effect, move on |
| Lift +6%, CI [+1%, +11%], guardrail worse | win with a cost | fix the guardrail, then ship |
| Lift -3%, CI [-5%, -1%] | clear loss | revert, write down why |

7.6 Log the decision and the effect size, so the next test in that area starts from evidence instead of a hunch.

7.7 Ask what the test cost: two weeks of engineering plus the opportunity cost of the traffic. A 0.3% lift that took three weeks is a decision about priorities, not statistics.

7.8 If the decision is inconclusive, say so in the write-up and name the sample size that would settle it. "Inconclusive, needs 3x traffic" is a real result.

Gate: decision written with the interval that justified it.

## Stage 8 - Analyse segments carefully

8.1 Pre-specify at most 3 segments: device, new versus returning, or one geography. Every extra cut multiplies the false positive rate.

8.2 With 3 pre-specified segments you are running 3 extra tests; apply a Bonferroni correction (alpha 0.0167) or treat segment results as hypotheses, not findings.

8.3 Never report a segment win as the headline result after the overall test was flat. That is how a product ships a change that helps 4% of users and hurts the rest.

8.4 Check that segment effects are plausible, not just significant. A win only on Tuesdays is a bug, not a segment.

8.5 Use segment analysis to form the next hypothesis, and test it as its own experiment.

8.6 Report the segment counts. A "win" on 340 users in one segment is not a finding, whatever the p-value says.

8.7 Prefer one strong segment hypothesis over six weak ones; the second experiment is cheaper than the sixth post-hoc cut.

Gate: segment cuts pre-specified, corrections applied, no headline from a subgroup.

## Stage 9 - Write it up so it is reusable

9.1 One page per test: hypothesis, design, sample, dates, primary result with interval, guardrails, decision, and one line on what you would test next.

9.2 Include the losing tests. A register of what did not work is worth more than a folder of wins.

9.3 Note the estimated effect size and the MDE, so a future test can be sized from real data.

9.4 Store the assignment data and the analysis script with the write-up. A result nobody can reproduce is folklore.

9.5 Review the register quarterly and look for a pattern: a metric that never moves, or a segment that always wins.

Gate: a one-page write-up and a row in the register.

## Stage 10 - Build the habit

10.1 Cap concurrent tests to avoid interaction effects; if two tests touch the same surface, run them sequentially.

10.2 Keep one holdout group for a quarter if you are stacking many wins - the sum of many small wins is not always a win.

10.3 Make the metric definitions a shared, versioned file. Half of all test disputes are definition disputes.

10.4 Automate the SRM check and the interval, so nobody hand-computes a lift in a spreadsheet at 11pm.

10.5 Expect 10-20% of tests to be flat and treat that as the cost of learning, not as a failure of the team.

Gate: two or fewer concurrent tests per surface, metric definitions versioned.

## Worked example

A pricing-page test, 14 days, 128,000 users per arm, activation as the primary metric.

| Arm | Users | Activated | Rate |
|---|---|---|---|
| Control | 128,410 | 25,682 | 20.00% |
| Variant | 128,190 | 27,246 | 21.25% |

Absolute lift +1.25 pp, relative +6.3%, 95% CI [+0.99 pp, +1.51 pp], p under 0.001. SRM p = 0.17, so the split is sound. Guardrails flat. Decision: ship.

The same test read on day 4 had shown +2.1 pp, which would have been a 68% overestimate of the real effect - the reason for the fixed end date.

## Quality checklist

- [ ] Hypothesis with a because-clause
- [ ] One primary metric, chosen in advance
- [ ] Guardrail metrics named
- [ ] Decision rule written before launch
- [ ] MDE and baseline recorded
- [ ] Sample size per arm computed, not guessed
- [ ] End date fixed on day one
- [ ] Randomisation unit matches the decision
- [ ] Assignment sticky and logged at exposure
- [ ] SRM check run, p above 0.001
- [ ] Pre-period metrics balanced within 1%
- [ ] Ran 7 full days minimum, 14 for weekly behaviour
- [ ] No peeking without a sequential plan
- [ ] Interval reported with the point estimate
- [ ] Guardrails checked before shipping
- [ ] Segments pre-specified, corrections applied
- [ ] Decision written with the number behind it
- [ ] One-page write-up and a register row

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Test "won" then lost on full rollout | Stopped the test at the first significant day | Fixed end date, or a sequential test |
| 52/48 split on 500,000 users | A bug drops or duplicates one arm | Chi-square SRM check, then debug assignment |
| p = 0.08, team wants to ship | Decision rule written after the result | Judge the interval, and default to not shipping |
| Huge lift in a segment only | 12 segments tested, one is significant by chance | Pre-specify 3 segments, apply a correction |
| Effect vanished in the next test | Metric definition changed between tests | Version the metric definitions |
| Revenue test moved on one order | Heavy-tailed metric analysed with a mean t-test | Winsorise or bootstrap, report the median too |
| Test never reached significance | MDE was smaller than the traffic could detect | Size the sample first, or test a bigger change |
| Two tests disagree | Interaction between concurrent tests on one surface | Run sequentially, keep one holdout |

## Copy-ready agent prompt

> Read the skill at the URL above and design or analyse an A/B test with me. If I am designing: ask for my baseline rate, the smallest effect I care about, my daily traffic and my randomisation unit, then compute the sample per arm and the end date, write the hypothesis, the primary metric, the guardrails and the decision rule. If I am analysing: ask for the counts per arm and the dates, run the SRM check first, then give me the absolute difference, relative lift, 95% confidence interval and p-value, and tell me whether the interval supports shipping. Then the guardrail check, the pre-specified segments, and a one-paragraph write-up with the decision. Do not tell me a result is significant without the interval, and do not invent a benchmark.
