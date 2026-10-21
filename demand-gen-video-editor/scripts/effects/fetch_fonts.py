#!/usr/bin/env python3
"""Download the open-licence (OFL) Google Fonts the effect library uses into ./fonts.

Run once: python3 -I fetch_fonts.py
Effects fall back to installed system fonts if these are missing (look will differ slightly).
"""
import os, sys, urllib.request, urllib.parse

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FILES = [
    "instrumentserif/InstrumentSerif-Regular.ttf",
    "instrumentserif/InstrumentSerif-Italic.ttf",
    "caveat/Caveat[wght].ttf",
    "courierprime/CourierPrime-Regular.ttf",
    "courierprime/CourierPrime-Bold.ttf",
    "intertight/InterTight[wght].ttf",
    "intertight/InterTight-Italic[wght].ttf",
    "jetbrainsmono/JetBrainsMono[wght].ttf",
]


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    os.makedirs(out, exist_ok=True)
    for f in FILES:
        name = os.path.basename(f)
        dst = os.path.join(out, name)
        if os.path.exists(dst):
            continue
        url = BASE + urllib.parse.quote(f, safe="/")
        try:
            urllib.request.urlretrieve(url, dst)
            print("ok  ", name)
        except Exception as e:  # noqa: BLE001
            print("FAIL", name, e, file=sys.stderr)


if __name__ == "__main__":
    main()
