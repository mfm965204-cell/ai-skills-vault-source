---
name: cold-outreach-system
description: Run outbound email and DM that gets replies without burning your domain - ICP and list building, a four-touch sequence, 90-word copy, sending infrastructure with SPF and DMARC, India compliance and reply-rate measurement.
version: 1.0.0
license: MIT
tags: [marketing, outbound, email, sales, deliverability, india]
---

# Cold Outreach System

Cold outreach fails for arithmetic reasons more often than copy reasons: 500 sends from a brand-new domain lands 400 in spam, so the reply rate is 0.2% and the copy never got a fair test.

This skill builds the machine first - a verified list, a warmed domain, a four-touch sequence - and only then the words. You finish with reply rate per touch, bounce rate under 3%, and a domain that still works next month.

## When to use this skill

- You sell a service or B2B product with a deal size above ₹25,000 and a named buyer.
- Referrals and inbound are not enough volume and you need a predictable top of funnel.
- You have 50-300 accounts you can name, not 50,000.
- A founder or one person will do the sending and handle replies personally.

Do NOT use for: B2C consumer blasts, bulk SMS or cold calls (different rules and consent regimes), or anything sent to purchased lists. Purchased lists are a legal and deliverability liability in every market.

## Stage 1 - Define the buyer and build a real list

1.1 Write the ICP in five fields: industry, company size, role, the trigger that makes them buy now, and the one thing they are measured on.

1.2 Name the trigger. "Hiring a second support person" or "just raised a seed round" beats "wants to grow" because the trigger decides the timing of the send.

1.3 Build the list from sources where the contact is public in a professional capacity: company sites, LinkedIn, conference lists, community directories, job postings.

1.4 Verify every address before sending. A bounce rate above 3% damages the domain; above 5% the provider starts throttling.

| List size | Verification target | Bounce ceiling | Expected replies at 4% |
|---|---|---|---|
| 100 | 100 verified | under 2% | 4 |
| 300 | 100 verified | under 3% | 12 |
| 1,000 | 100 verified | under 3% | 40 |
| 5,000 | 100 verified | under 3% | 200 |

1.5 Keep a "why this person" note per contact, one line. If you cannot write it, the contact does not belong on the list and the email will read like a blast.

1.6 Segment by trigger and role. One segment, one message - a single sequence for four segments produces four mediocre emails.

Gate: a verified list with a one-line reason per contact, segmented by trigger.

## Stage 2 - Build the offer and the proof

2.1 Write the offer as a specific outcome with a number and a time: "cut first-response time from 9 hours to under 2 in six weeks".

2.2 Name the proof you can show today: a named customer, a number you measured, or a work sample built for them. Proof you would have to invent is not proof.

2.3 State the cost of doing nothing. The buyer is not choosing between you and a competitor; they are choosing between you and the current mess.

2.4 Define the smallest ask that moves the deal: a 15-minute call, a reply with one question, or permission to send a 2-page teardown. Never "book a demo" as the first ask.

2.5 Write the offer in one sentence and read it aloud. If it takes two breaths, it is not ready.

Gate: one sentence offer, one piece of real proof, one small ask.

## Stage 3 - Design the sequence

3.1 Four touches over 12 working days. More than four on a cold list is harassment; fewer than three leaves money on the table.

3.2 Each touch must add something: a different angle, a relevant example, a short teardown, then a clean close.

| Touch | Day | Length | Angle | Ask |
|---|---|---|---|---|
| 1 | 0 | 90 words | the specific observation | 15-minute call |
| 2 | 3 | 60 words | one proof point with a number | reply with one line |
| 3 | 7 | 80 words | a teardown or resource made for them | permission to send it |
| 4 | 12 | 40 words | close the loop, easy out | "should I stop?" |

3.3 Send touches 1-3 in the morning IST (09:30-11:00) for Indian recipients; for US recipients, send at 20:00-22:00 IST to land in their morning.

3.4 Never send two touches in one day and never send on a Sunday. Monday and Tuesday get the best open rates for B2B in most measured cohorts (estimate; check your own).

