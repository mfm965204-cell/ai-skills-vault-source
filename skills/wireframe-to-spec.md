---
name: wireframe-to-spec
description: Turn a wireframe into a developer-ready spec - states, spacing, copy, edge cases and acceptance criteria - so build starts without a meeting per screen.
version: 1.0.0
license: MIT
tags: [design, wireframe, specification, handoff, product]
---

# Wireframe To Spec

A wireframe says where things go. It does not say what happens when the list is empty, what the button says while it is loading, how wide the column is on a 320 px screen, or whether the destructive action is reversible. Those gaps are filled in by whoever is building, which is why two developers build two different screens from one wireframe.

This skill converts a wireframe into a spec a developer can build without asking: every state, every measurement, every string, and an acceptance criterion per element. It ends with a document that survives review and a checklist that catches the questions a wireframe always leaves open.

The test of a finished spec: a developer can build the screen and a QA engineer can write the test cases from the document alone, without either of you in the room.

## When to use this skill

- You have wireframes and the build is about to start.
- Developers keep asking the same questions about states and copy.
- Two people built two versions of the same screen.
- You need acceptance criteria for QA from a design document.
- **Do NOT use for:** visual design or brand systems, writing the actual component code, or usability research - this covers the handoff document between design and build.

## Stage 1 - Name the screen, the route and the job

A spec without a route is a picture. Fix the identity of the screen first so everything else can reference it.

1.1 Name the screen in the product's own vocabulary, not "screen 3".

1.2 Write the route or the component path it will live at.

1.3 Write the one job the screen does, in a single sentence.

1.4 List the entry points: which screens or links lead here, and with what state.

1.5 List the exits: where each action goes on success, failure and cancel.

1.6 Name the owner on design and the owner on build.

| Field | Value |
|---|---|
| Screen | Invoice list |
| Route | `/invoices` |
| Job | Find an invoice and open it |
| Entry | Sidebar, dashboard card, email link |
| Owner (design) | Name |
| Owner (build) | Name |

Gate: screen name, route, one-sentence job, entry and exit points, and both owners are recorded.

## Stage 2 - Break the wireframe into named regions

Regions give the developer a vocabulary for the layout and give the spec a structure that matches the DOM.

2.1 Name each region: header, filter bar, table, empty state, pagination, bulk action bar.

2.2 State the layout rule per region: fixed height, sticky, scrolls with the page, collapses below a breakpoint.

2.3 State the width behaviour: fixed, fluid, min and max in pixels.

2.4 Note which regions are conditional and what condition shows them.

2.5 Note which regions are shared components that already exist, and name them.

2.6 Mark the region that carries the primary action, so build order follows the job.

Gate: every region is named, with its layout rule, width behaviour and visibility condition.

## Stage 3 - Write every state, including the boring ones

Most handoff failures are missing states. A screen with a happy path and no empty state is half a screen.

3.1 Write the default state with realistic content - not lorem ipsum, real-shaped values.

3.2 Write the empty state: the message, the illustration or icon, and the action it offers.

3.3 Write the loading state: skeleton, spinner or nothing, and after how many milliseconds it appears.

3.4 Write the error state: what the message says, what the retry does, and whether it is inline or full-screen.

3.5 Write the partial state: some rows loaded, some failed, one field missing.

3.6 Write the success state after an action, including whether it is a toast, an inline change or a redirect.

3.7 Write the permission state: what a read-only user sees, and which controls disappear versus disable.

| State | Trigger | What the user sees | Primary action |
|---|---|---|---|
| Default | 1+ records | Table with 20 rows | Open invoice |
| Empty | 0 records | Message plus "Create invoice" | Create |
| Loading | Request in flight over 300 ms | 5 skeleton rows | None |
| Error | Request failed | Inline message plus Retry | Retry |
| Read-only | No edit permission | Table without edit controls | Open (view only) |

Gate: seven states written for the screen, each with its trigger and its primary action.

## Stage 4 - Specify measurements, not adjectives

"Spacious" is not a measurement. Give numbers a developer can type, and reference the design tokens rather than raw values where the system has them.

4.1 Give spacing in multiples of the system's base unit - 4 or 8 px - and name the token where one exists.

4.2 Give type sizes and weights by token, not by pixel guess.

4.3 Give the table's row height, column widths and the rule for truncation, with the tooltip behaviour.

4.4 Give the breakpoints: what changes at 320, 768 and 1280 px.

4.5 Give the focus and hover treatments, including the focus ring width and colour token.

4.6 Give the icon sizes and their alignment relative to text.

```css
/* the numbers a spec should carry, expressed as tokens */
.filter-bar { padding: var(--space-3) var(--space-4); gap: var(--space-2); }
.table-row  { height: 44px; }
.cell       { padding-inline: var(--space-3); }
.cell--truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 768px) {
  .table-row { height: 56px; }         /* taller touch target */
  .filter-bar { flex-wrap: wrap; }
}
```

Gate: every measurement is a number or a token, and the 320, 768 and 1280 px behaviours are stated.

## Stage 5 - Put every string in the document

Copy written at build time is copy nobody reviewed. Put the strings in the spec, in a table, with the character limit where layout depends on it.

5.1 List every label, placeholder, helper text, error message and button label.

5.2 Give each string a maximum length, and note the ones that must not wrap.

5.3 Write the error messages as what happened plus what to do: "Could not load invoices. Retry."

5.4 Write the destructive confirmations with the object named: "Delete invoice INV-1042? This cannot be undone."

5.5 Note the strings that are dynamic and what fills them.

