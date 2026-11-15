---
name: review-request-funnel
description: Ask every happy customer for a public review at the right
moment,
with a one-tap link, honest disclosure, a response routine and a
measured
conversion rate.
version: 1.0.0
license: MIT
tags: [marketing, local-seo, reviews, whatsapp, compliance]
---

# Review Request Funnel

A business with 40 reviews at 4.1 stars loses a customer to a
competitor with
400 at 4.4, even when the service is better. The gap is rarely
quality; it is
that nobody asked. Asking badly is worse than not asking: a mass SMS
after
purchase converts under 0.5% and trains people to ignore you.

The output is a funnel that asks at the moment satisfaction is
highest, in one
channel, with one tap to the review form, with suppression so nobody
is asked
twice in 90 days, and with a response routine that turns each review
into
either a thank-you or a fixed problem.

## When to use this skill

- You have fewer than 50 Google reviews and more than 500 completed orders.
- A competitor outranks you locally on review count alone.
- You are about to send a discount-for-review offer and need to know why that breaks the rules.
- Nobody has replied to a review in six months and three of them are one star.

Do NOT use for: manufacturing or buying reviews (that is fraud on
every
platform), or responding to a review bomb from a coordinated group —
that is
an escalation to the platform.

## Stage 1 — Find the moment satisfaction peaks

The ask works when the customer has just experienced the value and
before
memory fades. That moment differs by business type.

1.1 Map the delivery moment: a service visit ends at job completion, a product arrives at first successful use, a course ends at the first result.

1.2 Ask within 24 hours of that moment, and never on the same day as an invoice or a complaint.

1.3 Exclude anyone with an open ticket, a refund in progress, or a delivery delay in the last 14 days — asking an unhappy customer manufactures a one-star review.

| Business type | Best ask moment | Worst ask moment |
|---|---|---|
| Home service | 2 hours after job completion | during the invoice conversation |
| E-commerce | 7 days after delivery | on dispatch day |
| Clinic or salon | same evening | at the front desk |
| Course or coaching | after the first result | on enrolment |

Gate: one trigger event per business type, with a documented exclusion
list.

## Stage 2 — Pick one channel and one ask

Multichannel asking reads as desperation and multiplies the opt-out
rate.

2.1 Use WhatsApp where you already have an opt-in, SMS where you do not, and email only for B2B — WhatsApp click-through on a review link runs several times higher than email in practice.

2.2 Write the message in three lines: what they bought, the one-tap link, and one sentence on why it helps. No discount, no incentive, no "5 stars please".

2.3 Send exactly one request per order, with one reminder after 5 days and no third attempt.

```text
Hi <name>, thanks for the <service> on <date>. If it went well, a short
review helps other people in <city> decide. One tap, 30 seconds:
<short link>

No pressure either way — reply here if anything was not right.
```

Gate: one channel, one request, one reminder, and the message fits
three
lines.

## Stage 3 — Make the link one tap and the form short

Every extra tap loses roughly half the remaining intent. The review
form is
where most funnels die.

3.1 Use the platform's short review link and test it on a phone on mobile data, not on office wifi.

3.2 Pre-fill what the platform allows, and give the customer two sentences of guidance in the message — "what you came for and whether it worked" — because a blank box stops people.

3.3 Put a QR code on the invoice and at the counter for walk-in businesses, pointing at the same short link.

3.4 Generate the QR code from the same short link, so the code and the message never point at different forms:

```bash
qrencode -o review-qr.png -s 8 -m 2 "https://g.page/r/<place-id>/review"
```

Gate: the link opens the review form in one tap from a phone, and the
whole
path takes under 45 seconds.

## Stage 4 — Never gate, never incentivise

Asking only happy customers for reviews, or paying for them, breaks
platform
policy and consumer law in India.

4.1 Ask everyone who is not excluded by the rule in Stage 1, and route unhappy customers to support in parallel, not instead of the review ask.

4.2 Never offer a discount, a gift, a prize draw or a refund in exchange for a review — platforms detect it and remove the reviews, and the Indian consumer-protection rules treat it as a misleading practice.

4.3 Keep the ask wording free of "5 star" or "positive" — a review request that names the rating is a solicitation of a specific outcome.

| Practice | Allowed | Why |
|---|---|---|
| Ask all customers | yes | honest solicitation |
| Ask only happy customers | no | review gating, policy violation |
| Discount for a review | no | incentive, removable and illegal in spirit |
| Reply to every review | yes | platform-supported |
| Remove a review by asking the customer | no | only the platform can remove |

Gate: the ask goes to all non-excluded customers, and no message
mentions an
incentive or a rating.

## Stage 5 — Suppress so nobody is asked twice

Repeated asks are the fastest way to a spam report on WhatsApp and a
mute on
email.

5.1 Suppress any customer who reviewed in the last 90 days, unsubscribed, or opened a ticket in the last 30 days.

5.2 Cap at two asks per customer per year, regardless of how many orders they place.

5.3 Keep the suppression list in the same system that sends, not in a spreadsheet someone updates weekly.

Gate: a customer with three orders in a month receives one request,
not three.

## Stage 6 — Respond to every review within 48 hours

A reply is public proof that someone is listening, and it is read by
far more
people than the review itself.

6.1 Reply to positive reviews in two sentences: thank by name, mention the specific thing they praised.

