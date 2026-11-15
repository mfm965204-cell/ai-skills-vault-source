---
name: first-90-days-plan
description: Write the 30/60/90 plan that turns a new job into a named deliverable, a stakeholder map and three measured outcomes instead of six months of being useful in meetings.
version: 1.0.0
license: MIT
tags: [career, onboarding, planning, management, first-90-days]
---

# First 90 Days Plan

A new job gives you roughly 90 days of goodwill before people start judging output. Most people spend it on 40 introductions and no deliverable, then discover at month four that nobody can name what they own.

This skill builds the plan before day one: one deliverable per month, a stakeholder map with what each person needs from you, the questions to ask in the first 10 days, and three numbers you will be measured on. You end with a one-page plan you can send your manager in week one - which itself is the first test.

## When to use this skill

- You start a new role in under 3 weeks, in a new company or a new team internally.
- You were promoted and the old peer group is now your report group.
- Your manager said "take the first month to settle in" and you can feel the drift starting.
- You are contracting or consulting for 3 months and need the deliverable defined on day 2.

Do NOT use for: performance reviews of existing work, job hunting, or salary negotiation. It also does not replace the onboarding the company gives you - it sits beside it.

## Stage 1 - Learn the mandate before the org chart

1.1 Write down what your manager thinks you were hired to fix, in their words. Ask directly in the first week; the answer is often different from the job description.

1.2 Ask what would make the next 90 days a success, then ask what would make it a failure. The second question is where the real expectations live.

1.3 Ask who else was considered for the role, or what happened to the person who held it. Both answers explain constraints you cannot see.

1.4 Confirm the decision rights: which calls you make alone, which need a review, which need a signature.

| Question | Why it matters | Red flag answer |
|---|---|---|
| What am I here to fix? | defines the deliverable | "just help out" |
| What would failure look like? | names the real risk | "no pressure" |
| Who decides what? | prevents blocked work | "we all decide" |
| What is broken and tolerated? | reveals sacred cows | "nothing is broken" |
| What happened to the last person? | explains constraints | deflection |

Gate: one sentence in your manager's words for why the role exists, written in your own file.

## Stage 2 - Map stakeholders by what they need, not by seniority

2.1 List 12-15 people who affect your work: direct team, 2 adjacent teams, 1 finance or legal, 1 customer-facing, your manager's manager.

2.2 For each, write one line: what they need from you, what you need from them, and the cost of getting it wrong.

2.3 Classify each as decision-maker, blocker, amplifier or observer. Only 3-4 people will be decision-makers; treat them differently.

2.4 Book 20-minute conversations with the top 8 in the first 10 days, and ask each the same 3 questions so you can compare answers.

2.5 Keep the map in a single table and update it weekly. A stale stakeholder map is worse than none.

| Type | What they do for you | How to work with them |
|---|---|---|
| Decision-maker | approves the direction | short written asks, early |
| Blocker | can stop the work quietly | understand their constraint first |
| Amplifier | repeats your work to others | give them the number, not the story |
| Observer | watches, rarely acts | monthly one-paragraph update |

Gate: 12+ people mapped with a need and a type, top 8 conversations booked.

## Stage 3 - Ask the same 3 questions in every first conversation

3.1 "What is working that I should not break?" - this prevents your first visible mistake.

3.2 "What is broken that nobody has time to fix?" - this is where your first deliverable usually comes from.

3.3 "What would you want from me in 60 days?" - this converts goodwill into a specific ask.

3.4 Write the answers verbatim in one document, grouped by theme. The same complaint from 3 people is a mandate; from 1 person it is an opinion.

3.5 At the end of 10 conversations, pick the theme with the most mentions and the least ownership. That is your month-1 deliverable.

Gate: 10 conversations logged, and the top theme has at least 3 independent mentions.

## Stage 4 - Choose one deliverable per month, not a list

4.1 Month 1: a small, visible, low-risk fix - a report nobody trusts, a broken handover, a slow query. It buys credibility.

4.2 Month 2: one owned system or process, with a named metric and a baseline you measured yourself.

4.3 Month 3: one improvement with a number attached, delivered and documented so someone else can run it.

