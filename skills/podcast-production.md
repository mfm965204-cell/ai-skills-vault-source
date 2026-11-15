---
name: podcast-production
description: Produce a podcast episode that sounds professional - format and brief, mic and room setup, a double-ender for remote guests, the edit chain with exact EQ and loudness targets, show notes, artwork, RSS and distribution to every platform.
version: 1.0.0
license: MIT
tags: [creative, podcast, audio, editing, rss, distribution]
---

# Podcast Production

Listeners forgive a dull topic and never forgive bad audio. The difference between an amateur episode and a professional one is mostly four things: mic distance, a treated room, a consistent loudness, and a transcript.

This skill is the full chain from brief to published episode, with the numbers for each step: -18 dBFS peaks in recording, -16 LUFS for stereo delivery, 80 Hz high-pass, 3:1 compression, and an RSS feed that every platform accepts.

## When to use this skill

- Starting a podcast and unsure which of the 40 decisions actually matter.
- Existing episodes sound quiet in a car and loud in headphones.
- Guests record remotely and one side sounds like a phone call.
- You need to publish to Spotify, Apple and YouTube without a host that locks you in.

Do NOT use for: music production or mastering a song (different loudness targets), or video-first podcasts where the camera work dominates - the audio half of this still applies.

## Stage 1 - Decide the format and write the brief

1.1 Choose one format and keep it for 20 episodes: solo commentary, interview, two-host conversation, or narrative with edits. Switching formats resets your audience's expectations.

1.2 Set the length from the format, not from ambition. A solo episode of 12-20 minutes is easier to sustain than a 90-minute interview.

1.3 Write a one-page brief per episode: the question the episode answers, three points, the guest's one useful story, and the closing call to action.

1.4 Decide the release cadence and stick to it. Weekly for 8 weeks beats daily for 6 days and then silence.

| Format | Target length | Prep time | Editing time per finished hour |
|---|---|---|---|
| Solo commentary | 12-20 min | 45 min | 1.5-2 h |
| Two hosts | 30-45 min | 30 min | 2-3 h |
| Interview | 35-55 min | 60 min | 2.5-4 h |
| Narrative | 15-25 min | 3-5 h | 6-10 h |

1.5 Write the first 30 seconds word for word. The intro is where most listeners leave, and an unscripted intro rambles.

1.6 Decide the call to action before recording: subscribe, a newsletter, a product, or nothing. One ask per episode.

Gate: a one-page brief with the episode question and three points.

## Stage 2 - Set up the recording so the edit is short

2.1 Mic 10-15 cm from the mouth, slightly off-axis so plosives miss the capsule. Distance is the single biggest quality factor after the room.

2.2 Record at 48 kHz, 24-bit WAV. Voice at 44.1 kHz is fine, but 48 kHz matches video if the episode ever becomes a clip.

2.3 Set gain so normal speech peaks at -18 dBFS and never touches 0. Leave 6 dB of headroom; clipping cannot be repaired.

2.4 Kill the room before buying gear. A duvet behind the speaker, a rug, and a mic close to the mouth beats a ₹40,000 microphone in a bare room.

2.5 Turn off everything that makes noise: fans, notifications, the fridge two rooms away, and the laptop's own fan by closing heavy apps.

2.6 Monitor with closed-back headphones, and record a 20-second test to listen back before the guest joins.

| Setting | Value | Why |
|---|---|---|
| Sample rate | 48 kHz | video-compatible |
| Bit depth | 24-bit | headroom for editing |
| Speech peaks | -18 dBFS | room for loud moments |
| True peak ceiling | -6 dBFS | never clip |
| Mic distance | 10-15 cm | presence without plosives |
| Noise floor | under -60 dBFS | room tone must be quiet |

Gate: a 20-second test recording with peaks at -18 dBFS and a noise floor under -60 dBFS.

## Stage 3 - Record remote guests properly

3.1 Never record a guest through a call platform if you can avoid it. Zoom and Meet compress audio to save bandwidth, and that compression is permanent.

