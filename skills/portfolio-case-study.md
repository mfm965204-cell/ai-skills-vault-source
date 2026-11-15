---
name: portfolio-case-study
description: Turn two or three real projects into portfolio case studies with problem, decision, measurement and proof, written so a hiring manager reads past the first screen.
version: 1.0.0
license: MIT
tags: [career, portfolio, writing, hiring, freelancing]
---

# Portfolio Case Study

A portfolio is not a gallery of screenshots. Hiring managers and clients are not asking "what did it look like", they are asking "can this person make a decision under constraint, and did it work". A page of pretty mockups answers neither question, and a wall of tool logos answers it negatively.

This skill turns two or three projects you already did into case studies with the same spine: the constraint, the decision, the number, the artefact. Two good ones beat six thin ones, and the constraint section is what makes a reader believe the rest.

The test of a case study is that a reader who knows the domain can ask you one follow-up question about a trade-off, and you have the answer already on the page.

## When to use this skill

- You have shipped real work but your portfolio is a list of technologies.
- You are switching from service work to product work, or the reverse, and need to show the transfer.
- A recruiter asked for "a portfolio" and you do not know what shape they want.
- You are freelancing and your site shows screenshots but no outcomes.
- **Do NOT use for:** writing a resume or a CV (different artefact and different length), building the site itself, or inventing projects - if you cannot evidence it, it does not go on the page.

## Stage 1 - Pick the projects by the decision they show

Choose by what each project proves, not by how much you liked it. Three slots is the right number for most portfolios: one that shows depth, one that shows range, one that shows judgement under a real constraint.

1.1 List every project from the last 4 years where you made a decision someone else could disagree with.

1.2 For each, write one line: the constraint, the decision, the outcome. If you cannot fill all three, the project is a task, not a case study.

1.3 Score each on evidence - do you have a number, a screenshot of the before state, a testimonial, a repository? A project with no evidence is a claim.

1.4 Pick the top 3, and force them to differ in domain, in scale or in the type of constraint.

1.5 Drop anything under NDA to an anonymised version or drop it entirely. Client confidentiality beats portfolio completeness.

1.6 Write one sentence per chosen project stating who was stuck and what changed. That sentence becomes the case study's subtitle.

Gate: three projects, each with a constraint, a decision, an outcome and at least one piece of evidence.

## Stage 2 - Reconstruct the constraint with real numbers

The constraint is the part most portfolios omit and the part that makes the work legible. "Built a dashboard" is a task; "built a dashboard that had to load 40,000 rows in under 2 seconds on a ₹25,000 Android tablet" is a case study.

2.1 Write the constraint in numbers: team size, timeline, budget, traffic, device, regulatory requirement.

2.2 Write the constraint you could not move, and why it was immovable. That is where judgement shows.

2.3 State what you were told to do, and what you decided to do instead, if they differ.

2.4 Note who else was involved and what they owned. Claiming a team's work as solo is the fastest way to lose an offer in the reference call.

2.5 Record the state before you started, ideally with a screenshot, a metric or a quote.

| Constraint type | Weak phrasing | Strong phrasing |
|---|---|---|
| Time | "tight deadline" | "6 weeks, fixed launch date tied to a festival campaign" |
| Team | "small team" | "2 engineers, no designer, me owning both" |
| Budget | "limited budget" | "₹40,000 a month total infrastructure ceiling" |
| Scale | "high traffic" | "18,000 sessions a day on launch day, 4x the previous peak" |
| Compliance | "had to be compliant" | "RBI data localisation, no card data outside India" |

Gate: every constraint has a number, and the immovable one is named.

## Stage 3 - Write the decision, not the process

A process log ("first I set up the repo, then I...") reads as inexperience. A decision log reads as seniority: what the options were, what you chose, what you gave up.

3.1 List 2-4 options you genuinely considered. One option is not a decision, it is a preference.

3.2 For each, write the cost: what it would have taken and what it would have prevented.

3.3 State the choice and the reason in one sentence, with the trade-off named.

3.4 State what you gave up. A case study with no downside reads as marketing and gets discounted.

