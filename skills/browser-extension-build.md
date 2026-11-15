---
name: browser-extension-build
description: Ship a Chrome Manifest V3 extension that passes store review - single-purpose scope, minimum permissions, content script and service worker split, messaging, storage limits, options UI, store assets and a publish checklist.
version: 1.0.0
license: MIT
tags: [frontend, chrome-extension, manifest-v3, javascript, publishing]
---

# Browser Extension Build

Most extensions are rejected for one of three reasons: too many permissions, a single-purpose rule they broke by adding a second feature, or remote code loaded from a server. All three are design decisions you make in the first hour, not bugs you fix at the end.

This skill takes you from a one-sentence purpose to a published extension with minimal permissions, a working service worker, and a store listing that survives review.

## When to use this skill

- You want to add functionality to a site you do not control.
- A workflow needs the page context: form filling, highlighting, scraping your own account data.
- An internal tool is better as a button in the browser than as a separate app.
- You are turning a bookmarklet into something installable.

Do NOT use for: reading or modifying data on sites without permission, ad injection, or anything that hides its own behaviour from the user. Also not for Firefox-only or Safari-only extensions without re-reading their manifest differences.

## Stage 1 - Define one purpose and the permissions it truly needs

1.1 Write the purpose in one sentence a reviewer would accept: "highlights prices above a threshold on the user's own shopping list page". If it needs "and", it is two extensions.

1.2 Derive permissions from the purpose, not from convenience. Every permission you request is shown to the user at install time and increases review scrutiny.

| Permission | What it grants | Request only if |
|---|---|---|
| `activeTab` | temporary access to the current tab on click | you act only after a user click |
| `scripting` | inject JS/CSS into a page | you inject programmatically |
| `storage` | `chrome.storage` | you persist anything |
| `tabs` | read tab URLs and titles | you need URLs beyond the active tab |
| `alarms` | scheduled wakeups | you poll or schedule |
| `notifications` | desktop notifications | you notify outside the popup |
| `<all_urls>` host | every site | almost never - list the sites you need |
| `webRequest` | intercept network | rarely; MV3 restricts blocking |

1.3 Prefer `activeTab` plus a user gesture over a broad host permission. It is the difference between "reads data on the current tab when you click" and "reads data on all websites".

1.4 List the exact hosts you need: `https://*.example.com/*`, not `<all_urls>`. A reviewer reads this field first.

1.5 Never request `tabs` when `activeTab` suffices; never request `<all_urls>` to make a CORS error go away - fix the fetch instead.

Gate: a permission list where each entry has a one-line justification.

## Stage 2 - Lay out the Manifest V3 structure

2.1 MV3 means no persistent background page. The service worker sleeps after 30 seconds idle and restarts on an event, so no state may live in a module variable.

2.2 Use this file layout: `manifest.json`, `src/background.js`, `src/content.js`, `src/popup.html`, `src/options.html`, `icons/16/32/48/128`.

2.3 Keep the manifest minimal and readable:

```json
{
  "manifest_version": 3,
  "name": "Price Watch",
  "version": "1.0.0",
  "description": "Highlights list items priced above your threshold.",
  "permissions": ["storage", "activeTab", "scripting"],
  "host_permissions": ["https://*.example.com/*"],
  "action": { "default_popup": "src/popup.html", "default_icon": "icons/32.png" },
  "background": { "service_worker": "src/background.js", "type": "module" },
  "content_scripts": [
    { "matches": ["https://*.example.com/*"], "js": ["src/content.js"], "run_at": "document_idle" }
  ],
  "options_page": "src/options.html",
  "icons": { "16": "icons/16.png", "48": "icons/48.png", "128": "icons/128.png" }
}
```

2.4 Bump `version` on every upload - the store rejects a duplicate version, and a rejected upload costs a day.

2.5 Keep every asset inside the package. No CDN scripts, no `eval`, no `new Function`, no remote WASM. Remote code is an automatic rejection in MV3.

2.6 Set `minimum_chrome_version` only if you truly need a newer API; it silently excludes users.

