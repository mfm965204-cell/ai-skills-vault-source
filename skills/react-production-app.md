---
name: react-production-app
description: Ship a production-grade React or Next.js application - architecture, data layer, auth, forms, error handling, performance budget, testing and deploy - with the decisions that usually cause rewrites made up front.
version: 1.0.0
license: MIT
tags: [react, nextjs, frontend, architecture, typescript, production]
---

# React Production App

Build a React app that survives real users: typed, tested, observable, fast, and deployable on day one.

## When to use this skill

- A new React/Next.js app that will actually be shipped, not a demo.
- Rescuing a prototype that has become unmaintainable.
- Adding a serious feature to an existing React codebase.

## Stage 1 - Decisions to lock before any code

Write these six answers into `DECISIONS.md`. Changing any of them later is a rewrite.

1. **Rendering model.** Static + client for a dashboard; SSR/ISR for public pages that need SEO; SPA only if the app is behind auth and never indexed.
2. **Router.** Next.js App Router (default for new work), or React Router 6+ for a Vite SPA.
3. **Data layer.** Server Components fetching directly for reads; TanStack Query for client cache, mutations and optimistic UI; never both for the same data.
4. **State split.** Server state in the query cache. UI state local. Cross-tree UI state in Zustand or Context. Never put server data in a global store.
5. **Styling.** Tailwind + CSS variables for tokens. No runtime CSS-in-JS on a performance budget.
6. **Auth.** Managed provider (Supabase/Auth0/Clerk) unless there is a compliance reason to self-host. Session in httpOnly cookies, never localStorage.

## Stage 2 - Folder structure that scales

```
src/
  app/            routes only, thin - no business logic
  features/       feature folders: components, hooks, api, types
  components/ui/  design system primitives
  lib/            clients, utils, formatters
  server/         server-only code, db access, actions
  styles/         tokens and globals
```

Rules: a route file imports from `features/`, never the reverse. Nothing in `features/` imports from `app/`. `server/` never leaks into a client bundle - enforce with `import 'server-only'`.

## Stage 3 - Types and contracts first

1. Define the domain types (`User`, `Order`, `Plan`) in `features/*/types.ts`.
2. Derive API types from one source: Zod schema, OpenAPI, or the database schema. Hand-written duplicate types drift within a week.
3. Validate every boundary: form input, API response, URL params, environment variables. `zod` at the edge, inferred types inside.
4. No `any`. Use `unknown` + a parser. `strict: true` in tsconfig, plus `noUncheckedIndexedAccess`.

```ts
import { z } from "zod";
export const OrderSchema = z.object({
  id: z.string().uuid(),
  total: z.number().int().nonnegative(),
  status: z.enum(["pending", "paid", "shipped", "cancelled"]),
});
export type Order = z.infer<typeof OrderSchema>;
```

## Stage 4 - The data layer

- Reads: fetch on the server where possible; cache with explicit `revalidate` (Next) or `staleTime` (Query).
- Writes: server actions or route handlers. Validate, authorise, then mutate. Authorise on the server every time - a hidden button is not a permission.
- Mutations: optimistic update + rollback on error + toast. Never leave the UI in a lying state.
- Errors: one error boundary per route segment, one per async island. Show a retry, log the digest.
- Loading: skeletons that match the final layout's shape, not spinners in the middle of nowhere.
- Pagination: cursor-based for feeds, offset for admin tables. Never `SELECT *` unbounded.

## Stage 5 - Forms

Every form gets: schema validation, per-field errors on blur, disabled submit while pending, success state, server-error mapping to fields, and a double-submit guard.

```tsx
const { register, handleSubmit, formState: { errors, isSubmitting } } =
  useForm<z.infer<typeof FormSchema>>({ resolver: zodResolver(FormSchema) });
```

## Stage 6 - Performance budget (enforce it, do not hope)

| Metric | Budget |
|---|---|
| First-load JS (gzipped) | under 180 KB |
| LCP on 4G mobile | under 2.5 s |
| CLS | under 0.1 |
| INP | under 200 ms |
| Route-level code splitting | every route |
| Images | `next/image` or `srcset` + `loading=lazy`, AVIF/WebP |

Tactics: `dynamic()` for heavy widgets, no barrel-file imports of large libs, virtualise lists over 100 rows, debounce search 250 ms, memoise only measured hot paths.

## Stage 7 - Testing that earns its place

1. **Unit** - pure functions, formatters, reducers (Vitest).
2. **Component** - the 5 highest-risk components: form, table, auth gate, payment sheet, empty/error states (Testing Library).
3. **E2E** - one happy path per critical journey: signup, login, core action, checkout (Playwright).
4. **Contract** - API schema against a mocked response so a backend change fails the build.

Skip snapshot tests of large trees - they fail on every styling change and catch nothing.

## Stage 8 - Observability and CI

- Error tracking (Sentry) with source maps, release tags, user id.
- Structured logs on the server; no `console.log` in production code.
- CI gates in order: typecheck, lint, unit, build, e2e on preview, then deploy.
- Environment variables validated at boot - fail fast, not at 3am.

## Stage 9 - Deploy checklist

- [ ] `NODE_ENV=production` build passes locally
- [ ] Env vars set in the host, none committed
- [ ] HTTPS, security headers (CSP, HSTS, X-Frame-Options)
- [ ] 404 and 500 pages designed
- [ ] Preview deploy reviewed on a real phone
- [ ] Rollback path tested once

## Definition of done

Typed end to end, no `any`; every async path has loading, empty and error states; auth enforced server-side; Lighthouse mobile 90+ performance and 100 accessibility; critical journey covered by one passing e2e; deploy reproducible from a clean clone in under 10 minutes.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Re-render storms | Server data in global store, unstable props | Query cache + stable keys + memo on hot list rows |
| Hydration mismatch | `Date.now()`/`window` in render | Move to `useEffect` or server-provide the value |
| Bundle bloat | Barrel imports, whole-lib imports | Named imports, `dynamic()`, bundle analyser |
| Auth bypass | Client-only route guards | Server-side session check in middleware + loader |
| Slow lists | 1000 rows rendered | Virtualise, paginate, memoise row |

## Copy-ready agent prompt

> Read the skill at the URL above. Start by asking me the six Stage 1 decisions in one message and write `DECISIONS.md`. Then scaffold the folder structure, define Zod contracts, and build feature by feature with loading/empty/error states included from the first commit. Enforce the Stage 6 performance budget and finish with the Stage 9 deploy checklist. Never use `any`.
