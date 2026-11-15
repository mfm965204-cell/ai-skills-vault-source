---
name: multistep-form-wizard
description: Build a multi-step form that keeps state, validates per
step, survives a refresh, manages focus correctly and measures where
people drop out.
version: 1.0.0
license: MIT
tags: [frontend, forms, accessibility, ux, react]
---

# Multi-Step Form Wizard

Long forms fail at the step boundary: the user fills four screens,
refreshes, and starts again. Or they press Back and lose the fields
they typed, or a validation error appears on a screen they cannot see,
or the screen reader announces nothing when the step changes.

This skill builds the wizard properly: one state object with a schema,
validation per step, a draft saved locally and server-side, focus
moved to the new heading on every step change, an idempotent submit,
and drop-off measured per step so you can find the screen people
abandon.

## When to use this skill

- A form has more than 8 fields and conversion is below 40%.
- Users refresh mid-form and lose everything.
- A required field error appears after the final step with no way to find it.
- You are adding a checkout or KYC flow where the steps have legal meaning.

Do NOT use for: single-screen forms under 8 fields (validation only),
or a conversational form built by an AI agent, which has different
state semantics.

## Stage 1 — Decide the steps from the data, not the layout

Steps should group fields by the decision the user is making, not by
how much space they take.

1.1 Group fields by what they belong to: identity, contact, payment, consent. Four steps is the practical maximum for a checkout.

1.2 Put the cheapest fields first — name, email — so the user has invested something before the expensive ones.

1.3 Put consent and terms last, immediately before submit, where they can be read in context.

| Step | Fields | Why here |
|---|---|---|
| 1 Identity | name, email | cheapest, builds investment |
| 2 Address | line 1, city, state, PIN | needed for shipping and tax |
| 3 Payment | method, instrument | expensive, after commitment |
| 4 Consent | terms, marketing opt-in | read in context of submit |

Gate: each step holds one decision, no step exceeds 6 fields, and
consent is the last step.

## Stage 2 — Keep one state object with a schema

State split across components is where half-filled forms come from.
One object, one schema.

2.1 Hold the whole form in one object validated by a schema, with per-step field subsets for step validation.

2.2 Derive the step's validity from the schema rather than duplicating rules in components.

2.3 Never mutate state on Back; keep values and only change the visible step.

```javascript
const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  city: z.string().min(2),
  pin: z.string().regex(/^[1-9][0-9]{5}$/),
  method: z.enum(["upi", "card", "netbanking"]),
  consent: z.literal(true),
});
const stepFields = { 1: ["name", "email"], 2: ["city", "pin"],
                     3: ["method"], 4: ["consent"] };
```

Gate: one state object, one schema, and step validity computed from
the schema.

## Stage 3 — Validate on step exit, not on every keystroke

Validating while typing punishes the user for a half-typed email.

3.1 Validate a field on blur and a step on Next; never on the first keystroke.

3.2 Show the error next to the field with the fix in the message — "PIN must be 6 digits", not "invalid input".

3.3 Block Next only on that step's fields, and allow moving backwards without validation.

Gate: a step advances only when its fields pass the schema, and no
error appears before blur.

## Stage 4 — Save a draft and survive a refresh

A refresh is a lost sale. Persist the draft at two levels.

4.1 Save to local storage on every change, debounced by 500 ms, with a version key so a schema change invalidates old drafts.

4.2 Save to the server after each completed step for logged-in users, so a different device can resume.

4.3 On load, restore the draft and show a banner: "we saved your details from 2 days ago" — silent restoration confuses people.

Gate: a hard refresh at any step restores every field and the current
step, and the banner appears.

## Stage 5 — Manage focus and announce step changes

A step change is a page change for a screen reader, and it must be
announced as one.

5.1 Move focus to the step heading on every step change, with `tabindex="-1"` on the heading.

5.2 Announce the step number in an `aria-live="polite"` region: "step 2 of 4, address".

5.3 Never trap focus inside the step, and keep the Back button reachable by keyboard before the fields.

Gate: a keyboard-only run completes the flow, and the step change is
announced once.

## Stage 6 — Summarise before submit

A review step reduces failed submissions and support tickets,
especially when money is involved.

6.1 Show a review step for anything involving payment or identity, with each value and an edit link that jumps back to its step.

6.2 Keep the review read-only; editing happens on the step, not inline.

6.3 Show the total and the fees in the same currency format used elsewhere in the product.

Gate: the review step shows every submitted value with a working edit
link per group.

## Stage 7 — Make submit idempotent and guarded

Double submits are the most expensive bug in a payment form.

7.1 Disable the submit button on first click and show a spinner, but also guard on the server with an idempotency key generated per form session.

7.2 On network failure, keep the data and offer retry with the same key, so a retry cannot create a second order.

7.3 Show the success state as a separate route, so a refresh does not resubmit.

