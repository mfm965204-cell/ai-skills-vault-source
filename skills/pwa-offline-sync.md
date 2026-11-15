---
name: pwa-offline-sync
description: Make a web app work on a bad connection - cache shell and data, queue writes in IndexedDB, and resolve conflicts without losing a user's work.
version: 1.0.0
license: MIT
tags: [frontend, pwa, offline, service-worker, indexeddb]
---

# PWA Offline Sync

A field app that shows a spinner on a 2G connection is a field app nobody uses. The work happens where the signal is bad: a warehouse, a bus, a basement, a village with one tower. Users type the data, the request fails, and the work is gone.

This skill makes the app usable offline and honest about it: a cached shell so it opens, cached reads so the last known data is visible, a write queue in IndexedDB that survives a reload, and a conflict rule chosen per entity rather than a generic "last write wins". It ends with a test that simulates offline, a 20-write queue and a mid-sync reload.

The rule that keeps this from becoming a data-loss bug: never show a write as saved until it is queued, and never let a queued write disappear silently.

## When to use this skill

- Users report lost work when the connection drops mid-form.
- The app needs to open and show yesterday's data with no network.
- You have a service worker that caches the shell but nothing else works offline.
- Writes fail with a generic error and the user retypes everything.
- **Do NOT use for:** native app offline storage, real-time collaboration, or backend queue design - this covers the client-side offline layer and its contract with the API.

## Stage 1 - Decide what offline means for this app

"Offline support" is not one feature. Decide the three levels before writing a service worker, because each level changes the API and the UI.

1.1 Level one: shell only - the app opens and shows an offline page. Cheap, and often enough for a marketing site.

1.2 Level two: read cache - the last fetched data is visible offline, marked as stale with a timestamp.

1.3 Level three: write queue - actions are accepted offline, queued, and replayed when the connection returns.

1.4 Write which level each screen needs, because a read-only report screen does not need a write queue.

1.5 Decide the staleness limit: how old may cached data be before the app refuses to show it as current.

1.6 Decide the user-visible truth: what the UI says when data is stale, queued or failed.

| Screen | Level | Staleness limit | Offline behaviour |
|---|---|---|---|
| Dashboard | Read cache | 24 hours | Show with "last updated" banner |
| Stock list | Read cache | 1 hour | Show, disable actions requiring live stock |
| Delivery entry | Write queue | - | Accept, queue, show pending badge |
| Payments | Online only | - | Block with a clear message |

Gate: every screen is assigned a level, a staleness limit and an offline behaviour.

## Stage 2 - Register the service worker without breaking updates

A service worker that never updates is worse than none: users stay on a cached build for weeks. Control the update path from the start.

2.1 Register the worker at the root scope so it can control the whole app.

2.2 Use a versioned cache name derived from the build hash, so each deploy gets a fresh cache.

2.3 Delete old caches on `activate`, or the device fills up over months.

2.4 Call `skipWaiting` only after the user accepts an update, so a reload does not interrupt a form.

2.5 Show an "update available" prompt and reload on the user's action, not automatically mid-task.

2.6 Keep the worker file small; it is downloaded and parsed on every check.

```js
const CACHE = `app-${__BUILD_HASH__}`;
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/", "/offline.html"])));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
});
self.addEventListener("message", (e) => {
  if (e.data === "SKIP_WAITING") self.skipWaiting();
});
```

Gate: a new deploy produces a new cache name, old caches are deleted, and the update prompt appears.

## Stage 3 - Cache the shell and the static assets precisely

Cache too much and the user gets stale code; cache too little and the app does not open. Be explicit about which strategy applies to which path.

3.1 Cache-first for hashed static assets - JS, CSS, fonts, icons - because their names change on every build.

3.2 Network-first with a cache fallback for HTML navigation, so a deploy is picked up on the next load.

3.3 Stale-while-revalidate for read APIs the screen can tolerate being one request old.

3.4 Never cache authenticated POST responses, payment pages or anything with a `Cache-Control: no-store`.

3.5 Exclude analytics and third-party beacons from the cache; they will fail offline anyway.

3.6 Set a cache size ceiling and evict the oldest entries when it is exceeded.

```js
self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  if (new URL(request.url).pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(request, copy));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }
  event.respondWith(caches.match(request).then((hit) => hit || fetch(request)));
});
```

Gate: the app opens with the network disabled, and no authenticated response is present in the cache.

## Stage 4 - Queue writes in IndexedDB with an idempotency key

The queue is the heart of the feature. It must survive a reload, a crash and a mid-sync failure without duplicating work.

4.1 Create one object store for the queue, keyed by a client-generated `opId` (a UUID).

4.2 Store the operation type, the payload, a client timestamp, an idempotency key and a retry count.

4.3 Generate the idempotency key on the client and send it with every replay, so the server can dedupe a double send.

4.4 Write to the queue and to the local view in one transaction, so the UI never shows a save the queue does not have.

4.5 Cap the retry count at 5 and mark the item `failed` after that, visible to the user.

4.6 Keep the queue small: replay and delete on success, never accumulate a history in the same store.

```ts
async function enqueue(op: Op) {
  const db = await openDB("offline", 1);
  const tx = db.transaction(["queue", "view"], "readwrite");
  await tx.objectStore("queue").put({
    ...op,
    opId: crypto.randomUUID(),
    idemKey: crypto.randomUUID(),
    queuedAt: Date.now(),
    retries: 0,
    state: "pending",
  });
  await tx.objectStore("view").put(applyLocally(op));
  await tx.done;
}
```

Gate: a queued write survives a page reload, and the same `idemKey` is sent on every retry.

## Stage 5 - Replay the queue in order, with backoff

Replaying in parallel is how a queue creates duplicate records and out-of-order state. Replay sequentially, oldest first.

