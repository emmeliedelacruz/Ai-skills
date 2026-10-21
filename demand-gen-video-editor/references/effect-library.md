# Video Effect Library — Index

Text index of `video-effect-library.html` (same folder). Open the HTML for the animated preview of each effect (click a tile to replay); use this file to pick effects without parsing it.

Effects are 9:16 motion treatments built around a speaker/footage frame. Loop length is the preview cycle (seconds), a guide for how long the effect needs on screen — not a hard limit.

Implement with FFmpeg (overlays, `zoompan`, `drawtext`, `xfade`, blur/colour filters) or pre-rendered transparent overlay assets, per `ffmpeg-editing.md`. Always composite over the user's original footage — never replace it.

IDs: `A##` = Set 1, `B##` = Set 2.

## Set 1 — 20 effects

| ID | Effect | What it does | Loop (s) |
|---|---|---|---:|
| A01 | Kinetic hook | Heavy words slam in letter by letter over the footage. | 4.2 |
| A02 | Title card dive | Cream title card, then a phone frame zooms up to full screen. | 4.4 |
| A03 | Screenplay page | Script page slides in, types out, highlights the beat, lifts away. | 4.4 |
| A04 | Gravity drop | Serif letters fall in and bounce over the footage. | 4.6 |
| A05 | Grade slider | Before/after split with a handle sweeping the grade. | 5.0 |
| A06 | Knockout captions | Giant serif text cut out of a cream panel, footage shows through. | 4.8 |
| A07 | Receipt printer | Effect name prints out on a receipt from a slot. | 4.8 |
| A08 | Mood curtain | Footage drains to a moody grade as a dark curtain rises. | 4.8 |
| A09 | Intertitle | Iris wipe to a framed silent-film title card with grain. | 4.8 |
| A10 | Comment CTA | Comment box types a keyword, then the auto-reply lands. | 5.2 |
| A11 | Magazine cover | Gold frame, cover lines and a sticker over live footage. | 4.8 |
| A12 | Odometer recursion | Counter rolls to the take length, then footage nests inside itself. | 4.8 |
| A13 | Contact sheet hook | Frames fill a grid, one gets picked and zooms to full screen. | 5.0 |
| A14 | Picture dive | Footage inside a picture frame, zoom through into the frame. | 4.8 |
| A15 | Live markup | Footage goes B&W, hand-drawn circle and note with arrow. | 4.6 |
| A16 | Projected film | Sprocket borders, sepia flicker, scratches and grain. | 5.0 |
| A17 | Reel feed | Cut to a social feed UI, swipe back out with a blur. | 4.4 |
| A18 | Giant captions | A caption word grows into a giant stacked title block. | 4.6 |
| A19 | File drop | A file card drops into a panel, then becomes the phone frame. | 4.6 |
| A20 | Eyedropper grade | Sample colors from the frame, then regrade the shot to a new palette. | 5.2 |

## Set 2 — 17 effects

| ID | Effect | What it does | Loop (s) |
|---|---|---|---:|
| B01 | Orbit | Clip cards orbit the speaker, passing behind and in front. | 4.6 |
| B02 | Couch wall | A wall of video tiles pops in behind the speaker. | 3.8 |
| B03 | UI world | App UI fills the top half; clips drop in, a command types. | 4.4 |
| B04 | Frame break | Footage in a small social frame that expands to full screen. | 3.6 |
| B05 | Digital zoom | Fast punch-in with a blur kick; caption stacks in. | 4.2 |
| B06 | Phone mockup | A 3D phone with an approval notification slides in. | 4.4 |
| B07 | Checklist | Glass checklist panel ticks off steps in time with the talk. | 4.2 |
| B08 | Headline wall | Paper headline notes get pinned to the wall behind. | 4.4 |
| B09 | Zoom-through cut | Dive into a dark spot, then cut out to a new shot. | 4.2 |
| B10 | Chart grow | Glowing line chart draws across the frame with a tag. | 4.2 |
| B11 | Pull-back reveal | Zoomed video pulls back to reveal the editor app around it. | 5.0 |
| B12 | Green screen | Green backdrop wipes away to reveal a UI scene behind. | 4.4 |
| B13 | Paper cut | Cut-out speaker on a paper collage with ransom-note type. | 4.6 |
| B14 | Doodle boil | Boiling hand-drawn outline and doodles on a dimmed shot. | 4.2 |
| B15 | Vertigo | Dolly zoom: background stretches while the speaker holds still. | 4.8 |
| B16 | Cover story | Giant serif masthead sits behind the speaker. | 4.0 |
| B17 | Glass type | Frosted glass lettering behind the speaker, ends in a ripple. | 4.4 |

## Picking effects

- One effect per clip, max two. Effects are the visual hook, not decoration.
- Match effect to the spoken beat: stat/number → A12, B10; app/product demo → B03, B06, B11; opinion/hook → A01, A04, B05, B16; CTA → A10, A19; mood/story → A08, A09, A16.
- Effects that hide the speaker (A02, A13, A14, A17, B04, B11) need a clip with a strong opening beat that survives without a visible face.
- Keep the Video Style Profile's caption and headline rules; an effect replaces the headline only if the user approves it in the Edit Map.
- Set 2 effects that use cut-outs (B13, B15, B16, B17) require a subject mask; propose them only if the source footage allows a clean matte, otherwise pick another.
