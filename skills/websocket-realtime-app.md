---
name: websocket-realtime-app
description: Ship realtime features that survive flaky mobile networks - transport choice, message envelope, authenticated connect, presence and heartbeat, reconnect with replay, Redis scale-out, backpressure limits and a 1,000-connection load test.
version: 1.0.0
license: MIT
tags: [engineering, websockets, realtime, nodejs, redis, scaling]
---

# WebSocket Realtime App

Polling every 3 seconds looks fine on a laptop and falls apart on a 3G phone in a lift. Realtime is not "open a socket" - it is a protocol with sequence numbers, a reconnect path, and a limit that stops one slow client from eating the server.

This skill takes you from a socket that works on localhost to one that holds 1,000 concurrent connections through a proxy, a deploy and a network switch, with presence that does not lie.

## When to use this skill

- Chat, live cursors, collaborative editing, order tracking or a live dashboard.
- Notifications that must arrive in under a second.
- Any feature where the user asks "why do I have to refresh?".

Do NOT use for: one-off status polls (a 10-second fetch is simpler and cheaper), file transfer (use object storage and a URL), or server-to-server messaging (use a queue).

## Stage 1 - Pick the transport before the framework

1.1 Count the direction of traffic. Server pushing only means Server-Sent Events; both directions means WebSocket; a few updates an hour means polling.

| Need | Transport | Why |
|---|---|---|
| Server push, no client messages | SSE | Plain HTTP, auto-reconnect built in, works through every proxy |
| Chat, cursors, presence | WebSocket | Full duplex, low per-message overhead |
| Updates every 30 s or slower | Polling | No infra, cacheable, easy to debug |
| Binary media | WebSocket or WebRTC | WebRTC only if latency under 300 ms matters |
| One-way fan-out to 100k clients | SSE behind a CDN | CDN holds the connections |

1.2 Assume a proxy in front of you. Indian enterprise networks and many mobile carriers buffer or break long-lived connections; SSE over HTTP/1.1 gets stuck behind a 6-connection browser limit unless you are on HTTP/2.

1.3 Decide the reconnect budget now: how long may a client be disconnected before the UI shows "offline"? 15-30 seconds is right for chat; 5 seconds for a live auction.

1.4 Write the fallback: if WebSocket fails twice, fall back to polling every 10 seconds. Every realtime app needs one, and it is 30 lines.

Gate: transport chosen with a one-line reason, fallback path named.

## Stage 2 - Design the message envelope

2.1 One envelope for every message, in both directions. Ad-hoc shapes are what make realtime code unmaintainable.

```json
{"v":1,"type":"message.new","id":"01HQ8Z3K","seq":4127,"ts":1763200000123,
 "room":"order-2291","data":{"text":"packed","by":"u_812"}}
```

2.2 `seq` is a per-room monotonic counter. It is how a client detects a gap after reconnect, and without it you will ship duplicate messages for a year.

2.3 `type` is namespaced (`room.join`, `message.new`, `presence.update`) so a client can route with a switch and the server can validate against a whitelist.

2.4 Version the envelope (`v`) from day one. A client on a cached old bundle will still connect, and the server must know how to talk to it.

2.5 Keep `data` small. Send an id and let the client fetch the object, or send the 6 fields the UI needs - never the whole ORM row with internal columns.

2.6 Cap message size at 16 KB. Anything larger goes through an HTTP upload with a socket notification afterwards.

2.7 Reserve a `type` for errors: `error` with a code and a human message. The client needs one shape for "your message was rejected", and it is not a silent close.

2.8 Document the envelope in `protocol.md` with one example per type. Two clients and a server will diverge within a month without it.

Gate: envelope documented, and every message in the codebase uses it.

## Stage 3 - Stand up the server

3.1 Use a maintained server library: `ws` for Node, `uWebSockets.js` when you need 10k+ connections per process, or FastAPI's WebSocket support in Python.

3.2 Keep the socket handler thin: parse, authenticate once, then hand off to the same functions your HTTP API uses. Business logic duplicated in the socket layer is the classic bug.

3.3 Send a `hello` frame on connect with the server version and the current `seq` for each room the client is in. The client reconciles immediately instead of waiting for the next event.

3.4 Never trust a client-supplied `seq`, `user_id` or `room`. Take identity from the token and room membership from your own store.

