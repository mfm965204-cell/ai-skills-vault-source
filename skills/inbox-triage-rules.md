---
name: inbox-triage-rules
description: Turn a shared or personal inbox into a routed queue with
five buckets, rules that label instead of delete, template replies and
a measured response time.
version: 1.0.0
license: MIT
tags: [automation, email, triage, support, operations]
---

# Inbox Triage Rules

An inbox with 4,000 unread messages is not a backlog; it is an
untriaged queue with no owner, no priority and no response time. The
work is not reading faster. It is deciding once, in rules, what
happens to each kind of message.

The output is five buckets with rules that label and archive rather
than delete, an escalation path for the senders who matter, ten
template replies for the questions that repeat, and three numbers:
time to first response, messages needing a human per day, and the
count of anything missed.

## When to use this skill

- A shared inbox has more than one person replying and no one knows who answered what.
- You answer the same eight questions every week in your own words.
- A customer email sat for four days because it arrived during a launch week.
- You are about to turn on an auto-reply and want it to route rather than promise.

Do NOT use for: transactional email delivery and deliverability
(different problem, different records), or a full helpdesk migration —
that is a ticketing tool decision.

## Stage 1 — Count what actually arrives

Rules are built from the distribution of mail, not from the memorable
messages. Measure a week first.

1.1 Export one week of headers — sender domain, subject, received time — from the mail provider's API or a mailbox export.

1.2 Group by sender type: customer, vendor, automated notification, internal, newsletter, spam.

1.3 Count how many need a human reply versus how many need a decision or nothing at all; in most inboxes 70% to 85% need nothing.

| Sender type | Typical share | Needs a reply | Destination |
|---|---|---|---|
| Automated notification | 40% | no | label plus archive |
| Newsletter | 20% | no | read-later label |
| Vendor | 15% | sometimes | vendor label, weekly review |
| Customer | 15% | yes | queue with SLA |
| Internal | 10% | yes, fast | VIP path |

Gate: a table of sender type, count and share for one week, and the
share that needs a reply.

## Stage 2 — Define five buckets and nothing more

Five buckets is the maximum a person can hold in their head. Each
bucket maps to a label and a rule.

2.1 Now: needs a reply within 4 working hours — customers with an open order, anything from a VIP sender.

2.2 Today: needs a reply within 24 hours — vendor questions, partnership requests, billing.

2.3 This week: needs a decision, not a reply — proposals, contracts, invoices to approve.

2.4 Reference: needs nothing now but must be findable — receipts, statements, confirmations.

2.5 Trash: nothing needed ever — newsletters you never read, notifications with a dashboard.

Gate: every message in the inbox has exactly one bucket, and no
message is unlabelled at end of day.

## Stage 3 — Write rules that label and archive, never delete

A rule that deletes is a rule you cannot audit. Label plus archive is
reversible and searchable.

3.1 Start with 10 rules covering the top 10 sender patterns from Stage 1 — domain matches, subject prefixes like "Your receipt" or "Build failed".

3.2 Each rule sets a label and removes the inbox flag; nothing is deleted, and nothing is forwarded outside the account.

3.3 Order matters: the specific rules run before the general ones, so a customer at a vendor domain is not caught by the vendor rule.

```text
Rule 3  if from matches "@stripe.com" and subject contains "receipt"
        then label "Reference/Receipts", skip inbox
Rule 4  if from matches "@github.com" and subject contains "[build]"
        then label "Reference/Builds", skip inbox
Rule 5  if to matches "support@" and from in VIP list
        then label "Now", keep in inbox, notify #support
Rule 6  if from matches "@bigvendor.in"
        then label "Today/Vendor", keep in inbox
```

Gate: 10 rules live, each with a label and a skip-inbox action, and a
week of mail is labelled correctly by spot-checking 30 messages.

## Stage 4 — Keep the humans' mail out of the rules

Rules that touch a colleague's mail break trust faster than any missed
message.

4.1 Exclude internal domains from every auto-archive rule, so a teammate's message always reaches a person.

4.2 Give named people a VIP label that survives all rules and notifies a channel.

4.3 Never auto-forward mail to an external address, and never grant a rule the ability to send on your behalf.

Gate: an internal sender and each VIP reach the inbox regardless of
any rule.

## Stage 5 — Set the response promise per bucket

A promise without a number is a hope. Put the number in the rule and
the auto-reply.

5.1 Now: first response within 4 working hours; Today: within 24 working hours; This week: a decision within 5 working days.

5.2 Set an auto-reply that states the promise for the bucket and nothing else — no "we will get back to you shortly", which promises everything.

5.3 Alert the channel when a Now message passes 2 hours without a reply, because silent breach is the failure this fixes.

Gate: each bucket has a stated number, and a breached Now message
produces an alert within 2 hours.

## Stage 6 — Template the ten questions that repeat

Templates are not for customers you do not care about; they are how
you answer the tenth identical question in the same words as the
first.

6.1 From the week's customer mail, list the ten questions asked most often with the exact wording customers use.

6.2 Write one reply per question, under 120 words, with the answer in the first line and the next step in the last.

