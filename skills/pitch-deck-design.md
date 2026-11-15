---
name: pitch-deck-design
description: Build a 10-12 slide deck that closes - a five-beat narrative spine, one idea per slide, a type and grid system, chart and financial slides that survive scrutiny, a design QA pass and an export under 10 MB.
version: 1.0.0
license: MIT
tags: [design, pitch-deck, presentation, fundraising, narrative, sales]
---

# Pitch Deck Design

Investors and buyers decide in the first 90 seconds and then look for reasons to keep the decision. A deck with 34 slides of features is a reason to stop; a deck with 11 slides in a clear order is a reason to ask for the next meeting.

This skill builds the narrative first, then the slides, then the design pass - with the slide map, the type scale and the QA checks that stop a deck looking like five people made it.

## When to use this skill

- Raising money and you have 10 minutes and a follow-up document.
- Selling a large contract where a deck travels without you.
- Pitching internally for budget and need one page of approval.
- You have 40 slides and need to know which 11 matter.

Do NOT use for: a leave-behind document that must stand alone in detail (that is a memo, not a deck), or a keynote with 300 slides of images - different craft.

## Stage 1 - Fix the narrative spine before opening the tool

1.1 Five beats, in this order: the problem, the insight, the solution, the proof, the ask. Every slide belongs to exactly one beat.

1.2 Write the whole deck as 11 sentences first. One sentence per slide, in order, on a single page.

1.3 Read the sentences aloud without slides. If the argument does not stand on its own, no amount of design will save it.

1.4 Name the decision you want at the end: a second meeting, a term sheet, a budget approval, a pilot. The ask slide is built backwards from that.

1.5 Cut every slide that does not change the decision. A team-history slide does not change the decision; a traction chart does.

| Beat | Slides | Purpose |
|---|---|---|
| Problem | 2 | the pain, with a number |
| Insight | 1 | the non-obvious thing you know |
| Solution | 3 | what it is, how it works, why now |
| Proof | 3 | traction, customers, unit economics |
| Ask | 2 | what you want, how it is used |

1.6 Put the strongest slide at position 2 or 3. Decks are abandoned in the first third, and a strong early slide buys the middle.

1.7 Keep the 11 sentences in a plain text file next to the deck, so the argument is versioned separately from the design:

```text
1  Clinics wait 30 days for a payment they have already earned.
2  That gap is ₹4.2 lakh of working capital locked per clinic.
3  The delay is not the payer, it is the reconciliation after the claim.
4  We reconcile the claim before the payer sees it.
5  Three steps: capture, reconcile, submit.
6  UPI and the new claims API make this possible this year, not in 2020.
7  ₹42 lakh collected for 11 clinics in 9 months.
8  A 24-doctor clinic cut its gap from 31 days to 4.
9  ₹2,900 per clinic per month, 71% gross margin.
10 ₹4 crore to reach 900 clinics and ₹2.4 crore ARR.
11 Three people: payments, clinical ops, engineering.
```

Gate: 11 sentences in five beats, read aloud in under 2 minutes.

## Stage 2 - Order the slides for a reader who is skimming

2.1 Slide 1 is a title with the one-line description, not a logo on white. "X helps clinics collect payments in 2 days instead of 30."

2.2 Slide 2 is the problem with a number: how much it costs, how many people it affects, how often.

2.3 Slide 3 is the insight - the thing you know that the market has not priced in. This is the slide that gets a second meeting.

2.4 Slides 4-6 are the solution: what it is, one screen of the product, and why now.

2.5 Slides 7-9 are proof: traction over time, a named customer with a result, and unit economics.

2.6 Slides 10-11 are the ask and the appendix pointer. The appendix holds the 20 slides you were tempted to include.

| # | Slide | One idea |
|---|---|---|
| 1 | Title | what it is, in one line |
| 2 | Problem | the cost of the status quo |
| 3 | Insight | what everyone else misses |
| 4 | Solution | the product in one frame |
| 5 | How it works | three steps, no more |
| 6 | Why now | the change that makes this possible |
| 7 | Traction | one chart, up and to the right |
| 8 | Customer | one named result |
| 9 | Economics | one number per customer |
| 10 | Ask | amount, use of funds, milestone |
| 11 | Team | three people, one line each |

2.7 Appendix slides are numbered A1, A2 and never shown unless asked. They answer the questions you know are coming.

Gate: a slide map with one idea per slide and an appendix list.

## Stage 3 - Put one idea on every slide

3.1 The slide title is the claim, not the topic. "Churn is 4% because onboarding takes 11 days" beats "Churn".

3.2 If the title can be read alone and understood, the slide works even if nobody reads the body.

