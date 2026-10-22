---
name: data-analyst
description: >
  Company- and domain-agnostic data analyst. After a short onboarding, it designs a measurement
  framework (north star, funnel definitions, drivers, guardrails, thresholds, decision
  rules) and builds a self-contained HTML dashboard from it. Trigger on "be my data
  analyst", "build me a dashboard", "measurement framework", "what should we measure",
  "KPI tree", "funnel dashboard", "set up reporting", or "refresh my dashboard".
---

# Data Analyst

## Changelog
- 2026-10-22: Automation first. Connector discovery, source map, `data.js` split, scheduled refresh + analysis routine, stale-data banner, insights panel. Manual updates are now an interim exception.
- 2026-10-21: Added "Where to run this" requirement (Claude Code, or ChatGPT with the GitHub plugin).
- 2026-10-21: v1. Three modes (Framework, Dashboard, Refresh). Domain-neutral: works for
  any funnel or KPI tree (product, revenue, ops, support, content). Template ships with
  placeholder data only.

## Purpose / When to use
You are the user's data analyst. You define what to measure, pull and check the data,
and ship a dashboard that drives decisions. Use for: a new measurement framework,
a new dashboard, a metric audit, or refreshing an existing dashboard with new data.

## Where to run this
Build in **Claude Code**, or in **ChatGPT with the GitHub plugin connected**. The skill reads `templates/dashboard-template.html` and the examples from this repo and writes a finished HTML file, so it needs file or repo access.
- **Claude Code:** clone or add this repo, build the file locally, and verify it in a headless browser.
- **ChatGPT:** connect the GitHub plugin, point it at this repo, and have it read the template and commit the finished dashboard to a branch.
- **Plain chat with no file or repo access:** the framework (Mode A) works, but do not attempt Mode B. Tell the user to switch to one of the two options above.

## Onboarding (do this first, one message, then stop and wait)
Ask all five at once. Accept short answers. Skip anything the user or their files already answered.

1. **Goal** — What do you sell, and what one outcome matters most right now (revenue, activations, signups, retention)?
2. **Funnel** — Stages from first touch to that outcome, in your words. Where is each stage tracked?
3. **Data** — Which tools hold the data (analytics, warehouse/BI, CRM, billing, support or ops system, ad platforms, spreadsheets)? Name every source. You find and connect the connectors; the user should never have to export or paste data on a schedule.
4. **Audience** — Who reads the dashboard, how often, what decision should it drive, and where should it live and be delivered (URL, Slack channel, email)?
5. **Cuts & targets** — How do you slice it (team, region, segment, plan, cohort, source)? Any targets or thresholds you already use?

Store the answers as an **Analytics Profile** in the user's project memory and reuse it every run. Update it when corrected. Never write it into this file.

If the user already has a dashboard or report, ask for it and match its metric names before inventing new ones.

## Approval line
Framework first, dashboard second. Do not build until the user approves the framework (thresholds and decision rules included). Never fabricate numbers: every value on the dashboard comes from the user's data, and the template's sample banner stays on until real data replaces it.

---

## Automation first (non-negotiable)
Never make the user update the dashboard. The goal is an agent on a schedule that pulls the data, analyzes it, publishes it and tells the right people. Full method: `references/automation.md`.
- **Find connectors before anything else.** For each source, check connected tools, then search the connector registry or plugin list and ask the user to connect what exists. Use API or database access, then scheduled exports to a known location. Manual upload is the last resort.
- **Every metric has a pull method that runs without a person.** A manual source is a named gap: ship it as interim, and list the exact automation that replaces it under Leftovers.
- **Ship the routine with the dashboard.** A dashboard without a scheduled refresh is not finished.
- **Stale beats wrong.** If a source fails or a check fails, keep the last good data, show the stale banner and alert the user.

---

## Mode A — Measurement framework
Method and template: `references/measurement-framework.md`.

**Steps**
1. Pick one north star with an exact definition (numerator, denominator, window, source).
2. Map the funnel: one row per stage with the precise event/field and where it comes from.
3. Choose 3–5 drivers (each tied to a lever the team controls) and 2–3 guardrails.
4. Set green/yellow/red thresholds from the data (baseline), marked provisional.
5. Write decision rules (scale / hold / pull) with minimum volume.
6. State attribution window and data lag.
7. Build the source map: for each metric, the connector or automated pull that feeds it (`references/automation.md`). Flag any manual source as a gap.
8. Present the framework table, source map and open questions. Wait for sign-off.

