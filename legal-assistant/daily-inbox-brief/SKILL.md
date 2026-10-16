---
name: daily-inbox-brief
description: Weekday-morning Gmail scan for a law firm. Finds items that need the attorney's attention and returns a short prioritized brief with drafts ready for approval. Use when the attorney asks for the morning brief, inbox check, or "what needs my attention."
---

# Daily Legal Inbox Brief

**Status:** Approved
**Type:** New skill
**Canonical copy:** `legal-assistant/daily-inbox-brief/SKILL.md` in the Ai-skills repo. Do not keep a second copy in a project or on Drive. Projects reference this file.

## Changelog
- 2026-10-16: Approved. Pushing straight to main from now on.
- 2026-10-16: First draft.

## Purpose / When to use
Turn the last day of firm email into a one-page brief: what needs the attorney today, what can wait, and what is already drafted. Run every weekday morning, or on request.

## Steps
1. **Load the firm profile** from the project (attorney name, firm, practice areas, working hours, signature, fee schedule, intake questionnaire). If it is missing, ask once in one grouped message and save it to the project. Never store it in this repo.
2. **Confirm Gmail access.** If no Gmail tool is connected, say so in one line and stop. Do not invent emails.
3. **Scan** email since the last brief (default: since 8am the previous weekday). Include the inbox and any starred or labeled client threads.
4. **Classify** each thread:
   - **Act today:** deadline within 7 days, an agency action (USPTO office action, notice, refusal), a client waiting more than 24 hours, a contract with a signing date, overdue payment.
   - **This week:** new inquiries, scheduling requests, opposing counsel, upcoming maintenance deadlines (for example Section 8 windows), non-urgent client questions.
   - **FYI:** receipts, filing confirmations, thank-yous, newsletters.
   - **Ignore:** marketing and spam, counted but not listed.
5. **Extract for each Act and This-week item:** client and matter, what is being asked, the deadline and its source, and one concrete next step.
6. **Check the calendar** (Google Calendar) for today's events and for open slots when a scheduling request needs a reply.
7. **Draft replies** for items that need a response. Use the firm's signature and tone. Mark any draft that depends on a legal judgment as "Needs your review first."
8. **Output the brief** in the format below. Then stop. Nothing is sent, filed, or scheduled without approval.

## Gotchas & learnings
- **Sample vs real data:** Example briefs must be labeled fictional. Never reuse sample client names in a real brief.
- **Deadlines:** Use the date stated in the email or agency notice. Say "verify in USPTO TSDR before relying on it." Do not compute a final legal deadline from memory. Flag extension options, but leave the decision to the attorney.
- **Never send.** Create drafts only. The attorney approves every outbound message.
- **Confidentiality:** Client emails are privileged. Do not paste email content into any external tool other than the connected Gmail, Calendar, and Drive.
- **Ambiguity:** If a thread could be urgent, put it in Act today and say why. A false alarm costs less than a missed deadline.
- **Quiet days:** If nothing needs attention, say "Nothing urgent" and list only the FYI count.
- **Attachments:** Trademark applications and contracts that arrive by email trigger a separate review. Note them in the brief and ask whether to start the review (contracts use the Contract Review skill). Do not start it unprompted.
- **Skill gap:** Trademark application review and client email drafting are not yet separate skills. Add them once the attorney confirms the checklist and templates.

## Output format
```
# Morning Brief, <weekday> <Mon DD>
Scanned <n> emails since <time>. <x> need you, <y> do not.

## Act today
1. **<Item>, <Client / matter>**
   - <Deadline and days left>. <One-line what and why.>
   - **Next step:** <action>. <Draft ready / on request>

## This week
<same format, shorter>

## FYI
- <count and one-line list>

## Drafts ready for your approval
| # | To | Subject | Status |

## Today's calendar
<time event, comma-separated>
```
Keep the brief under one screen where possible. Put the highest-risk item first.
