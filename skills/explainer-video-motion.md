---
name: explainer-video-motion
description: Make a 60-90 second motion explainer that holds attention - a word-counted script, an 8-12 frame storyboard, a two-font style system, build in CapCut, After Effects or Remotion, timing to the voiceover, sound design and platform exports.
version: 1.0.0
license: MIT
tags: [creative, video, motion-graphics, explainer, remotion, captions]
---

# Explainer Video Motion Graphics

An explainer fails in the first 4 seconds, not the last 4. If the opening frame is a logo animation, the viewer is gone before the problem is named - and the remaining 80 seconds were wasted work.

This skill builds the script first, then the frames, then the motion, with a word count that matches the runtime and a timing sheet that keeps every scene on the voiceover beat.

## When to use this skill

- You need to explain a product, process or idea in 60-90 seconds.
- A landing page converts on text alone and you want video on it.
- You have a voiceover or transcript and need visuals that follow it.
- You want to produce these repeatedly, so the template matters more than one video.

Do NOT use for: a live-action brand film, a 30-second ad built for paid placement (different pacing and hook rules), or a tutorial over 5 minutes - that is a screen-recording job.

## Stage 1 - Write the script to a word count

1.1 Speaking pace for narration is 140-160 words a minute. A 60-second explainer is 140-160 words, and that is the whole budget.

1.2 Structure in five beats: the problem (0-10 s), why it is hard (10-25 s), what you do (25-50 s), proof (50-70 s), the one action (70-90 s).

| Runtime | Words | Beats | Scenes |
|---|---|---|---|
| 30 s | 70-80 | 3 | 4-5 |
| 60 s | 140-160 | 4 | 8-10 |
| 90 s | 210-240 | 5 | 10-14 |
| 120 s | 280-320 | 5-6 | 14-18 |

1.3 Write the first line as the problem in the viewer's words, not yours. "Your invoices are paid 45 days late" beats "Introducing our payment platform".

1.4 Cut every sentence that explains the company. Nobody watches an explainer to learn when you were founded.

1.5 Read the script aloud with a timer. If it runs 12 seconds over, cut words, do not speed up the read.

1.6 Mark the beat boundaries in the script; those marks become scene cuts later.

Gate: a script at the word count, timed aloud, with five beats marked.

## Stage 2 - Storyboard 8-12 frames

2.1 One frame per sentence group, sketched as a box with three labels: what is on screen, what moves, what text appears.

2.2 Every frame must be understandable as a still. If a frame needs the previous one to make sense, it is a transition, not a scene.

2.3 Put the number or the noun on screen when it is spoken. A viewer who looks away for 2 seconds should still catch the claim.

2.4 Vary the frame type: full-bleed illustration, UI close-up, data callout, human moment. Twelve identical cards is a slideshow.

2.5 Plan the transitions as part of the board - a match cut or a continuous line costs nothing and a random spin costs 20 minutes.

| Frame type | Use for | Build time |
|---|---|---|
| Illustration | abstract problem | 30-60 min |
| UI close-up | product proof | 15-30 min |
| Data callout | a number that matters | 10-20 min |
| Kinetic type | a single claim | 10-15 min |
| Human/photo | emotion, trust | 15 min |

2.6 Number the frames and put the script line under each one, so the board and the audio cannot drift apart.

Gate: a board where each frame carries one script line and one motion note.

## Stage 3 - Record or generate the voiceover

3.1 Record a human when the brand has a voice worth hearing; use TTS when you need five language variants of the same 60 seconds.

3.2 Record in a treated space at 48 kHz, peaks at -18 dBFS, 10-15 cm from the mic, and read 5% slower than feels natural.

3.3 Record each beat as a separate take, named by beat. Re-cutting one beat then costs 40 seconds, not a full re-record.

3.4 If you use TTS, pick one voice and keep it for every video; changing voice between episodes resets recognition.

3.5 Keep the voiceover under 60 seconds for a 60-second video. Audio that runs long forces either a cut or an overrun.

3.6 Normalise the voiceover to -16 LUFS mono before editing, so the music bed can be set relative to a known level.

Gate: one voiceover file per beat, normalised, with a timing sheet of start and end per beat.

## Stage 4 - Fix the style system before building

4.1 Two fonts: one for headlines with weight, one for body and labels. A third font is always a mistake.

4.2 Four colours: background, text, accent, and one highlight for data. Everything else is a tint of those.

4.3 One grid: a 12-column layout at 1920x1080, with a 60 px margin and a consistent safe area for captions.

4.4 Type sizes from a fixed scale: 96 px headline, 56 px sub, 32 px label, 24 px caption. Consistent sizes read as craft.

4.5 Pick one motion rule and repeat it: elements enter from 24 px below with a 240 ms ease-out and a 60 ms stagger.

4.6 Set the safe zones once: keep text out of the bottom 220 px for platform UI, and out of the top 120 px.