6.3 Store them as snippets with a short trigger, and edit the snippet when the answer changes rather than typing a correction.

Gate: 10 snippets exist, each under 120 words, and 60% of customer
replies in a week used one.

## Stage 7 — Share the inbox without doubling the work

A shared inbox needs an assignment rule, or two people answer and one
customer gets two replies.

7.1 Assign on open: whoever opens a message is the owner, and the label changes to In-progress with their name.

7.2 Reply from the shared address, never from a personal one, so the thread stays in the shared history.

7.3 Close by changing the label to Done and setting a follow-up date only when a real follow-up is owed.

Gate: every open customer thread has one named owner and no thread has
two replies from two people.

## Stage 8 — Review the pile weekly, not daily

A daily zero-inbox target creates busywork. A weekly review of what
remains is the useful habit.

8.1 Once a week, sort by oldest unread and delete or label everything older than 30 days — the decision is the point, not the reading.

8.2 Count what was missed: messages older than 3 days that needed a reply. That number is the health metric.

8.3 Review the rules monthly against the current top senders; a rule for a service you stopped using is noise with a label.

8.4 Find the missed messages with a saved search rather than by scrolling:

```text
in:inbox is:unread older_than:3d -label:Reference -label:Trash
label:Now -label:Done older_than:2h
label:Today -label:Done older_than:24h
```

Gate: a weekly review happens with a missed count recorded, and rules
are revised at least monthly.

## Stage 9 — Measure three numbers and publish them

Three numbers are enough to know whether triage is working.

9.1 Time to first response per bucket, measured from receipt, not from open.

9.2 Messages needing a human per day — the number that falls when rules improve.

9.3 Missed count per week — messages needing a reply that sat over 3 days.

Gate: all three numbers are on one page and reviewed weekly with the
team.

## Worked example - 4,200 unread to 40

A 6-person company sharing `support@` and `hello@`, 4,200 unread
messages at the start.

| Week | Unread | Needs a human per day | Time to first response | Change |
|---|---|---|---|---|
| 0 | 4,200 | 96 | 2.5 days | baseline |
| 1 | 1,900 | 62 | 1.1 days | 10 rules, label and archive |
| 2 | 620 | 48 | 6 hours | five buckets and bucket labels |
| 3 | 180 | 41 | 3.5 hours | 10 snippets |
| 4 | 40 | 38 | 1.8 hours | assignment on open |
| 8 | 35 | 36 | 1.4 hours | weekly review and rule pruning |

The decisive change was the first 10 rules, and none of them was
clever: receipts from two payment providers, build notifications, four
calendar and meeting tools, and three vendor domains. They removed
2,100 messages in a week.

The failure worth copying the fix for: an early rule auto-archived
anything from `@bigvendor.in`, including a renewal notice that was
also a contract change. The renewal was found three weeks later. The
rule now keeps vendor mail in the inbox under Today and only archives
receipts with "invoice" or "receipt" in the subject.

The other lesson: the auto-reply that said "we will get back to you
shortly" produced 14 follow-up emails in a day asking when. Replacing
it with "first response within 24 working hours for this address" cut
follow-ups to two.

## Quality checklist

- [ ] One week of headers counted by sender type and share.
- [ ] Five buckets defined, each with a label.
- [ ] Every message labelled at end of day.
- [ ] 10 rules live, each labelling and skipping the inbox.
- [ ] Specific rules ordered before general ones.
- [ ] No rule deletes mail.
- [ ] Internal domains excluded from auto-archive.
- [ ] VIP senders bypass every rule.
- [ ] Response promise stated per bucket.
- [ ] Auto-reply states the number, not "shortly".
- [ ] 10 snippets under 120 words each.
- [ ] 60% of customer replies use a snippet.
- [ ] One named owner per open thread.
- [ ] Weekly missed count recorded.
- [ ] Rules reviewed monthly.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Customer mail is archived automatically | A general vendor-domain rule runs before the customer rule | Order specific rules first and spot-check 30 messages |
| Two people reply to the same customer | No assignment on open, so both saw an unlabelled thread | Assign the owner when the thread is opened |
| Follow-ups asking when | Auto-reply promises "shortly" with no number | State the bucket's response time in the auto-reply |
| Important notice missed for weeks | A rule archived a whole domain instead of a subject pattern | Narrow the rule to subject keywords and keep the domain in the inbox |
| Inbox is empty but work is late | Messages archived without a follow-up date | Set a follow-up date whenever a reply is owed |
| Rules stop matching | Sender changed its subject format | Review rules monthly against the current top senders |
| Time to first response unknown | Measured from open rather than receipt | Measure from the received timestamp |

## Copy-ready agent prompt

> Read the skill at the URL above and triage my inbox. Count one week of mail by sender type, define the five buckets with labels, write 10 rules that label and skip the inbox without deleting anything, add VIP and internal exclusions, set a response promise per bucket with an auto-reply that states the number, and draft 10 snippets under 120 words for the questions that repeat. Then report unread count, messages needing a human per day, time to first response and the weekly missed count. Stop and show me any rule that deletes mail or archives an internal sender.
