# Automation: connectors, refresh routine, analysis

A dashboard someone has to update by hand has failed. Get as close as possible to an agent that pulls, analyzes and publishes on a schedule.

## 1. Find the connector first
For every source named in onboarding, in this order:
1. **Already connected** — list the tools/connectors available in the session and use them directly (analytics, BI, warehouse, CRM, billing, ad platforms, support, Slack, Drive/Sheets).
2. **Available to connect** — search the connector registry (Claude) or the connector/plugin list (ChatGPT). If one exists, ask the user to connect it, then continue. Don't build around a connector the user could add in a minute.
3. **API or database access** — read-only credentials the routine can use. Ask for the least privilege that works. Never write secrets into the dashboard file or this repo.
4. **Scheduled export to a known place** — Drive/Sheets/warehouse table/GitHub path the source writes on its own (most tools can schedule a report). The routine reads that location.
5. **Manual upload** — last resort and interim only. Say so, ship it, and list the exact automation that replaces it under Leftovers (who sets up what, where).

## 2. Source map (fill during Mode A, before building)
| Metric / stage | Source | Pull method (connector, query, export path) | Refresh needed | Lag |
|---|---|---|---|---|

Every row needs a pull method that runs without a person. A row that is manual is a named gap, not a done item.

## 3. Split definitions from data
- `dashboard.html` holds definitions (columns, thresholds, labels, framework). It changes only when the framework changes.
- `data.js` holds the numbers. The routine rewrites only this file:

```js
window.DASH_DATA = {
  meta: { period: 'Oct 1-21', updated: '2026-10-22T06:00:00Z', sample: false, staleAfterHours: 36 },
  groups:   [ /* same shape as DASH.funnel.groups */ ],
  segments: [ /* same shape as DASH.segments */ ],
  periods:  [ /* same shape as DASH.periods */ ],
  insights: [ { tone: 'r', text: 'What moved, why it likely moved, what to do.' } ] // tone: g | y | r
};
```
The page shows the update time and turns red when the data is older than `staleAfterHours`, so a dead routine can't pass for fresh data.

## 4. The routine
Run as a scheduled agent: Claude Code routine (cloud session on a cron), or a ChatGPT scheduled task with the GitHub plugin. Daily by default; match the framework's fastest cadence.

**Each run**
1. Pull every source in the source map for the framework's windows.
2. Check: row counts, date range, nulls, duplicate keys, totals tie to the source, ratios from summed numerators and denominators.
3. If a check fails or a source is unreachable: do not overwrite `data.js`. Alert the user (below) and stop. Stale beats wrong.
4. Write `data.js` with fresh numbers and `meta.updated`.
5. Analyze against the framework's thresholds and decision rules: new red or yellow cells, what crossed a threshold since the last run, likely cause from the segment breakdown, and the recommended action. Write 3-6 `insights`, most important first, with real numbers.
6. Publish: commit `data.js` to the branch the host deploys from, or republish the artifact, so the live URL updates itself.
7. Deliver the read to where the audience already looks (Slack channel, email) if a connector exists and the user's send rule allows it. Otherwise keep it on the dashboard.

**Approval line.** Refreshing data, analyzing and updating the dashboard run unattended. Changing a metric definition or threshold, sending to a new audience, or acting on a recommendation (pausing, repricing, restaffing) needs the user's approval unless they set a standing rule.

**Alerts.** On failure, message the user with: which source failed, the error, when data was last good. Use the same channel as the read.

## 5. Routine prompt (fill from the Analytics Profile)
> You are the data analyst for [company]. Run the refresh in `data-analyst/references/automation.md` section 4. Sources and pull methods: [source map]. Framework: [thresholds, decision rules]. Write `data.js` in [repo/path], publish to [host], send the read to [channel] if a send rule exists: [rule]. If any check fails, do not overwrite data; alert [user] with the failing source and last good time.

## 6. Hosting
Pick one place the dashboard lives at a stable URL (GitHub Pages, Vercel/Netlify from the repo, or a published artifact) so the routine's commit or republish is the whole deploy. Confirm it during onboarding.
