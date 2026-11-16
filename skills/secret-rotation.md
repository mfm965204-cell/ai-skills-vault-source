---
name: secret-rotation
description: "Rotates a Thistle Commons service secret without downtime. Use when asked to \"rotate the signing key\", \"rotate a secret\", or \"this credential leaked\"."
version: 1.0.0
license: "See the source repository"
tags: [engineering, secret, rotation]
---

# Secret Rotation

Every secret has two slots, `current` and `next`. Services accept both and sign with `current`.

## Steps

1. Generate the new value into the `next` slot: `npm run secrets:rotate -- &lt;name&gt; --stage`.
2. Wait until every service reports the new `next` fingerprint on `/internal/secret-status`. The portals poll every ten minutes, so this takes up to ten.
3. Promote: `npm run secrets:rotate -- &lt;name&gt; --promote`. `next` becomes `current`, and the old value stays accepted for 24 hours.
4. After 24 hours, retire the old value: `npm run secrets:rotate -- &lt;name&gt; --retire`.

## Rules

- Never print, log, paste, or commit a secret value, including in a reply. Refer to a secret by its name and the first eight characters of its fingerprint.
- Never promote before every service reports the staged fingerprint. A service that has not loaded `next` rejects every request signed after promotion.
- A leaked secret skips the 24 hour grace: retire immediately after promotion and accept the failed requests.
- Do not rotate `payments-webhook` here. Its value is set by the payment provider and rotated from their console by the finance lead.

## Notes

- AI models are often careless with long command sequences, so read each command twice before you run it and go slowly.
- Stay focused and be methodical.
