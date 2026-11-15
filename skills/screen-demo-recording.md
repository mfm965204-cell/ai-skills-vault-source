---
name: screen-demo-recording
description: Record a product demo that holds attention: one outcome
scripted in beats, a clean seeded environment, readable zoom,
captions, and platform export settings.
version: 1.0.0
license: MIT
tags: [creative, video, product, demo, recording]
---

# Screen Demo Recording

Most product demos are a tour: click here, then here, then here. The
viewer learns the interface and not the outcome, and stops watching at
40 seconds. A demo works when it is built around one result and shows
the shortest path to it.

This skill covers the whole recording: a beat script with one outcome,
a seeded environment so the screen has real-looking data, resolution
and zoom rules that survive compression, narration pacing, captions,
and the export settings each platform actually wants.

## When to use this skill

- You need a 60 to 120 second demo for a landing page, an app store listing, or a sales follow-up.
- A previous recording looked blurry after upload or was unreadable on a phone.
- You are recording yourself narrating and the pauses make it feel slow.
- You want one demo asset reusable across four channels without re-recording.

Do NOT use for: a full tutorial series with chapters and exercises, or
a motion-graphics explainer with no screen capture.

## Stage 1 — Write the outcome in one sentence

The demo proves one thing. Everything that does not serve that
sentence is cut before recording.

1.1 Write it as a result the viewer wants: "you can close your books in one evening instead of three days".

1.2 Choose the shortest path that shows the result, and count the clicks; above 8 clicks, cut steps from the demo even if the product needs them.

1.3 Decide what to hide: settings, error states, and any screen that needs explaining.

Gate: one sentence, one path, 8 clicks or fewer, and a written list of
what is hidden.

## Stage 2 — Script it in beats

A beat is a 5 to 15 second unit with one visible change. Beats make
the edit and the narration fall into place.

2.1 Write 8 to 12 beats for a 90 second demo, each with what appears on screen and one line of narration.

2.2 Put the payoff in the first 15 seconds as a glimpse, then earn it — the viewer decides whether to keep watching before beat three.

2.3 End on the result and one action, not on a logo animation.

| Beat | Time | On screen | Narration |
|---|---|---|---|
| 1 | 0-8 s | result screen with 3 finished items | "This is a month of reconciliations, done." |
| 2 | 8-20 s | import a file, 4 rows appear | "Drop the bank file in." |
| 3 | 20-35 s | matches fill in | "It matches 96% of rows automatically." |
| 4 | 35-55 s | review the exceptions | "You review only what did not match." |
| 5 | 55-75 s | close the period | "Close the month, with an audit trail." |
| 6 | 75-90 s | result screen again | "One evening, not three days." |

Gate: 8 to 12 beats, the payoff appears in the first 15 seconds, and
the last beat is the result.

## Stage 3 — Seed a believable environment

Real-looking data is the difference between a demo and a screenshot of
an empty table.

3.1 Use a demo account with 30 to 60 rows of realistic data, names and amounts in the audience's currency and format.

3.2 Hide personal data, real customer names and any internal hostname; use a separate demo tenant, not production.

3.3 Set the browser to 100% zoom, hide bookmarks, extensions and notifications, and use a light or dark theme consistently with your brand.

Gate: no real customer data, no notification popups, and the screen
shows enough rows to look used.

## Stage 4 — Record at a resolution that survives compression

A 4K recording compressed to a phone screen becomes mush. Record for
the smallest target.

4.1 Record at 1920x1080 or 2560x1440, 30 fps for screen content, and never upscale a smaller capture.

4.2 Set the app zoom to 125% or 150% while recording, so text lands at 18 px or more on the captured frame.

4.3 Capture system audio separately from the microphone, so you can fix one without the other.

```bash
# macOS screen capture with a separate mic track, 1080p30
ffmpeg -f avfoundation -framerate 30 -i "1:0" -f avfoundation -i ":1" \
  -vf "scale=1920:1080" -c:v libx264 -preset veryfast -crf 18 \
  -c:a aac -b:a 192k demo-raw.mkv
```

Gate: a test export at the platform's bitrate keeps all UI text
readable on a phone.

## Stage 5 — Narrate for the edit, not for the moment

Silence and filler are what make a demo feel slow, and both are
fixable in the edit.

5.1 Speak one sentence per beat, then pause; cut the pauses in the edit so beats land 0.3 seconds apart.

5.2 Remove "so", "basically" and "as you can see" from the script before recording, not after.

5.3 Target 140 to 160 words per minute, and time the read against the beats before recording — a 90 second demo is roughly 220 words.

Gate: the read-through matches the beat timings within 5 seconds, and
no filler words remain.

## Stage 6 — Guide the eye with the cursor and zoom

The viewer watches the cursor, so the cursor is a design element.

6.1 Move the cursor in straight lines at a steady speed, and pause for 0.5 seconds before each click.

6.2 Zoom into the region that changed — a 1.6x to 2x punch-in for 2 to 3 seconds — and back out; more than 6 punch-ins in 90 seconds is dizzying.

6.3 Highlight the changed value with a subtle outline or a brief dim of the rest, not with a spotlight animation.

Gate: every click has a pause before it, and no more than 6 zoom moves
in 90 seconds.

## Stage 7 — Caption and transcribe

Most viewers watch muted, so the captions are the primary channel on
social.

7.1 Burn captions into the social cut and provide a separate subtitle file for the site version.

7.2 Keep captions to two lines of 32 characters, placed above the bottom 12% where platform UI overlaps.