```js
import { WebSocketServer } from "ws";
const wss = new WebSocketServer({ noServer: true, maxPayload: 16 * 1024 });

server.on("upgrade", (req, socket, head) => {
  const user = verifyToken(new URL(req.url, "http://x").searchParams.get("t"));
  if (!user) return socket.destroy();          // 401 before any frame is read
  wss.handleUpgrade(req, socket, head, (ws) => {
    ws.user = user;
    ws.isAlive = true;
    ws.on("pong", () => { ws.isAlive = true; });
    wss.emit("connection", ws, req);
  });
});
```

3.5 Turn on compression only for text above 1 KB. Per-message deflate costs CPU per message and hurts latency on small frames.

Gate: a client connects, receives `hello`, and an unauthenticated connect is refused before a frame is parsed.

## Stage 4 - Authenticate the connection

4.1 Browsers cannot set headers on a WebSocket handshake, so the token goes in the query string or a subprotocol. Prefer a short-lived ticket: `POST /ws-ticket` returns a 30-second single-use token.

4.2 Never put a long-lived JWT in the query string - it lands in proxy logs and referrers.

4.3 Re-authenticate on a timer: at token expiry the server sends `auth.expiring`, the client fetches a new ticket and reconnects. Silent expiry is why users get logged out mid-session.

4.4 Authorise per room on join, not on connect. A user may read room A and not room B, and the socket does not change that.

4.5 Close with a code: 4001 for auth failure, 4008 for rate limit, 1012 for server restart. The client behaves differently for each and needs to know which.

Gate: expired ticket rejected, room join without permission rejected, close codes mapped in the client.

## Stage 5 - Presence and heartbeat

5.1 Heartbeat with a ping every 25 seconds and a 30-second pong deadline. Mobile NATs drop idle connections silently; without a heartbeat you keep thousands of dead sockets.

5.2 Presence is not the socket. Track `user_id -> connection_count` in Redis and emit `presence.online` when the count goes 0 to 1, `offline` when it goes 1 to 0. Two tabs are one online user.

5.3 Debounce offline by 10 seconds. A phone switching from Wi-Fi to 4G drops and reconnects in 2 seconds, and a presence list that flickers is worse than none.

5.4 Store `last_seen` at write time, not at read time, and render "online" only if the heartbeat is under 60 seconds old.

| Signal | Interval | Action |
|---|---|---|
| Server ping | 25 s | No pong in 30 s, terminate |
| Client ping | 20 s | Reconnect after 2 missed |
| Presence debounce | 10 s | Prevents Wi-Fi to 4G flicker |
| Typing indicator | 3 s throttle | Never per keystroke |
| Stale presence | 60 s | Show offline |

5.5 Do not broadcast presence to every room member by default. A 500-person room with presence broadcast is 500 messages per join; send presence only for rooms under 50 members or on explicit subscribe.

5.6 Store presence in Redis with a 90-second TTL and refresh it on each heartbeat, so a crashed process leaves no ghost users behind.

Gate: killing a client's network shows offline within 60 seconds, not immediately and not never.

## Stage 6 - Reconnect with replay

6.1 Reconnect with exponential backoff and jitter: 1 s, 2 s, 4 s, 8 s, capped at 30 s, each with plus or minus 20% jitter so a server restart does not bring 10,000 clients back in the same second.

6.2 On reconnect, send the last `seq` per room. The server replies with everything after it, up to a 30-second buffer; if the gap is larger, it sends a `resync` flag and the client refetches the room over HTTP.

6.3 Buffer the client's own outbound messages while offline, with an idempotency key, and flush on reconnect. Server-side dedupe on that key prevents double sends.

6.4 Show connection state in the UI: connected, reconnecting, offline. Users forgive a reconnect they can see and rage at one they cannot.

6.5 Cap the replay buffer at 500 messages per room. Beyond that, HTTP resync is cheaper and more correct.

Gate: a 20-second network drop produces zero duplicates and zero missing messages.

## Stage 7 - Scale past one process

7.1 Two Node processes mean a user on process A cannot see a message published on process B. Fix it with Redis pub/sub or NATS: every process subscribes to the rooms it holds.

7.2 Subscribe per room, not per user, and unsubscribe when the last local connection to that room closes. A process holding 5,000 room subscriptions pays for all of them.

7.3 Do not use Redis pub/sub for history. It is fire-and-forget; a process that restarts mid-message loses it. Persist messages, publish notifications.