Gate: `chrome://extensions` loads the unpacked extension with zero warnings.

## Stage 3 - Split the content script from the service worker

3.1 The content script runs in the page, has DOM access, and dies on navigation. The service worker has no DOM and no persistent state.

3.2 Put DOM work in the content script and coordination in the worker. A content script that opens connections or the worker that queries the DOM are both wrong.

3.3 Make the content script idempotent: check for a marker element or a global flag before injecting UI, or an SPA navigation will render it three times.

3.4 Never mutate the page's global scope. Wrap everything in an IIFE or a module, and namespace CSS classes with a prefix.

3.5 Handle SPAs: `history.pushState` does not fire a navigation event. Patch `pushState` or poll `location.href` on a 500 ms interval inside the content script only.

3.6 Inject CSS with `insertCSS` or a namespaced `<style>`, and respect the site's `prefers-color-scheme` so your panel is readable in dark mode.

```js
// background.js - state lives in storage, never in a variable
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "getThreshold") {
    chrome.storage.sync.get({ threshold: 1000 }).then(({ threshold }) => {
      sendResponse({ threshold });
    });
    return true;             // keep the channel open for the async reply
  }
});
```

3.7 Scope the content script's CSS to a single root class (`#pw-root`) so the host page's styles cannot restyle your UI and yours cannot leak into theirs.

3.8 Use `run_at: document_idle` unless you must beat the page's own render. `document_start` on a heavy page delays the first paint and shows up as a performance regression the user blames on the site.

Gate: reloading the extension does not duplicate UI, and SPA navigation re-runs cleanly.

## Stage 4 - Get messaging right

4.1 Use `chrome.runtime.sendMessage` for popup to worker, and `chrome.tabs.sendMessage` for worker to content script. Both are async and both fail silently if nobody is listening.

4.2 Always return `true` from a listener that responds asynchronously. Forgetting it closes the channel and the reply is lost with no error.

4.3 Handle "receiving end does not exist". It means the content script is not injected on that tab, which is normal on `chrome://` pages and the store.

4.4 Version your message types (`v1:getThreshold`). Extensions update while tabs stay open, and an old content script talking to a new worker is a real crash.

| From | To | API | Failure mode |
|---|---|---|---|
| popup | worker | `runtime.sendMessage` | no listener, silent |
| popup | content | `tabs.sendMessage` | not injected, throws |
| worker | content | `tabs.sendMessage` | tab closed mid-call |
| content | worker | `runtime.sendMessage` | worker asleep, wakes it |
| page | extension | `postMessage` + content bridge | page scripts can spoof it |

4.5 Validate every message payload in the receiver. A content script runs in a hostile page, so treat its messages as untrusted input.

Gate: every message path has a test or a manual check for the failure case.

## Stage 5 - Store state within the limits

5.1 `chrome.storage.sync` is limited to 100 KB total and about 8 KB per item; `chrome.storage.local` is 10 MB by default and can be raised with `unlimitedStorage`.

5.2 Put settings in `sync` (small, user-facing) and data caches in `local`. A 200 KB cache in `sync` fails silently once it crosses the quota.

5.3 Handle quota errors: `chrome.runtime.lastError` on a failed write is the only signal, and it is easy to ignore.

5.4 Store nothing you would not want read out loud: no tokens in `sync`, no full page content, no personal data beyond what the feature needs.

5.5 Version your stored schema (`{v:1, ...}`) and migrate on read. Extensions live for years and users update mid-state.

Gate: a write above the quota produces a handled error, not a silent failure.

## Stage 6 - Build the popup and options UI

6.1 The popup is 400x600 at most and closes on any outside click. Anything longer than one screen belongs in the options page.

6.2 Show state the user can act on: current status, the last action, and one primary button. No dashboards in a popup.

6.3 The options page is a full page - use it for settings, thresholds, host lists and export/import of configuration.

6.4 Add a keyboard shortcut in `commands` and a context menu entry where it fits the workflow; power users find both.

