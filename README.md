# AI Marketing Skills

Company-agnostic marketing skills that turn Claude into a marketing operator you
can start using in minutes — no downloads, no file edits, no config to fill in.

Point Claude at this repo, say what you want, and the skill interviews you to learn
your business, then gets to work.

## The skills

### 🧭 Growth Marketing Manager
Your analyst and operator. Five modes in one skill:
- **Daily Brief** — a high-signal competitive & industry digest for your team channel.
- **Paid Monitor** — a weekly, honest read on paid performance (with blended CAC as
  the source of truth).
- **Exec Update** — a concise weekly PPF (Progress / Plans / Fires) for leadership.
- **Lifecycle Email** — onboarding, activation, and win-back / churn-save sequences.
- **Strategy** — ICP sharpening and rank-ordered GTM plays.

### 🎨 Creative Director
Your performance-creative lead. Four modes in one skill:
- **Paid Social Copy** — scroll-stopping ad copy for cold audiences.
- **Paid Search Copy** — full responsive search ad sets.
- **Video Scripts** — production-ready short-form scripts.
- **Ad Image / Display** — creative direction and specs (or finished images).

### 🎬 Demand Gen Video Editor
Your transcript-to-short-form editing workflow. It:
- **Onboards your visual style first** — upload a screenshot/reference, or review 4 generated style directions for headlines, captions, and end screens.
- **Finds demand-gen clips** — reviews timestamped transcripts and ranks strong standalone moments up to 45 seconds.
- **Stops for approval** — no editing starts until you approve the exact clips/timestamps.
- **Uses a 37-effect library** — kinetic hooks, zoom-throughs, phone mockups, grade reveals and more, each implemented as a renderer (`scripts/render_effect.py`, Pillow + NumPy + FFmpeg). See the [animated preview](demand-gen-video-editor/references/video-effect-library.html) and the [index with text slots](demand-gen-video-editor/references/effect-library.md); the editor picks one per clip.
- **Storyboard feedback gate** — before any full render, builds an editable storyboard (real mockup frames, per-scene notes) and revises it from your notes until you say "render". See [Video Storyboard Artifact](video-storyboard-artifact/SKILL.md).
- **Edits with FFmpeg** — cuts the approved source footage, reframes it for short-form, burns captions, adds headline overlays and end cards, then runs technical QC.

### 💻 Vibe Coding
A folder of three skills for building interfaces that look designed, not templated:
- **[UI Principles](vibe-coding/ui-principles/SKILL.md)**: visual exclusions, seven UI principles, a complete working flow, responsive behavior and visual QA. Load it for any UI work.
- **[Premium Pages](vibe-coding/premium-pages/SKILL.md)**: the layout recipe for any multi-section page. It covers a hero with a live product preview, alternating section backgrounds, photo-backed sections, three levels of hierarchy, high-contrast pricing and copy rules.
- **[Software Landing Page](vibe-coding/software-landing-page/SKILL.md)**: the landing page recipe for software products. It shows the product working, uses an interactive product tour instead of crammed feature grids, leads pricing with the outcome, and cuts any section that does nothing.

### 📊 Data Analyst
Your measurement and dashboard analyst, for any funnel or KPI tree (product, revenue, ops, support, content). See **[data-analyst/SKILL.md](data-analyst/SKILL.md)**. Build dashboards in **Claude Code**, or in **ChatGPT with the GitHub plugin**; plain chat can draft the framework only. It:
- **Onboards in one message** — goal, funnel, data sources, audience, cuts and targets.
- **Automates the data** — finds and connects the connectors for every source, then runs a scheduled routine that pulls, checks, analyzes, publishes and delivers the read ([method](data-analyst/references/automation.md)). Nobody updates it by hand, and a stale-data banner flags a failed refresh.
- **Designs the measurement framework** — north star, funnel definitions, drivers, guardrails, thresholds and decision rules ([method](data-analyst/references/measurement-framework.md)). Nothing gets built until you approve it.
- **Builds the dashboard** from a single-file, config-driven [HTML template](data-analyst/templates/dashboard-template.html): overview funnel, segment heatmap, sortable performance tables, act/hold/fix lists, an experiments board and the framework itself.
- **Ships with worked examples** (fictional data): a [retail store group](data-analyst/examples/retail-store-dashboard.html), a [hotel group](data-analyst/examples/hotel-dashboard.html) and a [cafe](data-analyst/examples/cafe-dashboard.html).
- **Refreshes and audits** — re-pulls data, re-runs the checks and flags what moved.

Shared creative references:
- **[Short-Form Video Format Library](creative-director/video-formats.md)** — eight reusable structures for choosing a visual format before scripting or storyboarding.

## How to use

1. Add this repo to your Claude project (or reference it). To build files, such as the Data Analyst's dashboards, use **Claude Code**, or **ChatGPT with the GitHub plugin** connected to this repo.
2. Say, e.g., *"be my growth marketing manager"*, *"be my creative director"*, *"be my data analyst, build me a dashboard"*, or *"turn this transcript into demand-gen clips."*
3. On first run each skill asks a few grouped questions to build the profile it needs. The video editor specifically locks the visual style before transcript analysis.
4. Claude stores that profile in **your** project/memory and reuses it every time — so the shared skill files stay generic while your setup stays personal.

You never edit these files. Your customization lives in your own workspace, not here.

## Design principles

- **Company-agnostic by construction.** No account IDs, no company names, no private
  methodology — only the transferable method.
- **You ship, the skill prepares.** Nothing goes live, external, or to an exec
  without your approval. Ad-platform assets are always created PAUSED. Video edits
  do not begin until clip/timestamp approval.
- **Original footage stays original.** The video editing workflow uses FFmpeg on the
  user's source footage by default and does not spend generative-video credits unless
  the user explicitly asks for generated footage.
- **Honest over polished.** Findings ship caveated with a confidence level; claims
  and stats are confirmed with you, never invented.

## Contributing / adapting

Fork it, extend a mode, or add a new one. Keep skills generic (interview the user;
don't hard-code a company) so they stay reusable for everyone.

## License

MIT — see `LICENSE`.
