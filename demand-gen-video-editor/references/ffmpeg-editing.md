# FFmpeg Editing Patterns

Use these as starting points. Inspect the source first and adapt paths, timing, frame rate, and codecs as needed.

## 1. Inspect source

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate -of json input.mp4
```

## 2. Accurate cut with re-encode

Prefer re-encoding for frame-accurate social cuts.

```bash
ffmpeg -y -ss START -i input.mp4 -t DURATION \
  -map 0:v:0 -map 0:a? \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 192k -movflags +faststart cut.mp4
```

Use `scripts/cut_clip.py` for this operation when convenient.

## 3. Landscape to vertical with blurred background

Use when cropping would remove important content.

```bash
ffmpeg -y -i cut.mp4 -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:10[bg]; \
 [0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg]; \
 [bg][fg]overlay=(W-w)/2:(H-h)/2" \
-c:v libx264 -crf 18 -preset medium -c:a copy vertical.mp4
```

## 4. Straight 9:16 crop

Use when the subject remains safely framed.

```bash
ffmpeg -y -i cut.mp4 \
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
-c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k vertical.mp4
```

## 5. Burn captions from SRT

ASS/libass styling names vary by environment. Verify visually.

```bash
ffmpeg -y -i vertical.mp4 \
-vf "subtitles=captions.srt:force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=4,Shadow=0,Alignment=2,MarginV=220'" \
-c:v libx264 -crf 18 -preset medium -c:a copy captioned.mp4
```

For a TikTok-style baseline, use bold white text with a strong black outline and no background box.

## 6. Overlay a transparent headline asset

Use this for custom headline cards, rounded corners, glow, gradients, or brand-specific typography.

```bash
ffmpeg -y -i captioned.mp4 -i headline.png \
-filter_complex "[0:v][1:v]overlay=(W-w)/2:120:enable='between(t,0,4)'" \
-c:v libx264 -crf 18 -preset medium -c:a copy with-headline.mp4
```

Headline PNG should already include the approved text treatment and have a transparent background.

## 7. Append a static end card

Create a video segment from the approved end-card image, then concatenate.

```bash
ffmpeg -y -loop 1 -i endcard.png -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
-t 2 -r 30 -vf "scale=1080:1920,format=yuv420p" \
-c:v libx264 -c:a aac -shortest endcard.mp4
```

Normalize both clip and end card to the same codec, resolution, frame rate, audio sample rate, and channel layout before concatenation.

```bash
printf "file '%s'\nfile '%s'\n" "$PWD/with-headline.mp4" "$PWD/endcard.mp4" > concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

If stream-copy concatenation fails because stream parameters differ, re-encode the final concat instead of forcing `-c copy`.

## 8. Final technical check

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height -of json final.mp4
```

Then inspect the rendered video visually. Technical metadata does not replace visual QC.
