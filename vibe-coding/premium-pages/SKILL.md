---
name: premium-pages
description: Build or restyle any multi-section page (landing, product, pricing, about, feature, app home) so it looks premium and designed instead of flat or templated. Use when a page "looks like every box is the same", when asked to make a page look better, more premium, more polished, or on-brand, or when building a new page from scratch. Pairs with ui-principles, which it never overrides.
---

# Vibe Coding: Premium Pages

## Changelog
- 2026-09-23: v1. Built from real redesigns: a hero with a live product preview, alternating section backgrounds, three levels of hierarchy, photo-backed sections, token-based brand re-skinning, and copy rules (no eyebrows, no em dashes, one-sentence headlines, centered section headlines).

## Purpose / when to use
Turn a page with no hierarchy into one that has a strong first screen, a clear rhythm and one obvious next action. It works for marketing pages and app screens alike. Unless asked otherwise, keep the page's structure, copy meaning and data, and change the design.

**Always load `../ui-principles/SKILL.md` first.** Its exclusions and principles win over anything here. This skill is the layout and styling recipe that sits on top of it.

## Steps

### 1. Put tokens on one root class before writing any CSS
Give each page one root class (`.page`) and define every color, font and radius there. Re-skinning to a new brand is then only re-pointing these variables.

```css
.page{
  --ink:#16140F; --ink-2:#4A453D; --ink-3:#6F685E;  /* text: primary, secondary, muted (still readable) */
  --bg:#FFFFFF;  --bg-alt:#F4F1EA;                   /* page + alternate section */
  --line:#DDD5C6;                                    /* full hairline borders */
  --brand:#1F2A24; --brand-deep:#0E1411;             /* dark bands, primary buttons */
  --accent:#E8DDBF;                                  /* on dark only: key phrase, main button */
  --font:"Inter",system-ui,sans-serif;               /* follow ui-principles for type */
  --radius-card:20px; --radius-ctl:10px;             /* one card radius + one control radius */
}
```
- **Matching a reference site:** take colors from its screenshots. You need a dark band color, the alternate background, one accent, and the text colors. A reference is not permission to copy the motifs ui-principles excludes.
- **Two radii only:** one for cards and one for controls. Never mix radii at random.

### 2. Hero: text on the left, a live product preview on the right
This single change adds the most.
- **Left column:**
  - one headline sentence, with the payoff phrase in the accent color,
  - one line of subhead,
  - a main button filled with the accent and a ghost button (clear with a full thin outline),
  - three short check-mark reassurances ("No setup fee", "Cancel anytime", ...).
- **Right column:** a small preview of the real product, built in HTML/CSS rather than a screenshot.
  - Use a plain frame with no fake window dots or browser chrome.
  - Put a dark stat band with 2 to 3 big numbers at the top, and two cards below it: a list with one item marked as the next step, and a short to-do list with one warning chip.
  - Mark it `aria-hidden="true"` and label its numbers as sample data wherever a claim could be misread.
- **Background:** dark brand color with a subtle radial glow, or a photo with a veil (step 4).
- Keep the hero only as tall as its content.

### 3. Alternate section backgrounds
Never stack two sections with the same background. A proven order to adapt to the page's real content:

| Order | Section | Background |
|---|---|---|
| 1 | Hero + preview | Dark or photo |
| 2 | Photo strip of real places, products or people (optional) | Edge to edge |
| 3 | Problem, as a short set of cards | Light |
| 4 | What changes, as columns with dividers | Dark band |
| 5 | How it works, as a real sequence; last step dark | Light |
| 6 | Pricing, featured plan inverted to dark | Alternate tint |
| 7 | Proof or extra value, as a real list or photo | Light |
| 8 | FAQ that opens and closes, first item open | Alternate tint |
| 9 | Closing call to action repeating the main button | Dark or photo |
| 10 | Footer | Darkest |

- **Spacing:** 96 to 104px of vertical padding per section (72px on mobile). Content max width about 1160px.
- **Section headline blocks are centered:** a headline plus at most one paragraph, capped near 720px wide. Keep the hero text left-aligned when it sits beside the preview.
- **Change the section formula when the content changes.** Don't repeat the same card grid down the page.

### 4. Photo-backed sections (1 or 2 per page)
- Put a full-bleed photo behind one or two dark sections, usually the hero and the closing call to action. More than two feels busy.
- Photos can also fill a photo strip or sit beside a list.
- **Source:** free stock sites (Unsplash, Pexels) or the brand's own photos.
  - Unsplash URL format: `https://images.unsplash.com/<photo-id>?auto=format&fit=crop&w=2400&q=70`.
  - Keep the ids in one constant so they're easy to swap.
