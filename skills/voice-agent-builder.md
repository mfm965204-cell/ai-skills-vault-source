---
name: voice-agent-builder
description: Build a production AI voice agent that handles real phone calls - telephony, speech-to-text, turn detection, tool calling, barge-in, fallbacks, latency budget, compliance and call analytics.
version: 1.0.0
license: MIT
tags: [voice, ai, telephony, agents, ivr, realtime]
---

# Voice Agent Builder

A voice agent is a latency problem wearing a conversation costume. Get the turn loop under 800 ms and the rest is ordinary engineering.

## When to use this skill

- Building an inbound receptionist, booking line, support line or outbound follow-up caller.
- Replacing a phone-tree IVR with a conversational agent.
- Adding a voice channel to an existing text assistant.

Do NOT use for: high-stakes medical, legal or financial advice without a human handoff path, or emergency numbers.

## Stage 1 - Define the job before the voice

Write the call contract:

1. **Who calls** and what they want in their own words.
2. **Outcomes** - the 3-6 states a call can end in (booked, answered, escalated, declined, callback).
3. **Tools** the agent can call: check calendar, create booking, look up order, transfer to human.
4. **Hard limits** - what it must never say, never promise, never charge.
5. **Handoff trigger** - the exact conditions for transferring to a person, and the transfer target.
6. **Language(s)** and accent handling; code-switching (Hindi/English) needs an explicit policy.

Every outcome must be reachable without the caller saying a magic phrase. The agent drives; the caller should not have to know the script.

## Stage 2 - The latency budget (the whole game)

| Component | Budget |
|---|---|
| Caller stops speaking → end-of-turn detected | 200-300 ms |
| STT final transcript | 100-150 ms (streaming, not batch) |
| LLM first token | 300-400 ms |
| TTS first audio byte | 150-250 ms |
| Telephony jitter buffer | 60-100 ms |
| **Total perceived** | **under 800 ms** |

Techniques that actually move the number:

- Stream everything: STT partials, LLM tokens, TTS chunks. Never wait for a complete sentence.
- Use a small fast model for the turn loop and a bigger one only for background tasks.
- Pre-warm the connection at call start with a short filler ("one moment").
- Speak the acknowledgement before the tool call: "Let me check that for you" buys 1-2 seconds honestly.
- Keep the system prompt under 1,500 tokens. Long prompts cost first-token latency every single turn.

## Stage 3 - Turn detection and barge-in

- Use semantic end-of-turn detection (model-based) plus a 200-300 ms silence floor. Pure silence timers cut people off mid-thought.
- Support **barge-in**: when the caller speaks, stop TTS within 100 ms. Anything slower feels like talking over a machine.
- After barge-in, discard the rest of the interrupted response from context so the agent does not resume mid-sentence.
- Handle backchannels ("hmm", "haan", "okay") - do not treat them as a turn.

## Stage 4 - Conversation design

- First 10 seconds: identify the business, ask one open question. No menu of five options.
- One question at a time. Two questions in one turn guarantees one is ignored.
- Confirm critical data by repeating it back (phone numbers, dates, amounts) - read digits individually.
- Numbers, emails and IDs: slow down, spell when asked, never rush.
- Silence handling: after 4 seconds, one prompt; after 9, offer a callback or transfer.
- Never say "as an AI". Say what you can do, then do it.
- Fallback ladder: rephrase once → offer alternatives → transfer to human. Three strikes, never four.

## Stage 5 - Tools and state

```json
{"name":"book_slot","description":"Book an appointment. Only call after the caller confirms date and time.",
 "parameters":{"date":{"type":"string","format":"date"},"time":{"type":"string"},"name":{"type":"string"},"phone":{"type":"string"}}}
```

- Tools must be idempotent per call id - a repeated tool call must not double-book.
- Validate before acting; ask for the missing field, not the whole form again.
- On tool error: say what happened in plain words, offer the human. Never expose an error code to a caller.
- Persist call state server-side so a transfer carries context.

## Stage 6 - Audio quality

- Telephony is 8 kHz narrowband. Test on a real phone call, never only in the browser.
- Echo cancellation and noise suppression on; gain normalisation on.
- TTS: pick a voice that matches the brand; keep sentences under 15 words; add 120-200 ms pauses at commas for natural rhythm.
- Record consent, not just audio: state that the call is recorded, log the timestamp.

## Stage 7 - Compliance and safety

- Announce AI disclosure where the jurisdiction requires it; keep the wording in config, not hard-coded.
- Outbound calling: check local rules on hours, consent and do-not-call lists before dialling anything.
- Do not collect card numbers by voice; use a DTMF or payment-link handoff.
- PII in transcripts: redact at write time, set retention (default 30 days), restrict access.
- Always provide a human path. A voice agent with no escape hatch is a liability.

## Stage 8 - Testing

1. **Scripted regression set** - 25 real call recordings, replayed against every prompt change. Score: outcome reached, turns taken, latency p95.
2. **Adversarial set** - interruptions, accents, background noise, angry caller, silence, off-topic, third-party on the line.
3. **Latency test** on a real phone over 4G, not localhost.
4. **Tool failure injection** - API down, timeout, partial data.
5. Ship only if p95 perceived latency is under 1.2 s and the outcome rate beats the old IVR.

## Stage 9 - Analytics

Track per call: outcome, turns, duration, p50/p95 latency, barge-in count, fallback count, transfer reason, sentiment at end. Review the 10 worst calls weekly - that is where the prompt fixes come from.

## Quality checklist

- [ ] Call contract written with reachable outcomes
- [ ] p95 turn latency under 1.2 s on a real call
- [ ] Barge-in stops audio within 100 ms
- [ ] Every tool idempotent, every failure has a spoken fallback
- [ ] Human transfer works and carries context
- [ ] AI disclosure and recording consent handled
- [ ] PII redaction and retention set
- [ ] 25-call regression suite green

## Copy-ready agent prompt

> Read the skill at the URL above. Start by writing my call contract: callers, outcomes, tools, hard limits, handoff triggers. Then design the turn loop with a latency budget, write the system prompt under 1,500 tokens, define the tool schemas with idempotency, and give me the fallback ladder and barge-in handling. Finish with the test plan and the analytics events to emit.
