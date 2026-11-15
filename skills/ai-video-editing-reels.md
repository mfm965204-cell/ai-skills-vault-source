---
name: ai-video-editing-reels
description: Script, edit and publish short-form vertical video (Reels, Shorts, TikTok) that holds attention - hook formulas, cut rhythm, caption styling, sound design, export specs and a repurposing matrix.
version: 1.0.0
license: MIT
tags: [video, reels, shorts, tiktok, editing, content, capcut]
---

# AI Video Editing For Reels

The difference between a 2,000-view video and a 200,000-view video is usually the first 2 seconds and the cut rhythm. This skill engineers both.

## When to use this skill

- Producing Reels/Shorts/TikTok from raw footage, a screen recording or an AI avatar.
- Turning long-form content into a series of shorts.
- Diagnosing why a video underperforms.

## Stage 1 - The retention architecture

Every short is built in five blocks. Get the seconds right:

| Block | Time | Job |
|---|---|---|
| Hook | 0.0-1.5s | Stop the scroll - motion, claim, or a visual oddity |
| Setup | 1.5-4s | Promise what the viewer gets, create an open loop |
| Payload | 4-20s | Deliver in 3-5 beats, one idea each |
| Twist / proof | 20-30s | The thing they did not expect, or the evidence |
| CTA + loop | last 2-3s | Ask once, then cut so it loops to the hook |

Under 30 seconds is the default. Up to 45 s only if the payload genuinely needs it.

## Stage 2 - Hook formulas that work

1. **Contradiction** - "Your phone is why your 3D looks fake."
2. **Number + outcome** - "3 settings that doubled my render quality."
3. **Direct callout** - "If you edit on your phone, stop doing this."
4. **Mid-action open** - start inside the motion, no intro.
5. **Result first** - show the finished thing, then explain how.
6. **Mistake reveal** - "I wasted 6 hours so you don't have to."

Never open with a logo, a "hey guys", or an introduction. Those are three separate scroll triggers.

## Stage 3 - Scripting (write it, do not improvise)

Format: `[SHOT] | on-screen text | voiceover line | duration`.

Rules: one idea per line, under 12 words per line, spoken at ~150 words per minute, read it aloud once and cut every word you stumbled on. Put the payoff at 60% of the runtime, not at the end - retention curves collapse after the payoff, so end fast.

## Stage 4 - Edit mechanics (CapCut / VN / Premiere Rush)

- **Cut rhythm:** a visual change every 1.5-2.5 s in the payload. A cut can be a new angle, a zoom, a text pop, a b-roll insert, or a jump cut. Something must move.
- **J-cut audio:** start the next line's audio 4-6 frames before its picture. It removes the stitched feel.
- **Punch-ins:** scale 100% to 108% on emphasis words; never more than 3 per 10 s.
- **B-roll:** 1 b-roll per 5 s maximum; every b-roll must illustrate the words being spoken at that moment.
- **Speed ramps:** 1.0x to 1.15x on transitions only. Slow motion needs 60 fps source; 30 fps slowed looks like a slideshow.
- **No transition packs.** Hard cuts and one whip pan or flash. Everything else reads as 2016.

## Stage 5 - Captions

- Burned-in captions are mandatory - most viewers watch muted.
- 3-6 words per line, 2 lines max, centred in the middle third of the frame (safe from UI overlays).
- Font: bold, heavy, high contrast; white with a 2-3 px dark stroke, or a solid accent box behind key words.
- Highlight 1-2 keywords per line in the accent colour. Never highlight everything.
- Keep captions inside the safe area: 1080x1920 frame, keep text within x 90-990, y 260-1500.

## Stage 6 - Sound design

Sound is 50% of perceived quality.

- Music: 90-110 BPM for tutorial, 120-140 for hype. Duck the music to -18 dB under voice; voice sits at -6 to -3 dB peak.
- Cut on the beat: place cuts on kicks for the payload section.
- Foley: whoosh on transitions, click on text pops, sub-bass hit on the hook. Keep all under -20 dB.
- Normalise the final mix to -14 LUFS (platform standard). Loudness mismatch is why some videos sound "cheap" next to others.
- Never use trending audio with a claim you cannot legally back; keep a licence note.

## Stage 7 - Export specs

| Platform | Frame | fps | Bitrate | Notes |
|---|---|---|---|---|
| Instagram Reels | 1080x1920 | 30 | 10-12 Mbps | under 90 s, cover frame set manually |
| YouTube Shorts | 1080x1920 | 30-60 | 12 Mbps | under 60 s for the Shorts shelf |
| TikTok | 1080x1920 | 30 | 10 Mbps | avoid watermarks from other apps |

Safe zones: keep text 250 px from the top and 320 px from the bottom (platform UI).

## Stage 8 - Repurposing matrix

One long video becomes many shorts:

1. Pick the 5 most quotable 20-second moments.
2. Each becomes one short with its own hook written fresh - never reuse the long-form sentence as a hook.
3. Re-cut the first 3 seconds differently per platform; the same hook fatigues fast.
4. Repost the best performer after 3 weeks with a new hook and cover.
5. Keep a swipe file of hooks that worked; the hook is the reusable asset, not the video.

## Stage 9 - Diagnose underperformance

| Symptom | Likely cause | Fix |
|---|---|---|
| High views, low completion | Payoff too late | Move the payoff to 60% |
| Low views, good completion | Weak hook / bad cover | Rewrite first 1.5 s, change cover frame |
| Views stall at 3 s | Setup promises nothing | Add an open loop in the first line |
| Comments say "too fast" | Cut rhythm under 1 s | Lengthen beats to 2-2.5 s |
| Looks amateur | Flat audio, no captions, wrong bitrate | Normalise to -14 LUFS, add captions, re-export |

## Quality checklist

- [ ] Hook lands in under 1.5 s, no logo or intro
- [ ] A visual change every 1.5-2.5 s in the payload
- [ ] Captions burned in, 3-6 words per line, inside safe zones
- [ ] Music ducked, mix at -14 LUFS
- [ ] Payoff at 60% of runtime
- [ ] Loops cleanly back to the hook
- [ ] Exported at platform spec, no watermark
- [ ] Cover frame chosen deliberately

## Copy-ready agent prompt

> Read the skill at the URL above. I will give you a topic and my raw material. Produce: (1) three hook options using different formulas, (2) a full shot-by-shot script table with durations, (3) the exact CapCut edit steps with cut timings, (4) caption text split per line with the keyword to highlight, (5) export settings for my platform. Then run the quality checklist on your own output and fix anything that fails.
