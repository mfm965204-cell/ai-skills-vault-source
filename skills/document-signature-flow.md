---
name: document-signature-flow
description: Send a contract for signature with a lawful e-signature
path in India, correct field placement, reminder cadence, an audit
trail and a retention rule.
version: 1.0.0
license: MIT
tags: [automation, contracts, esign, compliance, documents]
---

# Document Signature Flow

A signed PDF arrives as a scan with a squiggle, no timestamp, no
signer identity and no record of what was agreed. When the deal goes
wrong, that file proves nothing. The alternative is not a lawyer; it
is a process with fields, timestamps, an audit trail and a retention
rule.

This skill builds the flow: pick the signature type the law accepts,
place fields so a signer cannot skip a page, run a three-reminder
cadence, keep a hash and an audit trail, and delete the document on a
schedule.

## When to use this skill

- You send contracts as a PDF and ask for "a signed copy back".
- Two signers need to sign the same document and you are emailing versions.
- You cannot prove when a client accepted your terms.
- You have 400 signed documents in a folder and no retention rule.

Do NOT use for: drafting or reviewing contract terms (that is a
lawyer's job), or a registered agreement that needs stamp duty and
notarisation — those need physical execution.

## Stage 1 — Pick the signature type the law accepts

India recognises three practical paths, and they are not
interchangeable for every document.

1.1 Aadhaar eSign for most business contracts: it is an electronic signature backed by OTP to the signer's Aadhaar-linked mobile, and it carries a verifiable audit trail.

1.2 A digital signature certificate for filings and documents where a specific class of DSC is required, such as certain tax and registry documents.

1.3 A click-to-accept with a recorded audit trail for low-value terms — order forms, service terms, NDAs under a set value — where the platform's trail is the evidence.

| Path | Identity proof | Typical use | Watch out for |
|---|---|---|---|
| Aadhaar eSign | OTP to Aadhaar-linked mobile | most B2B contracts | signer must have Aadhaar-linked mobile |
| DSC token | certificate issued to a person | filings, registry documents | token and driver needed per signer |
| Click-to-accept | email plus OTP | terms, order forms, NDAs | keep the full audit trail, not just the PDF |
| Wet signature scan | none | physical execution | proves nothing about identity |

Gate: the chosen path is named in the send, and the document type is
one that path covers.

## Stage 2 — Prepare one document, not three

Signature blocks drift when the document is assembled per recipient.
Build one file and place fields on it.

2.1 Export a single PDF with page numbers, a document title in the header and the version in the filename: `service-agreement-v3-2026-11.pdf`.

2.2 Put every signature block on the last page with the name, designation, date and place pre-filled except the signature and date fields.

2.3 Initial every page for contracts above ₹1,00,000; a page initial field prevents a page being swapped after signature.

Gate: one PDF, numbered pages, versioned filename, and a signature
block with pre-filled signer details.

## Stage 3 — Order the signers and set the fields

Field placement is where signature flows fail: a signer skips the
annexure and signs the cover.

3.1 Decide parallel or sequential: parallel for two co-founders, sequential when one signature depends on the other's approval.

3.2 Place required fields on every page that needs one — signature, date, initials, and a checkbox for terms acceptance where relevant.

3.3 Make every field required and validate the date field to today or later, so a back-dated signature is impossible.

| Document type | Signers | Order | Fields per signer |
|---|---|---|---|
| NDA | 2 | parallel | signature, date, initials on 2 pages |
| Service agreement | 2 | sequential | signature, date, initials on all pages |
| Order form | 1 | — | signature, date, terms checkbox |
| Vendor onboarding | 2 | sequential | signature, date, bank detail confirmation |

3.4 Keep the field map in version control next to the template, so a template edit cannot silently drop a field:

```yaml
reminders_days: [3, 7, 14]
expiry_days: 30
fields:
  - { signer: 1, page: 1, type: signature, required: true }
  - { signer: 1, page: 1, type: date, required: true }
  - { signer: 1, pages: [2, 3], type: initials, required: true }
on_complete:
  webhook: /hooks/contract-signed
  store: { certificate: true, sha256: true }
```

Gate: every required field is on the right page for the right signer,
and the flow cannot complete with a field empty.

## Stage 4 — Verify the signer before sending

A contract signed by the wrong person at the right company is worse
than unsigned.

4.1 Send to a named individual at a company domain, and confirm the person is authorised to sign — the title in the email signature is not proof.

4.2 Require an OTP or an email verification step on the platform, so the trail records an identity check and not just a click.

4.3 For high-value contracts, add one confirming email to a second contact at the company.

Gate: every signer's identity check is recorded in the audit trail
with a timestamp.

## Stage 5 — Run a three-reminder cadence

Most documents are signed on the first reminder, not on the first
send.

5.1 Send on a Tuesday to Thursday morning IST; a Friday afternoon send waits until Monday anyway.

5.2 Remind on day 3, day 7 and day 14, each from the same thread with the document link and one line on what is outstanding.

5.3 Expire the request at day 30 and mark the document void, so a stale link cannot be signed months later against changed terms.

Gate: three reminders logged per recipient, and every request carries
a 30-day expiry.

## Stage 6 — Capture the audit trail, not just the PDF

The PDF is the artefact; the trail is the evidence. Store both.

6.1 Download the completion certificate with each signature: signer name, email, IP address, timestamp in IST and the method used.

6.2 Compute a SHA-256 hash of the final PDF and store it with the certificate, so tampering is detectable later.

6.3 Store the certificate and hash in the contract record, not in a mail attachment that will be lost.

```bash
sha256sum service-agreement-v3-signed.pdf > service-agreement-v3-signed.sha256
```

Gate: every completed document has a certificate, a hash and a record
row linking the two.

## Stage 7 — Handle refusals, changes and expiry

The flow needs a defined path for the three ways it stops.

7.1 A refusal is recorded with the reason and the document is closed as refused, never re-sent unchanged.

7.2 A change request restarts as a new version with a new version number, and the old request is voided so two versions cannot be live.

7.3 An expired request is re-sent only after confirming the terms still apply.

Gate: no two versions of the same document are open at once, and every
closed request carries a reason.

## Stage 8 — Set the retention and deletion rule

Signed documents are personal data as well as evidence. Both duties
apply.

8.1 Retain signed contracts for 8 years from the end of the financial year they relate to, which matches the working assumption for Indian tax and limitation purposes; confirm the number with your accountant.

8.2 Delete draft and voided documents after 90 days, and expired unsigned requests after 30.

8.3 Record the deletion in a log with the document id and date, and never delete a signed document without a legal hold check.

Gate: a retention rule exists per document class, and deletions are
logged.

## Stage 9 — Automate the handoff after signature

The value of a signed contract is what happens next: billing, access,
onboarding.

9.1 On completion, trigger the next step — create the invoice, provision the account, or open the onboarding task — from the webhook, not from someone noticing the email.

9.2 Send a confirmation to both parties with the signed PDF attached and the hash in the footer.

9.3 Write the signed date and expiry into the contract record so renewals are visible 60 days before they are due.

Gate: a signed contract produces an invoice or an onboarding task
within 5 minutes, and a renewal reminder at 60 days.

## Worked example - 180 contracts a quarter, no lost signatures

A services firm sending 180 contracts a quarter by email and asking
for a scan back.

| Measurement | Before | After | Change |
|---|---|---|---|
| Median days to signature | 11 | 3 | three-reminder cadence |
| Documents needing a re-send | 34% | 6% | required fields, no missing pages |
| Signed files with a timestamp | 12% | 100% | platform completion certificate |
| Disputes over agreed terms | 4 per quarter | 0 | hash plus version control |
| Manual steps per contract | 7 | 2 | webhook triggers the invoice |
| Storage | shared drive folder | contract record plus certificate | retention rule |

The 34% re-send rate had one cause: signers were skipping the annexure
page because the only signature field sat on the last page of the main
agreement. Adding an initial field on every annexure page removed
almost all of it.

The disputes ended when the hash went into the record. Two clients
claimed the terms had changed after signing; the stored hash and the
completion certificate answered both in minutes.

The one thing to avoid: the first version sent in parallel to two
signers where the second signer's approval was a precondition. Both
signed, and the company was bound before the internal approver had
seen it. Sequential order exists for that reason.

## Quality checklist

- [ ] Signature path named and appropriate to the document type.
- [ ] One versioned PDF with numbered pages.
- [ ] Signature block pre-filled except signature and date.
- [ ] Initials required on every annexure page.
- [ ] Signer order set to parallel or sequential deliberately.
- [ ] All fields required, date validated to today or later.
- [ ] Named signer at a company domain, identity checked by OTP.
- [ ] Three reminders at day 3, 7 and 14.
- [ ] 30-day expiry on every request.
- [ ] Completion certificate downloaded per signature.
- [ ] SHA-256 hash stored with the certificate.
- [ ] No two versions open at once.
- [ ] Retention rule per document class, deletions logged.
- [ ] Post-signature step triggered by webhook.
- [ ] Renewal reminder scheduled 60 days ahead.

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Signature page left blank | The field was optional or absent on that page | Make every field required and add initials per page |
| Client says they never received it | Send went to a personal address and landed in spam | Send to a company domain and confirm delivery on day 1 |
| Contract signed after terms changed | No expiry, so an old link stayed valid | Expire requests at 30 days and void on version change |
| Two versions signed by different people | A new version was sent without voiding the first | Void the old request in the same action as the re-send |
| Cannot prove the signing time | Only the PDF was kept | Store the completion certificate with the platform timestamp |
| Signed document deleted in a cleanup | Retention rule applied to drafts and signed files alike | Classify documents first; legal hold check before deletion |
| Invoice sent before the contract was signed | The next step depended on a human noticing the email | Trigger from the completion webhook only |

## Copy-ready agent prompt

> Read the skill at the URL above and set up my signature flow. Choose the lawful path per document type, prepare one versioned PDF with numbered pages and pre-filled signature blocks, place required fields with initials on every annexure page, set parallel or sequential signer order, and add OTP identity verification. Configure reminders at day 3, 7 and 14 with a 30-day expiry, store the completion certificate plus a SHA-256 hash in the contract record, and trigger the post-signature step from the webhook. Report median days to signature and the re-send rate after 20 documents. Stop and show me the field map if any required field is optional.
