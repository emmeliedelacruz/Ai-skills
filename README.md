# AI Marketing Skills

Three company-agnostic "master" skills that turn Claude into a marketing operator you
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
- **Edits with FFmpeg** — cuts the approved source footage, reframes it for short-form, burns captions, adds headline overlays and end cards, then runs technical QC.

Shared creative references:
- **[Short-Form Video Format Library](creative-director/video-formats.md)** — eight reusable structures for choosing a visual format before scripting or storyboarding.

## How to use

1. Add this repo to your Claude project (or reference it).
2. Say, e.g., *"be my growth marketing manager"*, *"be my creative director"*, or *"turn this transcript into demand-gen clips."*
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