3.2 Use a double-ender: each side records locally at full quality and sends the file afterwards. The call is only for conversation; the audio comes from the local recordings.

3.3 If a double-ender is impossible, use a platform with a local-recording option or a dedicated remote-recording service that stores lossless tracks.

3.4 Record a shared clap or count at the start. It gives you a visible waveform spike to align tracks to within 1 ms.

3.5 Tell the guest the setup in advance: headphones, quiet room, no speakerphone, and a hard-wired connection if possible.

3.6 Always record a backup track on your side. A guest whose file fails to upload is a re-recorded episode.

3.7 Keep the video call running for the conversation even when recording locally - people talk better when they can see a face, and the call audio is only a backup.

Gate: two local tracks plus an alignment spike, or a documented reason why not.

## Stage 4 - Run the edit chain in order

4.1 Order matters: cleanup, then EQ, then compression, then de-essing, then loudness normalisation. Normalising before compression means doing it twice.

4.2 Cut the content first: remove false starts, long pauses, filler words that repeat, and any tangent that does not serve the brief. Aim to cut 10-25% of an interview.

4.3 Clean up room tone and mouth noise before any tonal processing; a noise reducer applied after compression amplifies the artefacts.

4.4 Apply the chain with these starting values and adjust by ear:

| Step | Setting | Purpose |
|---|---|---|
| High-pass filter | 80 Hz, 12 dB/oct | removes rumble and handling noise |
| Low-mid cut | -2 to -3 dB at 250-400 Hz | removes boxiness |
| Presence lift | +1.5 to +2 dB at 3-5 kHz | intelligibility |
| De-esser | 5-8 kHz, 3-6 dB reduction | kills sibilance |
| Compressor | 3:1, attack 10 ms, release 100 ms, 3-6 dB gain reduction | evens the level |
| Limiter | -1.5 dBTP ceiling | prevents clipping |
| Loudness | -16 LUFS integrated, stereo | platform-consistent |

4.5 Process the two speakers separately. One track's gain and EQ should not be applied to a guest recorded in a different room.

4.6 Do a two-pass loudness normalisation with ffmpeg so the measurement and the correction use the same reference:

```bash
# pass 1: measure
ffmpeg -i episode.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2> measured.json
# pass 2: apply the measured values (fill from measured.json)
ffmpeg -i episode.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-19.4:measured_TP=-2.1:measured_LRA=8.6:measured_thresh=-30.2:offset=0.3:linear=true \
  -ar 48000 -c:a pcm_s24le episode-master.wav
```

4.7 Export a master WAV and an MP3 at 128 kbps mono or 192 kbps stereo. Speech is fine at 96-128 kbps mono; stereo music beds need 192.

4.8 Do the export in one command so the settings cannot drift between episodes:

```bash
# delivery MP3 from the normalised master, with metadata
ffmpeg -i episode-master.wav -c:a libmp3lame -b:a 128k -ac 1 -ar 44100 \
  -metadata title="Ep 12 - 900 tickets a week" -metadata artist="Show Name" \
  -metadata album="Show Name" -metadata track="12" -metadata date="2026" \
  -metadata genre="Business" -i cover-3000.jpg -map 0:a -map 1:v \
  -c:v mjpeg -id3v2_version 3 -metadata:s:v title="Album cover" \
  -metadata:s:v comment="Cover (front)" episode-12.mp3
```

Gate: master at -16 LUFS plus or minus 0.5, true peak under -1.5 dBTP.

## Stage 5 - Write show notes and chapters

5.1 The episode title is a promise, not a label: "How a 3-person team handles 900 tickets a week" beats "Episode 12 with Ravi".

5.2 Write a 2-3 sentence description with the guest's name, the core claim, and one number.

5.3 Add timestamps at every topic change, in `mm:ss` format. Chapters are what turn a 45-minute episode into something a listener can navigate.

5.4 Produce a transcript. It doubles as a search asset, an accessibility feature, and the source for clips and quotes.

5.5 Link everything mentioned, once each, at the bottom. Broken links in show notes are worse than no links.

