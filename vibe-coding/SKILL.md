---
name: vibe-coding
description: Build, refine, or audit websites and app interfaces with intentional product design and working behavior. Use for vibe coding, frontend builds, dashboards, landing pages, UI redesigns, or requests to remove an AI-generated or template-like appearance. Enforces Emmelie's visual exclusions, seven UI principles, responsive implementation, and visual QA.
---

# Vibe Coding

Build interfaces around a specific user's task, content, and product. Deliver working software with deliberate visual choices. Apply this skill alongside the project's engineering instructions and the available building or hosting workflow. Do not require Figma access to use these principles.

## Priority and scope

Follow the current user request first, then repository instructions and explicit project requirements. Apply the exclusions below unless the user explicitly requests an exception. A reference image or an existing theme is not implicit permission to reproduce a prohibited motif. Preserve existing behavior and unrelated code when redesigning.

These visual exclusions are Emmelie's preferences for this workflow. They are not claims that a font or ornament proves AI authorship. Do not promise that software will be undetectable as AI-assisted.

## Non-negotiable visual exclusions

1. **No eyebrows.** Do not place decorative kicker text above a heading: small uppercase labels, letter-spaced category names, pill badges such as "THE PLATFORM," or a colored dot with "INTRODUCING." Start with the actual heading. Keep useful form labels, breadcrumbs, statuses, and table headers; they serve a different function.
2. **No serif fonts.** Use sans-serif type for headings, body text, and controls. Do not use editorial serif headlines, italic serif accent words, or a serif/sans pairing. Preserve supplied logos as assets.
3. **No decorative partial outlines.** Do not draw one side of a card, incomplete corner brackets, half-outlined shapes, broken border frames, offset outline duplicates, isolated accent strokes around a container, or gradient border fragments. Use a consistent full border, a solid surface, or no container. Keep functional separators, input underlines where the system uses them, selection indicators, chart axes, and complete visible keyboard focus rings.
4. Do not substitute another fashionable template after removing these three motifs. Make layout and interaction decisions from the actual task.

## Other template patterns to reject by default

- Purple/blue gradient washes, gradient headline text, glowing orbs, mesh backgrounds, glass panels, or floating geometric blobs added merely to make a page feel "AI" or "premium."
- Sparkles, rocket icons, emoji feature icons, decorative terminal windows, browser chrome, and tiny monospace microcopy with no product purpose.
- A centered oversized headline, two generic buttons, a fake logo strip, and three identical feature cards used as the automatic answer to every brief.
- Bento grids when the content has no reason to be presented as separate cards; cards nested inside cards; an icon badge on every heading.
- Excessively rounded containers, pills for ordinary buttons, heavy shadows on every surface, and arbitrary mixtures of corner radii.
- Giant unused gutters, hero sections taller than their content needs, and dashboards arranged like marketing landing pages.
- Repeated section formulas, repetitive "Everything you need" copy, vague CTA labels, and decorative section numbering.
- Fabricated testimonials, customer logos, revenue numbers, growth percentages, or activity feeds presented as real evidence.
- Motion on every element, scroll-jacking, distracting background animation, and hover-only essential controls.

Use a brand-required color or a legitimate visualization when it serves the brief. These defaults prohibit decoration without purpose, not color, personality, useful cards, or information-dense screens. Never replace meaningful content with blank space just to look minimal.

## Seven UI principles

