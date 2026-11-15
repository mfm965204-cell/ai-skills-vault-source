---
name: launch-day-playbook
description: Launch a product publicly without wasting the one day of attention you get - a readiness gate, positioning, demo assets, a channel plan with effort and return, IST timing, launch copy, a comment playbook and a 48-hour follow-up.
version: 1.0.0
license: MIT
tags: [marketing, launch, product-hunt, community, positioning, growth]
---

# Launch Day Playbook

A launch is a single day of concentrated attention, and most of it is decided before the day starts: whether the product holds 200 concurrent users, whether the demo GIF explains it in 8 seconds, and whether 20 people are ready to comment in the first hour.

This skill gives you a readiness gate you cannot skip, a channel plan with honest effort and return, and a 48-hour follow-up that turns a traffic spike into a list.

## When to use this skill

- A product, feature or major version is ready and you want public attention on a specific date.
- You have never launched and do not know what to do with the day.
- A previous launch produced traffic and no signups, and you want to know why.
- You are launching in India and need to time it against a US-centric internet.

Do NOT use for: ongoing content marketing (that is a cluster strategy, not a launch), or launching something that cannot survive a traffic spike - fix that first.

## Stage 1 - Pass the readiness gate or move the date

1.1 Ten checks, all pass or the date moves. A launch is not a deadline you can negotiate with; a broken product on launch day is a public failure that costs more than a delay.

| Check | Pass condition |
|---|---|
| Signup works | 20 real signups tested, no manual steps |
| Onboarding | a new user reaches first value in under 5 minutes |
| Payments | a real ₹1 test payment completes and reconciles |
| Load | 200 concurrent users for 10 minutes with no errors |
| Mobile | the landing page and signup work on a mid-range Android |
| Support | an email address that a human answers within 4 hours |
| Analytics | signup and activation events visible in the dashboard |
| Legal | terms, privacy policy and refund policy linked |
| Demo | a 15-second GIF or video that explains it silently |
| Rollback | a one-command way back to the previous version |

1.2 Fix the two worst checks and re-test. Do not fix all ten at once in the last 48 hours; that is how a launch ships a new bug.

1.3 Set the success metric before the day: signups, activations, paying customers, or waitlist. One metric, written down.

1.4 Tell your current users the date. A launch with no existing users is a cold start and needs a different plan.

Gate: all ten checks pass, success metric written.

## Stage 2 - Write the positioning in one sentence

2.1 Format: "For [who] who [problem], [product] is a [category] that [outcome]. Unlike [alternative], it [difference]."

2.2 Keep the category familiar. A new category needs a paragraph of education; a known category with one clear difference gets understood in 5 seconds.

2.3 Name the alternative your buyer actually uses today: a spreadsheet, a WhatsApp group, an intern. Comparing to a competitor nobody knows is wasted words.

2.4 Test the sentence on 5 people outside the company. If 3 cannot repeat it back, rewrite it before launch day.

2.5 Write the tagline separately: 6 words maximum, no jargon, no puns.

Gate: one sentence that 3 of 5 strangers can repeat back.

## Stage 3 - Build the assets that carry the launch

3.1 The demo asset matters more than the copy. A 15-second silent screen recording that shows the core action is worth more than 400 words.

3.2 Capture at 1280x720, 30 fps, under 3 MB, and make sure the first 2 seconds show the outcome, not the login screen.

3.3 Five screenshots with captions: the outcome, the workflow, the integration, the pricing, the dashboard. Each caption under 12 words.

3.4 Write a 100-word description and a 300-word description. Directories want the short one; your blog post wants the long one.

3.5 Have a founder photo and a one-line bio ready. People back people, and directories surface the maker.

| Asset | Spec | Used on |
|---|---|---|
| Demo GIF | 15 s, under 3 MB, silent | Product Hunt, X, LinkedIn |
| Screenshots | 5, 1280x720, captioned | listing, landing page |
| Logo tile | 240x240 PNG | directory listings |
| Short description | 100 words | directories, newsletters |
| Long description | 300 words | blog, press |
| Founder photo | 400x400 | maker profile |

Gate: every asset above exists and renders on a phone.

## Stage 4 - Choose channels by effort and return

4.1 You cannot do eight channels well in one day. Pick three primary and two secondary, and prepare them all in advance.

4.2 Know what each channel rewards: directories reward novelty and a good GIF, communities reward participation history, LinkedIn rewards a personal story, HN rewards technical substance.

| Channel | Prep needed | Effort | Realistic return |
|---|---|---|---|
| Product Hunt | listing, assets, 20 supporters | high | 200-2,000 visits |
| Hacker News | a technical post, no marketing | high | 0 or 20,000 |
| Reddit niche sub | 30 days of participation first | medium | 100-800 visits |
| LinkedIn | founder post, 3 comments early | low | 500-3,000 impressions |
| X thread | 6 tweets, images | low | variable, often low |
| WhatsApp and Telegram groups | personal asks, no spam | low | 20-100 visits, high intent |
| Existing email list | a short email | low | highest conversion |
| Niche newsletter | pitch 2 weeks ahead | medium | 100-1,000 visits |

