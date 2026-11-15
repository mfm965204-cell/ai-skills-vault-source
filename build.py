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

def head(title, desc, extra=""):
    return f"""<!doctype html>
<html lang="en" class="nojs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#07070b">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{BASE}/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%237c5cff'/><text x='16' y='22' font-size='16' font-family='monospace' fill='%2307070b' text-anchor='middle'>S</text></svg>">
<style>{CSS}</style>
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


def build_legal():
    """Render terms, privacy, disclaimer and licence from the content above."""
    for slug in LEGAL_PAGES:
        title, desc, body = LEGAL[slug]
        page = head(f"{title} — Skill Vault", desc) + f"""
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

    html_out = head(
        f"Skill Vault — {n} installable AI agent skills",
        f"{n} detailed, downloadable skills for Claude, Copilot, Cursor and any AI agent. Install with one prompt and a URL."
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
        page = head(f"{m['title']} — Skill Vault", m["tag"]) + f"""
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
        sm.append(f"<url><loc>{u}</loc><lastmod>2026-11-15</lastmod><priority>0.9</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    nf = head("404 — Skill Vault", "Page not found.") + """
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
print("built index +", len(META), "skill pages")
for p in sorted(ROOT.rglob("*")):
    if p.is_file():
        print(p.relative_to(ROOT), p.stat().st_size)
