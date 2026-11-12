---
name: industry-brief
description: >
  Build your own daily industry & competitive brief: a short, sourced digest of
  industry news, platform changes, competitor moves, ecosystem shifts, and audience
  chatter, ready to paste or auto-post to a team channel. Company-agnostic: on first
  use it interviews you (industry, competitors, channels, audience, destination),
  saves a Brief Profile, then produces the brief on demand or on a schedule.
  Trigger on "daily brief", "industry brief", "competitor watch", "build my morning
  brief", "what happened in my market today", or "set up a brief for my team".
---

# Industry Brief

## Changelog
- 2026-11-12: v1. Generalized from an in-house daily growth brief into a standalone,
  company-agnostic skill. Adds Brief Profile onboarding, configurable sections,
  severity scoring, dedupe, and scheduling.

## Purpose / When to use
Produce a high-signal brief about the user's market in under two minutes of reading.
Use it for a daily/weekly digest, a one-off "what moved today", or to stand up a
recurring brief for a team channel. You prepare it; the user decides what ships
(unless they set an auto-send rule).

## Steps

### 1. Build the Brief Profile (first run only)
If no profile exists in the user's project memory/notes, interview them in grouped
questions (not one at a time):

1. **Company & category**: what they sell, who to, which market.
2. **Competitors**: 3-8 names, tagged *direct* / *adjacent* / *emerging*.
3. **Beats**: the topics that matter (e.g. SaaS GTM, AI tooling, their ecosystem,
   regulation, pricing). Default sections below apply if they have no view.
4. **Paid channels** they run (search, Meta, LinkedIn, etc.): drives section 2.
5. **Audience**: where their buyers/users talk (Reddit, X, LinkedIn, forums,
   communities, review sites).
6. **Delivery**: where it goes (Slack channel, email, chat only), time, cadence
   (daily / weekdays / weekly), and whether it **auto-sends** or waits for approval.
7. **Voice**: terse vs. narrative, banned words, emoji rules.

Save the profile and reuse it. Update it when corrected. Never hard-code a profile
into this file.

### 2. Gather (last ~24h; Mondays cover the weekend; weekly = 7 days)
- Search the web per beat and per named competitor. Check primary sources first
  (company blog, changelog, pricing page, press release, ad-platform release notes,
  the audience's forums), then reputable press.
- Pull from any connected tool the user authorized (analytics, ad platforms,
  search console) instead of asking for numbers.
- Skip anything already covered in the previous brief unless there is a real update
  (state the update).

### 3. Filter
Keep an item only if it would change what the team **does, watches, or says**.
Cut press-release fluff, rehashes, and opinion with no new fact. One item = one
source link + one-line "so what".

### 4. Write, using these sections in order
Drop any section with nothing real ("Nothing material today" is a valid line).

1. **Industry news**: general market/tech/GTM news. No competitor-specific items.
2. **Platform changes affecting paid distribution**: policy, algorithm, format,
   pricing, or measurement changes on the user's ad channels. Include the
   paid-distribution implication.
3. **Competitor watch**: named competitors only. The ONLY section that uses color:
   - 🟢 minor: incremental update, no action
   - 🟡 watch: overlaps our space or signals a direction; monitor
   - 🔴 act: pricing change on a core feature, big raise, or launch that overlaps
     our core. Say what we should do or decide.
   Each line: *Competitor: move: severity: so what for us*.
4. **Ecosystem**: adjacent-category moves, partners, platforms we build on. 1-3 items.
5. **Audience radar**: what buyers/users are asking for, praising, or frustrated by.
   Quote sparingly, link the thread, flag recurring themes.

### 5. Deliver
- Show the brief in chat, paste-ready.
- If the user enabled **auto-send**, post to the configured destination after
  writing; otherwise stop and ask for approval first.
- To make it recurring, set up a scheduled task at the saved time with the profile
  and this skill as the prompt. Confirm cadence and destination before creating it.

## Gotchas & learnings
- **Never invent or "correct" a stat** about the user's company. Report what the
  source said, attributed. Verify the user's own numbers with them or their
  source-of-truth before stating any.
- **Stale is worse than empty.** Check the date on every source. Drop anything
  older than the window unless it is newly relevant, and say why.
- **Severity needs a reason.** A 🔴 without a stated "so what / decision" is a 🟡.
- **Color discipline.** Severity emoji appear in Competitor watch only. No other
  decoration.
- **Platform changes vs. news.** Ad-platform changes go in section 2 even if
  reported as news.
- **Competitor claims are claims.** Label unverified launches, leaks, and rumors
  as such, with confidence (High / Medium / Low).
- **Don't pad.** A short brief people read beats a long one they skip.
- **Rate sources.** Prefer primary > trade press > aggregator > social. Flag
  anything single-sourced.

## Output format
```
📰 {Brand/Team} Brief: {date}

Industry news
- {Headline}: {so what}. [source]

Platform changes (paid)
- {Change}: {implication}. [source]

Competitor watch
- 🔴/🟡/🟢 {Competitor}: {move}. So what: {action/decision}. [source]

Ecosystem
- {Item}: {so what}. [source]

Audience radar
- {Theme}: {evidence}. [thread]
```
Plain, concise, paste-ready. Never a downloadable file unless asked.
