import html, json, pathlib, re

import shutil

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "skills"          # append-only source of truth: one .md per skill
OUT = HERE / "dist"            # generated site, this is what gets deployed
OUT.mkdir(exist_ok=True)
(OUT / "skills").mkdir(exist_ok=True)
for _f in SRC.glob("*.md"):
    shutil.copy2(_f, OUT / "skills" / _f.name)

ROOT = OUT
SK = OUT / "skills"
BASE = "https://ai-skills-vault.pages.dev"

_WORDS = {20: "Twenty", 40: "Forty", 60: "Sixty", 80: "Eighty", 100: "One hundred"}
def numword(n):
    """Spell out the skill count for prose, falling back to the digits."""
    return _WORDS.get(n, str(n))

META = [
    dict(slug="3d-animation-on-phone", cat="Creative", accent="#a855f7",
         title="3D Animation On Phone",
         tag="Cinematic 3D clips rendered entirely on a phone — no desktop, no render farm.",
         hi=["7-stage pipeline from beat sheet to export",
             "Exact lighting + camera settings that stop it looking like a toy",
             "Platform render specs and a 9-point quality gate"]),
    dict(slug="clone-ui-from-screenshot", cat="Frontend", accent="#38bdf8",
         title="Clone UI From Screenshot",
         tag="Reverse-engineer any app or site UI into pixel-accurate responsive code.",
         hi=["Measurement + design-token recovery from images",
             "Grey-skeleton-first build order",
             "Two-pass pixel-diff verification loop"]),
    dict(slug="react-production-app", cat="Engineering", accent="#22d3ee",
         title="React Production App",
         tag="Ship a React or Next.js app that survives real users: typed, tested, observable.",
         hi=["Six decisions locked before any code",
             "Server/client state split and data contracts",
             "Performance budget, test pyramid, deploy gates"]),
    dict(slug="prompt-to-landing-page", cat="Marketing", accent="#34d399",
         title="Prompt To Landing Page",
         tag="One-line idea to a conversion-optimised page, deployed today.",
         hi=["Positioning sentence before copy",
             "Section order that earns every scroll",
             "Mobile-first, under 500 KB, schema-ready"]),
    dict(slug="ai-video-editing-reels", cat="Creative", accent="#f472b6",
         title="AI Video Editing For Reels",
         tag="Short-form vertical video engineered for retention, not just edited.",
         hi=["5-block retention architecture with timings",
             "Cut rhythm, caption and sound-design rules",
             "Underperformance diagnosis table"]),
    dict(slug="agentic-web-scraper", cat="Data", accent="#fbbf24",
         title="Agentic Web Scraper",
         tag="A data pipeline an agent can run unsupervised for a year.",
         hi=["Legality and robots checks before anything else",
             "Anti-brittleness selectors with fallbacks",
             "Validation gates and drift alerts"]),
    dict(slug="seo-content-engine", cat="Marketing", accent="#a3e635",
         title="SEO Content Engine",
         tag="Publish in clusters that compound, not singles that decay.",
         hi=["Intent map and hub-and-spoke clustering",
             "SERP-informed outlines, E-E-A-T writing rules",
             "Monthly refresh loop with position-based actions"]),
    dict(slug="api-builder-fastapi", cat="Engineering", accent="#60a5fa",
         title="API Builder (FastAPI)",
         tag="Contract-first backend with auth, idempotency and observability built in.",
         hi=["Resource table before a line of code",
             "One error envelope, one ownership dependency",
             "Migration, test and deploy checklists"]),
    dict(slug="data-dashboard-storyteller", cat="Data", accent="#f97316",
         title="Data Dashboard Storyteller",
         tag="Raw CSV in, decision-ready dashboard and narrative out.",
         hi=["Data audit: grain, duplicates, definition conflicts",
             "Chart selection table by question type",
             "Narrative structure: headline to falsifier"]),
    dict(slug="spreadsheet-automation-agent", cat="Automation", accent="#c084fc",
         title="Spreadsheet Automation Agent",
         tag="Turn a fragile manual workbook into a three-layer system with a readme.",
         hi=["Input / calculation / output separation",
             "Formula library that survives row inserts",
             "Apps Script + Power Query automation patterns"]),
    dict(slug="voice-agent-builder", cat="AI", accent="#22d3ee",
         title="Voice Agent Builder",
         tag="A phone agent that handles real calls with sub-second turns.",
         hi=["Latency budget for the whole turn loop",
             "Barge-in, turn detection and the fallback ladder",
             "Compliance, disclosure and call analytics"]),
    dict(slug="rag-knowledge-base", cat="AI", accent="#818cf8",
         title="RAG Knowledge Base",
         tag="Retrieval that answers correctly, with citations you can click.",
         hi=["Chunking with context headers - the real fix",
             "Hybrid dense + BM25 with reranking",
             "Eval set with recall, MRR and faithfulness"]),
    dict(slug="ai-workflow-automation", cat="Automation", accent="#fbbf24",
         title="AI Workflow Automation",
         tag="Automate a real business process, exceptions included.",
         hi=["Exception mapping before any wiring",
             "Code vs n8n vs Zapier decision table",
             "Idempotency, DLQ, and alerts on silence"]),
    dict(slug="mobile-app-with-ai", cat="Engineering", accent="#34d399",
         title="Mobile App With AI",
         tag="Ship an Expo app with an AI feature that survives store review.",
         hi=["On-device vs cloud model table",
             "Offline-first data and optimistic writes",
             "Cost caps, four failure states, staged rollout"]),
    dict(slug="game-dev-2d", cat="Creative", accent="#f472b6",
         title="2D Game Development",
         tag="A finished small game in weeks, with feel that actually lands.",
         hi=["Scope limits that stop the project dying",
             "Input buffering, coyote time, hit stop, shake",
             "Difficulty ramp and 60 fps budget"]),
    dict(slug="resume-job-hunter", cat="Career", accent="#a3e635",
         title="Resume & Job Hunter",
         tag="Run the search like a campaign: ATS-proof, tailored, honest.",
         hi=["One-page ATS-safe structure",
             "Bullet formula with real metrics only",
             "90-word outreach and negotiation scripts"]),
    dict(slug="brand-identity-system", cat="Design", accent="#c084fc",
         title="Brand Identity System",
         tag="Logo, colour, type and voice that a team can actually follow.",
         hi=["Positioning and anti-brand before visuals",
             "Three logo tiers, contrast-checked palette",
             "One-page guideline plus an editable asset kit"]),
    dict(slug="prompt-engineering-lab", cat="AI", accent="#60a5fa",
         title="Prompt Engineering Lab",
         tag="Treat prompts like code: spec, schema, evals, versioning.",
         hi=["Spec and JSON schema before prose",
             "30-case eval set with a frozen baseline",
             "Injection defence and cost per 1,000 calls"]),
    dict(slug="cloud-deploy-ops", cat="Engineering", accent="#38bdf8",
         title="Cloud Deploy & Ops",
         tag="Localhost to monitored production, with a tested rollback.",
         hi=["Platform choice by constraint table",
             "Docker, CI gates, secrets, headers",
             "Backups you restore once, alerts with runbooks"]),
    dict(slug="pdf-document-automation", cat="Data", accent="#f97316",
         title="PDF Document Automation",
         tag="Piles of PDFs into validated rows, with a review loop.",
         hi=["Text layer first, OCR only where needed",
             "Extraction ladder: rules, then LLM",
             "Source quotes, arithmetic checks, rejects.csv"]),
    dict(slug="llm-cost-optimizer", cat="AI", accent="#22d3ee",
         title="LLM Cost Optimizer",
         tag="Cut the bill 40-80% without losing quality.",
         hi=["Token buckets measured before any change",
             "Six levers, one per deploy, each with an eval delta",
             "Alarms on cost per request, not total spend"]),
    dict(slug="llm-finetune-qlora", cat="AI", accent="#818cf8",
         title="Fine-Tune With QLoRA",
         tag="Train a 7B model on one 24 GB GPU, with an eval that proves it.",
         hi=["Dataset, split and leakage checks",
             "QLoRA config with r, alpha and epochs justified",
             "Merge, quantise, re-score, ramp at 5%"]),
    dict(slug="ai-code-review-bot", cat="AI", accent="#fbbf24",
         title="AI Code Review Bot",
         tag="An LLM reviewer that is not muted by week two.",
         hi=["Written policy with severities",
             "Seven-comment cap and dismissal memory",
             "30-PR eval plus prompt-injection tests"]),
    dict(slug="zero-downtime-migrations", cat="Engineering", accent="#34d399",
         title="Zero-Downtime Migrations",
         tag="Change a live Postgres schema without a maintenance window.",
         hi=["Lock table for every operation",
             "Expand-contract with a deploy order",
             "Batched backfill with a stop switch"]),
    dict(slug="websocket-realtime-app", cat="Engineering", accent="#f472b6",
         title="WebSocket Realtime App",
         tag="Realtime that survives flaky mobile networks.",
         hi=["Transport decision table",
             "Replay from per-room sequence numbers",
             "Buffer limits and a 1,000-connection test"]),
    dict(slug="cli-tool-shipping", cat="Engineering", accent="#a3e635",
         title="CLI Tool Shipping",
         tag="Package and release a CLI people keep installed.",
         hi=["Exit codes scripts can branch on",
             "Golden-file tests on three operating systems",
             "Tagged release from CI, never a laptop"]),
    dict(slug="web-performance-audit", cat="Frontend", accent="#c084fc",
         title="Web Performance Audit",
         tag="Core Web Vitals passing on a mid-range Android.",
         hi=["Field p75 before any lab score",
             "Images, cache, fonts, JS, in that order",
             "Lighthouse CI that fails the build"]),
    dict(slug="browser-extension-build", cat="Frontend", accent="#60a5fa",
         title="Browser Extension Build",
         tag="A Manifest V3 extension that passes review first time.",
         hi=["Minimum permissions, exact host list",
             "Service worker with storage-backed state",
             "Review rejection causes designed out"]),
    dict(slug="cold-outreach-system", cat="Marketing", accent="#f97316",
         title="Cold Outreach System",
         tag="Outbound that gets replies without burning the domain.",
         hi=["Four touches, four angles, stop on reply",
             "SPF, DKIM, DMARC and a warmup ramp",
             "Reply rate per touch, not per campaign"]),
    dict(slug="launch-day-playbook", cat="Marketing", accent="#38bdf8",
         title="Launch Day Playbook",
         tag="One day of attention, planned before the day.",
         hi=["Ten-check readiness gate",
             "Channel plan with effort and return",
             "48-hour follow-up that keeps the list"]),
    dict(slug="freelance-client-pipeline", cat="Career", accent="#22d3ee",
         title="Freelance Client Pipeline",
         tag="Stop scrambling: five numbers that keep work coming.",
         hi=["Niche sentence and three case studies",
             "One-page proposal with three options",
             "GST, invoices and payment terms"]),
    dict(slug="gst-invoice-billing", cat="Finance", accent="#818cf8",
         title="GST Invoice And Billing",
         tag="Invoices that survive an accountant and an audit.",
         hi=["All sixteen mandatory particulars",
             "CGST and SGST versus IGST from place of supply",
             "Filing calendar and 72-month records"]),
    dict(slug="podcast-production", cat="Creative", accent="#fbbf24",
         title="Podcast Production",
         tag="An episode that sounds professional end to end.",
         hi=["-18 dBFS recording, -16 LUFS master",
             "Edit chain in the right order",
             "A feed you own, validated before submit"]),
    dict(slug="explainer-video-motion", cat="Creative", accent="#34d399",
         title="Explainer Video Motion",
         tag="A 60-second explainer that holds attention.",
         hi=["Script at 140-160 words, timed aloud",
             "Style sheet with one motion rule",
             "Captions plus per-platform exports"]),
    dict(slug="thumbnail-design-system", cat="Design", accent="#f472b6",
         title="Thumbnail Design System",
         tag="Thumbnails that earn the click at 120 pixels.",
         hi=["Three words, one subject, one accent",
             "Greyscale and 120 px legibility tests",
             "Three variants, swapped after 72 hours"]),
    dict(slug="pitch-deck-design", cat="Design", accent="#a3e635",
         title="Pitch Deck Design",
         tag="Eleven slides that end in a second meeting.",
         hi=["Five-beat narrative spine",
             "One claim per slide, source on every number",
             "QA at 25% zoom, greyscale and phone"]),
    dict(slug="postgres-index-tuning", cat="Data", accent="#c084fc",
         title="Postgres Index Tuning",
         tag="A 4-second query turned into a 40 ms index scan.",
         hi=["EXPLAIN with buffers before any index",
             "Composite order: equality, range, sort",
             "Concurrent build and unused-index audit"]),
    dict(slug="ab-test-analysis", cat="Data", accent="#60a5fa",
         title="A/B Test Analysis",
         tag="Read the test correctly and ship the right decision.",
         hi=["Sample size from the MDE",
             "SRM check before any analysis",
             "Interval first, p-value second"]),
    dict(slug="whatsapp-business-bot", cat="Automation", accent="#f97316",
         title="WhatsApp Business Bot",
         tag="A compliant WhatsApp bot for Indian customers.",
         hi=["Templates and the 24-hour window",
             "Webhook answers in 5 s, work queued",
             "Opt-in records and a human handoff"]),
    dict(slug="cron-monitoring", cat="Automation", accent="#38bdf8",
         title="Cron Monitoring",
         tag="Scheduled jobs that fail loudly instead of silently.",
         hi=["Inventory with owner and SLA",
             "Advisory locks and retry backoff",
             "Heartbeat dead-man switch"]),
    dict(slug="audiobook-mastering", cat="Creative", accent="#a855f7",
         title="Audiobook Mastering",
         tag="Record, clean and master an audiobook to a retail platform's technical spec - noise floor, loudness",
         hi=[
             "Fix the recording settings before fixing anything in software",
             "Edit for content before touching tone",
             "Measure before you process"]),
    dict(slug="comic-strip-from-script", cat="Creative", accent="#f472b6",
         title="Comic Strip From Script",
         tag="Turn a written script into a finished 4-8 panel comic strip - beat sheet, panel grid, balloon order",
         hi=[
             "Convert the script into beats before drawing",
             "Choose the grid from the rhythm, not from habit",
             "Thumbnail the eye path before drawing anything"]),
    dict(slug="motion-microinteractions", cat="Creative", accent="#fbbf24",
         title="Motion Microinteractions",
         tag="Specify UI motion with durations, easing and distances that feel deliberate",
         hi=[
             "Decide what motion is for",
             "Set five duration tokens and stop adding more",
             "Choose three easing curves with real values"]),
    dict(slug="product-photo-on-phone", cat="Creative", accent="#a855f7",
         title="Product Photo On Phone",
         tag="Shoot marketplace-ready product photos on a phone with a window, a sheet and two lamps",
         hi=[
             "Set the light before you touch the product",
             "Build the table and the background",
             "Compose the five frames every listing needs"]),
    dict(slug="screen-demo-recording", cat="Creative", accent="#f472b6",
         title="Screen Demo Recording",
         tag="Record a product demo that holds attention from the first second",
         hi=[
             "Write the outcome in one sentence",
             "Script it in beats",
             "Seed a believable environment"]),
    dict(slug="subtitle-sync-pipeline", cat="Creative", accent="#fbbf24",
         title="Subtitle Sync Pipeline",
         tag="Produce subtitles that are accurate, in sync and readable, with a timing pass",
         hi=[
             "Start from a clean transcript, not from auto-captions",
             "Segment by sentence, then split by reading speed",
             "Set timing from the audio, not from the model"]),
    dict(slug="accessible-form-validation", cat="Frontend", accent="#38bdf8",
         title="Accessible Form Validation",
         tag="Build a form whose errors are announced and focus lands on the right field",
         hi=[
             "Decide when each field validates",
             "Put the message in the DOM beside the field",
             "Write messages that name the fix"]),
    dict(slug="html-email-templates", cat="Frontend", accent="#60a5fa",
         title="HTML Email Templates",
         tag="Build one table-based email template that survives Outlook, Gmail and Apple Mail, with dark-mode rules",
         hi=[
             "Fix the layout constraints before writing markup",
             "Write markup that survives Word's renderer",
             "Decide the CSS delivery strategy"]),
    dict(slug="i18n-localization-pass", cat="Frontend", accent="#c084fc",
         title="i18n Localization Pass",
         tag="Take a working web app to a second language properly - extract every string, use ICU plurals",
         hi=[
             "Inventory every user-visible string",
             "Choose the library and the message format by constraint",
             "Extract strings without changing behaviour"]),
    dict(slug="multistep-form-wizard", cat="Frontend", accent="#38bdf8",
         title="Multi-Step Form Wizard",
         tag="Build a multi-step form that keeps state and validates at every step",
         hi=[
             "Decide the steps from the data, not the layout",
             "Keep one state object with a schema",
             "Validate on step exit, not on every keystroke"]),
    dict(slug="pwa-offline-sync", cat="Frontend", accent="#60a5fa",
         title="PWA Offline Sync",
         tag="Make a web app work on a bad connection - cache shell and data, queue writes in IndexedDB",
         hi=[
             "Decide what offline means for this app",
             "Register the service worker without breaking updates",
             "Cache the shell and the static assets precisely"]),
    dict(slug="virtualized-data-table", cat="Frontend", accent="#c084fc",
         title="Virtualized Data Table",
         tag="Render a 100,000-row table that scrolls at 60 fps - windowing, fixed row heights, server-side sort and filter",
         hi=[
             "Measure the table before changing it",
             "Decide windowing, pagination or server-side paging",
             "Fix the row height and the scroll container"]),
    dict(slug="api-rate-limiting", cat="Engineering", accent="#22d3ee",
         title="API Rate Limiting",
         tag="Rate-limit an HTTP API with cost-weighted token buckets in Redis",
         hi=[
             "Classify routes and assign a cost",
             "Choose the algorithm by burst behaviour",
             "Make the counter atomic"]),
    dict(slug="docker-image-slimdown", cat="Engineering", accent="#34d399",
         title="Docker Image Slimdown",
         tag="Cut a bloated container image to a small, non-root, reproducible build",
         hi=[
             "Measure before you cut",
             "Fix the base image first",
             "Split build from runtime"]),
    dict(slug="feature-flag-rollout", cat="Engineering", accent="#a3e635",
         title="Feature Flag Rollout",
         tag="Ship a change behind a flag and ramp it from 1 to 100 percent safely",
         hi=[
             "Inventory the flags you already have",
             "Pick the flag type before writing code",
             "Default off, evaluated at one boundary"]),
    dict(slug="flaky-test-triage", cat="Engineering", accent="#22d3ee",
         title="Flaky Test Triage",
         tag="Find flaky tests from rerun data, quarantine them with an owner",
         hi=[
             "Detect flakiness from data, not memory",
             "Quarantine without losing the gate",
             "Classify the cause into one of five buckets"]),
    dict(slug="typescript-strict-migration", cat="Engineering", accent="#34d399",
         title="TypeScript Strict Migration",
         tag="Convert a JavaScript or loosely typed codebase to strict TypeScript",
         hi=[
             "Measure the baseline you will ratchet against",
             "Separate type checking from emitting",
             "Convert files before turning on flags"]),
    dict(slug="email-lifecycle-flows", cat="Marketing", accent="#34d399",
         title="Email Lifecycle Flows",
         tag="Write and wire the five lifecycle emails that earn most of the revenue - welcome, activation, abandoned action",
         hi=[
             "Define the lifecycle states before writing copy",
             "Design the welcome flow as three emails, not one",
             "Write the abandoned-action flow"]),
    dict(slug="google-ads-waste-audit", cat="Marketing", accent="#a3e635",
         title="Google Ads Waste Audit",
         tag="Find the money leaking out of a Google Ads account in one afternoon - search terms with no conversion",
         hi=[
             "Pull the six reports before forming an opinion",
             "Verify the conversion tracking first",
             "Read the search terms report for the four waste patterns"]),
    dict(slug="influencer-outreach-kit", cat="Marketing", accent="#f97316",
         title="Influencer Outreach Kit",
         tag="Run a creator campaign end to end, from a qualified list to a rate card",
         hi=[
             "Fix the goal and the one deliverable",
             "Qualify the list before you write a single email",
             "Price from a rate card, not from the ask"]),
    dict(slug="local-seo-gbp", cat="Marketing", accent="#34d399",
         title="Local SEO For Google Business Profile",
         tag="Fix a Google Business Profile so a local business shows up in the map pack - categories, service area, photos",
         hi=[
             "Audit the profile fields that carry ranking weight",
             "Choose the category by testing, not by guessing",
             "Complete every field, including the boring ones"]),
    dict(slug="newsletter-growth-engine", cat="Marketing", accent="#a3e635",
         title="Newsletter Growth Engine",
         tag="Build a newsletter that grows from a real capture surface, not from luck",
         hi=[
             "Define one offer and one action",
             "Build three capture surfaces, not one",
             "Confirm consent and keep the record"]),
    dict(slug="review-request-funnel", cat="Marketing", accent="#f97316",
         title="Review Request Funnel",
         tag="Ask every happy customer for a public review at the right moment",
         hi=[
             "Find the moment satisfaction peaks",
             "Pick one channel and one ask",
             "Make the link one tap and the form short"]),
    dict(slug="anomaly-detection-alerts", cat="Data", accent="#fbbf24",
         title="Anomaly Detection Alerts",
         tag="Replace threshold alerts with seasonal baselines and a drift check",
         hi=[
             "Inventory the metrics and their natural cycles",
             "Build a seasonal baseline, not a moving average",
             "Use a stable spread and a defensible band"]),
    dict(slug="chart-design-system", cat="Data", accent="#f97316",
         title="Chart Design System",
         tag="Set chart rules that make dashboards readable: chart type, axes, colour, annotation",
         hi=[
             "List the questions, not the charts",
             "Choose the type from the question",
             "Fix the axes"]),
    dict(slug="cohort-retention-analysis", cat="Data", accent="#c084fc",
         title="Cohort Retention Analysis",
         tag="Build a cohort retention table in SQL and separate churn from mix",
         hi=[
             "Define two events in words before writing SQL",
             "Build the cohort table in SQL",
             "Choose the windows you will report"]),
    dict(slug="data-quality-contract", cat="Data", accent="#fbbf24",
         title="Data Quality Contract",
         tag="Write executable data contracts - schema, nulls, ranges, uniqueness and freshness",
         hi=[
             "List the tables and who depends on them",
             "Write the schema part of the contract",
             "Turn each declaration into an executable check"]),
    dict(slug="duckdb-analytics-warehouse", cat="Data", accent="#f97316",
         title="DuckDB Analytics Warehouse",
         tag="Query 10 GB of CSV and Parquet on one laptop with DuckDB - partitioned files, fast joins",
         hi=[
             "Size the data and the question before choosing the tool",
             "Land raw data once and never edit it",
             "Convert to Parquet, partitioned by the filter you actually use"]),
    dict(slug="receipt-ocr-pipeline", cat="Data", accent="#c084fc",
         title="Receipt OCR Pipeline",
         tag="Turn a folder of photographed receipts into a validated expense table, with confidence thresholds",
         hi=[
             "Define what a valid receipt is before parsing",
             "Preprocess the image before OCR",
             "Extract fields with confidence, not just text"]),
    dict(slug="backup-restore-drill", cat="Automation", accent="#c084fc",
         title="Backup Restore Drill",
         tag="Prove backups work by restoring them on a timer against a stated RPO and RTO",
         hi=[
             "Write the two numbers before touching a script",
             "Move the backup off the machine it protects",
             "Take the backup with a method that can be verified"]),
    dict(slug="document-signature-flow", cat="Automation", accent="#fbbf24",
         title="Document Signature Flow",
         tag="Send a contract for signature with a lawful e-signature flow",
         hi=[
             "Pick the signature type the law accepts",
             "Prepare one document, not three",
             "Order the signers and set the fields"]),
    dict(slug="inbox-triage-rules", cat="Automation", accent="#38bdf8",
         title="Inbox Triage Rules",
         tag="Turn a shared or personal inbox into a routed queue with owners",
         hi=[
             "Count what actually arrives",
             "Define five buckets and nothing more",
             "Write rules that label and archive, never delete"]),
    dict(slug="slack-ops-bot", cat="Automation", accent="#c084fc",
         title="Slack Ops Bot",
         tag="Build a Slack bot that carries alerts, deploys and approvals",
         hi=[
             "Define the three message types",
             "Route to the owning team, not to one channel",
             "One thread per incident, updated in place"]),
    dict(slug="webhook-retry-idempotency", cat="Automation", accent="#fbbf24",
         title="Webhook Retry And Idempotency",
         tag="Receive third-party webhooks without losing events or processing them twice, using signature checks, a durable queue",
         hi=[
             "Write down the delivery contract",
             "Verify the signature before reading the body",
             "Acknowledge fast and process later"]),
    dict(slug="zapier-to-n8n-migration", cat="Automation", accent="#38bdf8",
         title="Zapier To n8n Migration",
         tag="Move automations off a per-task billing tool onto a self-hosted workflow runner, one workflow at a time",
         hi=[
             "Inventory and price every workflow",
             "Stand up the runner before migrating anything",
             "Rebuild the simplest workflow first, end to end"]),
    dict(slug="agent-memory-design", cat="AI", accent="#818cf8",
         title="Agent Memory Design",
         tag="Give an agent memory that helps: three tiers with a write path and expiry",
         hi=[
             "Split memory into three tiers",
             "Write to durable memory only on an explicit signal",
             "Retrieve by entity and recency, not similarity alone"]),
    dict(slug="llm-eval-harness", cat="AI", accent="#22d3ee",
         title="LLM Eval Harness",
         tag="Build an evaluation harness for an LLM feature - a labelled set, deterministic scorers",
         hi=[
             "Write the decision the eval supports",
             "Build the set from real inputs, not from imagination",
             "Prefer a rule over a judge whenever a rule can decide"]),
    dict(slug="prompt-injection-guardrails", cat="AI", accent="#60a5fa",
         title="Prompt Injection Guardrails",
         tag="Harden an LLM feature against prompt injection",
         hi=[
             "Write the blast radius first",
             "Draw a trust boundary around data",
             "Constrain what the model can call"]),
    dict(slug="structured-output-extraction", cat="AI", accent="#818cf8",
         title="Structured Output Extraction",
         tag="Extract structured records from messy text with a schema-constrained LLM call plus validation",
         hi=[
             "Define the schema before writing a prompt",
             "Build a labelled set before the first prompt",
             "Constrain the call, do not request the format"]),
    dict(slug="first-90-days-plan", cat="Career", accent="#a3e635",
         title="First 90 Days Plan",
         tag="Write the 30/60/90 plan that turns a new job into a named deliverable",
         hi=[
             "Learn the mandate before the org chart",
             "Map stakeholders by what they need, not by seniority",
             "Ask the same 3 questions in every first conversation"]),
    dict(slug="interview-take-home", cat="Career", accent="#22d3ee",
         title="Interview Take Home",
         tag="Scope, timebox and ship a take-home assignment that reads as professional work",
         hi=[
             "Read the brief twice and write the acceptance list",
             "Timebox the work in fixed blocks",
             "Choose the smallest architecture you can defend"]),
    dict(slug="job-offer-comparison", cat="Career", accent="#f472b6",
         title="Job Offer Comparison",
         tag="Compare two or more job offers on take-home cash, equity that may never vest",
         hi=[
             "Get every offer in writing before comparing",
             "Compute take-home cash, not CTC",
             "Price the equity as a bet, not a number"]),
    dict(slug="performance-review-brief", cat="Career", accent="#a3e635",
         title="Performance Review Brief",
         tag="Build a review packet from evidence - impact statements with numbers, a brag log that is already written",
         hi=[
             "Start the impact log, even mid-year",
             "Turn entries into impact statements",
             "Get the next level's expectations in writing"]),
    dict(slug="portfolio-case-study", cat="Career", accent="#22d3ee",
         title="Portfolio Case Study",
         tag="Turn two or three real projects into portfolio case studies with problem, decision, measurement and proof",
         hi=[
             "Pick the projects by the decision they show",
             "Reconstruct the constraint with real numbers",
             "Write the decision, not the process"]),
    dict(slug="salary-negotiation-brief", cat="Career", accent="#f472b6",
         title="Salary Negotiation Brief",
         tag="Build the one-page brief that turns an offer conversation into a number you can defend, with the market band",
         hi=[
             "Build the band before the call",
             "Write the evidence column, not the wish",
             "Fix the three numbers before you speak"]),
    dict(slug="system-design-interview-drill", cat="Career", accent="#a3e635",
         title="System Design Interview Drill",
         tag="Run a timed 45-minute system design drill that ends with a scored answer",
         hi=[
             "Set up the drill so it cannot be cheated",
             "Spend the first 6 minutes on scope, not on boxes",
             "Draw the data model before the architecture"]),
    dict(slug="dark-mode-palette", cat="Design", accent="#f472b6",
         title="Dark Mode Palette",
         tag="Build a dark theme that passes contrast - separate surface tiers, desaturated accents, image and chart handling",
         hi=[
             "Audit the light palette before translating it",
             "Build surface tiers before choosing any text colour",
             "Set text colours by opacity and role"]),
    dict(slug="design-tokens-tailwind", cat="Design", accent="#c084fc",
         title="Design Tokens For Tailwind",
         tag="Turn a visual style into one token source that drives Tailwind classes, CSS variables and dark mode",
         hi=[
             "Separate the three token layers",
             "Author tokens as JSON, not as CSS",
             "Generate CSS variables for both themes"]),
    dict(slug="figma-variables-to-css", cat="Design", accent="#a3e635",
         title="Figma Variables To CSS",
         tag="Export Figma variables into the same JSON the frontend already uses",
         hi=[
             "Audit the Figma variable structure first",
             "Choose the export route",
             "Read variables through the plugin API"]),
    dict(slug="print-poster-layout", cat="Design", accent="#f472b6",
         title="Print Poster Layout",
         tag="Lay out a print poster that survives the press - correct bleed, a real grid",
         hi=[
             "Set the document up before anything is drawn",
             "Build a grid that can survive trimming",
             "Set type sizes for viewing distance"]),
    dict(slug="svg-icon-set", cat="Design", accent="#c084fc",
         title="SVG Icon Set",
         tag="Draw and ship a consistent icon set on a 24 px grid with one stroke weight",
         hi=[
             "Set the geometry rules before drawing",
             "Draw the anchor set of 8 first",
             "Build the 3 optical sizes"]),
    dict(slug="wireframe-to-spec", cat="Design", accent="#a3e635",
         title="Wireframe To Spec",
         tag="Turn a wireframe into a developer-ready spec - states, spacing, copy, edge cases and acceptance criteria",
         hi=[
             "Name the screen, the route and the job",
             "Break the wireframe into named regions",
             "Write every state, including the boring ones"]),
    dict(slug="capital-gains-workbook", cat="Finance", accent="#818cf8",
         title="Capital Gains Workbook",
         tag="Turn broker and registrar statements into a per-lot capital gains statement",
         hi=[
             "Collect every record before computing anything",
             "Classify every instrument first",
             "Compute the holding period from the dates"]),
    dict(slug="emi-prepayment-planner", cat="Finance", accent="#fbbf24",
         title="EMI Prepayment Planner",
         tag="Build a loan amortisation schedule you can reconcile to the lender's statement",
         hi=[
             "Fix the loan facts, including the ones lenders hide",
             "Build the schedule from first principles",
             "Reconcile against the lender's statement"]),
    dict(slug="expense-claim-audit", cat="Finance", accent="#34d399",
         title="Expense Claim Audit",
         tag="Audit a month of employee expense claims against written policy and produce a flagged register with the rupee amount",
         hi=[
             "Write the policy down before auditing against it",
             "Pull the claims and the policy into comparable shapes",
             "Run the duplicate check first, because it is the biggest"]),
    dict(slug="gst-2b-reconciliation", cat="Finance", accent="#818cf8",
         title="GST 2B Reconciliation",
         tag="Match GSTR-2B against your purchase register and ship a claim-ready ITC register where every exception has a rupee",
         hi=[
             "Freeze the period before you touch a file",
             "Normalise both files into one schema",
             "Match on three keys, not one"]),
    dict(slug="runway-cashflow-model", cat="Finance", accent="#fbbf24",
         title="Runway Cashflow Model",
         tag="Build a 12-month cashflow model that shows the month you run out of money, with the drivers",
         hi=[
             "Fix the opening balance to one number",
             "Model collections with the lag, not the invoice date",
             "Build spend as fixed, variable and lumpy"]),
    dict(slug="unit-economics-model", cat="Finance", accent="#34d399",
         title="Unit Economics Model",
         tag="Build a per-customer unit economics model with real cohort data - CAC, contribution margin, payback and LTV",
         hi=[
             "Define the customer and the period before any maths",
             "Pull one row per customer, not one row per order",
             "Split acquisition cost by channel, not in total"]),
    dict(slug="upi-reconciliation-sheet", cat="Finance", accent="#818cf8",
         title="UPI Reconciliation Sheet",
         tag="Match a month of UPI and bank credits to the invoices that caused them",
         hi=[
             "Freeze both datasets before matching",
             "Normalise the narration into usable fields",
             "Match in three passes, strictest first"]),
    dict(slug="xirr-sip-tracker", cat="Finance", accent="#fbbf24",
         title="XIRR SIP Tracker",
         tag="Turn a pile of SIP and lump-sum entries into one XIRR number per folio, with the cashflow export",
         hi=[
             "Collect the raw cashflows before any calculation",
             "Add the terminal value as a dated cashflow",
             "Compute XIRR with the right solver settings"]),
    dict(slug="academy-guide", cat="AI", accent="#818cf8",
         title="Academy Guide",
         tag="Stop and check this skill before finishing any reply to a question about how to use Claude or a Claude product — it recommends…",
         hi=["The catalog", "128 lines of procedure", "Worked examples and thresholds"]),
    dict(slug="algorithmic-art", cat="Frontend", accent="#38bdf8",
         title="Algorithmic Art",
         tag="Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request…",
         hi=["Algorithmic Philosophy Creation", "Deducing The Conceptual Seed", "P5.Js Implementation"]),
    dict(slug="canvas-design", cat="Design", accent="#c084fc",
         title="Canvas Design",
         tag="Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to…",
         hi=["Design Philosophy Creation", "Deducing The Subtle Reference", "Canvas Creation"]),
    dict(slug="claude-api", cat="AI", accent="#818cf8",
         title="Claude API",
         tag="Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token…",
         hi=["Before You Start", "Output Requirement", "Defaults"]),
    dict(slug="managed-agents-quickstarts", cat="AI", accent="#818cf8",
         title="Managed Agents Quickstarts",
         tag="Reads a codebase in parallel, takes a second look at every part, and reports only bugs a separate agent proved.",
         hi=["Agent.md", "Environment.yaml", "Session.yaml"]),
    dict(slug="managed-agents-quickstarts-anthropic-4", cat="AI", accent="#818cf8",
         title="Managed Agents Quickstarts Anthropic 4",
         tag="Turns a topic and your source material into a short captioned video with music, with an agent per scene.",
         hi=["Agent.md", "Environment.yaml", "Session.yaml"]),
    dict(slug="discernment-nudge", cat="Finance", accent="#818cf8",
         title="Discernment Nudge",
         tag="After you give a substantive answer or draft that the user may act on — advice or recommendations, drafted artifacts such as…",
         hi=["Why this exists", "When to offer the nudge", "When not to"]),
    dict(slug="doc-coauthoring", cat="Automation", accent="#c084fc",
         title="Doc Coauthoring",
         tag="Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals…",
         hi=["When to Offer This Workflow", "Context Gathering", "Refinement & Structure"]),
    dict(slug="docx", cat="Engineering", accent="#34d399",
         title="Docx",
         tag="this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx…",
         hi=["Creating with docx-js — gotchas", "Verify the output", "Editing existing documents"]),
    dict(slug="frontend-design", cat="Design", accent="#c084fc",
         title="Frontend Design",
         tag="Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic…",
         hi=["Ground your designs in the subject matter", "Design principles", "Process: plan, review against the brief, build, critique"]),
    dict(slug="mcp-builder", cat="AI", accent="#818cf8",
         title="Mcp Builder",
         tag="Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through…",
         hi=["Overview", "🚀 High-Level Workflow", "📚 Documentation Library"]),
    dict(slug="pdf", cat="Engineering", accent="#34d399",
         title="PDF",
         tag="this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs…",
         hi=["Overview", "Quick Start", "Python Libraries"]),
    dict(slug="pptx", cat="Automation", accent="#c084fc",
         title="Pptx",
         tag="this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide…",
         hi=["Creating with pptxgenjs — gotchas", "Editing existing decks and templates", "Deck content and flow"]),
    dict(slug="skill-creator", cat="Engineering", accent="#34d399",
         title="Skill Creator",
         tag="Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from…",
         hi=["Communicating with the user", "Creating a skill", "Report structure"]),
    dict(slug="slack-gif-creator", cat="Automation", accent="#c084fc",
         title="Slack Gif Creator",
         tag="Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation…",
         hi=["Slack Requirements", "Core Workflow", "Drawing Graphics"]),
    dict(slug="theme-factory", cat="Frontend", accent="#38bdf8",
         title="Theme Factory",
         tag="Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are…",
         hi=["Usage Instructions", "Themes Available", "Theme Details"]),
    dict(slug="web-artifacts-builder", cat="Frontend", accent="#38bdf8",
         title="Web Artifacts Builder",
         tag="Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React…",
         hi=["Design & Style Guidelines", "Quick Start", "Reference"]),
    dict(slug="webapp-testing", cat="Frontend", accent="#38bdf8",
         title="Webapp Testing",
         tag="Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality…",
         hi=["Decision Tree: Choosing Your Approach", "Example: Using withserver.py", "Reconnaissance-Then-Action Pattern"]),
    dict(slug="xlsx", cat="Data", accent="#f97316",
         title="Xlsx",
         tag="this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read…",
         hi=["Requirements for every output", "Recalculate (mandatory whenever the file contains formulas)", "Choosing formulas that survive verification"]),
    dict(slug="agent-ready", cat="AI", accent="#818cf8",
         title="Agent Ready",
         tag="Implements agent-readiness on public sites and docs from Mintlify Agent Score, AFDocs, Is Agentic, Is It Agent Ready, or…",
         hi=["Contents", "Workflow", "Reference files"]),
    dict(slug="agent-skills-creator", cat="AI", accent="#818cf8",
         title="Agent Skills Creator",
         tag="Creates and improves portable Agent Skills with a validator, routing scenarios, and evidence-based keep, cut, merge, or retire…",
         hi=["Choose a Mode", "Reference Files", "Creation Workflow"]),
    dict(slug="deploy-checklist", cat="Engineering", accent="#34d399",
         title="Deploy Checklist",
         tag="Walks through deploying the Orchard storefront to staging and production, including pre-deploy checks, the canary, monitoring…",
         hi=["Why deployment discipline matters", "What a deployment is", "Before you start"]),
    dict(slug="agents-md", cat="AI", accent="#818cf8",
         title="Agents Md",
         tag="Audits and edits agent instruction files, verifies repository commands, and migrates repositories to AGENTS.md as the single…",
         hi=["Choose a Mode", "Size Budget", "Reference Files"]),
    dict(slug="app-verification", cat="Data", accent="#f97316",
         title="App Verification",
         tag="Builds and maintains a repo's own verification harness (verify CLI, doctor, worktree isolation, feature map, seed data) and a…",
         hi=["Invocation", "Contents", "The harness contract"]),
    dict(slug="autoship", cat="Engineering", accent="#34d399",
         title="Autoship",
         tag="Runs a changesets npm release through the version PR, CI publish, and registry verification. Use when asked to \"release this…",
         hi=["The Release Loop", "Reference Files", "Intent Map"]),
    dict(slug="ax-audit", cat="AI", accent="#818cf8",
         title="Ax Audit",
         tag="Audits agentic products for tool parity, authority, approval payloads, recovery, and trust using 24 rules and a ship verdict. Use…",
         hi=["Contents", "Audit workflow", "Two rule layers"]),
    dict(slug="chat-history", cat="AI", accent="#818cf8",
         title="Chat History",
         tag="Recovers decisions, previous fixes, research, and what followed a prompt from past AI conversations, with source evidence. Use…",
         hi=["Workflow", "Execute the primitives", "Evidence and performance contracts"]),
    dict(slug="ci-speedup", cat="Engineering", accent="#34d399",
         title="CI Speedup",
         tag="Speeds up CI and the merge path: finds where changes wait between push and deploy, then fixes the critical path, check placement…",
         hi=["The Model", "Reference Files", "Workflow"]),
    dict(slug="codebase-architecture", cat="AI", accent="#818cf8",
         title="Codebase Architecture",
         tag="Designs module interfaces, deepens shallow modules, and installs enforceable repository guardrails and agent wayfinding. Use when…",
         hi=["Contents", "References", "Design mode (new codebase)"]),
    dict(slug="dx-audit", cat="Engineering", accent="#34d399",
         title="Dx Audit",
         tag="Audits libraries, CLIs, and SDKs using 38 rules for public contracts, package exports, piped output, errors, and configuration.…",
         hi=["Audit progress", "DX Audit", "Reference files"]),
    dict(slug="eli5", cat="Frontend", accent="#38bdf8",
         title="Eli5",
         tag="Picks the form that explains best and applies the house explanation style: plain prose, controlled English modelled on…",
         hi=["Pick the form", "Boundaries", "Maintenance"]),
    dict(slug="ghostwriter", cat="AI", accent="#818cf8",
         title="Ghostwriter",
         tag="Writes, rewrites, and critiques messages, posts, review comments, tickets, PRDs, design docs, talk scripts, docs, READMEs, and…",
         hi=["Done looks like", "The default", "Make a profile from samples"]),
    dict(slug="multi-tenant-architecture", cat="Engineering", accent="#34d399",
         title="Multi Tenant Architecture",
         tag="Designs tenant isolation, hostname routing, custom-domain lifecycle, and plan limits on Cloudflare or Vercel. Use when asked to…",
         hi=["Contents", "Platform dispatch (decide first)", "Reference files"]),
    dict(slug="planning", cat="Engineering", accent="#34d399",
         title="Planning",
         tag="Creates and reviews executable implementation plans grounded in repository evidence, with vertical slices, explicit decisions…",
         hi=["References", "Workflow", "Plan contract"]),
    dict(slug="pr-babysitter", cat="Engineering", accent="#34d399",
         title="Pr Babysitter",
         tag="Monitors or repairs an open GitHub PR: CI failures, conflicts, review threads, and merge readiness, reporting state changes. Use…",
         hi=["Mode Selection", "Reference Files", "Monitor Loop"]),
    dict(slug="pr-creator", cat="Engineering", accent="#34d399",
         title="Pr Creator",
         tag="Creates or updates GitHub PRs with house-style titles and bodies, issue linking, repository templates, and draft state. Use when…",
         hi=["Reference Files", "Workflow", "Anti-patterns: never write these"]),
    dict(slug="presentation-creator", cat="Engineering", accent="#34d399",
         title="Presentation Creator",
         tag="Builds decks with a story spine, house visual system, setting-specific density, and speaker notes. Use when asked to \"create a…",
         hi=["Workflow", "Related skills", "103 lines of procedure"]),
    dict(slug="product-design", cat="Design", accent="#c084fc",
         title="Product Design",
         tag="Specifies interaction choices, action scope, reversibility, recovery, and reachable states. Use when asked to \"design the flow\"…",
         hi=["Routing boundary", "Request modes", "Workflow"]),
    dict(slug="scaffold-cli", cat="Engineering", accent="#34d399",
         title="Scaffold CLI",
         tag="Scaffolds a TypeScript CLI and npm package with the house toolchain, dual tsdown outputs, CLI contracts, changesets, and…",
         hi=["Reference Files", "Scaffold Workflow", "Dependencies"]),
    dict(slug="scaffold-nextjs", cat="Engineering", accent="#34d399",
         title="Scaffold Nextjs",
         tag="Scaffolds a Next.js turborepo with Blode UI, icons, Ultracite (oxlint/shadcn), workspace hooks, and GitHub/Vercel setup. Use when…",
         hi=["Reference Files", "Scaffold Workflow", "Placeholder Reference"]),
    dict(slug="seo", cat="Marketing", accent="#34d399",
         title="SEO",
         tag="Audits and fixes technical SEO, researches search demand, creates content briefs, and measures SEO, AEO and GEO performance. Use…",
         hi=["Route the task", "Establish the evidence boundary", "Working sequence"]),
    dict(slug="test-audit", cat="Engineering", accent="#34d399",
         title="Test Audit",
         tag="Prunes low-value tests across a whole suite to a measured target while holding coverage. Use when asked to \"remove useless…",
         hi=["Pick a mode", "Set a target before starting", "Junk patterns"]),
    dict(slug="tidy", cat="Engineering", accent="#34d399",
         title="Tidy",
         tag="Reviews a local diff, branch diff, or PR with file:line findings in confirmed and plausible tiers, gates any test the diff adds…",
         hi=["Report or apply", "Harness precedence", "Mode dispatch"]),
    dict(slug="typography-audit", cat="Design", accent="#c084fc",
         title="Typography Audit",
         tag="Audits font loading, type scales, measure, spacing, OpenType, and rendered punctuation with 78 scoped rules. Use when asked to…",
         hi=["Audit Workflow", "Scoping Signals → Categories", "Rule Categories by Priority"]),
    dict(slug="ui-animation", cat="Creative", accent="#f472b6",
         title="UI Animation",
         tag="Builds, reviews, and measures UI motion, including springs, gestures, scroll effects, curve fitting from recordings, and sparse…",
         hi=["Reference files", "Core rules", "Motion design principles"]),
    dict(slug="ui-design", cat="Design", accent="#c084fc",
         title="UI Design",
         tag="Designs and builds React/Next/Tailwind UI, audits visual and interaction defects, and stress-tests components with worst-case…",
         hi=["Contents", "Existing brand and specs", "Direction mode"]),
    dict(slug="ui-verification", cat="Frontend", accent="#38bdf8",
         title="UI Verification",
         tag="Runs scoped browser probes for focus, hit targets, overflow, themes, request failures, and performance attribution, with evidence…",
         hi=["Contents", "When to run", "Probe catalogue"]),
    dict(slug="brainstorming", cat="Frontend", accent="#38bdf8",
         title="Brainstorming",
         tag="You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or…",
         hi=["First: What Do You Actually Know?", "Look Before You Ask", "Your First Message"]),
    dict(slug="dispatching-parallel-agents", cat="Engineering", accent="#34d399",
         title="Dispatching Parallel Agents",
         tag="Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies",
         hi=["Overview", "The Pattern", "Agent Prompt Structure"]),
    dict(slug="receiving-code-review", cat="Engineering", accent="#34d399",
         title="Receiving Code Review",
         tag="when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically…",
         hi=["Overview", "The Response Pattern", "Forbidden Responses"]),
    dict(slug="requesting-code-review", cat="Engineering", accent="#34d399",
         title="Requesting Code Review",
         tag="Use when completing tasks, implementing major features, or before merging to verify work meets requirements",
         hi=["When to Request Review", "How to Request", "Common Rationalizations"]),
    dict(slug="systematic-debugging", cat="Engineering", accent="#34d399",
         title="Systematic Debugging",
         tag="Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes",
         hi=["Overview", "The Iron Law", "The Four Phases"]),
    dict(slug="test-driven-development", cat="Engineering", accent="#34d399",
         title="Test Driven Development",
         tag="Use when implementing any feature or bugfix, before writing implementation code",
         hi=["Overview", "The Iron Law", "Red-Green-Refactor"]),
    dict(slug="using-superpowers", cat="Engineering", accent="#34d399",
         title="Using Superpowers",
         tag="when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including…",
         hi=["The Rule", "Skill Priority", "Red Flags"]),
    dict(slug="verification-before-completion", cat="Finance", accent="#818cf8",
         title="Verification Before Completion",
         tag="when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification…",
         hi=["Overview", "The Iron Law", "The Gate Function"]),
    dict(slug="writing-plans", cat="Engineering", accent="#34d399",
         title="Writing Plans",
         tag="Use when you have a spec or requirements for a multi-step task, before touching code",
         hi=["Overview", "Scope Check", "File Structure"]),
    dict(slug="writing-skills", cat="Creative", accent="#f472b6",
         title="Writing Skills",
         tag="Use when creating new skills, editing existing skills, or verifying skills work before deployment",
         hi=["Overview", "What is a Skill?", "TDD Mapping for Skills"]),
    dict(slug="artifacts-builder", cat="Frontend", accent="#38bdf8",
         title="Artifacts Builder",
         tag="Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React…",
         hi=["Design & Style Guidelines", "Quick Start", "Reference"]),
    dict(slug="changelog-generator", cat="Engineering", accent="#34d399",
         title="Changelog Generator",
         tag="Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming…",
         hi=["What This Skill Does", "How to Use", "✨ New Features"]),
    dict(slug="competitive-ads-extractor", cat="Marketing", accent="#34d399",
         title="Competitive Ads Extractor",
         tag="Extracts and analyzes competitors' ads from ad libraries (Facebook, LinkedIn, etc.) to understand what messaging, problems, and…",
         hi=["What This Skill Does", "How to Use", "Overview"]),
    dict(slug="abuselpdb-automation", cat="AI", accent="#818cf8",
         title="Abuselpdb Automation",
         tag="Automate Abuselpdb tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="accredible-certificates-automation", cat="AI", accent="#818cf8",
         title="Accredible Certificates Automation",
         tag="Automate Accredible Certificates tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="active-campaign-automation", cat="Marketing", accent="#34d399",
         title="Active Campaign Automation",
         tag="Automate ActiveCampaign tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="addresszen-automation", cat="AI", accent="#818cf8",
         title="Addresszen Automation",
         tag="Automate Addresszen tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="aero-workflow-automation", cat="Automation", accent="#c084fc",
         title="Aero Workflow Automation",
         tag="Automate Aero Workflow tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="aeroleads-automation", cat="AI", accent="#818cf8",
         title="Aeroleads Automation",
         tag="Automate Aeroleads tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
    dict(slug="agencyzoom-automation", cat="AI", accent="#818cf8",
         title="Agencyzoom Automation",
         tag="Automate Agencyzoom tasks via Rube MCP (Composio). Always search tools first for current schemas.",
         hi=["Prerequisites", "Tool Discovery", "Core Workflow Pattern"]),
]

def esc(s):
    return html.escape(s, quote=False)

def inline(t):
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t

def md2html(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"^\s*#\s+.*\n", "", md, count=1)
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(esc(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        if not s:
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            head = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = "<div class='tw'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            for r in rows:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table></div>")
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            n = len(m.group(1))
            txt = inline(m.group(2))
            anchor = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append(f"<h{n} id='{anchor}'>{txt}</h{n}>")
            i += 1
            continue
        if s.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(inline(lines[i].strip()[1:].strip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
            continue
        if s.startswith("- [ ] ") or s.startswith("- [x] "):
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- [ ] ") or lines[i].strip().startswith("- [x] ")):
                done = lines[i].strip().startswith("- [x] ")
                items.append(f"<li class='chk'><span class='box{' on' if done else ''}'></span>{inline(lines[i].strip()[6:])}</li>")
                i += 1
            out.append("<ul class='checks'>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^[-*]\s+", s):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append("<li>" + inline(re.sub(r"^[-*]\s+", "", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append("<li>" + inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if s.startswith("---"):
            out.append("<hr>")
            i += 1
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|\||>|```|---)", lines[i].strip()):
            buf.append(inline(lines[i].strip()))
            i += 1
        out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)

PROMPT = ("Read the skill at {url} and install it as a skill in your agent. "
          "Follow it exactly, including its checklists. Then ask me the questions it requires and do the work.")

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
 --bg:#07070b; --bg2:#0b0b12; --card:#111119; --card2:#16161f; --line:#232332;
 --tx:#f2f2f7; --mut:#9a9aad; --dim:#6e6e82;
 --brand:#7c5cff; --brand2:#22d3ee; --ok:#34d399;
 --max:1180px; --r:16px;
 --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,Helvetica,Arial,sans-serif;
 --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);font-family:var(--sans);
 font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background:
  radial-gradient(900px 500px at 12% -8%,rgba(124,92,255,.22),transparent 60%),
  radial-gradient(760px 420px at 92% 4%,rgba(34,211,238,.14),transparent 62%),
  radial-gradient(700px 500px at 50% 110%,rgba(124,92,255,.10),transparent 65%);}
.wrap{position:relative;z-index:1;max-width:var(--max);margin:0 auto;padding:0 22px}
a{color:inherit;text-decoration:none}
code{font-family:var(--mono);font-size:.86em;background:#ffffff0f;border:1px solid var(--line);
 padding:.12em .38em;border-radius:5px;color:#c7d2fe}
h1,h2,h3,h4{line-height:1.15;letter-spacing:-.022em;margin:0}
p{margin:0}
nav{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);
 background:rgba(7,7,11,.72);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;gap:18px;height:62px}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:-.02em}
.mark{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font-size:13px;
 font-weight:800;color:#0a0a12;background:linear-gradient(135deg,var(--brand),var(--brand2))}
nav .links{display:flex;gap:22px;margin-left:auto;font-size:14px;color:var(--mut)}
nav .links a:hover{color:var(--tx)}
.navcta{font-size:13.5px;font-weight:600;padding:8px 15px;border-radius:9px;
 border:1px solid var(--line);background:var(--card);color:var(--tx)}
.navcta:hover{border-color:#3a3a52;background:var(--card2)}
@media(max-width:720px){nav .links{display:none}}

header.hero{padding:82px 0 54px;text-align:center}
.badge{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;letter-spacing:.02em;
 color:#cfcaff;background:#7c5cff1f;border:1px solid #7c5cff40;padding:6px 13px;border-radius:999px;margin-bottom:22px}
.dot{width:6px;height:6px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 3px #34d39926}
h1.title{font-size:clamp(2.2rem,5.6vw,4.05rem);font-weight:800;letter-spacing:-.035em;max-width:20ch;margin:0 auto}
h1.title .grad{background:linear-gradient(105deg,#fff 12%,#b7a8ff 46%,#7de9ff 88%);
 -webkit-background-clip:text;background-clip:text;color:transparent}
.sub{max-width:64ch;margin:20px auto 0;color:var(--mut);font-size:clamp(1rem,1.5vw,1.12rem)}
.herobtns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:30px}
.btn{display:inline-flex;align-items:center;gap:9px;font-size:14.5px;font-weight:650;
 padding:12px 22px;border-radius:11px;border:1px solid transparent;cursor:pointer;transition:.16s;
 font-family:inherit}
.btn.p{background:linear-gradient(135deg,var(--brand),#5b8cff);color:#fff;box-shadow:0 10px 30px -12px #7c5cffaa}
.btn.p:hover{transform:translateY(-1px);box-shadow:0 14px 34px -12px #7c5cffcc}
.btn.s{background:var(--card);border-color:var(--line);color:var(--tx)}
.btn.s:hover{border-color:#3a3a52;background:var(--card2)}
.stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:44px}
.stat{background:linear-gradient(180deg,#14141d,#0e0e15);border:1px solid var(--line);
 border-radius:13px;padding:14px 22px;min-width:132px}
.stat b{display:block;font-size:1.42rem;letter-spacing:-.02em}
.stat span{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.08em}

section{padding:64px 0}
.shead{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:28px;flex-wrap:wrap}
.shead h2{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:750;letter-spacing:-.03em}
.shead p{color:var(--mut);font-size:14.5px;margin-top:8px}
.eyebrow{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:#9d8cff;font-weight:700;margin-bottom:10px}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
.card{position:relative;background:linear-gradient(180deg,#12121a,#0d0d14);border:1px solid var(--line);
 border-radius:var(--r);padding:22px 22px 18px;display:flex;flex-direction:column;transition:.18s;overflow:hidden}
.card::after{content:"";position:absolute;inset:0;border-radius:var(--r);pointer-events:none;
 background:radial-gradient(420px 180px at 88% -20%,var(--ac),transparent 70%);opacity:.13}
.card:hover{transform:translateY(-3px);border-color:#34344a}
.ctop{display:flex;align-items:center;gap:10px;margin-bottom:13px}
.cat{font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
 color:var(--ac);background:color-mix(in srgb,var(--ac) 13%,transparent);
 border:1px solid color-mix(in srgb,var(--ac) 30%,transparent);padding:3.5px 9px;border-radius:6px}
.num{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--dim)}
.card h3{font-size:1.16rem;font-weight:720;letter-spacing:-.02em;margin-bottom:8px}
.card .tag{color:var(--mut);font-size:14px;margin-bottom:15px}
.hi{list-style:none;padding:0;margin:0 0 18px;display:flex;flex-direction:column;gap:7px}
.hi li{position:relative;padding-left:18px;font-size:13.2px;color:#b8b8c8;line-height:1.45}
.hi li::before{content:"";position:absolute;left:2px;top:7px;width:5px;height:5px;border-radius:50%;
 background:var(--ac);opacity:.9}
.acts{margin-top:auto;display:flex;gap:8px;flex-wrap:wrap}
.mini{font-size:12.5px;font-weight:620;padding:8px 12px;border-radius:8px;border:1px solid var(--line);
 background:#ffffff08;color:#dcdce8;cursor:pointer;transition:.15s;font-family:inherit}
.mini:hover{background:#ffffff14;border-color:#3a3a52}
.mini.cp{border-color:color-mix(in srgb,var(--ac) 45%,transparent);
 color:var(--ac);background:color-mix(in srgb,var(--ac) 10%,transparent)}
.mini.cp:hover{background:color-mix(in srgb,var(--ac) 18%,transparent)}

.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.step{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
.step .n{font-family:var(--mono);font-size:12px;color:#9d8cff;margin-bottom:10px}
.step h3{font-size:1.02rem;margin-bottom:8px}
.step p{color:var(--mut);font-size:13.8px}
.panel{background:linear-gradient(180deg,#101018,#0b0b12);border:1px solid var(--line);
 border-radius:16px;padding:26px;margin-top:22px}
.panel h3{font-size:1.05rem;margin-bottom:6px}
.panel p.hint{color:var(--dim);font-size:13px;margin-bottom:14px}
pre.snip{background:#08080d;border:1px solid var(--line);border-radius:11px;padding:16px 18px;
 overflow-x:auto;font-family:var(--mono);font-size:12.6px;line-height:1.7;color:#c9d3f5;margin:0;white-space:pre-wrap}
.faq{display:grid;gap:10px}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:0 18px}
details[open]{border-color:#34344a}
summary{cursor:pointer;padding:16px 0;font-weight:620;font-size:14.6px;list-style:none;
 display:flex;justify-content:space-between;gap:14px;align-items:center}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--dim);font-size:18px;font-weight:400}
details[open] summary::after{content:"–"}
details .a{color:var(--mut);font-size:14px;padding:0 0 16px;max-width:75ch}
footer{border-top:1px solid var(--line);padding:38px 0 54px;margin-top:40px;color:var(--dim);font-size:13px}
footer .wrap{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;align-items:center}
footer a:hover{color:var(--tx)}

.toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,90px);opacity:0;z-index:200;
 background:#12121a;border:1px solid #34d39955;color:#d6ffe9;padding:12px 20px;border-radius:11px;
 font-size:13.5px;font-weight:600;transition:.22s;box-shadow:0 18px 40px -18px #000}
.toast.on{transform:translate(-50%,0);opacity:1}

/* skill page */
.doc{max-width:820px;margin:0 auto;padding:44px 0 70px}
.doc .back{font-size:13px;color:var(--mut);display:inline-block;margin-bottom:24px}
.doc .back:hover{color:var(--tx)}
.doc h1{font-size:clamp(1.9rem,4vw,2.7rem);font-weight:800;letter-spacing:-.032em;margin-bottom:10px}
.doc h2{font-size:1.42rem;font-weight:730;margin:44px 0 14px;padding-top:14px;border-top:1px solid var(--line)}
.doc h3{font-size:1.1rem;font-weight:700;margin:28px 0 10px;color:#e8e8f4}
.doc h4{font-size:1rem;margin:22px 0 8px;color:#d5d5e6}
.doc p{margin:12px 0;color:#c3c3d2}
.doc ul,.doc ol{margin:12px 0;padding-left:22px;color:#c3c3d2}
.doc li{margin:6px 0}
.doc strong{color:#fff}
.doc blockquote{margin:18px 0;padding:14px 18px;border-left:3px solid var(--brand);
 background:#7c5cff10;border-radius:0 10px 10px 0;color:#d8d8ea}
.doc blockquote p{margin:0;color:inherit}
.doc hr{border:0;border-top:1px solid var(--line);margin:34px 0}
.doc pre{background:#08080d;border:1px solid var(--line);border-radius:11px;padding:16px 18px;
 overflow-x:auto;font-family:var(--mono);font-size:12.8px;line-height:1.7;margin:16px 0;color:#c9d3f5}
.doc pre code{background:none;border:0;padding:0;font-size:inherit;color:inherit}
.tw{overflow-x:auto;margin:18px 0;border:1px solid var(--line);border-radius:11px}
.doc table{border-collapse:collapse;width:100%;font-size:13.4px;min-width:460px}
.doc th{text-align:left;padding:11px 14px;background:#15151f;color:#e6e6f2;font-weight:650;
 border-bottom:1px solid var(--line);white-space:nowrap}
.doc td{padding:11px 14px;border-bottom:1px solid #1b1b26;color:#bdbdcd;vertical-align:top}
.doc tr:last-child td{border-bottom:0}
.doc ul.checks{list-style:none;padding-left:0}
.doc ul.checks li.chk{display:flex;gap:10px;align-items:flex-start;padding-left:0}
.box{flex:0 0 15px;width:15px;height:15px;border:1.5px solid #4a4a60;border-radius:4px;margin-top:4px}
.box.on{background:var(--ok);border-color:var(--ok)}
.dochead{border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:8px}
.dochead .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
.dochead .tagline{color:var(--mut);font-size:15px;max-width:70ch}
.docacts{display:flex;gap:9px;flex-wrap:wrap;margin-top:20px}
.doccard{background:#101018;border:1px solid var(--line);border-radius:13px;padding:18px;
 margin:22px 0;display:flex;gap:16px;flex-wrap:wrap;align-items:center;justify-content:space-between}
.doccard .l b{display:block;font-size:13.5px;margin-bottom:3px}
.doccard .l span{font-size:12.5px;color:var(--dim)}
.urlbox{font-family:var(--mono);font-size:12.5px;color:#9d8cff;word-break:break-all}

/* ---------- 3D stage (transform/opacity only, no filters, no blur) ---------- */
.hero3d{display:grid;grid-template-columns:1fr 1.02fr;gap:28px;align-items:center;text-align:left}
.hero3d .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;max-width:392px;margin-top:32px}
.hero3d .stat{min-width:0;padding:12px 16px}
.hero3d .stat b{font-size:1.3rem}
@media(max-width:980px){.hero3d{grid-template-columns:1fr;text-align:center;gap:6px}
 .hero3d h1.title{margin:0 auto}.hero3d .sub{margin-left:auto;margin-right:auto}
 .hero3d .herobtns,.hero3d .stats{justify-content:center}}
.stage{position:relative;height:500px;perspective:1250px;perspective-origin:50% 46%;touch-action:pan-y}
.stage::before{content:"";position:absolute;left:4%;right:4%;top:16%;bottom:16%;border-radius:50%;
 background:radial-gradient(closest-side,rgba(124,92,255,.20),rgba(34,211,238,.06) 60%,transparent 72%)}
@media(max-width:1080px){.stage{height:420px}}
.ring{position:absolute;inset:0;transform-style:preserve-3d;animation:spin 34s linear infinite;will-change:transform}
.ring.b{animation:spinb 48s linear infinite}
@keyframes spin{from{transform:rotateY(0) rotateX(-8deg)}to{transform:rotateY(360deg) rotateX(-8deg)}}
@keyframes spinb{from{transform:rotateY(0) rotateX(10deg)}to{transform:rotateY(-360deg) rotateX(10deg)}}
.tile{position:absolute;top:50%;left:50%;width:126px;height:74px;margin:-37px 0 0 -63px;
 border-radius:13px;border:1px solid #ffffff1f;background:linear-gradient(160deg,#1b1b26,#0f0f17);
 display:flex;flex-direction:column;justify-content:center;gap:7px;padding:0 11px;
 backface-visibility:hidden}
.ring.b .tile{width:98px;height:60px;margin:-30px 0 0 -49px;border-radius:11px}
.ring.b .tile b{font-size:9px}
.tile b{font-size:10px;font-weight:640;letter-spacing:-.01em;color:#e6e6f2;line-height:1.3;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tile i{width:16px;height:2px;border-radius:2px;display:block;background:linear-gradient(90deg,#7c5cff,#22d3ee)}
.ring .tile{transform:rotateY(var(--a)) translateZ(var(--r))}
@media(max-width:760px){
 .stage{height:320px;perspective:900px}
 .ring.b{display:none}
 .ring .tile{width:96px;height:58px;margin:-29px 0 0 -48px}
 .ring .tile b{font-size:9px}}
@media(prefers-reduced-motion:reduce){
 .ring,.ring.b{animation:none}
 .ring{transform:rotateY(-20deg) rotateX(-7deg)}
 .ring.b{transform:rotateY(18deg) rotateX(8deg)}}

/* ---------- visible prompt box ---------- */
.pbox{margin-top:13px;border:1px solid var(--line);border-radius:10px;background:#0a0a11;
 padding:10px 12px;cursor:pointer;transition:.15s}
.pbox:hover{border-color:#3a3a52;background:#0d0d17}
.pbox .lbl{display:flex;justify-content:space-between;gap:8px;font-size:9.5px;letter-spacing:.12em;
 text-transform:uppercase;color:var(--dim);font-weight:700;margin-bottom:6px}
.pbox .lbl span{color:var(--ac,var(--brand))}
.pbox code{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;
 font-family:var(--mono);font-size:11.2px;line-height:1.55;color:#a7b2d4;background:none;border:0;padding:0}

/* ---------- scroll reveal ---------- */
.rv{opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .55s cubic-bezier(.2,.7,.3,1)}
.rv.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rv{opacity:1;transform:none;transition:none}}
.nojs .rv{opacity:1;transform:none}

/* ---------- developer credit + social links ---------- */
.dev{margin-top:24px;border:1px solid var(--line);border-radius:16px;padding:26px;
 background:linear-gradient(180deg,#111119,#0b0b12);display:grid;grid-template-columns:1fr auto;
 gap:24px;align-items:center}
.dev .who{display:flex;gap:14px;align-items:center}
.dev .av{width:48px;height:48px;border-radius:13px;display:grid;place-items:center;
 font-weight:800;font-size:19px;color:#0a0a12;background:linear-gradient(135deg,var(--brand),var(--brand2))}
.dev h3{font-size:1.06rem;font-weight:720;letter-spacing:-.02em}
.dev p{color:var(--mut);font-size:13.4px;margin-top:5px;max-width:52ch}
.socials{display:flex;gap:9px;flex-wrap:wrap}
.soc{display:flex;align-items:center;gap:9px;padding:9px 14px;border:1px solid var(--line);
 border-radius:10px;background:#ffffff08;font-size:12.8px;font-weight:620;color:#dcdce8;
 transition:.15s;white-space:nowrap}
.soc:hover{border-color:#3a3a52;background:#ffffff14;transform:translateY(-1px)}
.soc svg{width:15px;height:15px;fill:currentColor;opacity:.92;flex:0 0 auto}
.soc small{color:var(--dim);font-weight:500;font-size:11.5px}
@media(max-width:860px){.dev{grid-template-columns:1fr}}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--line);padding:40px 0 44px;margin-top:44px;color:var(--dim);font-size:13px}
footer .cols{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:28px;padding-bottom:26px;
 border-bottom:1px solid var(--line)}
footer h4{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);
 margin:0 0 12px;font-weight:700}
footer ul{list-style:none;padding:0;margin:0;display:grid;gap:9px;font-size:13.2px}
footer ul a{color:#b6b6c6}
footer ul a:hover{color:var(--tx)}
footer .brandblk{display:flex;gap:12px;align-items:flex-start}
footer .fmark{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;
 font-weight:800;font-size:13px;color:#0a0a12;background:linear-gradient(135deg,var(--brand),var(--brand2));flex:0 0 auto}
footer .bott{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;padding-top:18px;font-size:12.4px}
footer .bott a:hover{color:var(--tx)}
@media(max-width:820px){footer .cols{grid-template-columns:1fr 1fr;gap:22px}}

/* ---------- legal pages ---------- */
.doc .updated{font-size:12.5px;color:var(--dim);margin-top:6px;font-family:var(--mono)}
.doc .lede{font-size:15.5px;color:#cfcfdd;border-left:2px solid var(--brand);padding-left:14px;margin:18px 0 26px}
"""

JS = """
document.documentElement.classList.remove('nojs');
function copyText(t, msg){
  const done=()=>{const el=document.getElementById('toast');
    el.textContent=msg||'Copied to clipboard';el.classList.add('on');
    clearTimeout(window.__t);window.__t=setTimeout(()=>el.classList.remove('on'),2200);};
  if(navigator.clipboard && window.isSecureContext){
    navigator.clipboard.writeText(t).then(done).catch(fallback);
  } else { fallback(); }
  function fallback(){
    const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';
    ta.style.opacity='0';document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy');done();}catch(e){prompt('Copy this prompt:',t);}
    document.body.removeChild(ta);
  }
}

/* one delegated listener for every copy control on the page */
document.addEventListener('click', function(e){
  var el = e.target.closest('[data-p],[data-c]');
  if(!el) return;
  e.preventDefault();
  var t = el.getAttribute('data-p') || el.getAttribute('data-c');
  if(!t) return;
  copyText(t, el.hasAttribute('data-p') ? 'Install prompt copied' : 'URL copied');
});

/* keyboard activation for the prompt boxes */
document.addEventListener('keydown', function(e){
  if(e.key !== 'Enter' && e.key !== ' ') return;
  var el = e.target.closest('[data-p],[data-c]');
  if(!el || el.tagName === 'BUTTON') return;
  e.preventDefault();
  var t = el.getAttribute('data-p') || el.getAttribute('data-c');
  if(t) copyText(t, 'Copied to clipboard');
});

/* scroll reveal */
(function(){
  var nodes = document.querySelectorAll('.rv');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!('IntersectionObserver' in window) || reduce){
    for(var i=0;i<nodes.length;i++) nodes[i].classList.add('in');
    return;
  }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, {rootMargin:'0px 0px -50px 0px'});
  for(var j=0;j<nodes.length;j++) io.observe(nodes[j]);
})();

/* pointer tilt: desktop with a fine pointer only, rAF-throttled */
(function(){
  if(!window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var raf = null, cur = null;
  document.querySelectorAll('.card').forEach(function(card){
    card.addEventListener('pointermove', function(e){
      cur = {el:card, x:e.clientX, y:e.clientY};
      if(raf) return;
      raf = requestAnimationFrame(function(){
        raf = null;
        if(!cur) return;
        var r = cur.el.getBoundingClientRect();
        var px = (cur.x - r.left) / r.width - .5;
        var py = (cur.y - r.top) / r.height - .5;
        cur.el.style.transform = 'perspective(900px) rotateX(' + (-py*4.5).toFixed(2) +
          'deg) rotateY(' + (px*4.5).toFixed(2) + 'deg) translateY(-3px)';
      });
    });
    card.addEventListener('pointerleave', function(){ card.style.transform = ''; });
  });
})();
"""

VERIFY = '<meta name="google-site-verification" content="tMhCBaMY8rxKG1oI79L7en-ncRHKgykYXxysMzd6KzM" />'
OG_IMAGE = "/og.png"

def ld(obj):
    """Serialise one JSON-LD graph as a script tag."""
    return ('<script type="application/ld+json">'
            + json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "</script>")

PERSON_LD = {
    "@type": "Person", "@id": BASE + "/#author", "name": "Error",
    "url": "https://github.com/ERROR0101r/",
    "sameAs": ["https://github.com/ERROR0101r/",
               "https://t.me/aab_ho_ga_comeback",
               "https://t.me/Hacking_with_ERROR_group",
               "https://www.instagram.com/fahad0101r"],
}

def site_ld():
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "Skill Vault",
         "description": "Free, detailed, MIT-licensed skills that install into Claude, Copilot, Cursor "
                        "or any AI agent with one prompt and a URL.",
         "inLanguage": "en", "publisher": {"@id": BASE + "/#author"},
         "license": "https://opensource.org/licenses/MIT"},
        PERSON_LD,
    ]}

def article_ld(title, desc, url):
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "TechArticle", "headline": title, "description": desc,
         "url": url, "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "datePublished": "2026-11-15", "dateModified": "2026-11-15",
         "inLanguage": "en", "isAccessibleForFree": True,
         "license": "https://opensource.org/licenses/MIT",
         "image": BASE + OG_IMAGE,
         "author": {"@id": BASE + "/#author"},
         "publisher": {"@id": BASE + "/#author"},
         "isPartOf": {"@id": BASE + "/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "All skills", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": url}]},
    ]}

def page_ld(title, desc, url):
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "description": desc, "url": url,
         "inLanguage": "en", "isPartOf": {"@id": BASE + "/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "All skills", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": url}]},
    ]}

def head(title, desc, canonical="", jsonld="", og_type="website", noindex=False, extra=""):
    canon = canonical or (BASE + "/")
    robots = "noindex,nofollow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1"
    ld_tags = ld(jsonld) if isinstance(jsonld, dict) else (jsonld or "")
    return f"""<!doctype html>
<html lang="en" class="nojs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
{VERIFY}
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#07070b">
<meta name="author" content="Error">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Skill Vault">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}{OG_IMAGE}">
<link rel="alternate" type="application/json" href="/skills.json" title="Skill manifest">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%237c5cff'/><text x='16' y='22' font-size='16' font-family='monospace' fill='%2307070b' text-anchor='middle'>S</text></svg>">
<style>{CSS}</style>
{ld_tags}
{extra}
</head>
<body>
<nav><div class="wrap">
  <a class="logo" href="/"><span class="mark">S</span> Skill Vault</a>
  <div class="links">
    <a href="/#skills">Skills</a>
    <a href="/#install">How to install</a>
    <a href="/#use">Use cases</a>
    <a href="/#faq">FAQ</a>
  </div>
  <a class="navcta" href="/skills.json">skills.json</a>
</div></nav>
"""

SOCIALS = [
    ("Telegram channel", "@aab_ho_ga_comeback", "https://t.me/aab_ho_ga_comeback",
     '<svg viewBox="0 0 24 24"><path d="M21.9 4.3 18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1L18 6.7c.4-.4-.1-.6-.6-.2L6.5 13.3l-4.9-1.5c-1.1-.3-1.1-1.1.2-1.6L20.4 2.8c.9-.3 1.7.2 1.5 1.5Z"/></svg>'),
    ("Telegram group", "Hacking with ERROR", "https://t.me/Hacking_with_ERROR_group",
     '<svg viewBox="0 0 24 24"><path d="M21.9 4.3 18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1L18 6.7c.4-.4-.1-.6-.6-.2L6.5 13.3l-4.9-1.5c-1.1-.3-1.1-1.1.2-1.6L20.4 2.8c.9-.3 1.7.2 1.5 1.5Z"/></svg>'),
    ("GitHub", "ERROR0101r", "https://github.com/ERROR0101r/",
     '<svg viewBox="0 0 24 24"><path d="M12 .5A11.5 11.5 0 0 0 .5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.1.1 1.7 1.1 1.7 1.1 1 1.7 2.7 1.2 3.3.9.1-.7.4-1.2.7-1.5-2.6-.3-5.3-1.3-5.3-5.8 0-1.3.5-2.3 1.2-3.2-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.1 18.3 4.4 18.3 4.4c.6 1.6.2 2.8.1 3.1.8.9 1.2 1.9 1.2 3.2 0 4.5-2.7 5.5-5.3 5.8.4.4.8 1.1.8 2.2v3.3c0 .4.2.7.8.6A11.5 11.5 0 0 0 12 .5Z"/></svg>'),
    ("Instagram", "@fahad0101r", "https://www.instagram.com/fahad0101r?dlrf=MWVrd2hoZXBuZHk0cw==",
     '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 1.8.3 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.3 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.8-.3-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.3-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2Zm0 3.2A6.6 6.6 0 1 0 18.6 12 6.6 6.6 0 0 0 12 5.4Zm0 10.9A4.3 4.3 0 1 1 16.3 12 4.3 4.3 0 0 1 12 16.3Zm6.9-11.1a1.5 1.5 0 1 1-1.5-1.5 1.5 1.5 0 0 1 1.5 1.5Z"/></svg>'),
]

N = len(META)

_LEGAL_LINKS = "".join(
    f'<li><a href="/{s}.html">{label}</a></li>' for s, label in
    [("terms", "Terms of Use"), ("privacy", "Privacy Policy"),
     ("disclaimer", "Disclaimer"), ("license", "Licensing &amp; MIT")])

_SOC_FOOT = "".join(
    f'<li><a href="{url}" target="_blank" rel="noopener noreferrer me">{label}</a></li>'
    for label, _h, url, _svg in SOCIALS)

FOOT = f"""
<footer><div class="wrap">
  <div class="cols">
    <div>
      <div class="brandblk">
        <span class="fmark">S</span>
        <div>
          <div style="color:var(--tx);font-weight:700;font-size:14px">Skill Vault</div>
          <div style="font-size:12.6px;margin-top:3px">{N} installable agent skills. Free to use, MIT licensed.</div>
          <div style="font-size:12.6px;margin-top:8px">Developed by <strong style="color:var(--tx)">Error</strong></div>
        </div>
      </div>
    </div>
    <div><h4>Skills</h4><ul>
      <li><a href="/#skills">All skills</a></li>
      <li><a href="/#install">How to install</a></li>
      <li><a href="/skills.json">skills.json</a></li>
      <li><a href="/llms.txt">llms.txt</a></li>
    </ul></div>
    <div><h4>Legal</h4><ul>{_LEGAL_LINKS}</ul></div>
    <div><h4>Connect</h4><ul>{_SOC_FOOT}</ul></div>
  </div>
  <div class="bott">
    <div>&copy; 2026 Skill Vault. Skill files MIT licensed. Built and maintained by Error.</div>
    <div><a href="/sitemap.xml">Sitemap</a> · <a href="/#faq">FAQ</a> · <a href="/terms.html">Terms</a></div>
  </div>
</div></footer>
<div class="toast" id="toast">Copied</div>
<script>%s</script>
</body>
</html>""" % JS

LEGAL_PAGES = ["terms", "privacy", "disclaimer", "license"]

_UPDATED = "15 November 2026"
_CONTACT = ('<a href="https://t.me/aab_ho_ga_comeback" target="_blank" rel="noopener noreferrer">'
            'Telegram channel</a> or <a href="https://github.com/ERROR0101r/" target="_blank" '
            'rel="noopener noreferrer">GitHub</a>')

LEGAL = {}

LEGAL["terms"] = ("Terms of Use",
 "The rules for using Skill Vault: licence, acceptable use, warranty and liability.",
 """
 <p class="lede">These terms govern your use of Skill Vault. By opening this site or using any
 skill file from it, you agree to them. If you do not agree, please do not use the site.</p>

 <h2>1. What Skill Vault is</h2>
 <p>Skill Vault is a free, static library of markdown files that instruct AI agents how to perform a
 task. There is no account, no subscription and no payment. The files are instructions for software
 you run yourself; the site does not execute them and does not control what your agent does with them.</p>

 <h2>2. Licence to use</h2>
 <p>Every skill file is released under the <strong>MIT Licence</strong> (full text on the
 <a href="/license.html">Licensing page</a>). You may use, copy, modify and redistribute them,
 including commercially, provided the copyright notice is kept.</p>
 <p>The site's design, name, wordmark and logo are &copy; 2026 Error and are not licensed for reuse as
 your own brand. You may link to the site freely.</p>

 <h2>3. Acceptable use</h2>
 <p>You agree not to use the skills or the site to break the law, to harm or defraud anyone, to
 infringe someone's rights, or to violate the terms of a third-party service. Several skills describe
 work with legal limits — scraping, personal data, security testing, hiring, finance. Those sections are
 part of the skill and are not optional.</p>
 <p>You are responsible for what your agent does with a skill. Running a skill against a system you do
 not own or have permission to test may be a criminal offence.</p>

 <h2>4. No warranty</h2>
 <p>The site and every skill are provided <strong>"as is", without warranty of any kind</strong>,
 express or implied, including merchantability, fitness for a particular purpose and non-infringement.
 No guarantee is given that a skill is accurate, current, complete, or that it will produce any
 particular result. AI systems produce wrong output; a skill reduces that risk and does not remove it.</p>

 <h2>5. Limitation of liability</h2>
 <p>To the maximum extent permitted by law, Error and Skill Vault are not liable for any indirect,
 incidental, special or consequential loss, or for lost profits, lost data, business interruption,
 account suspension, or damage arising from your use of the site or any skill.</p>

 <h2>6. Third-party links and tools</h2>
 <p>The site links to Telegram, GitHub and Instagram, and skills name third-party tools. Those services
 are not affiliated with Skill Vault, and their own terms and privacy policies apply once you use them.
 Listing a tool is not an endorsement.</p>

 <h2>7. Availability and changes</h2>
 <p>The site may change, break or be withdrawn at any time without notice. These terms may be updated;
 the date at the top of this page is the current version. Continuing to use the site after a change
 means you accept the updated terms.</p>

 <h2>8. Governing law</h2>
 <p>These terms are governed by the laws of India, and disputes are subject to the jurisdiction of the
 courts of India.</p>

 <h2>9. Contact</h2>
 <p>Questions about these terms: """ + _CONTACT + """.</p>
 """)

LEGAL["privacy"] = ("Privacy Policy",
 "What Skill Vault does and does not collect. Short version: no accounts, no tracking, no ads.",
 """
 <p class="lede">Skill Vault is a static website. There are no accounts, no sign-up, no analytics and
 no advertising. This page explains the small amount of data that does exist and why.</p>

 <h2>1. What this site does not collect</h2>
 <ul>
   <li>No accounts, names, email addresses or phone numbers.</li>
   <li>No newsletter or contact form — there is no form on this site.</li>
   <li>No analytics, no tracking pixels, no advertising or retargeting.</li>
   <li>No profiling, no selling or sharing of data with advertisers.</li>
 </ul>

 <h2>2. What is processed when you visit</h2>
 <p>The site is served by Cloudflare Pages, which processes standard request data to deliver pages and
 protect the service: IP address, user agent, requested path, timestamp and coarse location. This is
 used for delivery, security and abuse prevention, and is retained under Cloudflare's own policies.
 Skill Vault does not receive or store this as a profile of you.</p>

 <h2>3. Cookies and local storage</h2>
 <p>This site sets <strong>no cookies</strong> and writes nothing to your browser's local storage.
 The copy buttons use the browser clipboard API only when you click them, and nothing is transmitted
 anywhere when you do.</p>

 <h2>4. Third-party services</h2>
 <p>Outbound links go to Telegram, GitHub and Instagram. Once you follow one, that platform's terms and
 privacy policy apply and Skill Vault has no control over what it collects. No third-party scripts,
 embeds or trackers are loaded on this site.</p>

 <h2>5. If you contact us</h2>
 <p>If you message the developer on Telegram or GitHub, that platform holds the conversation and Skill
 Vault sees only what you send. Do not send secrets, credentials or personal documents through those
 channels.</p>

 <h2>6. Children</h2>
 <p>The site is written for professional and adult use and is not directed at children under 13.
 No personal data is knowingly collected from anyone.</p>

 <h2>7. Your rights</h2>
 <p>Because Skill Vault stores no personal data, there is no profile to export, correct or delete.
 For request logs held by the hosting provider, contact the developer and it will be raised with the
 provider on your behalf.</p>

 <h2>8. Changes</h2>
 <p>If this policy changes, the date at the top of the page changes with it.</p>

 <h2>9. Contact</h2>
 <p>Privacy questions: """ + _CONTACT + """.</p>
 """)

LEGAL["disclaimer"] = ("Disclaimer",
 "Skills are procedures, not guarantees. Read this before acting on anything here.",
 """
 <p class="lede">Every skill on this site is a procedure written for an AI agent to follow. It is
 guidance from experience, not a promise of an outcome. Read this page before you rely on one.</p>

 <h2>1. Informational and educational use</h2>
 <p>The content is published to teach a workflow. It is not tailored to your situation, your data,
 your jurisdiction or your risk tolerance.</p>

 <h2>2. Not professional advice</h2>
 <p>Nothing here is legal, financial, tax, medical or security advice. Skills that touch contracts,
 invoicing, hiring, health, trading or compliance describe a method; they do not replace a qualified
 professional. For anything consequential, consult a licensed practitioner in your jurisdiction.</p>

 <h2>3. AI agents can be wrong</h2>
 <p>Models hallucinate. A skill that tells an agent to verify its own output is doing that because the
 failure is real and common. Check code before shipping it, check numbers before sending them, and
 check any legal or medical text before anyone relies on it.</p>

 <h2>4. No guarantee of results</h2>
 <p>Where a skill mentions a figure — a conversion lift, a ranking improvement, a latency budget, a
 cost saving — it is an illustrative target or a typical range, not a forecast for your project.</p>

 <h2>5. Third-party tools and trademarks</h2>
 <p>Product and company names are used for identification only. No affiliation, sponsorship or
 endorsement is implied in either direction.</p>

 <h2>6. Security work</h2>
 <p>Skills that cover security testing are for systems you own or have <strong>written authorisation</strong>
 to test. Unauthorised access or interference with a computer system is a criminal offence in India
 under the Information Technology Act, 2000, and under equivalent laws elsewhere. A lab, a range or
 written permission — never a live third-party system.</p>

 <h2>7. Use at your own risk</h2>
 <p>You are responsible for the cost, data loss, account suspension or other consequence of running a
 skill. Where a skill conflicts with a third-party service's terms, those terms win.</p>

 <h2>8. Contact</h2>
 <p>Spotted something wrong or unsafe in a skill: """ + _CONTACT + """.</p>
 """)

LEGAL["license"] = ("Licensing &amp; MIT",
 "Skill files are MIT licensed. Use them, change them, ship them — keep the notice.",
 """
 <p class="lede">Everything you download from Skill Vault is free to use, including commercially. This
 page states exactly what is licensed and how.</p>

 <h2>1. Skill files — MIT</h2>
 <p>Every <code>skills/&lt;slug&gt;.md</code> file, and the JSON and text manifests
 (<code>skills.json</code>, <code>status.json</code>, <code>llms.txt</code>), are released under the MIT
 Licence below. You may use, copy, modify, merge, publish, distribute, sublicense and sell copies,
 provided the copyright notice and permission notice are included.</p>

 <h2>2. Site code</h2>
 <p>The generator that builds this site is also MIT licensed and public:
 <a href="https://github.com/mfm965204-cell/ai-skills-vault-source" target="_blank" rel="noopener noreferrer">ai-skills-vault-source</a>.
 Fork it and run your own vault.</p>

 <h2>3. Brand</h2>
 <p>The name "Skill Vault", the wordmark and the logo are &copy; 2026 Error. The MIT licence does not
 grant rights to them. If you republish the skills, use your own name and branding.</p>

 <h2>4. Attribution</h2>
 <p>Not required by the licence, but a link back to
 <a href="https://ai-skills-vault.pages.dev/">ai-skills-vault.pages.dev</a> is appreciated and keeps the
 library growing.</p>

 <h2>5. Contributions</h2>
 <p>If you send a skill, a fix or a suggestion, you agree it may be published here under the MIT
 Licence.</p>

 <h2>6. MIT Licence</h2>
 <pre>MIT License

Copyright (c) 2026 Error — Skill Vault

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.</pre>
 """)


def build_og():
    """1200x630 social card, drawn once at build time."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#07070b")
    d = ImageDraw.Draw(img, "RGBA")
    for cx, cy, r, col in [(180, 60, 520, (124, 92, 255, 46)), (1040, 90, 420, (34, 211, 238, 34)),
                           (600, 700, 520, (124, 92, 255, 26))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    def font(sz, bold=True):
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
                  else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            try: return ImageFont.truetype(p, sz)
            except Exception: continue
        return ImageFont.load_default()
    # monogram
    d.rounded_rectangle([80, 76, 148, 144], radius=18, fill=(124, 92, 255))
    d.text((99, 92), "S", font=font(40), fill="#07070b")
    d.text((166, 100), "Skill Vault", font=font(30), fill="#f2f2f7")
    d.text((80, 208), "Skills that make", font=font(64), fill="#ffffff")
    d.text((80, 282), "your AI agent", font=font(64), fill="#ffffff")
    d.text((80, 356), "actually useful", font=font(64), fill="#9d8cff")
    d.text((82, 452), f"{len(META)} detailed, free skills — one-prompt install from a URL.",
           font=font(28, False), fill="#9a9aad")
    d.line([80, 512, 1120, 512], fill=(255, 255, 255, 26), width=1)
    d.text((82, 536), "Claude · Copilot · Cursor · Codex · any agent", font=font(22, False), fill="#6e6e82")
    d.text((830, 536), "Developed by Error", font=font(22), fill="#c7c7d6")
    img.save(ROOT / "og.png", "PNG", optimize=True)
    return True

def build_legal():
    """Render terms, privacy, disclaimer and licence from the content above."""
    for slug in LEGAL_PAGES:
        title, desc, body = LEGAL[slug]
        page = head(f"{title} — Skill Vault", desc,
                canonical=f"{BASE}/{slug}.html",
                jsonld=page_ld(title, desc, f"{BASE}/{slug}.html")) + f"""
<div class="wrap"><div class="doc">
  <a class="back" href="/">← All skills</a>
  <h1>{title}</h1>
  <p class="updated">Last updated: {_UPDATED} · Developed by Error</p>
  {body}
  <hr>
  <p style="font-size:13.5px;color:var(--dim)">Skill Vault is free and MIT licensed. Other pages:
  <a href="/terms.html">Terms</a> · <a href="/privacy.html">Privacy</a> ·
  <a href="/disclaimer.html">Disclaimer</a> · <a href="/license.html">Licensing</a></p>
</div></div>
""" + FOOT
        (ROOT / f"{slug}.html").write_text(page, encoding="utf-8")

def build_index():
    cards = []
    for i, m in enumerate(META, 1):
        url = f"{BASE}/skills/{m['slug']}.md"
        prompt = PROMPT.format(url=url)
        cards.append(f"""
    <article class="card rv" style="--ac:{m['accent']}">
      <div class="ctop"><span class="cat">{esc(m['cat'])}</span><span class="num">{i:02d}</span></div>
      <h3>{esc(m['title'])}</h3>
      <p class="tag">{esc(m['tag'])}</p>
      <ul class="hi">{''.join(f'<li>{esc(h)}</li>' for h in m['hi'])}</ul>
      <div class="acts">
        <button class="mini cp" data-p="{html.escape(prompt, quote=True)}">Copy install prompt</button>
        <a class="mini" href="/skills/{m['slug']}.html">Read skill</a>
        <a class="mini" href="/skills/{m['slug']}.md" download>Download .md</a>
      </div>
      <div class="pbox" data-p="{html.escape(prompt, quote=True)}" role="button" tabindex="0"
           aria-label="Copy the install prompt for {esc(m['title'])}">
        <div class="lbl">Install prompt <span>tap to copy</span></div>
        <code>{esc(prompt)}</code>
      </div>
    </article>""")
    cards = "\n".join(cards)

    n = len(META)
    total_lines = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in SK.glob("*.md"))

    all_prompt = ("Read all " + str(n) + " skills in the Skill Vault manifest at " + BASE + "/skills.json "
                  "(raw markdown for each is at " + BASE + "/skills/<slug>.md). Install them as skills in your agent. "
                  "Then list what each one does and ask me which to run first.")

    ring_a = ["3D on Phone", "Clone UI", "React App", "Reels", "Voice Agent", "Scraper"]
    ring_b = ["Landing Page", "SEO Engine", "FastAPI", "RAG", "Sheets", "Dashboards"]

    def ring(items, radius, cls):
        tiles = "".join(
            f'<div class="tile" style="--a:{i*60}deg;--r:{radius}"><i></i><b>{esc(name)}</b></div>'
            for i, name in enumerate(items))
        return f'<div class="ring {cls}">{tiles}</div>'

    stage = (ring(ring_a, "clamp(128px,17vw,238px)", "a")
             + ring(ring_b, "clamp(84px,11.5vw,158px)", "b"))

    index_ld = site_ld()
    index_ld["@graph"].append({
        "@type": "ItemList", "name": "All skills", "numberOfItems": n,
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": m["title"],
             "url": f"{BASE}/skills/{m['slug']}.html"}
            for i, m in enumerate(META)],
    })
    index_ld["@graph"].append({
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "Which AI agents can use these skills?",
             "acceptedAnswer": {"@type": "Answer", "text": "Any agent that can read a URL or a pasted file: Claude, ChatGPT with browsing, GitHub Copilot Chat, Cursor, Windsurf, Codex, Gemini, or your own agent loop."}},
            {"@type": "Question", "name": "Is installing a skill really just one prompt?",
             "acceptedAnswer": {"@type": "Answer", "text": "Yes. The prompt tells the agent to fetch a specific URL and follow it. The skill itself is a 250-340 line markdown procedure, so the agent gets a full method instead of a one-line request."}},
            {"@type": "Question", "name": "Are the skills free?",
             "acceptedAnswer": {"@type": "Answer", "text": "Yes. Every skill file is MIT licensed: use, modify and redistribute them, including commercially, provided the copyright notice is kept."}},
            {"@type": "Question", "name": "Do these skills work for non-coding work?",
             "acceptedAnswer": {"@type": "Answer", "text": "About half are non-coding: 3D animation, video editing, landing page copy, SEO, dashboards, spreadsheets, resumes, branding and PDF pipelines."}},
        ],
    })
    html_out = head(
        f"Skill Vault — {n} free AI agent skills for Claude & Copilot",
        f"Download {n} detailed, free skills for Claude, Copilot, Cursor and any AI agent. "
        f"One-prompt install from a URL. MIT licensed, no signup, no tracking.",
        canonical=f"{BASE}/", jsonld=index_ld
    ) + f"""
<header class="hero"><div class="wrap hero3d">
  <div>
    <span class="badge"><span class="dot"></span> {n} skills live · one-prompt install · MIT</span>
    <h1 class="title">Skills that make your <span class="grad">AI agent actually useful</span></h1>
    <p class="sub">{numword(n)} deeply detailed skills — 3D animation on a phone, cloning a UI from screenshots,
    shipping a production React app, voice agents, RAG, deployment and more. Each one installs into Claude,
    Copilot, Cursor, Codex or any agent that can read a URL. No marketplace, no account, no package manager.</p>
    <div class="herobtns">
      <a class="btn p" href="#skills">Browse all {n} skills</a>
      <button class="btn s" data-p="{html.escape(all_prompt, quote=True)}">Copy the install-all prompt</button>
    </div>
    <div class="stats">
      <div class="stat"><b>{n}</b><span>Skills</span></div>
      <div class="stat"><b>{total_lines:,}</b><span>Lines of guidance</span></div>
      <div class="stat"><b>1</b><span>Prompt to install</span></div>
      <div class="stat"><b>0</b><span>Dependencies</span></div>
    </div>
  </div>
  <div class="stage" aria-hidden="true">{stage}</div>
</div></header>

<section id="skills"><div class="wrap">
  <div class="shead">
    <div>
      <div class="eyebrow">The library</div>
      <h2>{numword(n)} skills, each a full operating procedure</h2>
      <p>Not prompts. Each file is a workflow with stages, settings, tables, checklists and failure modes.</p>
    </div>
    <a class="btn s" href="/skills.json">View manifest</a>
  </div>
  <div class="grid">{cards}
  </div>
</div></section>

<section id="install"><div class="wrap">
  <div class="shead"><div>
    <div class="eyebrow">Installation</div>
    <h2>One prompt. One URL. Done.</h2>
    <p>The URL is the whole install. Any agent that can fetch a page can hold the skill.</p>
  </div></div>
  <div class="steps">
    <div class="step"><div class="n">STEP 01</div><h3>Copy a prompt</h3>
      <p>Every card has a <em>Copy install prompt</em> button. It contains the live URL of that skill's markdown file.</p></div>
    <div class="step"><div class="n">STEP 02</div><h3>Paste it into your agent</h3>
      <p>Claude with a project or file access, ChatGPT with browsing, Copilot, Cursor, Windsurf, Codex, or your own agent loop.</p></div>
    <div class="step"><div class="n">STEP 03</div><h3>Ask for the work</h3>
      <p>The agent reads the file, follows its stages, asks you the questions it needs, then executes with its checklists.</p></div>
  </div>
  <div class="panel">
    <h3>What a copied prompt looks like</h3>
    <p class="hint">Replace the slug with any of the {n} above.</p>
    <pre class="snip">Read the skill at {BASE}/skills/3d-animation-on-phone.md and install it
as a skill in your agent. Follow it exactly, including its checklists.
Then ask me the questions it requires and do the work.</pre>
  </div>
  <div class="panel">
    <h3>Install all {n} at once</h3>
    <p class="hint">Point the agent at the manifest; it resolves every slug to its raw markdown.</p>
    <pre class="snip">Read {BASE}/skills.json
Install every skill listed in it as a skill in your agent.
Each entry has a raw URL — fetch it and follow it exactly.</pre>
  </div>
  <div class="panel">
    <h3>For agents and developers</h3>
    <p class="hint">Stable, machine-readable endpoints.</p>
    <pre class="snip">GET {BASE}/skills.json      → manifest: slug, title, category, description, raw url
GET {BASE}/skills/&lt;slug&gt;.md  → raw skill file, YAML frontmatter + markdown body
GET {BASE}/llms.txt         → plain-text index for LLM crawlers</pre>
  </div>
</div></section>

<section id="use"><div class="wrap">
  <div class="shead"><div>
    <div class="eyebrow">What people build</div>
    <h2>Four real starting points</h2>
    <p>Pick the skill that matches the job you are stuck on.</p>
  </div></div>
  <div class="steps">
    <div class="step"><div class="n">CREATIVE</div><h3>“I only have a phone”</h3>
      <p>3D Animation On Phone and AI Video Editing For Reels take a raw idea to a platform-spec export without a desktop.</p></div>
    <div class="step"><div class="n">FRONTEND</div><h3>“Rebuild this screen”</h3>
      <p>Clone UI From Screenshot measures the image, recovers the tokens, builds a grey skeleton, then verifies with pixel diffs.</p></div>
    <div class="step"><div class="n">ENGINEERING</div><h3>“Make it production-ready”</h3>
      <p>React Production App and API Builder lock the decisions that cause rewrites, then enforce budgets and checklists.</p></div>
    <div class="step"><div class="n">GROWTH</div><h3>“Get users”</h3>
      <p>Prompt To Landing Page and SEO Content Engine build the page and the cluster that feeds it, with measurement wired in.</p></div>
  </div>
</div></section>

<section id="faq"><div class="wrap">
  <div class="shead"><div>
    <div class="eyebrow">FAQ</div><h2>The practical questions</h2>
  </div></div>
  <div class="faq">
    <details><summary>Which agents can use these?</summary>
      <div class="a">Any agent that can read a URL or a pasted file: Claude (projects, or paste the file),
      ChatGPT with browsing, GitHub Copilot Chat, Cursor, Windsurf, Codex, Gemini, or your own agent loop.
      If the agent cannot browse, download the .md and attach it — the content is identical.</div></details>
    <details><summary>Is it really just a prompt?</summary>
      <div class="a">Yes. The “prompt” is an instruction to fetch a specific URL and follow it. The skill itself lives
      in the markdown file, so the agent gets 120–150 lines of procedure instead of a one-line request.
      That is the whole difference in output quality.</div></details>
    <details><summary>What is inside a skill file?</summary>
      <div class="a">YAML frontmatter (name, description, version, tags), when to use and when not to,
      hard constraints to confirm, a numbered pipeline, tables of exact settings, code templates,
      a quality checklist, a failure-mode table and an output contract.</div></details>
    <details><summary>Can I edit or fork them?</summary>
      <div class="a">They are MIT licensed. Download, edit, add your own house rules, host them anywhere.
      Keeping the URL stable is all that matters for the one-prompt install.</div></details>
    <details><summary>Do these work for non-coding work?</summary>
      <div class="a">Roughly half are non-coding: 3D animation, video editing, landing page copy, SEO,
      dashboards, spreadsheets, resumes, branding and PDF pipelines. The rest are engineering and AI work.</div></details>
    <details><summary>How do I host my own copy?</summary>
      <div class="a">Copy the folder to any static host — Cloudflare Pages, Netlify, GitHub Pages, S3.
      This site is a single HTML file plus a folder of markdown, with no build step and no dependencies.</div></details>
  </div>
</div></section>

<section id="developer"><div class="wrap">
  <div class="shead"><div>
    <div class="eyebrow">Credits</div>
    <h2>Built by Error</h2>
    <p>Skill Vault is written, built and maintained by one developer. Every skill is free, MIT licensed, and updated by hand.</p>
  </div></div>
  <div class="dev">
    <div class="who">
      <span class="av">E</span>
      <div>
        <h3>Developed by Error</h3>
        <p>Independent developer and security researcher. If a skill here saved you an afternoon,
        a follow on any of these costs nothing.</p>
      </div>
    </div>
    <div class="socials">{''.join(
      f'<a class="soc" href="{url}" target="_blank" rel="noopener noreferrer me" aria-label="{label}">{svg}<span>{label}<br><small>{handle}</small></span></a>'
      for label, handle, url, svg in SOCIALS)}</div>
  </div>
</div></section>
""" + FOOT

    (ROOT / "index.html").write_text(html_out, encoding="utf-8")

    # per-skill pages
    for m in META:
        md = (SK / (m["slug"] + ".md")).read_text(encoding="utf-8")
        body = md2html(md)
        url = f"{BASE}/skills/{m['slug']}.md"
        prompt = PROMPT.format(url=url)
        page = head(f"{m['title']} — free AI agent skill | Skill Vault",
                f"{m['tag']} Free MIT-licensed skill for Claude, Copilot, Cursor and any AI agent.",
                canonical=f"{BASE}/skills/{m['slug']}.html", og_type="article",
                jsonld=article_ld(m["title"], m["tag"], f"{BASE}/skills/{m['slug']}.html")) + f"""
<div class="wrap"><div class="doc">
  <a class="back" href="/">← All skills</a>
  <div class="dochead">
    <div class="row"><span class="cat" style="color:{m['accent']};background:color-mix(in srgb,{m['accent']} 13%,transparent);border:1px solid color-mix(in srgb,{m['accent']} 30%,transparent)">{esc(m['cat'])}</span>
      <span class="urlbox">{esc(url)}</span></div>
    <h1>{esc(m['title'])}</h1>
    <p class="tagline">{esc(m['tag'])}</p>
    <div class="docacts">
      <button class="btn p" data-p="{html.escape(prompt, quote=True)}">Copy install prompt</button>
      <a class="btn s" href="/skills/{m['slug']}.md" download>Download .md</a>
      <a class="btn s" href="/">All skills</a>
    </div>
  </div>
  <div class="doccard">
    <div class="l"><b>Install URL</b><span class="urlbox">{esc(url)}</span></div>
    <button class="mini" data-c="{esc(url)}">Copy URL</button>
  </div>
  <div class="pbox" data-p="{html.escape(prompt, quote=True)}" role="button" tabindex="0"
       aria-label="Copy the install prompt">
    <div class="lbl">Install prompt <span>tap to copy</span></div>
    <code>{esc(prompt)}</code>
  </div>
  {body}
</div></div>
""" + FOOT
        (SK / (m["slug"] + ".html")).write_text(page, encoding="utf-8")

    manifest = {
        "name": "Skill Vault",
        "version": "1.0.0",
        "license": "MIT",
        "homepage": BASE,
        "updated": "2026-11-15",
        "install_prompt_template": PROMPT,
        "skills": [
            {"id": i + 1, "slug": m["slug"], "title": m["title"], "category": m["cat"],
             "description": m["tag"],
             "url": f"{BASE}/skills/{m['slug']}.html",
             "raw": f"{BASE}/skills/{m['slug']}.md",
             "tags": [m["cat"].lower().replace(" ", "-")],
             "highlights": m["hi"]}
            for i, m in enumerate(META)
        ],
    }
    (ROOT / "skills.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # status.json: deliberately tiny (< 2 KB at 100 skills) so an agent can read the
    # whole inventory in one fetch even when the page-text fetcher truncates long files.
    cats = {}
    for m in META:
        cats[m["cat"]] = cats.get(m["cat"], 0) + 1
    status = {"name": "Skill Vault", "count": len(META), "updated": "2026-11-15",
              "categories": cats, "slugs": [m["slug"] for m in META]}
    (ROOT / "status.json").write_text(json.dumps(status, separators=(",", ":")), encoding="utf-8")

    llms = ["# Skill Vault", "",
            "Installable AI agent skills. Each skill is a detailed markdown procedure.",
            "Install by telling your agent to read the raw URL and follow it exactly.", "",
            "## Skills", ""]
    for i, m in enumerate(META, 1):
        llms += [f"{i}. {m['title']} ({m['cat']}) — {m['tag']}",
                 f"   page: {BASE}/skills/{m['slug']}.html",
                 f"   raw:  {BASE}/skills/{m['slug']}.md", ""]
    llms += ["## Manifest", f"{BASE}/skills.json", "",
             "## One-prompt install", "",
             PROMPT.format(url=BASE + "/skills/<slug>.md"), ""]
    (ROOT / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n# AI crawlers welcome\nUser-agent: GPTBot\nAllow: /\n"
        "User-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\n\n"
        f"Sitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

    urls = ([f"{BASE}/"] + [f"{BASE}/skills/{m['slug']}.html" for m in META]
            + [f"{BASE}/{s}.html" for s in LEGAL_PAGES])
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        if u == f"{BASE}/":
            pri = "1.0"
        elif "/skills/" in u:
            pri = "0.8"
        else:
            pri = "0.3"
        sm.append(f"<url><loc>{u}</loc><lastmod>2026-11-15</lastmod>"
                  f"<changefreq>weekly</changefreq><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    nf = head("404 — Skill Vault", "Page not found.", canonical=f"{BASE}/404.html", noindex=True) + """
<div class="wrap" style="text-align:center;padding:110px 0 130px">
  <h1 style="font-size:clamp(2rem,5vw,3rem);font-weight:800;letter-spacing:-.03em">404</h1>
  <p style="color:var(--mut);margin-top:14px">That skill does not exist — yet.</p>
  <div class="herobtns"><a class="btn p" href="/">Back to the vault</a></div>
</div>""" + FOOT
    (ROOT / "404.html").write_text(nf, encoding="utf-8")

    (ROOT / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: geolocation=(), microphone=(), camera=()\n\n"
        "/skills/*.md\n  Content-Type: text/markdown; charset=utf-8\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n"
        "/skills.json\n  Content-Type: application/json; charset=utf-8\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=600\n\n"
        "/status.json\n  Content-Type: application/json; charset=utf-8\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=60\n\n"
        "/llms.txt\n  Content-Type: text/plain; charset=utf-8\n  Access-Control-Allow-Origin: *\n", encoding="utf-8")

build_index()
build_legal()
print("og.png:", build_og())
print("built index +", len(META), "skill pages")
for p in sorted(ROOT.rglob("*")):
    if p.is_file():
        print(p.relative_to(ROOT), p.stat().st_size)
