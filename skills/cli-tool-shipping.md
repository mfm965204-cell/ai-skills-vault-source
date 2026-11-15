---
name: cli-tool-shipping
description: Build, package and release a command line tool people keep installed - command surface, exit codes, config precedence, human and JSON output, golden-file tests, packaging for pip and npm, cross-platform paths and a tagged release.
version: 1.0.0
license: MIT
tags: [engineering, cli, packaging, testing, releases, devtools]
---

# CLI Tool Shipping

A CLI is judged in the first 30 seconds: does `--help` explain it, does the error say what to fix, and does it exit non-zero so the script stops. Everything after that is craft.

You finish with a packaged tool installable by `pipx install` or `npx`, a test suite with golden files, and a tagged release that installs clean on a machine that has never seen your repo.

## When to use this skill

- An internal script is being copy-pasted between machines and has drifted.
- You want a tool distributed to users who will not clone a repo.
- A pipeline needs a reliable exit code, not a human reading logs.
- You are turning a one-off notebook into something a teammate can run.

Do NOT use for: a long-running service (that is a server, not a CLI), or a tool whose main job is a GUI (a CLI wrapper around it is fine).

## Stage 1 - Design the command surface

1.1 Write the tool's one-line job, then the verbs: `deploy`, `logs`, `status`, `init`. Verbs are short and there are never more than seven.

1.2 Use noun-verb nesting only when you have more than seven verbs: `config get`, `config set`, `config list`. Otherwise flat commands.

1.3 Write the help text first, before the code. If `--help` reads badly the tool is badly shaped, and this is the cheapest moment to find out.

1.4 Pick names that are already in the user's head: `--output`, `--verbose`, `--dry-run`, `--force`, `--config`. Invented flags cost a lookup every time.

1.5 Decide what runs without arguments. `mytool` with no args prints help and exits 1, not 0 - a bare invocation in a script is a mistake, and 0 hides it.

| Element | Rule | Example |
|---|---|---|
| Command name | lowercase, one word, no hyphen | `mytool` |
| Verbs | 1-7, imperative | `run`, `init`, `ls` |
| Flags | long form, kebab-case | `--dry-run` |
| Short flags | only for the 3 most used | `-v`, `-o`, `-n` |
| Positional args | at most 2 | `mytool run api` |
| Defaults | safe, no side effects | dry run off, overwrite off |
| Help | under 25 lines | 6 lines of usage |

Gate: `--help` written and read aloud before any implementation.

## Stage 2 - Parse arguments and return honest exit codes

2.1 Use the standard library parser (argparse, click, typer, commander). Hand-rolled parsing breaks on `--flag=value` and negative numbers.

2.2 Exit codes are the API: 0 success, 1 general failure, 2 usage error, 126 not executable, 127 not found, 130 interrupted by Ctrl-C. Scripts branch on these.

2.3 Print usage errors to stderr with the offending argument named, and exit 2. Never exit 0 on a bad flag.

2.4 Handle Ctrl-C: catch the signal, clean up, exit 130. A tool that exits 1 on Ctrl-C breaks every `set -e` script around it.

2.5 Never prompt when stdin is not a TTY. In CI a prompt blocks forever; check `sys.stdin.isatty()` and require a `--yes` flag instead.

```python
import argparse, signal, sys

def main(argv=None):
    p = argparse.ArgumentParser(prog="mytool", description="Deploy and inspect a service.")
    p.add_argument("verb", choices=["run", "init", "ls"])
    p.add_argument("target", nargs="?", default="api")
    p.add_argument("-o", "--output", choices=["human", "json"], default="human")
    p.add_argument("-n", "--dry-run", action="store_true")
    p.add_argument("-v", "--verbose", action="count", default=0)
    args = p.parse_args(argv)
    if args.verb == "run" and not sys.stdin.isatty() and not args.yes:
        print("error: refusing to run non-interactively without --yes", file=sys.stderr)
        return 2
    return 0
```

2.6 Keep a `--version` that prints a machine-readable line: `mytool 1.4.2 (build a1b2c3d)`. Support asks for it constantly.

