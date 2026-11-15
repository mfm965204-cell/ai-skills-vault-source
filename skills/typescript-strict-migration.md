---
name: typescript-strict-migration
description: Convert a JavaScript or loosely typed codebase to strict
TypeScript with a per-file allowlist ratchet, one compiler flag at a time, and
a CI gate that never lets the count rise.
version: 1.0.0
license: MIT
tags: [typescript, refactoring, engineering, ci, types]
---

# TypeScript Strict Migration

Turning on `strict` in a 300-file codebase produces 8,000 errors and no path
forward, so teams either abandon it or paste `any` until the count drops. Both
outcomes leave the same untyped code with a config file that claims otherwise.

The method here is a ratchet: enable one compiler flag at a time, allowlist
the files that still fail, and fail CI whenever the count of allowlisted files
or `any` usages rises. The end state is a codebase where a new file cannot be
added without types and every remaining exception has a name and a date.

## When to use this skill

- `tsconfig.json` has `strict: false` and turning it on produces thousands of errors.
- The codebase is half `.js`, half `.ts`, and new code copies whichever file it lands next to.
- Types exist but `any` and `as unknown as` do the work of types.
- A production bug traced back to a field the type said existed and the API did not send.

Do NOT use for: choosing a framework or build tool, or a single-file type fix
— that is an ordinary PR. This skill is for a codebase that cannot turn strict
on today.

## Stage 1 — Measure the baseline you will ratchet against

The ratchet needs three numbers: errors per flag, files that fail, and `any`
occurrences. Without them, progress is a feeling.

1.1 Count errors with the current config: `npx tsc --noEmit | grep -c 'error TS'` — write it down with the date.

1.2 Count the escape hatches: `rg -c ':\\s*any\\b|as any|<any>' src/ | awk -F: '{s+=$2} END {print s}'` and the same for `@ts-ignore` and `@ts-expect-error`.

1.3 Count files by extension: `find src -name '*.js' | wc -l` against `find src -name '*.ts' | wc -l`; the ratio decides whether to convert files first or flags first.

Gate: three numbers recorded — compiler errors, `any` count, and the JS-to-TS
file ratio — with the command that produced each.

## Stage 2 — Separate type checking from emitting

A migration needs the compiler to check without changing the build. Set that
up before touching code.

2.1 Add a `tsconfig.check.json` that extends the build config with `noEmit: true`, and run it as its own CI step so a type error is never a build failure during the migration.

2.2 Keep the existing build untouched for the first two weeks; a migration that breaks deploys gets reverted, and a reverted migration costs more than a slow one.

