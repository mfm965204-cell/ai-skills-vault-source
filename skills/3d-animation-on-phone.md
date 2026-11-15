---
name: 3d-animation-on-phone
description: Produce a cinematic 3D animation end-to-end on a phone - no desktop, no render farm. Handles storyboard, model sourcing, rigging, lighting, camera, render and edit, with exact app settings and export specs.
version: 1.0.0
license: MIT
tags: [3d, animation, mobile, video, blender-alternative, content]
---

# 3D Animation On Phone

Turn a one-line idea into a finished 3D animation clip (9:16, 16:9 or 1:1) using only a phone.
This skill is the production pipeline, not the theory: every stage names the app, the tap path and the number to use.

## When to use this skill

- The user wants a 3D animation, product spin, logo reveal, explainer or looping background and has only a phone.
- The user wants to publish 3D content to Reels / Shorts / TikTok.
- The user wants to learn a repeatable 3D workflow rather than a one-off trick.

Do NOT use it for: 2D motion graphics that CapCut keyframes can do faster (use the short-form video skill), or photoreal VFX compositing, which needs plate tracking a phone cannot do reliably.

## Hard constraints to confirm before starting

1. **Device class** - iPhone 12+ or Android with 6GB+ RAM. Under that, cap at 720p and single-object scenes.
2. **Free storage** - at least 6 GB. Renders write temp frames.
3. **Target** - platform, aspect ratio, duration, loop or one-shot.
4. **Audio** - does the clip need a beat-synced track? If yes, lock the track first; timing drives every cut.

If the user has not stated these, ask all four in one message. Do not start modelling on a guess.

## The pipeline (7 stages, do them in order)

### Stage 1 - Beat sheet (10 minutes, in a notes app)

Write the clip as 4-6 shots with a duration in seconds for each. A 15-second clip is 4 shots of ~3.5s, not 30 shots of 0.5s - phone GPUs punish complexity.

For each shot record: subject, camera move, light mood, transition out.
Example beat sheet for a sneaker reveal:
- Shot 1, 0-3s: shoe in darkness, single rim light, slow dolly in. Cut on motion.
- Shot 2, 3-6s: hard cut to macro of sole tread, orbit right.
- Shot 3, 6-11s: full hero turntable, three-point light, 360 degrees.
- Shot 4, 11-15s: pull back to logo on floor, light sweep, hold 1s, loop back to shot 1.

Rule: the first frame must be the most interesting frame. Phone viewers decide in 0.8s.

### Stage 2 - Assets (choose the cheapest path)

Order of preference, cheapest first:

1. **Primitives and text** - most product loops are a cube, a cylinder and a light. Do not model what you can fake.
2. **Free model download** - Sketchfab (CC0 filter) or Poly Pizza. Import .glb, not .obj - materials survive.
3. **Scan** - Polycam / Luma AI room or object scan, then retopologise in-app if offered.
4. **Model in-app** - Nomad Sculpt (paid, best on phone) or Prisma3D. Budget 40 minutes per object maximum; if it takes longer the shot is too ambitious.

Decimate every imported mesh to under 150k triangles before it enters the scene. On phone hardware, triangle count is the frame rate.

### Stage 3 - Scene assembly

Use **Prisma3D** (Android/iOS) or **Spline** (iOS, web) for the scene. Both handle import, materials, lights and camera keyframes on device.

- One scene per shot. Do not animate four shots in one timeline; a phone preview will stutter and you will misjudge timing.
- Set the project frame rate to 30 fps and keep it. Mixing 24 and 30 causes visible judder after the edit.
- Name every object (`hero_shoe`, `floor`, `key_light`). Unnamed objects are un-animatable at speed.
- Duplicate, then move - never delete and rebuild a light you liked.

### Stage 4 - Lighting (the whole look lives here)

Three lights, always:

