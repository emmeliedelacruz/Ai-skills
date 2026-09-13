#!/usr/bin/env python3
"""Basic technical QC for rendered social clips using ffprobe."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--max-content-seconds", type=float, default=None,
                        help="Optional runtime ceiling for the whole rendered file")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    args = parser.parse_args()

    if not shutil.which("ffprobe"):
        print("ffprobe not found", file=sys.stderr)
        return 2

    path = Path(args.video)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-show_entries", "stream=index,codec_type,codec_name,width,height",
        "-of", "json", str(path),
    ]
    data = json.loads(subprocess.check_output(cmd, text=True))
    duration = float(data.get("format", {}).get("duration", 0.0))
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]

    errors = []
    if not videos:
        errors.append("no video stream")
    if not audios:
        errors.append("no audio stream")
    if args.max_content_seconds is not None and duration > args.max_content_seconds + 0.05:
        errors.append(f"duration {duration:.3f}s exceeds {args.max_content_seconds:.3f}s")
    if videos and args.width is not None and videos[0].get("width") != args.width:
        errors.append(f"width {videos[0].get('width')} != {args.width}")
    if videos and args.height is not None and videos[0].get("height") != args.height:
        errors.append(f"height {videos[0].get('height')} != {args.height}")

    print(json.dumps({"duration": duration, "video_streams": videos, "audio_streams": audios,
                      "ok": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