| Element | Value | Why |
|---|---|---|
| Canvas | 1920x1080 | 16:9 master |
| Vertical cut | 1080x1920 | Reels, Shorts |
| Margin | 60 px | breathing room |
| Headline | 96 px | readable at 480p |
| Body/label | 32 px | minimum for phone |
| Caption | 24 px | with 2-line limit |
| Enter motion | 24 px, 240 ms ease-out | consistent feel |
| Stagger | 60 ms per element | reads as deliberate |

Gate: a style sheet with fonts, colours, sizes and one motion rule.

## Stage 5 - Build the scenes

5.1 Choose the tool by team, not by capability: CapCut or Canva for speed, After Effects for control, Remotion for anything generated from data or repeated monthly.

5.2 Build the master timeline at 1920x1080, 30 fps, with the voiceover as the first track and beats marked on it.

5.3 Build one hero scene completely, then template it. The other eleven scenes are variations, and consistency is what makes it look designed.

5.4 For code-driven video, Remotion lets you build from a data file, so a monthly explainer becomes a JSON edit:

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Claim = ({ text, start, accent }: { text: string; start: number; accent: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - start * fps;
  const enter = spring({ frame: local, fps, config: { damping: 18, mass: 0.6 } });
  const y = interpolate(enter, [0, 1], [24, 0]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: 60 }}>
      <h1 style={{ transform: `translateY(${y}px)`, opacity, fontSize: 96,
                   color: accent, fontFamily: "Inter, sans-serif", margin: 0 }}>{text}</h1>
    </AbsoluteFill>
  );
};
```

5.5 Keep every asset inside the project folder, named by frame number. A missing font at render time is a day lost.

5.6 Render a low-quality pass every 3 scenes and watch it at phone size. Problems that are invisible on a 27-inch monitor are obvious at 390 px.

Gate: all scenes built, one low-quality pass watched on a phone.

## Stage 6 - Time everything to the voiceover

6.1 Place each scene's start on the spoken beat, not on a round number. A cut 300 ms late reads as a mistake.

6.2 Put the key word on screen within 400 ms of hearing it. Later than that and the viewer has already moved on.

6.3 Leave 400-600 ms of silence between beats. Continuous narration with no gaps feels rushed and unmemorable.

6.4 Hold the final frame for at least 1.5 seconds so the call to action is readable without pausing.

6.5 Check the total runtime against the platform: 15 s, 30 s, 60 s are the useful lengths; 47 seconds is not.

| Beat | Duration | Hold after |
|---|---|---|
| Problem | 8-10 s | 500 ms |
| Why hard | 12-15 s | 400 ms |
| What you do | 20-25 s | 500 ms |
| Proof | 15-20 s | 400 ms |
| Action | 8-10 s | 1500 ms |

Gate: every cut lands on a beat, final frame held 1.5 s or longer.

## Stage 7 - Sound design and music

7.1 Music bed at -24 to -28 LUFS under the voice, ducked by 6-10 dB whenever narration plays.

7.2 Choose music with no vocals and no strong melody in the 1-4 kHz range where speech lives.

7.3 Add a transition sound only where the scene changes meaning, not on every cut. Six whooshes in 60 seconds is noise.

7.4 Mix in order: voice first, then music under it, then effects, then master to -14 LUFS for web platforms.

7.5 Check the mix on a phone speaker, which is where most viewers will hear it, and on headphones for balance.

7.6 Keep the music licence file with the project. A copyright claim on a paid ad is an expensive lesson.

```bash
# mix voice + bed, duck the bed, master for web
ffmpeg -i voice.wav -i music.wav -filter_complex \
"[1:a]volume=0.18,aloop=loop=-1:size=2e9[bed]; \
 [0:a][bed]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck]; \
 [0:a][duck]amix=inputs=2:duration=first:dropout_transition=0[mix]; \
 [mix]loudnorm=I=-14:TP=-1.5:LRA=9[out]" -map "[out]" -c:a aac -b:a 192k mix.m4a
