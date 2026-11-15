---
name: newsletter-growth-engine
description: Build a newsletter that grows from a real capture surface,
verified consent, deliverability that reaches the inbox, and a five-email
welcome sequence measured by list growth rate.
version: 1.0.0
license: MIT
tags: [newsletter, email, marketing, consent, deliverability]
---

# Newsletter Growth Engine

Most newsletters do not fail on writing; they fail on plumbing. The signup
form collects an address nobody confirms, the sending domain has no DKIM
record, the first email lands in promotions, and the list stops growing at 400
because there is one capture point on a page nobody visits.

The output is a working engine: three capture surfaces, double opt-in with a
stored consent record, an authenticated sending domain, a five-email welcome
sequence, a pruning rule, and one number that tells you whether any of it
works — net list growth per week.

## When to use this skill

- You have a signup form and no idea whether the addresses are deliverable.
- Your first email to a new subscriber gets a 12% open rate and no clicks.
- You are about to import 4,000 contacts from a spreadsheet or a bought list.
- You send weekly but cannot say whether the list is growing or slowly dying.

Do NOT use for: transactional email like receipts and password resets
(different deliverability rules and different triggers), or a full lifecycle
program with cart recovery and win-back flows — that is a separate sequence
design job.

## Stage 1 — Define one offer and one action

A newsletter with three calls to action converts on none. Choose the promise
and the single next step.

1.1 Write the promise in one sentence with a frequency and a payoff: "one email every Tuesday, one worked example of an Indian tax or billing problem, no pitches".

1.2 Pick the single action the subscriber takes next — read the archive, reply to the welcome email, or download the template. One, not four.

1.3 Put the promise in three places: the form, the confirmation email and the footer of every issue, because subscribers forget what they signed up for and the footer is what stops the spam report.

Gate: one sentence, one action, and the sentence appears verbatim in the form,
the confirmation email and the footer.

## Stage 2 — Build three capture surfaces, not one

A single form on a low-traffic page caps the list at the traffic of that page.
Three surfaces compound.

2.1 Put an inline form in the middle of the highest-traffic article, after the first useful section rather than at the end — readers who reach the end rarely convert.

2.2 Add a content upgrade on the top three pages: a template, a checklist or a spreadsheet that solves the page's problem, exchanged for an address.

2.3 Add a footer form on every page and one in the product if you have one, so a reader who arrives from search has a path without scrolling.

| Surface | Typical share of signups | Effort | Notes |
|---|---|---|---|
| Inline in top article | 35% | low | after the first section, not the end |
| Content upgrade | 40% | medium | one asset per top page |
| Footer form | 15% | low | catches returning readers |
| Product or app | 10% | high | highest intent, lowest volume |

Gate: three surfaces are live, each tagged with its own source parameter, and
signups are attributed by surface.

## Stage 3 — Confirm consent and keep the record

An unconfirmed list is a list of typo addresses plus a legal exposure.
Confirmation costs about 20% of signups and saves the rest.

3.1 Use double opt-in: the form sends a confirmation email, and the address is only mailed once the link is clicked.

3.2 Store five fields per subscriber: email, source, timestamp, IP address, and the exact consent wording shown at signup — this is the record that answers a complaint.

3.3 Expire an unconfirmed signup after 7 days, and never mail an unconfirmed address.

Gate: no address receives a newsletter without a confirmed flag and a stored
consent timestamp.

## Stage 4 — Authenticate the sending domain

Deliverability is decided before the copy is read. Four DNS records and one
warm-up decide the inbox.

4.1 Send from a subdomain you own — `mail.yourdomain.in` rather than the root — so a reputation problem cannot affect password resets.

4.2 Publish SPF, DKIM and DMARC: SPF listing the provider, DKIM signed by the provider, and `_dmarc` at `p=none` first with a reporting address, moving to `p=quarantine` after two weeks of clean reports.

4.3 Warm up: 200 sends on day one, doubling daily to 3,200 by day five, and no new domain sending to a 20,000-person list on day one.

```dns
mail.yourdomain.in.      TXT  "v=spf1 include:sendprovider.yourdomain.in ~all"
sel1._domainkey.mail.yourdomain.in.  CNAME  sel1.dkim.provider.in
_dmarc.yourdomain.in.    TXT  "v=DMARC1; p=quarantine; pct=100"   # add rua= with your reporting mailbox
```

Gate: SPF and DKIM pass on a test send to a Gmail address, and DMARC reports
arrive.

## Stage 5 — Write the five-email welcome sequence

The welcome sequence is where a subscriber decides whether you are worth the
inbox. Five emails over 7 days, each with one job.

