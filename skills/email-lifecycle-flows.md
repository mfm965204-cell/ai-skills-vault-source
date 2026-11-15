---
name: email-lifecycle-flows
description: Write and wire the five lifecycle emails that earn most of the revenue - welcome, activation, abandoned action, win-back and receipt - with triggers, timing and one measurable goal each.
version: 1.0.0
license: MIT
tags: [marketing, email, lifecycle, automation, retention]
---

# Email Lifecycle Flows

A newsletter sent to a 20,000-person list earns a fraction of what 5 triggered emails earn, because a campaign is sent to everyone at the same time regardless of what each person just did. Lifecycle email is sent because of behaviour, and behaviour is what makes it worth opening.

This skill builds the five flows that do the work - welcome, activation, abandoned action, win-back, receipt - with an exact trigger, a send delay, one goal, a subject line rule, and the suppression logic that stops a user getting three emails on day one. You end with a spec a developer can implement and a copy deck a writer can fill.

## When to use this skill

- You have a list and a broadcast tool but no triggered emails.
- A new signup gets a newsletter three days later and nothing else.
- Users abandon a cart, a form or a trial and hear nothing.
- Your emails overlap and a user receives 4 in 48 hours, then nothing for a year.

Do NOT use for: deliverability infrastructure (SPF, DKIM, warmup), cold outreach to purchased lists, or SMS and push strategy. It also does not cover campaign calendars - this is triggered mail only.

## Stage 1 - Define the lifecycle states before writing copy

1.1 List the states a user can be in: signed up, activated, active, dormant, churned, paying. Five or six states is enough.

1.2 Define activation as an event, not a feeling: "created a project and invited one teammate" is activation; "engaged" is not.

1.3 Assign one email flow to each transition between states. Every email belongs to a transition; an email with no transition is a campaign.

1.4 Write the entry and exit condition for each flow. Exit on the goal event, not on the end of a sequence.

| State | Transition | Flow | Goal event |
|---|---|---|---|
| signed up | to activated | welcome + activation | activation event |
| activated | to active | usage nudge | 3 sessions in 7 days |
| active | to dormant | win-back | any session |
| dormant | to churned | last call | reply or return |
| paying | to renewing | receipt + renewal | renewal |

Gate: every flow maps to one transition and exits on one goal event.

## Stage 2 - Design the welcome flow as three emails, not one

2.1 Email 1, immediate: confirm the account, deliver the thing they asked for, and state the one next action.

2.2 Email 2, day 2: the single most useful thing they can do in the product, with the exact steps, in under 120 words.

2.3 Email 3, day 5: a short proof - one customer story with a number - and the same next action again.

2.4 Stop the flow the moment activation happens. A user who activated on day 1 must not receive day-5 activation copy.

2.5 Keep the welcome flow out of the newsletter list until it ends. A promo email on day 1 undercuts the sequence.

| Email | Send at | Length | Goal |
|---|---|---|---|
| welcome | immediately | 80 words | confirm and one action |
| how-to | +2 days | 120 words | first activation step |
| proof | +5 days | 150 words | repeat the same action |

Gate: three emails, one goal, and a hard stop on the goal event.

## Stage 3 - Write the abandoned-action flow

3.1 Trigger on the abandonment event with a real timestamp - cart abandoned, form started but not submitted, trial ended without a payment method.

3.2 Wait 1-4 hours for the first email. Immediate abandonment emails read as surveillance and convert worse than a short delay.

3.3 Email 2 at 24 hours: remove friction, name the likely blocker, offer help. Do not add a discount yet.

3.4 Email 3 at 72 hours: one incentive, with an expiry. Only if margin allows; a permanent discount trains waiting.

3.5 Suppress anyone who completed the action, and anyone in the win-back flow.

```text
trigger: cart_abandoned
wait: 2 hours
if not order_placed:
  send: cart-1 (friction removal, no discount)
wait: 22 hours
if not order_placed:
  send: cart-2 (objection answer)
wait: 48 hours
if not order_placed:
  send: cart-3 (one incentive, 72-hour expiry)
exit: order_placed
```

