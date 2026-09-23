---
name: software-landing-page
description: Build or restyle the landing page for a software product (SaaS, app, tool) so a visitor understands within seconds that it is software, sees it working, and knows what it will help them achieve. Use when asked for a landing page, home page, marketing site or pricing page for an app, or when a product page "doesn't make it clear what we sell", looks flat, or crams too much into one section. Pairs with ui-principles and premium-pages; ui-principles wins on any conflict.
---

# Vibe Coding: Software Landing Page

## Changelog
- 2026-09-23: v1. Built from a full landing page rebuild and every round of feedback on it:
  - show the product in action, not just describe it
  - one idea at a time through an interactive tour
  - high-contrast tabs, an outcome-led pricing headline, centered section headlines
  - no eyebrows, no em dashes, one-sentence headlines
  - photo sections with a fallback, nothing that looks clickable unless it is, and cut sections that do nothing

## Purpose / when to use
A software landing page has three jobs, in this order:
1. **Make it obvious this is software.** A visitor should see real screens in the first scroll.
2. **Show what it does, one idea at a time.**
3. **Sell the outcome** (what the customer gets: more sales, more profit, hours back), not the feature list.

Load `../ui-principles/SKILL.md` first; its rules win. Use `../premium-pages/SKILL.md` for tokens, spacing and mobile basics. This skill is the software-specific layer on top.

## Steps

### 1. Write the outcome down before designing
- One sentence: **what the software helps the customer do**, in their words ("sell out retreats and profit", "close the books in a day").
- **That sentence drives the hero and the pricing headline.** If you can't write it, ask the user one question before building.
- List the 3 to 5 core screens of the product. These become the product tour.

### 2. Section order
Every section must answer "what does this make the visitor believe or do?" **If a section repeats another or does nothing, cut it.** A "how it works" steps row usually repeats the product tour.

| # | Section | Background | Job |
|---|---|---|---|
| 1 | Hero + live product preview | Dark or photo | "This is software, and it's for me" |
| 2 | The problem: the tools they juggle today | Light | "That's my life" |
| 3 | Photo strip: real places, customers or use cases (optional) | Edge to edge | Makes it human |
| 4 | Product tour, one screen at a time | Dark band | "I can see how it works" |
| 5 | Pricing with an outcome-led headline | Tint | "It's worth it" |
| 6 | Extra value: a bonus, coaching or integrations, as a timeline or list | Light | "And there's more" |
| 7 | FAQ, first item open | Tint | Removes objections |
| 8 | Closing call to action | Dark or photo | One last ask |
| 9 | Footer, flush to section 8 | Darkest | |

- **Alternate backgrounds**, and never put two with the same background next to each other.
- **Photo strip position:** after the problem section, not directly under the hero. It gives the problem a human face and keeps the hero next to the product.

### 3. Hero: text on the left, a live product preview on the right
- **Left column:**
  - one headline sentence built from the outcome, with the payoff phrase highlighted in the accent,
  - one line of subhead naming what's inside,
  - a main button that shows the price where it helps ("Get started from $X/mo") and a ghost button ("See pricing"),
  - three short check-mark reassurances (billing, cancel anytime, no setup fee).
- **Right column:** a small HTML/CSS mockup of the real dashboard, not a screenshot.
  - A stat band with 2 to 3 key numbers, one list with the next item highlighted, and one to-do list with a warning chip.
  - Use sample data, and mark it `aria-hidden`.
- The hero text stays left-aligned because it's paired with the preview. Every other section headline is centered.

### 4. Product tour: interactive, one idea at a time
When a section describes the product, **show screens in action and keep it from getting crammed.**
- **Layout:** tabs on the left (icon + screen name), a mockup of that screen on the right in a simple frame.
- **Only the open tab expands:** a one-sentence benefit and 3 short points. Closed tabs show just their name.
- **One mockup per tab**, each showing the screen doing its job, with realistic sample content:
  - a chart that shows progress against a target
  - a task list with one overdue item
  - the customer-facing page next to its checkout
  - a customer table with one row needing action and its action button
- **Motion:**
  - Advance on its own every ~6.5s, with a thin progress line on the open tab.
  - Stop for good once the visitor clicks, pause on hover, and turn autoplay off for `prefers-reduced-motion`.