3.5 Stop the sequence the moment there is a reply, positive or negative. Continuing after a reply is the single most common way to lose a warm lead.

3.6 Keep the sequence as configuration, so you can change a day offset without editing code:

```json
{"name":"support-automation-in","stop_on_reply":true,"send_window":["09:30","11:00"],
 "timezone":"Asia/Kolkata","skip_days":["sat","sun"],
 "steps":[
  {"day":0,"template":"t1_observation","max_words":90},
  {"day":3,"template":"t2_proof","max_words":60},
  {"day":7,"template":"t3_teardown","max_words":80},
  {"day":12,"template":"t4_close","max_words":40}
 ]}
```

3.7 Cap the total daily sends at the inbox count times 40, and fail the job rather than silently sending the overflow.

Gate: sequence written with four distinct angles and a stop rule.

## Stage 4 - Write the subject and the first line

4.1 Subject lines of 3-5 words, lowercase, no punctuation tricks, no "Re:" or "Fwd:" fakery. Anything that looks automated gets deleted.

4.2 Never use the recipient's company name as the whole subject. "Question about Acme" reads like a template because it is one.

4.3 The first line is about them, not you. A specific observation from their site, their job post or their changelog.

4.4 Ban the three openers that mark a blast: "I hope this email finds you well", "I'm reaching out because", "My name is X and I work at Y".

4.5 Put the ask in the last line, alone, so it is the last thing read.

| Subject style | Example | Works because |
|---|---|---|
| Observation | "your 9-hour first reply" | specific to them |
| Question | "still doing tickets manually?" | names the pain |
| Reference | "saw the Pune hiring post" | proves you looked |
| Blunt | "one idea for onboarding" | no hype, clear value |
| Bad | "Revolutionise your CX today!!" | reads as spam |

Gate: subject under 5 words, first line references something real about them.

## Stage 5 - Write the body

5.1 90 words for touch 1, under 60 for follow-ups. Long emails get skimmed and skimmed emails get no reply.

5.2 Structure: observation (1 sentence), implication (1 sentence), proof (1 sentence with a number), ask (1 sentence). Four sentences, one paragraph each.

5.3 No attachments on the first touch. Attachments raise spam scores and nobody opens them cold.

5.4 One link maximum, and only if it is the resource you offered. Links per email above 3 measurably increase spam classification.

5.5 Plain text. No images, no HTML signature with logos, no tracking pixels on the first touch - all three cost deliverability and none of them help a 90-word email.

5.6 Write at a grade-6 reading level and read it out loud. If you stumble, the recipient will too.

5.7 Keep templates as plain text with two variables, not twelve. Every extra variable is a merge field that will one day render as `{{first_name}}` to 300 people.

```text
Subject: your 9-hour first reply

Hi Meera - I saw the support job post for two more agents in Pune.

At 9 hours to first reply, most of that queue is the same six questions.

We cut it to under 2 hours at a 40-person clinic chain without adding staff.

Worth 15 minutes next week to see how?

- Arjun
```

5.8 Read the template with the wrong name substituted, and with a name missing. If it reads badly, the fallback is broken.

Gate: every email under 100 words, one ask, no attachment, one link or none.

## Stage 6 - Build the sending infrastructure

6.1 Send from a separate domain that resembles your brand (`getyourbrand.com`), not your primary domain. If the outbound domain burns, your invoices and support mail still arrive.

6.2 Set up SPF, DKIM and DMARC before the first send. DMARC at `p=none` first, read the reports for a week, then move to `p=quarantine`.

6.3 Warm the domain for 2-3 weeks: 10 sends a day in week 1, 20 in week 2, 30-40 by week 3. Sending 300 on day one is how a new domain dies.

6.4 Cap at 30-50 sends per inbox per day, and never more than 1 send per second. Volume above that on a new domain is the classic spam signal.

