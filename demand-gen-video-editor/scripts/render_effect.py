#!/usr/bin/env python3
"""Apply a Video Effect Library effect to a clip.

  render_effect.py --list
  render_effect.py A05 in.mp4 out.mp4 [--text "line one" --text "line two"] [--at 0.0]
                   [--duration SECONDS] [--mask matte.mp4] [--fps 30]
  render_effect.py A05 in.mp4 sheet.png --frames 0.2,1,2,3.5     # contact sheet of single frames for QC

Pipeline: FFmpeg decodes the clip to 1080x1920 (cover-crop), each frame is composited in
Python (Pillow/NumPy) using the effect's function of time, FFmpeg encodes it and copies the
original audio. The source footage is never regenerated. Outside [at, at+duration] the
footage passes through untouched.

--text fills the effect's copy slots in order (see `--list` for each effect's slots).
--mask is a grayscale video (white = subject) for the effects that need a cut-out; without
it a rough centre-column stand-in is used (preview quality only).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from effects import core  # noqa: E402
from effects.core import EFFECTS, H, W, Ctx  # noqa: E402


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate,duration:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    n, d = j["streams"][0]["r_frame_rate"].split("/")
    fps = float(n) / float(d)
    dur = float(j["format"]["duration"])
    return fps, dur


VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"


def decoder(path, fps, pix="rgb24", ss=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    cmd += ["-i", path, "-vf", f"{VF},fps={fps}", "-pix_fmt", pix, "-f", "rawvideo", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


class MaskReader:
    """Sequential matte reader: returns the matte frame nearest to t (assumes forward-only access)."""

    def __init__(self, path, fps):
        self.fps, self.proc, self.idx, self.cur = fps, decoder(path, fps, "gray"), -1, None
        self.size = W * H

    def __call__(self, t):
        want = int(round(t * self.fps))
        while self.idx < want:
            buf = self.proc.stdout.read(self.size)
            if len(buf) < self.size:
                break
            self.cur = Image.frombytes("L", (W, H), buf)
            self.idx += 1
        return self.cur or Image.new("L", (W, H), 0)

    def close(self):
        self.proc.kill()
        self.proc.wait()


def read_frame_at(path, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-vf", VF, "-frames:v", "1",
                        "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True)
    if len(p.stdout) < W * H * 3:
        raise SystemExit(f"no frame at t={t}")
    return Image.frombytes("RGB", (W, H), p.stdout[: W * H * 3])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("effect", nargs="?")
    ap.add_argument("src", nargs="?")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--text", action="append", default=[])
    ap.add_argument("--at", type=float, default=0.0, help="effect start time within the clip (s)")
    ap.add_argument("--duration", type=float, default=None, help="override effect length (s)")
    ap.add_argument("--mask", default=None)
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--frames", default=None, help="comma-separated effect times: write a contact sheet PNG instead of a video")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list or not a.effect:
        for k, e in sorted(EFFECTS.items()):
            print(f"{k:4} {e.name:20} {e.duration:4.1f}s  mask={'yes' if e.needs_mask else 'no ':3}  texts={e.texts}")
        return
    eid = a.effect.upper()
    if eid not in EFFECTS:
        raise SystemExit(f"unknown effect {eid}; try --list")
    spec = EFFECTS[eid]
    texts = a.text + spec.texts[len(a.text):]
    dur = a.duration or spec.duration
    if spec.needs_mask and not a.mask:
        print(f"note: {eid} works best with --mask (subject matte video); using a rough stand-in", file=sys.stderr)

    if a.frames:
        ts = [float(x) for x in a.frames.split(",")]
        fps = a.fps or 30
        ctx = Ctx(texts, fps, dur, MaskReader(a.mask, fps) if a.mask else None)
        thumbs = []
        for t in ts:
            ctx.t_abs = a.at + t
            img = read_frame_at(a.src, a.at + t)
            out = spec.fn(img, min(t, dur), ctx).convert("RGB")
            if spec.outro_fade and dur - t < spec.outro_fade:
                out = Image.blend(out, img, 1 - max(0.0, dur - t) / spec.outro_fade)
            thumbs.append(out.resize((W // 3, H // 3), Image.LANCZOS))
        sheet = Image.new("RGB", (len(thumbs) * (W // 3 + 6), H // 3), "white")
        for i, th in enumerate(thumbs):
            sheet.paste(th, (i * (W // 3 + 6), 0))
        sheet.save(a.dst)
        if ctx._mask_reader:
            ctx._mask_reader.close()
        return

    fps, src_dur = probe(a.src)
    fps = a.fps or fps
    ctx = Ctx(texts, fps, dur, MaskReader(a.mask, fps) if a.mask else None)
    dec = decoder(a.src, fps)
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-i", a.src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.dst],
        stdin=subprocess.PIPE)
    fsize = W * H * 3
    i = 0
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        t = i / fps
        local = t - a.at
        img = Image.frombytes("RGB", (W, H), buf)
        if 0 <= local <= dur:
            ctx.t_abs, ctx.frame_idx = t, i
            out = spec.fn(img, local, ctx).convert("RGB")
            if spec.outro_fade and dur - local < spec.outro_fade:
                out = Image.blend(out, img, 1 - (dur - local) / spec.outro_fade)
            img = out
        enc.stdin.write(img.tobytes())
        i += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    if ctx._mask_reader:
        ctx._mask_reader.close()
    if enc.returncode:
        raise SystemExit("ffmpeg encode failed")


if __name__ == "__main__":
    main()