5.6 Mark strings that need translation, so they get extracted rather than hardcoded.

| Element | String | Max chars | Notes |
|---|---|---|---|
| Page title | Invoices | 24 | Static |
| Filter placeholder | Search by number or client | 32 | Static |
| Empty message | No invoices yet. Create your first one. | 60 | Two lines allowed |
| Error | Could not load invoices. Retry. | 48 | Inline |
| Delete confirm | Delete invoice {number}? This cannot be undone. | 70 | Names the object |

Gate: every user-visible string is in the table with a maximum length.

## Stage 6 - Cover the edge cases the wireframe cannot show

Edge cases are where a spec earns its keep. Write the ones that decide the implementation, and the ones QA will find anyway.

6.1 Long values: a 60-character client name, a 12-digit invoice number, an amount in crores.

6.2 Many records: what the screen does at 1, 20, 200 and 100,000 rows.

6.3 Slow network: what shows at 1 second, 5 seconds and after a timeout.

6.4 Permissions: read-only, owner, and a user whose permission changed mid-session.

6.5 Concurrency: another user deleted the record while this screen was open.

6.6 Failure of the destructive action: what the user sees and what state the record is in.

6.7 Time zones and locales: a date near midnight, a currency with a different separator.

Gate: each edge case has a stated behaviour, not a "TBD".

## Stage 7 - Write acceptance criteria per element

Acceptance criteria turn a design document into something QA can test and a developer can finish against.

7.1 Write one criterion per interactive element, in the form "given, when, then".

7.2 Cover the negative case for each: invalid input, no permission, network failure.

7.3 Include the measurable criteria: renders under 1 second, keyboard reachable, contrast at least 4.5:1.

7.4 Include accessibility criteria: focus order, labels, announced errors.

7.5 Number the criteria so a pull request can reference them.

7.6 Keep each criterion to one assertion; a compound criterion cannot fail cleanly.

```markdown
AC-1  Given 200 invoices, when the screen loads, then 20 rows render within 1 second.
AC-2  Given no invoices, when the screen loads, then the empty state shows with a Create action.
AC-3  Given the search field, when I type 3 characters, then results filter within 300 ms.
AC-4  Given a read-only user, when the screen loads, then no edit or delete controls render.
AC-5  Given a failed request, when Retry is pressed, then the request repeats and the error clears on success.
```

Gate: every interactive element has at least one positive and one negative criterion, numbered.

## Stage 8 - Review the spec with the builder before build

A spec reviewed by the person who wrote it is a draft. Twenty minutes with the developer finds the gaps that would have cost two days.

8.1 Walk the developer through the states table, not the wireframe.

8.2 Ask them to name the one thing they would have to guess; fix it in the document.

8.3 Confirm the components that already exist, and delete any spec text that re-describes them.

8.4 Confirm the data shape: which fields exist today and which need an API change.

8.5 Agree the build order and what can ship behind a flag.

8.6 Record the review date and the open questions with owners.

Gate: the developer has named no remaining guess, and open questions carry owners and dates.

## Stage 9 - Keep the spec alive through build

A spec that stops at handoff is wrong by week two. Keep it the reference during build, and update it in the same place.

9.1 Keep the spec in the repository next to the code, not in a design tool export.

9.2 Update it when a decision changes during build, with a date and a reason.

9.3 Link the pull request to the acceptance criteria numbers it satisfies.

9.4 Add the questions that came up during build to the edge-case section, so the next screen benefits.

9.5 After release, note which criteria were tested and which were skipped.

9.6 Archive the final version with the release, so a later bug can be traced to a decision.

Gate: the spec lives with the code, is updated with dated decisions, and the pull request references its criteria.

## Quality checklist

- [ ] The screen has a name, a route and a one-sentence job.
- [ ] Entry and exit points are listed with their state.
- [ ] Every region is named with a layout and width rule.
- [ ] Conditional regions state their condition.
- [ ] All seven states are written with triggers.
- [ ] The empty state offers an action.
- [ ] Measurements use tokens or explicit numbers.
- [ ] Behaviour at 320, 768 and 1280 px is stated.
- [ ] Focus and hover treatments are specified.
- [ ] Every user-visible string is in a table with a maximum length.
- [ ] Error messages state what happened and what to do.
- [ ] Edge cases are covered with stated behaviour, not TBD.
- [ ] Acceptance criteria are numbered, one assertion each.
- [ ] Every element has a positive and a negative criterion.
- [ ] The developer review found no remaining guess.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Two developers built two screens | Spec had no states or measurements, so each filled the gaps | Write the seven states and the token values in the document |
| "What does this button say while loading" | Copy left to build time | Put every string in the spec table with a length limit |
| Empty state shipped as a blank page | Only the default state was wireframed | Add the empty state with a message and an action |
| QA cannot write tests | No acceptance criteria | Write numbered given-when-then criteria per element |
| Spec obsolete by week two | Document lives outside the repository | Keep it beside the code and update with dated decisions |
| Accessibility fixed after launch | Criteria had no accessibility assertions | Add focus order, labels and contrast criteria |

## Copy-ready agent prompt

> Read the skill at the URL above and turn my wireframe into a build-ready spec. Ask me for the wireframe, the route and the design tokens I use, then produce the screen header, the named regions with layout rules, all seven states with triggers, the measurements as tokens with 320, 768 and 1280 px behaviour, a string table with maximum lengths, the edge cases with stated behaviour, and numbered acceptance criteria with a positive and negative case per element. Finish with the questions I should ask the developer in the review. Do not write component code.
