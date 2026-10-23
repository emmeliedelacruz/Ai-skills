---
name: video-storyboard-artifact
description: Build and run an editable storyboard artifact that locks a video's scenes, layout and revision notes before any render. Use before rendering any video (reel, ad, explainer, motion graphics, YouTube) and every time the user sends revision notes.
---

# video-storyboard-artifact

**Changelog**
- 2026-10-23 v3: added to this repo and wired into `demand-gen-video-editor` as the pre-render feedback gate. Genericized (user, not a named person).
- 2026-10-23 v2: made format-agnostic. Platform numbers moved into "Format profiles".
- 2026-10-23 v1 draft: first version, built from a reel storyboard (v8 to v10).

**New vs. update:** NEW skill (replaces the earlier reel-only draft `reel-storyboard-artifact`; delete that one if it still exists anywhere). **Canonical copy:** this file, `video-storyboard-artifact/SKILL.md` in this repo. One copy only.

## Purpose / When to use

Renders are slow (15 to 25 minutes on one CPU). Storyboard changes take about a minute. Decide every change in the storyboard first, then render once. Use it for any video with more than one scene or overlay, whether or not it has a talking head.

How the artifact works:
- One card per scene: number, time range, the spoken or narrated line (if any), a layout badge, a mockup image (two when the scene changes state), "On screen", "Motion", and "From your notes".
- Mockups are real: each image is one frame from the same renderer the final video uses (footage composited if there is footage). Never fake them.
- Guides toggle: a checkbox overlays the format profile's no-go areas and content zones.
- Notes box + status per scene (Keep / Change / Cut this scene / Add something) and one global notes box.
- Notes sync to Claude through the artifact `db` capability, with `localStorage` as fallback and a "Copy all notes" button as last resort.

## Steps

1. Pick the format profile (below). If none fits, create one first.
2. Build scene data from the timeline: id, time, spoken text, layout badge, what, motion, note, mockup images (base64 JPEG, about 360 wide, same aspect as the video).
3. Render mockups with the real renderer, one frame per scene (two for state changes). Check the contact sheet before publishing.
4. Build the page: self-contained HTML, scene data embedded, light and dark theme tokens, `viewport-fit=cover`. Add a "What to check first" box listing open decisions and the defaults you applied.
5. Publish with `capabilities: {db: {}}`. Republish to the same URL for each version (omitting `capabilities` keeps it). Put the version in the title.
6. Version the notes: per-version `localStorage` key (`sb-<project>-vN`) and db doc (`notes/vN`). Scene numbers change between versions, so never reuse a doc.
7. Read notes yourself: `Artifact read_db`, `collection: notes`, `doc_id: vN`. Keys: `s<scene number>` (text), `s<scene number>st` (status), `g` (global). Also check `comments`. Do NOT ask for a paste.
8. Map notes to scenes by that version's scene numbers. Apply every note. Unflagged scenes stay as they are, and say so on the page. Ambiguous note: apply the best reading and list it under "What to check first".
9. Publish the next version showing the user's original note on each changed scene. Repeat until the user says to render.
10. Render only on "render". Deliver with `present_files`.

## Format profiles

A profile is the platform-specific part. Each one lists: aspect and size, no-go areas, content zones, caption position and size, layout badges used, and the guide boxes the page draws.

- **Instagram Reel (9:16, 720x1280):** numbers and layout badges live in `talking-head-reel-editor` (not in this repo). Use them for the guides; if that skill is unavailable, confirm the numbers with the user and save a profile.
- **Other formats (TikTok, Shorts, YouTube, LinkedIn, paid social):** do not guess numbers. Confirm the platform's current safe areas, or measure from a test upload, then save a profile.
- **16:9 YouTube or motion graphics with no face:** no platform overlay to dodge. Use a title-safe margin (about 5 percent), badge scenes by type (title, UI recreation, product shot, end card), and skip the face-clearance guides.
- **New profile template:** aspect/size; no-go areas (px); content zones (px); captions (y, size, lines); layout badges; notes on face or subject clearance.

## Gotchas & learnings

- Notes stay in the user's browser until `db` is declared. Declare it on the first publish.
- "No document" when reading means the user has not opened the new version or has typed nothing.
- Keep old versions' docs as history. Never overwrite them.
- Use `edit` for small page changes; republish the whole file only for big rewrites.
- Make it fast to scan: short text, one decision per bullet, defaults applied, thumbnails visible.
- Notes are scene instructions, not global preferences. If a note says "remove text that repeats the caption", check other scenes for the same issue and mention it, but only change flagged scenes unless a global note says otherwise.
- Test before publishing: load the HTML in headless Chromium, confirm scene count and no JS errors.

## Output format

- A storyboard link (same URL each version), version in the title.
- Two lines in chat: what changed from the user's notes, and decisions for the user.
- No render until the user says "render".