- **Access:** `role="tablist"`/`tab`/`tabpanel`, `aria-selected`, arrow-key navigation, visible focus ring. The mockup is `aria-hidden`; the tab text carries the meaning.
- **Contrast:** tabs on a dark band must not blend in. Closed tabs get a solid surface a step lighter than the band with a visible border. The **open tab inverts** to the light accent with dark text and a shadow.
- **Mobile:** tabs stack, and the mockup sits below them, with non-essential columns hidden.

### 5. Pricing
- **The headline is the outcome, not the plan count.** Write "Sell out every retreat and keep more of the profit." Don't write "Two plans with no setup fees." Plan facts (number of plans, no contract, which plan is for whom) go in the subline.
- **Cards:** rounded (about 20px), white with a visible full border and soft shadow, on a tinted background.
- **Featured plan inverted:** dark card, white text, accent badge and button.
- **Excluded features** are muted but still readable.
- **Prices and features come from the data source** (database, CMS, config), never from text typed into the page. Clean copy in that data too.

### 6. Extra value section: nothing looks clickable unless it is
- Show bonus content (live calls, templates, onboarding) as a **numbered timeline**:
  - a dot and a connecting line,
  - a title and one line of description per item,
  - no card borders.
- **Outlines, borders, hover states and raised cards signal "click me".** Use them only on things that respond.

### 7. Photos
- Put stock photos (Unsplash, Pexels) or the brand's own photos behind **1 to 2 sections**, usually the hero and the closing call to action. Photos can also fill the photo strip.
- **Always layer the photo over a gradient**, `url(photo), linear-gradient(...)`, plus a dark `::before` veil so text stays readable. A photo that fails to load then still looks designed.
- Keep the photo ids in one constant.

### 8. Copy rules
- **No eyebrows** (small caps labels above headings). If one held real information, move it into the paragraph.
- **No em dashes** anywhere visible, including buttons, FAQ answers and copy that comes from data. Use periods, commas or colons.
- **Headlines are one sentence.** Join ideas with "and", "then" or "with", and highlight the payoff phrase.
- **Say "software", "app" or "tool" early**, at least in the product tour headline. The visitor should never wonder what's for sale.
- **Button labels describe the action:** "Start on Pro", "See pricing", "Book a demo".
- **Never invent testimonials, logos, user counts or revenue.** The product mockups and real plan data are the proof.

### 9. Matching a brand
- Put every color, font and radius on the page root as tokens. Re-skinning then only means re-pointing the variables.
- **Matching a reference site:** sample its colors from a screenshot (dark band, dune/secondary, light accent, off-white, text).
- Keep the layout. Colors and imagery change; structure does not.

### 10. Check before you ship
- Take full-page screenshots at 1300px and 390px, plus one per product tour tab.
- Confirm the page doesn't scroll sideways: `document.documentElement.scrollWidth > innerWidth` must be false.
- Screenshot the bottom of the page and check that the closing section and footer meet with no gap.
- **Copy sweep:** no `—`, no eyebrow labels, one sentence per headline, and the outcome stated in the hero and pricing.
- Run the typecheck and build.

## Gotchas & learnings
- **"It's not clear we sell software"** means descriptions without screens. Fix it with mockups in the hero and the product tour, not more copy.
- **A crammed section** means everything is visible at once. Fix it with tabs or steps that reveal one idea at a time.
- **Tabs on a dark band blend in** when they're transparent with faint borders. Give them solid surfaces and invert the open tab.
- **A pricing headline about plan counts is weak.** Lead with the outcome.
- **Left-aligned section headings above wide grids look off.** Center section headlines, and stack two-column FAQ or text-beside-list blocks under them.
- **A list with its first item outlined reads as a clickable, selected card.** Use a timeline for static sequences.
- **Global app CSS leaks into the landing page.**
  - A global `footer{margin-top}` left a white strip between the last section and the footer.
  - Global `h1,h2{text-transform:uppercase}` uppercased every heading.
  - Reset both under the page root.
- **Sandboxes often block fonts and stock photo hosts.** Screenshots show a stand-in font and the gradient fallbacks, so check the real photos on a preview deployment.
- **Production often builds only the default branch.** Changes on a feature branch won't show until they're merged.

## Output format
- **Code:**
  - one page component,
  - one product tour component,
  - one CSS block scoped to the page root, with a header comment listing the tokens and section order.
- **Report:**
  - the section order with each background and job,
  - the outcome sentence used in the hero and pricing,
  - the tour tabs and what each mockup shows,
  - the photo ids,
  - what was cut and why,
  - desktop and mobile screenshots.