Gate: the flow exits on the goal event and cannot send twice for the same abandoned item.

## Stage 4 - Build the receipt and renewal flow for trust

4.1 Receipt within 60 seconds of payment, with the amount, the last 4 digits, the date in dd/mm/yyyy, and a support path.

4.2 A receipt is not a marketing email: no upsell in the body, no tracking pixel in the payment details section.

4.3 Renewal reminders at 30, 7 and 1 day before, with the amount that will be charged. A surprise charge costs more in support than the reminder costs in churn.

4.4 Failed payment recovery: retry at 1, 3 and 7 days with a plain link to update the card, and stop all marketing mail until it is fixed.

| Email | Timing | Must contain |
|---|---|---|
| receipt | under 60 s | amount, date, last 4 digits, support |
| renewal 30 days | T-30 | amount, date, cancel path |
| renewal 7 days | T-7 | amount, date, cancel path |
| payment failed | 1, 3, 7 days | update-card link only |

Gate: a receipt arrives within 60 seconds in a live test, and every renewal email names the amount.

## Stage 5 - Design win-back with a real reason to return

5.1 Trigger on 30-45 days of no session for a weekly-use product, or 2 missed cycles for a monthly one. A fixed 30 days for every product is a guess.

5.2 Email 1: what changed since they left. Two specific product changes, no "we miss you".

5.3 Email 2: one offer with an expiry, or a human offer of a 15-minute call. For B2B, the call outperforms the discount.

5.4 Email 3: the goodbye, with a one-click unsubscribe and a single question about why they left. This email produces the most useful feedback of the five flows.

5.5 Stop after 3 emails. A fourth is a spam complaint waiting to happen.

| Day | Email | Content |
|---|---|---|
| 0 | what changed | 2 specific improvements |
| 4 | offer | expiry-dated, one only |
| 9 | goodbye | one question, one-click out |

Gate: three emails maximum, and the goodbye email records the answer in a field, not in a reply inbox nobody reads.

## Stage 6 - Set the suppression rules that stop the overlap

6.1 One priority order: transactional > payment failure > lifecycle flow > campaign. A lower priority never overrides a higher one.

6.2 Maximum one marketing email per 24 hours and three per week per person, regardless of how many flows they qualify for.

6.3 A user in the welcome flow is excluded from win-back and campaigns.

6.4 A user with a failed payment is excluded from everything except payment recovery.

6.5 Store the last send timestamp per person and check it at send time, not at schedule time.

```sql
-- eligibility check at send time
SELECT u.id
FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM sends s
  WHERE s.user_id = u.id AND s.sent_at > now() - interval '24 hours'
)
AND NOT EXISTS (
  SELECT 1 FROM flow_state f
  WHERE f.user_id = u.id AND f.blocking = true
);
```

Gate: a test user qualifying for 3 flows receives at most 1 email in 24 hours.

## Stage 7 - Write subject lines to a rule, not a mood

7.1 Under 45 characters, so a phone shows the whole line.

7.2 No false urgency, no "Re:" or "Fwd:" fakery, no all caps, and at most one emoji or none.

7.3 The preview text continues the subject; it does not repeat it. 40-90 characters of preview is what most clients show.

7.4 Test one variable at a time on the same flow, with at least 1,000 recipients per variant before reading a result.

| Rule | Target | Why |
|---|---|---|
| subject length | under 45 chars | mobile truncation |
| preview length | 40-90 chars | continues the subject |
| emoji | 0 or 1 | spam and rendering risk |
| variants | 1 change at a time | readable result |
| sample | 1,000+ per variant | noise below that |

Gate: every subject in the deck passes the length and fakery checks.

## Stage 8 - Instrument the five flows before launch

8.1 Per email: sent, delivered, opened (with the caveat that opens are unreliable since privacy protection), clicked, goal completed, unsubscribed.

8.2 Per flow: goal completion rate, time to goal, and revenue or retention attributed to the flow.

8.3 Attribution: last non-direct click within 7 days, stated plainly in the report so nobody over-reads it.

8.4 A control group of 5-10% held out per flow, where volume allows. Without it, you are measuring the season, not the email.