Gate: `mytool --nope; echo $?` prints a useful error and returns 2.

## Stage 3 - Get config precedence right

3.1 Fixed precedence, highest first: command-line flag, environment variable, project config file, user config file, built-in default. Any other order confuses everyone.

3.2 Name environment variables with a prefix: `MYTOOL_API_URL`, `MYTOOL_TIMEOUT`. Bare `TIMEOUT` collides with everything.

3.3 Read the project file from the working directory upward, stopping at the repo root, like git does. Look for `.mytool.toml` then `mytool.toml`.

3.4 Print where each value came from under `--verbose`: `api_url=https://x (env MYTOOL_API_URL)`. This one line ends most support threads.

3.5 Never write config without being asked. `mytool init` writes; `mytool run` reads. A tool that edits dotfiles on first run is a tool people uninstall.

| Source | Example | Wins over |
|---|---|---|
| CLI flag | `--timeout 30` | everything |
| Env var | `MYTOOL_TIMEOUT=30` | files |
| Project file | `./.mytool.toml` | user file |
| User file | `~/.config/mytool/config.toml` | default |
| Default | `timeout = 10` | nothing |

Gate: `--verbose` shows the source of every resolved value.

## Stage 4 - Two output modes, one of them machine-readable

4.1 Human output is for a terminal: aligned columns, colour only when `isatty()`, and a summary line at the end.

4.2 JSON output is for scripts: one object or an array on stdout, no colour, no progress bars, no summary prose. `--output json` must produce something `jq` can read.

4.3 Send logs and progress to stderr, data to stdout. Piping `mytool ls | jq` must work with progress still visible.

4.4 Disable colour when `NO_COLOR` is set or when stdout is not a TTY. Honour `FORCE_COLOR=1` for CI logs.

4.5 Keep JSON keys stable across versions; add fields, never rename them without a major version.

```bash
# human
mytool ls
NAME    STATUS   UPDATED
api     running  2m ago

# machine
mytool ls --output json | jq -r '.[] | select(.status!="running") | .name'
```

4.6 Respect terminal width for tables (`shutil.get_terminal_size()`), and truncate the middle of long values rather than wrapping a table into chaos.

4.7 Add `--output json` to every read command before you need it; the first script that wraps your tool will otherwise parse the human output and break on your next release.

4.8 Keep a `--quiet` mode that prints only the final value, for `$(...)` capture. Three modes is the most a CLI can carry.

Gate: `mytool ls --output json | jq .` parses, and `mytool ls > /dev/null` still shows progress.

## Stage 5 - Make errors say what to do

5.1 Every error message has three parts: what failed, why, and the next command. "Connection refused to https://api.internal:8080 - is the VPN up? Try `mytool doctor`."

5.2 `--verbose` adds the cause chain and a stack trace; the default prints one line. Users who want the trace will ask for it.

5.3 Add a `doctor` verb. It checks config, network, auth and version and prints a checklist. It answers 60% of support questions before they are asked.

5.4 Exit non-zero on any partial failure, and print a summary: "3 of 12 targets failed". Silently succeeding on 9 of 12 is the worst possible behaviour.

5.5 Retry only idempotent operations, at most 3 times, with backoff, and say when you retry.

Gate: the three most common failure modes each produce a message with a next command.

## Stage 6 - Test it like a user

6.1 Test through the CLI boundary: spawn the process and assert on stdout, stderr and exit code. Unit-testing the parser function misses the thing users experience.

6.2 Use golden files: store expected stdout in `tests/golden/<case>.txt` and diff. One command updates them, and every diff is visible in review.

6.3 Cover the five cases every CLI needs: happy path, bad flag (exit 2), missing config, network failure, and Ctrl-C.

6.4 Freeze time and environment in tests: `TZ=UTC`, a temp `HOME`, and a fixed config path, so tests pass on the reviewer's laptop.

6.5 Test on Linux, macOS and Windows in CI. Windows breaks on path separators, line endings and file locking, and you will not catch it by testing locally.

