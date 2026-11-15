---
name: docker-image-slimdown
description: Cut a bloated container image to a small, non-root, reproducible
one by measuring layers, splitting build from runtime, and gating size and
CVEs in CI.
version: 1.0.0
license: MIT
tags: [docker, containers, devops, security, ci]
---

# Docker Image Slimdown

A 1.2 GB image is three problems wearing one tag: it takes 40 seconds to pull
on a cold node, it carries a compiler and a shell an attacker can use, and
half its layers are files nobody can name. The fix is not a smaller base image
alone; it is separating the build stage from the runtime stage and deleting
everything the runtime never opens.

By the end you hold a Dockerfile whose final stage is under 180 MB, runs as a
numeric non-root user, has no package manager inside it, and fails CI when it
grows past a set budget.

## When to use this skill

- Your image is above 500 MB and deploys take longer than 2 minutes because of pulls.
- A scanner reports 40+ CVEs, most of them from build tools that never run in production.
- Your Dockerfile copies the whole repo and rebuilds every layer on a one-line change.
- You need the container to run as non-root and there is no `USER` line yet.

Do NOT use for: orchestrator sizing, Kubernetes resource limits or autoscaling
policy (that is a cluster config job), or shrinking a VM disk image — the
layer model does not apply there.

## Stage 1 — Measure before you cut

You cannot trim what you have not counted. Record the current size, the layer
breakdown, and the pull time from a cold node.

1.1 Record the baseline: `docker image ls app:current` and `docker history app:current --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' | head -20`.

1.2 Time a cold pull on a clean runner: `docker rmi app:current && time docker pull registry.yourdomain.in/app:current` — write the seconds down, that is the number users feel.

1.3 List what actually opens files at runtime: `docker run --rm --entrypoint sh app:current -c 'ls -la /app /bin /usr/bin | head -40'` and check for compilers, `git`, `curl` and test directories.

Gate: you have three numbers — image size, cold pull seconds, and the count of
build-only binaries still present in the runtime image.

## Stage 2 — Fix the base image first

Most of the win is one decision. Match the base to the runtime you need and
prefer a pinned digest over a floating tag.

2.1 Replace `node:20` (roughly 1.1 GB) with `node:20-slim` (roughly 220 MB) for Node services, or `gcr.io/distroless/nodejs20-debian12` (roughly 120 MB) when you do not need a shell.

2.2 Pin by digest, not tag: `FROM node:20-slim@sha256:<digest> AS build` — a tag can be repointed under you, a digest cannot.

2.3 Pick the base from this table rather than by habit:

| Runtime | Base to ship | Approx. size | Trade-off |
|---|---|---|---|
| Node service, needs a shell for ops | `node:20-slim` | 220 MB | 60+ packages you do not use |
| Node service, no shell needed | `distroless/nodejs20-debian12` | 120 MB | no `sh`, debugging needs `kubectl debug` |
| Go or Rust binary, static | `distroless/static-debian12` | 2 MB plus binary | no glibc, no timezone data unless copied |
| Python with C extensions | `python:3.12-slim` | 130 MB | needs `build-essential` in the build stage |
| Anything needing `apt` at runtime | none of the above | — | reconsider the requirement |

2.4 For compiled binaries, build against `golang:1.22` or `rust:1.77` and ship on `gcr.io/distroless/static-debian12`, which is about 2 MB before your binary.

Gate: the runtime base alone pulls in under 250 MB, and the `FROM` line
carries a digest.

## Stage 3 — Split build from runtime

A multi-stage file keeps the toolchain in a stage that is thrown away. Only
the final stage is published.

3.1 Name every stage and copy artefacts explicitly — never `COPY . .` into the runtime stage:

```dockerfile
FROM node:20-slim@sha256:<digest> AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:20-slim@sha256:<digest> AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev

FROM gcr.io/distroless/nodejs20-debian12 AS runtime
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
USER 10001
CMD ["dist/server.js"]
```

3.2 Copy only the four paths the server reads: `node_modules`, `dist`, `package.json`, and any static asset directory.

3.3 Confirm the build stage is absent from the result: `docker history app:slim --format '{{.Size}}' | wc -l` should show 6 layers or fewer for this pattern.

Gate: the published stage contains no compiler, no package manager and no
source `.ts` files.

## Stage 4 — Remove package-manager residue

Every `apt-get install` leaves 20–60 MB of lists and caches behind unless you
clean in the same layer.

