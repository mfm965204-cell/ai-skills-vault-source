---
name: accessible-form-validation
description: Build a form whose errors are announced, focus lands on the right field, and the validation never loses what the user typed, tested against a keyboard and a screen reader.
version: 1.0.0
license: MIT
tags: [frontend, forms, accessibility, validation, ux]
---

# Accessible Form Validation

A red border and a `div` with the text "Invalid input" is what most forms ship. A screen reader user hears nothing, a keyboard user tabs past the field that failed, and a 40-field form resets on submit and loses every answer.

This skill builds validation as a layer with four rules: errors are in the DOM next to their field, focus moves to the first error, the message names the fix, and the submit path never clears data. You end with a working form pattern, an aria wiring checklist and a test list that includes a screen reader pass.

## When to use this skill

- Your form uses `alert()` or a toast to report a validation failure.
- A user submits twice because nothing visible happened.
- Errors are shown only on submit and only as a border colour.
- Your form has 20+ fields, multi-step flow, or a file upload, and you have never tested it with a keyboard.

Do NOT use for: server-side validation design on its own (this covers the client contract with it), authentication architecture, or payment compliance. It also does not replace a real accessibility audit for legal conformance.

## Stage 1 - Decide when each field validates

1.1 Validate on blur for format errors (email, phone, PIN code), and on submit for everything else. Validating on every keystroke punishes a user mid-typing.

1.2 Re-validate on input only after a field has already failed once. This is the pattern that lets an error clear as soon as it is fixed.

1.3 Never validate on blur if the field is empty and untouched. Tabbing through a form must not produce 12 errors.

1.4 Debounce remote checks (username availability, coupon code) by 400-600 ms and cancel the in-flight request on the next keystroke.

| Field type | Trigger | Re-validate |
|---|---|---|
| email, phone | blur | input, after first error |
| required text | submit | input, after first error |
| password strength | input, debounced 300 ms | input |
| username availability | input, debounced 500 ms | input |
| file upload | on change | on change |

Gate: no field shows an error before the user has interacted with it or pressed submit.

## Stage 2 - Put the message in the DOM beside the field

2.1 The error element sits immediately after the input in DOM order, not in a summary at the top.

2.2 Give the input `aria-describedby` pointing at the error element's id, so a screen reader reads the error when focus lands.

2.3 Add `aria-invalid="true"` on the input when it fails, and remove it when it passes. Leaving it set is a common bug.

2.4 Use `role="alert"` only on the summary, not on every field. Twelve alerts firing at once is unusable.

2.5 The label is a real `<label for>`. A placeholder is not a label: it disappears on typing and screen readers may skip it.

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email"
       aria-describedby="email-error" aria-invalid="true" />
<p id="email-error" class="error">
  Enter an email in the form name at domain dot com