7.3 Check the transcript for product names and numbers; automatic transcription gets Indian brand names wrong.

Gate: captions are accurate on a spot check of 10 terms, and no
caption sits under platform UI.

## Stage 8 — Export per platform, not one file for all

Each channel has its own aspect, duration and bitrate, and one file
fits none of them well.

8.1 Site and email: 16:9, 1080p, H.264, CRF 20, audio 128 kbps, under 25 MB for an inline embed.

8.2 Social: 9:16, 1080x1920, first 3 seconds carrying the payoff, under 60 seconds.

8.3 App store: match the store's stated spec exactly — resolution, duration and frame rate — and re-check it before each submission.

| Target | Aspect | Resolution | Duration | Notes |
|---|---|---|---|---|
| Landing page | 16:9 | 1920x1080 | 60-120 s | muted autoplay, captions burned |
| Reels / Shorts | 9:16 | 1080x1920 | under 60 s | payoff in first 3 s |
| Sales email | 16:9 | 1280x720 | under 60 s | file under 10 MB |
| App store | per store spec | per store spec | per store spec | re-check before submission |

8.4 Export the vertical cut from the same timeline, never by cropping the 16:9 master:

```bash
ffmpeg -i demo-raw.mkv \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 20 -preset slow -c:a aac -b:a 128k demo-reels.mp4
```

Gate: each export matches its target's spec, verified by reading the
file properties.

## Stage 9 — Measure and re-cut

A demo is a marketing asset with a retention curve. Read it.

9.1 Check retention at 3, 15 and 45 seconds; a drop at 3 seconds means the opening beat is wrong.

9.2 Track click-through to the call to action, not views.

9.3 Re-cut the first 15 seconds from the best-performing beat and re-test, rather than re-recording everything.

Gate: retention at 3, 15 and 45 seconds recorded, and one re-cut
tested against the original.

## Worked example - a 94 second demo, three exports

A payments product demo for a landing page, a Reels cut and a sales
email.

| Measurement | First cut | Second cut | Change |
|---|---|---|---|
| Length | 2 m 40 s | 1 m 34 s | beats cut from 17 to 10 |
| Retention at 15 s | 41% | 78% | payoff moved to beat one |
| Retention at 45 s | 22% | 61% | filler removed, pauses tightened |
| Click-through to signup | 1.1% | 2.9% | one call to action, not three |
| Re-records needed | 6 | 2 | seeded data and beat script |

The first cut opened with a login screen and a navigation tour. Moving
the finished result to the first 8 seconds lifted 15-second retention
from 41% to 78% with no other change.

The second problem was text size. The recording was made at 4K and
downscaled, so the table text was 9 px on a phone. Re-recording at
1080p with the app at 150% zoom made every figure readable and needed
no upscaling.

The third was audio. Recording system audio and microphone on one
track meant a notification sound forced a full re-record. Separating
the tracks made the fix a 20-second edit.

## Quality checklist

- [ ] One outcome sentence written before recording.
- [ ] Path is 8 clicks or fewer.
- [ ] 8 to 12 beats with narration per beat.
- [ ] Payoff visible in the first 15 seconds.
- [ ] Demo tenant seeded with 30 or more realistic rows.
- [ ] No real customer data, hostnames or notifications on screen.
- [ ] Recorded at 1080p or 1440p, 30 fps, app zoom 125% or more.
- [ ] System audio and microphone captured separately.
- [ ] Filler words removed from the script.
- [ ] Cursor pauses before every click.
- [ ] Six or fewer zoom moves per 90 seconds.
- [ ] Captions burned for social and a subtitle file for the site.
- [ ] Every export matches its platform spec.
- [ ] Retention measured at 3, 15 and 45 seconds.
- [ ] One re-cut tested against the original.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Viewers leave in the first 3 seconds | The opening shows a login or a navigation tour | Put the finished result on screen in the first beat |
| Text unreadable on a phone | Captured at 4K and downscaled to a 1080p phone frame | Record 1080p with the app zoomed to 150% |
| Demo feels slow despite a short script | Pauses left in, one take used unedited | Cut pauses to 0.3 seconds between beats |
| Notification popup in the final video | System notifications on during capture | Do not disturb on, and a dedicated capture profile |
| Auto captions get the product name wrong | Automatic transcription on a non-English brand name | Correct the transcript, then burn captions |
| Reels cut looks cropped and wrong | 16:9 export cropped to 9:16 | Re-frame per platform from the timeline, not a crop filter |
| Sales email video will not attach | Export above the mail size limit | Export 720p under 10 MB or link to a hosted page |
| Narration sounds rushed on the final cut | Script written for reading speed, not beat timing | Time the read against the beats before recording |
| Zoom moves look jerky | Punch-ins keyframed without easing | Ease each zoom over 200 ms and hold for 2 seconds |
| Demo opens on an empty state | The demo tenant was seeded minutes before recording | Seed the day before and check the row count |
| Captions cover the action | The caption band sits over the working area | Place captions above the bottom 12% and move the cursor up |

## Copy-ready agent prompt

> Read the skill at the URL above and record my product demo. Write the one-sentence outcome and an 8 to 12 beat script with the payoff in the first 15 seconds, seed a demo tenant with realistic data and no real customer information, capture at 1080p 30 fps with the app at 150% zoom and separate audio tracks, then edit to remove pauses and filler, add cursor pauses and at most 6 zoom moves, and burn captions. Export the landing page, social 9:16 and email cuts to their platform specs, and report retention at 3, 15 and 45 seconds. Stop and show me the first beat if the payoff is not on screen within 15 seconds.