4.1 Combine install and clean in one `RUN`, because a later `rm` in a separate layer does not shrink the image:

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
 && apt-get purge -y --auto-remove
```

4.2 For Python, use `pip install --no-cache-dir` and add a `.dockerignore` covering `.git`, `node_modules`, `tests`, `*.md` and `dist`.

4.3 Check what the ignore file actually saves: build once with it and once with `--no-cache` after removing it; the byte difference is the local `node_modules` and `.git` you were copying on every build.

4.4 Verify nothing is left: `docker run --rm --entrypoint sh app:slim -c 'du -sh /var/lib/apt/lists /root/.npm 2>/dev/null'` should print nothing or under 1 MB.

Gate: `/var/lib/apt/lists`, `~/.npm` and `~/.cache` are each under 1 MB or
absent.

## Stage 5 — Order layers for cache hits

Rebuild time is a layer-order problem, not a machine problem. Put the
slowest-changing files first.

5.1 Order as: base image, lockfile, dependency install, source copy, build, prune. A source edit then reuses the dependency layer.

5.2 Use BuildKit cache mounts so a rebuild does not refetch the registry: `RUN --mount=type=cache,target=/root/.npm npm ci`.

5.3 Turn on inline cache export so CI runners keep the layer cache between jobs: `docker buildx build --cache-to type=inline --cache-from app:slim -t app:slim .`.

5.4 Measure both: a no-change rebuild should finish in under 10 seconds, and a source-only change in under 60 seconds for a mid-size Node app.

Gate: a source-only change rebuilds without re-running the dependency install
step.

## Stage 6 — Drop root and the shell

The runtime stage should be unable to do damage. That means a numeric user, a
read-only filesystem and no shell.

6.1 Create a fixed UID in the build stage and `COPY --chown=10001:10001` the app files, then `USER 10001`. A numeric UID lets Kubernetes `runAsNonRoot` verify it without reading `/etc/passwd`.

6.2 Run with `--read-only --tmpfs /tmp` and confirm the app starts; anything that writes to the image filesystem shows up as an error in the first 30 seconds.

6.3 Drop Linux capabilities: `--cap-drop=ALL --security-opt=no-new-privileges` — a Node or Go service needs none of them.

Gate: `docker run` with a read-only root filesystem starts cleanly and the
process UID is 10001, not 0.

## Stage 7 — Scan and sign the result

A smaller image still needs a gate. Scan the final stage only, since the build
stage never ships.

7.1 Scan: `trivy image --severity HIGH,CRITICAL --exit-code 1 app:slim` and fail the build on any HIGH.

7.2 Generate an SBOM: `syft app:slim -o spdx-json > sbom.json` and attach it to the release, so a CVE found later can be traced to the exact package.

7.3 Sign with cosign and verify at deploy time: `cosign sign --key env://COSIGN_KEY app:slim`.

Gate: zero HIGH or CRITICAL findings attributable to the runtime stage, and
the image digest is signed.

## Stage 8 — Set the size and pull budget in CI

A budget is the only thing that keeps an image small after the first cleanup.
Enforce it on every merge.

8.1 Add a CI step that reads the image size and fails above the budget:

```yaml
- name: image budget
  run: |
    SIZE=$(docker image inspect app:slim --format '{{.Size}}')
    LIMIT=209715200   # 200 MB
    echo "image bytes: $SIZE"
    test "$SIZE" -lt "$LIMIT"
```

8.2 Set the budget 15% above today's size, not at the theoretical minimum, so ordinary dependency bumps do not block merges.

8.3 Record cold pull time weekly; a pull above 20 seconds on a standard runner is a regression worth a ticket.

Gate: CI fails on an image above 200 MB and the pull time is logged with each
release.

## Stage 9 — Document the decisions

The next person will want to add `curl` for a healthcheck. Give them the
reason not to.

9.1 Write four lines in the Dockerfile: why this base, why this UID, what the budget is, and what is deliberately absent.

9.2 Add a healthcheck that uses the app's own HTTP endpoint rather than `curl` — a distroless image has no curl.

9.3 Put the size, pull time and scan counts in the README so the numbers are visible without running anything.

Gate: the Dockerfile states the budget and the absence list, and the README
carries the current three numbers.

## Worked example — a 1.2 GB Node image to 154 MB

A queue worker image, measured on the same runner before and after.