| Setup item | Value | Why |
|---|---|---|
| Sending domain | separate from primary | protects transactional mail |
| SPF | include your provider | authentication |
| DKIM | 2048-bit key | authentication |
| DMARC | `p=none` then `p=quarantine` | reporting, then enforcement |
| Warmup | 2-3 weeks, ramp 10 to 40/day | reputation |
| Daily cap per inbox | 30-50 | stays under provider radar |
| Bounce handling | suppress hard bounces immediately | protects reputation |

6.5 Suppress hard bounces and spam complaints automatically, on the first event. A second send to a hard bounce is a deliberate reputation hit.

6.6 Use 2-3 inboxes for 100+ sends a day, each with its own warmup, and route replies to one shared inbox so nobody gets missed.

Gate: SPF, DKIM and DMARC pass on a test send, warmup schedule written.

## Stage 7 - Handle India compliance and consent

7.1 Under the DPDP Act, personal data used for outreach needs a lawful basis and a purpose; record where each contact came from and why you may email them.

7.2 Honour opt-outs within 24 hours, permanently, across every list and tool. Keep the suppression list separate from the campaign tool so a tool migration does not resurrect it.

7.3 Do not buy lists, do not scrape personal emails from social profiles at scale, and do not email addresses harvested from leaked data - that is both a legal risk and a domain killer.

7.4 For phone follow-ups, check TRAI's DND rules and the calling-hour restrictions before dialling anyone; unsolicited commercial calls are regulated separately from email.

7.5 Include a physical address and a one-click unsubscribe in every email. Both are required by most providers' bulk-sender rules and reduce complaints.

7.6 Keep records of consent and opt-out for at least the period your legal advisor confirms; DPDP retention rules are still being operationalised, so do not assume a default.

Gate: a written basis per contact, opt-out processed within 24 hours in a test.

## Stage 8 - Handle replies like a person

8.1 Reply within 2 hours during the working day. Reply speed is the highest-return variable in outbound and the one most teams ignore.

8.2 Classify every reply into one of five buckets: interested, not now, wrong person, not interested, angry. Route each to a different next action.

8.3 "Not now" gets a dated follow-up in 60-90 days, not silence. That list is your warmest future pipeline.

8.4 "Wrong person" gets one question: "who owns this?" - and the contact moves to a referral, not the bin.

8.5 Negative replies get a one-line thank-you and a permanent suppression. Arguing with a no costs you the referral they might have given.

8.6 Log every reply in one place with the date, bucket and next action. Outbound without a CRM is a hobby with a spreadsheet.

8.7 Set an out-of-office rule: a reply that matches "out of office" or "on leave" is not a reply, and the sequence continues.

8.8 Keep a shared inbox with two people on rotation, and a rule that nothing sits unanswered past 4 working hours.

Gate: five buckets defined, 2-hour reply target stated, suppression tested.

## Stage 9 - Measure the four numbers that matter

9.1 Track sent, delivered, opened (unreliable, treat as a trend), replied, and positive replies. Reply rate is the only number that decides anything.

9.2 Per touch, not per campaign. A 6% overall reply rate that is 5% on touch 1 and 0.3% on touch 4 tells you the follow-ups are the problem.

| Metric | Weak | Workable | Good |
|---|---|---|---|
| Bounce rate | over 5% | 3-5% | under 3% |
| Reply rate | under 2% | 2-5% | 5-12% |
| Positive reply rate | under 1% | 1-3% | over 3% |
| Meeting rate per 100 sends | under 1 | 1-3 | over 3 |
| Spam complaints | over 0.1% | 0.05-0.1% | under 0.05% |

9.3 Change one variable per 100 sends: subject, first line, offer or ask. Below 100 sends per arm you are reading noise.

9.4 Keep a control: the same 100 contacts sent the previous version, so a seasonal shift does not look like an improvement.

9.5 Kill a sequence that is under 2% reply after 300 sends across two segments. It is the offer, not the copy, nine times out of ten.

9.6 Report reply rate by touch and by segment in one table, so the weakest touch is obvious without reading three dashboards.

9.7 Do not optimise the open rate. Pixel blocking in most mail clients makes it a guess, and chasing it leads to clickbait subjects.

Gate: a dashboard with the five metrics per touch and per segment.

