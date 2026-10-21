# Video Effect Library — Index

37 reusable 9:16 motion treatments. Animated previews: `video-effect-library.html` (same folder; click a tile to replay). Every effect is implemented and renderable with `scripts/render_effect.py` (see below). IDs: `A##` = Set 1, `B##` = Set 2.

## Render an effect

```bash
pip install pillow numpy                       # once; FFmpeg must be on PATH
python3 scripts/effects/fetch_fonts.py         # once; Google Fonts the effects use (falls back to system fonts)
python3 scripts/render_effect.py --list        # every effect, duration, mask need, text slots
python3 scripts/render_effect.py A05 clip.mp4 out.mp4 --text BEFORE --text AFTER --at 0.5
python3 scripts/render_effect.py B13 clip.mp4 out.mp4 --mask matte.mp4
python3 scripts/render_effect.py A05 clip.mp4 sheet.png --frames 0.2,1,2,3.5   # single-frame contact sheet for QC
```

- Input is an already-cut approved clip; it is scaled/cropped to 1080x1920. The original audio is kept and the footage is never regenerated.
- `--at` starts the effect that many seconds into the clip; before and after it the footage passes through. `--duration` overrides the effect length. The last 0.25s crossfades back to plain footage unless the effect already ends clean.
- `--text` fills the effect's copy slots in order (table below). Omitted slots use the preview's sample copy, so always pass real copy.
- `--mask` is a grayscale video, white = subject, same length as the clip. Needed by the effects marked **mask**. Without it a rough centre-column stand-in is used, fine for a preview, not for delivery. Produce a matte with any video background-removal tool.
- Effects are built from the current frame only, so tiles/thumbnails/orbiting cards show crops of the same footage, not other clips.
- A render is ~0.05-0.9s per frame (a 5s effect is roughly 1-2 minutes). Run the mandatory frame-by-frame QC from `SKILL.md` on the result.

Adding an effect: new `scripts/effects/set_<name>.py`, register with `@effect(id, name, duration, texts, needs_mask)` (see `effects/set_lead.py`, `effects/core.py`).

## Set 1 — 20 effects

| ID | Effect | What it does | Loop (s) | Mask | Text slots (`--text`, in order) |
|---|---|---|---:|:-:|---|
| A01 | Kinetic hook | Heavy words slam in letter by letter over the footage. | 4.2 |  | 1='KINETIC'; 2='HOOK' |
| A02 | Title card dive | Cream title card, then a phone frame zooms up to full screen. | 4.4 |  | 1='TITLE'; 2='DIVE' |
| A03 | Screenplay page | Script page slides in, types out, highlights the beat, lifts away. | 4.4 |  | 1='INT. GREEN ROOM - DAY'; 2='JUSTYN'; 3='(to camera)'; 4='Kinetic hook.'; 5='Title card dive.'; 6='Screenplay page.'; 7='Gravity drop.'; 8='CUT TO:' |
| A04 | Gravity drop | Serif letters fall in and bounce over the footage. | 4.6 |  | 1='gravity'; 2='DROP' |
| A05 | Grade slider | Before/after split with a handle sweeping the grade. | 5.0 |  | 1='BEFORE'; 2='AFTER' |
| A06 | Knockout captions | Giant serif text cut out of a cream panel, footage shows through. | 4.8 |  | 1='knockout'; 2='KNOCK'; 3='OUT' |
| A07 | Receipt printer | Effect name prints out on a receipt from a slot. | 4.8 |  | 1='EFFECT NAME'; 2='READ ALOUD'; 3='1 TAKE'; 4='RECEIPT'; 5='PRINTER'; 6='TOTAL'; 7='2 WORDS' |
| A08 | Mood curtain | Footage drains to a moody grade as a dark curtain rises. | 4.8 |  | — |
| A09 | Intertitle | Iris wipe to a framed silent-film title card with grain. | 4.8 |  | 1='Intertitle.' |
| A10 | Comment CTA | Comment box types a keyword, then the auto-reply lands. | 5.2 |  | 1='EDIT'; 2='creator'; 3='Sent. Check your DMs.'; 4='to get all of these and more' |
| A11 | Magazine cover | Gold frame, cover lines and a sticker over live footage. | 4.8 |  | 1='OCTOBER 2026 · ISSUE NO. 3'; 2='ON THE COVER'; 3='Magazine/cover.'; 4='COVER'; 5='Shot in/one/take' |
| A12 | Odometer recursion | Counter rolls to the take length, then footage nests inside itself. | 4.8 |  | 1='RAW TAKE'; 2='0:24' |
| A13 | Contact sheet hook | Frames fill a grid, one gets picked and zooms to full screen. | 5.0 |  | 1='CONTACT SHEET' |
| A14 | Picture dive | Footage inside a picture frame, zoom through into the frame. | 4.8 |  | — |
| A15 | Live markup | Footage goes B&W, hand-drawn circle and note with arrow. | 4.6 |  | 1='markup'; 2='50,102' |
| A16 | Projected film | Sprocket borders, sepia flicker, scratches and grain. | 5.0 |  | — |
| A17 | Reel feed | Cut to a social feed UI, swipe back out with a blur. | 4.4 |  | 1='// NO HUMAN TOUCHED'; 2='CLAUDE'; 3='EDITED'; 4='THIS'; 5='creator'; 6='12.9K'; 7='13.7K'; 8='187'; 9='5,833' |
| A18 | Giant captions | A caption word grows into a giant stacked title block. | 4.6 |  | 1='GIANT'; 2='captions.' |
| A19 | File drop | A file card drops into a panel, then becomes the phone frame. | 4.6 |  | 1='A1C5E028-9919-490F-93DD-7E5F98782750.MP4'; 2='0:25 · 29.4 MB · 1080×1920'; 3='Drop raw footage'; 4='0:25'; 5=' of raw footage' |
| A20 | Eyedropper grade | Sample colors from the frame, then regrade the shot to a new palette. | 5.2 |  | 1='SAMPLED'; 2='GRADE'; 3='SHIRT'; 4='WALL'; 5='MAT'; 6='CAP'; 7='SKIN' |

