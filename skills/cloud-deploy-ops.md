---
name: cloud-deploy-ops
description: Take an app from localhost to a monitored production deployment - hosting choice, Docker, CI/CD, secrets, domains and TLS, backups, logging, alerting, zero-downtime releases and a rollback you have actually tested.
version: 1.0.0
license: MIT
tags: [devops, deploy, docker, ci-cd, cloudflare, monitoring, sre]
---

# Cloud Deploy & Ops

The deploy is not the finish line. The ability to roll back at 2am is.

## When to use this skill

- Deploying a new app or API to production for the first time.
- Moving off a laptop/Vercel-hobby setup onto something you control.
- Adding CI/CD, monitoring and backups to a project that has none.
- Debugging a deploy that works locally and fails in production.

## Stage 1 - Choose the platform by constraint

| Situation | Use | Why |
|---|---|---|
| Static site / SPA | Cloudflare Pages, Netlify | Free, global CDN, instant rollback |
| Next.js with SSR | Vercel, or Cloudflare Workers | Native support |
| Containerised API + DB | VPS (Hetzner/DO) + Docker Compose, or Fly.io/Railway | Cost control, full access |
| Background jobs + cron | Same host as the API, separate process | Simplicity |
| Managed Postgres | Neon/Supabase/RDS | Backups and failover are not your problem |
| Global low-latency edge logic | Cloudflare Workers | Cold starts near zero |

Rule: pick managed for anything you would be sad to lose (database, object storage, email). Pick self-hosted for anything you can rebuild in an hour.

## Stage 2 - Dockerfile that builds fast and small

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
USER node
EXPOSE 3000
CMD ["node","server.js"]
```

Rules: multi-stage, non-root user, `.dockerignore` with `node_modules`, `.git`, `.env`. Pin base image major versions. One process per container. Never bake secrets into an image - they arrive as environment variables at runtime.

## Stage 3 - Environment and secrets

- Three environments minimum: local, staging, production. Staging must be reachable by a URL you can test.
- Secrets in the platform's secret store (Cloudflare vars, GitHub Actions secrets, Doppler), never in git, never in the image, never in a `.env` committed by accident.
- Validate all env vars at boot and crash loudly with the missing key named. Failing at 3am on a `undefined` is a self-inflicted wound.
- Separate credentials per environment. Production keys never touch a laptop.
- Rotate on any suspicion of exposure; assume a leaked key is already used.

## Stage 4 - CI/CD

```yaml
on: { push: { branches: [main] } }
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint
      - run: npm test -- --run
      - run: npm run build
```

- Gate in that order: typecheck → lint → test → build → deploy. Fail fast, cheapest first.
- Deploy only from `main`. Preview deploys for pull requests.
- Migrations run as an explicit release step with a backup taken immediately before.
- Keep the pipeline under 10 minutes; beyond that, people stop waiting and start bypassing.

## Stage 5 - Domains, TLS, headers

- DNS at one provider, documented. `A`/`AAAA` for the server, `CNAME` for managed hosts.
- TLS automatic (Cloudflare, Let's Encrypt with auto-renew). Verify the renewal actually fires.
- Headers: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, a CSP that you have tested in report-only mode first.
- Redirect `www` to apex or the reverse - pick one and make it permanent.
- Health endpoint `/healthz` that does not touch the database, plus `/readyz` that does.

## Stage 6 - Backups and restore

- Database: automated daily snapshot plus point-in-time recovery if available. **Retention must exceed your worst realistic discovery time** (30 days minimum).
- Uploads/objects: versioning on, lifecycle rules stated.
- Config and infrastructure: in git.
- **Test a restore once.** An untested backup is a rumour. Record the restore time - that is your real RTO.
- Run a quarterly drill: restore into staging, run the smoke test, delete.

## Stage 7 - Logging and alerting

- Structured JSON logs, one line per request: timestamp, level, request_id, route, status, duration, user_id.
- Ship to a central store with 14-30 day retention. `docker logs` is not observability.
- Alert on symptoms, not causes: error rate over 5% for 5 minutes, p95 latency over threshold, 5xx spike, disk over 85%, certificate expiring in 14 days, backup did not run, zero traffic during expected hours.
- Every alert must have a runbook line: what it means, what to check first, how to roll back.
- Page a human only for things that need a human at 3am. Everything else is a dashboard or a digest.

## Stage 8 - Zero-downtime release and rollback

1. Deploy the new version alongside the old.
2. Wait for `/readyz` to pass.
3. Switch traffic.
4. Watch error rate and latency for 10 minutes.
5. Roll back by switching traffic back - and know the exact command before you need it.

For managed hosts, use their instant rollback. For a VPS: keep the previous image tagged, `docker compose up -d` with the old tag. Database migrations must be backward-compatible for one release so a rollback does not corrupt data (expand → migrate → contract).

## Stage 9 - Cost and capacity

Know three numbers: monthly cost, cost per 1,000 requests, and the traffic at which you must scale. Set a billing alert. Check the bill monthly - the top three line items are usually fixable.

## Quality checklist

- [ ] Staging environment reachable and used
- [ ] Secrets in a store, validated at boot
- [ ] CI gates typecheck, lint, test, build
- [ ] TLS valid, security headers set
- [ ] `/healthz` and `/readyz` implemented
- [ ] Backups automated and one restore tested
- [ ] Structured logs centralised
- [ ] Alerts on symptoms with runbooks
- [ ] Rollback command written down and exercised
- [ ] Billing alert set

## Copy-ready agent prompt

> Read the skill at the URL above. Ask me what I am deploying and where. Then produce: the platform recommendation with reasons from the Stage 1 table, a multi-stage Dockerfile and compose file, the GitHub Actions pipeline, the env-var validation code, the health endpoints, the security headers, the backup and restore procedure with the exact commands, and the alert rules with runbook lines. Finish with the rollback command written out so I can paste it at 2am.