5.6 Keep a `show-notes.md` template so the structure never varies and publishing stays a 15-minute job.

Gate: title, description, chapters and transcript ready before upload.

## Stage 6 - Make the artwork and metadata

6.1 Cover art at 3000x3000 px, JPEG or PNG, under 500 KB, with no text smaller than about 60 px at that size - it is read at 60 px on a phone.

6.2 Use two colours and one large word or symbol. Podcast art is seen at thumbnail size, and detail disappears.

6.3 Keep the same artwork for at least a year. Listeners navigate by the image, not the name.

6.4 Set the ID3 tags: title, artist, album, track number, year, genre and cover art embedded in every file.

| Asset | Spec | Check |
|---|---|---|
| Cover art | 3000x3000, under 500 KB | legible at 60 px |
| Episode title | under 70 characters | readable on a phone lock screen |
| Description | 2-3 sentences plus links | no broken links |
| ID3 tags | title, artist, album, track, year, art | filled in the file, not only the host |
| Transcript | plain text or VTT | matches the audio |

6.5 Embed the cover art in the MP3 itself, not only in the RSS item. Some players read only the file.

6.6 Keep a title formula you can repeat: a specific number or outcome plus the audience. It makes the 40th episode as easy to name as the first.

Gate: artwork at spec, every ID3 field filled, art embedded.

## Stage 7 - Host the audio and own the feed

7.1 Host the media files on a podcast host that gives you an RSS feed you control, with a custom domain in the enclosure URLs if possible.

7.2 Never host audio on a free file-sharing link. Enclosure URLs must be stable, direct, and served with the right content type.

7.3 Keep the feed URL permanent. Moving the feed later means every platform re-verification and a lost subscriber base.

7.4 Publish the feed at `https://yourdomain.com/feed.xml` and redirect the host's URL to it, so the host can change without changing the feed.

7.5 Validate the feed before submitting: required channel fields, item fields, GUID per episode, and an `<enclosure>` with length and type.

7.6 Check the enclosure URL returns 200 with `Content-Type: audio/mpeg` from a browser with no session, and that the `length` attribute matches the real byte size.

7.7 Back up the master files and the feed XML monthly. Hosts close, and a feed you cannot rebuild is a catalogue you lose.

Gate: a validated feed at your own domain, with one test episode.

## Stage 8 - Distribute to every platform

8.1 Submit the feed once to each directory: Spotify, Apple Podcasts, YouTube (as a podcast), and the smaller ones that matter for your audience.

8.2 Apple and Spotify both verify the feed by fetching it. Ensure it is public, returns 200, and has at least one episode with a working enclosure.

8.3 YouTube needs video or a static image; upload a 1080p file with the artwork and an audio waveform if you want the visual.

8.4 Set the episode as published, not scheduled, in one place and let the feed propagate - platforms poll on their own schedule.

8.5 Add the show to your site with an embedded player and a link to the feed, so search engines can index the transcripts.

8.6 Re-check the feed in a validator after every episode for the first 10 episodes. A single malformed item can stop Apple from updating the whole show.

Gate: show live on three platforms, feed validated, transcript indexed on your site.

## Stage 9 - Cut clips and repurpose

9.1 Pull 3 clips per episode, 30-60 seconds each, with a hook in the first 2 seconds. Vertical, captioned, and loud enough to hear on a phone speaker.

9.2 Cut on a sentence boundary and add 200 ms of silence at each end so the clip does not start mid-word.

9.3 Burn captions with a 2-line limit and high contrast. Auto-captions need a human pass; names and numbers are always wrong.

9.4 Publish one clip per day for three days, not all three at once. It extends the episode's life by a week.

9.5 Keep the transcript as a blog post with the audio embedded; it ranks for the phrases the guest actually used.

9.6 Cut clips from the transcript, not from memory. The line that reads best is usually the one you had forgotten.

Gate: three clips published per episode, captions corrected by hand.

## Stage 10 - Run the publishing checklist

10.1 A 12-item checklist, run every time, so publishing does not depend on remembering.

