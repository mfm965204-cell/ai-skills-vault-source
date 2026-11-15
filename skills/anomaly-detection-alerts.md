---
name: anomaly-detection-alerts
description: Replace threshold alerts with seasonal baselines that
page only on real anomalies, tuned to a low false-positive rate and
reviewed every month.
version: 1.0.0
license: MIT
tags: [data, monitoring, alerting, statistics, reliability]
---

# Anomaly Detection Alerts

A fixed threshold on a metric with a daily and weekly shape pages
every night at 02:00 and never pages during the outage. The team mutes
it, and the mute is the real failure.

This skill builds alerts that compare a metric with what it normally
does at that hour on that weekday: a seasonal baseline, a stable
spread, an anomaly rule with a false-positive budget, and a monthly
review that deletes rules which never led to an action.

## When to use this skill

- A metric alert fires every night and the on-call engineer has muted the channel.
- Your traffic drops 40% on a holiday and the alert calls it an incident.
- An outage was found by a customer before any alert fired.
- You have 60 alert rules and no idea which 10 are useful.

Do NOT use for: log-based error grouping (that is an error tracker),
or capacity planning forecasts — different method, different horizon.

## Stage 1 — Inventory the metrics and their natural cycles

An anomaly is a deviation from a pattern. You cannot detect one
without knowing the pattern.

1.1 List the metrics that would page a human, and cap the list at 12; anything beyond that belongs on a dashboard.

1.2 Classify each by cycle: hourly (API traffic), daily (signups), weekly (B2B usage), seasonal (festival weeks, financial year end).

1.3 Record the metric's unit, its aggregation window and the smallest change that matters — 5% on revenue, 20% on signups.

| Metric | Cycle | Window | Smallest change worth a page |
|---|---|---|---|
| API requests | hourly plus daily | 5 min | 30% below baseline |
| Payment success rate | daily | 15 min | 3 percentage points |
| Signups | daily plus weekly | 1 hour | 40% below baseline |
| Queue depth | none, bursty | 1 min | above 3x baseline |
| Revenue | weekly plus festival | 1 day | 5% below baseline |

Gate: at most 12 paging metrics, each with a cycle, a window and a
stated sensitivity.

## Stage 2 — Build a seasonal baseline, not a moving average

A 7-day moving average smears the weekend into the weekday. A seasonal
baseline compares like with like.

2.1 For each metric, keep 4 to 8 weeks of history and compute the baseline per slot — same weekday, same hour.

2.2 Use the median rather than the mean, because one incident in the history skews a mean for weeks.

2.3 Require at least 4 observations per slot before the rule can fire; below that, fall back to a wide fixed threshold and say so.

```python
def baseline(series, slot, weeks=8, min_obs=4):
    hist = [v for ts, v in series if slot_of(ts) == slot][-weeks:]
    if len(hist) < min_obs:
        return None                      # not enough history: use fallback threshold
    med = statistics.median(hist)
    mad = statistics.median([abs(x - med) for x in hist]) or 1e-9
    return med, mad                      # median and median absolute deviation
```

Gate: every paging metric has a per-slot baseline with a stated
observation count, and slots under 4 observations use the fallback.

## Stage 3 — Use a stable spread and a defensible band

Standard deviation is dragged by outliers, and outliers are exactly
what you are looking for.

3.1 Use median absolute deviation scaled by 1.4826 as the spread estimate, which is the standard deviation equivalent for a normal distribution.

3.2 Set the band at 3 scaled MADs for paging and 2 for a dashboard warning; a 3-MAD band on a stable metric is roughly 1 expected false positive per 370 observations under normality.

3.3 Clamp the band to a minimum width — 5% of the baseline — so a nearly constant metric cannot page on a rounding difference.

3.4 Apply the band and the guards in one function, so the rule cannot drift between services:

```python
def should_page(value, base, mad, direction="down", hits=0):
    if base is None or hits < 2:
        return False
    band = max(3 * 1.4826 * mad, 0.05 * base)
    return value < base - band if direction == "down" else value > base + band
```

Gate: the band width is stored per metric, and no rule can page on a
change under its stated smallest-worth-paging value.

## Stage 4 — Add direction, duration and seasonality guards

Three guards remove most false positives, and each one is a single
line of logic.

4.1 Direction: page only on the direction that matters — traffic drop, not traffic rise; latency rise, not latency drop.

4.2 Duration: require 2 consecutive windows outside the band, so a single scrape glitch does not page.

4.3 Seasonality: suppress the rule during declared event windows — Diwali week, financial year end, a known marketing push — and log the suppression with an end date.

| Guard | Default | Effect |
|---|---|---|
| Direction | one-sided | halves the false-positive rate |
| Duration | 2 windows | removes scrape and deploy spikes |
| Event calendar | declared windows | removes planned traffic changes |
| Minimum change | 5% of baseline | removes rounding noise |
| History requirement | 4 observations | stops firing on new metrics |

Gate: every rule declares its direction, its consecutive-window count,
and its event suppression.

## Stage 5 — Budget the false positives

A pager that cries twice a night is a pager nobody trusts. Set the
budget in numbers.

5.1 Target under 2 pages per week per team that are not actionable; measure the actual number from the acknowledgement log.

5.2 Tune sensitivity per metric against the budget: raise the MAD multiplier for the noisy ones rather than deleting the rule.

5.3 Track precision — pages that led to an action divided by pages sent — and treat anything under 50% as a rule to fix.