| Test type | What it proves | Count |
|---|---|---|
| Golden stdout | output format is stable | 6-10 |
| Exit codes | scripts can branch | 5 |
| Config precedence | flags beat env beat files | 4 |
| Error messages | the next command is printed | 3 |
| Cross-platform | paths and newlines | 1 job |

6.6 Assert on stderr as well as stdout. Half of a CLI's contract lives in stderr, and a test suite that ignores it will pass while users see nothing useful.

6.7 Keep the golden files small and named for the case (`ls-empty.txt`, `ls-two-rows.txt`). A 200-line golden file nobody reads is a rubber stamp.

Gate: `pytest -q` green on three operating systems.

## Stage 7 - Package for the registry people use

7.1 Python: `pyproject.toml` with an entry point, then `pipx install mytool`. Do not ask users to manage a virtualenv for a CLI.

7.2 Node: `bin` field in `package.json`, then `npx mytool`. Keep the dependency tree small; install time is part of the product.

7.3 Ship a single file when you can (PyInstaller, `bun build --compile`, Go). Single binaries remove the runtime-version problem entirely.

```toml
[project]
name = "mytool"
version = "1.4.2"
requires-python = ">=3.10"
dependencies = ["httpx>=0.27"]

[project.scripts]
mytool = "mytool.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

7.4 Pin the minimum language version you actually test. `requires-python = ">=3.8"` while testing only on 3.12 is a bug report generator.

7.5 Keep the install under 20 seconds. Every heavy dependency is a reason for someone to give up.

Gate: a clean machine installs and runs `--version` with no extra steps.

## Stage 8 - Handle the platform differences

8.1 Use `pathlib` for paths and never concatenate with `/`. Windows accepts forward slashes in most APIs but not all.

8.2 Write files with `newline="\n"` explicitly so Windows does not produce CRLF in generated configs and diffs.

8.3 Handle Windows file locking: an open file cannot be replaced. Write to a temp file and rename, with a retry.

8.4 Read `APPDATA` on Windows, `XDG_CONFIG_HOME` on Linux, `~/Library/Application Support` on macOS, with `~/.config` as the fallback.

8.5 Do not assume a shell. `&&`, `$VAR` and `~` are not universal; spawn processes with an argument list, not a shell string.

8.6 Handle long paths and spaces in paths on Windows by quoting every argument you print in an error message.

8.7 Check the terminal encoding on Windows and set UTF-8 explicitly; a box-drawing table on a cp1252 console crashes with a UnicodeEncodeError.

8.8 Handle `SIGTERM` as well as `SIGINT`. Containers and CI runners send SIGTERM, and a tool that ignores it gets killed mid-write.

Gate: the tool runs on a Windows machine with a space in the username.

## Stage 9 - Release with a tag and a changelog

9.1 Semantic versioning: patch for fixes, minor for new flags, major for changed output or removed flags. CLI output is an API.

9.2 Automate: tag `v1.4.2`, CI builds, publishes to PyPI or npm, and creates a GitHub release with the changelog section.

9.3 Keep `CHANGELOG.md` in Keep-a-Changelog form, one section per version, written for users not for git.

9.4 Publish a checksum for any downloadable binary, and sign the release tag.

9.5 Never publish from a laptop. A release job with a scoped token is the only way to be sure the artefact matches the tag.

9.6 Keep the previous minor version installable; users pin.

9.7 Keep a `1.x` maintenance branch for patch releases while `2.x` settles; enterprise users pin majors.

9.8 Add a `--version` check against the registry at most once a day, cached in the user config, and never let it block or fail a command.

Gate: `pipx install mytool==1.4.2` on a clean machine, and the tag matches the published version.

## Stage 10 - Document and finish the edges

10.1 `--help` is the primary documentation. The README is second and has exactly three code blocks: install, first run, one real example.

10.2 Ship shell completion for bash and zsh; it is 40 lines and doubles the perceived quality.

10.3 Add `--dry-run` to anything that changes state, and make it print the exact commands it would run.

10.4 Include a `--quiet` flag for scripts and make `-v -v` mean debug.

10.5 Print a clear message when the tool is out of date, checked at most once a day and never blocking the command.

Gate: a new user completes the README's first example without asking a question.

## Worked example

An internal deploy tool for 12 services, previously a 300-line bash script.

| Metric | Before | After |
|---|---|---|
| Install steps | clone + export PATH | `pipx install mydeploy` |
| Bad flag behaviour | exit 0 | exit 2 with a message |
| Machine-readable output | none | `--output json` |
| Partial failure | silent | "3 of 12 failed", exit 1 |
| Ctrl-C | exit 1, half-deployed | exit 130, clean rollback |
| Support questions per month | 9 | 2 (the `doctor` verb) |

The bash script's real problem was not language, it was that nothing checked a return code, so a failed deploy looked identical to a successful one.

## Second worked example - a data export tool

A tool that dumps a database table to CSV, used in 40 cron jobs.

| Problem | Cause | Fix |
|---|---|---|
| Cron job kept going after a failure | Exit 0 on a partial write | Exit 1, and write to a temp file then rename |
| CSV had CRLF on one machine | Default newline handling | `newline=""` on open, explicit `\n` |
| Script parsed a progress bar | Data and logs both on stdout | Data on stdout, progress on stderr |
| 3-hour run killed by CI | No timeout flag | `--timeout 7200`, exit 124 on expiry |
| Nobody knew which config applied | No source reporting | `--verbose` prints value and source |

A data tool is a function with a shell interface. Its contract is the exit code, the CSV on stdout and the log on stderr - nothing else.

## Quality checklist

- [ ] Verbs under seven, help written before code
- [ ] `--help` under 25 lines with a real example
- [ ] Exit codes 0, 1, 2, 130 used correctly
- [ ] Usage errors on stderr, exit 2
- [ ] Ctrl-C handled, exits 130
- [ ] No prompt when stdin is not a TTY
- [ ] Config precedence flag > env > project > user > default
- [ ] Env vars prefixed with the tool name
- [ ] `--verbose` prints the source of each config value
- [ ] JSON output on stdout, logs on stderr
- [ ] Colour off when not a TTY or `NO_COLOR` set
- [ ] Every error names the next command
- [ ] `doctor` verb exists
- [ ] Golden-file and exit-code tests, CI green on Linux, macOS and Windows
- [ ] Packaged with an entry point, install under 20 s
- [ ] Changelog and tag published by CI, not a laptop
- [ ] Shell completion for bash and zsh
- [ ] SIGTERM handled, flushed cleanly, atomic writes via temp file and rename

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Scripts keep running after a failure | Errors exit 0 | Return 1 on failure, 2 on usage, and test the codes |
| CI job hangs forever | A confirmation prompt with no TTY | Check `isatty()` and require `--yes` |
| Users cannot tell which config won | No source reporting | Print value and source under `--verbose` |
| `mytool ls | jq` breaks | Progress bars and colour written to stdout | Send logs to stderr, data to stdout |
| Windows users get CRLF in generated files | Default newline translation | Open with `newline="\n"` |
| Install takes 3 minutes | Heavy dependencies pulled for one feature | Make it optional, or ship a single binary |
| Published version differs from the tag | Built on a laptop | Publish only from CI with a scoped token |
| Ctrl-C leaves half-deployed state | No signal handler | Catch SIGINT, roll back, exit 130 |
| CSV corrupt on Windows | Text mode newline translation | Open with `newline=""` and write `\n` |
| Container kills the tool mid-write | SIGTERM ignored | Handle SIGTERM, flush, exit 143 |

## Copy-ready agent prompt

> Read the skill at the URL above and help me ship a CLI tool. Ask me: what it does, who runs it, and whether it is Python or Node. Then write the command surface and the full `--help` text before any code, give me the argument parser with correct exit codes and a non-TTY guard, and the config precedence with source reporting under `--verbose`. Then the human and JSON output paths, the error messages with next commands, the golden-file test plan, the packaging file for pipx or npx, the cross-platform checklist and the CI release workflow. Finish with the changelog entry for the first release. Keep the install under 20 seconds.