## Stage 10 - Scale it or stop it

10.1 Scale volume only after two segments clear 5% reply. Scaling a 1% sequence just burns domains faster.

10.2 Add capacity by adding warmed inboxes, not by raising the per-inbox cap.

10.3 Refresh the list monthly; a list older than 90 days has moved on, changed jobs and forgotten you.

10.4 Keep the human in the loop. Automated reply handling on a ₹5 lakh deal is how you lose the deal in one message.

10.5 Review monthly: reply rate by segment, meetings booked, deals closed and revenue per 100 sends. If revenue per 100 sends is below your cost, stop and fix the offer.

Gate: monthly review with revenue per 100 sends as the headline number.

## Worked example

A 2-person agency selling support automation, ₹60,000 a month retainers.

| Week | Sends | Replies | Positive | Meetings | Notes |
|---|---|---|---|---|---|
| 1 (warmup) | 70 | 1 | 0 | 0 | domain warming, 10/day |
| 2 | 210 | 7 | 3 | 2 | 3.3% reply |
| 3 | 350 | 15 | 6 | 4 | subject change to observation style |
| 4 | 350 | 21 | 9 | 6 | 6.0% reply, 2.6% positive |

Two deals closed at ₹60,000 a month each, from 980 sends. The subject change in week 3 was worth more than the copy rewrite in week 2, which is why you change one variable at a time.

## Quality checklist

- [ ] ICP written with a buying trigger
- [ ] Every contact verified, bounce rate under 3%
- [ ] One-line reason per contact
- [ ] Segments by trigger and role
- [ ] Offer is one sentence with a number and a time
- [ ] Real proof, nothing invented
- [ ] Four touches over 12 working days, four angles
- [ ] Sequence stops on any reply
- [ ] Subject 3-5 words, lowercase
- [ ] Body under 100 words, one ask
- [ ] No attachments, one link at most, plain text
- [ ] Separate sending domain with SPF, DKIM, DMARC
- [ ] Warmup ramp written, cap 30-50 per inbox per day
- [ ] Hard bounces and complaints suppressed on first event
- [ ] Opt-out honoured within 24 hours, list kept separately
- [ ] Five reply buckets with a next action each
- [ ] Metrics per touch and per segment, revenue per 100 sends reviewed

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| 0.4% reply rate on 500 sends | New domain, no warmup, 500 sent on day two | Restart on a fresh domain, ramp 10 to 40 a day |
| 12% bounce rate | List built without verification | Verify before send, suppress hard bounces |
| Replies stop after touch 2 | Follow-ups repeat the first email | Give each touch a new angle |
| Opens 60%, replies 1% | Subject oversells, body does not deliver | Make the subject an observation, not a promise |
| Domain blacklisted | Complaints above 0.1% and no unsubscribe | Add one-click unsubscribe, suppress complainers |
| Prospect replies angrily | Sequence continued after a soft no | Stop the sequence on any reply, permanently |
| Meetings book but nobody shows | Ask was a demo link with no context | Ask for 15 minutes and confirm the agenda in the reply |
| Works at 100 sends, fails at 1,000 | Same inbox scaled 10x | Add warmed inboxes instead of raising the cap |
| 300 emails sent with `{{first_name}}` visible | A missing field with no fallback | Always define a fallback value per merge field |
| Sequence continued after an out-of-office | Auto-reply counted as a reply, or not counted at all | Match out-of-office patterns and continue the sequence |

## Copy-ready agent prompt

> Read the skill at the URL above and build a cold outreach system with me. Ask me: what I sell, the deal size, my ICP, how many contacts I can name, and whether my domain is warm. Then write the ICP with a buying trigger, the one-sentence offer with real proof, and a four-touch sequence with four different angles and word counts. Then give me the sending infrastructure checklist with SPF, DKIM, DMARC values and a warmup ramp, the India compliance rules I must follow, the five reply buckets, and a tracking sheet with reply rate per touch. Do not write a sequence that runs over 100 words per email, and do not invent a case study or a number I have not given you.
