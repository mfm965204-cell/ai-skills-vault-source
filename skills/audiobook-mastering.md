---
name: audiobook-mastering
description: Record, clean and master an audiobook to a retail platform's technical spec - noise floor, loudness, chapter files and a pass-fail check before upload.
version: 1.0.0
license: MIT
tags: [audio, mastering, audiobook, ffmpeg, publishing]
---

# Audiobook Mastering

Audiobooks are rejected for technical reasons far more often than for performance. The room had a fan, one chapter peaks at -0.2 dB and clips, the noise floor sits at -42 dB so every pause hisses, and the chapter files are named in an order that makes the upload tool shuffle them.

This skill takes raw narration to a submission-ready set: one folder of chapter files, each inside the platform's loudness and peak window, with a noise floor low enough to disappear, a consistent tone between sessions, and a naming scheme that survives an automated upload. The numbers here are ranges - confirm the current spec with the platform you are publishing to, because they do change.

The single check that catches most rejections is measuring integrated loudness and true peak per file, not per book. One chapter out of spec fails the whole submission.

## When to use this skill

- You have finished narration and need the files to pass a retail platform's technical review.
- A submission was rejected for noise floor, loudness or peak levels.
- Chapters recorded across several days sound different from each other.
- You are producing for someone else and need a repeatable process with a pass-fail gate.
- **Do NOT use for:** narration technique or performance coaching, music mixing, or podcast publishing - this ends at mastered chapter files and a measurement report.

## Stage 1 - Fix the recording settings before fixing anything in software

What is captured is the ceiling on what can be mastered. Set the session once and never change it mid-book.

1.1 Record at 44.1 kHz or 48 kHz, 24-bit. Retail platforms accept 44.1 kHz; recording at 24-bit leaves room for level correction without audible artefacts.

1.2 Set gain so normal speech peaks between -12 dB and -6 dB. Peaks near 0 dB cannot be fixed later; a quiet take can.

1.3 Record 30 seconds of room tone at the start of every session - the room's sound with nobody speaking. It is the raw material for noise reduction and for filling gaps.

1.4 Disable every noise source you can: fans, refrigerators, phone radios, notifications, and the machine's own fan by moving the mic away from it.

1.5 Keep the mic distance and angle identical across sessions, and mark the stand position with tape.

1.6 Note the settings in a session log: rate, bit depth, gain, mic distance, room.

Gate: every session file is 24-bit, peaks between -12 dB and -6 dB, and starts with 30 seconds of room tone.

## Stage 2 - Edit for content before touching tone

Editing and mastering are separate passes. Cutting and pasting first keeps the noise reduction consistent, because one noise profile is applied to one continuous performance.

2.1 Remove flubs, long pauses over 1.5 seconds, and any mouth noise loud enough to distract.

2.2 Keep breaths that carry meaning and cut the ones that whistle. Cut breaths to a fixed short length rather than deleting them entirely, which sounds unnatural.

2.3 Replace any fix with room tone from the same session, never with silence - digital silence next to room tone is audible.

2.4 Level-match a re-take to the paragraph around it before inserting it, or the patch will sound like a different room.

2.5 Keep an edit decision log: file, timestamp, what changed. It makes a later fix 10 minutes instead of an hour.

2.6 Export the edited pass as 24-bit WAV at the session rate and keep it. Never master from a compressed file.

2.7 Note the edit timestamps in the log as you go, not from memory afterwards. A patched paragraph found later needs its source.

Gate: the edited file has no pause longer than 1.5 seconds, no flub, and no digital silence anywhere.

## Stage 3 - Measure before you process

Every processing decision starts from a measurement. Run three numbers on each chapter: integrated loudness, true peak and noise floor.

3.1 Measure integrated loudness in LUFS with `ffmpeg`'s `loudnorm` in analysis mode, and read the printed input values.

3.2 Measure true peak, which accounts for inter-sample peaks a sample-peak meter misses.

3.3 Measure the noise floor from the room tone section, using a loudness or RMS reading of a quiet passage.

3.4 Write all three numbers per chapter into a table before any processing. If you cannot measure it, you cannot claim it is fixed.

| Measurement | Tool | Target | What it catches |
|---|---|---|---|
| Integrated loudness | `loudnorm` analysis | platform target ±1 LU | Chapters that jump in volume |
| True peak | `loudnorm` analysis | at or below -3 dBTP | Clipping the sample meter misses |
| Noise floor | RMS on room tone | -60 dB or below | Fans, fridges, hiss |
| Duration | `ffprobe` | under the file-length limit | A single 3-hour file |

