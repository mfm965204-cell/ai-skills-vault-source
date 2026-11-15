---
name: whatsapp-business-bot
description: Ship a WhatsApp Business bot in India that stays compliant - WABA setup, template approval and the 24-hour window, a webhook that answers in under 5 seconds, a conversation state machine, opt-in under DPDP, tier limits and human handoff.
version: 1.0.0
license: MIT
tags: [automation, whatsapp, bot, india, messaging, compliance]
---

# WhatsApp Business Bot

WhatsApp is the channel Indian customers actually answer, and it is also the one where a mistake is visible to the customer instantly: a template sent outside the window, a webhook that times out, or a broadcast that gets the number's quality rating killed.

This skill builds the bot in the order the platform demands: a verified business, approved templates, a webhook that answers in 5 seconds, opt-in records, and a handoff to a human that actually works.

## When to use this skill

- Order updates, appointment reminders, or support on WhatsApp for Indian customers.
- You want a bot for the first reply and a human for the hard cases.
- You are moving from a personal number and group chats to the official API.
- A marketing team wants broadcasts and you need the compliance guardrails.

Do NOT use for: bulk unsolicited marketing to purchased numbers (a fast route to a banned number), or anything requiring medical, legal or financial advice without a human handoff.

## Stage 1 - Set up the business and the number

1.1 Create a Meta Business account, verify the business, and add a WhatsApp Business Account (WABA). Business verification takes days, so start it before you write code.

1.2 Use a phone number that is not already on a personal WhatsApp account. A number cannot be on both; migrating removes it from the app.

1.3 The display name must follow Meta's rules: related to the business, no generic words like "Support", no promotional text. A rejected name blocks the whole setup.

1.4 Choose the right number type: a dedicated business number, not the founder's mobile. Porting later is painful and unnecessary.

1.5 Decide the provider path: Meta Cloud API directly, or a Business Solution Provider. Direct is cheaper and more work; a BSP adds cost and a dashboard.

| Setup item | Requirement | Blocks launch |
|---|---|---|
| Business verification | legal documents, 1-5 working days | yes |
| Phone number | not on personal WhatsApp | yes |
| Display name | matches business, no generic words | yes |
| Two-factor PIN | 6 digits, stored safely | yes |
| Payment method | for per-conversation charges | yes |
| Webhook endpoint | HTTPS, valid certificate | yes |

1.6 Store the phone number id, WABA id and the permanent token in a secret manager. Temporary tokens expire in 24 hours and break a production bot overnight.

Gate: verified business, approved display name, permanent token stored.

## Stage 2 - Design templates and respect the 24-hour window

2.1 Outside a 24-hour window that the customer opens, you may only send pre-approved templates. Inside the window, you may send free-form messages.

2.2 The window opens when the customer messages you and lasts 24 hours. Plan every outbound flow around it - a reminder sent 25 hours after the last message is a template.

2.3 Templates are categorised: marketing, utility, authentication, and service. Category affects price and approval. An order update is utility; a discount is marketing.

2.4 Keep templates short, with variables in double braces, and a clear reason to receive them:

```json
{
  "name": "order_shipped_v2",
  "language": "en",
  "category": "UTILITY",
  "components": [
    { "type": "BODY",
      "text": "Your order {{1}} shipped on {{2}}. Track it here: {{3}}",
      "example": { "body_text": [["ORD-2291", "14 Nov", "https://ex.com/t/abc"]] } },
    { "type": "FOOTER", "text": "Reply HELP for support" }
  ]
}
```

2.5 Submit templates with realistic examples; a template rejected for a variable in the wrong place costs a day.

2.6 Keep a version suffix (`_v2`) and never edit an approved template's meaning - submit a new version and retire the old one.

| Template type | Use | Free-form allowed |
|---|---|---|
| Utility | order, appointment, payment | inside the window only |
| Marketing | offers, re-engagement | never outside a template |
| Authentication | OTP, login codes | never |
| Service | reply to a customer message | inside the window |

2.7 Test each template against your own number before wiring it into a flow.

Gate: every outbound message maps to an approved template or to an open window.

## Stage 3 - Build a webhook that never times out

3.1 WhatsApp expects a 200 within 5 seconds. Do the work asynchronously: acknowledge, enqueue, then reply.

3.2 Verify the webhook once with the hub challenge, then validate the `X-Hub-Signature-256` header on every call using the app secret.

3.3 Deduplicate on the message id (`wamid`). The platform retries, and a bot without dedupe sends the same reply twice.

```python
import hmac, hashlib, os, json
from flask import Flask, request, abort
app = Flask(__name__)
SECRET = os.environ["WA_APP_SECRET"].encode()

@app.post("/webhook")
def hook():
    raw = request.get_data()
    sig = request.headers.get("X-Hub-Signature-256", "")
    expect = "sha256=" + hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expect):
        abort(403)
    body = json.loads(raw)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                enqueue(msg)          # return fast; reply from the worker
    return "ok", 200
```