4.4 Each deliverable gets a definition of done, a date, and one person who will notice it shipped.

4.5 Refuse a fourth deliverable in month 1. Accepting everything is how the 90 days produce nothing finished.

| Month | Type | Example | Definition of done |
|---|---|---|---|
| 1 | visible fix | invoice report reconciled to the rupee | used by finance once |
| 2 | owned system | deploy pipeline with a runbook | 5 deploys with no manual step |
| 3 | measured improvement | p95 latency 900 to 400 ms | one week at target |

Gate: exactly 3 deliverables, each with a date, a metric and a named observer.

## Stage 5 - Write the baseline before you change anything

5.1 Measure the current state of your month-2 system in week 2: volume, error rate, latency, cost, time spent.

5.2 Save the numbers in a dated file. Without a baseline, month 3 has no improvement - only opinion.

5.3 Note how the number is produced, so a later change in method is visible rather than silent.

5.4 If no measurement exists, the measurement is the month-2 deliverable.

```sql
-- baseline for an order pipeline, run before any change
SELECT date_trunc('day', created_at) AS day,
       count(*) AS orders,
       count(*) FILTER (WHERE status = 'failed') AS failed,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms
FROM orders
WHERE created_at >= now() - interval '30 days'
GROUP BY 1 ORDER BY 1;
```

Gate: a dated baseline file exists, with the query or command that produced it.

## Stage 6 - Publish a one-page plan in week one

6.1 One page: mandate, 3 deliverables with dates, 3 metrics, the stakeholder map summary, and what you need from your manager.

6.2 Send it to your manager and ask for one correction, not approval. "Is anything here wrong" gets a faster and more honest answer than "does this look good".

6.3 Update it at day 30 and day 60 with what changed. The update is the progress report and it replaces a status meeting.

6.4 Keep the same file name and add the date; do not send v7 of a document nobody can track.

```text
First 90 days - <name>, <role>
Mandate: <one sentence in my manager's words>

Deliverables
  1. by <date> - <fix> - done when <observable>
  2. by <date> - <system I own> - baseline <number>
  3. by <date> - <improvement> - target <number>

Metrics I will report: <3 numbers>
Need from you: <one decision, one access, one intro>
```

Gate: the page is sent before day 10 and contains one specific ask for the manager.

## Stage 7 - Run the day-30 review as a working session

7.1 Bring the plan, the baseline numbers and one blocker. Three items, 30 minutes.

7.2 Ask for one thing removed from your plate. New joiners accumulate orphan work in month 1.

7.3 Confirm the month-2 deliverable is still the right one. Priorities move; the plan must move with them.

7.4 Write the decisions from the meeting and send them back in 5 lines. This is how you build a record of agreed scope.

Gate: day-30 review done, one item removed, month-2 deliverable confirmed or changed in writing.

## Stage 8 - Deliver something visible by day 45

8.1 Ship the month-1 fix publicly: a short message to the affected team with before and after numbers.

8.2 Credit the person who told you about the problem. It converts a source into an ally.

8.3 Keep it under 100 words. A launch email longer than the fix reads as self-promotion.

8.4 Do not ship the month-2 system yet. Two unfinished things is worse than one finished and one started.

Gate: one visible fix shipped, with numbers and a named credit.

## Stage 9 - Close the 90 days with evidence, not adjectives

9.1 Compare each of the 3 metrics against the baseline: start, current, target.

9.2 List what you own now that you did not own on day one. Ownership is the real output of 90 days.

9.3 Ask your manager for one written sentence on what to do more of and one on what to stop. Ask for it in writing, in the same message as the summary.

9.4 Agree the next 90-day plan in the same meeting, so the cycle continues with a fresh mandate.

9.5 Save the whole record - plan, baselines, updates, close-out - in one folder. It becomes your promotion case and your next interview story.

| Close-out item | Evidence |
|---|---|
| Deliverable 1 | shipped, used by a named team |
| Deliverable 2 | owned, with a runbook |
| Deliverable 3 | metric moved from baseline to target |
| Ownership gained | list of systems now yours |
| Feedback | one written do-more, one stop |