3.3 Maximum 25 words of body text per slide. Beyond that it is a document, and documents belong in the appendix.

3.4 Every number on a slide needs a source line in 12 px at the bottom. Unsupported numbers end conversations.

3.5 One chart per slide, with the axis labelled and the takeaway in the title. Two charts on one slide means two slides.

3.6 Delete the bullet list of features. Three capabilities that matter beat nine that exist.

Gate: every slide title is a claim, body under 25 words, source on every number.

## Stage 4 - Build a type and grid system

4.1 One font family, two weights. A deck with four fonts reads as four decks stapled together.

4.2 Type scale: 40-48 px title, 24-28 px body, 12-14 px source. Set it once and never type a size by hand again.

4.3 Grid: 12 columns, 64 px margin at 1920x1080, 24 px gutter. Every element snaps to it.

4.4 Two colours plus a neutral. Accent used for the one thing per slide that matters - the number, the chart line, the call to action.

4.5 Left-align body text. Centred paragraphs are harder to read and impossible to keep consistent across 11 slides.

4.6 Keep a running header or footer with the slide number and the company name in 12 px. It costs nothing and makes a printed deck navigable.

| Element | Value | Note |
|---|---|---|
| Canvas | 1920x1080 (16:9) | also fine at 1280x720 |
| Margin | 64 px | 12-column grid |
| Gutter | 24 px | consistent spacing |
| Title | 40-48 px, bold | the claim |
| Body | 24-28 px, regular | under 25 words |
| Source | 12-14 px | every number |
| Colours | 2 plus neutral | accent once per slide |
| Fonts | 1 family, 2 weights | no exceptions |

Gate: a master slide with the grid and type scale applied.

## Stage 5 - Make the charts say one thing

5.1 One message per chart, and the message is the title: "Revenue grew 4x in 9 months" over a line that shows exactly that.

5.2 Label the axes, remove gridlines that carry no information, and drop the legend if there is only one series.

5.3 Start the y-axis at zero for bars; a truncated axis on a bar chart is a credibility problem, not a design choice.

5.4 Highlight the one series that matters in the accent colour and make the rest grey.

5.5 Round numbers for a slide: ₹1.2 crore, not ₹1,23,47,890. Precision belongs in the appendix.

5.6 If the data is weak, say so on the slide. "12 customers, early signal" is stronger than a chart implying 200.

Gate: every chart has a claim as its title and a labelled axis.

## Stage 6 - Build the financial and economics slide

6.1 One number per customer that matters: contribution margin, CAC payback, or gross margin. Pick the one your business lives on.

6.2 Show the arithmetic in a line, not a spreadsheet screenshot: revenue per customer, cost to serve, margin, payback in months.

6.3 Projections go in the appendix. The main deck shows what happened and what one unit earns.

6.4 State the assumption behind any projection in the same font size as the projection. Small print assumptions read as concealment.

6.5 Use a range for forward numbers, not a point. "₹8-11 crore in FY27" is defensible; a single number invites a fight about the decimal.

6.6 Reconcile the deck's numbers with the spreadsheet before sending. One mismatch and the reader stops believing the rest.

Gate: one economics slide with visible arithmetic and a stated assumption.

## Stage 7 - Make it survive scrutiny

7.1 Prepare an appendix slide for each question you have been asked more than once: competition, pricing, churn, hiring plan, regulatory risk.

7.2 Answer the obvious objection on a slide before it is raised - a "why this fails" slide builds more trust than it costs.

7.3 Name competitors on the competition slide. A 2x2 with only your logo in the top right is the most distrusted slide in any deck.

7.4 Show the weakest number and explain it. Every experienced reader looks for the hole; finding it explained is reassuring, finding it hidden is fatal.

7.5 Keep a source file for every external number with the URL and the date you checked it.

Gate: five appendix slides covering the five most-asked questions.

## Stage 8 - Run the design QA pass

8.1 View the deck at 25% zoom. Alignment errors, inconsistent margins and colour drift are obvious at that size and invisible at 100%.

8.2 Check every slide for the four failures: text overflowing its box, two fonts, a number without a source, and an accent colour used twice.

8.3 Print one slide in greyscale and read it. If the chart becomes one grey mass, the value contrast is wrong.

8.4 Check the deck on a phone. Half your readers will open it on one, and 16:9 at phone width means 24 px body text is unreadable.

8.5 Run a spell check and a number check separately. Spell check does not catch ₹1.2 crore written as ₹12 crore.

8.6 Have one person who has not seen the deck read it in silence for 3 minutes, then state the ask. If they cannot, the narrative is wrong.