2.3 Turn on `allowJs: true` and `checkJs: false` so JS files are included in the program but not yet checked — this is what lets one flag at a time apply.

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "noEmit": true,
    "allowJs": true,
    "checkJs": false,
    "strict": false,
    "noImplicitAny": false,
    "strictNullChecks": false
  },
  "include": ["src"]
}
```

Gate: `npx tsc -p tsconfig.check.json` exits 0 on today's code, and the
production build is unchanged.

## Stage 3 — Convert files before turning on flags

A `.js` file cannot be checked at all. Converting is mechanical and unblocks
every later flag.

3.1 Rename leaf files first — utilities and constants with no imports from application code — because they have the fewest callers to fix per rename.

3.2 Convert 20 files per pull request and stop; a 300-file rename PR cannot be reviewed and will be merged blind.

3.3 Fix the imports the rename breaks in the same PR, and never mix a conversion PR with a behaviour change.

| Approach | Files per PR | Review load | When it works |
|---|---|---|---|
| Leaf-first | 20 | low | most codebases, default choice |
| Entry-point-first | 3 to 5 | high | when the entry points are the risk |
| Big-bang rename | 300 | unreviewable | never |

Gate: the `.js` count drops by at least 20 per week and no conversion PR
changes behaviour.

## Stage 4 — Type the boundaries first, internals later

The bugs live at the edges: HTTP responses, environment variables, form
payloads. Typing those pays before typing a helper.

4.1 Validate every external response with a runtime schema and derive the type from it, so the type and the check cannot drift:

```typescript
const Order = z.object({
  id: z.string().uuid(),
  total_paise: z.number().int().nonnegative(),
  status: z.enum(["pending", "paid", "refunded"]),
});
type Order = z.infer<typeof Order>;
```

4.2 Parse environment variables once at startup into a typed object; a missing `DATABASE_URL` should stop the process at boot, not at the first request.

4.3 Type the public props of each component or exported function, and leave the internal locals inferred — inference is free, annotations are maintenance.

Gate: every HTTP response and every environment variable passes through a
runtime parse, and the parsed type is the only one used downstream.

## Stage 5 — Turn on strictNullChecks first

It produces the most errors and prevents the most production incidents. Do it
alone, with nothing else changing.

5.1 Set `strictNullChecks: true` and capture the error count; on a 300-file app expect 40% of the eventual total.

5.2 Fix by narrowing at the source — return `T | undefined` honestly and check it — rather than adding `!`, which is a lie the compiler accepts.

5.3 Allowlist the files you cannot fix this sprint in a `strict-null.allowlist` file read by a wrapper script, so the flag stays on for everything else.

Gate: `strictNullChecks` is on, the non-allowlisted error count is zero, and
the allowlist has a date per entry.

## Stage 6 — Add noImplicitAny, then the rest

Each later flag is smaller and each one must land alone, so a regression has
one candidate cause.

6.1 Order: `strictNullChecks`, then `noImplicitAny`, then `strictFunctionTypes`, then `strictBindCallApply`, then `exactOptionalPropertyTypes` last because it changes the meaning of `?:`.

6.2 Give each flag its own two-week window; a flag that produces more than 1,500 errors is split by directory instead.

6.3 Keep `noUncheckedIndexedAccess` for a separate window after the five above; it is the one flag that turns every array read into a possible `undefined` and needs its own fortnight.

6.4 Re-run the ratchet after each flag and publish the number in the team channel; visible progress is what keeps a 90-day migration alive.

| Flag | Typical error share | Risk if skipped |
|---|---|---|
| `strictNullChecks` | 40% | undefined reads at runtime |
| `noImplicitAny` | 30% | silent type holes in callbacks |
| `strictFunctionTypes` | 10% | unsound callback variance |
| `strictBindCallApply` | 5% | wrong `this` in bound handlers |
| `exactOptionalPropertyTypes` | 15% | `undefined` versus absent |

Gate: each flag landed in its own PR, with the before and after counts in the
description.

## Stage 7 — Budget the escape hatches

`any` is not banned; it is rationed. A budget makes the ration visible.

7.1 Add an ESLint rule set that errors on `any` in new files and warns in allowlisted ones, so a new file cannot start untyped.

7.2 Ratchet the allowance down by 25% every two weeks: 400, 300, 225, 169 — a schedule beats a target because it has a date.

7.3 Require a comment with a ticket id on every `@ts-expect-error`, and delete the ones whose ticket is closed.

Gate: `any` count falls every two weeks and no new file contains `any` without
a ticket id.

## Stage 8 — Gate CI on the count, not on perfection

The ratchet is a comparison against a committed baseline file, which is the
only way to fail on regression without failing on legacy.

8.1 Commit `type-baseline.json` with the current error and `any` counts per directory.

8.2 Fail the build when any directory's count rises, even if the total falls:

```bash
node scripts/type-ratchet.js --baseline type-baseline.json --current out/type-count.json
# exits 1 when any directory increases, prints the delta table
```

8.3 Regenerate the baseline only in the same PR that lowers a number, never in a PR that raises one.

Gate: a PR that adds a single `any` fails CI with the directory and the delta
named.

## Stage 9 — Retire the allowlists

The migration ends when the allowlists are empty and `strict: true` sits in
the main config with no overrides.

9.1 Delete each allowlist entry as its file is fixed, and assert in CI that no allowlisted file has zero errors — a stale entry hides the fact that it is done.

9.2 Set `strict: true` in `tsconfig.json`, remove `tsconfig.check.json`, and confirm the production build still passes.

9.3 Add `@typescript-eslint/no-explicit-any: error` for `src/` and leave it on permanently.

Gate: zero allowlist entries, `strict: true` in the main config, and the lint
rule at error level.

## Worked example — 312 files, 8,140 errors, 96 days

A Node service with 312 files, 41% still `.js`, and `strict: false`.

| Week | Flag or step | Errors left | Files allowlisted | `any` count |
|---|---|---|---|---|
| 0 | baseline | 8,140 | — | 412 |
| 2 | `noEmit` check config | 8,140 | — | 412 |
| 6 | JS to TS conversion done | 8,140 | — | 398 |
| 10 | `strictNullChecks` | 4,910 | 61 | 351 |
| 14 | `noImplicitAny` | 2,240 | 44 | 268 |
| 18 | `strictFunctionTypes` | 1,410 | 29 | 194 |
| 22 | `strictBindCallApply` | 1,180 | 21 | 147 |
| 26 | `exactOptionalPropertyTypes` | 380 | 9 | 96 |
| 96 days | allowlists empty | 0 | 0 | 88 |

The conversion step produced no error reduction, which surprised the team. It
was still the right first move: without `allowJs` and real `.ts` files, every
later flag would have needed the same renames mixed into type work, and the
PRs would have been unreviewable.

The one wrong turn was `exactOptionalPropertyTypes` scheduled alongside
`strictNullChecks`. It changes `foo?: string` from "string or undefined" to
"absent or string", so 700 errors were not nullability at all but a semantics
change. Splitting it into its own window at the end removed the confusion.

The 88 remaining `any` at the end were all in generated API clients. They
stayed, with a lint exemption scoped to `src/generated/**` and a comment
naming the generator.

## Reference — the flags and what each one changes

| Flag | What it forbids | First error you will see | Fix pattern |
|---|---|---|---|
| `strictNullChecks` | `null` and `undefined` assigned to other types | "possibly undefined" | narrow at the source, return `T \| undefined` |
| `noImplicitAny` | parameters and returns with no inferred type | "implicitly has an 'any' type" | annotate the public signature only |
| `strictFunctionTypes` | unsound parameter variance in callbacks | "not assignable" on a handler | widen the parameter type or use a generic |
| `strictBindCallApply` | `call`, `apply`, `bind` with wrong argument types | "expected 2 arguments, got 1" | type the function then bind |
| `noImplicitThis` | `this` with no type in a function | "'this' implicitly has type any" | arrow functions or an explicit `this` parameter |
| `useUnknownInCatchVariables` | `catch (e)` typed as `any` | "unknown" on property access | narrow with `instanceof Error` |
| `exactOptionalPropertyTypes` | `undefined` passed for an absent optional | "not assignable to exact type" | omit the key, or widen the type |
| `noUncheckedIndexedAccess` | indexing an array without a check | "possibly undefined" on `arr[i]` | check the element or use `at()` |

Two of these change semantics rather than catching mistakes:
`exactOptionalPropertyTypes` and `noUncheckedIndexedAccess`. Schedule both
after everything else, and expect the fixes to be real code changes rather
than annotations.

## Quality checklist

- [ ] Baseline errors, `any` count and JS-to-TS ratio recorded with dates.
- [ ] A `noEmit` check config exists and CI runs it.
- [ ] Production build untouched for the first two weeks.
- [ ] JS files converted at 20 per PR or fewer.
- [ ] Every HTTP response parsed by a runtime schema.
- [ ] Environment variables parsed once at startup.
- [ ] `strictNullChecks` landed in its own PR.
- [ ] No `!` non-null assertion added without a comment.
- [ ] Each later flag landed alone with its before and after counts.
- [ ] `any` budget ratcheted 25% every two weeks.
- [ ] Every `@ts-expect-error` carries a ticket id.
- [ ] CI fails when any directory's count rises.
- [ ] Baseline regenerated only in PRs that lower a number.
- [ ] Allowlists empty and `strict: true` in the main config.
- [ ] One named owner and a weekly published ratchet number.
- [ ] `noUncheckedIndexedAccess` scheduled after the main five flags.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Error count does not fall despite weeks of work | Conversion PRs and flag PRs are mixed, so neither shows progress | Separate the two and measure only flag windows |
| Every fix adds two `any` | The migration is fixing call sites instead of typing the boundary | Parse external data once and let inference flow inward |
| A PR fixes 300 errors and breaks production | Behaviour change hidden inside a type change | Forbid behaviour changes in type PRs; split the diff |
| Allowlist grows every sprint | No expiry, and entries are added during incidents | Fail CI on an entry with no date, and review weekly |
| `strict: true` breaks the build at the end | The check config and build config diverged over 90 days | Keep `extends` and one compiler option list, and diff them weekly |
| Type says the field exists, runtime says otherwise | Hand-written interface for an external API | Derive the type from the runtime schema |
| Migration stalls at 60% | No owner and no published number, so it loses every priority argument | Name one owner and post the weekly ratchet table |
| `@ts-expect-error` used to silence real bugs | The suppression hides a type error that is also a logic error | Convert to `@ts-ignore` never; fix the type or narrow the value |

## Copy-ready agent prompt

> Read the skill at the URL above and migrate my codebase to strict TypeScript. Record the baseline error count, `any` count and JS-to-TS ratio first, then add a `noEmit` check config, convert 20 files per PR, type every HTTP response and environment variable through a runtime schema, and enable one compiler flag at a time in the order null checks, implicit any, function types, bind-call-apply, exact optional properties. Add the per-directory ratchet to CI and report the table of week, flag, errors left, files allowlisted and `any` count. Stop and show me the failing directory if any count rises.
