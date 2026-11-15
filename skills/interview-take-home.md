---
name: interview-take-home
description: Scope, timebox and ship a take-home assignment that reads as professional work - working build, README with trade-offs, tests that prove the claims, and a cover note that closes the loop.
version: 1.0.0
license: MIT
tags: [career, interview, engineering, take-home, hiring]
---

# Interview Take Home

A take-home is not a coding test. It is a work sample: the reviewer is deciding whether they want this person's commits in their repository next quarter. Most submissions fail on presentation rather than capability - no README, no stated assumptions, a build that does not run on the reviewer's machine, and a cover note that says "let me know if you have questions".

This skill timeboxes the assignment, sets the scope you will actually defend, and produces the four artefacts reviewers look for: a build that runs in one command, a README with the trade-offs named, tests that prove the claims, and a short cover note that says what you would do next.

The single rule that decides the outcome: an incomplete submission with a clear README beats a complete one that nobody can run.

## When to use this skill

- You received a take-home with a stated time budget and no further guidance.
- The assignment is vague ("build something with this API") and you need to choose scope.
- You have 6 hours and could spend 30 of them.
- You want the submission to survive a reviewer who runs it for 3 minutes and then skims the README.
- **Do NOT use for:** timed live coding or whiteboard interviews, unpaid production work dressed up as a test (decline that), or negotiating the offer afterwards - this ends at the submitted repository.

## Stage 1 - Read the brief twice and write the acceptance list

The brief usually contains four requirements and two hidden expectations. Extract both before you open an editor, because the hidden ones - tests, README, running instructions - are what separate a pass from a rejection.

1.1 Copy the brief into a file and mark every explicit requirement with a number.

1.2 Mark every implied requirement: it runs, it is documented, it handles bad input, it is tested.

1.3 Write the acceptance list as binary checks you can verify before submitting: "one command starts it", "README explains the schema choice".

1.4 Note the stated time budget and halve your ambition to fit it, not your quality.

1.5 Identify the one requirement that carries the most weight and plan to over-deliver there only.

1.6 Ask the recruiter one clarifying question at most, and make it about scope, not about permission.

Gate: an acceptance list of 8-12 binary checks exists, with the heaviest requirement marked.

## Stage 2 - Timebox the work in fixed blocks

Take-homes expand to fill the time you give them. Assign minutes per block before you start and stop at the boundary, because a submission that stops cleanly reads as discipline.

2.1 Reserve the first 10% of the budget for reading and planning, and write the plan into the README before any code.

2.2 Reserve 50% for the core path only - the happy path plus the one edge case the brief names.

2.3 Reserve 20% for tests, 10% for the README and 10% for the cover note.

2.4 Keep the last 10% as buffer for the environment problems you will hit, usually a dependency that will not install.

2.5 Set a hard stop and a cut list: what you will drop if you run out of time, decided in advance.

| Block | Share of budget | Deliverable | Cut if short |
|---|---|---|---|
| Read and plan | 10% | Acceptance list, README skeleton | Never cut |
| Core path | 50% | Working happy path | Never cut |
| Tests | 20% | 5-8 meaningful tests | Cut to 3 |
| README | 10% | Run instructions, trade-offs | Never cut |
| Cover note | 10% | Half a page | Never cut |
| Buffer | 10% | Fix install problems | Absorbed |

Gate: every block has a minute allocation and the cut list is written before coding starts.

## Stage 3 - Choose the smallest architecture you can defend

Reviewers judge fit, not cleverness. Pick the stack you can explain in one sentence, and write down why you picked it in the README, because that sentence is the first thing a reviewer reads.

3.1 Choose the stack the team already uses if the brief names it, without exception.

3.2 If the stack is free, pick the one where you can ship a tested path in the time available, not the one you find most interesting.

3.3 Avoid infrastructure that needs a paid account or a manual console step - the reviewer will not do it.

3.4 Keep the dependency count low. Every dependency is a thing that can fail on the reviewer's machine.

3.5 Decide the data layer first: in-memory, SQLite file, or a hosted database. In-memory plus a seed file is enough for a take-home and never fails to run.

3.6 Write the architecture decision into the README as one paragraph with the alternative you rejected.

Gate: the stack is named, the data layer is decided, and the README carries one paragraph on why.

## Stage 4 - Build the happy path first, and make it run in one command

The reviewer's first action is to run it. If that fails, nothing else in the submission matters.

4.1 Make the entry point one command: `make run`, `npm start`, `docker compose up` - whichever your stack makes trivial.

4.2 Pin versions in a lockfile and commit it.

4.3 Seed the database or the in-memory store on first run so there is data to look at without manual setup.

4.4 Print the URL and any credentials on startup. A reviewer should never hunt through a README for a port.

4.5 Handle the empty state and one bad input, so the app does not crash on the reviewer's first click.

4.6 Commit in small, readable commits as you go. A single "final" commit reads as work done in one panic.

```bash
# the reviewer's path - keep it this short
git clone <repo> && cd <repo>
cp .env.example .env
make run
# prints: listening on http://localhost:3000, seeded 40 records
```

Gate: a clean clone plus one command produces a running app with data, on a machine that is not yours.

## Stage 5 - Write the tests that prove the claims in the README

Tests are not for coverage percentages here. They are the evidence for the statements you make in the README, and five well-chosen ones beat forty trivial ones.

5.1 Test the one behaviour the brief cares about, in the terms the brief used.

5.2 Test the edge case the brief named, plus the empty-input case.

5.3 Test the failure path: what happens when the external call fails or the record is missing.

