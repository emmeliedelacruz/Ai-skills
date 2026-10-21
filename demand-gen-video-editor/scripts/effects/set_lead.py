"""A01 Kinetic hook and A05 Grade slider. Reference implementations: copy their structure."""
from PIL import Image, ImageDraw

from .core import (EASE_IN_OUT, SPRING, W, H, cq, css_filter, effect, font, keyframes, paste, place, rgba, rrect,
                   seg, text_layer, text_w, ellipse, drop_shadow)

SWEEP = 3.4  # seconds; preview: 0% x=96 -> 55% x=8 -> 100% x=52, ease-in-out per span


@effect("A05", "Grade slider", duration=5.0, texts=["BEFORE", "AFTER"])
def grade_slider(img, t, ctx):
    p = min(t, SWEEP)
    x = keyframes(p, [(0, 96), (0.55 * SWEEP, 8), (SWEEP, 52)], EASE_IN_OUT) / 100 * W

    # graded half (right of the split): brightness 1.12 saturate .65 sepia .15 contrast .92
    graded = css_filter(img, brightness=1.12, saturate=.65, sepia_amt=.15, contrast=.92)
    out = img.copy()
    xi = int(round(x))
    if xi < W:
        out.paste(graded.crop((xi, 0, W, H)), (xi, 0))

    # split line, .5cqw white with soft shadow
    lw = max(2, int(cq(.5)))
    line = drop_shadow(rgba(lw, H, (255, 255, 255, 255)), blur=cq(.75), offset=(0, 0), color=(0, 0, 0, 85))
    paste(out, line, (x - line.width / 2, -(line.height - H) / 2))

    # handle: [BEFORE] (knob) [AFTER], centred on the line at top:113cqw
    f = font("mono", cq(1.9), 500)
    tr = .12 * cq(1.9)
    labels = []
    for s in (ctx.text(0, "BEFORE"), ctx.text(1, "AFTER")):
        tw = text_w(s, f, tr)
        padx, pady = cq(1.3), cq(.8)
        box = rrect((int(tw + padx * 2), int(f.size * 1.2 + pady * 2)), cq(1), (0, 0, 0, 136))
        tl = text_layer(s, f, (255, 255, 255, 255), tr, pad=0)
        paste(box, tl, (padx, pady + (box.height - pady * 2 - tl.height) / 2))
        labels.append(box)
    kd = int(cq(9))
    knob = ellipse((kd, kd), (0x16, 0x33, 0x2a, 255), (255, 255, 255, 255), int(cq(.5)))
    kt = text_layer("‹›", font("sans", cq(4.4), 600), (255, 255, 255, 255), cq(.2), pad=0)
    paste(knob, kt, ((kd - kt.width) / 2, (kd - kt.height) / 2))
    gap = cq(1.2)
    total = labels[0].width + gap + kd + gap + labels[1].width
    cy = cq(113)
    x0 = x - total / 2
    paste(out, labels[0], (x0, cy - labels[0].height / 2))
    paste(out, knob, (x0 + labels[0].width + gap, cy - kd / 2))
    paste(out, labels[1], (x0 + labels[0].width + gap + kd + gap, cy - labels[1].height / 2))
    return out


@effect("A01", "Kinetic hook", duration=4.2, texts=["KINETIC", "HOOK"], outro_fade=0)
def kinetic_hook(img, t, ctx):
    """Letters slam in one by one (spring, scale .6->1, rise 40%), hold, fade out at 3.4s.
    Preview CSS: .k left 4cqw top 46cqw, 800 19cqw/.86, tracking -.035em, shadow 0 .5cqw 2cqw #0006."""
    words = [ctx.text(0, "KINETIC"), ctx.text(1, "HOOK")]
    starts = [.1, .55]
    size = cq(19)
    f = font("sans", size, 800)
    tr = -.035 * size
    line_h = size * .86
    out = img.copy()
    fade = 1 - seg(t, 3.4, .3)
    if fade <= 0:
        return out
    for li, word in enumerate(words):
        x = cq(4)
        top = cq(46) + li * line_h
        for i, ch in enumerate(word):
            adv = f.getlength(ch) + tr
            if ch != " ":
                p = SPRING(seg(t, i * .045 + starts[li % 2] if li < 2 else starts[1] + li * .45, .22))
                if p > 0:
                    lay = text_layer(ch, f, (255, 255, 255, 255), pad=int(cq(3)),
                                     shadow=(0, int(cq(.5)), cq(2), (0, 0, 0, 102)))
                    sc = .6 + .4 * p
                    # translateY(40% * (1-p)) of the glyph box height
                    dy = .4 * (1 - p) * line_h
                    cx = x + f.getlength(ch) / 2
                    cy = top + line_h / 2 + dy + (size * .09)
                    place(out, lay, cx, cy, scale=sc, opacity=min(1.0, max(0.0, p * 1.6)) * fade)
            x += adv
    return out