| Measurement | Before | After | What changed |
|---|---|---|---|
| Image size | 1,218 MB | 154 MB | distroless runtime, pruned dev deps |
| Layers | 31 | 6 | one `RUN` per concern, no `rm` in a later layer |
| Cold pull | 41 s | 6 s | 8x fewer bytes over the wire |
| Rebuild, source change | 2 m 10 s | 22 s | lockfile copy above the source copy |
| HIGH CVEs | 23 | 0 | build toolchain no longer shipped |
| Startup time | 3.1 s | 1.4 s | fewer files to stat at boot |

The first build after the split failed twice, and both failures are worth
naming because they recur.

The container exited with code 1 and no log line. The worker wrote a pid file
to `/app/run` at startup, and the runtime stage was read-only. Fix: `COPY
--chown=10001:10001` an empty `run` directory and point the pid path at
`/tmp`.

The healthcheck reported unhealthy while the process was fine. The image was
distroless, so `CMD curl -f localhost:8080/health` did not exist. Fix: the
orchestrator's `httpGet` probe replaced the in-image healthcheck entirely.

Reproduce the measurement yourself before claiming a win:

```bash
docker build -t app:slim .
docker image inspect app:slim --format '{{.Size}}'
docker history app:slim --no-trunc --format '{{.Size}}	{{.CreatedBy}}'
docker rmi app:slim && time docker pull registry.yourdomain.in/app:slim
trivy image --severity HIGH,CRITICAL app:slim | tail -5
```

If the layer list still shows 20+ entries, the Dockerfile has one instruction
per line rather than one per concern, and the size win is partly luck.

## Quality checklist

- [ ] Image size recorded before and after, both numbers in the PR description.
- [ ] Runtime `FROM` line pinned by digest.
- [ ] Multi-stage file where the runtime stage copies named paths only.
- [ ] No `COPY . .` in the runtime stage.
- [ ] `USER` is a numeric UID above 999.
- [ ] Read-only root filesystem tested and the app starts.
- [ ] No package manager binary present in the runtime stage.
- [ ] `/var/lib/apt/lists` and package caches under 1 MB.
- [ ] Trivy scan passes with zero HIGH or CRITICAL findings.
- [ ] SBOM generated and attached to the release.
- [ ] CI size gate present with the budget in bytes.
- [ ] Cold pull time under 20 seconds on a standard runner.
- [ ] Healthcheck uses an app endpoint, not a shell tool.
- [ ] `.dockerignore` covers `.git`, tests, docs and local node_modules.
- [ ] BuildKit inline cache configured for CI runners.
- [ ] Startup time measured and recorded beside the size number.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Image still 900 MB after switching base | A later `COPY . .` in the runtime stage re-adds source and local modules | Copy named paths only; add `.dockerignore` before the next build |
| `rm -rf` did not shrink the image | The delete ran in a new layer; earlier layers keep the bytes | Combine install and delete in one `RUN` |
| Build takes 6 minutes every time | `COPY . .` sits above the dependency install, invalidating the cache | Move the lockfile copy and install above the source copy |
| Container exits immediately as non-root | App writes to `/app` or `/var/log` at startup | `COPY --chown` the writable paths and mount `/tmp` as tmpfs |
| Distroless image fails its healthcheck | Healthcheck calls `curl`, which distroless does not ship | Use the app's own HTTP probe or an orchestrator probe |
| Scan reports CVEs in packages not installed | The scan covered the build stage | Scan the final stage tag only |
| Pull time unchanged despite a smaller image | Layers are many and small; the registry fetches each separately | Squash related `RUN` steps into one and re-measure |
| CI build slower than the developer laptop | No BuildKit cache export, so every job starts cold | Add `--cache-to type=inline` and `--cache-from` in CI |
| Image grows 40 MB after a routine dependency bump | A transitive package pulled a native build tool into production deps | Re-check with `npm ls --omit=dev` and move it to devDependencies |
| Same digest builds two different sizes | A floating tag moved between builds | Pin by digest and rebuild once to confirm stability |

## Copy-ready agent prompt

> Read the skill at the URL above and shrink my container image. Start by recording size, layer breakdown and cold pull time, then rewrite the Dockerfile with a pinned base, a multi-stage split, a numeric non-root user and cache-friendly layer order. Add the CI size gate and a Trivy scan step, rebuild, and report before and after numbers for size, pull seconds, layer count and HIGH findings. Stop and show me the failing check if the image cannot start read-only as a non-root user.
