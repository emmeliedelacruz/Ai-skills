---
name: breakdown-video-editor
description: >
  Edit supplied presenter footage into creator-led editorial breakdown videos with
  word-synced animated cards, bold typography, full-screen graphic reframes, and
  clean presenter shots. Use for "make a breakdown video", "apply this breakdown
  style to another video", or "add editorial graphics to this explainer".
  Adapts to each topic, presenter, brand, duration, and spoken performance.
  Not for generating presenters or finding clips in long recordings.
---

# Breakdown Video Editor

## Changelog

- 2026-09-14: Created a reusable editing skill that transfers the editorial style across topics and source videos without reusing campaign copy, timestamps, or presenter coordinates.

## Purpose / When to use

Produce a finished breakdown video from existing footage: the creator carries the explanation while precisely timed graphics clarify its argument. This skill owns execution of the breakdown style. The [Video Format Library](../creative-director/video-formats.md#breakdown-video--creator-led-editorial-treatment) owns format selection and general visual logic. For selecting short clips from a long recording, use [Demand Gen Video Editor](../demand-gen-video-editor/SKILL.md) first, then apply this skill to the selected segment.

The transferable style is the typography, restrained motion, graphic hierarchy, and relationship between speech and visuals. It is not a fixed script, a particular presenter, a fixed runtime, or a mandatory sequence of signup cards and marketing channels.

## 1. Resolve inputs with minimal setup

Reuse everything already supplied or approved. Obtain only missing essentials:

- Source footage with original audio, or a selected segment.
- Intended audience, central takeaway, and CTA if they are not clear from the recording.
- Target aspect ratio/runtime and destination.
- Brand styling or a reference; reuse an accepted style profile on subsequent videos.
- Supplied proof, product media, and end card if the planned treatment needs them.

If source footage is missing, ask for it. Do not generate a replacement presenter. If only an optional supporting asset is missing, use appropriate authored text/shapes or omit that visual; never invent evidence.

Read the selected source's actual dimensions, duration, frame rate, and audio. Watch its movement. A transcript helps find words but does not establish their final timing.

## 2. Create or reuse a style profile

Save the profile with the user's project, not in this shared skill. Parameterize:

| Setting | Starting treatment; user branding overrides |
| --- | --- |
| Canvas | 9:16, 1080 × 1920, 30 fps |
| Typography | Manrope or similar clean sans serif; heavy headlines, medium labels, regular support |
| Colors | Dark ink, vivid accent, pale tinted ground, white cards, muted support |
| Default palette | Ink #12122B, accent #3D3BF3, ground #EDEAFE, muted #4B4B63 |
| Safe areas | At least 80 px sides at 1080 width; top/bottom checked for destination controls |
| Cards | Rounded white rectangles, roughly 28–38 px radii at 1080 width |
| Detail | Thin dark outlines, minimal pictograms, subtle shadows |
| Motion | Short slides, small overshoot, typed phrases, drawn lines, message highlights |
| Captions | Only if requested or part of the accepted style; keep separate from editorial graphics |

Keep the editorial character across brands: oversized but restrained type, short readable lines, simple UI-inspired illustrations, flat colors, and purposeful motion. No emojis, glossy generic effects, generated text, or fake product screenshots.

When style is already approved, reuse it without another onboarding round. For a new uncertain brand treatment, show a small representative style frame before the full render. Do not require style approval again for ordinary copy/timing revisions.

## 3. Map the new argument to visual operations

Identify what each spoken beat is doing. Choose graphics by meaning, not by copying the prior video's nouns.

| Communication job | Available treatment | Adaptation rule |
| --- | --- | --- |
| Establish recognition | Presenter plus small typed pill | Use a short phrase from this hook |
| Make a problem tangible | Counter, compact comparison, or evidence card | Use verified evidence; label conceptual illustrations clearly |
| Reject a mistaken focus | Full-screen keyword with drawn strike or de-emphasis | Only use a strike when the speaker actually rejects something |
| Introduce the real focus | Matching full-screen keyword and one or two example cards | Make this video's core idea dominant |
| Explain a principle | Presenter plus question or principle card | Keep the creator's face clear |
| Demonstrate a change | Transform existing card contents or highlight a phrase | Preserve continuity; avoid stacking a second unrelated card |
| Show applications | Branch, ordered steps, or a compact comparison | Use categories appropriate to the topic, not preset channels |
| Close | Brief payoff hold and supplied CTA/end card | Match the actual call to action |

These are optional components, not compulsory scenes. A three-step teaching video may need sequential cards instead of a false-belief strike; a product explanation may need real screenshots instead of schematic UI. Do not force every script into “not X, but Y.”

Keep one dominant visual idea per beat. Alternate full-screen moving presenter and full-screen graphics when the argument warrants it. Do not automatically turn this into split screen or a miniature slide deck. Preserve clean presenter moments so the graphics have contrast.

## 4. Measure speech and build the edit map

Use word alignment or waveform-assisted listening against the actual audio. Verify important cue words by listening. Never reuse timestamps from a previous video.

Track separately:

- Scene start/end frames.
- Cue word and its measured onset in the final audio timeline.
- Animation start, landing/settle, hold, and exit.
- Source in/out when the edit trims the recording.

The landing frame should match the word the visual illustrates. An entrance can start slightly before that landing. A sentence can begin over one scene and cut on its key word. Avoid arbitrary visual changes merely to satisfy a fixed interval.

Write the storyboard as:

| Planned timing | Dialogue | Visual used |
| --- | --- | --- |
| Measured window | Exact recorded words | Treatment, asset/component, cue word, entrance/landing/exit, placement |

Get approval for a new storyboard unless the user has already supplied or authorized the edit map. A later user correction updates the affected beats; it does not restart the workflow.

Quantize to integer output frames. Use half-open intervals [start, end) consistently so scenes meet without uncovered frames. Replace planned timing with actual frame-derived final timing after rendering. Do not force a recording into 15 seconds if that clips words or the CTA; follow the user's runtime constraint through explicit editing.

## 5. Compose around the moving presenter

Find the face/head envelope across each entire shot, including zoom and gestures. Position cards in usable headroom or torso space according to the approved layout. Do not inherit absolute coordinates from another presenter.

If the user requests every overlay above the head, reframe to create sufficient headroom. Otherwise choose the cleanest available area. Do not cover the face, mouth, hands demonstrating something, or important source content.

Check combined bounds of text, shadows, connector paths, and animation overshoot. Review the busiest simultaneous state. Measure text using the actual loaded font; shorten lines before shrinking type. Keep all words inside safe areas.

Use one persistent card when the idea evolves: question → answer → application source, for example. Remove obsolete contents before new contents appear. Channels, steps, or outcomes should arrive one at a time on the spoken cadence and remain only as long as they aid comprehension.

## 6. Build an editable deterministic composition

Use a capable non-generative editor or compositor, such as FFmpeg with Pillow/vector layers, or a conventional timeline editor. Preserve natural motion and original audio. Do not regenerate footage, voice, graphics, or identity to make an editing revision.

Separate project data into:

- Style tokens: colors, font, dimensions, margins.
- Copy tokens: repeated message, labels, CTA.
- Cue data: frame boundaries and word-linked events.
- Layout: component bounds and face-exclusion regions.
- Media references and render configuration.

Reference repeated text from one token. A copy change must update every use, including small cards and secondary examples. This does not mean every future video must use the same message.

Keep continuous narration under cutaways unless the approved edit calls for a change. Avoid concatenating separately encoded AAC segments when one continuous audio encode will preserve sync.

Contain supplied flyers or graphics when cropping would remove important text or branding. Fill unused canvas with a matching background or source-derived edge extension. Add no new text over a designed end card unless requested.

Export MP4 using H.264, yuv420p, AAC, and faststart; 30 fps and CRF 19 are useful defaults. Confirm the encoder has finished successfully before treating its file as a deliverable.

## 7. Review the actual new export

Watch the entire finished video sequentially with sound. Inspect transitions and animation-heavy passages frame by frame, including every entrance/exit. Contact sheets support review but cannot prove word sync or natural movement.

Verify:

- Every graphic lands on its intended cue; dialogue remains synced.
- Presenter motion is preserved and faces stay unobstructed.
- Combined cards/labels never collide or clip.
- Repeated copy is correct everywhere after revisions.
- Full-screen cutaways cover every intended frame without leaks or stale layers.
- Evidence remains authentic and readable; end-card content is intact.
- Runtime, aspect ratio, codecs, full decode, and playback pass.

Useful technical checks:

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate -show_entries format=duration,size -of json OUTPUT.mp4
ffmpeg -v error -i OUTPUT.mp4 -f null -
```

If a tool cannot provide a required review, state that limitation instead of claiming QA passed. Fix observed failures and recheck the changed export.

## 8. Deliver and revise

Return a playable video in chat with a short description of actual changes. Use a distinct review filename/path and verify that the linked file is the new render, not a stale version.

Do not upload or update Drive or another publishing destination until the user approves the rendered video and authorizes that destination. Follow any applicable brand delivery procedure. Preserve the editable project, style profile, copy, and cues.

For revisions, change only requested dimensions: a copy change preserves audio, timing, and accepted layout; a timing correction changes the relevant cues; a layout correction preserves wording and performance.

## Gotchas & learnings

- A visually similar still-frame animatic is not finished moving presenter footage.
- A previous video's timestamps and coordinates do not transfer to another recording.
- A graphic that starts on the cue but lands much later can still feel mistimed.
- Individually clean cards can overlap when all are visible or during overshoot.
- A new filename does not prove a new render; inspect its actual contents.
- A yielded encoder is still running; incomplete MP4 files may appear incompatible.
- Reusable style means reusable design decisions and components, not campaign-specific copy.

## Output format

- Playable review MP4 and a concise change note.
- Frame-accurate final storyboard with cue words and treatments.
- Reusable project style/copy/cue data and editable composition.
- Honest QA status and any remaining limitation.