4.3 Never launch on a channel where you have no history. A first post in a subreddit is removed by the automod nine times out of ten.

4.4 Ask 20 people for the first-hour comments on Product Hunt, personally, one message each. Generic broadcast asks get ignored.

4.5 Prepare the HN post as a technical write-up with numbers, and expect it to be ignored. It is the highest-variance channel there is.

Gate: three primary channels with assets ready, 20 supporters asked personally.

## Stage 5 - Pick the time, in IST

5.1 Product Hunt resets at 12:01 AM Pacific, which is 12:31 PM IST. Launching at 12:31 PM IST gives you the full day.

5.2 For Indian audiences, post on LinkedIn at 09:30-11:00 IST on Tuesday-Thursday. For US audiences, post at 20:00-22:00 IST to land in their morning.

5.3 Never launch on a Friday, a public holiday, or the week between Christmas and New Year.

5.4 Avoid the day a major competitor or a big industry event dominates the same channel.

5.5 Generate every launch link with a UTM tag before the day, from one script, so no channel is left untagged:

```bash
BASE=https://example.com/?utm_source=%s&utm_medium=%s&utm_campaign=launch-nov15
for pair in producthunt:referral linkedin:social x:social email:email hn:referral; do
  ch=${pair%%:*}; md=${pair##*:}
  printf "$BASE\n" "$ch" "$md"
 done
```

5.6 Put the generated URLs in a single sheet and copy from it during the day. A retyped link loses its attribution and the launch report becomes fiction.

| Target audience | Channel | Best IST window |
|---|---|---|
| India B2B | LinkedIn, email | 09:30-11:00 Tue-Thu |
| India consumer | Instagram, WhatsApp | 19:00-21:30 |
| US B2B | Product Hunt | 12:31 onward, all day |
| Global technical | Hacker News | 19:00-21:00 (US morning) |
| Developer India | X, Discord | 21:00-23:00 |

Gate: launch time written down with the timezone arithmetic shown.

## Stage 6 - Write the launch copy

6.1 The first line does the work. "We built X because Y was broken for us" beats "Introducing X, the platform for Z".

6.2 Structure: the problem in one line, what you built, one proof point with a number, the ask, the link. Under 150 words for a social post.

6.3 Include the price or say it is free. Hiding pricing on launch day produces traffic that bounces when it finds out.

6.4 One call to action. "Try it free" or "Join the waitlist" - not both, not three.

6.5 Write the comment you will post first yourself: the story, the trade-off, and one thing you would like feedback on.

6.6 Prepare a short version for directories and a long version for the blog, both consistent on numbers.

6.7 Keep the post as a template with the blanks marked, so the version you paste at 21:00 is the one you wrote at 10:00:

```text
We built <product> because <the specific thing that broke for us>.

It does <one outcome> in <time or count>.

<one proof point with a number>.

Free to try, <price> after that. Link in the first comment.

What I would most like feedback on: <one specific question>.
```

6.8 Read the post on a phone before publishing. Line breaks that look fine on a laptop turn into a wall of text in a feed.

Gate: copy written for each primary channel, first comment drafted.

## Stage 7 - Run the day

7.1 Block 6 hours on the day. Launch day is a conversation, and unanswered comments read as indifference.

7.2 Reply to every comment within 30 minutes for the first 6 hours. On Product Hunt, comment velocity in the first 4 hours drives ranking more than total votes.

7.3 Answer technical questions with specifics and admit what is missing. "Not yet - here is the plan" lands better than a dodge.

7.4 Never ask for upvotes; ask for feedback. Vote-asking gets listings penalised and reads badly to everyone else.

7.5 Watch the error dashboard, not just the traffic graph. A 500 error during the spike is the only thing that can turn a good launch into a bad one.

7.6 Post one update mid-day: a number, a thank-you, a lesson. It brings a second wave.

7.7 Do not touch pricing or the landing page during the day. Change nothing that could break while 2,000 people are looking.

Gate: every comment answered within 30 minutes, error rate watched hourly.

## Stage 8 - Prepare for the traffic spike

8.1 Test 200 concurrent users for 10 minutes on the exact production configuration, not on a staging box with more memory.

8.2 Put the landing page behind a CDN with a 60-second cache, and make sure the signup form posts to a queue or a rate-limited endpoint.

8.3 Add a queue for anything expensive: sending the welcome email, generating a report, calling an LLM. A synchronous call in the signup path is what falls over first.

8.4 Set a hard timeout on every external call in the signup path, and a fallback that still creates the account.

8.5 Watch four numbers hourly: requests per minute, p95 latency, error rate, signup completions. A latency spike with flat errors usually means the database, not the app.

8.6 Have the rollback command written out and one person authorised to run it.

8.7 Put a queue between signup and every slow side effect: welcome email, workspace creation, any model call. The signup itself must take under 400 ms at p95.

8.8 Watch the database connection count during the spike. Most launch outages are connection pool exhaustion, not CPU.

