---
name: slack-ops-bot
description: Build a Slack bot that carries alerts, deploys and
on-call
actions with the right routing, one message per incident, and buttons
that
actually run the runbook step.
version: 1.0.0
license: MIT
tags: [automation, slack, ops, incident, bot]
---

# Slack Ops Bot

An alert channel with 400 messages a day is a channel nobody reads,
and the
one message that mattered scrolled away at 03:12. A bot that posts
everything
is the same as no bot at all.

This skill builds the opposite: alerts routed to the team that owns
them, one
thread per incident that updates rather than reposts, action buttons
that run
a real runbook step, and a resolution message that closes the loop. It
also
covers the parts that break in practice — signature verification,
retries,
rate limits and the token scope.

## When to use this skill

- Your alert channel gets more than 50 messages a day and the team has muted it.
- An incident produced 60 messages in one channel and the timeline had to be rebuilt by hand.
- You want a "restart the worker" button in Slack and do not want to hand a bot production root.
- Deploys are announced by a human pasting a link, and half of them are forgotten.

Do NOT use for: paging and escalation policy (that is an on-call tool
with
schedules and acknowledgements), or general chat automation unrelated
to
operations.

## Stage 1 — Define the three message types

A bot with one message format uses it for everything. Three types
cover
operations.

1.1 Alert: something is broken now, it has an owner, and it needs an acknowledgement.

1.2 Event: something changed — a deploy, a config change, a backup finished. No action needed, no notification sound.

1.3 Action: a request for a human decision, with buttons, and a timeout after which it expires.

| Type | Channel | Notifies | Lifetime | Example |
|---|---|---|---|---|
| Alert | team channel | yes, with mention | until resolved | p99 above 800 ms for 5 min |
| Event | team channel | no | 7 days retention | deploy of api@2f3c1a shipped |
| Action | team channel | yes | 30 minutes | approve rollback of api |

Gate: every message the bot sends is one of the three types, and the
type is
in the payload.

## Stage 2 — Route to the owning team, not to one channel

Routing is a lookup from service to channel, kept in one file that
both the
bot and the humans can read.

2.1 Maintain a routing table: service name, owning team, channel id, escalation handle.

2.2 Route by the service label on the alert, and fail loudly to a fallback channel if the label is unknown — an unrouted alert is a dropped alert.

2.3 Never fan out one alert to three channels; the duplicate is what teaches people to mute.

```yaml
routes:
  api:        { channel: "C0API", team: payments, oncall: "@payments-oncall" }
  worker:     { channel: "C0WRK", team: platform, oncall: "@platform-oncall" }
  web:        { channel: "C0WEB", team: growth,   oncall: "@growth-oncall" }
fallback:     { channel: "C0OPS", team: platform, oncall: "@platform-oncall" }
```

Gate: a test alert for each service lands in the right channel, and an
unknown
service lands in the fallback with a warning.

## Stage 3 — One thread per incident, updated in place

Sixty messages per incident is a formatting problem: every update
should edit
the same message or reply in one thread.

3.1 Post the first message with the incident key in the metadata, then reply in its thread for every update.

3.2 Edit the top message to carry current state — status, owner, last update time — so the thread is optional reading.

3.3 Post the resolution as a final thread reply with duration and the action taken, and never delete the original.

Gate: an incident with 20 updates produces 1 message and 20 thread
replies,
not 21 messages.

## Stage 4 — Make the buttons run a real, bounded action

A button that only posts "someone should restart it" is a reminder. A
button
that runs a command needs a scope and a timeout.

4.1 Allow exactly three actions at first: acknowledge, silence for 30 minutes, and run one named runbook job.

4.2 The runbook job takes a service name and an action from an allowlist, never a free-text command.

4.3 Require the clicker to be in the on-call group, verify that server-side, and log the click with user id, action, and result.

```python
ALLOWED = {"restart_worker", "drain_queue", "clear_cache"}
@app.post("/slack/actions")
async def actions(req):
    verify_signature(req)                      # HMAC over the raw body
    payload = parse(req)
    if payload["user"]["id"] not in ONCALL_IDS:
        return deny("not on call")
    action = payload["actions"][0]["value"]
    if action not in ALLOWED:
        return deny("action not allowed")
    result = await runbook(action, payload["incident"])
    return ephemeral(f"{action}: {result.status}")
```

Gate: a click by a non-on-call user is refused, and an action outside
the
allowlist is refused, both proven by test.

## Stage 5 — Verify signatures and handle retries

An unverified Slack endpoint is a public command runner. Slack also
retries,
so the same event arrives twice.

5.1 Verify the request signature with the signing secret over the raw body, and reject anything older than 5 minutes.

5.2 Deduplicate on the event id with a 10-minute key in Redis, because Slack retries after 3 seconds if you are slow.

5.3 Answer within 3 seconds with a 200 and do the work asynchronously; a slow handler is retried and doubles the action.

Gate: a replayed request is rejected by timestamp, a duplicated event
runs
once, and p99 handler time is under 500 ms.

## Stage 6 — Respect the rate limits

Slack limits posting per channel and per method, and a burst during an
incident is exactly when you hit them.