```bash
ffmpeg -hide_banner -i chapter-01.wav -af loudnorm=I=-19:TP=-3:print_format=json -f null - 2>&1 | tail -14
```

Gate: loudness, true peak and noise floor are recorded per chapter in one table.

## Stage 4 - Fix the noise floor with the least processing that works

Noise reduction is the easiest way to damage a voice. Aim for the target with the smallest amount of reduction, and check the result by ear every time.

4.1 Target a noise floor at or below -60 dB. Most retail platforms want it inaudible; -60 dB is comfortably below anything a listener notices.

4.2 Take the noise profile from the session's own room tone, not from a generic profile.

4.3 Apply reduction in stages of 6-9 dB rather than one 20 dB pass, listening after each.

4.4 Listen for the artefacts that signal over-processing: a metallic tail on consonants, a swimming background, a voice that sounds underwater.

4.5 If the floor is above -45 dB, fix the room and re-record instead of processing harder. Processing cannot rescue a noisy capture without damaging the voice.

4.6 Re-measure the floor after processing and record the before and after numbers.

Gate: noise floor at or below -60 dB, and no audible artefact on a full listen of one chapter.

## Stage 5 - Normalise loudness per chapter, then check the set

Loudness normalisation is a two-pass job: measure, then apply the measured values. One-pass normalisation drifts between files.

5.1 Set the target from the platform spec. Retail audiobook specs commonly sit near -19 LUFS integrated with a true peak ceiling around -3 dB; confirm the current numbers with your platform.

5.2 Use two-pass `loudnorm`: the first pass prints measured values, the second applies them with `linear=true` so dynamics are preserved.

5.3 Apply a true-peak limiter at -3 dB after normalisation, not before - normalising after limiting will push peaks back up.

5.4 Measure every chapter again after processing and record the result in the same table.

5.5 Reject any chapter outside 1 LU of the target or above the peak ceiling, and reprocess that chapter alone.

5.6 Keep the pre-normalisation file for each chapter until the book is accepted; a re-do from a mastered file compounds limiting.

```bash
ffmpeg -i chapter-01.wav -af "loudnorm=I=-19:TP=-3:LRA=7:measured_I=-22.4:measured_TP=-4.1:measured_LRA=9.2:measured_thresh=-32.6:linear=true" \
  -ar 44100 -c:a pcm_s16le chapter-01-master.wav
```

Gate: every chapter measures within 1 LU of target and at or below the true-peak ceiling.

## Stage 6 - Check consistency across the whole book

Per-chapter compliance is not enough. A book that jumps 2 LU between chapters sounds like two narrators.

6.1 Compare the measured loudness of all chapters in one column and look at the spread. A spread above 1.5 LU is audible on headphones.

6.2 Compare the tone: pick the same sentence from chapter 1, chapter 8 and the last chapter and listen back to back.

6.3 Check the room tone level across sessions. A session recorded after a rain shower will sit differently and needs its own treatment.

6.4 Fix outliers by reprocessing the single chapter against the book's median, not by re-processing everything.

6.5 Re-listen to the first 60 seconds and the last 60 seconds of the book end to end; these are the two places a listener judges quality.

6.6 Check the noise floor across sessions too. A session recorded in a different room often needs its own noise profile even when loudness matches.

Gate: chapter loudness spread is 1.5 LU or less and the tone is consistent across sessions.

## Stage 7 - Export to the delivery spec

The export is a technical contract. Get the format, sample rate, bit depth and channel count exactly right, and keep the master separate from the delivery file.

7.1 Export delivery files as the platform requires - commonly 44.1 kHz, 16-bit, mono for spoken word; confirm before exporting.

7.2 Keep a 24-bit master folder untouched, so a spec change means re-exporting rather than re-mastering.

7.3 Name files so they sort correctly: zero-padded chapter numbers and the book title, with no spaces or punctuation.

7.4 Keep intro, outro and credits as separate files if the platform expects them separately.

7.5 Check total runtime per file against the platform's limit - a 3-hour single file usually fails.

| Name | Sorts correctly | Problem |
|---|---|---|
| `01-intro.wav` | Yes | None |
| `1-intro.wav` | No | Sorts after `10-` |
| `Chapter 1 final FINAL.wav` | No | Spaces and duplicates break upload tools |
| `intro.wav` | No | No position at all |