| Check | Pass condition |
|---|---|
| 25% zoom | no misalignment visible |
| Text overflow | none, on every slide |
| Fonts | one family, two weights |
| Numbers | every one has a source |
| Greyscale | charts still readable |
| Phone view | body text readable |
| Silent read | the ask is stated correctly |

Gate: all seven checks pass, one silent read confirms the ask.

## Stage 9 - Export and send

9.1 Export a PDF at 16:9, under 10 MB, with fonts embedded. A deck that reflows on the reader's machine is worse than a PDF.

9.2 Name it `company-deck-2026-11.pdf`. Version and date in the filename, not in the slide footer.

9.3 Keep a link version as well, and check that the link opens without a login.

9.4 Send the PDF, not the source file. Editable decks get edited by people who are not you.

9.5 If sending by email, keep the file under 10 MB or use a link. A 40 MB deck never arrives.

9.6 Test the PDF on a phone before sending. It is the most common way your deck will be read.

9.7 Export from one source of truth. If the deck is authored in markdown, one command produces the PDF with embedded fonts:

```bash
pandoc deck.md -o company-deck-2026-11.pdf \
  --pdf-engine=weasyprint \
  -V pagestyle=empty -V papersize=a4 \
  --metadata title="Company - seed deck - 2026-11"
ls -lh company-deck-2026-11.pdf   # check it is under 10 MB
```

Gate: a PDF under 10 MB, opened and checked on a phone.

## Stage 10 - Present it and leave it behind

10.1 Rehearse to 10 minutes for a 10-minute slot, and 3 minutes for the version you will be asked for.

10.2 Write the spoken line for each slide. The slide is the claim; the talk track is the evidence.

10.3 Never read the slides. If the slide is being read, it has too much text.

10.4 Leave 5 minutes for questions and have the appendix ready to jump to by number.

10.5 Send the deck within 2 hours of the meeting, with the three numbers discussed restated in the email body.

10.6 Update the deck after every meeting with the question you could not answer. It becomes the appendix.

Gate: rehearsed to time, sent within 2 hours with a summary.

## Worked example

A seed deck for a clinic payments product, 34 slides reduced to 11.

| Version | Slides | Meeting rate per 10 sends |
|---|---|---|
| v1, feature-led | 34 | 1 |
| v2, problem-led, 11 slides | 11 | 4 |
| v3, insight at slide 3 | 11 | 6 |

The change was not design polish. Moving the insight to slide 3 and cutting 23 slides moved the meeting rate more than any visual decision in the deck.

## Quality checklist

- [ ] 11 sentences in five beats, read aloud
- [ ] The decision you want named before building
- [ ] One idea per slide, title is a claim
- [ ] Body text under 25 words per slide
- [ ] Source line on every number
- [ ] One font family, two weights
- [ ] 12-column grid, 64 px margin
- [ ] Two colours plus neutral, accent used once
- [ ] Charts labelled, bars from zero
- [ ] One economics number with visible arithmetic
- [ ] Projections in the appendix with assumptions
- [ ] Competitors named on the competition slide
- [ ] Weakest number shown and explained
- [ ] Five appendix slides for likely questions
- [ ] QA at 25% zoom, greyscale and phone
- [ ] Silent read by a stranger states the ask
- [ ] PDF under 10 MB, fonts embedded, phone-tested

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| No second meeting | 34 slides, feature-led, no single claim | Cut to 11, one idea per slide |
| Deck reflows on the reader's laptop | Sent as an editable file | Export a PDF with fonts embedded |
| Reader cannot say what you do | Title slide is a logo and a tagline | Put the one-line description on slide 1 |
| Chart distrusted | Truncated y-axis on a bar chart | Start bars at zero, keep the point in the title |
| Questions about a hidden number | Weak metric buried in the appendix | Show it on the slide and explain it |
| Deck looks like five authors | Four fonts and three accent colours | One master, one type scale, two colours |
| Numbers do not match the model | Deck built from memory | Reconcile every figure against the spreadsheet |
| Body unreadable on a phone | 18 px text at 16:9 | 24-28 px body, check on a phone |
| Presentation ran long | No rehearsal to a clock | Rehearse to 10 minutes, and to 3 |

## Copy-ready agent prompt

> Read the skill at the URL above and build a pitch deck with me. Ask me: what the product does, who the buyer is, the decision I want, my strongest three numbers and my weakest one. Then write the 11 sentences in five beats and read them back to me for approval before designing anything. Then give me the slide map with a claim title per slide, the type scale and grid values, the chart rules, the one economics slide with visible arithmetic, and the five appendix slides for the questions I will be asked. Finish with the QA checklist and the export settings. Do not add a slide that does not change the decision, and do not invent a number I have not given you.