6.1 Keep under 1 message per second per channel; queue bursts and coalesce updates that arrive within 5 seconds into one edit.

6.2 Read `Retry-After` on a 429 and wait; retrying immediately during an incident multiplies the failure.

6.3 Never post from a loop over 100 users — use a single message with mentions, or open a canvas.

Gate: a 200-alert burst produces no 429 errors in the bot log, and the
queue
drains within 30 seconds.

## Stage 7 — Give the token the smallest scope

A bot with `chat:write` and nothing else cannot leak data. Start there
and add
only what the runbook needs.

7.1 Scopes: `chat:write`, `chat:write.customize` for per-service identity, and `reactions:write` for acknowledgement. Nothing else for v1.

7.2 Keep the token in a secret store with rotation every 90 days, and never in the repo or a screenshot.

7.3 Log every API call with method, channel and status, but never log the token or message contents containing customer data.

Gate: the app's scope list matches the code's usage exactly, and no
token
appears in any log line.

## Stage 8 — Make silence visible

A bot that stops posting looks identical to a quiet week. Add a
heartbeat.

8.1 Post a daily digest at 09:00 IST with open incidents, alerts in the last 24 hours and the bot's own uptime.

8.2 Alert if the bot has not sent anything in 26 hours, which means the webhook is broken rather than the system healthy.

8.3 Track the alert-to-acknowledge time and the percentage of alerts acknowledged within 10 minutes.

Gate: the digest posts daily and a stopped bot triggers its own alert
within
26 hours.

## Stage 9 — Review the channel monthly

The channel is a product; review it like one.

9.1 Count alerts per week and delete or demote the noisiest source; a source that fires more than 5 times a week without an action is a dashboard, not an alert.

9.2 Ask the team one question monthly: which message in this channel did you act on?

9.3 Keep the routing table current — a service renamed without the table updated routes to the fallback forever.

Gate: alert volume falls month over month, and every routed service
still has
a live owner.

## Worked example - 400 messages a day to 30

A platform team's `#alerts` channel, before and after.

| Measurement | Before | After | Change |
|---|---|---|---|
| Messages per day | 412 | 31 | one thread per incident, events demoted |
| Incidents per day | 18 | 18 | unchanged |
| Duplicate alerts per incident | 4.1 | 1.0 | routed by service label |
| Acknowledged within 10 min | 34% | 88% | owner mention in the alert |
| Time to first action | 11 min | 3 min | runbook button in the message |
| Muted by team | yes | no | volume and routing fixed |

The single largest reduction came from deleting three alert rules that
had
never produced an action. They accounted for 240 messages a day, and
nobody
could say what they meant.

The second came from the thread model. The incident bot now edits one
message
per incident, so a 20-update incident is one line in the channel
instead of a
scroll.

The mistake was allowing free-text commands in the action handler for
the
first two weeks. One click ran `restart_worker` against production
instead of
staging because the service name came from the button payload without
an
allowlist check. The handler was rewritten to accept only an
allowlisted
action and to resolve the target from the routing table, and a test
now
asserts that an unknown service is refused.

## Quality checklist

- [ ] Every message carries a type of alert, event or action.
- [ ] Routing table maps service to channel, team and handle.
- [ ] Unknown service routes to the fallback with a warning.
- [ ] No alert is posted to more than one channel.
- [ ] Incident updates are thread replies, not new messages.
- [ ] Top message edited to show current state.
- [ ] Actions limited to an allowlist of three.
- [ ] Clicker verified against the on-call group server-side.
- [ ] Request signature verified over the raw body.
- [ ] Event ids deduplicated for 10 minutes.
- [ ] Handler responds within 3 seconds and works asynchronously.
- [ ] Posting rate kept under 1 per second per channel.
- [ ] Token scopes limited to chat write and reactions.
- [ ] Daily digest and 26-hour heartbeat alert configured.
- [ ] Monthly review removes any source with no action.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Same alert posted 4 times | Three alert rules match one condition and each posts | Deduplicate on the incident key before posting |
| Buttons do nothing | Handler exceeded 3 seconds, Slack retried, the first request was cancelled | Respond 200 immediately and run the action in a worker |
| Bot posts as itself, not the service | No `chat:write.customize` scope, so username is ignored | Add the scope and set username and icon per service |
| 429 storms during an incident | A loop posts one message per affected host | Coalesce into one message with a count and a list |
| Anyone can click a production action | Only the button visibility was restricted, not the handler | Check the user against the on-call group in the handler |
| Channel quiet for two days, nobody notices | No heartbeat, so silence looks like health | Daily digest plus a 26-hour dead-man alert |
| Renamed service never alerts again | Routing table still has the old name | Fail loudly on unknown labels and review the table monthly |

## Copy-ready agent prompt

> Read the skill at the URL above and build my Slack ops bot. Define the alert, event and action message types, create the service-to-channel routing table with a fallback, implement one-thread-per-incident updates with the top message edited to current state, and add three allowlisted actions with server-side on-call verification and an audit log. Add signature verification, 10-minute event deduplication, a 3-second handler deadline, rate-limit handling and a daily digest with a 26-hour heartbeat. Report message volume per day and acknowledgement rate before and after. Stop and show me the handler if any action can be triggered by a non-on-call user.