The following is a concise adaptation of [Figma's UI design principles](https://www.figma.com/resource-library/ui-design-principles/), accessed September 23, 2026. The visual exclusions above are separate user preferences.

| Principle | Apply it |
| --- | --- |
| Hierarchy | Make the current task and its primary action visually clear through size, weight, placement, and spacing. |
| Progressive disclosure | Present essentials first. Reveal advanced options when needed, with clear location and progress cues. |
| Consistency | Reuse component behavior and visual rules across screens. |
| Contrast | Distinguish importance and states without making everything compete for attention. |
| Accessibility | Support keyboard use, assistive technology, readable contrast, and meaningful alternative text. |
| Proximity | Place related information and controls together; separate unrelated actions. |
| Alignment | Use shared grid lines and predictable edges to organize the interface. |

Treat these as functional constraints, not a reason to add visual clutter.

## 1. Establish the job before choosing the layout

Inspect the existing repository, applicable instructions, framework, components, design tokens, routes, assets, and validation commands. Reuse the working stack. Do not install a new framework or UI library solely for aesthetics.

Determine:
- Who uses the product, what they are trying to accomplish, and the primary action.
- Whether the screen is a marketing page, task workspace, dashboard, editor, or transactional flow.
- The real content, data objects, brand assets, and required integrations.
- What is already functional and what is explicitly a prototype.

Use available context and sensible defaults. Ask a short question only when an unanswered choice would materially change the product. Do not delay a clear build for a style questionnaire.

Write a brief implementation direction: task, structure, typography, palette, density, and interaction. Continue into the build without a routine approval gate.

## 2. Define an intentional visual system

Use existing approved tokens where compatible with the user's exclusions. Otherwise define a small shared system for color, type, spacing, radius, borders, and elevation.

- Choose one readable sans-serif family by default. Use weight and size for hierarchy instead of mixing decorative fonts.
- Choose colors from the actual brand or product context. Use restrained accents for actions and state.
- Use consistent spacing increments. Keep related controls closer than separate groups.
- Set content width by the task. Use compact, scannable density for workspaces and comfortable reading width for prose.
- Prefer alignment, typography, and proximity before adding boxes.
- Choose one coherent icon family. Include icons only when they improve recognition or action.
- Use actual product visuals or relevant assets when available. Preserve aspect ratios and meaningful image crops.
- Give the product character through content, composition, imagery, and useful interaction rather than ornament.

Do not hard-code every future product to one font, one palette, one hero layout, or one border radius.

## 3. Implement a complete primary flow

Build a usable path through the user's central task before polishing secondary sections.

- Make navigation, links, forms, menus, sorting, search, filters, and buttons work where included.
- Connect real integrations when authorized and available. If a backend is absent, clearly distinguish local prototype behavior from persisted or shared behavior.
- Do not display a success message for an operation that did not occur.
- Implement relevant loading, empty, validation, error, success, disabled, and selected states.
- Keep form labels visible; use placeholders for examples rather than as the only label.
- Preserve entered data across correctable errors. Explain the next recovery action.
- Use semantic elements, accessible names, logical heading order, visible focus, and predictable keyboard navigation.
- Keep secrets out of client code and preserve existing authorization checks.
- Never invent business evidence to fill a layout. Use clearly identified sample data for prototypes.
- Hide advanced configuration only when the primary task remains understandable and operable.

## 4. Adapt to screen size and input

Design for narrow and wide screens, not a shrunk desktop screenshot.

- Reflow columns, navigation, action groups, and forms according to available space.
- Avoid accidental horizontal page scrolling. For genuinely wide tables, use a deliberate scrolling region with readable headers.
- Keep touch targets comfortable and controls reachable.
- Check long names, realistic text lengths, empty lists, and large values.
- Preserve reading and keyboard order when rearranging layouts.
- Respect reduced-motion preferences; keep animation purposeful.
- Do not remove focus indicators to comply with the decorative-outline ban.

## 5. Inspect, test, and repair before delivery

Run the project's relevant build, lint, or type checks. Exercise the primary flow with available browser tools and inspect rendered screenshots at a representative narrow mobile width and a desktop width. Check a middle width if the layout changes there.

Inspect actual renders, not just the source:
- Is the task understandable without an explanation?
- Are the primary action, current state, and next step clear?
- Does the page contain any decorative eyebrows, serif text, or partial outline ornaments?
- Has an automatic card grid or generic hero replaced a task-specific layout?
- Do spacing, type hierarchy, alignment, and repeated controls follow the same system?
- Are important labels, errors, focus indicators, and selected states readable?
- Do text, images, dialogs, menus, and sticky elements avoid clipping or overlap?
- Do all included controls have useful behavior?
- Are data and claims real or explicitly identified as samples?

Use automated checks where they resolve a concrete risk. A code search for fonts, border utilities, or uppercase styling is only a candidate finder: inspect context so functional labels, dividers, tabs, and focus rings are preserved.

Fix observed issues and recheck the affected flow or viewport. Do not claim visual, accessibility, or functional validation that was not performed. If rendering or an integration is unavailable, report the specific remaining limitation.

## Delivery

Deliver the requested working artifact through the project's normal workflow. Summarize what changed, what was verified, and any material unfinished behavior. Follow the user's authorization and the environment's publishing rules.

Do not expose implementation jargon inside the product unless users need it to make a decision. Do not declare a project production-ready solely because it builds.