5.1 Replay on three triggers: page load, the `online` event, and a periodic check every 60 seconds while the app is open.

5.2 Send one operation at a time and wait for the response before the next.

5.3 Back off on 5xx and network errors at 2, 4, 8, 16 and 32 seconds, and stop after the retry cap.

5.4 On a 4xx that is not 408 or 429, mark the item `failed` and surface it - do not retry a validation error forever.

5.5 On success, delete the queue item and reconcile the local view with the server response.

5.6 Record the last successful sync time and show it in the UI.

Gate: a 20-item queue replays in order, and a validation error stops retrying and becomes visible.

## Stage 6 - Choose a conflict rule per entity

Conflicts are a product decision. "Last write wins" is correct for a note and catastrophic for stock levels or payments.

6.1 For append-only records - logs, readings, visits - accept both and merge; conflicts do not exist.

6.2 For editable records with a single owner, last-write-wins by server timestamp is acceptable if the UI warns on overwrite.

6.3 For counters and stock, use server-side deltas - send "+3", not "13" - so concurrent writes compose instead of overwrite.

6.4 For records needing review, send the conflicting version to a review queue and tell the user.

6.5 Include the base version or `updatedAt` the client edited, so the server can detect a stale write.

6.6 Write the rule per entity in a table and show it in the UI where it applies.

| Entity | Conflict rule | Why |
|---|---|---|
| Delivery note | Append-only | Two notes are two facts |
| Customer phone number | Last write wins, warn on overwrite | Single owner, low risk |
| Stock quantity | Server-side delta | Concurrent decrements must compose |
| Invoice amount | Review queue | Money needs a human decision |

Gate: every synced entity has a named conflict rule, and counter entities send deltas rather than absolutes.

## Stage 7 - Tell the user the truth about their data

Offline UX fails when the app lies. Three states must be visible at all times: online or offline, synced or pending, fresh or stale.

7.1 Show a persistent connection indicator, not a toast that disappears.

7.2 Badge queued records with a pending state and the queued timestamp.

7.3 Show the age of cached data wherever stale data is displayed: "as of 09:14 today".

7.4 On a failed item, show the reason and a retry action, never a silent drop.

7.5 Disable actions that genuinely need the network, and say why, instead of failing after the user finishes typing.

7.6 Never show a success toast for a write that is only queued; say "saved, will sync".

Gate: offline, pending and stale states are all visible without opening a menu.

## Stage 8 - Test offline, mid-sync and reload

Offline bugs appear in transitions, not in steady state. Test the three transitions that break real apps.

8.1 Load the app, go offline, submit 20 writes, and confirm all 20 appear in the queue and the UI.

8.2 Reload while offline and confirm the queue and the local view survive.

8.3 Go online and kill the connection after the 5th replay; confirm replay resumes from item 6 without duplicates.

8.4 Send the same operation twice with the same idempotency key and confirm the server creates one record.

8.5 Test on a real Android phone with airplane mode toggled, not only with the devtools checkbox.

8.6 Test a slow 3G profile with 400 ms latency and confirm the pending state appears rather than a hang.

Gate: all five scenarios pass, and no duplicate record is created by a double replay.

## Stage 9 - Monitor sync health in production

The queue is invisible until it breaks. Instrument it, or the first report will be a user with 300 unsynced records.

9.1 Log queue length, oldest pending age and failure count per session to your analytics.

9.2 Alert when the oldest pending item exceeds 24 hours for more than a small percentage of users.

9.3 Track the retry distribution; a rising retry count means the API changed or the network assumption is wrong.

9.4 Version the queue schema and write a migration, because a format change with a full queue loses data.

9.5 Give support a way to inspect and re-trigger a user's queue without asking them to clear app data.

9.6 Review the conflict-rule table each quarter as entities are added.

Gate: queue length and oldest-pending age are monitored, and a queue schema migration path exists.

## Quality checklist

- [ ] Every screen has an assigned offline level and a staleness limit.
- [ ] The cache name includes the build hash.
- [ ] Old caches are deleted on activate.
- [ ] Updates are applied only after the user accepts.
- [ ] Hashed assets are cache-first and HTML is network-first.
- [ ] No authenticated POST response is cached.
- [ ] The write queue lives in IndexedDB and survives a reload.
- [ ] Every queued write carries a client-generated idempotency key.
- [ ] The queue and the local view are written in one transaction.
- [ ] Replay is sequential and oldest-first.
- [ ] Retries back off and stop at the cap.
- [ ] A non-retryable 4xx marks the item failed and visible.
- [ ] Each synced entity has a named conflict rule.
- [ ] Counter entities send deltas, not absolutes.
- [ ] Queue length and oldest pending age are monitored.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Same record created twice | Replay retried without an idempotency key | Generate the key on the client and send it on every retry |
| Queue empties after a reload | Queue held in memory, not IndexedDB | Persist the queue in an object store and write it transactionally |
| Users stuck on an old build | Cache name is static and never invalidated | Derive the cache name from the build hash and delete old caches |
| Stock goes negative offline | Client sent absolute quantities | Send deltas and let the server apply them |
| App shows data as current when it is not | No staleness limit or timestamp in the UI | Show the data's age wherever cached data renders |
| Failed writes vanish silently | Retry loop stopped without a state change | Mark the item failed, show the reason and offer retry |

## Copy-ready agent prompt

> Read the skill at the URL above and make my web app work offline. Ask me for the screens, the entities I write to and the API contract, then assign an offline level and staleness limit per screen, give me the service worker with a build-hashed cache and an update prompt, and the IndexedDB write queue with idempotency keys and sequential replay. Produce the conflict-rule table per entity and the three offline states in the UI. Finish with the five test scenarios including a mid-sync kill and a duplicate send. Do not cache any authenticated response.