6.5 Never auto-run on install. Open a welcome page that explains what the extension does and asks for any optional permission separately.

6.6 Make every permission request contextual: a button that says "enable on this site" using `chrome.permissions.request`, not a blanket install-time ask.

6.7 Keep the popup under 100 KB including icons; a popup that takes 300 ms to appear feels broken.

6.8 Persist the popup's last state so reopening it does not reset the form the user was half-way through.

Gate: a first-run user understands what it does without reading documentation.

## Stage 7 - Test and debug

7.1 Reload the extension from `chrome://extensions` after every change; content scripts need a page reload too.

7.2 Inspect the service worker from `chrome://extensions` - it has its own DevTools, and its console is not the page console.

7.3 Test the four states that break extensions: worker asleep, tab closed mid-request, extension updated with tabs open, and user offline.

7.4 Test on a fresh Chrome profile with no other extensions, and on a profile with an ad blocker that may block your fetch.

7.5 Add a debug flag that logs to a namespaced console (`[pw]`) so support can ask for logs without a build change.

7.6 Keep a `test-plan.md` with 10 manual checks; automated end-to-end for extensions is possible with Playwright but slow to maintain.

7.7 Test with the service worker stopped from `chrome://extensions` (the "service worker" link has a stop control) - this is the state your users hit every 30 seconds.

7.8 Test an update: load version 1.0, keep a tab open, reload the unpacked extension as 1.0.1, and confirm the open tab still works.

Gate: the 10-item manual test plan passes on a clean profile.

## Stage 8 - Prepare the store listing

8.1 Assets the Chrome Web Store requires: 128x128 icon, at least one 1280x800 or 640x400 screenshot, a 440x280 small promo tile, and a 140-character summary.

8.2 Write the description for the reviewer first: what it does, on which sites, and what data it touches. Ambiguity is what triggers a manual review.

8.3 Host a privacy policy at a public URL even if you collect nothing. Say plainly: "no data leaves the browser" or exactly what is sent and where.

8.4 Fill the data-use disclosure honestly. Saying "no data collected" while shipping analytics is the fastest route to removal.

8.5 Use the single-purpose field to state the one thing the extension does, in the same words as the manifest description.

| Asset | Spec | Notes |
|---|---|---|
| Icon | 128x128 PNG | must be legible at 16 px |
| Screenshot | 1280x800 or 640x400 | show the real UI, no mockups |
| Promo tile | 440x280 | optional but improves listing |
| Summary | 140 characters | the first thing a reviewer reads |
| Privacy policy | public URL | required if you handle any data |

Gate: every asset uploaded at the right dimensions, policy URL live.

## Stage 9 - Survive review

9.1 The three rejection causes to design out: excessive permissions, remote code, and a second purpose bolted on.

9.2 Remove every unused permission before submitting. A permission you plan to use later is a rejection today.

9.3 Explain unusual behaviour in the reviewer notes field: "injects a highlight span into list items on example.com when the user clicks the toolbar icon".

9.4 Keep a demo account or test instructions if the extension needs a login. Reviewers cannot evaluate what they cannot reach.

9.5 Expect 1-7 days for a first review and 1-3 for an update (estimate). Do not plan a launch on the same day.

9.6 If rejected, fix the named cause and resubmit with a note describing the fix. Arguing with the rejection costs more time than the fix.

Gate: reviewer notes written, unused permissions removed, no remote code.

## Stage 10 - Publish and maintain

10.1 Upload the zip, fill the listing, set visibility, and pay the one-time developer registration fee if this is a new account.

10.2 Roll out to 10% first when the store offers staged rollout, and watch the crash rate and reviews for a week.

10.3 Keep the version history in `CHANGELOG.md`; users read it when something changes under them.

10.4 Watch the API deprecations: MV2 is gone, and MV3 itself keeps tightening. Budget one maintenance release a quarter.

10.5 Answer reviews for the first month. A one-line reply to a bug report often prevents a 1-star rating from sticking.