3.4 Handle the non-message events too: delivery status, read receipts, errors. An error webhook is how you find out a template was rejected mid-flow.

3.5 Log the raw payload for 30 days. When a customer says "I never got it", the payload is the only evidence.

3.6 Run the webhook behind a queue with a retry policy; a slow database call inside the request handler is the classic 5-second timeout.

Gate: p95 webhook response under 800 ms, duplicate delivery produces one reply.

## Stage 4 - Model the conversation as a state machine

4.1 Every user has a state: `new`, `awaiting_choice`, `awaiting_address`, `handed_off`, `closed`. Store it, do not infer it from the last message.

4.2 Transitions are explicit and validated; an unexpected message in a state either falls back to a menu or goes to a human.

4.3 Store the state keyed by the WhatsApp id (`wa_id`), with a `last_seen` timestamp and the last 10 messages.

4.4 Time out stale states after 24 hours and reset to the menu. A user returning after three days should not resume at "enter your pincode".

4.5 Buttons and lists beat free text. Up to 3 reply buttons, up to 10 list rows - design within those limits rather than asking users to type.

4.6 Keep the language policy explicit: detect the language on the first message, reply in it, and allow a switch command.

4.7 Cap the conversation at 12 bot turns. Past that, a bot that has not solved it will not, and the user is about to type something rude.

| State | Accepts | Next |
|---|---|---|
| new | any message | menu |
| awaiting_choice | button or 1-3 | the chosen flow |
| awaiting_address | text, 6 digits or more | confirm |
| handed_off | nothing (bot muted) | human closes |
| closed | any message | new session |

Gate: every state has a defined transition for an unexpected input.

## Stage 5 - Get consent and keep records

5.1 Opt-in must be explicit, recorded, and traceable to a source: a web form, a checkbox at checkout, or an inbound message from the customer.

5.2 Store for each contact: the number, the opt-in timestamp, the source, the exact wording shown, and the IP or channel where it happened.

5.3 Under India's DPDP Act, the customer can withdraw consent and ask what you hold. Build the delete and export path before launch, not after the first request.

5.4 Honour STOP immediately and permanently, across every list. One "STOP" that still receives a marketing template is a complaint to Meta and a quality-rating hit.

5.5 Never message a number you scraped, bought, or got from a group. Meta's quality rating and the law both punish it.

5.6 Keep a retention policy for message content: 90 days is a common default, and it should be a written decision, not an accident.

Gate: an opt-in record for every contact, and a tested delete path.

## Stage 6 - Work within tiers and limits

6.1 Messaging limits scale with quality and volume: a new number starts small (1,000 unique customers in 24 hours) and grows as the quality rating holds.

6.2 Quality rating is per number, based on blocks and reports. One bad broadcast can drop it and cut your limit.

6.3 Rate limits apply per second, not just per day. Batch sends with a queue and a fixed rate, not a loop.

6.4 Send marketing in the recipient's evening, and utility whenever the event happens. The same send at the wrong hour produces blocks.

| Limit | New number | Established |
|---|---|---|
| Unique customers per 24 h | 1,000 | 10,000 to unlimited by tier |
| Quality rating | starts green | green needed to grow |
| Throughput | throttled per second | higher, still throttled |

6.5 Add a global kill switch that stops all outbound sends in one config change. You will need it during an incident.

6.6 Monitor blocks and reports daily. A rising block rate is the earliest signal that the content is wrong.

6.7 Queue marketing sends at 10-20 messages a second even when the tier allows more; bursts correlate with blocks, not with reach.

Gate: send rate limited in code, kill switch tested.

## Stage 7 - Understand what you are charged for

7.1 WhatsApp charges per conversation, by category, and rates differ by country and change by notification. Read Meta's current rate card for India before you price anything.

7.2 Service conversations started by the customer are usually the cheapest or free within a limit; marketing conversations cost the most.

7.3 Design flows that invite the customer to message first where possible - it moves the conversation into the cheaper category and often improves engagement.

7.4 Calculate cost per outcome, not per message: a reminder that prevents a no-show is worth many times a marketing blast.

7.5 Model the monthly bill at your expected volume before launch, and put a hard daily cap on sends so a bug cannot run up a bill overnight.

7.6 Log the conversation category on every send so the bill can be attributed to a feature.

Gate: a cost model per feature, and a daily send cap in the code.

## Stage 8 - Hand off to a human cleanly

8.1 Define the trigger: an explicit "agent" request, an angry sentiment, a payment dispute, or two failed attempts at the same step.

8.2 On handoff, mute the bot for that conversation and notify the agent with the transcript, the state and the reason.

