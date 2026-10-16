---
name: contract-review
description: Reviews creator contracts (brand deals, sponsorships, UGC, licensing, agency and management agreements) and produces initial redlines. Always checks usage rights, net payment terms and kill fees. Use when a contract arrives or the attorney says "review this contract" or "redline this."
---

# Creator Contract Review and Initial Redlines

**Status:** DRAFT, awaiting sign-off
**Type:** New skill
**Canonical copy:** `legal-assistant/contract-review/SKILL.md` in the Ai-skills repo. Do not keep a second copy in a project or on Drive.

## Changelog
- 2026-10-16: First draft.

## Purpose / When to use
Give the attorney a fast first pass on a creator's contract: a risk summary and redlines she can edit, not a final legal opinion. The client is the creator unless told otherwise. Three items are checked on every contract: **usage rights, net payment terms, kill fees.**

## Steps
1. **Get the deal context.** Ask once, grouped, for anything not already in the project or thread: who the client is, the fee, deliverables, platforms, dates, whether paid media is expected, how much leverage the client has, and any must-haves. Do not start the redline without knowing the client's side.
2. **Read the full contract**, including exhibits, SOWs, briefs and linked terms. Note anything referenced but not attached.
3. **Run the three core checks** (below). Quote the clause number and text for each. If the contract is silent, mark it MISSING and draft a clause to add.
4. **Run the secondary scan:** revisions and approval windows, exclusivity and non-compete, name and likeness, FTC and platform disclosure, indemnity, liability cap, termination, confidentiality, morality clause, payment in product or "exposure," taxes and W-9, agency commission, governing law and venue, auto-renewal, assignment.
5. **Draft redlines.** For each issue give the original text, the proposed replacement, a fallback position, a one-line reason the client can understand, and a priority.
6. **Output the review** in the format below. Redlines go in the chat. Create a Word file with tracked changes only if the attorney asks.
7. **Stop for approval.** Nothing is sent to the client or the counterparty without the attorney's approval.

## The three core checks

### 1. Usage rights
- **Grant type:** License or assignment? Work-for-hire? Prefer a limited license. Flag any assignment or work-for-hire.
- **Scope:** Organic only, or paid ads, whitelisting or Spark Ads, TV, OOH, email, website, packaging, retail?
- **Duration:** Fixed term or perpetual and irrevocable? Is there a renewal or extension fee?
- **Territory:** Limited or worldwide?
- **Media and edits:** Who can edit, cut down, or create derivative works? Raw footage included?
- **Name, likeness, voice, handle:** Included in the grant? For how long?
- **AI:** Any right to train models, clone voice or likeness, or generate synthetic content? Strike unless separately paid.
- **Post-termination:** Does usage end when the contract ends or when the brand cancels without paying in full?
- **Pricing:** Is paid or extended usage priced separately from the base fee?

### 2. Net payment terms
- **Days:** Net 30 or less is the starting position. Flag net 45, 60, 90, or "upon brand approval" with no outside date.
- **Trigger:** Invoice date, posting date, or approval date? Flag "pay when paid" language that ties payment to the brand's client.
- **Deposit:** Is there an upfront payment on signing? Is it non-refundable?
- **Late payment:** Interest or a late fee? Right to remove content or suspend work if unpaid?
- **Milestones:** For larger deals, are payments split by milestone?
- **Deemed approval:** Does silence after delivery count as approval so payment is triggered?
- **Offsets:** Can the brand deduct, withhold, or offset?
- **Mechanics:** Currency, method, who pays fees, and tax forms.

### 3. Kill fees
- **Exists?** If missing, add one.
- **Who can cancel?** Mutual or brand-only? What notice is required?
- **Amount:** Tiered by stage is the starting position. See defaults below.
- **Deposit:** Kept by the creator on cancellation.
- **Expenses:** Out-of-pocket costs reimbursed, including non-cancellable bookings.
- **Content:** If killed, does the brand get any usage? Default is none unless paid in full.
- **Brand-caused delay:** Fees for postponed shoots or late approvals.
- **Revisions:** Capped, with additional rounds billed.

## Default starting positions
These are the skill's opening asks, not legal rules. The attorney confirms or edits them. Adjust per deal using the leverage noted in step 1.

| Item | Opening position | Typical fallback |
| --- | --- | --- |
| Usage | Limited license, organic posting on named channels, fixed term | Add paid usage for a stated term at a stated fee |
| Paid media / whitelisting | Separate fee, fixed term, per-platform | Short term bundled at a higher base fee |
| Perpetual / irrevocable | Strike | Long fixed term with a renewal fee |
| Payment | Net 15 from invoice, 50% on signing for larger deals | Net 30 from invoice |
| Late fee | 1.5% per month, right to pause usage if unpaid | Interest at the legal rate |
| Kill fee | 25% before work starts, 50% after work starts, 100% after delivery | 50% flat after signing |
| Revisions | Two rounds, extras billed hourly | Three rounds |

## Gotchas & learnings
- **The client is the creator.** Do not suggest changes that favor the brand.
- **Do not state legal conclusions as fact.** Phrase as "this clause may let the brand..." and flag items for the attorney's judgment. Enforceability depends on the governing law, which needs the attorney's review.
- **Quote, don't paraphrase.** Always cite the clause number and the exact text being changed.
- **Missing is a finding.** A contract with no kill fee, no usage limits, or no payment date is worse than one with a bad clause. Draft the missing clause.
- **Exhibits override.** Check SOWs, briefs and linked terms. Terms there can contradict the main body.
- **Defined terms hide the grant.** Read the definitions of "Content," "Materials," and "Deliverables" before judging the usage clause.
- **Rank the redlines.** Must-have, Should-have, Nice-to-have. Too many changes on a small deal can lose it, so say which to trade away.
- **Plain language for the client.** Every redline reason should be understandable to a non-lawyer.
- **No docx by default.** Redlines stay in the chat unless asked for.

## Output format
```
# Contract Review: <Client> / <Brand or Counterparty>
**Deal:** <fee, deliverables, dates>   **Contract type:** <type>   **Reviewed:** <date>

## Bottom line
<Two or three sentences: sign as is, sign with changes, or push back hard, and the top risks.>

## Core checks
| Check | Finding | Clause | Risk |
| --- | --- | --- | --- |
| Usage rights | <summary> | <§> | High / Med / Low / MISSING |
| Net payment terms | <summary> | <§> | ... |
| Kill fee | <summary> | <§> | ... |

## Redlines
### 1. <Issue>, <Must-have / Should-have / Nice-to-have>
**Clause:** §<n>
**Original:** "<exact text>"
**Proposed:** "~~struck text~~ **inserted text**"
**Fallback:** <acceptable compromise>
**Why:** <one line for the client>

## Missing clauses to add
<Clause text for each.>

## Other issues
<Short list from the secondary scan.>

## Questions for the client
<Anything needed to finalize.>

## Next steps
<Send redline to counterparty / call client / draft cover email.>
```