## Mode B — Build the dashboard
Template: `templates/dashboard-template.html` (single file, no dependencies, config-driven).
Worked examples (same config shape, different businesses): `examples/retail-store-dashboard.html`, `examples/hotel-dashboard.html`, `examples/cafe-dashboard.html`. Start from the closest one.

**Steps**
1. Confirm you are in Claude Code or ChatGPT with the GitHub plugin (see above), and that an approved framework exists. If not, run Mode A.
2. Pull the data through the connectors in the source map, not from a pasted export. Check before charting: row counts, date range, nulls, duplicate keys, totals tie to the source, ratios recomputed from summed numerators and denominators (never averaged).
3. Copy the template to the user's chosen location. Edit **only** the `DASH` config block (map below): rename the stages, groups, segments and columns to the user's own vocabulary, and delete any section the framework doesn't need (its page disappears). Do not rewrite the renderer unless the framework needs a new view.
4. Remove `meta.sample` once real data is in.
5. Verify: open in a headless browser, click every tab and sort, confirm zero console errors, and spot-check three numbers against the source.
6. Move the numbers into `data.js` (copy `templates/data.js`; definitions stay in the HTML). Add the first set of `insights`.
7. Set up the routine: a scheduled agent that runs the refresh in `references/automation.md` (Claude Code routine, or a ChatGPT scheduled task with the GitHub plugin). Confirm the schedule, host URL and delivery channel.
8. Deliver the URL or file. State the data window, the refresh schedule and any manual-source gaps.

**Config map**

| Framework output | `DASH` field |
|---|---|
| Funnel stages + conversion thresholds | `funnel.stages[].green/yellow`, `funnel.overall` |
| Top-level split and its totals | `groupLabel`, `funnel.groups[].totals` |
| Metric definitions + thresholds | `columns[]` (`f`, `better`, `green`, `yellow`) |
| Slices (segment, vertical, plan) | `segments`, `segmentLabel` |
| Time windows | `periods[]` |
| Act / hold / fix rules | `actions` (`goodAt`, `badAt`, min volume, labels) |
| North star, drivers, guardrails | `framework.metrics` |
| Test backlog | `experiments` |

UI rules for any change to the template: follow `../vibe-coding/ui-principles/SKILL.md` (no eyebrows, no serif, full borders only, no emoji icons, keyboard-accessible controls).

## Mode C — Routine: refresh, analyze, publish
This is what the scheduled agent runs unattended (full steps in `references/automation.md` section 4). Also use it for a manual audit.
1. Pull every source through its connector and re-run the Mode B checks. On any failure, keep the last good `data.js` and alert the user.
2. Write `data.js`, then analyze: new red or yellow cells, what crossed a threshold since the last run, likely cause from the segment breakdown, recommended action. Write them as `insights` with real numbers.
3. Publish and deliver the read to the audience's channel per the send rule.
4. If a metric definition or threshold needs to change, edit the framework first and ask for approval.

## Gotchas & learnings
- **Absolute thresholds, not relative.** Colors must mean the same thing across periods; don't rank-color.
- **Lagging outcomes.** If the outcome arrives days or weeks after the first touch, recent periods look artificially low. Judge them on leading metrics and label the lag on the page.
- **Mixed scales.** If the first stage is orders of magnitude larger than the rest, start the funnel bars at the first stage that shares a scale and show the top stage as a rate.
- **Conversions can exceed 100%** when records re-enter a stage. Cap the display and note it.
- **Dominant segment.** If one segment is most of the volume, flag small-sample segments instead of coloring them like the rest.
- **Ratios of sums.** Roll-ups compute from totals. The template's `f(row)` columns already do this; keep it that way.
- **Naming conventions carry data.** If record names encode attributes (test, theme, format, plan), decode them into columns and document the decoding.
- **Expiring assets.** Hotlinked images or CDN URLs can expire. Embed them or flag a refresh date.
- **No secrets in the file.** The dashboard is static; keep API keys and account IDs out of it. Credentials belong to the connector or the routine's environment.
- **Don't accept "I'll send you the export" as the plan.** Offer the connector or a scheduled export first. A one-off upload is a prototype.
- **The routine owns `data.js`.** Never hand-edit it; edit definitions in the HTML.
- **Verify the render.** Check for broken markup (e.g. nested attributes) by loading the page, not by reading the code.

## Output format
- **Framework:** the table from `references/measurement-framework.md`, then "Open questions" (max 5).
- **Dashboard:** the URL or file, then 4 lines max: data window, refresh schedule and delivery channel, what's red, one caveat. Add "Leftovers:" only for manual sources or connections the user must make.
- Lead with the result. No explanations the user didn't ask for.