6.2 Reply to negative reviews in four: acknowledge the specific problem, state what changed, offer a direct channel, and sign with a name.

6.3 Never argue, never blame the customer, and never paste the same template under every review — repetition is visible and reads as indifference.

Gate: 100% of reviews from the last 30 days have a reply, and no two
replies
are identical.

## Stage 7 — Handle the one-star reviews with a script

An angry review answered well converts better than no review at all.
Answer it
with a process, not adrenaline.

7.1 Respond within 24 hours, publicly and briefly, then move the detail to a private channel.

7.2 State the fix in the public reply if there is one — "we changed our delivery window to 48 hours after this" — because future customers read the fix, not the complaint.

7.3 If the review is fake or abusive, report it through the platform's process and reply once, factually, without escalating in public.

Gate: every one-star review has a reply within 24 hours that names a
specific
action.

## Stage 8 — Measure conversion, not volume

Requests sent is an activity metric. Conversion from request to
published
review is the number that decides whether the funnel works.

8.1 Track four numbers per month: requests sent, reviews published, conversion rate, and average rating.

8.2 Expect 3% to 8% conversion from a single WhatsApp request with a one-tap link; below 2% means the timing or the link is wrong, not the wording.

8.3 Attribute reviews to the trigger event, so you can see whether the 24-hour ask beats the 7-day ask.

Gate: conversion rate per trigger window is reported monthly with the
rating
trend beside it.

## Stage 9 — Close the loop with the team

Reviews are feedback with a public audience. Route the content to the
people
who can act on it.

9.1 Send a weekly digest to the operations lead with the themes from the last 20 reviews, quoted, not summarised into adjectives.

9.2 Track the fix for every recurring complaint to a date, and mention the fix in the next reply to that theme.

9.3 Put the current rating and count on the team dashboard, because the number moves slowly and needs to stay visible.

Gate: a weekly digest exists, and every recurring complaint has a
dated fix.

## Worked example - 3.9 to 4.6 stars in five months

A home-cleaning service in Pune, 1,800 completed jobs per quarter, 38
reviews
at 3.9 stars.

| Month | Requests | Reviews | Conversion | Rating | Change made |
|---|---|---|---|---|---|
| 0 | 0 | 38 total | — | 3.90 | baseline, no ask |
| 1 | 410 | 14 | 3.4% | 3.98 | WhatsApp ask at 2 hours |
| 2 | 460 | 19 | 4.1% | 4.10 | one-tap short link |
| 3 | 480 | 26 | 5.4% | 4.28 | exclusion list for open tickets |
| 4 | 470 | 31 | 6.6% | 4.44 | QR on the invoice |
| 5 | 455 | 30 | 6.6% | 4.60 | replies to 100% within 48 h |

The jump in month 3 came from the exclusion list, not from better
copy. Before
it, 22% of requests went to customers with an open complaint, and
those
produced most of the one-star reviews. Removing them cut the request
volume
slightly and raised the rating every month after.

The conversion jump in month 4 came from the QR code: walk-in and
same-building customers who never read WhatsApp messages reviewed from
the
invoice.

One thing did not work. An SMS reminder at day 5 to customers who had
already
ignored WhatsApp produced 2 reviews from 300 sends and 11 opt-outs. It
was
removed in month 4; the reminder now goes on the same channel as the
ask,
once.

## Quality checklist

- [ ] One trigger event per business type, documented.
- [ ] Exclusion list covers open tickets, refunds and delays.
- [ ] One channel, one request, one reminder.
- [ ] Message fits three lines and names no rating.
- [ ] Short link tested on a phone on mobile data.
- [ ] Whole path completes in under 45 seconds.
- [ ] Every non-excluded customer is asked, with no gating.
- [ ] No incentive of any kind appears in the ask.
- [ ] 90-day suppression and a two-per-year cap enforced in the sending system.
- [ ] 100% of reviews from the last 30 days have a reply.
- [ ] No identical replies across reviews.
- [ ] One-star reviews answered within 24 hours with a named action.
- [ ] Conversion rate reported per trigger window.
- [ ] Weekly digest with quoted themes sent to operations.
- [ ] Every recurring complaint has a dated fix.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| 0.4% conversion from a mass SMS | The ask arrived days after the moment and had no one-tap link | Move to WhatsApp within 24 hours of the trigger event |
| Rating falls while review count rises | Unhappy customers with open tickets are being asked | Add the exclusion list before the next send |
| Reviews removed in a batch | A discount or a "5 star" request in the message | Remove the incentive and the rating wording, then re-ask |
| Customer says they were asked four times | Suppression lives in a spreadsheet, not in the sender | Move suppression into the sending system with a 90-day rule |
| Link opens a login wall | The platform's long URL instead of the short review link | Use the short link and test on mobile data |
| One-star review unanswered for a week | No owner and no alert | Route new reviews to a channel with a 24-hour alert |
| Same template reply on 40 reviews | Replying from a saved snippet library | Write the specific thing they praised into the first line |

## Copy-ready agent prompt

> Read the skill at the URL above and build my review funnel. Identify the trigger event and the exclusion list, write the one-channel three-line ask with a one-tap link and no incentive, set 90-day suppression and a two-per-year cap in the sending system, and add the 48-hour reply routine with a script for one-star reviews. Then report requests sent, reviews published, conversion rate per trigger window and the rating trend for the last three months. Stop and show me the message if it names a rating or offers any incentive.