```

Gate: voice intelligible on a phone speaker with the music playing.

## Stage 8 - Captions, because most viewers watch muted

8.1 Burn captions for social cuts and provide an SRT for the site version. Assume at least half of the views are silent.

8.2 Two lines maximum, 32-42 characters per line, at 24-28 px with a 2 px shadow or a solid background bar.

8.3 Sync captions to the spoken word, not to the scene. Auto-captions are 85-95% right and the remaining errors are always names and numbers.

8.4 Correct every proper noun and number by hand. A wrong figure in a caption is worse than no caption.

8.5 Keep captions out of the bottom 220 px so platform UI does not cover them.

Gate: captions hand-corrected, readable at 480p width.

## Stage 9 - Export for each destination

9.1 Master once at high quality, then derive per platform. Never re-edit for a different aspect ratio.

| Destination | Resolution | FPS | Bitrate | Audio |
|---|---|---|---|---|
| Master | 1920x1080 | 30 | 16-20 Mbps H.264 | AAC 192 kbps |
| Website embed | 1280x720 | 30 | 4-6 Mbps | AAC 128 kbps |
| YouTube | 1920x1080 | 30 | 12-16 Mbps | AAC 192 kbps |
| Reels / Shorts | 1080x1920 | 30 | 8-10 Mbps | AAC 128 kbps |
| LinkedIn | 1920x1080 or 1080x1080 | 30 | 8 Mbps | AAC 128 kbps |

9.2 Keep the file under 200 MB for a web embed; a 60-second video over 40 MB is a slow page, not a video.

9.3 Use H.264 with `yuv420p` and `+faststart` for web compatibility. H.265 breaks older Android browsers.

9.4 Derive the vertical cut by re-framing, not by cropping blind. A centre crop cuts the headline in half.

9.5 Name files by version and destination: `explainer-v3-web.mp4`, `explainer-v3-reels.mp4`.

Gate: every destination has a file at spec, all playing on an Android phone.

## Stage 10 - Quality pass and handoff

10.1 Watch the whole video muted first, then with sound. Muted shows whether the visuals carry the story; sound shows whether the timing works.

10.2 Watch at 25% speed and look for elements that pop in a frame late or sit 4 px off the grid.

10.3 Check spelling on every frame, and read the numbers against the source. A wrong number survives every review except this one.

10.4 Get one review from someone outside the project, with one question: what does this product do? If they cannot answer, the script is wrong.

10.5 Deliver the project folder: assets, fonts, the data file, the licence, and the render command.

10.6 Keep a `changelog.md` per video so version 4 does not repeat version 2's mistake.

10.7 Export a still of the first frame and the last frame. They are the thumbnail and the end card, and they should each work alone.

Gate: muted watch, spelling pass, one outside review, project folder handed over.

## Worked example

A 60-second explainer for an invoicing tool, built in Remotion from a JSON data file.

| Beat | Words | Seconds | Scene |
|---|---|---|---|
| Problem | 26 | 10 | invoice dates floating past, one red overdue |
| Why hard | 34 | 13 | three tools with a broken link between them |
| What you do | 56 | 22 | UI close-up: create, send, remind |
| Proof | 26 | 11 | "paid 12 days faster" callout with a bar |
| Action | 14 | 4 | one button, held 1.5 s |

Total 156 words, 60 seconds. The first build ran 71 seconds because the proof beat was 22 seconds of narration; cutting 14 words fixed it without touching a single animation.

## Quality checklist

- [ ] Script at 140-160 words for 60 seconds, timed aloud
- [ ] First line names the problem, not the company
- [ ] Five beats marked in the script
- [ ] 8-12 storyboard frames, each with one script line
- [ ] Every frame readable as a still
- [ ] Voiceover recorded per beat, normalised to -16 LUFS
- [ ] Two fonts, four colours, one grid, fixed type scale
- [ ] One motion rule repeated everywhere
- [ ] Hero scene templated before building the rest
- [ ] Key word on screen within 400 ms of the audio
- [ ] 400-600 ms of silence between beats
- [ ] Final frame held at least 1.5 seconds
- [ ] Music ducked 6-10 dB under narration, no vocals
- [ ] Captions hand-corrected, two lines maximum
- [ ] Master exported, then derived per platform
- [ ] H.264, yuv420p, faststart, under 200 MB for web
- [ ] Watched muted, then with sound
- [ ] Outside review answered "what does this do?"

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Viewers drop at 3 seconds | Opening on a logo animation | Open on the problem in the viewer's words |
| Video runs 70 s for a 60 s slot | Script written to a word count nobody timed aloud | Cut words, never speed up the narration |
| Feels like a slideshow | Twelve frames of the same card type | Mix illustration, UI, data and type frames |
| Text unreadable on a phone | Body text at 18-20 px | Minimum 32 px for labels, 24 px for captions |
| Cuts feel late | Scenes placed on round numbers, not on beats | Snap every cut to the spoken beat |
| Music fights the voice | Bed at -16 LUFS with no ducking | -24 to -28 LUFS bed, sidechain duck 6-10 dB |
| Caption shows the wrong number | Auto-captions accepted without a pass | Hand-correct every proper noun and figure |
| Vertical cut crops the headline | Centre crop of a 16:9 master | Re-frame per scene for 9:16 |
| Web embed takes 8 seconds to start | H.265 or 90 MB file | H.264, faststart, under 40 MB for embeds |
| End card unreadable | Call to action held under 1 second | Hold the last frame 1.5 seconds minimum |

## Copy-ready agent prompt

> Read the skill at the URL above and make a motion explainer with me. Ask me: what the product does, who it is for, the runtime I want, the language, and whether I have a voiceover or need one. Then write the script to the word count for that runtime with five beats marked, then an 8-12 frame storyboard with one script line per frame. Give me the style sheet with two fonts, four colours, the type scale and one motion rule, then the build plan for my tool, the timing table with beat durations and holds, the sound design levels, the caption rules and the export specs per platform. Tell me what to cut if the narration runs long.