- **Always layer the photo over a gradient**, so a missing or slow photo still looks designed:
  ```css
  .photo-sec{position:relative;isolation:isolate;background-size:cover;background-position:center}
  .photo-sec::before{content:"";position:absolute;inset:0;z-index:-1;
    background:linear-gradient(90deg,rgba(0,0,0,.86),rgba(0,0,0,.55) 55%,rgba(0,0,0,.35))}
  ```
  Set it inline as `style="background-image:url(PHOTO), linear-gradient(...)"`.
- Pick photos that have calm, darker areas where the text sits, and test the veil with the lightest photo you might use.
- Give meaningful photos alt text or a caption. Decorative backgrounds need neither.

### 5. Three levels of hierarchy on every page
1. **Headline:** one dark band or one big number.
2. **Working sections:** raised cards, white on a slightly darker page, with a soft shadow *or* a full hairline border.
3. **Detail:** flat lists and tables inside the cards. Never put a card inside a card.
- **Emphasize exactly one thing per group:** the featured plan, the last step, the next item. Everything else stays quiet.

### 6. Pricing that reads at a glance
- Use rounded cards (the card radius) with a visible full border and a soft shadow, on a tinted background.
- **Invert the featured plan:** dark card, white text, accent button and badge. That gives the page its strongest contrast point.
- **Excluded features stay readable:** muted but still passing contrast, with a strike-through or dash.
- Pull prices and features from the data source, never from text typed into the page.

### 7. Copy rules
- **No eyebrows**, per ui-principles. If an eyebrow held real information ("Included with Pro"), move it into the paragraph.
- **No em dashes** anywhere in visible copy, including button labels, FAQ answers and copy that comes from data (pricing features, CMS fields). Use a period, comma or colon.
- **Headlines are one sentence.** Join two short statements with "and", "then" or "with", and highlight the payoff phrase.
- **Button labels say what happens:** "Start on Pro", "See pricing", not "Learn more".
- **Never invent testimonials, logos, customer counts or revenue.** Use real product parts: the live preview, real plan data, real feature names.

### 8. Mobile
- **Under 980px:** one column, hide the nav links and keep one button, show the preview below the text, 4-up grids become 2-up, the photo strip shows 3 tiles.
- **Under 600px:** stack everything, make buttons full width, use a 16px side margin, the photo strip shows 2 tiles.
- **Stat bands stay 2-up on phones.**

### 9. Check before you ship
- Take full-page screenshots at 1300px and 390px wide (Playwright or similar). Look at them; don't trust the CSS.
- Confirm the page doesn't scroll sideways: `document.documentElement.scrollWidth > innerWidth` must be false.
- **Copy sweep:** search the rendered text for `—`, eyebrow-style caps labels, and headlines with more than one sentence.
- Run the project's typecheck and build, then commit.

## Gotchas & learnings
- **Global heading styles leak in.** A site-wide `h1,h2{text-transform:uppercase}` or heavy weight will change the new headings. Reset them inside the root class.
- **Scope everything** under the root class so other screens don't change.
- **Restyle shared components** (pricing cards, buttons) with scoped overrides, not rewrites. Admin previews and other pages use them too.
- **Utility class names can clash** with app class names (a Tailwind `ring` against a custom `.ring` drew a stray outline).
- **Labels beside big numbers break at narrow widths.** Put the label above the number (`flex-direction: column-reverse`).
- **Divider rules that assume a column count** (`nth-child(n+3)`) break when the grid wraps. Add a matching rule for each breakpoint.
- **Centering headlines** fixes pages where left-aligned headings sit awkwardly above wide card grids. Two-column FAQ and "text beside list" blocks read better stacked under a centered headline.
- **Sandboxes often block fonts and stock photo hosts.** Screenshots then show a stand-in font and the gradient fallback, so judge layout and color there and check the photos on a real preview deployment.
- **Low contrast hides in pale-on-pale pricing.** A white card on a champagne background needs a darker border and shadow, and the featured plan should invert.
- **Deploys:** the production site often builds only the default branch, so changes on a feature branch won't show until they're merged.

## Output format
- **Code:** one page component, plus one CSS block with a header comment listing the tokens and section order, scoped to the root class.
- **Report:** the section order with each background (light/dark/photo), the one emphasized item per group, what didn't change, the photo ids used, and desktop plus mobile screenshots.
