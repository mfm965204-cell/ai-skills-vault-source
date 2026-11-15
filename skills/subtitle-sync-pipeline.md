---
name: subtitle-sync-pipeline
description: Produce subtitles that are accurate, in sync and readable, with a timing pass, a reading-speed check and one deliverable per platform.
version: 1.0.0
license: MIT
tags: [creative, subtitles, srt, captions, video, accessibility]
---

# Subtitle Sync Pipeline

Auto-generated captions arrive with the right words in the wrong places: two-line blocks that vanish in 0.8 seconds, a speaker change with no marker, and a technical term transcribed as something else. Viewers read a third of a vertical video, so a bad caption is not a small defect - it is the video.

This skill turns a transcript into a timed subtitle file that passes four checks: sync within 100 ms, reading speed under 17 characters per second, two lines of 42 characters maximum, and a minimum display time of 1 second. You end with an SRT and a burn-in master, plus a QC sheet.

## When to use this skill

- Auto-captions are 80% right and fixing them by hand in a player takes longer than doing it properly.
- A client asked for captions in two languages and one burned-in version.
- Your videos are mostly watched on mute and the captions sit behind the action.
- A course or compliance requirement needs accurate captions with speaker labels.

Do NOT use for: translation quality on its own, dubbing, or audio repair. It also does not replace a human review for legal or medical content, where a misheard word changes meaning.

## Stage 1 - Start from a clean transcript, not from auto-captions

1.1 Transcribe with a speech model that returns word-level timestamps. Word timings are what make re-timing possible.

1.2 Correct the transcript against the audio in one pass before any timing work: names, numbers, product terms, and the client's own vocabulary list.

1.3 Keep filler words out of the caption text but keep them in the timing map. Removing them shifts every later cue if done after timing.

1.4 Agree the spelling of proper nouns with the client in a glossary file. "Razorpay" written four ways across a course is a visible defect.

| Input | Required | Why |
|---|---|---|
| audio | 48 kHz, clean | transcription accuracy |
| word timings | per word | re-timing and sync |
| glossary | names and terms | consistency |
| speaker map | who speaks when | labels |

Gate: transcript corrected against audio, glossary applied, word timings available.

## Stage 2 - Segment by sentence, then split by reading speed

2.1 Start from sentence boundaries from the transcript. A cue that breaks mid-clause forces the eye to jump.

2.2 Split any cue longer than 42 characters per line into two lines at a natural break - after a comma, before a conjunction, never mid-phrase.

2.3 If a sentence needs three lines, split it into two cues. Three lines is a wall on a phone.

2.4 Keep a maximum of 2 lines per cue and 84 characters total.

2.5 Never break a line between an article and its noun, or between a number and its unit.

| Rule | Value | Failure it prevents |
|---|---|---|
| max lines | 2 | wall of text on mobile |
| max chars per line | 42 | overflow and reflow |
| max chars per cue | 84 | reading speed blowout |
| min cue duration | 1.0 s | flicker |
| max cue duration | 7 s | stale text |

Gate: zero cues with 3 lines, and zero lines over 42 characters.

## Stage 3 - Set timing from the audio, not from the model

3.1 Snap each cue's start to the first word's onset and its end to the last word's offset, then add 2 frames (about 80 ms) of lead-in.

3.2 Leave a minimum gap of 2 frames between cues. Cues that touch read as one block.

3.3 Extend a cue's end to the next cue's start minus the gap, up to 7 seconds, so short cues do not flash.

3.4 Move a cue earlier rather than later when it feels late: viewers notice late captions more than early ones.

3.5 Check 5 random cues against the waveform at 100% zoom. Sync errors cluster at cuts and at music beds.

```python
MIN_DUR, MAX_DUR, GAP = 1.0, 7.0, 0.08   # seconds
def retime(cues):
    for i, c in enumerate(cues):
        c["end"] = max(c["end"], c["start"] + MIN_DUR)
        c["end"] = min(c["end"], c["start"] + MAX_DUR)
        if i + 1 < len(cues):
            limit = cues[i + 1]["start"] - GAP
            c["end"] = min(c["end"], max(c["start"] + MIN_DUR, limit))
    return cues
```

