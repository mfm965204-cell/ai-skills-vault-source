---
name: incident-notes
description: "Writes the incident note for an Orchard storefront outage or rollback from the release thread and the deploy log. Use when asked to \"write the incident note\", \"write up the rollback\", or \"do the post-incident summary\"."
version: 1.0.0
license: "See the source repository"
tags: [engineering, incident, notes]
---

# Incident Notes

Write the note within one working day of the incident, while the release thread is still fresh.

## Steps

1. Read the release thread from the first message of the deploy to the all-clear.
2. Pull the deploy log for the tag: `make deploy-log ENV=prod RELEASE=&lt;tag&gt;`.
3. Write the note in `docs/incidents/&lt;date&gt;-&lt;slug&gt;.md` with four sections: what customers saw, timeline in UTC, cause, what changes.
4. State customer impact as numbers from the checkout dashboard: failed checkouts, and minutes above the latency threshold.
5. List each follow-up as one line with one owner.

## Gotchas

- The timeline uses the timestamps in the deploy log, not the times people posted. Messages lag the events by minutes.
- Name systems, not people. "The promote target does not check the payments queue", not who ran it.