7.4 Sticky sessions are not required for pure WebSocket traffic, but the upgrade request must not be load-balanced to a different process than the one that answers it - terminate at one layer.

7.5 Plan the deploy: on shutdown send close code 1012, wait 5 seconds for clients to leave, then exit. Clients reconnect to another instance instead of seeing a dead socket.

| Connections per process | Memory | Notes |
|---|---|---|
| 1,000 | 150-300 MB | `ws` on a 1 GB instance |
| 5,000 | 600 MB-1 GB | Tune GC, cap payload |
| 10,000+ | 2 GB+ | uWebSockets.js or a dedicated box |

7.6 Keep the fan-out payload small: publish `{room, seq}` to Redis and let each process read the message body from its own cache, rather than publishing the full body N times.

7.7 Version the channel name (`v1:room:<id>`) so a protocol change can run both versions during a rolling deploy.

Gate: two instances, a message sent to one reaches a client on the other.

## Stage 8 - Backpressure and limits

8.1 A slow client fills the socket buffer. Check `ws.bufferedAmount` before sending and drop or disconnect above 1 MB - one stuck phone must not grow your heap.

8.2 Rate limit per connection: 20 messages per 10 seconds for chat, 5 per second for cursors. Exceed it and close with 4008 rather than silently dropping.

8.3 Cap rooms per connection at 20 and connections per user at 5. Both are cheap to enforce and stop accidental abuse.

8.4 Validate every frame: type whitelist, payload schema, 16 KB max. A single unvalidated frame type is a remote crash.

8.5 Batch high-frequency updates. Cursor moves at 60 fps go out as one frame every 50 ms, not 60 frames a second.

8.6 Set a per-IP connection cap of 20 to blunt a naive script, and a per-user cap of 5 to stop one account opening sockets in a loop.

8.7 Close rather than drop when a limit is hit, with a code the client can show: 4008 rate limit, 4009 too many connections.

| Limit | Value | Close code |
|---|---|---|
| Frame size | 16 KB | 1009 |
| Buffered outbound | 1 MB | 4008 |
| Messages per 10 s | 20 | 4008 |
| Rooms per connection | 20 | 4009 |
| Connections per user | 5 | 4009 |
| Connections per IP | 20 | 4009 |

Gate: a client that stops reading is disconnected within 30 seconds, and the server's memory stays flat.

## Stage 9 - Observability

9.1 Export four metrics: open connections, messages per second, p95 send latency, and reconnects per minute. A reconnect spike is the first sign of a proxy timeout or a deploy loop.

9.2 Log connect, disconnect and close code with user id and duration. The close-code histogram tells you whether clients leave cleanly or are being cut.

9.3 Alert on: connections dropping 50% in a minute, p95 latency above 500 ms, or error close codes above 5% of disconnects.

9.4 Trace one message end to end with a correlation id in the envelope, so "the message never arrived" becomes a query instead of an argument.

9.5 Sample slow-message traces at 1 in 100, not all of them; full tracing on a socket server adds more overhead than the feature it measures.

9.6 Export connection count per room. One room holding 80% of connections is a hot room and the next thing that breaks.

Gate: a dashboard with the four metrics and three alerts, all owned by a named person.

## Stage 10 - Load test before launch

10.1 Test with a real client library, not `ab`. Open 1,000 connections, join 50 rooms, send 1 message per second per 20 connections.

10.2 Measure: time to accept 1,000 connections, p95 latency, memory per connection, and behaviour when 10% of clients stop reading.

10.3 Run the test through your actual proxy and TLS terminator. A test on localhost proves nothing about nginx's `proxy_read_timeout`.

10.4 Check the proxy timeouts: nginx defaults to 60 seconds for `proxy_read_timeout` and will cut an idle socket. Set 75 seconds with a 25-second heartbeat, so the heartbeat always wins.

10.5 Load test the deploy too: rolling restart with 1,000 clients connected, and count how many reconnect cleanly.

| Test | Pass condition |
|---|---|
| 1,000 connects | under 10 s |
| p95 message latency | under 200 ms |
| Memory per connection | under 300 KB |
| Slow-reader disconnect | within 30 s |
| Rolling restart | 100% reconnect within 30 s |

10.6 Test the client too: a browser tab backgrounded for 10 minutes, a phone that locks its screen, and a laptop that sleeps. Each behaves differently and each will be reported as a bug.