```bash
for f in master/*.wav; do
  ffmpeg -y -i "$f" -ar 44100 -ac 1 -c:a pcm_s16le "delivery/$(basename "${f%.wav}").wav"
done
ls delivery | sort
```

Gate: delivery files match the spec exactly, sort in chapter order, and each is under the platform's file-length limit.

## Stage 8 - Run the pass-fail check before upload

One table, every chapter, three columns, all green or nothing goes up. This is the step that prevents a rejection after a week of waiting.

8.1 Check each file's integrated loudness against the target with a 1 LU tolerance.

8.2 Check each file's true peak against the ceiling.

8.3 Check each file's noise floor from a quiet passage.

8.4 Check duration, channel count, sample rate and bit depth for every file.

8.5 Listen to 30 seconds from the middle of three chapters, chosen at random, at normal volume.

8.6 Record the pass-fail table with the date and the tool versions, so a later dispute has evidence.

8.7 Fix the chapter, not the target. Moving the target to fit a bad file is how a book ends up inconsistent.

| Check | Target | Tolerance | Chapter 1 | Chapter 12 |
|---|---|---|---|---|
| Integrated loudness | -19 LUFS | ±1 LU | -18.6 | -19.2 |
| True peak | -3 dBTP max | none | -3.4 | -3.1 |
| Noise floor | -60 dB or below | none | -64 | -61 |
| Format | 44.1 kHz, 16-bit, mono | none | pass | pass |

Gate: every cell in the pass-fail table is inside its tolerance before upload.

## Stage 9 - Archive and hand over

An audiobook has a second life: a re-issue, a sample, a platform migration. The archive is what makes that cheap.

9.1 Keep the 24-bit masters, the session log, the edit decision log and the measurement table together, in one folder per book.

9.2 Keep the raw session files for at least a year, or until the book is accepted and paid.

9.3 Write a one-page handover: settings, target spec used, platform, date, any known defects.

9.4 Store a checksum file so a corrupted archive is detectable rather than discovered years later.

9.5 Record which platform spec version the delivery was built against, with its date.

9.6 Keep the delivery folder read-only after upload, so a later edit cannot silently change what was submitted.

Gate: one folder holds masters, logs, measurements and a checksum file, with the spec version dated.

## Quality checklist

- [ ] Every session file is 24-bit with peaks between -12 dB and -6 dB.
- [ ] Every session starts with 30 seconds of room tone.
- [ ] No pause longer than 1.5 seconds survives the edit.
- [ ] No digital silence appears anywhere in the edited file.
- [ ] Loudness, true peak and noise floor are measured per chapter before processing.
- [ ] Noise floor is at or below -60 dB after processing.
- [ ] Noise reduction was applied in stages of 6-9 dB, not one large pass.
- [ ] Normalisation used two-pass `loudnorm` with linear mode.
- [ ] A true-peak limiter is applied after normalisation.
- [ ] Every chapter is within 1 LU of target.
- [ ] Chapter-to-chapter loudness spread is 1.5 LU or less.
- [ ] Delivery files match the platform's rate, bit depth and channel count.
- [ ] File names sort in chapter order with zero padding.
- [ ] The pass-fail table is complete and all green.
- [ ] Masters, logs, measurements and a checksum file are archived together.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Rejected for loudness | Per-book average measured, not per file | Measure and normalise each chapter, then verify each |
| Every pause hisses | Noise floor above -45 dB from a fan or fridge | Fix the room and re-record rather than processing harder |
| Voice sounds metallic | Noise reduction applied in one large pass | Reprocess in 6-9 dB stages and listen after each |
| Chapters sound like different narrators | Gain or mic distance changed between sessions | Re-record the outlier, or match it to the book median |
| Peaks clip after normalising | Limiter applied before normalisation | Normalise first, then limit at -3 dBTP |
| Upload order is scrambled | File names without zero padding | Rename to `01-...`, `02-...` and re-sort before upload |

## Copy-ready agent prompt

> Read the skill at the URL above and master my audiobook. Ask me for the platform and its current technical spec, then walk me through the session settings, the edit pass and the measurement of loudness, true peak and noise floor per chapter. Give me the exact ffmpeg commands for two-pass normalisation and the limiter, a per-chapter pass-fail table with tolerances, the delivery export command and the file naming scheme. Do not process anything until the measurement table exists, and tell me which chapters need re-recording rather than processing.