3.5 Add the decision that was wrong, if there was one, and what it cost. One honest reversal does more for credibility than three successes.

3.6 Keep the tool names out of the decision sentence. The decision is "server-rendered pages instead of a client app", the tool is an implementation detail that belongs in Stage 5.

Gate: every case study names at least two options, the choice, the trade-off and one cost.

## Stage 4 - Measure the outcome in the unit the client cared about

Numbers must be the ones the client or employer tracked, not ones you invented afterwards. If you have no number, use a verifiable qualitative outcome and say so plainly.

4.1 Write the metric that was already being tracked before you started - revenue, signups, support tickets, page load, error rate.

4.2 Write the before value and the after value with the measurement window: "checkout completion 61% to 74% over 8 weeks".

4.3 If you cannot disclose the absolute number, use a ratio and say why the absolute is withheld.

4.4 Add one number about the work itself: lines of code removed, queries eliminated, manual steps deleted, hours saved per week.

4.5 Attribute honestly: "the campaign also changed that week" is a sentence that raises trust, not lowers it.

4.6 Where there is no number, quote the user: one sentence from a customer or the client beats a vague claim of improvement.

Gate: every case study has a before value, an after value and a measurement window, or an explicit statement that no number exists.

## Stage 5 - Assemble the artefact set

A case study needs something to look at, and it needs to be the right something. Screenshots of finished states prove the least; the messy middle proves the most.

5.1 Include one before artefact: the old screen, the spreadsheet, the manual process.

5.2 Include one decision artefact: a wireframe, an architecture sketch, a data model, a sketch of two options.

5.3 Include one after artefact: the shipped screen or the live link.

5.4 Annotate each artefact with one line explaining what the reader should notice. Unannotated images are decoration.

5.5 Keep images under 400 KB each and use WebP, so the page loads on a phone on mobile data.

5.6 For code, link to a repository or a gist rather than pasting 200 lines into the page.

5.7 Compress every image before it goes near the page, and check the output size:

```bash
for f in shots/*.png; do
  cwebp -q 78 "$f" -o "${f%.png}.webp"
done
du -h shots/*.webp | sort -h | tail -3
```

| Artefact | Proves | Common mistake |
|---|---|---|
| Before screenshot | The problem was real | Missing entirely |
| Wireframe or sketch | You think before building | Replaced by a polished mockup |
| Architecture diagram | You can hold a system in your head | Too detailed to read at page size |
| Shipped screen | It exists | Only artefact included |
| Metric chart | It worked | No axis labels or window |

Gate: each case study has one artefact of each of the three kinds, each with a one-line annotation.

## Stage 6 - Write the page at three reading depths

Different readers stop at different points. Structure the page so a 15-second reader, a 2-minute reader and a 10-minute reader each get something true.

6.1 The 15-second layer: title, subtitle with the outcome, one hero image, one metric.

6.2 The 2-minute layer: the constraint paragraph, the decision sentence, the outcome table.

6.3 The 10-minute layer: the decision log, the artefacts with annotations, the honest reversal.

6.4 Keep sentences under 25 words and paragraphs under 4 sentences. Case studies are read on phones between meetings.

6.5 Put the outcome number in the subtitle, not at the bottom. Readers who stop early should still leave with the number.

6.6 Cut every adjective that is not load-bearing. "Beautiful" and "innovative" carry no information; "40% fewer taps to checkout" does.

6.7 Write the page from a skeleton so all three case studies share a shape a reader learns once:

```markdown
## <Project name>
**<Outcome with a number> in <window>**

- Constraint: <numbers>
- Options: <A> vs <B>
- Chose: <option> because <reason>
- Gave up: <cost>
- Result: <before> to <after> over <window>
- My role: <exact scope>

![before](before.webp) ![after](after.webp)
```

Gate: the outcome number appears above the fold, and the page has three distinct reading layers.

## Stage 7 - Add the proof layer that closes doubt

A case study invites one question: "did this person really do that?" Answer it before it is asked, without breaching anyone's confidence.

7.1 Add a testimonial line from the client or manager, with their role and company type - not a logo wall.

