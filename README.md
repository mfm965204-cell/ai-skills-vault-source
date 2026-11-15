# Skill Vault — source of truth

Build source for **https://ai-skills-vault.pages.dev** — 20 installable AI agent skills, served as static files from Cloudflare Pages.

This repository exists because the deploy is a **full-manifest publish**: Cloudflare Pages replaces the entire deployment on every upload. If you deploy without every existing file, the missing ones return 404 and the live library is silently deleted. So the complete source must live somewhere durable and readable in full. That is this repo.

## Layout

```
skills/<slug>.md    append-only source of truth — one file per skill
build.py            generator: reads skills/*.md, writes dist/
dist/               generated site — created by the build, not committed
```

`dist/` is generated, never committed and never hand-edited. It is the exact set of files that gets deployed, so it must always be produced by `build.py` from the current `skills/`.

## Rules

1. **Never edit an existing `skills/*.md`.** Add new files only. The library is append-only.
2. **Never hand-edit anything in `dist/`.** Change the source or `build.py`, then rebuild.
3. **Never deploy a partial manifest.** See the deploy gate below.
4. No personal data, agent system prompts, API keys, email addresses or owner configuration in this repo. It is public.

## Getting the source (read this first)

`git clone` and `git push` from a sandbox may be refused: the GitHub App is installed on selected repositories only, and this repo is not one of them. Use the platform tools instead.

- **Read:** the `fetch_repo` platform tool, `owner="mfm965204-cell"`, `repo="ai-skills-vault-source"`. It unpacks the full tree to `/scratch/repos/ai-skills-vault-source/`. This is a public repo, so it needs no App installation and no token.
- **Write:** the GitHub connector's multi-file commit action, which authenticates separately and can write here. Commit the new `skills/*.md` files and the updated `build.py` in one commit.

## Build

```bash
cd /scratch/repos/ai-skills-vault-source
python3 build.py
```

Reads `skills/*.md`, writes `dist/` containing:

| File | Purpose |
|---|---|
| `index.html` | the catalogue, cards grouped by category |
| `skills/<slug>.html` | rendered page per skill |
| `skills/<slug>.md` | raw skill, the install target for agents |
| `skills.json` | full manifest: id, slug, title, category, description, url, raw, tags, highlights |
| `status.json` | tiny inventory: count, categories, slugs — designed to survive truncated fetches |
| `llms.txt`, `sitemap.xml`, `robots.txt`, `404.html`, `_headers` | crawler and platform config |

## Deploy

The sandbox **cannot** reach `ai-skills-vault.pages.dev` or `api.cloudflare.com` — the egress proxy refuses both. Deploy through the Cloudflare connector, not `curl`:

1. Upload every file in `dist/` as a Pages asset, keyed by the **MD5 hex digest of its bytes**, base64-encoded, in batches of 8, with the correct content type.
2. Create a deployment with a manifest mapping `"/<path>"` → hash for **every** file, `branch: "main"`, project `ai-skills-vault`.
3. `_headers` is platform config — it goes in the manifest but is not a served page.

### Deploy gate (do not skip)

Before creating a deployment, assert:

- every slug in the previous `status.json` has a matching file in `dist/skills/`, both `.md` and `.html`;
- the number of manifest entries is **greater than or equal to** the number of entries in the previous deployment (26 at 20 skills: 1 index + 20 pages + 20 raws + 4 root files + status.json);
- `dist/skills.json` parses and its `skills` length equals `dist/status.json` `count`.

If any check fails, **stop**. A partial publish destroys the library.

## Verify

The sandbox cannot fetch the live site either. Use the platform's page-fetch tool on:

- `https://ai-skills-vault.pages.dev/status.json?t=<timestamp>` — cache-busted, under 2 KB, returns the full count and slug list. This is the authoritative post-deploy check.
- one or two new `skills/<slug>.md` raw URLs — confirm frontmatter renders as plain text.

Note: that fetch tool truncates long page bodies at roughly 4.5 KB. `skills.json` and the skill files will come back cut off. That is expected — never try to reconstruct file bodies from a fetch. The bodies are here, on disk, after `git clone`.