| Light | Position | Intensity guide | Purpose |
|---|---|---|---|
| Key | 45 degrees up, 30 degrees to the side | 100% | Main form |
| Fill | Opposite side, lower | 25-35% | Stops shadows going black |
| Rim / back | Behind subject, aimed at camera | 60-80% | Separates subject from background |

Then add **one** atmosphere element: a gradient background plane, a reflective floor, or volumetric fog. One. Three atmosphere tricks reads as noise.

Colour rule: warm key (3200-4000K) against cool rim (6500-7500K) instantly looks cinematic. If the brand has colours, use the brand as key and its complement as rim.

### Stage 5 - Camera and animation

- Set **depth of field** on, focus distance on the subject, f-stop 2.0-2.8 equivalent. Phone 3D without DOF looks like a toy.
- Every camera move needs an **ease**: ease-in on the start, ease-out on the stop. Linear keyframes are the single biggest tell of amateur phone 3D.
- Move one thing at a time per shot. Camera moves OR subject moves. Both at once looks chaotic at phone scale.
- Turntables: rotate the subject, not the camera. Easier to loop and to re-light.
- Loop clips: last keyframe must equal first keyframe, and the last two frames must not duplicate - trim one frame.

### Stage 6 - Render

| Output | Resolution | fps | Format |
|---|---|---|---|
| Reels / Shorts / TikTok | 1080x1920 | 30 | MP4 H.264 |
| YouTube / site hero | 1920x1080 | 30 | MP4 H.264 |
| Loop for web | 1080x1080 | 24-30 | MP4 or WebM, under 4 MB |

Render settings that matter on a phone: samples/quality at medium (not high), motion blur off (it doubles render time and phone blur is coarse), transparent background off unless compositing.

Render shot by shot and save each clip to the camera roll. A crashed app mid-render loses the whole timeline.

### Stage 7 - Edit and sound (CapCut / VN)

1. Drop shots in beat-sheet order on the timeline.
2. Cut to the music: place cuts on the kick or snare, not on the bar.
3. Add **one** transition type maximum, and only between shots 2 and 3. Hard cuts everywhere else.
4. Grade: lift blacks slightly (+5), add contrast (+8), saturate (+5). Do not stack filters.
5. Sound design carries more realism than resolution: add a whoosh on every camera move, a low sub hit on each cut, room tone underneath at -28 dB.
6. Export at the platform spec, then watch it once on the phone speaker at 50% volume - that is how it will be heard.

## Quality checklist (reject the render if any fails)

- [ ] First frame is the best frame
- [ ] No shot longer than 4 seconds without a change
- [ ] Every camera move has ease in and out
- [ ] Depth of field is on and focused on the subject
- [ ] One light mood, one atmosphere element, one transition
- [ ] Loops seamlessly if it is a loop
- [ ] Text is readable at arm's length on the phone
- [ ] Exported at the platform's exact resolution and frame rate
- [ ] Under 60 seconds unless the brief says otherwise

## Failure modes and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Preview stutters, timing wrong | Too many triangles or 4K preview | Decimate meshes, preview at 540p |
| Looks like a toy | No DOF, flat lighting, no rim light | Add rim light, f/2.4 DOF, dark background |
| Animation feels robotic | Linear keyframes | Ease in/out, offset the start by 3-4 frames |
| Export is washed out | Colour space mismatch | Force sRGB / Rec.709 on export |
| App crashes on render | RAM ceiling | Render in 2 halves, close all other apps |
| Model import is black | Missing material or no lights in scene | Add an environment light before diagnosing |

## Output contract

Deliver: the beat sheet (text), the finished MP4(s) at platform spec, the app + settings used for each stage, and a 3-line note on what to change for the next clip. If asked for a reusable template, output the beat sheet as a fill-in table.

## Copy-ready agent prompt

> You are a 3D animation director working with a phone-only pipeline. Read the full skill at the URL above and follow its 7 stages in order. Ask me the four constraint questions first, then produce a beat sheet, then guide me tap-by-tap through Prisma3D/Spline, then give me the render and export settings for my platform. Do not skip the quality checklist.