7.2 Add a link to something verifiable: a live URL, a public repository, a published article, a talk recording.

7.3 If the work is under NDA, say what you can: the industry, the scale, the role, and that details are withheld.

7.4 Name your exact role in the project. "Led design and frontend" is verifiable; "worked on" is not.

7.5 Check every link before publishing. A dead live link on a portfolio is worse than no link.

7.6 Ask for the testimonial with a shape, not an open request: "one sentence on what changed and one on what it was like to work with me" gets a usable reply in a day.

Gate: every case study carries one verifiable proof and an explicit role statement.

## Stage 8 - Publish, then test it on three readers

The page is not done when it is written. It is done when three people who are not you can restate what you did.

8.1 Publish at one URL you control, with a plain HTML page or a static site - no gate, no email capture.

8.2 Send it to three readers: one in your field, one adjacent, one outside. Ask each one question: "what did this person do, and did it work?"

8.3 Fix the place where a reader hesitates. Usually it is the constraint paragraph, not the design.

8.4 Check the page on a phone at 4G speed and confirm it renders under 2 seconds.

8.5 Add a single call to action at the bottom - email, calendar link or contact form - and nothing else.

8.6 Re-read after a week with fresh eyes and delete the first paragraph if it is throat-clearing.

8.7 Note which case study readers mention first. That is the one to lead with when you tailor the page for a specific role.

Gate: three readers can restate your role and the outcome, and the page loads under 2 seconds on mobile data.

## Stage 9 - Keep it alive with a 90-minute quarterly pass

A portfolio decays quietly: links break, numbers age, the last project is 3 years old. One short pass per quarter keeps it honest.

9.1 Check every link and every live URL; remove anything that no longer resolves.

9.2 Add one project if you shipped one, and retire the weakest if you now have four.

9.3 Re-check the metrics against the source of truth; do not let a number drift from the dashboard.

9.4 Update the date on the page so a reader knows it is maintained.

9.5 Keep an evidence folder per project - screenshots, metrics exports, testimonials - so a rebuild takes minutes.

9.6 Archive the old version of the page with its date, so you can show how the work evolved rather than only the current state.

Gate: all links resolve, the page carries a current date, and one new project has been added or explicitly considered.

## Quality checklist

- [ ] Exactly three projects are featured, chosen for the decision each shows.
- [ ] Every project has a constraint, a decision and an outcome.
- [ ] Every constraint is written with a number.
- [ ] The immovable constraint is named for each project.
- [ ] Each case study lists at least two options considered.
- [ ] Each case study names the trade-off and one thing given up.
- [ ] Every outcome has a before value, an after value and a window.
- [ ] Attribution states what teammates owned.
- [ ] Each project has a before, a decision and an after artefact.
- [ ] Every artefact carries a one-line annotation.
- [ ] The outcome number appears above the fold.
- [ ] Each case study names your exact role.
- [ ] Every external link resolves.
- [ ] Three readers could restate your role and outcome.
- [ ] The page loads under 2 seconds on mobile data.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Recruiters skim and leave | The page opens with tools and a self-description, not an outcome | Move the outcome number into the subtitle |
| "Looks nice, but what did you do?" | Team work presented without role attribution | Name your role in one sentence per project |
| No callbacks after applying | No number anywhere, so nothing is memorable | Add a before and after value with a window |
| A reader doubts the work | Only finished screenshots, no decision or sketch | Add a wireframe or architecture artefact |
| Client asks to take it down | NDA ignored in the write-up | Anonymise industry and scale, keep the decision story |
| Portfolio feels stale | Last update 3 years ago and no date on the page | Quarterly pass with a visible update date |

## Copy-ready agent prompt

> Read the skill at the URL above and turn my projects into portfolio case studies. Ask me for a list of projects, then pick three by the decision each proves and tell me which you rejected and why. For each, extract the constraint in numbers, the options considered, the trade-off, the outcome with before and after values and a window, and my exact role. Then give me the page copy at three reading depths plus a list of the artefacts I still need to supply. Do not invent a metric or a testimonial; where I have no number, write the qualitative outcome and say so.
