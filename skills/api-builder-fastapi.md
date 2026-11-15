---
name: api-builder-fastapi
description: Design and ship a production backend API - contract-first design, typed validation, auth, authorisation, idempotency, pagination, rate limits, migrations, tests, observability and deploy - in FastAPI or equivalent.
version: 1.0.0
license: MIT
tags: [api, backend, fastapi, python, rest, postgres, production]
---

# API Builder (FastAPI)

Most APIs fail on the same five things: unclear contracts, no authorisation model, no idempotency, no pagination discipline, and no observability. This skill closes all five before launch.

## When to use this skill

- Building a new REST API that will serve a real client.
- Adding endpoints to an existing service.
- Hardening a prototype API before exposing it.

## Stage 1 - Contract before code

Write the OpenAPI shape first, or the resource table:

| Resource | Method | Path | Auth | Success | Errors |
|---|---|---|---|---|---|
| user | GET | /v1/users/{id} | bearer | 200 | 401, 403, 404 |
| user | POST | /v1/users | bearer + admin | 201 | 400, 401, 403, 409 |
| order | POST | /v1/orders | bearer | 201 | 400, 402, 409, 422 |

Rules that prevent rewrites: version in the path (`/v1`), plural nouns, no verbs in paths, snake_case JSON, ISO-8601 UTC timestamps, ids as UUID or ULID strings, money as integer minor units plus a currency code (never floats).

## Stage 2 - Project layout

```
app/
  main.py            app factory, middleware, routers
  core/              config, security, logging, errors
  db/                engine, session, migrations
  models/            SQLAlchemy models
  schemas/           pydantic request/response models
  api/v1/            routers per resource
  services/          business logic - no HTTP here
  tests/
```

Hard rule: routers validate and delegate; services contain logic; models touch the database. No SQL in a router, no `Request` object in a service.

## Stage 3 - Validation and error model

```python
from pydantic import BaseModel, EmailStr, Field
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=80)
    plan: Literal["free", "pro"] = "free"
```

One error envelope for the whole API, always:

```json
{"error": {"code": "email_taken", "message": "That email is already registered.",
           "field": "email", "request_id": "req_01H..."}}
```

- 400 malformed, 401 unauthenticated, 403 not permitted, 404 absent, 409 conflict, 422 semantic validation, 429 rate limited, 500 unexpected.
- Never leak stack traces, SQL or internal ids to clients. Log them with the `request_id` instead.
- Error `code` is a stable machine string; `message` is human and safe to show.

## Stage 4 - Auth and authorisation

1. Authentication: bearer JWT or opaque session in an httpOnly cookie. Short-lived access token (15 min) + refresh token rotation.
2. Passwords: argon2id, never bcrypt-with-default-cost, never MD5/SHA.
3. Authorisation: a dependency that loads the resource and checks ownership or role **on the server**, per endpoint. A check in the UI is not a check.

```python
def get_owned_order(order_id: str, user=Depends(current_user), db=Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "order_not_found")
    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(403, "forbidden")
    return order
```

4. Rate limit per user and per IP on auth and write endpoints. 429 with `Retry-After`.
5. Never trust client-supplied role, price, total or user id. Derive them server-side.

## Stage 5 - Idempotency and safety on writes

- Accept `Idempotency-Key` on POST that creates money or state. Store key -> response for 24h; replay returns the same response.
- Wrap multi-step writes in a transaction. Commit once, at the end.
- Use `SELECT ... FOR UPDATE` or an optimistic version column where concurrent updates matter.
- Soft-delete with `deleted_at` when recovery or audit is needed; hard-delete for genuine privacy requests.

## Stage 6 - Pagination, filtering, sorting

```python
@router.get("/orders")
def list_orders(cursor: str | None = None, limit: int = Query(20, le=100), ...):
```

- Cursor pagination for feeds and anything that changes while paging; offset for admin tables.
- Cap `limit` at 100. Reject unknown `sort` fields against an allowlist - never interpolate into SQL.
- Return `{"data": [...], "next_cursor": "..."}`. Never return an unbounded array.

## Stage 7 - Database and migrations

- Alembic (or equivalent) from commit one. Never `create_all()` in production.
- Every migration is reversible; test the downgrade once.
- Index every foreign key and every column you filter or sort on. Verify with `EXPLAIN`.
- Add NOT NULL columns with a default, backfill, then drop the default - in three steps, not one.
- Connection pooling sized to the database's limit, not to hope.

## Stage 8 - Tests

1. Unit tests for services with a fake repository - fast, no DB.
2. Integration tests against a real ephemeral Postgres (testcontainers or a docker service) - catches what mocks hide.
3. Contract tests: every endpoint's success and error shape asserted against the OpenAPI schema.
4. Auth tests: unauthenticated, wrong user, admin, expired token, for each protected route.
5. One load smoke test at 10x expected traffic on the heaviest read path.

Target: the auth-and-write paths have 100% of their branches covered. Chasing a global coverage number is theatre.

## Stage 9 - Observability and operations

- Structured JSON logs with `request_id`, `user_id`, `route`, `status`, `duration_ms`.
- `/healthz` (liveness) and `/readyz` (dependencies reachable).
- Metrics: p50/p95/p99 latency per route, error rate, queue depth, DB pool saturation.
- Tracing across the API and any downstream calls.
- Sentry with release tags and source maps where relevant.

## Stage 10 - Deploy checklist

- [ ] Secrets in the platform's secret store, validated at boot, none in the repo
- [ ] CORS locked to real origins, not `*` with credentials
- [ ] Security headers, HTTPS enforced
- [ ] Rate limits live
- [ ] Migrations run as a release step, not on app boot
- [ ] Backups enabled and one restore tested
- [ ] OpenAPI docs either public deliberately or disabled in production
- [ ] Rollback path exercised once

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| 500s under load | Pool exhaustion / N+1 queries | Pool sizing, eager loading, indexes |
| Duplicate charges | No idempotency key | Add key + unique constraint |
| Slow list endpoint | OFFSET on a big table | Cursor pagination |
| Data leak | Missing ownership check | Central ownership dependency, test it |
| Broken clients after a change | Unversioned breaking change | `/v2`, deprecate with a sunset header |

## Copy-ready agent prompt

> Read the skill at the URL above. Start with the Stage 1 resource table for my domain and get my approval. Then scaffold the layout, write pydantic schemas, services with the logic, routers that only delegate, one error envelope, an ownership-check dependency, cursor pagination, Alembic migrations and tests including auth failure cases. Finish with the Stage 10 deploy checklist and tell me honestly which items are not done.
