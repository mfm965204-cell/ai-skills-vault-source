---
name: performance-review-brief
description: Build a review packet from evidence - impact statements with numbers, a brag log that is already written, and a one-page brief that maps your work to the next level's expectations.
version: 1.0.0
license: MIT
tags: [career, performance-review, promotion, writing, evidence]
---

# Performance Review Brief

Review season punishes people with good memories and rewards people with good records. The work you did in March is invisible in November unless you wrote it down while it was fresh, and "I worked really hard on the migration" loses to a colleague's "cut p95 latency 40% for 2.1 million requests a day".

This skill builds the packet from evidence: an impact log you maintain weekly, a mapping from your work to the expectations of the next level, and a one-page brief a manager can forward upward without rewriting it. It also prepares the two things reviewers actually ask - what you would do differently, and what you need.

The packet is not a boast. It is a record with numbers, dates and a named witness per claim, which is why it survives calibration.

## When to use this skill

- Review season opens in two weeks and you have no record of the year.
- You are going for promotion and do not know what the next level expects.
- Your manager's summary of your year is thinner than your actual year.
- You manage someone and want them to build the same record.
- **Do NOT use for:** writing a resume or negotiating a raise (both different artefacts), or fabricating impact - a claim without evidence in a calibration meeting damages you more than an omission.

## Stage 1 - Start the impact log, even mid-year

The log is the packet's raw material: one line per event, written the week it happened. Starting it in November means reconstructing 10 months from memory and calendar invites.

1.1 Create one file per year with a fixed line format: date, what shipped, the metric, who noticed.

1.2 Add an entry the week something ships, not when the quarter ends.

1.3 Record the number even when it is small: "reduced build time 14 minutes to 9 minutes".

1.4 Name the witness - who reviewed it, who depended on it, who thanked you. Names convert a claim into a fact.

1.5 Record the unglamorous work separately: incidents handled, reviews done, onboarding help, docs written. It is a third of your value and the first thing forgotten.

1.6 Backfill the current year from pull requests, tickets, documents and calendar, in that order, before the season opens.

```markdown
## 2026 impact log

- 2026-02-11 | Shipped checkout retry | failure rate 3.1% -> 0.4% | reviewed by R
- 2026-03-04 | Migration cutover | zero downtime, 2.1M rows | witness: infra lead
- 2026-05-22 | Ran 14 interviews | hired 3 engineers | witness: hiring manager
- 2026-08-09 | Incident 214 | restored in 38 min, wrote postmortem | witness: on-call
```

Gate: at least 20 dated entries for the year, each with a metric or a named witness.

## Stage 2 - Turn entries into impact statements

A log line is evidence. An impact statement is the sentence a reviewer can repeat in a room you are not in.

2.1 Write each statement in the form: action, metric, scale, window.

2.2 Put the number before the adjective, always: "cut p95 from 820 ms to 480 ms" beats "improved performance significantly".

2.3 Name the scale - users, rupees, requests, records - because impact without scale is effort.

2.4 Name the window: over 6 weeks, in one release, across the quarter.

2.5 Cut anything you cannot defend with a link, a ticket or a witness. One weak claim discounts the strong ones beside it.

2.6 Keep the top 6 statements for the brief and the rest in an appendix.

| Weak | Strong |
|---|---|
| Worked on the payments migration | Migrated 2.1M payment records to the new schema with zero downtime over 3 weekends |
| Improved test coverage | Raised coverage from 41% to 68% in the billing module, catching 9 regressions before release |
| Helped with hiring | Ran 14 interviews and closed 3 engineers in 5 weeks, against a 9-week average |
| Fixed many bugs | Closed 34 bugs, 11 of them P1, median time to fix 1.8 days |

Gate: six statements, each with a number, a scale and a window, each defensible with a link.

## Stage 3 - Get the next level's expectations in writing

Promotion is not a reward for good work at your level. It is evidence that you already operate at the next one, and the expectations are usually documented somewhere.

3.1 Find the level rubric, career ladder or competency document; if it does not exist, ask your manager for one paragraph per expectation.

3.2 Copy the expectations for the next level verbatim into a file, one per line.

3.3 Against each, write the strongest evidence you have, or write "gap" honestly.

3.4 Count the gaps. More than two means this cycle is about closing them, not about a promotion case.

3.5 Ask your manager which expectation they would weight most, and record the answer with a date.

3.6 Check the rubric version. Ladders get revised, and a case argued against last year's document is a wasted cycle.

Gate: every next-level expectation has either evidence or the word gap beside it.

## Stage 4 - Fill the gaps with scope, not hours

Gaps close with a different kind of work, not more of the same. The usual gaps at the next level are ambiguity, influence and ownership beyond your team.

4.1 For an ambiguity gap, take one problem with no ticket and write the spec for it.

4.2 For an influence gap, get one piece of work adopted by a team that does not report to your manager.

4.3 For a scope gap, own one thing end to end, including the part nobody enjoys: rollout, docs, on-call.

4.4 For a mentoring gap, take one person through one project and let them present it.

4.5 Timebox each gap to one quarter and record the artefact it produced.

4.6 Tell your manager what you are taking on and why, in writing, before you start. Promotion cases built in secret are usually rejected.

Gate: each open gap has one named piece of work, a quarter and a written note to the manager.

## Stage 5 - Write the one-page brief

The brief is what gets forwarded. It has to survive being read by someone who has never met you and has 90 seconds.

5.1 Header: name, role, level, review period, and the level being requested.

5.2 Six impact statements, strongest first, each one line with a number.