10.6 Keep a crash and error channel: log uncaught errors to your own endpoint only if your privacy policy says so, otherwise rely on user reports and reviews.

10.7 Watch the review rating weekly for the first quarter. A 3.0 average is usually one broken site integration, not a bad product.

Gate: published, staged rollout observed for a week, changelog current.

## Worked example

An extension that flags invoices above a threshold on a B2B portal, built in 4 days.

| Decision | Choice | Why |
|---|---|---|
| Scope | one site, one action | single purpose, passes review |
| Permissions | `storage`, `activeTab`, `scripting` | no `tabs`, no `<all_urls>` |
| Host permission | `https://*.portal.example.com/*` | exact hosts, not all sites |
| Content script | injects one namespaced badge | idempotent on SPA nav |
| Worker | reads threshold from `sync` | stateless, survives sleep |
| Storage | settings in `sync`, cache in `local` | stays under 100 KB |
| Review | approved first attempt | permissions justified in notes |

The first version asked for `<all_urls>` and `tabs` and was rejected in 36 hours. Removing both, and scoping to the one portal, got it approved without a single code change to the feature itself.

## Second worked example - an internal tool for one team

A support team needs to paste a customer id from the CRM into the ticket tool.

| Decision | Choice | Why |
|---|---|---|
| Distribution | unlisted, link-only | no public review, no store assets |
| Permissions | `storage`, `activeTab`, `scripting` | clicks only, nothing automatic |
| Host permission | none | `activeTab` covers the click |
| Storage | last 20 ids in `local` | 4 KB, no quota risk |
| UI | popup with one button and a history list | under one screen |
| Update path | `chrome://extensions` developer mode | no store review lag |

An unlisted extension still goes through review, but it is not searchable and needs no promo assets. For 8 internal users that is the right trade.

## Quality checklist

- [ ] Purpose is one sentence with no "and"
- [ ] Every permission has a one-line justification
- [ ] Host permissions list exact hosts, not `<all_urls>`
- [ ] No remote code, no `eval`, no `new Function`
- [ ] State in `chrome.storage`, never in a module variable
- [ ] Async message listeners return `true`
- [ ] "Receiving end does not exist" handled
- [ ] Content script idempotent on SPA navigation
- [ ] CSS namespaced, dark mode respected
- [ ] Sync storage under 100 KB, quota errors handled
- [ ] Stored schema versioned with a migration path
- [ ] First run opens a welcome page, not an auto-run
- [ ] Manual test plan covers worker sleep and tab close
- [ ] Screenshots and promo tile at exact dimensions
- [ ] Privacy policy live at a public URL
- [ ] Reviewer notes explain the injection behaviour
- [ ] Staged rollout observed for a week

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Rejected for "excessive permissions" | `<all_urls>` and `tabs` requested for convenience | Scope to exact hosts, use `activeTab` |
| Rejected for remote code | A script or WASM loaded from a CDN | Bundle it in the package |
| Extension stops working after 30 s | State kept in a service worker variable | Move state to `chrome.storage` |
| Popup button does nothing | Async listener did not return `true` | Return `true` from the listener |
| Badge renders three times | Content script re-injected on SPA navigation | Guard with a marker element |
| Settings silently stop saving | `sync` quota exceeded at 100 KB | Move cache to `local`, handle `lastError` |
| Works for you, fails for a user | Another extension blocked your fetch | Test on a profile with an ad blocker |
| Update breaks open tabs | Old content script talking to a new worker | Version message types and handle mismatch |

## Copy-ready agent prompt

> Read the skill at the URL above and help me build a Chrome extension. Ask me: the one thing it does, which sites it works on, and what it must store. Then give me the minimal `manifest.json` with every permission justified and exact host permissions, the content script with an idempotency guard, the service worker with storage-backed state and message handlers that return `true`, and the popup and options pages. Then the storage schema with limits and migration, the 10-item manual test plan, the store listing assets at the right dimensions, the privacy policy text and the reviewer notes. Tell me which permission I could remove and what would break.