5.4 Keep the suite under 30 seconds so the reviewer actually runs it.

5.5 Name tests as sentences: "returns 404 when the order does not exist" reads better than "test order 2".

5.6 Add one end-to-end test through the real entry point, not only unit tests.

```bash
npm test -- --runInBand
# 7 passing, 0 failing, 3.1s
```

Gate: the test suite runs green from a clean clone in under 30 seconds and covers the brief's named edge case.

## Stage 6 - Write the README the reviewer reads in 3 minutes

The README is the submission. Many reviewers read it before running anything, and some never run anything at all.

6.1 Open with what it does, in two sentences, and one screenshot or a curl example.

6.2 Follow with how to run it in exactly the commands from Stage 4, copy-pasteable.

6.3 Add an "Assumptions" section: every ambiguity in the brief and the reading you chose.

6.4 Add a "Trade-offs" section: what you did not build, and what you would build next with more time.

6.5 Add a "Tests" section with the command and what it covers.

6.6 Keep it under 150 lines. A README longer than the code is a signal in itself.

```markdown
# <Project> - take-home for <role>

<What it does in two sentences.>

## Run it
    cp .env.example .env && make run

## Assumptions
- Amounts are stored in paise, not rupees, to avoid float rounding.
- Auth is out of scope; a seeded user is used for every request.

## Trade-offs
- SQLite over Postgres: zero setup for the reviewer; would move to Postgres in production.
- No pagination: dataset is seeded at 40 rows.

## Tests
    npm test    # 7 tests, covers the partial-refund edge case
```

Gate: README under 150 lines with run instructions, assumptions, trade-offs and tests.

## Stage 7 - Write the cover note that closes the loop

Half a page, sent with the link. It is where you show judgement about your own work, which is the thing the take-home cannot test.

7.1 State what you built and the time you spent, honestly.

7.2 Name the two decisions you would defend in a review, and the one you are least sure about.

7.3 Say what you would do with another 4 hours, in order.

7.4 Ask one specific question about the team's real system that your work touches.

7.5 Keep it under 250 words. Long cover notes read as anxiety.

Gate: a cover note under 250 words naming two decisions, one doubt and one question.

## Stage 8 - Verify from a clean machine before sending

Your machine has the dependency cached, the environment variable exported and the database seeded. The reviewer's machine has none of that.

8.1 Clone the repository into a fresh directory and run the documented commands verbatim.

8.2 Check that no secret, personal path or absolute local URL is in the repository.

8.3 Run the tests from the fresh clone and confirm green.

8.4 Open the app on a phone-sized viewport if there is any UI at all.

8.5 Read the README as if you were hostile: any step you would question, rewrite.

8.6 Send the link, the cover note and the time spent, in one message.

Gate: a fresh clone passes the documented commands, the tests are green, and no local path or secret is committed.

## Stage 9 - Handle the follow-up review well

Most take-homes are followed by a 30-minute walkthrough. Prepare for it as part of the submission, not after.

9.1 Keep a note of the two decisions you would defend and the one you would change.

9.2 Be ready to say what you would delete first if the code had to live in a real repository.

9.3 Answer scope questions with the trade-off, not with defensiveness: "I chose SQLite for setup time, it would be Postgres with a migration tool in production".

9.4 If the reviewer found a bug, thank them and fix it in a follow-up commit; that response is part of the signal.

9.5 Ask what the team's actual review standard is, so you learn from the exercise either way.

Gate: two defended decisions, one acknowledged weakness and one prepared scope answer before the call.

## Quality checklist

- [ ] The acceptance list has 8-12 binary checks and was written before coding.
- [ ] The time budget is split into blocks with a written cut list.
- [ ] The stack choice is one paragraph in the README with the rejected alternative.
- [ ] A clean clone plus one command runs the app with seeded data.
- [ ] The startup output prints the URL and any credentials.
- [ ] The test suite is green in under 30 seconds.
- [ ] The brief's named edge case has a test.
- [ ] Tests are named as sentences.
- [ ] The README is under 150 lines with run instructions.
- [ ] The README has an Assumptions section covering every ambiguity.
- [ ] The README has a Trade-offs section naming what was not built.
- [ ] The cover note is under 250 words with two decisions and one doubt.
- [ ] A fresh clone passes the documented commands verbatim.
- [ ] No secret, local path or absolute URL is committed.
- [ ] Commits are small and readable, not one final commit.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Rejected with "could not run it" | An undocumented environment variable or a manual database step | Make one command work from a clean clone and print what it needs |
| Feedback says "unclear what was done" | No README, only code | Write the README first, from the acceptance list |
| Ran out of time and shipped nothing working | Scope grew past the stated budget | Apply the cut list and ship the core path only |
| Tests all pass but reviewer found a crash | Tests covered the happy path only | Add the empty-input and failure-path tests |
| Interviewer questions the stack | No stated reason, so it reads as arbitrary | Put the reason and the rejected alternative in the README |
| Cover note ignored | It was 900 words and asked for nothing | Cut to 250 words, name one doubt, ask one question |

## Copy-ready agent prompt

> Read the skill at the URL above and help me ship a take-home assignment. Paste-in my brief and my stated time budget, then produce the acceptance list with binary checks, a timeboxed plan with a cut list, and a README skeleton with Assumptions, Trade-offs and Tests sections. Then review my repository as a hostile reviewer would: a clean clone, the documented commands, the tests, and the first 150 lines of the README. Stop at a list of the gaps that would fail a 3-minute review, and do not write the feature code for me.