5.3 Three lines on scope: what you owned, what you influenced outside your team, who you helped grow.

5.4 Two lines on what you would do differently, with the lesson in the same sentence.

5.5 Two lines on what you need next - a specific project, a specific support, not "more growth opportunities".

5.6 One appendix listing links: pull requests, dashboards, documents, postmortems.

5.7 Write the brief in the past tense with dates. "Shipped on 2026-02-11" is checkable; "have been shipping" is not.

```markdown
# Review brief - <name>, <role>, <period>

Requested level: <next level>

## Impact
1. <action> - <metric> - <scale> - <window>
2. ...

## Scope
- Owned: <system or area>
- Influenced: <team or decision outside my team>
- Grew: <person, what they now do alone>

## Differently
- <what I would change> - <the lesson>

## Next
- <the project or support I need>
```

Gate: one page, six statements, three scope lines, two lines on change, two on need, one appendix.

## Stage 6 - Rehearse the three questions reviewers ask

Calibration asks the same three things. Answers prepared in advance sound like judgement; answers improvised sound like defensiveness.

6.1 "What would you do differently?" - have one real answer with the cost, not a humble-brag.

6.2 "What is the hardest thing you did this year?" - answer with the constraint, not the outcome alone.

6.3 "Who else knows about this work?" - have two names outside your immediate team.

6.4 "What would break if you left?" - have an answer that names systems and people, not just yourself.

6.5 Write each answer in three sentences and say them out loud once before the meeting.

Gate: four prepared answers, each three sentences, one with a named cost.

## Stage 7 - Ask for the review, with the packet attached

The brief does not submit itself. The ask is a short message with the packet attached, sent before the manager writes their summary.

7.1 Send the brief 10 working days before the review deadline, not the day before.

7.2 Ask for one specific thing: "please use this in your write-up, and tell me where it overclaims".

7.3 Offer the appendix links but do not attach 40 files.

7.4 Ask for the level conversation explicitly if that is what you want, rather than hoping it is inferred.

7.5 Record what the manager says they will do, with a date, so the follow-up is not a memory contest.

7.6 Send a two-line follow-up a week later restating the ask. One message gets lost in a busy week; two is a record.

Gate: the brief is sent 10 days early with one specific ask and a recorded commitment.

## Stage 8 - Handle the outcome, either way

Reviews return one of three answers: yes, not this cycle, or a version of "yes but quieter". Each needs a different next move.

8.1 On yes, ask what made the difference so you can repeat it, and get the scope in writing.

8.2 On not this cycle, ask for the specific gap in writing, with the evidence that would close it and a date to review.

8.3 On a quiet yes - title without scope - ask for the scope in the next quarter and record it.

8.4 If the written feedback contradicts the verbal feedback, ask which one the calibration committee saw.

8.5 Keep the packet. Next year's version starts from this one, and the trend is often the strongest argument.

Gate: the outcome is written down with the next step, the owner and a date.

## Stage 9 - Maintain the log so next year starts full

The whole system costs 10 minutes a week. The alternative costs two weeks in November and a weaker case.

9.1 Add an entry every Friday, even a small one.

9.2 Every quarter, re-read the log and promote the three strongest lines into the brief's draft.

9.3 Every quarter, check the gaps list against the next level's expectations.

9.4 Keep the appendix links alive; dead links in an appendix are worse than no appendix.

9.5 At year end, archive the packet with its date so the trend across years is visible.

9.6 Keep the packet in one file per year named by year, so a comparison across three years takes one command.

Gate: a weekly habit, a quarterly review and an archived packet for the year.

## Quality checklist

- [ ] The impact log has at least 20 dated entries for the year.
- [ ] Every entry carries a metric or a named witness.
- [ ] Six impact statements exist, each with a number, a scale and a window.
- [ ] Every statement is defensible with a link, a ticket or a witness.
- [ ] The next level's expectations are copied verbatim from a source.
- [ ] Every expectation has evidence or the word gap beside it.
- [ ] Each gap has one named piece of work and a quarter.
- [ ] The manager has been told in writing which gaps you are closing.
- [ ] The brief fits on one page with six statements.
- [ ] The brief names what you would do differently, with a cost.
- [ ] The brief names what you need next, specifically.
- [ ] Four rehearsal answers are written, three sentences each.
- [ ] The brief was sent 10 working days before the deadline.
- [ ] The manager's commitment is recorded with a date.
- [ ] The outcome and next step are written down with an owner.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Manager's summary omits your biggest project | The packet arrived after their write-up | Send the brief 10 working days early |
| Case rejected in calibration | Claims without witnesses, so the committee discounted them | Add a named witness or a link to each statement |
| "Great work, not this cycle" | No next-level expectations were ever named | Copy the rubric and map evidence to it before the cycle |
| Feedback is vague and unactionable | The ask was "any feedback", not a specific gap | Ask for the gap in writing with the evidence that closes it |
| Title without scope | The case argued level, not responsibility | Ask for the scope in the same conversation and record it |
| Log empty in November | Entries batched at quarter end | One entry every Friday, in the same file |

## Copy-ready agent prompt

> Read the skill at the URL above and build my review packet. Ask me for my role, level, review period and the next level's expectations, then take whatever evidence I paste in and turn it into six impact statements with a number, a scale and a window each. Map every next-level expectation to evidence or the word gap, write the one-page brief in the given format, and prepare the four rehearsal answers. Flag any claim I cannot defend with a link or a named witness, and do not soften a weak claim into a strong one.