Gate: 5 spot-checked cues within 100 ms of the audio, and no cue shorter than 1 second.

## Stage 4 - Enforce reading speed

4.1 Reading speed is characters per second: `len(text_without_spaces) / duration`. Target under 17 cps for general content, under 15 for dense technical content.

4.2 For a cue over the limit, either extend the duration into available silence or shorten the text. Shortening is usually correct.

4.3 Shortening rules: drop "you know", "sort of", repeated words, and redundant subject pronouns. Never drop a number or a negation.

4.4 Re-check after shortening - a shortened cue that now ends 2 seconds before the speech is worse than the long one.

| Content type | Target cps | Hard limit |
|---|---|---|
| conversational | 15-17 | 20 |
| technical or course | 12-15 | 17 |
| children's content | 10-12 | 15 |
| translated subtitles | 12-15 | 17 |

Gate: no cue above the hard limit for its content type, measured by script, not by eye.

## Stage 5 - Add speaker labels and non-speech cues

5.1 Label speakers as `- Name:` on the first cue of a speaker change, then drop the label until the speaker changes again.

5.2 Use brackets for non-speech only when it carries meaning: `[laughs]`, `[phone rings]`, `[music]`. Do not describe every pause.

5.3 For two speakers in one cue, use a hyphen and a line break per speaker.

5.4 Keep labels consistent with the glossary. A name spelled two ways in captions looks careless even when the audio is right.

Gate: every speaker change is marked, and no cue has an unlabelled speaker when two people talk.

## Stage 6 - Decide the deliverable per platform

6.1 Sidecar SRT for YouTube and most players; WebVTT for web players, which needs `WEBVTT` as the first line and `.` as the millisecond separator.

6.2 Burn-in for vertical social video, where the platform's own captions are often turned off by default and captions carry retention.

6.3 Burn-in needs safe-area placement: bottom 20% is covered by the UI on several apps. Place captions at 60-70% height, not at the bottom.

6.4 For burned-in captions, use a heavy weight with a stroke or a 60% background box. Plain thin text over video is unreadable at 480p.

| Deliverable | Format | Placement |
|---|---|---|
| YouTube | SRT sidecar | platform default |
| web player | WebVTT | platform default |
| reels and shorts | burned-in | 60-70% height, centred |
| course platform | SRT plus VTT | platform default |

Gate: one file per platform, in the format that platform reads, with the right placement for burn-in.

## Stage 7 - Run QC against a fixed list

7.1 Play the whole video with captions on at 1x. Skipping is how a 0.4-second cue survives.

7.2 Check the four numbers with a script: max lines, max chars per line, min duration, max cps.

7.3 Check the first 10 seconds and the last 10 seconds by hand. Those are where cues get clipped by export ranges.

7.4 Check on a phone at 50% brightness. Captions that pass on a desktop monitor can disappear on a phone outdoors.

7.5 Watch once muted with the audio off entirely. If the story is unclear, the captions are doing too little.

```bash
python3 qc.py subtitles.srt --max-lines 2 --max-chars 42 \
  --min-dur 1.0 --max-cps 17
# exits 1 with a per-cue report if any rule fails
```

Gate: script passes all four rules, and one full watch-through with audio off is clear.

## Stage 8 - Package and hand over

8.1 Name files by video id and language: `ep04-hi.srt`, `ep04-en.vtt`.

8.2 Deliver the SRT, the VTT, the burn-in master and the QC report together. A client who receives only the SRT will burn it in badly.

8.3 Include the glossary and the timing convention in a one-page note, so the next editor matches it.

8.4 Archive the word-level timing file. Re-timing for a new cut takes minutes from timings and hours from audio.

| File | Purpose | Named |
|---|---|---|
| `ep04-en.srt` | sidecar captions | video id plus language |
| `ep04-en.vtt` | web player | same stem |
| `ep04-en-burn.mp4` | social master | suffix |
| `ep04-qc.txt` | QC report | same stem |

Gate: all four files present, named to the convention, and the QC report shows a pass.