</p>
```

Gate: every input has a `<label for>`, and every possible error has a described-by target that exists in the DOM.

## Stage 3 - Write messages that name the fix

3.1 State what is wrong and what to do, in that order, in under 90 characters: "Enter a 6-digit PIN code", not "Invalid input".

3.2 Never use the field's own name alone. "Email" tells nothing; "Email needs an @ symbol" does.

3.3 Do not blame the user. "That date is in the past" beats "You entered an invalid date".

3.4 Keep one message per field. Three simultaneous complaints on one input is a wall, not help.

| Bad message | Better message | Why |
|---|---|---|
| Invalid input | Enter a 6-digit PIN code | names the format |
| Required | Enter your name | names the field and the action |
| Error: email | Email needs an @ symbol | specific and short |
| Wrong password | Password must be 8+ characters | actionable |
| Invalid file | File must be a PDF under 5 MB | states both limits |

Gate: every message passes the "could a stranger fix it without asking" test.

## Stage 4 - Move focus, once, to the first error

4.1 On submit failure, focus the first invalid field. One focus move, not a scroll animation per error.

4.2 Focus the field, not the error text. The screen reader then reads label, value, error via `aria-describedby`.

4.3 Show a summary above the form with `role="alert"` and links to each field. This is required when the form is longer than one screen.

4.4 Do not trap focus in the summary. The user must be able to Tab from the summary into the fields.

```js
function focusFirstError(form) {
  const first = form.querySelector('[aria-invalid="true"]');
  if (!first) return false;
  first.focus({ preventScroll: false });
  return true;
}
```

Gate: submitting an empty 10-field form moves focus to field 1 and announces one summary, not 10 errors.

## Stage 5 - Never lose the user's input

5.1 The submit handler returns `false` or calls `preventDefault()` before any reset. A reset on failure is the worst bug in this skill.

5.2 For a server-rendered form, re-render with the posted values filled in and errors attached; do not redirect to a blank form.

5.3 Persist draft state to `sessionStorage` for forms over 10 fields, and clear it on success only.

5.4 For a multi-step form, keep state in one object and never unmount a completed step's data.

5.5 On a 422 from the API, map field errors to the same `aria-describedby` targets so client and server errors look identical.

```js
async function onSubmit(e) {
  e.preventDefault();                     // never reset on failure
  const errors = validate(new FormData(e.target));
  renderErrors(e.target, errors);
  if (Object.keys(errors).length) return focusFirstError(e.target);
  const res = await fetch("/api/save", { method: "POST", body: new FormData(e.target) });
  if (res.status === 422) {
    const body = await res.json();
    renderErrors(e.target, body.errors);  // same targets, same markup
    return focusFirstError(e.target);
  }
  sessionStorage.removeItem("draft");
}
```

Gate: a failed submit leaves every typed value in place, verified by hand in the browser.

## Stage 6 - Handle the file upload case

6.1 Accept types and sizes in the UI text before the picker opens: "PDF, up to 5 MB". The constraint is information, not a surprise.

6.2 Validate size and type on change and on submit. A user can rename a 40 MB file to `.pdf`.

6.3 Announce progress for anything over 2 MB, with a `role="status"` region that updates at most every 500 ms.

6.4 Show the selected file name with a remove button that is keyboard reachable.

Gate: an oversized file produces a message naming the limit, and the rest of the form is untouched.

## Stage 7 - Test with a keyboard, then a screen reader

7.1 Tab through the whole form. Every control reachable, focus visible, order matching the visual order.

7.2 Submit with errors using the keyboard only. Focus must land on the first invalid field and the message must be readable.

7.3 Run a screen reader pass: NVDA on Windows, VoiceOver on macOS, TalkBack on Android. One form, 10 minutes each.

7.4 Check zoom at 200% and 400%: no control clipped, no horizontal scroll on a 320 px viewport.

7.5 Check the error state is not colour-only. A red border with no text fails for 8% of men with a colour-vision deficiency.

| Test | Pass condition |
|---|---|
| keyboard only | all controls reachable, focus visible |
| focus order | matches visual order |
| screen reader | label, value and error read together |
| 200% zoom | no clipping, no overlap |
| 320 px width | no horizontal scroll |
| error without colour | text still explains the failure |

Gate: all 6 tests pass on the real form, not a demo.

## Stage 8 - Keep the markup honest in review

8.1 A PR that adds an input without a label fails review. Add it to the checklist, not to a wiki.

8.2 Add an automated check: axe-core in a component test, failing on `label`, `aria-describedby` and `aria-invalid` violations.

8.3 Snapshot the error markup for one field. It is the markup every other field copies.

8.4 Log validation failures by field name on the server. A field that fails 40% of the time is a badly designed field, not a user error.

Gate: axe-core passes on the form with errors displayed, not only in the clean state.

## Stage 9 - Measure whether the form works

9.1 Track three numbers per field: error rate, time to complete, and abandonment at that step.

9.2 A field with an error rate above 15% needs a better input, not a better message. A date picker beats a text field for dates.

9.3 A step with abandonment above 20% needs fewer fields. Removing one field usually beats any validation improvement.

9.4 Review the numbers monthly against the previous month. Forms degrade as business rules are added.

9.5 Compare error rate against field type, not only against last month. A phone field failing at 8% is normal; a name field failing at 8% is a bug.

9.6 Fix the input before the copy. A PIN code field that accepts letters will fail no matter how good the message is.

Gate: the three numbers exist per field for 2 consecutive months.

## Worked example

A 24-field KYC form, before and after.

| Item | Before | After |
|---|---|---|
| Error display | toast, one message | inline per field plus summary |
| Focus on failure | none | first invalid field |
| Screen reader | errors not announced | described-by on 24 fields |
| Data on failure | reset to blank | all values preserved |
| Fields with error rate over 15% | 5 | 1 |
| Abandonment at step 2 | 31% | 12% |
| axe-core violations | 14 | 0 |

The largest single gain came from preserving values on failure: 31% abandonment at step 2 dropped to 12% in one release, before any message was rewritten.

## Quality checklist

- [ ] Validation triggers chosen per field type
- [ ] No error before interaction or submit
- [ ] Re-validation only after a first failure
- [ ] Remote checks debounced 400-600 ms and cancelled
- [ ] Error element in the DOM next to its input
- [ ] `aria-describedby` wired to an existing id on every field
- [ ] `aria-invalid` set and cleared correctly
- [ ] Real `<label for>` on every input, no placeholder labels
- [ ] Every message names the fix in under 90 characters
- [ ] One message per field, no stacked complaints
- [ ] Focus moves to the first invalid field on submit
- [ ] Summary with `role="alert"` for long forms
- [ ] Submit never resets values on failure
- [ ] Server 422 errors reuse the same markup and targets
- [ ] File upload limits stated before the picker and enforced after
- [ ] axe-core passes with errors displayed

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Screen reader hears no error | Message not referenced by `aria-describedby` | Wire the id, set `aria-invalid` |
| User tabs past the failing field | Focus never moved on failure | Focus the first invalid field |
| Form clears after a failed submit | Reset called in the submit handler | `preventDefault()` before validation |
| Errors appear while tabbing through | Validating empty untouched fields | Validate on blur only after interaction |
| 12 alerts read at once | `role="alert"` on every field message | Alert only on the summary |
| Error is invisible to some users | Colour-only signalling | Text message plus border plus icon |
| Availability check flickers | No debounce, races on response order | Debounce 500 ms, cancel in-flight |
| Renamed file accepted | Type checked by extension only | Check size and MIME on submit |
| Same error twice, client and server | Two different render paths | Map 422 errors to the same targets |
| Form passes tests, fails users | Tested clean state only | Test with errors displayed, keyboard and screen reader |
| Error rate stays high after copy rewrite | The input control is wrong for the data | Change the control, not the message |
| Draft lost on a refresh | State only in component memory | Persist to sessionStorage, clear on success |

## Copy-ready agent prompt

> Read the skill at the URL above and fix validation on my form. Ask me: how many fields, which ones are required, whether it is single-step or multi-step, and which framework I use. Then give me the per-field trigger table, the exact markup for one field with label, `aria-describedby`, `aria-invalid` and the error paragraph, the submit handler that never resets values and maps 422 server errors to the same targets, the focus-first-error function, the summary block with `role="alert"`, and the file-upload rules with size and type stated before the picker. Finish with the 6-test keyboard and screen-reader checklist and the axe-core setup. Tell me which of my current fields would show an error before the user touches them.