8.3 Give the agent a reply window and a timeout; if nobody answers in 10 minutes, tell the customer honestly and offer a callback.

8.4 When the human finishes, the conversation returns to the bot only on an explicit action, never automatically.

8.5 Log handoff reason and resolution. The top three reasons are your next three automations.

8.6 Give the agent a canned first line with the customer's name and the reason for the handoff, so the customer does not repeat themselves.

Gate: handoff tested end to end, with a timeout path that messages the customer.

## Stage 9 - Test before you go live

9.1 Use the test number Meta provides, and a small set of real staff numbers, before any customer sees the bot.

9.2 Test the failures, not just the happy path: expired token, rejected template, closed window, unknown message type, duplicate webhook, media upload failure.

9.3 Test on a real phone with the app installed, not on a desktop emulator. Buttons render differently and media behaves differently.

9.4 Test the language switch, the STOP path and the handoff with a person who has never seen the bot.

9.5 Keep a `test-plan.md` with 15 checks and run it before every template or flow change.

9.6 Test with the network off mid-flow. A half-completed conversation must resume at the right state, not restart.

Gate: 15-item test plan passes on two real phones.

## Stage 10 - Monitor quality and iterate

10.1 Watch four numbers: messages sent, delivered, replied, and blocked. Blocks are the leading indicator of a problem.

10.2 Alert on a quality rating drop, a webhook error rate above 1%, and a template rejection.

10.3 Review the top 20 conversations weekly, especially the ones that ended in a handoff or a block.

10.4 Retire templates with a reply rate under 5% after 1,000 sends; they are costing money and attention.

10.5 Re-check Meta's policy changes quarterly. Template categories and pricing rules change, and a silent change can break a flow.

Gate: dashboard with the four numbers, weekly review scheduled.

## Worked example

An appointment reminder bot for a clinic chain, 3 branches, 400 appointments a week.

| Metric | Before WhatsApp | After |
|---|---|---|
| No-show rate | 19% | 11% |
| Reminder delivery | 62% by SMS | 94% |
| Staff calls per day | 40 | 12 |
| Cost per appointment | ₹6 SMS plus calls | ₹1.80 |
| Handoffs per week | n/a | 22, mostly reschedules |

Two design decisions did the work: a utility template sent 24 hours before, and a reply button that reschedules inside the window instead of asking the patient to call.

## Quality checklist

- [ ] Business verified, display name approved
- [ ] Dedicated number, not on personal WhatsApp
- [ ] Permanent token in a secret manager
- [ ] Every outbound message is a template or inside an open window
- [ ] Template categories correct, examples realistic
- [ ] Webhook returns 200 in under 5 seconds, work queued
- [ ] Signature verified on every call
- [ ] Duplicate `wamid` produces one reply
- [ ] Conversation state stored, not inferred
- [ ] Stale state resets after 24 hours
- [ ] Opt-in recorded with source, timestamp and wording
- [ ] STOP honoured permanently and tested
- [ ] Delete and export path built before launch
- [ ] Send rate limited in code, daily cap set
- [ ] Global kill switch tested
- [ ] Handoff mutes the bot and notifies an agent
- [ ] 15-item test plan passed on two real phones
- [ ] Blocks and quality rating on a dashboard

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Messages rejected outside the window | Free-form send after 24 hours | Route every outbound through a template |
| Webhook timeouts and duplicate replies | Work done synchronously in the request | Acknowledge, enqueue, reply from a worker |
| Customer gets the same reply twice | No dedupe on `wamid` | Store processed ids, skip repeats |
| Number banned after a broadcast | Marketing to numbers without opt-in | Consent records, STOP handling, rate limit |
| Quality rating dropped to yellow | High block rate from a bad send hour | Send in the evening, cut marketing volume |
| Bot answers "enter pincode" to a returning user | State persisted with no timeout | Reset stale state after 24 hours |
| Agent never saw the handoff | Notification sent but the bot stayed active | Mute the bot on handoff, notify with the transcript |
| Bill 4x the model | Marketing category used for utility messages | Re-categorise templates, log category per send |
| Bot keeps asking after 12 turns | No turn cap, no fallback | Cap at 12 turns, then offer a human |
| Flow restarts after a network drop | State inferred from the last message | Persist state keyed by `wa_id` with a timeout |

## Copy-ready agent prompt

> Read the skill at the URL above and build a WhatsApp Business bot with me. Ask me: the use case, whether the customer messages first, my volume, and whether the business is verified. Then give me the setup checklist with verification, number and display name rules, the templates I need with categories and JSON, and a webhook implementation with signature verification, dedupe and a queue. Then the conversation state machine with states and transitions, the opt-in record fields and DPDP obligations, the tier limits, the cost model per feature, the handoff design and the 15-item test plan. Tell me which of my messages would be rejected for being outside the 24-hour window.