5.1 Day 0 — confirm and deliver the promised thing immediately, in the same email, with no pitch.

5.2 Day 1 — the single best piece of your archive, with one line on why it matters.

5.3 Day 3 — a short story that shows how you work, ending with one question the reader can reply to; replies train the provider that this is a real relationship.

5.4 Day 5 — the offer or the product, named plainly, with the price or the next step.

5.5 Day 7 — the expectation email: what arrives weekly, when, and the one-click unsubscribe. Subscribers who read this email unsubscribe less later.

Gate: five emails scheduled with 0, 1, 3, 5 and 7 day delays, and each has a
single call to action.

## Stage 6 — Send on a cadence you can hold

An irregular newsletter is a list that forgets you. Pick a day, a time and a
frequency you can sustain for 52 weeks.

6.1 Send on a fixed day and time — Tuesday 09:00 IST works for Indian professional audiences — and keep it fixed for at least 8 issues before changing.

6.2 Cap at two sends per week including the welcome sequence; above that, unsubscribes rise faster than signups.

6.3 Keep one issue to one idea and under 700 words, with the first sentence doing the work; mobile clients show roughly 40 characters of subject and 90 of preview text.

Gate: 8 consecutive issues on the same day and time, and the unsubscribe rate
under 0.5% per send.

## Stage 7 — Segment by what people read

Segmentation by demographics is guesswork. Segmentation by click behaviour is
data.

7.1 Tag subscribers who click any link twice in 30 days as engaged, and those who have not opened in 90 days as dormant.

7.2 Send engaged subscribers the same issue; send dormant ones a single re-permission email — "still want this?" — and remove them if there is no click in 7 days.

7.3 Never segment by open pixel alone for a decision that removes someone: Apple's mail privacy protection pre-fetches pixels, so clicks are the honest signal.

Gate: engaged and dormant segments exist, and the dormant segment has received
exactly one re-permission email.

## Stage 8 — Prune on a schedule

A smaller list that opens is worth more than a large one that does not, and
providers score you on engagement.

8.1 Remove subscribers with no open and no click in 90 days, after the one re-permission email, and record the removal date.

8.2 Never re-add a removed address without a fresh signup; a re-imported list is the fastest route to a spam-trap hit.

8.3 Publish the pruning count next to the growth count, so a 400-person loss does not look like a failure when 900 joined.

Gate: list size, removals and net growth are reported together every month.

## Stage 9 — Measure the four numbers that matter

Open rate is a diagnostic, not a goal. Four numbers decide whether the engine
works.

9.1 Track: net list growth per week, click rate per issue, unsubscribe rate per send, and the welcome-sequence completion rate.

9.2 Set the working bands — click rate 2% to 5% on a professional list, unsubscribe under 0.5% per send, welcome completion above 60% — and treat a breach as a signal to change the offer, not the subject line.

9.3 Compute growth as signups minus removals minus unsubscribes, because gross signups flatter a list that is leaking.

9.4 Keep the growth arithmetic in one place, because two definitions produce two numbers in two meetings:

```python
net_growth = signups - removals - unsubscribes
growth_rate = net_growth / list_size_at_start_of_period
```

Gate: the four numbers are on one dashboard, updated weekly, with the growth
formula written on it.

## Reference — the compliance and deliverability rules

| Rule | What it requires | Where it bites |
|---|---|---|
| Consent record | Proof of opt-in with time and source | A complaint or a data request |
| Unsubscribe | One click, honoured within 24 hours | Every send, in the footer |
| Sender identity | Real postal or business address in the footer | Deliverability scoring |
| No purchased lists | Addresses must opt in themselves | Spam-trap hits, domain blocklisting |
| India DPDP Act | Purpose limitation and erasure on request | Storing consent and honouring deletion |
| Re-permission | One ask before removal, not silence | Pruning without a legal basis to keep |

Gate: the footer carries an unsubscribe link, a business address and the
consent line, and a deletion request can be honoured within 7 days.

## Worked example — 400 to 6,200 in nine months

A B2B newsletter for Indian finance teams, sent from a personal Gmail address,
with one footer form.

| Month | Subscribers | Net growth | Click rate | Unsub per send | Change made |
|---|---|---|---|---|---|
| 0 | 412 | +18 | 0.9% | 1.4% | baseline, Gmail sender |
| 1 | 780 | +368 | 1.2% | 1.1% | own subdomain, SPF and DKIM |
| 2 | 1,140 | +360 | 1.8% | 0.9% | inline form in top article |
| 3 | 1,690 | +550 | 2.4% | 0.7% | content upgrade on 3 pages |
| 5 | 2,880 | +1,190 | 2.9% | 0.6% | five-email welcome live |
| 7 | 4,410 | +1,530 | 3.4% | 0.5% | segmentation by clicks |
| 9 | 6,200 | +1,790 | 3.8% | 0.4% | 90-day pruning, weekly cadence |

