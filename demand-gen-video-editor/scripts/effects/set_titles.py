"""Title-card family: A02 Title card dive, A03 Screenplay page, A06 Knockout captions, A07 Receipt printer,
A09 Intertitle. Timings, sizes (cqw) and colours are copied from the preview CSS in video-effect-library.html."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .core import (EASE, H, W, bezier, cq, effect, drop_shadow, fit_cover, font, keyframes, paste, rgba, round_clip,
                   rrect, seg, steps, text_layer, text_w)

CREAM = (0xEC, 0xE8, 0xDC)
GREEN = (0x16, 0x33, 0x2A)


def _line(base, txt, fnt, x, top, lh, fill, align="l", tracking=0.0, opacity=1.0, dy=0.0, pad=4):
    """Draw one CSS line box: top-of-line-box `top`, `lh` px line-height, x = left/centre/right per align.
    Mirrors CSS half-leading so numbers copied from the preview CSS land in the same place."""
    asc, desc = fnt.getmetrics()
    y = top + (lh - (asc + desc)) / 2 + dy
    w = text_w(txt, fnt, tracking)
    x0 = x if align == "l" else x - w / 2 if align == "c" else x - w
    lay = text_layer(txt, fnt, fill, tracking, pad=pad)
    paste(base, lay, (x0 - pad, y - pad), opacity)
    return w


# =========================================================================== A02 Title card dive
_PF = bezier(.6, 0, .2, 1)


@effect("A02", "Title card dive", duration=4.4, texts=["TITLE", "DIVE"])
def title_card_dive(img, t, ctx):
    """Cream title card wipes up, big serif words rise in, a phone frame of the footage zooms to full screen.
    Slot 0 = top word, slot 1 = bottom word."""
    inset = keyframes(t, [(0, 100), (.3, 0)])               # clip-path inset(top) in %
    op = keyframes(t, [(0, 1), (2.34, 1), (3.0, 0)])         # card opacity, linear
    if op <= 0.001:
        return img
    card = rgba(W, H, CREAM + (255,))
    f = font("serif", cq(24), 400)
    # word 1 (z below the phone)
    p1 = EASE(seg(t, .3, .35))
    _line(card, ctx.text(0, "TITLE"), f, W / 2, cq(12), cq(24), GREEN + (255,), "c", opacity=p1, dy=cq(3) * (1 - p1))

    # phone: pfz 2.5s per-interval cubic-bezier(.6,0,.2,1), delay .5s
    pt = t - .5
    if pt > 0:
        sc = keyframes(pt, [(0, .35), (.55, 1), (1.375, 1), (2.5, 1.95)], _PF)
        ty = keyframes(pt, [(0, 12), (.55, 0)], _PF)
        pop = keyframes(pt, [(0, 0), (.55, 1)], _PF)
        rad = cq(7) * (1 - _PF(seg(pt, 0, 2.5)))
        bw, bh = cq(56) * sc, cq(56) * 16 / 9 * sc
        bord = cq(1.4) * sc
        R = rad * sc
        ph = rrect((int(bw), int(bh)), R, (0x0E, 0x1A, 0x15, 255))
        inner = fit_cover(img, int(bw - 2 * bord), int(bh - 2 * bord))
        ph.alpha_composite(round_clip(inner, max(0.0, R - bord)), (int(bord), int(bord)))
        paste(card, ph, (W / 2 - ph.width / 2, H / 2 + cq(ty) * sc - ph.height / 2), pop)

    p2 = EASE(seg(t, 1.0, .35))
    _line(card, ctx.text(1, "DIVE"), f, W / 2, cq(140), cq(24), GREEN + (255,), "c", opacity=p2, dy=cq(3) * (1 - p2))

    y0 = int(round(inset / 100 * H))
    out = img.copy()
    if y0 < H:
        paste(out, card.crop((0, y0, W, H)), (0, y0), op)
    return out


# =========================================================================== A03 Screenplay page
_SP_DARK = (0x2A, 0x2A, 0x26, 255)
_SP_GREY = (0x9B, 0x97, 0x8A, 255)
# (slot, indent ch, dark, start s, type dur s, highlight)   None = blank row
_SP_ROWS = [(0, 0, True, .6, .8, False), None, (1, 14, True, 1.4, .3, False), (2, 10, True, 1.7, .4, False),
            (3, 5, False, 2.0, .4, False), (4, 5, False, 2.3, .5, False), (5, 5, False, 2.7, .5, True),
            (6, 5, False, 3.1, .4, False), None, (7, 17, True, 3.5, .3, False)]
_SP_DEFAULT = ["INT. GREEN ROOM - DAY", "JUSTYN", "(to camera)", "Kinetic hook.", "Title card dive.",
               "Screenplay page.", "Gravity drop.", "CUT TO:"]


@effect("A03", "Screenplay page", duration=4.4, texts=_SP_DEFAULT)
def screenplay_page(img, t, ctx):
    """Script page slides up, lines type out in Courier, the 6th line is highlighted, page lifts away.
    Slots: scene heading, character, parenthetical, 4 dialogue lines (3rd one highlighted), transition."""
    y = keyframes(t, [(0, H), (.32, 0), (3.36, 0), (3.88, -H)], EASE)
    if y >= H or y <= -H:
        return img
    page = Image.new("RGB", (W, H), CREAM)
    size = cq(3.4)
    f = font("courier", size, 400)
    ch = f.getlength("0")
    lh = size * 1.55
    asc, desc = f.getmetrics()
    left, top = cq(3.5), cq(36)
    for i, row in enumerate(_SP_ROWS):
        if row is None:
            continue
        slot, indent, dark, s, d, hl = row
        txt = ctx.text(slot, _SP_DEFAULT[slot])
        n = max(1, len(txt))
        v = steps(seg(t, s, d), n)
        if v <= 0:
            continue
        width = v * (n * ch + 1)
        rowtop = top + i * lh
        x0 = left + indent * ch
        base_y = rowtop + (lh - (asc + desc)) / 2
        lay = rgba(int(n * ch + 12), int(lh + 8))
        if hl:  # <u class=hlt>: background #dcc99a over the text's content area
            ImageDraw.Draw(lay).rectangle((2, 2, 2 + n * ch, 2 + asc + desc), fill=(0xDC, 0xC9, 0x9A, 255))
        col = _SP_DARK if (dark or hl) else _SP_GREY
        for k, c in enumerate(txt):  # monospace: place on the ch grid like the browser does
            ImageDraw.Draw(lay).text((2 + k * ch, 2), c, font=f, fill=col)
        lay = lay.crop((0, 0, int(2 + width) + 1, lay.height))
        paste_y = base_y - 2
        page.paste(lay, (int(round(x0 - 2)), int(round(paste_y))), lay)
    out = img.copy()
    out.paste(page, (0, int(round(y))))
    return out


# =========================================================================== A06 Knockout captions
def _ko_mask(ctx, sc):
    """L mask: 255 where the (scaled) knockout words are, drawn about the frame centre."""
    size = cq(31) * sc
    f = font("serif", size, 400)
    tr = -.02 * size
    lh = cq(31) * .86 * sc
    words = [ctx.text(1, "KNOCK"), ctx.text(2, "OUT")]
    cy = (H - cq(10)) / 2                  # padding-bottom 10cqw shifts the flex centre up
    cy = H / 2 + (cy - H / 2) * sc
    top = cy - lh * len(words) / 2
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    asc, desc = f.getmetrics()
    for i, wd in enumerate(words):
        w = text_w(wd, f, tr)
        x = W / 2 - w / 2
        y = top + i * lh + (lh - (asc + desc)) / 2
        for c in wd:
            d.text((x, y), c, font=f, fill=255)
            x += f.getlength(c) + tr
    return m


@effect("A06", "Knockout captions", duration=4.8, texts=["knockout", "KNOCK", "OUT"])
def knockout_captions(img, t, ctx):
    """Small green chip, then giant serif words cut out of a cream panel (footage shows through) that scales in.
    Slot 0 = chip word, slots 1-2 = the two giant lines."""
    out = img.copy()
    # chip: rise .3s ease @ .1s, gone at 1s
    if .1 <= t < 1.0:
        p = EASE(seg(t, .1, .3))
        f = font("serif", cq(8), 400)
        txt = ctx.text(0, "knockout")
        w, h = text_w(txt, f), cq(8)
        chip = rgba(int(w + cq(4.4)), int(h + cq(2)), GREEN + (255,))
        _line(chip, txt, f, cq(2.2), cq(1), h, CREAM + (255,))
        paste(out, chip, (cq(36), cq(122) + cq(3) * (1 - p)), p)
    # panel: kos 3.2s ease @ 1s, mix-blend screen
    kt = t - 1.0
    if kt < 0:
        return out
    op = keyframes(kt, [(0, 1), (2.72, 1), (3.2, 0)], EASE)
    if op <= 0.002:
        return out
    sc = keyframes(kt, [(0, 2.4), (1.12, 1)], EASE)
    m = np.asarray(_ko_mask(ctx, sc), dtype=np.float32)[..., None] / 255.0
    panel = np.array(CREAM, np.float32)[None, None, :] / 255.0 * (1 - m)          # cream, black where the words are
    base = np.asarray(out, dtype=np.float32) / 255.0
    screen = 1 - (1 - base) * (1 - panel)
    res = base * (1 - op) + screen * op
    return Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8))


# =========================================================================== A07 Receipt printer
def _receipt_paper(ctx):
    w = int(cq(56))
    h = int(math.ceil(cq(40.34)))
    pp = rgba(w, h, CREAM + (255,))
    ink = GREEN + (255,)
    soft = GREEN + (153,)
    px, py = cq(3.2), cq(3.6)
    f_b = font("mono", cq(1.8), 700)
    f_r = font("mono", cq(1.8), 500)
    lh = cq(1.8) * 1.5
    _line(pp, ctx.text(0, "EFFECT NAME"), f_b, px, py, lh, ink)
    _line(pp, ctx.text(1, "READ ALOUD"), f_r, px, py + lh, lh, soft)
    _line(pp, ctx.text(2, "1 TAKE"), f_r, w - px, py, lh, ink, "r")
    f_big = font("mono", cq(8.4), 700)
    big_lh = cq(8.4) * 1.05
    by = py + 2 * lh + cq(2.4)
    for i, key in enumerate(("RECEIPT", "PRINTER")):
        _line(pp, ctx.text(3 + i, key), f_big, px, by + i * big_lh, big_lh, ink, tracking=-.03 * cq(8.4))
    dy = by + 2 * big_lh + cq(2.4)
    d = ImageDraw.Draw(pp)
    x, seg_len = px, cq(.9)
    while x < w - px:
        d.rectangle((x, dy, min(x + seg_len, w - px), dy + cq(.3)), fill=GREEN + (102,))
        x += seg_len * 2
    ty = dy + cq(.3) + cq(1.6)
    f2 = font("mono", cq(2), 500)
    _line(pp, ctx.text(5, "TOTAL"), f2, px, ty, cq(3), ink)
    _line(pp, ctx.text(6, "2 WORDS"), font("mono", cq(2), 700), w - px, ty, cq(3), ink, "r")
    return pp


@effect("A07", "Receipt printer", duration=4.8,
        texts=["EFFECT NAME", "READ ALOUD", "1 TAKE", "RECEIPT", "PRINTER", "TOTAL", "2 WORDS"])
def receipt_printer(img, t, ctx):
    """A receipt prints out of a dark slot in 10 steps, then vanishes. Slots: label, sub-label, right tag,
    the two big words, total label, total value."""
    out = img.copy()
    gone = 1 - seg(t, 4.0, .3)
    if gone <= 0:
        return out
    v = steps(seg(t, .3, 1.8), 10)
    pp = ctx.cached("A07paper", lambda: _receipt_paper(ctx))
    x0, y0 = cq(3), cq(42)
    vis = int(round(pp.height * v))
    if vis > 0:
        paste(out, pp.crop((0, 0, pp.width, vis)), (x0, y0), gone)
    slot = rrect((int(cq(59)), int(cq(2.6))), cq(1.3), GREEN + (255,), (0x3A, 0x6A, 0x58, 255), max(1, int(cq(.25))))
    dr = ImageDraw.Draw(slot)
    r = cq(.4)
    for cx in (cq(1.2) + r, slot.width - cq(1.2) - r):
        dr.ellipse((cx - r, slot.height / 2 - r, cx + r, slot.height / 2 + r), fill=CREAM + (255,))
    slot = drop_shadow(slot, blur=cq(1), offset=(0, int(cq(.6))), color=(0, 0, 0, 178))
    pad = (slot.width - int(cq(59))) // 2
    paste(out, slot, (x0 - cq(1.5) - pad, y0 + cq(40) * v - pad), gone)
    return out


# =========================================================================== A09 Intertitle
_FL = [(0, 0), (.04, .8), (.09, 1), (.14, .7), (.22, 1), (.33, .85), (.44, 1), (.55, .75), (.70, 1), (.85, .8), (1.0, 1)]
GOLD = (0xC8, 0xA9, 0x5D)


def _flicker(t):
    """fl keyframes with steps(1,end): holds each keyframe's value until the next one. Runs 3s starting at 1s."""
    p = (t - 1.0) / 3.0
    if p < 0:
        return 0.0
    v = _FL[0][1]
    for k, val in _FL:
        if p >= k:
            v = val
    return v


