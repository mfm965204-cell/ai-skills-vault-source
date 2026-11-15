---
name: game-dev-2d
description: Build and ship a 2D game in days, not months - core loop first, engine choice, sprite and audio pipeline, input feel, difficulty curve, juice, performance and publishing.
version: 1.0.0
license: MIT
tags: [game, gamedev, godot, phaser, 2d, indie, mobile]
---

# 2D Game Development

A finished small game beats an unfinished big one. Scope is the only real skill.

## When to use this skill

- Making a first game or a game jam entry.
- Building a hyper-casual mobile game, a web game, or an educational game.
- Prototyping a mechanic to test whether it is fun.

## Stage 1 - Scope it brutally

Write the one-sentence core loop: "The player ___ to ___, and the risk is ___."

Then set hard limits and do not negotiate with yourself:

| Limit | First game |
|---|---|
| Mechanics | 1 |
| Levels / waves | 5-10 |
| Enemies / obstacles | 3 |
| Screens | menu, game, game-over |
| Total dev time | 2-4 weeks |
| Art | one style, one palette |

If a feature is not required for the loop to be fun, it is in v2. Multiplayer, achievements, leaderboards, shop: v2.

## Stage 2 - Engine choice

| Engine | Best for | Language |
|---|---|---|
| Godot 4 | 2D games, desktop + mobile export, free | GDScript |
| Phaser 3 | Browser games, instant share link | JavaScript |
| Unity | Bigger 2D projects, huge ecosystem | C# |
| Love2D | Tiny prototypes, jams | Lua |
| Kaboom.js | Very fast web prototypes | JavaScript |

For a web game you want to share by URL: **Phaser or Kaboom**. For mobile export with real performance: **Godot 4**. Pick in 10 minutes and do not revisit.

## Stage 3 - Build the loop before any art

1. Grey boxes and circles. No sprites, no sound.
2. One input, one action, one feedback.
3. Play it for 5 minutes. If it is not fun with rectangles, art will not save it.

Fun comes from: a clear goal, a readable threat, a tight feedback loop, and slightly increasing pressure. Not from particle effects.

## Stage 4 - Feel (this is what separates good from lifeless)

- **Input latency under 100 ms.** Buffer the input 1-2 frames so a press during recovery still registers.
- **Coyote time**: allow a jump for ~6 frames after leaving a ledge.
- **Squash and stretch** on jump and land: scale 1.0 → 0.85/1.15 → 1.0 over 150 ms.
- **Screen shake** on impact: 2-4 px, 80-120 ms, then decay. More than that is nausea.
- **Hit stop**: freeze both actors 40-80 ms on a hit. It reads as impact.
- **Particles** on destruction: 6-12, short-lived, additive.
- **Sound before animation**: a click plus a flash reads better than a 20-frame animation.
- **Camera**: follow with smoothing (lerp 0.1), look ahead in the movement direction, clamp to level bounds.

## Stage 5 - Art and audio pipeline

- Pick a resolution and stick to it: 320x180 or 640x360 pixel art, or 1080x1920 for mobile portrait.
- One palette (Lospec has thousands of free ones), 3-4 shades per material, one light direction.
- Sprite sheets: consistent frame size, no padding drift, atlases packed to one texture.
- Free assets: Kenney (public domain), OpenGameArt (check licences), freesound (check licences). Keep a `CREDITS.md` from day one.
- Audio: short, punchy, compressed. One music loop per screen. Duck music under effects.

## Stage 6 - Difficulty curve

- Teach one mechanic per level, in a safe space, before testing it.
- Ramp: introduce → combine → twist → rest → escalate. A rest beat every 3 levels prevents fatigue.
- First failure should come after ~30 seconds of success, not 5.
- Death must be fast to retry: under 1.5 s from death to playing again. Long death animations kill retention.
- Difficulty options are cheaper than perfect balance: a single global speed or damage multiplier.

## Stage 7 - Performance

- Target 60 fps on the lowest device you can test. Budget: under 200 draw calls, under 100 active sprites.
- Object pooling for bullets and particles - never instantiate in the update loop.
- Texture atlas, not individual images.
- Fixed timestep for physics, interpolated rendering.
- Web: keep the whole game under 5 MB so it loads on a phone in 3 seconds.

## Stage 8 - Save, settings, accessibility

- Save to local storage with a version field; migrate, never wipe.
- Settings: mute, volume, screen shake off, reduced flashing, colourblind-safe palette option.
- Remappable or at least dual input (touch and keyboard) for web.
- Pause on tab blur. Mobile: handle the app going background mid-level.

## Stage 9 - Publish

- Web: static export, deploy to Cloudflare Pages/Netlify, test the share link on a phone in portrait and landscape.
- Mobile: portrait lock, safe-area insets, no reliance on hover.
- itch.io for feedback rounds; add a devlog and a GIF that shows the loop in 3 seconds.
- Ship with a 30-second trailer cut from actual gameplay, first 3 seconds showing the core loop.

## Quality checklist

- [ ] Core loop fun with grey boxes before any art
- [ ] Input latency under 100 ms with buffering
- [ ] Juice: squash, shake, hit stop, particles, sound
- [ ] Retry under 1.5 s
- [ ] 60 fps on a low-end device
- [ ] Pooling in place, atlases packed
- [ ] Credits and licences recorded
- [ ] Saves versioned, settings and mute work
- [ ] Share link tested on a real phone

## Copy-ready agent prompt

> Read the skill at the URL above. My game idea is one sentence: I will tell you. First force me to scope it to the Stage 1 limits and pick an engine from the table. Then give me the project structure, the player controller with input buffering and coyote time, the enemy and spawn logic, the difficulty ramp for 8 levels, and the juice checklist implemented as code. Flag every feature I ask for that belongs in v2.