| Metric | Healthy range | Red flag |
|---|---|---|
| welcome goal rate | 15-40% | under 8% |
| cart abandonment recovery | 5-15% | under 2% |
| win-back return rate | 3-10% | under 1% |
| unsubscribe per send | under 0.4% | over 1% |
| spam complaint | under 0.05% | over 0.1% |

Gate: all five flows have a goal event tracked, and one flow has a held-out control group.

## Stage 9 - Review monthly and prune

9.1 Monthly: goal rate per flow, unsubscribe rate, and complaint rate. A flow below half the healthy range gets rewritten or retired.

9.2 Retire a flow that has not moved its goal in 3 months. A dead flow still costs sends and reputation.

9.3 Refresh copy every 6 months; the audience sees the same words repeatedly and the open rate decays.

9.4 Keep the spec and the copy deck in the same repo as the product, versioned, so the flow that ships matches the flow that was approved.

Gate: a monthly review with 3 numbers per flow, and one documented change from it.

## Worked example

A subscription tool with 12,000 signups a month and no triggered mail.

| Flow | Emails | Goal rate | Revenue effect |
|---|---|---|---|
| welcome | 3 | 34% activation | +1,900 activations/month |
| abandoned checkout | 3 | 9% recovery | +₹4,10,000/month |
| receipt and renewal | 4 | 0.3% failed payment | ₹90,000 recovered |
| win-back | 3 | 6% return | +640 returning users |
| payment recovery | 3 | 41% recovered | ₹2,20,000/month |

The biggest gain came from suppression, not copy: before the priority order existed, 22% of users got 3 emails in 2 days and unsubscribed at 1.4%. After, the unsubscribe rate fell to 0.3% and total sends dropped 18%.

## Quality checklist

- [ ] Five or six lifecycle states defined
- [ ] Activation defined as an event, not a feeling
- [ ] Every flow mapped to one transition and one goal event
- [ ] Welcome flow stops the moment activation happens
- [ ] Abandoned-action first email delayed 1-4 hours
- [ ] No discount in the first abandonment email
- [ ] Receipt sent within 60 seconds with amount and date
- [ ] Renewal reminders at 30, 7 and 1 day with the amount
- [ ] Win-back capped at three emails
- [ ] Suppression priority order written down
- [ ] Maximum one marketing email per 24 hours enforced at send time
- [ ] Subjects under 45 characters, no fakery
- [ ] Preview text continues the subject
- [ ] Goal event tracked per flow
- [ ] Control group held out where volume allows
- [ ] Monthly review with 3 numbers per flow

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| User gets 3 emails in a day | No priority order or send-time check | One per 24 hours, checked at send |
| Welcome flow continues after activation | Exit condition is sequence end, not goal | Exit on the goal event |
| Abandonment email feels creepy | Sent within minutes of the event | Wait 2 hours minimum |
| Discounts train waiting | Permanent incentive, no expiry | One incentive with a 72-hour expiry |
| Surprise charge complaints | Renewal email missing the amount | Name amount and date at T-30, T-7, T-1 |
| Unsubscribe rate climbing | Too many flows targeting the same person | Suppression rules plus a frequency cap |
| Win-back emails read as guilt | "We miss you" copy | Two specific product changes instead |
| Opens look great, clicks do not | Privacy-protected opens inflating the metric | Judge on goal completion, not opens |
| Nobody can tell if a flow works | No control group, no goal event | Hold out 5-10% and track the goal |
| Flows multiply and nobody owns them | No owner per flow | One owner and one review date per flow |

## Copy-ready agent prompt

> Read the skill at the URL above and design my lifecycle email flows. Ask me: what my product is, how I define activation, my signup volume, my average order value, and which tool sends my mail. Then give me the five flows with the exact trigger, the delay before each email, one goal event per flow, the copy deck with subject under 45 characters and preview text that continues it, the suppression priority order with a one-per-24-hours cap checked at send time, the receipt and renewal timings, and the instrumentation table with a healthy range per metric. Include the 5-10% control group and the monthly review. Tell me which flows would fire for a user who activates on day one, and confirm they would receive exactly one email.