Gate: pages per week and precision are measured, and every rule with
precision under 50% has an owner and a fix date.

## Stage 6 — Route and group so one incident is one page

Alert grouping is the difference between one page and forty.

6.1 Group by service and root metric, so 40 pod-level alerts become one page naming the service.

6.2 Attach the baseline, the current value, the band and a link to the dashboard in the page body; a page without the baseline cannot be judged.

6.3 Route by owning team from the same routing table the ops bot uses, with one fallback channel.

Gate: a simulated 40-pod failure produces one page, containing the
baseline and the current value.

## Stage 7 — Distinguish a data gap from a real zero

The most dangerous false negative is the metric that stopped reporting
and reads as zero.

7.1 Alert on missing data as its own rule: no points in the window means unknown, not healthy.

7.2 Mark gaps explicitly in the store rather than interpolating, and let the anomaly rule skip gaps instead of treating them as zeros.

7.3 Test the rule with the metric switched off, which is the one failure mode no threshold catches.

Gate: stopping the metric produces a data-gap page within 2 windows,
distinct from an anomaly page.

## Stage 8 — Review monthly and delete rules

Alert rules accumulate like unused subscriptions. Review is the
mechanism that keeps the pager meaningful.

8.1 For each rule, count pages in 30 days and actions taken; delete any rule with zero actions in 30 days.

8.2 Re-derive the baseline window quarterly — a metric whose cycle changed needs a new slot definition.

8.3 Keep a one-line reason per rule, because a rule with no reason cannot be defended when someone wants it gone.

Gate: every rule has a 30-day action count and a written reason, and
zero-action rules are deleted.

## Stage 9 — Backtest before you trust it

A rule that has never been run against history is a guess with a cron
schedule.

9.1 Replay 8 weeks of history through the rule and count pages it would have sent.

9.2 Check that it would have caught the last 3 real incidents, with the lead time before the customer noticed.

9.3 Tune the multiplier until the backtest meets the budget, then deploy and compare the live count with the backtest.

Gate: backtest pages per week within 50% of the live count after two
weeks.

## Worked example - 380 pages a month to 9

A payments platform with 41 threshold rules on 9 services.

| Measurement | Before | After | Change |
|---|---|---|---|
| Pages per month | 380 | 9 | seasonal baselines, 12 metrics |
| Precision (page led to action) | 11% | 78% | direction and duration guards |
| Night pages (00:00-06:00 IST) | 96 | 2 | event calendar and MAD tuning |
| Incidents found by customer first | 4 per quarter | 1 | data-gap rule plus success-rate rule |
| Rules | 41 | 12 | delete zero-action rules |
| Mean time to acknowledge | 14 min | 4 min | one page per incident |

The biggest single removal was a rule on "API requests below 80% of
the 1-hour average" that fired every night at 01:00 because traffic
drops 55% after midnight. A seasonal baseline on the same metric, with
a one-sided band at 3 MADs, fired twice in the next month, both real.

The incident found by a customer was a payment success rate that fell
from 96% to 71% over 40 minutes while traffic stayed normal. No
threshold caught it because 71% is not below 70%. A per-slot baseline
on success rate, with a 3-percentage-point minimum change, would have
paged at the 12-minute mark.

The lesson on the backtest: the first version of the queue-depth rule
would have sent 60 pages in 8 weeks of replay, all during known batch
windows. Adding the event calendar and a 2-window duration requirement
took it to 3.

## Quality checklist

- [ ] At most 12 paging metrics, each with a stated unit and window.
- [ ] Cycle classified per metric.
- [ ] Per-slot seasonal baseline from at least 4 weeks of history.
- [ ] Median and MAD used, not mean and standard deviation.
- [ ] Band width has a minimum of 5% of baseline.
- [ ] Direction declared per rule.
- [ ] Two consecutive windows required before paging.
- [ ] Event calendar suppression with an end date.
- [ ] False-positive budget under 2 pages per week per team.
- [ ] Precision measured and above 50% per rule.
- [ ] Alerts grouped so one incident is one page.
- [ ] Page body carries baseline, current value and band.
- [ ] Data-gap rule distinct from anomaly rule.
- [ ] Zero-action rules deleted at the monthly review.
- [ ] Backtest run against 8 weeks before deployment.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Alert fires every night at the same hour | Fixed threshold on a metric with a daily cycle | Move to a per-slot baseline and a one-sided band |
| Alert fires on a holiday | No event calendar, so the baseline is weekday traffic | Declare event windows and suppress with an end date |
| Outage with no alert | A threshold below the observed value, so a real drop stays inside it | Use a relative band with a minimum change, not a fixed floor |
| Metric stops reporting and looks healthy | Missing data read as zero | Add a data-gap rule and skip gaps in the anomaly rule |
| 40 pages for one incident | Per-pod rules with no grouping | Group by service and root metric |
| Team mutes the channel | Precision under 50%, so most pages need no action | Raise the multiplier, add direction, delete zero-action rules |
| Backtest clean, live noisy | Backtest used a stable period; live includes deploys | Include deploy windows in the backtest history |

## Copy-ready agent prompt

> Read the skill at the URL above and replace my threshold alerts. Cap paging metrics at 12, classify each cycle, build a per-slot seasonal baseline with median and scaled MAD, add direction, two-window duration and event-calendar guards, and add a data-gap rule. Group alerts so one incident is one page, attach the baseline and band to every page, then backtest against 8 weeks of history and report pages per week, precision and night pages before and after. Stop and show me the backtest if pages per week exceed 2 per team.
