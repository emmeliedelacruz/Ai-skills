---
name: demand-gen-video-editor
description: >
  A transcript-first workflow for turning webinars, interviews, podcasts, founder videos,
  customer conversations, and long-form recordings into short demand-generation clips.
  Use when a marketer wants to define a reusable short-form visual style, review a transcript,
  identify strong clips up to 45 seconds, approve exact cuts, and then edit the approved source
  footage with FFmpeg using consistent headline overlays, captions, reframing, and end screens.
  Trigger on requests like "find clips from this transcript", "turn this webinar into ads",
  "cut short-form videos", "repurpose this interview", or "edit these approved clips with FFmpeg".
---

# Demand Gen Video Editor

Turn long-form source material into approved, branded short-form clips without regenerating the source footage.

## Workflow

Follow this order. Do not skip approval gates.

1. Build or load the **Video Style Profile**.
2. Review the timestamped transcript and propose clips.
3. Stop for explicit clip approval.
4. Receive the source video.
5. Cut and style only the approved clips with FFmpeg.
6. QC every render and return a clip manifest plus the finished files.

If a Video Style Profile already exists for the user, reuse it unless they ask to change the style.

## Step 1 — Onboard the visual style first

Before analyzing the first transcript, confirm a **Video Style Profile** exists.

Offer two paths:

- **Reference path:** ask the user to upload a screenshot, frame, or example video showing the style they want.
- **Exploration path:** offer to show 4 visual options. Generate four clearly different mockups for the same sample frame so the user can choose quickly.

Do not require the user to articulate design language if a visual reference is easier.

When generating style options:
- Use a generic presenter or neutral source frame unless the user has supplied an image of the actual person.
- Keep the spoken-caption copy and headline copy identical across options so the user is choosing design, not wording.
- Vary headline container, typography, caption treatment, placement, and end-screen direction.
- Prefer simple, legible short-form treatments over decorative motion graphics.

Capture these decisions in the Video Style Profile:
- default aspect ratio and resolution, usually 9:16 / 1080x1920 for short-form
- framing rule for landscape footage: crop, fit, or blurred-background fit
- headline placement, font feel, weight, size, colors, container, border/glow, and highlight treatment
- headline duration, normally the opening 2–5 seconds
- caption font feel, weight, case, size, color, outline/shadow/background, position, and maximum lines
- whether captions animate or remain simple
- end-screen duration, layout, logo treatment, CTA pattern, URL/domain behavior
- brand colors, logo files, fonts, and safe-zone preferences if supplied
- any banned treatments, words, or effects

Default to a simple caption system unless the user chooses otherwise: bold white text, strong dark outline, lower-third placement, maximum 2 lines, no karaoke or word-by-word animation.

Store the confirmed profile in the user's project memory / notes when available. Keep the shared skill generic; never hard-code one company's brand into this file.

See `references/style-onboarding.md` for the profile template and style-option rules.

## Step 2 — Analyze the transcript

Accept pasted text or transcript files such as TXT, SRT, or VTT.

Exact FFmpeg cutting requires timestamps. If the transcript has no timestamps:
- use the source video's transcript/timestamp tooling if available, or
- ask for a timestamped transcript or the video so timestamps can be established.

Do not invent timestamps.

### Clip selection objective

Find self-contained moments that can create demand, not merely summarize the source.

Prioritize clips with:
- a strong spoken hook in the first 1–3 seconds
- a sharp pain point, tension, surprising observation, or opinion
- clear relevance to the intended buyer/user
- a complete payoff without needing the rest of the video
- useful specificity, proof, or a concrete example
- language that can work for cold audiences
- natural product/category relevance without forcing a sales pitch

Ideal duration: 15–35 seconds.
Hard maximum: 45 seconds unless the user changes the rule.

Avoid:
- long introductions and speaker bios
- clips that begin with pronouns or context the viewer cannot understand
- sections that are mostly setup with no payoff
- duplicate ideas unless the delivery is materially different
- weak hooks that require a text overlay to make the clip interesting

The spoken opening matters more than the graphic headline. Use the headline to sharpen a good hook, not rescue a weak clip.

### Clip suggestion output

Rank the strongest candidates and use this table:

| Rank | Timestamp | Length | Spoken hook / angle | Why it works | Audience / funnel | Suggested headline | Edit note |
|---|---|---:|---|---|---|---|---|

Then name the **top 3–5 clips you would test first**.

For exact scoring guidance, read `references/clip-selection.md`.

## Step 3 — Approval gate

Stop after presenting clip suggestions.