```javascript
const key = crypto.randomUUID();          // generated once per form session
await fetch("/api/orders", {
  method: "POST",
  headers: { "Content-Type": "application/json", "Idempotency-Key": key },
  body: JSON.stringify(state),
});
```

Gate: a double click produces one record, and a retry with the same
key returns the first result.

## Stage 8 — Measure drop-off per step

The only way to know which step is bad is to count who leaves on it.

8.1 Emit one event per step view and one per step completion, with the step id and the form id.

8.2 Compute completion rate per step and the time spent; a step with 60% completion and 3x the median time is the one to fix.

8.3 Instrument field-level errors by field id, because a single field can cause most of the abandonment.

Gate: completion rate per step is on a dashboard with field-level
error counts.

## Stage 9 — Test the flows that break

Wizards break at the edges: Back after an error, a resumed draft, a
slow network, a failed payment.

9.1 Test: refresh on every step, Back from every step, a draft from a previous schema version, a submit with the network offline.

9.2 Test with a screen reader and keyboard only, on the two browsers your users actually use.

9.3 Add a synthetic check that walks the flow weekly, so a deploy cannot silently break the last step.

Gate: all four edge cases pass and the weekly synthetic walk
completes.

## Worked example - 31% to 58% completion

A KYC flow for a lending product, four steps, 1,200 sessions a week.

| Step | Completion before | Completion after | Change |
|---|---|---|---|
| 1 Identity | 84% | 91% | validate on blur, not on keystroke |
| 2 Address | 61% | 82% | PIN auto-filled city and state |
| 3 Document | 44% | 71% | camera retry and clear file-size error |
| 4 Consent | 83% | 79% | review step added before submit |
| Whole flow | 31% | 58% | draft restore plus step events |

The address step was the leak. It asked for city and state as free
text after a PIN, and 38% of users typed a city name that did not
match the state they chose. Auto-filling both from the PIN removed the
mismatch and the errors.

The document step improved for a different reason: the error said
"upload failed" for a 12 MB photo, and users retried the same file
four times. A message naming the 5 MB limit and the retake option took
that step from 44% to 71%.

The consent step fell slightly after the review step was added, which
was expected and accepted: the review shows the fees, and some users
leave at that point instead of at the payment failure screen.

## Quality checklist

- [ ] Steps grouped by decision, 4 or fewer for checkout.
- [ ] No step exceeds 6 fields.
- [ ] Consent is the final step.
- [ ] One state object validated by one schema.
- [ ] Step validity derived from the schema.
- [ ] Validation on blur and on Next, never on first keystroke.
- [ ] Errors name the fix, not the failure.
- [ ] Draft saved locally with a version key.
- [ ] Draft restored with a visible banner.
- [ ] Focus moved to the step heading on change.
- [ ] Step number announced in a live region.
- [ ] Review step for payment or identity flows.
- [ ] Submit guarded by an idempotency key.
- [ ] Success on a separate route.
- [ ] Step events and field errors instrumented.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Refresh loses the form | State lives only in component memory | Persist to local storage with a debounce and version key |
| Back clears fields | The step handler resets state on navigation | Keep one state object and only change the visible step |
| Error appears with no visible field | Validation runs on submit across all steps | Validate the current step only and focus the first invalid field |
| Two orders created from one click | Button disabled client-side, no server idempotency | Send an idempotency key and return the first result on retry |
| Screen reader announces nothing on Next | No focus move and no live region | Focus the heading and announce the step number |
| Completion drops at one step only | That step's fields fail for a mechanical reason, such as a size limit | Read field-level errors and name the fix in the message |
| Draft restores stale values after a deploy | Old draft shape read into a new schema | Version the draft key and discard mismatched drafts |
| Step counter says 2 of 4 but the URL says 3 | Step index lives in state and in the route separately | Derive the route from the step index only |
| Resume offers a draft from a different form | Draft key not namespaced per form | Prefix the key with the form id and the schema version |
| Back from review loses the edit target | The review step rebuilt state from props | Keep one state object and pass only the step index |
| Submit spinner never clears on a validation error | The submitting flag is not reset on the error path | Reset in a finally block and render field errors |
| Mobile keyboard covers the Next button | A fixed footer with viewport height assumptions | Use dynamic viewport units and test on iOS Safari |
| Autofill writes into a hidden step's field | Duplicate field names across steps mounted at once | Unique names per step, and mount only the visible step |

## Copy-ready agent prompt

> Read the skill at the URL above and rebuild my multi-step form. Group fields by decision into four or fewer steps, hold one state object validated by one schema, validate on blur and on Next, save a versioned draft locally and restore it with a banner, move focus to the step heading and announce the step number, add a review step for payment flows, guard submit with an idempotency key, and instrument step views, completions and field errors. Report completion rate per step and the whole-flow rate before and after. Stop and show me the flow if a refresh loses data or a double submit can create two records.