## Set 2 — 17 effects

| ID | Effect | What it does | Loop (s) | Mask | Text slots (`--text`, in order) |
|---|---|---|---:|:-:|---|
| B01 | Orbit | Clip cards orbit the speaker, passing behind and in front. | 4.6 | mask | 1='and you can get the'; 2='cool girl' |
| B02 | Couch wall | A wall of video tiles pops in behind the speaker. | 3.8 | mask | 1='selling a'; 2='course' |
| B03 | UI world | App UI fills the top half; clips drop in, a command types. | 4.4 |  | 1='Claude'; 2='Drop files here'; 3='DROP CLIPS'; 4='TRIGGER THE'; 5='RAW CLIPS'; 6='How can I help you today?'; 7='/video-' |
| B04 | Frame break | Footage in a small social frame that expands to full screen. | 3.6 |  | — |
| B05 | Digital zoom | Fast punch-in with a blur kick; caption stacks in. | 4.2 |  | 1='or know anything about'; 2='video'; 3='editing' |
| B06 | Phone mockup | A 3D phone with an approval notification slides in. | 4.4 |  | 1='all you'; 2='need to'; 3='Ads Assistant'; 4='Needs approval'; 5='Pause Ad 3, move the budget to Ad 1'; 6='Approve' |
| B07 | Checklist | Glass checklist panel ticks off steps in time with the talk. | 4.2 |  | 1='ALL YOU NEED TO DO'; 2='Drop your clips'; 3='Trigger the skill' |
| B08 | Headline wall | Paper headline notes get pinned to the wall behind. | 4.4 | mask | 1='Claude can edit everyone’s videos now'; 2='Claude edits your whole reel'; 3='Your next video editor is Claude'; 4='Yes, Claude can edit videos.'; 5='claude edits videos'; 6='your whole reel' |
| B09 | Zoom-through cut | Dive into a dark spot, then cut out to a new shot. | 4.2 |  | 1='you can get the'; 2='cool girl'; 3='aesthetic' |
| B10 | Chart grow | Glowing line chart draws across the frame with a tag. | 4.2 |  | 1='SCALE ↗' |
| B11 | Pull-back reveal | Zoomed video pulls back to reveal the editor app around it. | 5.0 |  | 1='a skill with'; 2='Transcribed 1 clip'; 3='Picked the take'; 4='Cut 3 shots'; 5='Captions added'; 6='Rendered 150 frames' |
| B12 | Green screen | Green backdrop wipes away to reveal a UI scene behind. | 4.4 | mask | 1='you need'; 2='edits' |
| B13 | Paper cut | Cut-out speaker on a paper collage with ransom-note type. | 4.6 | mask | 1='100%' |
| B14 | Doodle boil | Boiling hand-drawn outline and doodles on a dimmed shot. | 4.2 | mask | — |
| B15 | Vertigo | Dolly zoom: background stretches while the speaker holds still. | 4.8 | mask | 1='SUCK'; 2='AT'; 3='DESIGN' |
| B16 | Cover story | Giant serif masthead sits behind the speaker. | 4.0 | mask | 1='EDIT' |
| B17 | Glass type | Frosted glass lettering behind the speaker, ends in a ripple. | 4.4 | mask | 1='DESIGN' |

## Picking effects

- One effect per clip, max two. Effects are the visual hook, not decoration.
- Match effect to the spoken beat: stat/number → A12, B10; app/product demo → B03, B06, B11; opinion/hook → A01, A04, B05, B16; CTA → A10, A19; mood/story → A08, A09, A16.
- Effects that hide the speaker (A02, A13, A14, A17, B04, B11) need a clip with a strong opening beat that survives without a visible face.
- Keep the Video Style Profile's caption and headline rules; an effect replaces the headline only if the user approves it in the Edit Map.
- **mask** effects (B01, B02, B08, B12–B17) need a clean subject matte; propose them only if one can be produced, otherwise pick another.
- A08 and A09 end on a solid card, so cut to the next scene at `--at + duration`.
