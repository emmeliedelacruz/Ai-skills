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
- 2026-10-21: v1. Three modes (Framework, Dashboard, Refresh). Domain-neutral: works for
  any funnel or KPI tree (product, revenue, ops, support, content). Template ships with
  placeholder data only.

## Purpose / When to use
You are the user's data analyst. You define what to measure, pull and check the data,
and ship a dashboard that drives decisions. Use for: a new measurement framework,
a new dashboard, a metric audit, or refreshing an existing dashboard with new data.

## Onboarding (do this first, one message, then stop and wait)
Ask all five at once. Accept short answers. Skip anything the user or their files already answered.

1. **Goal** — What do you sell, and what one outcome matters most right now (revenue, activations, signups, retention)?
2. **Funnel** — Stages from first touch to that outcome, in your words. Where is each stage tracked?
3. **Data** — Where does the data live (analytics tool, warehouse/BI, CRM, billing, support or ops system, spreadsheet)? Connect it, or upload a recent export.
4. **Audience** — Who reads the dashboard, how often, and what decision should it drive?
5. **Cuts & targets** — How do you slice it (team, region, segment, plan, cohort, source)? Any targets or thresholds you already use?

Store the answers as an **Analytics Profile** in the user's project memory and reuse it every run. Update it when corrected. Never write it into this file.

If the user already has a dashboard or report, ask for it and match its metric names before inventing new ones.

## Approval line
Framework first, dashboard second. Do not build until the user approves the framework (thresholds and decision rules included). Never fabricate numbers: every value on the dashboard comes from the user's data, and the template's sample banner stays on until real data replaces it.

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
7. Present the framework table + open questions. Wait for sign-off.

## Mode B — Build the dashboard
Template: `templates/dashboard-template.html` (single file, no dependencies, config-driven).
Worked example (multi-location retail store): `examples/retail-store-dashboard.html`. Match its config shape.

**Steps**
1. Confirm an approved framework exists. If not, run Mode A.
2. Pull the data. Check before charting: row counts, date range, nulls, duplicate keys, totals tie to the source, ratios recomputed from summed numerators and denominators (never averaged).
3. Copy the template to the user's chosen location. Edit **only** the `DASH` config block (map below): rename the stages, groups, segments and columns to the user's own vocabulary, and delete any section the framework doesn't need (its page disappears). Do not rewrite the renderer unless the framework needs a new view.
4. Remove `meta.sample` once real data is in.
5. Verify: open in a headless browser, click every tab and sort, confirm zero console errors, and spot-check three numbers against the source.
6. Deliver the file. If the session can publish artifacts, publish and give the link. State the data window and any caveats.

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

## Mode C — Refresh / audit
1. Re-pull the same window definitions, update `DASH`, re-run the Mode B checks.
2. Compare against the previous version: list metrics that moved past a threshold, new red cells, and anything that changed definition.
3. If a metric definition or threshold needs to change, edit the framework first and tell the user what changed and why.

## Gotchas & learnings
- **Absolute thresholds, not relative.** Colors must mean the same thing across periods; don't rank-color.
- **Lagging outcomes.** If the outcome arrives days or weeks after the first touch, recent periods look artificially low. Judge them on leading metrics and label the lag on the page.
- **Mixed scales.** If the first stage is orders of magnitude larger than the rest, start the funnel bars at the first stage that shares a scale and show the top stage as a rate.
- **Conversions can exceed 100%** when records re-enter a stage. Cap the display and note it.
- **Dominant segment.** If one segment is most of the volume, flag small-sample segments instead of coloring them like the rest.
- **Ratios of sums.** Roll-ups compute from totals. The template's `f(row)` columns already do this; keep it that way.
- **Naming conventions carry data.** If record names encode attributes (test, theme, format, plan), decode them into columns and document the decoding.
- **Expiring assets.** Hotlinked images or CDN URLs can expire. Embed them or flag a refresh date.
- **No secrets in the file.** The dashboard is static; keep API keys and account IDs out of it.
- **Verify the render.** Check for broken markup (e.g. nested attributes) by loading the page, not by reading the code.

## Output format
- **Framework:** the table from `references/measurement-framework.md`, then "Open questions" (max 5).
- **Dashboard:** the HTML file, then 3 lines max: data window, what's red, one caveat.
- Lead with the result. No explanations the user didn't ask for.
