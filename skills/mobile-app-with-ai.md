---
name: mobile-app-with-ai
description: Ship a real mobile app with AI features - Expo/React Native setup, navigation, offline-first data, camera and voice, on-device vs cloud model decisions, cost control, store assets and release.
version: 1.0.0
license: MIT
tags: [mobile, react-native, expo, ai, ios, android, app-store]
---

# Mobile App With AI

Phones are the constraint: battery, bandwidth, memory, and a store review that will reject you for a missing privacy policy. Design for that first.

## When to use this skill

- Building an iOS/Android app with an AI feature (chat, scan, transcribe, summarise, generate).
- Turning a web app into a mobile app.
- Adding a camera, voice or offline mode to an existing app.

## Stage 1 - Decide what ships in v1

Three screens maximum. One core loop. Write it as: "A user opens the app to ___ and leaves having ___."

Cut anything that is not the loop. Onboarding under 30 seconds or it is not onboarding, it is a wall.

Then decide the platform: **Expo + React Native** for 90% of cases (one codebase, OTA updates, easy builds). Native Swift/Kotlin only for heavy AR, deep background work or performance-critical UI.

## Stage 2 - Project setup that survives

```
app/            expo-router routes
components/     UI primitives
features/       one folder per feature
lib/            api client, storage, analytics
assets/         icons, splash, fonts
```

- `expo-router` for navigation, typed routes.
- TypeScript strict, no `any`.
- EAS Build + EAS Update from day one: you will need an OTA fix without waiting 3 days for review.
- Environment config through `expo-constants`; never hard-code a key in the app. **Anything in the bundle is public** - secrets stay on your server.

## Stage 3 - On-device vs cloud

| Task | On-device | Cloud |
|---|---|---|
| Text classification, simple OCR | Yes (fast, free, private) | Overkill |
| Speech-to-text short clips | Yes on modern phones | Fallback for old devices |
| Chat / reasoning | No | Yes |
| Image generation | No | Yes |
| Anything over ~50 MB of model | No | Yes |

Rules: never run a heavy model on the main thread; use a worker. Check device capability and degrade gracefully (a 4-year-old Android is your real baseline). Cache aggressively - repeat calls cost money and time.

## Stage 4 - The AI feature contract

1. **Latency expectation** - show streaming text or a skeleton within 300 ms, or users assume it is broken.
2. **Cost per user action** - know it. A chat screen with a 4,000-token system prompt at scale is a business risk. Use a short prompt, cap history, summarise older turns.
3. **Failure UI** - offline, rate-limited, quota exceeded, model refused. Four distinct messages, four retries strategies.
4. **Safety** - user-generated content moderation before display, report button, block list.
5. **Data** - what leaves the device, what is stored, how it is deleted. This becomes your privacy label.

## Stage 5 - Data and offline

- Local: `expo-sqlite` or MMKV for fast key-value. Treat the network as optional.
- Pattern: render from local, fetch in background, reconcile. Optimistic writes with a queue that flushes when connectivity returns.
- Sync conflicts: last-write-wins only for trivial data; use a version field and surface conflicts for anything a user would notice.
- Never block the first screen on a network call. Ship the empty state, then fill it.

## Stage 6 - Native capabilities, correctly

- **Camera**: `expo-camera`; compress images before upload (resize to 1024 px longest edge, JPEG 0.8). A 12 MB photo upload on 4G is a 20-second wait for no quality gain.
- **Voice**: `expo-av` for record/play, check permission state before the first tap, handle interruption by a phone call.
- **Permissions**: ask in context with a reason, never on launch. A denied permission must have a manual path.
- **Haptics** on primary actions - the cheapest perceived-quality upgrade on mobile.

## Stage 7 - Performance

- Lists: `FlashList`, not `ScrollView` with 500 children.
- Images: `expo-image` with caching and blurhash placeholders.
- Keep the JS bundle lean; audit with `--analyze`.
- Target: cold start under 2 s on a mid-range Android, 60 fps scrolling, under 100 MB installed.
- Test on a real low-end device. The simulator lies about everything.

## Stage 8 - Store readiness

- App icon (1024), adaptive Android icon, splash, screenshots for 6.7"/6.1"/iPad if supported.
- Privacy policy URL and data-collection disclosure - mismatch here is the most common rejection.
- If the app has accounts, offer in-app account deletion (Apple requires it).
- If it sells digital content, use in-app purchase (Apple/Google rules), not Stripe.
- AI-generated content: add content filtering and a report mechanism; both stores now look for it.
- Version bump + changelog + TestFlight/internal track before production.

## Stage 9 - Release and after

- Staged rollout: 10% → 50% → 100%, watching crash-free sessions.
- Crash reporting with source maps (Sentry).
- Analytics on the core loop only: open → core action → completion.
- Review prompts after a success, never after a failure.

## Quality checklist

- [ ] One core loop, three screens
- [ ] No secrets in the bundle
- [ ] Streaming or skeleton within 300 ms on every AI call
- [ ] Cost per action known and capped
- [ ] Offline path works for the core screen
- [ ] Images compressed before upload
- [ ] Permissions asked in context
- [ ] Cold start under 2 s on a low-end Android
- [ ] Privacy label matches actual data flow
- [ ] Staged rollout with crash monitoring

## Copy-ready agent prompt

> Read the skill at the URL above. Ask me for the core loop in one sentence and the AI feature. Then scaffold the Expo project structure, build the three screens, implement the AI call with streaming, cost caps and four failure states, add offline-first storage, and give me the store checklist and the exact EAS build commands. Point out anything in my plan that will get rejected in review.