Gate: a load test at 200 concurrent users with the four numbers recorded.

## Stage 9 - Measure the day honestly

9.1 Track the funnel: visits, signups, activation (first real action), and paying. Most launches lose 90% between signup and activation, and that is the number to fix next week.

9.2 Separate traffic by channel with UTMs on every link. Without them, you will conclude the wrong channel worked.

9.3 Record votes, comments, and rank for directories, but do not confuse them with business outcomes.

9.4 Note the three questions that came up most in comments. They are your next three pieces of copy.

| Metric | Typical launch | Good launch |
|---|---|---|
| Visits | 300-1,000 | 3,000+ |
| Signup rate from visits | 5-12% | 15%+ |
| Activation within 24 h | 20-40% | 50%+ |
| Paying within 7 days | 1-3% | 5%+ |
| Support emails | 20-50 | under 20 |

Gate: a table with the four funnel numbers and the top three repeated questions.

## Stage 10 - Follow up for 48 hours, then keep going

10.1 Send a thank-you and a recap to everyone who signed up within 24 hours, with the one thing you learned from launch day.

10.2 Email the people who commented but did not sign up, individually, with the specific thing they asked about.

10.3 Publish a "what we learned on launch day" post within a week. It gets a second wave of attention and it ranks for your product name.

10.4 Turn the three repeated questions into a FAQ, a doc page and one onboarding email.

10.5 Fix the biggest activation drop before the next launch. The launch creates the list; activation creates the business.

10.6 Put the next launch date in the calendar 90 days out. Launches compound when they are a rhythm, not an event.

10.7 Answer the same three questions in public, once each, in the week after. The people who asked them are your best-qualified readers.

10.8 Update the landing page with the objection you heard most, in the user's own words.

Gate: recap sent, learnings post published, activation fix scheduled.

## Worked example

A ₹499/month scheduling tool for small clinics, launched on Product Hunt and LinkedIn.

| Hour (IST) | Action | Result |
|---|---|---|
| 12:31 | Product Hunt listing live, first comment posted | 40 visits in 1 h |
| 13:00 | LinkedIn founder post | 1,800 impressions |
| 15:00 | 20 supporters commented | rank 6 in category |
| 18:00 | mid-day update post | second wave, 600 visits |
| 21:00 | Hacker News technical post | 12 points, no traction |
| Day 2 | recap email to 214 signups | 38 activated |

Outcome: 214 signups, 38 activations, 6 paying customers in week one. The HN post produced nothing, which is normal, and the mid-day update produced more than the initial post.

## Quality checklist

- [ ] All ten readiness checks pass, or the date moved
- [ ] One success metric written down
- [ ] Positioning sentence repeatable by 3 of 5 strangers
- [ ] 15-second silent demo under 3 MB
- [ ] Five captioned screenshots
- [ ] 100-word and 300-word descriptions ready
- [ ] Three primary channels chosen with assets prepared
- [ ] 20 supporters asked personally for first-hour comments
- [ ] Launch time in IST with the timezone arithmetic checked
- [ ] Copy under 150 words with one call to action
- [ ] Price shown on the launch page
- [ ] Load test at 200 concurrent users passed
- [ ] Queue in the signup path, timeouts on external calls
- [ ] Rollback command written, one person authorised
- [ ] UTMs on every link
- [ ] Comment reply target of 30 minutes for 6 hours
- [ ] Recap email within 24 hours and a learnings post within a week

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| 2,000 visits, 12 signups | Landing page describes the category, not the outcome | Rewrite the first screen around the outcome and the demo GIF |
| Signups but nobody activates | Onboarding asks for setup before showing value | Show a populated example before asking for anything |
| Site down at peak | Untested concurrency and a synchronous email call | Queue the email, load test at 200 users |
| Listing ranked low despite votes | All votes arrived in the first hour from one network | Spread asks across the day, focus on comments |
| Comments went unanswered | Nobody staffed the day | Block 6 hours and assign one owner per channel |
| HN post removed | Account with no history posting a product | Participate for a month first, or skip HN |
| Traffic came from the wrong channel | No UTMs | Tag every link, re-check attribution next launch |
| Launch buzz, no revenue | No price on the page and no clear buyer | Show pricing, name the buyer in the first line |
| Cannot tell which channel worked | Links copied by hand without UTMs | Generate every link from one script before the day |
| Signup hangs at peak | Synchronous email or model call in the request path | Queue the side effect, keep signup under 400 ms p95 |

## Copy-ready agent prompt

> Read the skill at the URL above and plan my launch. Ask me: what I am launching, who buys it, the price, my current users and my launch date. Then run the ten readiness checks and tell me plainly whether to launch or move the date. Then write the positioning sentence, the tagline, the 15-second demo shot list, the 100-word description, and the copy for my three primary channels with a call to action each. Give me the launch time in IST with the timezone arithmetic, the comment reply plan for the day, the 200-user load test plan, and the metrics table. Do not invent traction numbers or user counts I have not given you.
