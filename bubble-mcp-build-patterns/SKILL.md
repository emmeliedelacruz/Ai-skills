---
name: bubble-mcp-build-patterns
description: Build or edit Bubble apps through the Bubble MCP so the result matches a reference 1:1 (coded app, design file, live site, or agreed spec). Use for new Bubble builds, rebuilds of coded UIs, large page edits through apply_changes, or any request to make a Bubble page match a reference exactly. Enforces reference capture, names every group as it is built, responsive-as-you-build, side-by-side fidelity checks, and real-browser testing.
---

# Bubble MCP Build Patterns

**Changelog**
- 2026-10-09 v2: app-agnostic; added 1:1 fidelity process, name-as-you-build, responsive recipe, editor/tool limits, parallelization rules.
- 2026-10-07 v1: initial.

**Use when:** building or editing any Bubble app through the Bubble MCP where the result must be a 1:1 match of a reference (coded app, design file, live site) or of an agreed spec.
**Canonical copy:** this file (`bubble-mcp-build-patterns/SKILL.md` in the AI skills repo). Keep one copy; do not fork it into project files or Drive.

## Purpose
Get a working, readable, responsive Bubble app that matches the reference exactly: right structure, exact values, correct names, no silent failures, verified in a real browser.

## Steps
1. **Branch + scope.** Ask which Bubble branch to build on (or use test). Change only the branch the user chose. No repo commits unless asked.
2. **Capture the reference before building anything.**
   - Run it locally or open the live reference. Screenshot every page and state (default, empty, loading, error, open menus, modals, tabs, hover/focus where visible) at 1440 and 390 with Playwright.
   - Extract the spec from the source, not by eye: computed styles and geometry per element (font family/size/weight/color, spacing, radii, shadows, widths, colors as hex), plus all copy, states, validations, toasts, and workflows.
   - Build a parity checklist file: every page > every section > every control (what it does, what data it reads or writes, what each state shows). The checklist is the definition of done.
   - List what Bubble cannot do (see Gotchas) and agree the accepted differences with the user before building. Ask early for anything only the editor can do (secrets, API-call initialization).
3. **Data first.** Types, fields, option sets, privacy rules, seed data (<=50 records per bulk call). Store computed values in fields maintained by backend workflows.
4. **Build structure, then bind.** Batch 1: create elements. Batch 2: expressions and workflows. Keep an id file; parse large results with a script.
5. **Name as you build (required).** Every create_element for a Group, RepeatingGroup, FloatingGroup, Popup, or reusable instance gets its final name in the same batch (rename_node). Never leave "Group A". Say what it is: "Sidebar", "Main column", "Stat tile - Revenue", "Day list (RG)", "Day cell", "Popup - Edit profile", "Floating - Account menu", "Form field - Email", "Button row". Repeated chrome gets identical names on every page. Name siblings by the content they hold. After each batch, get_node the area and fix any default names before moving on.
6. **Build to the spec, with the checklist open.**
   - Use exact values from the extracted spec (px, hex, weights, line heights, letter spacing, radii, shadows). No "close enough" and no default styles.
   - Same copy, order, states, interactions, empty/error/loading behavior, and validation messages. Same demo data and numbers where the reference shows them.
   - Build responsive as you go (see Responsive recipe) and match the reference's mobile layout, not just "no horizontal scroll".
7. **Verify 1:1 per page, side by side.**
   - Log in (saved storage state) and screenshot the Bubble page in the same states and widths as the reference screenshots. Compare with an image diff or section-by-section crops. Measure geometry on both (element boxes, fonts, colors) and list every delta.
   - Fix deltas until each is zero or an agreed accepted difference. Record accepted differences with the reason.
   - Functional parity: run the checklist in a real browser; each control does exactly what the reference does and writes the same data. Read the DB to confirm writes.
   - Mark each checklist line PASS / ACCEPTED DIFF / FAIL. A page is done only when no FAIL remains. check_app_issues = 0 is necessary but not sufficient.
8. **Test phase (do not skip).** Click every control; test empty and validation paths, each role, and logged-out. Delete test data and restore any user state you changed.
9. **Parallelize only across disjoint pages.** One brief file (these gotchas, ids, method, constraints), one agent per page group; you own shared reusables. Agents must not delete shared data or edit shared reusables.