Do not cut, render, download, or otherwise edit the source video until the user explicitly approves clips or timestamps.

Accept approval in any convenient form, for example:
- "1, 3, 5"
- "all except 4"
- revised timestamps
- a smaller shortlist

If the user changes a boundary, treat their timestamp as authoritative.

## Step 4 — Receive and inspect the source video

After approval, ask for or locate the source video file if it is not already available.

Before editing:
- inspect duration, dimensions, frame rate, and audio stream with `ffprobe`
- confirm approved transcript timestamps fall inside the source duration
- note whether source framing is portrait, landscape, or mixed

Do not replace or regenerate source footage. The default workflow uses the user's original video and audio only.

## Step 5 — FFmpeg edit

Use FFmpeg for the actual video editing. Use the scripts in `scripts/` when they fit; use direct FFmpeg commands when custom styling is required.

### Cut behavior

For each approved clip:
- cut the approved section accurately
- trim obvious dead air at the beginning/end only when it does not alter the approved meaning
- preserve original audio unless requested otherwise
- do not remove pauses inside a sentence just to make speech unnaturally fast
- do not splice separate statements into a new claim unless the user explicitly requests a montage

### Framing

Apply the Video Style Profile.

For 9:16 exports from landscape footage:
- crop when the subject remains naturally framed
- use blurred-background fit when cropping would cut off the speaker, slides, demo, or important context
- avoid stretching footage

### Headline overlay

Use the approved style profile.

The headline should:
- communicate one idea
- be concise enough to read immediately
- complement the spoken hook rather than repeat a long sentence verbatim
- remain inside the safe area
- normally appear for the first 2–5 seconds unless the chosen style calls for persistent text

If the approved headline design requires rounded cards, custom glow, gradients, or other styling that is awkward in `drawtext`, render a transparent headline overlay asset and composite it with FFmpeg. Do not regenerate the underlying video.

### Captions

Generate captions from the approved spoken excerpt and burn them into the render unless the user asks for a sidecar subtitle file.

Match the approved caption style exactly. Default rules:
- maximum 2 lines
- short readable phrases rather than paragraph blocks
- high contrast on every frame
- lower third but above platform UI / bottom safe zone
- keep captions off the speaker's mouth when possible
- no animated karaoke effects unless explicitly chosen during onboarding

### End screen

Append the approved end screen unless the profile says not to.

Default duration: 1.5–2.5 seconds.
Default content:
- brand/logo
- one CTA
- optional URL/domain

Do not cram multiple CTAs, paragraphs, or feature lists into the end card.

See `references/ffmpeg-editing.md` for tested command patterns.

## Step 6 — Mandatory frame-by-frame QC before delivery

Do not share a video immediately after rendering. Every render must pass both a full visual review and a playback check.

1. Inspect the complete rendered video frame-by-frame, or with an equivalent all-frame sequential review at full resolution. Do not substitute a few timestamp screenshots or a contact sheet for this review.
2. Play the exported MP4 from start to finish in a standard player.
3. Run `scripts/verify_video.py` for basic technical verification.

During the frame-by-frame review, check:
- runtime matches the approved cut plus intentional end screen
- opening starts cleanly and the hook is not clipped
- audio is synchronized and audible
- every headline and caption is readable, correctly spelled, timed correctly, and inside safe zones
- text never covers a face, product proof, or another important visual
- no subtitle overlaps with the end screen
- no accidental black, frozen, duplicated, or partially rendered frames
- no transition glitch, flash, incomplete end-card population, or logo crop
- portrait export is exactly the intended dimensions
- source footage has not been stretched and landscape demos use the approved crop or contained treatment
- final encode plays through successfully and the delivered file opens in the intended preview surface

If any issue is found, fix it, re-render, and repeat the full QC pass before presenting the file. Never present an unreviewed render as complete.

## Delivery format

Return a concise manifest:

| Clip | Source timestamp | Final runtime | Headline | CTA | File |
|---|---|---:|---|---|---|

Use deterministic filenames such as:
`01-people-buy-solutions-vertical.mp4`

Include the individual downloadable video files. Do not claim a render is finished unless the file exists and has passed QC.

## Editing guardrails

- Source footage is the source of truth. Do not generate replacement presenter footage.
- Do not spend generative-video credits as part of this workflow unless the user explicitly asks for generated footage.
- Do not begin editing before clip approval.
- Do not invent transcript lines, timestamps, brand claims, logos, URLs, or CTAs.
- Keep brand-specific customization in the user's Video Style Profile, not in this shared skill.
- If the user supplies a reference screenshot, reproduce its design logic without assuming every visible element is mandatory.