The single largest step was not the content upgrade; it was moving off a
personal Gmail address. Before the subdomain, 31% of sends to a seeded test
list landed in spam. After SPF, DKIM and DMARC with a two-week warm-up, the
same list delivered 96% to the inbox on a test send.

The pruning month looks bad and was not. Removing 610 dormant addresses cut
the list by 14%, and the click rate rose from 2.6% to 3.4% in the following
two issues because the denominator became honest. Providers score engagement
as a ratio, so a smaller engaged list reaches more inboxes.

One mistake worth avoiding: the first welcome sequence had four calls to
action across five emails, and completion fell to 34%. Rewriting each email to
one action took completion to 68% without changing a single subject line.

## Second example - the content upgrade that hurt the list

A team added a salary-negotiation template as a content upgrade on their
highest-traffic page. Signups tripled in a month.

| Metric | Before | After | Verdict |
|---|---|---|---|
| Signups per week | 60 | 180 | looks like a win |
| Confirmed rate | 88% | 61% | asset hunters do not confirm |
| 30-day open rate | 41% | 22% | the list got colder |
| Unsubscribe per send | 0.3% | 1.1% | wrong audience, right offer |
| Net growth | +48 | +31 | worse after removals |

The fix was not to remove the upgrade. It was to split the list: the asset
delivered through a separate sequence, and the newsletter asked for separately
with its own promise. Confirmed rate returned to 84%, and the asset list
became a second product rather than a drag on the first.

The lesson generalises: any capture surface that triples signups is worth
checking against the confirmed rate before it is called growth.

## Quality checklist

- [ ] One promise sentence with frequency and payoff, in three places.
- [ ] Three capture surfaces live with source tags.
- [ ] Double opt-in enabled and unconfirmed signups expire in 7 days.
- [ ] Consent record stores email, source, timestamp, IP and wording.
- [ ] Sending subdomain separate from the root domain.
- [ ] SPF, DKIM and DMARC published; DMARC reports arriving.
- [ ] Warm-up schedule followed to 3,200 sends before a full send.
- [ ] Five welcome emails with 0, 1, 3, 5, 7 day delays.
- [ ] One call to action per email in the sequence.
- [ ] Fixed send day and time held for 8 issues.
- [ ] Engaged and dormant segments defined by clicks, not pixels.
- [ ] One re-permission email before any removal.
- [ ] 90-day pruning runs on a schedule and the count is reported.
- [ ] Footer carries unsubscribe, business address and consent line.
- [ ] Net growth computed as signups minus removals minus unsubscribes.
- [ ] Confirmed rate measured separately for every capture surface.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Signups rise, opens fall | The form promises a download that never arrives, so subscribers disengage | Deliver the asset in the confirmation email, not after a redirect |
| 20% of the list never opens anything | Addresses imported without consent or confirmation | Prune after one re-permission email and switch to double opt-in |
| Emails land in spam from day one | New domain, no warm-up, no DMARC alignment | Warm up over 5 days and align DMARC with the sending subdomain |
| Unsubscribe rate doubles | Frequency rose and the footer no longer states the cadence | Return to two sends a week and restate frequency in the footer |
| Click rate high, list shrinking | The offer attracts readers who want the asset, not the newsletter | Separate the asset list from the newsletter list |
| Pruning removes engaged readers | Dormancy decided on open pixels, which clients pre-fetch | Decide dormancy on clicks over 90 days |
| Confirmed rate below 70% | The form promises something the confirmation email does not deliver | Deliver the asset in the first email and state the promise again |
| Same subscriber receives two issues in one day | Welcome sequence and weekly issue share a schedule | Exclude addresses in the welcome sequence from the weekly send |

## Copy-ready agent prompt

> Read the skill at the URL above and build my newsletter engine. Start by writing the one-sentence promise and picking the single action, then set up three capture surfaces with source tags, double opt-in with a stored consent record, and an authenticated sending subdomain with SPF, DKIM and DMARC plus a 5-day warm-up. Write the five-email welcome sequence with one call to action each, define engaged and dormant segments by clicks, schedule 90-day pruning, and put net growth, click rate, unsubscribe rate and welcome completion on one weekly dashboard. Stop and show me the DNS or consent gap before any send to the full list.