10.7 Keep the load test in CI as a nightly job with 200 connections. It catches the regression that only appears at scale without costing a full test run per commit.

Gate: all five pass on staging behind the real proxy.

## Worked example

An order-tracking screen for a food delivery app: 8,000 concurrent sockets at dinner peak, 3 Node processes, Redis pub/sub.

| Change | Before | After |
|---|---|---|
| Heartbeat 25 s | 12% dead sockets | 1% |
| Presence debounce 10 s | list flickered 4x per order | stable |
| `bufferedAmount` cutoff 1 MB | one client grew heap to 1.4 GB | flat at 300 MB |
| Replay buffer 500 per room | 3% duplicate messages after reconnect | 0.1% |
| Close code 1012 on deploy | 20% clients stuck until refresh | 2% |

The single largest win was the heartbeat: a quarter of the connections in the table were already dead and still costing memory.

## Second worked example - collaborative document cursors

A design tool with 40 cursors moving in one document, 3,000 documents open at peak.

| Decision | Choice | Result |
|---|---|---|
| Transport | WebSocket | 40 cursors per document need full duplex |
| Cursor throttle | one frame per 50 ms | 60 fps down to 20 fps, invisible to users |
| Payload | 3 fields per cursor, 48 bytes | 40 cursors per tick is under 2 KB |
| Presence | only for the open document | no fan-out to 3,000 documents |
| Replay | last 200 ops per document | resync over HTTP past that |
| Backpressure | drop cursor frames first | a slow reader never blocks an edit |

Cursor traffic is 95% of the messages and 5% of the value. Throttling it before touching anything else cut server CPU by 62% in this shape, and the editing experience did not change.

## Quality checklist

- [ ] Transport chosen with a written reason
- [ ] Polling fallback implemented
- [ ] One envelope with version, type, seq and ts
- [ ] Per-room monotonic sequence numbers
- [ ] Auth at handshake, short-lived ticket
- [ ] Per-room authorisation on join
- [ ] Heartbeat 25 s with a 30 s pong deadline
- [ ] Presence counted by connection, debounced 10 s
- [ ] Backoff with jitter, capped at 30 s
- [ ] Replay from last seq, HTTP resync past the buffer
- [ ] Outbound buffer with idempotency keys
- [ ] Redis pub/sub for cross-process fan-out
- [ ] Close code 1012 on deploy, 5 s drain
- [ ] `bufferedAmount` cutoff and per-connection rate limit
- [ ] Four metrics and three alerts live
- [ ] Proxy read timeout 75 s with a 25 s heartbeat
- [ ] 1,000-connection load test behind the real proxy
- [ ] Per-IP, per-user and per-room limits enforced with close codes, nightly 200-connection test in CI

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Messages vanish after a deploy | Clients reconnect to a new process with no replay | Persist messages, replay from last seq |
| Presence shows 40% online at 3am | Dead sockets never reaped | Heartbeat with a pong deadline |
| Duplicate messages after a phone unlocks | Client resends buffered messages with no dedupe key | Idempotency key plus server-side dedupe |
| Server memory climbs for hours | One slow client's buffer never drained | Check `bufferedAmount`, disconnect above 1 MB |
| Works locally, dies behind nginx | Default 60 s read timeout kills idle sockets | 25 s heartbeat, 75 s proxy timeout |
| Two users on different pods cannot chat | No cross-process fan-out | Redis pub/sub per room |
| CPU pegged with 2,000 clients | Per-message deflate on small frames | Compression only above 1 KB |
| Reconnect storm after a restart | Fixed 1 s retry with no jitter | Exponential backoff with 20% jitter |
| Cursors stutter for everyone when one user joins | Presence broadcast to all 500 members | Send presence only to small rooms or on explicit subscribe |
| Ghost users stay online after a crash | Presence written with no TTL | 90-second TTL refreshed by the heartbeat |

## Copy-ready agent prompt

> Read the skill at the URL above and build a realtime feature with me. Ask me: the feature, the expected concurrent connections, the client platforms, and whether I run one process or several. Then choose the transport with a reason, write the message envelope with version and per-room sequence numbers, and give me the server code with handshake auth, heartbeat, presence and close codes. Then the client with exponential backoff, replay from last seq and a polling fallback. Finish with the Redis fan-out plan, the backpressure limits, the four metrics, and a 1,000-connection load test with pass conditions. Tell me what will break first at 10x the traffic.