10.2 Check the master level, the intro and outro, the chapter timestamps, the description links and the transcript before upload.

10.3 Listen to the first 60 seconds and the last 60 seconds on a phone speaker. That is where the errors live.

10.4 Keep an episode log: number, title, guest, publish date, length, download count at 7 days.

10.5 Review downloads at 7 and 28 days. A 7-day number under 30% of subscribers usually means the title or the artwork, not the content.

10.6 Publish on the same weekday and time every week. Predictability is most of a podcast habit.

10.7 Archive the master WAV and the project file for each episode. Re-editing from a 128 kbps MP3 is a re-record.

10.8 Keep a running `episodes.md` with number, title, guest, publish date, length and 7-day downloads. It is the only reliable input to a decision about the show's direction.

Gate: checklist completed for the last three episodes, log up to date.

## Worked example

An interview podcast, 2 episodes a month, one host and a remote guest.

| Step | Before | After |
|---|---|---|
| Recording | Zoom call audio | double-ender, 48 kHz 24-bit |
| Room | bare walls, -42 dBFS noise | duvet and rug, -63 dBFS |
| Editing time | 6 h per episode | 3 h |
| Loudness | -21 LUFS, inconsistent | -16 LUFS, all episodes |
| Chapters | none | 7 timestamps per episode |
| Transcript | none | published with each episode |
| 7-day downloads | 140 | 380 after titles and artwork changed |

The downloads jump came from titles and artwork, not from audio quality. The audio work kept the people who arrived.

## Quality checklist

- [ ] One format held for 20 episodes
- [ ] One-page brief per episode with three points
- [ ] First 30 seconds scripted
- [ ] Mic at 10-15 cm, off-axis
- [ ] 48 kHz 24-bit, peaks at -18 dBFS
- [ ] Room treated, noise floor under -60 dBFS
- [ ] Double-ender for remote guests
- [ ] Alignment spike recorded
- [ ] Content cut before tonal processing
- [ ] Edit chain in order with documented settings
- [ ] Master at -16 LUFS, true peak under -1.5 dBTP
- [ ] Chapters at every topic change
- [ ] Transcript published
- [ ] Artwork 3000x3000, legible at 60 px
- [ ] ID3 tags and embedded art in every file
- [ ] Feed validated and hosted at your own domain
- [ ] Three vertical clips per episode, captions corrected
- [ ] Publishing checklist run, episode log updated

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Guest sounds like a phone call | Recorded through the call platform, not locally | Double-ender, local lossless tracks |
| Episode quiet in a car, loud in headphones | No loudness normalisation, peaks inconsistent | -16 LUFS integrated, -1.5 dBTP ceiling |
| Harsh S sounds | No de-esser, presence boost too high | De-ess 5-8 kHz before the presence lift |
| Background hiss rises after processing | Noise reduction applied after compression | Denoise first, then EQ, then compress |
| Clipping on laughs | Gain set for normal speech with no headroom | Peaks at -18 dBFS, limiter at -1.5 dBTP |
| Platforms reject the feed | Missing GUID or enclosure length | Validate the feed, add GUID and enclosure fields |
| Listeners drop at 30 seconds | Unscripted intro | Script the first 30 seconds, state the promise |
| Episode never found | Generic titles and unreadable artwork | Title as a promise, art legible at 60 px |
| Platform shows the wrong episode order | Missing or reused GUID in the feed | One permanent GUID per episode, never reused |

## Copy-ready agent prompt

> Read the skill at the URL above and produce a podcast episode with me. Ask me: the format, the length, whether the guest is remote, what gear I have and how much time I can spend editing. Then give me the one-page brief, the exact recording settings with mic distance and levels, the double-ender plan for a remote guest, and the edit chain with EQ, compression, de-essing and loudness values in order. Give me the ffmpeg commands for two-pass loudness normalisation and the export settings. Then the title formula, the chapter format, the artwork spec, the ID3 fields and the feed validation checklist. Tell me the three things most likely to make this episode sound amateur.