## Stage 9 - Keep quality as volume grows

9.1 Keep a 20-cue sample from each language reviewed by a human every batch. Auto-translation errors repeat, so a sample catches the pattern.

9.2 Track two numbers per batch: cues changed after QC, and average cps. Rising edits mean the transcription step is degrading.

9.3 Store the glossary per client and per project. Most caption defects are naming defects.

9.4 For medical, legal or financial content, require a human review of every cue and say so in the delivery note.

9.5 Keep a caption style guide of 6 rules for the client: line length, speaker labels, numbers as digits, no filler, placement, and how to write a range of numbers.

9.6 Never ship machine-translated captions unreviewed for content that makes a claim - medical, legal or financial. A mistranslated caption is a claim in the client's name.

Gate: a sample review per batch, with the two numbers recorded.

## Worked example

A 12-episode course, 8 minutes each, auto-captions replaced.

| Item | Before | After |
|---|---|---|
| Source | auto-captions, no word timings | corrected transcript with timings |
| Cues over 2 lines | 61 | 0 |
| Cues over 17 cps | 148 | 0 |
| Cues under 1 second | 27 | 0 |
| Speaker labels | none | on every change |
| Deliverables | SRT only | SRT, VTT, burn-in, QC report |
| Sync spot-check | not done | 5 cues per episode within 100 ms |
| Human review | none | 20-cue sample per episode |

The largest fix was segmentation: the auto-captions had been cut on a fixed character count, which broke clauses mid-phrase in 40% of cues.

## Quality checklist

- [ ] Transcript corrected against audio before any timing
- [ ] Word-level timings available
- [ ] Client glossary applied and names consistent
- [ ] No cue has more than 2 lines
- [ ] No line over 42 characters
- [ ] No cue over 84 characters in total
- [ ] Minimum cue duration of 1 second enforced
- [ ] Maximum cue duration of 7 seconds enforced
- [ ] 2-frame gap between cues
- [ ] 5 cues spot-checked within 100 ms of the audio
- [ ] Reading speed under the limit for the content type
- [ ] Shortening never removes a number or a negation
- [ ] Speaker changes labelled consistently
- [ ] Non-speech cues only where they carry meaning
- [ ] Burn-in placed at 60-70% height, not the bottom
- [ ] QC script passes all four rules and a muted watch-through is clear

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Captions flash and vanish | Cues below 1 second, no minimum duration | Enforce 1 s minimum, extend into silence |
| Captions read as one block | No gap between adjacent cues | 2-frame gap between cues |
| Text overflows the frame | Lines over 42 characters | Re-split at clause boundaries |
| Viewer cannot keep up | Reading speed above 17 cps | Shorten text, then re-time |
| Captions late by half a second | Timing taken from the model, not the audio | Snap to word onsets, add 2 frames lead-in |
| Name spelled three ways | No glossary | Glossary per client, applied in one pass |
| Burned-in captions hidden by UI | Placed at the bottom edge | Move to 60-70% height |
| Captions invisible on a phone | Thin font over bright video | Heavy weight, stroke or 50% box |
| First cue clipped | Export range cut before the first cue ends | Check first and last 10 seconds by hand |
| Course captions wrong on technical terms | Auto-translation without review | 20-cue human sample per batch |
| Style drifts between episodes | No written caption guide | Six-rule style guide per client |
| A mistranslated claim shipped | Machine translation reviewed by nobody | Human review for any content with a claim |

## Copy-ready agent prompt

> Read the skill at the URL above and build subtitles for my video. Ask me: the video length, the language, the platform it is for, whether I have a transcript with word timings, and the client's glossary of names and terms. Then correct the transcript, segment by sentence with a 2-line 42-character limit, time each cue to the audio with a 1-second minimum, a 7-second maximum and a 2-frame gap, enforce the reading-speed limit for my content type, add speaker labels and meaningful non-speech cues, and produce the right deliverable per platform - SRT, VTT and a burn-in master with captions at 60-70% height. Finish with the QC script and the 4-rule check plus a muted watch-through. Tell me which cues fail each rule before and after your pass.