def _grain_tile(ctx):
    rng = np.random.default_rng(3)
    n = rng.random((200, 200)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((int(cq(30)), int(cq(30))), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0


_GR_SHIFT = [(0, 0), (-5, 3), (4, -6), (-3, 5), (6, 2)]


def _intertitle_card(ctx, t):
    card = Image.new("RGB", (W, H), GREEN)
    # frame, left 4cqw top 30cqw 54 x 74
    fl = _flicker(t)
    if fl > 0:
        fm = rgba(W, H)
        d = ImageDraw.Draw(fm)
        x0, y0, x1, y1 = cq(4), cq(30), cq(58), cq(104)
        d.rectangle((x0, y0, x1, y1), outline=GOLD + (153,), width=max(1, int(cq(.35))))
        d.rectangle((x0 + cq(.35) + cq(1.6), y0 + cq(.35) + cq(1.6), x1 - cq(.35) - cq(1.6), y1 - cq(.35) - cq(1.6)),
                    outline=GOLD + (85,), width=max(1, int(cq(.2))))
        r = cq(.6)
        for cx, cy in ((x0 + cq(.15), y0 + cq(.15)), (x1 - cq(.15), y0 + cq(.15)), (x0 + cq(.15), y1 - cq(.15)),
                       (x1 - cq(.15), y1 - cq(.15))):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD + (255,))
        # .in9: flex column centred in the frame
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        total = cq(4 + .3 + 4 + 10.5 + 4 + .3 + 4)
        top = cy - total / 2
        for k in (0, 1):
            oy = top + cq(4) + (0 if k == 0 else cq(.3 + 4 + 10.5 + 4))
            d.rectangle((cx - cq(8), oy, cx + cq(8), oy + cq(.3)), fill=GOLD + (255,))
            if k == 0:
                dm = rgba(int(cq(2.2)), int(cq(2.2)))
                dd = ImageDraw.Draw(dm)
                c = dm.width / 2
                a = cq(1.7) / 2
                dd.polygon([(c, c - a * 1.414), (c + a * 1.414, c), (c, c + a * 1.414), (c - a * 1.414, c)],
                           fill=GREEN + (255,), outline=GOLD + (255,), width=max(1, int(cq(.3))))
                fm.alpha_composite(dm, (int(cx - c), int(oy + cq(.15) - c)))
        f = font("serif", cq(10.5), 400, italic=True)
        _line(fm, ctx.text(0, "Intertitle."), f, cx, top + cq(4 + .3 + 4), cq(10.5), CREAM + (255,), "c")
        card = Image.alpha_composite(card.convert("RGBA"), _with_op(fm, fl)).convert("RGB")
    # grain: screen blend @ .3, 5-step jitter every .1s
    tile = ctx.cached("A09grain", lambda: _grain_tile(ctx))
    k = int((t * 10) % 5)
    sx, sy = int(_GR_SHIFT[k][0] / 100 * W), int(_GR_SHIFT[k][1] / 100 * H)
    th, tw = tile.shape
    ys = (np.arange(H) + sy) % th
    xs = (np.arange(W) + sx) % tw
    g = tile[np.ix_(ys, xs)][..., None] * .3
    a = np.asarray(card, dtype=np.float32) / 255.0
    a = 1 - (1 - a) * (1 - g)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _with_op(layer, o):
    a = layer.getchannel("A").point(lambda v: int(v * o))
    layer = layer.copy()
    layer.putalpha(a)
    return layer


_IRIS = bezier(.6, 0, .2, 1)


@effect("A09", "Intertitle", duration=4.8, texts=["Intertitle."])
def intertitle(img, t, ctx):
    """Footage dips to black as a green iris opens onto a gold-framed silent-film title card with grain.
    Slot 0 = the italic title."""
    bk = EASE(seg(t, 0, .4))
    out = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), bk)
    ip = _IRIS(seg(t, .3, .9))
    if ip <= 0:
        return out
    r = .8 * math.sqrt((W * W + H * H) / 2) * ip
    big = Image.new("L", (W * 2, H * 2), 0)                  # 2x supersampled iris edge
    ImageDraw.Draw(big).ellipse((W - r * 2, H - r * 2, W + r * 2, H + r * 2), fill=255)
    m = big.resize((W, H), Image.LANCZOS)
    card = _intertitle_card(ctx, t)
    return Image.composite(card, out, m)