Gate: three metrics with before and after, plus written feedback from the manager.

## Stage 10 - Protect the record and the next cycle

10.1 Keep every artefact in one folder: the plan, the baseline files, the two updates, the close-out table.

10.2 Write 5 lines of reflection the same week: what you owned, what you refused, what you would do differently.

10.3 Convert the close-out into 3 CV-ready lines, each with a number. Memory decays faster than you expect.

10.4 Add one relationship that would survive you leaving: a person in another team who would take your call in 2 years.

| Artefact | Kept where | Used later for |
|---|---|---|
| one-page plan | folder, dated | interview story, promotion case |
| baseline files | folder, with the query | proving the improvement |
| day-30 and day-60 updates | folder | evidence of scope changes |
| close-out table | folder | next review, next job |

10.5 Diarise a 6-month check against the same 3 metrics. The 90-day win is only durable if it is still holding.

Gate: the folder, the 5-line reflection and the 6-month check date all exist before the plan is filed.

## Worked example

A product analyst joining a 40-person company, day 1 to day 90.

| Day | Action | Result |
|---|---|---|
| 3 | asked the failure question | manager named a reporting dispute as the risk |
| 8 | 10 stakeholder conversations | 4 people independently complained about the weekly revenue report |
| 10 | one-page plan sent | manager removed 2 inherited tasks from the plate |
| 24 | report reconciled to the rupee | finance started using it |
| 30 | baseline captured | report takes 3.5 hours a week to produce manually |
| 55 | report automated | 12 minutes, same output |
| 88 | close-out | 3.5 h to 12 min weekly, report owned, next 90-day plan agreed |

The visible fix at day 24 cost about 6 hours and bought the credibility to automate the report at day 55.

## Quality checklist

- [ ] Mandate written in the manager's words, not the job description
- [ ] Failure question asked and the answer recorded
- [ ] Decision rights confirmed for the 3 kinds of call
- [ ] 12+ stakeholders mapped with need and type
- [ ] Top 8 first conversations booked inside 10 days
- [ ] Same 3 questions asked in every conversation
- [ ] Top theme backed by 3 independent mentions
- [ ] Exactly 3 deliverables, one per month, each dated
- [ ] Each deliverable has an observable definition of done
- [ ] Baseline measured and saved with its query
- [ ] One-page plan sent before day 10 with one ask
- [ ] Day-30 review held and one task removed
- [ ] One visible fix shipped by day 45 with before and after
- [ ] Three metrics reported against baseline at day 90
- [ ] Written do-more and stop feedback obtained
- [ ] Next 90-day plan agreed in the close-out meeting

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Four months in, nobody can name your work | No deliverable, only meetings | One dated deliverable per month |
| First visible change breaks something | Never asked what is working | Ask that question in every first conversation |
| Plan approved but never followed | Approval asked instead of correction | Ask "is anything here wrong" |
| Month-3 improvement unprovable | No baseline captured in week 2 | Measure before changing anything |
| Drowning in orphan work | Accepted everything in month 1 | Refuse a fourth deliverable, ask for removal at day 30 |
| Manager surprised at review time | No written updates | Same file, updated at day 30 and 60 |
| Fix shipped quietly | No announcement to the affected team | 100-word before-and-after message |
| Feedback is vague at day 90 | Asked verbally, got adjectives | Ask in writing, one do-more and one stop |
| Credibility never built | Started with the big system | Ship the small visible fix first |
| Next 90 days start from zero | No close-out meeting | Agree the next plan in the same session |

## Copy-ready agent prompt

> Read the skill at the URL above and build my 30/60/90 plan. Ask me: the role, the team size, my manager's stated reason for the hire, what I already know is broken, and my start date. Then give me the 5 mandate questions with what a red-flag answer looks like, a stakeholder table with type and need for 12-15 people, the 3 questions to ask in every first conversation, exactly 3 deliverables with dates, definitions of done and metrics, the baseline query or command for the month-2 system, and the one-page plan I can send in week one with one specific ask of my manager. Finish with the day-30 review agenda and the day-90 close-out table. Do not give me a list of 12 goals - give me 3 deliverables.
