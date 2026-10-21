# Measurement Framework Method

Use in Mode A. Output is one table the user can approve in a minute.

## 1. North star
One metric that says whether the goal is being met.
- **Name**
- **Definition:** numerator / denominator, window, source system
- **Why this one:** what decision it changes
Reject it if the team can raise it without helping the business.

## 2. Funnel map
One row per stage, first touch to outcome.

| Stage | Exact definition (event / field / status) | Source | Typical lag |
|---|---|---|---|

Each stage must be countable the same way every time. If two teams define a stage differently, resolve it here.

## 3. Drivers (3–5)
Inputs that move the north star. Each needs a named lever (budget, creative, form length, follow-up speed) and an owner. Prefer rates and costs between adjacent stages.

## 4. Guardrails (2–3)
Metrics that must not get worse while chasing the north star (cost per outcome, lead quality, refund rate, stuck/untouched rate).

## 5. Thresholds
- Baseline from the last 8–12 weeks of the user's own data. Use any external benchmark the user supplies; don't invent one.
- Green = at or better than target. Yellow = within tolerance (about 15–25% off target). Red = beyond that.
- Absolute values, not relative rank.
- Label every threshold **provisional** until it survives four weeks of data.

| Metric | Direction | Green | Yellow | Red | Basis |
|---|---|---|---|---|---|

## 6. Decision rules
| Decision | Rule | Minimum volume |
|---|---|---|
| Scale | metric ≥ X | N units of volume |
| Hold | between | — |
| Pull back | metric ≤ Y | $/volume floor |

Minimum volume prevents acting on noise. State it in the same units as the data.

## 7. Attribution & lag
Window (e.g. 30 days from first touch), model (first/last/platform-reported vs. CRM), how recent days are treated, and which source wins when systems disagree.

## 8. Cadence & ownership
Daily / weekly / monthly views, who reads each, who acts.

## 9. Open questions
Max five. Each names the data or decision needed to close it.

## Final table (this populates `DASH.framework.metrics`)
| Tier | Metric | Definition | Source | Target | Cadence |
|---|---|---|---|---|---|
| North star | | | | | |
| Driver | | | | | |
| Guardrail | | | | | |