## Responsive recipe
- Under 720px: hide the sidebar wrapper; give the shared top bar a menu button that opens a floating nav.
- Fixed-width containers: make them fluid (single_width false, min 0px, max = old px) so a conditional only needs max_width_css "100%". Do not set "100%" min width on fixed-width elements (the editor flags it).
- Conditionals cannot set single_width, container_layout, fit_*, order, or overflow. They can set visibility, min/max width/height, margins, padding, gaps, alignment, fonts, colors, rotation.
- Rows wrap: min_width_css 45-100% on children gives 2x2 or stacked. Hide table header rows on mobile and add mobile-only label texts (hidden by default, shown by conditional).
- RepeatingGroup column count cannot change per breakpoint: use auto-fit columns with cell_min_width_css, or a hidden second RG shown on mobile (keep both in sync).
- Floating groups need a fixed height; position them with margins.

## Gotchas & learnings
**Structure**
- Typed groups: set group_type on create; set data_source in a later op. An untyped intermediate group gives "parent has no type".
- Repeating groups: show_all + show_all_items true, columns 1 for lists, cell min sizes 0px. New RGs default to fit width, min height, and min cell size: reset them.
- Do not pass styleId to create_element (it overwrites your properties); the default style is applied automatically. Re-apply props if you did.
- New elements carry default fonts, sizes, min heights, and padding: override every property the spec defines.
- Hidden elements keep space unless collapse_when_hidden is true.
- Moving large groups times out; plan the structure instead of reshuffling.
- Check desktop pages for stray reusables left inside content groups.

**Expressions and data**
- Operators on dynamic text (truncate, regex, split) can be dropped silently; build from literal lists + index + join. format_number and format_date options are ignored; use workarounds.
- validate_expression needs a scope. If an expression will not validate on create (for example an injected list-item value), create the action first, then set the property in a second op.
- Auto-binding inputs need privacy-rule auto-binding on those fields. Number-format inputs may silently not save. Initial content for number inputs must be numeric.
- Data that must exist per record (seeded rows, generated content): do not rely on a one-time seed. Use an idempotent backend workflow (check-exists condition) triggered when "missing" becomes true.
- Schedule-API-workflow actions need the workflow id, filled parameters, and "Ignore privacy" if the workflow reads private data. Database-trigger changes do not fire other triggers; chain stages with scheduled workflows.
- ChangePage must be the last action in a workflow; an action appended after it is flagged.
- Two workflows on one element both fire; check get_node after edits.
- Privacy rules: low-privilege roles can inherit broader rules; check them explicitly and test logged-out.

**Integrations**
- API Connector calls must be initialized in the editor before they appear as actions. Ask the user early; never put real secrets in the build.
- Webhooks are unauthenticated: store the event, re-fetch from the provider before trusting it.

**Fidelity**
- "Looks similar" is not a pass: compare numbers (computed styles, boxes), not impressions.
- Confirm the exact font and weights are loaded; fallback fonts shift every measurement.
- Shadows, gradients, letter spacing, and line height are the most commonly missed properties; set them explicitly.
- Things Bubble commonly cannot match (agree early, offer the closest workaround, log as accepted difference): mid-sentence bold, strikethrough, 3D or tilt effects, per-element sticky, number/date formatting options, clipboard, confirm dialogs, Excel export, native toasts without a reusable.
- Re-diff all pages after any shared-component change (top bar, side rail).
- Keep the reference runnable until sign-off; screenshots go stale if the source changes.

**Editor and tool limits**
- get_issues shows only what the user's open editor last computed; check_app_issues misses some editor-only warnings. After edits, tell the user to reload the editor and check the Issues tab.
- rename_node is one call per node; large renames must be parallelized by page.
- apply_changes responses can be huge: parse the saved file with a script and keep batches small.
- Concurrent edits to the same page cause revision errors and "page was updated" banners: edit disjoint pages, retry once on timeout, verify with get_node.
- The dev-mode "Built on Bubble" badge appears in test-version screenshots; ignore it.

## Output format
Concise report: pages done (+ ids); per page the parity checklist counts (PASS / ACCEPTED DIFF / FAIL) and a table of accepted differences (what, why); tested table (PASS/FAIL/FIXED); not built (+ reason); check_app_issues result; user-only actions (secrets, editor steps); before/after screenshots of anything fixed; end with a skill-update suggestion.
