#!/usr/bin/env python3
"""Frame-accurate FFmpeg clip cutter for approved transcript timestamps."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_timecode(value: str) -> float:
    value = value.strip()
    if not value:
        raise ValueError("empty timecode")
    parts = value.split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError as exc:
        raise ValueError(f"invalid timecode: {value}") from exc
    if len(nums) == 1:
        return nums[0]
    if len(nums) == 2:
        return nums[0] * 60 + nums[1]
    if len(nums) == 3:
        return nums[0] * 3600 + nums[1] * 60 + nums[2]
    raise ValueError(f"invalid timecode: {value}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--start", required=True, help="Start time: seconds, MM:SS, or HH:MM:SS")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--end", help="End time")
    group.add_argument("--duration", help="Duration")
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--preset", default="medium")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg not found", file=sys.stderr)
        return 2

    src = Path(args.input)
    if not src.exists():
        print(f"input not found: {src}", file=sys.stderr)
        return 2

    start = parse_timecode(args.start)
    if start < 0:
        raise ValueError("start must be non-negative")

    if args.end is not None:
        end = parse_timecode(args.end)
        duration = end - start
    else:
        duration = parse_timecode(args.duration)

    if duration <= 0:
        raise ValueError("duration must be positive")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{duration:.3f}",
        "-map", "0:v:0", "-map", "0:a?",
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out),
    ]
    print(" ".join(cmd))
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
