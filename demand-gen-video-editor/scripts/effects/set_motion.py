"""A04 Gravity drop, A08 Mood curtain, A10 Comment CTA, A11 Magazine cover, A12 Odometer recursion."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .core import (EASE, EASE_OUT, SPRING, W, H, bezier, clamp01, cq, drop_shadow, effect, ellipse, fit_cover,
                   font, gradient, lerp, paste, rgba, rrect, seg, text_layer, text_w)

# --------------------------------------------------------------------------- local helpers


def _text(txt, fnt, fill, tracking=0.0, shadow=None):
    """Text layer plus the offset of the glyph origin and the font content height."""
    pad = 6 + int(fnt.size * .1)
    lay = text_layer(txt, fnt, fill, tracking, pad=pad, shadow=shadow)
    extra = int(abs(shadow[0]) + abs(shadow[1]) + shadow[2] * 3) if shadow else 0
    asc, desc = fnt.getmetrics()
    return lay, pad + extra, asc + desc


def _put(base, layer, anchor, dest, scale=1.0, rot=0.0, opacity=1.0):
    """Paste layer so its `anchor` point lands on `dest`, scaling/rotating (clockwise deg) about the anchor."""
    if opacity <= 0.002 or scale <= 0.002:
        return base
    lw, lh = layer.size
    lay = layer
    if abs(scale - 1) > 1e-3:
        lay = lay.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.BICUBIC)
    ax, ay = (anchor[0] - lw / 2) * scale, (anchor[1] - lh / 2) * scale
    if abs(rot) > 1e-3:
        lay = lay.rotate(-rot, expand=True, resample=Image.BICUBIC)
        th = math.radians(rot)
        ax, ay = ax * math.cos(th) - ay * math.sin(th), ax * math.sin(th) + ay * math.cos(th)
    return paste(base, lay, (dest[0] - ax - lay.width / 2, dest[1] - ay - lay.height / 2), opacity)


def _line(base, txt, fnt, x, line_top, line_h, fill, tracking=0.0, shadow=None, opacity=1.0, dy=0.0, scale=1.0,
          rot=0.0, centered_on=None, layer_cache=None):
    """Draw one CSS-style line box: text laid out with line-height `line_h` from top `line_top`, left `x`.
    Transforms pivot on the line box centre (CSS transform-origin 50% 50%)."""
    key = (txt, id(fnt), tuple(fill), tracking, shadow)
    if layer_cache is not None and key in layer_cache:
        lay, ox, ch = layer_cache[key]
    else:
        lay, ox, ch = _text(txt, fnt, fill, tracking, shadow)
        if layer_cache is not None:
            layer_cache[key] = (lay, ox, ch)
    w = text_w(txt, fnt, tracking)
    if centered_on is not None:
        x = centered_on - w / 2
    anchor = (ox + w / 2, ox + ch / 2)
    return _put(base, lay, anchor, (x + w / 2, line_top + line_h / 2 + dy), scale, rot, opacity)


def _grad_circle(d, c0, c1):
    g = gradient((d, d), c0, c1, 135)
    g.putalpha(ellipse((d, d)).getchannel("A"))
    return g


def _rise(t, t0, dur):
    p = EASE(seg(t, t0, dur))
    return p, (1 - p) * cq(3)  # opacity, translateY px


# --------------------------------------------------------------------------- A04 gravity drop
_B_IN = bezier(.55, 0, 1, .45)
_B_OUT = bezier(0, .55, .45, 1)
_DROP_ROT = [-24, 18, -28, 22, -16, 26]  # preview uses random +-30deg; fixed so renders are repeatable


def _drop(p, r):
    """drp keyframes: fall from -75cqw spinning, bounce to -6cqw, -1.5cqw, settle. Returns (dy_cqw, rot_deg)."""
    if p < .45:
        e = _B_IN(p / .45)
        return lerp(-75, 0, e), r * (1 - e)
    if p < .65:
        return lerp(0, -6, _B_OUT((p - .45) / .2)), 0.0
    if p < .80:
        return lerp(-6, 0, _B_IN((p - .65) / .15)), 0.0
    if p < .90:
        return lerp(0, -1.5, EASE_OUT((p - .80) / .10)), 0.0
    return lerp(-1.5, 0, (p - .90) / .10), 0.0


@effect("A04", "Gravity drop", duration=4.6, texts=["gravity", "DROP"], outro_fade=0)
def gravity_drop(img, t, ctx):
    """Serif letters fall in spinning and bounce. text 0 = small italic gold lead-in, text 1 = big dropped word."""
    out = img.copy()
    fade = 1 - EASE(seg(t, 3.8, .3))
    if fade <= 0:
        return out
    cache = ctx.cached("a04_layers", dict)
    glow = (0, 0, cq(1.5), (0xec, 0xe8, 0xdc, 0x88))
    small_f = font("serif", cq(10), 400, italic=True)
    big_f = font("serif", cq(36), 400)
    tr = -.02 * cq(36)
    left, top = cq(3), cq(22)
    op, dy = _rise(t, .1, .5)
    _line(out, ctx.text(0, "gravity"), small_f, left, top, cq(10), (0xa9, 0x8a, 0x3e, 255), shadow=glow,
          opacity=op * fade, dy=dy, layer_cache=cache)
    word = ctx.text(1, "DROP")
    line_top, line_h = top + cq(10) - cq(2), cq(36) * .9
    x = left
    for i, ch in enumerate(word):
        adv = big_f.getlength(ch) + tr
        p = seg(t, .5 + i * .18, 1.3)
        if ch != " " and (t >= .5 + i * .18):
            ddy, rot = _drop(p, _DROP_ROT[i % len(_DROP_ROT)])
            lay_w = adv
            _line(out, ch, big_f, x, line_top, line_h, (0x16, 0x33, 0x2a, 255), shadow=glow, opacity=fade,
                  dy=cq(ddy), rot=rot, layer_cache=cache)
        x += adv
    return out


# --------------------------------------------------------------------------- A08 mood curtain
def _mood_filter(img, p):
    """filter: saturate(.25) brightness(.65) contrast(1.1) hue-rotate(185deg), each interpolated from identity by p."""
    sat, bri, con, hue = lerp(1, .25, p), lerp(1, .65, p), lerp(1, 1.1, p), lerp(0, 185, p)
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = np.array([.213, .715, .072], np.float32)
    g = (a * lum).sum(-1, keepdims=True)
    a = g + (a - g) * sat
    a = a * bri
    a = (a - .5) * con + .5
    th = math.radians(hue)
    c, s = math.cos(th), math.sin(th)
    m = np.array([[.213 + c * .787 - s * .213, .715 - c * .715 - s * .715, .072 - c * .072 + s * .928],
                  [.213 - c * .213 + s * .143, .715 + c * .285 + s * .140, .072 - c * .072 - s * .283],
                  [.213 - c * .213 - s * .787, .715 - c * .715 + s * .715, .072 + c * .928 + s * .072]], np.float32)
    a = np.clip(a, 0, 1) @ m.T
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _vignette_alpha():
    """radial-gradient(ellipse at 50% 45%, transparent 40%, #000b), farthest-corner ellipse. Returns float alpha HxW."""
    cx, cy = .5 * W, .45 * H
    ry_over_rx = min(cy, H - cy) / min(cx, W - cx)
    fx, fy = max(cx, W - cx), max(cy, H - cy)
    rx = math.sqrt(fx ** 2 + (fy / ry_over_rx) ** 2)
    ry = rx * ry_over_rx
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xs - cx) / rx, (ys - cy) / ry)
    return (np.clip((d - .4) / .6, 0, 1) * (0xbb / 255.0)).astype(np.float32)


@effect("A08", "Mood curtain", duration=4.8, texts=[], outro_fade=0)
def mood_curtain(img, t, ctx):
    """Footage drains to a moody blue-grey grade with a vignette, then a dark green curtain rises and fills the frame.
    Ends on the solid curtain colour: cut to the next scene/title card at `--at + duration`."""
    p = EASE(seg(t, .3, 2.2))
    out = _mood_filter(img, p) if p > 0 else img.copy()
    vp = EASE(seg(t, .3, 2.0))
    if vp > 0:
        va = ctx.cached("a08_vig", _vignette_alpha)
        a = np.asarray(out, dtype=np.float32) * (1 - va * vp)[..., None]
        out = Image.fromarray(a.astype(np.uint8))
    cp = bezier(.6, 0, .3, 1)(seg(t, 2.3, 1.3))
    if cp > 0:
        y = int(round(H * (1 - cp)))
        d = ImageDraw.Draw(out)
        d.rectangle((0, y, W, H), fill=(0x0f, 0x26, 0x1f))
        d.rectangle((0, y, W, y + int(cq(1.4)) - 1), fill=(0xf3, 0xef, 0xe3))
    return out


# --------------------------------------------------------------------------- A10 comment CTA
_WHITE = (255, 255, 255, 255)
_INK = (0x14, 0x21, 0x1b, 255)
_SHADOW = (0, cq(1), cq(2), (0, 0, 0, 0x44))


def _card_base(ctx, key, w, h, radius):
    """Cached white rounded card with its soft drop shadow baked in; returns (layer, pad)."""
    def build():
        lay = rrect((int(cq(w)), int(cq(h))), cq(radius), _WHITE)
        sh = drop_shadow(lay, blur=cq(2), offset=(0, int(cq(1))), color=(0, 0, 0, 0x44))
        return sh, (sh.width - lay.width) // 2
    return ctx.cached(("a10card", key), build)


def _heart(size_w, color):
    """Outline heart (the preview's ♡) as an RGBA layer."""
    ss = 4
    w = int(size_w * ss)
    h = int(size_w * .92 * ss)
    big = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pts = []
    for i in range(120):
        a = i / 120 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((w / 2 + x / 34 * w * .96, h / 2 + (y + 2.5) / 32 * h * .96))
    ImageDraw.Draw(big).line(pts + pts[:1], fill=color, width=int(cq(.42) * ss), joint="curve")
    return big.resize((w // ss, h // ss), Image.LANCZOS)


def _avatar(d, kind):
    return _grad_circle(int(cq(d)), (0x7b, 0xb8, 0x9a), (0x2f, 0x6a, 0x53)) if kind == "a" else \
        _grad_circle(int(cq(d)), (0xd4, 0xaa, 0x8f), (0x8a, 0x5f, 0x45))


def _pop(t, t0, dur=.3):
    p = bezier(.2, 1.5, .4, 1)(seg(t, t0, dur))
    return .4 + .6 * p, clamp01(p)


def _cap(out, parts, size, y, op, dy):
    f = font("sans", cq(size), 500)
    fb = font("sans", cq(size), 800)
    widths = [text_w(s, fb if b else f) for s, b in parts]
    pw = cq(2.6)
    w, h = sum(widths) + pw * 2, cq(size) * 1.2 + cq(1.2) * 2
    box = rrect((int(w), int(h)), cq(2.4), _WHITE)
    x = pw
    for (s, b), tw in zip(parts, widths):
        tl, ox, ch = _text(s, fb if b else f, _INK)
        paste(box, tl, (x - ox, cq(1.2) + (cq(size) * 1.2 - ch) / 2 - ox))
        x += tw
    paste(out, box, (W / 2 - box.width / 2, y + dy), op)


@effect("A10", "Comment CTA", duration=5.2,
        texts=["EDIT", "creator", "Sent. Check your DMs.", "to get all of these and more"], outro_fade=0.25)
def comment_cta(img, t, ctx):
    """Comment box types a keyword, posts it, and an auto-reply lands. text 0 = keyword, 1 = replier handle,
    2 = auto-reply, 3 = second caption line."""
    out = img.copy()
    kw = ctx.text(0, "EDIT")
    sans = lambda s, w: font("sans", cq(s), w)  # noqa: E731
    cache = ctx.cached("a10_text", dict)

    # --- c1: composer (0.1s .. 1.55s)
    op, dy = _rise(t, .1, .3)
    if 0 < op and t < 1.55:
        base, pad = _card_base(ctx, "c1", 64, 11, 8)
        card = base.copy()
        L = rgba(int(cq(64)), int(cq(11)))
        L.alpha_composite(_avatar(7, "a"), (int(cq(2)), int(cq(2))))
        fi_x, fi_y = cq(11.4), cq(3.5)
        if t < .55:
            tl, ox, ch = _text("Add a comment…", sans(3.4, 500), (0x8a, 0x8f, 0x8c, 255))
            paste(L, tl, (fi_x - ox, fi_y + cq(.2) - ox))
        wf = int(round(math.floor(seg(t, .6, .8) * 4) / 4 * cq(11))) if seg(t, .6, .8) < 1 else int(cq(11))
        tl, ox, ch = _text(kw, sans(3.8, 700), _INK)
        line_off = (cq(4) - ch) / 2
        txt = tl.crop((int(ox), 0, int(ox + wf), tl.height)) if wf > 0 else None
        if txt is not None:
            paste(L, txt, (fi_x, fi_y + line_off - ox))
        ImageDraw.Draw(L).rectangle((fi_x + wf, fi_y, fi_x + wf + cq(.35) - 1, fi_y + cq(4) - 1), fill=(0x16, 0x33, 0x2a, 255))
        sb = ellipse((int(cq(7)), int(cq(7))), (0x16, 0x33, 0x2a, 255) if t >= .6 else (0xc9, 0xcc, 0xc8, 255))
        al, ox2, ch2 = _text("↑", sans(3.6, 500), _WHITE)
        paste(sb, al, ((sb.width - text_w("↑", sans(3.6, 500))) / 2 - ox2, (sb.height - ch2) / 2 - ox2))
        paste(L, sb, (cq(55), cq(2)))
        card.alpha_composite(L, (pad, pad))
        paste(out, card, (cq(3) - pad, cq(4) - pad + dy), op)

    # --- c2: your posted comment (pops at 1.55s)
    s, o = _pop(t, 1.55)
    if o > 0:
        base, pad = _card_base(ctx, "c2", 64, 12, 5)
        card = base.copy()
        L = rgba(int(cq(64)), int(cq(12)))
        L.alpha_composite(_avatar(7, "a"), (int(cq(2.4)), int(cq(2.5))))
        tx = cq(11.8)
        tl, ox, ch = _text("you · now", sans(2, 500), (0x7b, 0x81, 0x7e, 255))
        paste(L, tl, (tx - ox, cq(2.4) + (cq(2.2) - ch) / 2 - ox))
        tl, ox, ch = _text(kw, sans(4.6, 800), _INK)
        paste(L, tl, (tx - ox, cq(5) + (cq(4.6) - ch) / 2 - ox))
        hc = (0xe0, 0x40, 0x5a, 255) if t >= 3 else _INK
        hl = _heart(cq(4), hc)
        paste(L, hl, (cq(57), cq(6) - hl.height / 2))
        card.alpha_composite(L, (pad, pad))
        cx, cy = cq(3) + cq(32), cq(4) + cq(6)
        _put(out, card, (card.width / 2, card.height / 2), (cx, cy), s, 0, o)

    # --- c3: auto-reply (pops at 2.2s)
    s, o = _pop(t, 2.2)
    if o > 0:
        h3 = 2 * 2 + 2.2 + .4 + 3.2 * 1.2
        base, pad = _card_base(ctx, "c3", 62, h3, 5)
        card = base.copy()
        L = rgba(int(cq(62)), int(cq(h3)))
        L.alpha_composite(_avatar(6, "b"), (int(cq(2.4)), int(cq((h3 - 6) / 2))))
        tx = cq(10.8)
        tl, ox, ch = _text(f"{ctx.text(1, 'creator')} · now", sans(2, 500), (0x7b, 0x81, 0x7e, 255))
        paste(L, tl, (tx - ox, cq(2) + (cq(2.2) - ch) / 2 - ox))
        tl, ox, ch = _text(ctx.text(2, "Sent. Check your DMs."), sans(3.2, 600), _INK)
        paste(L, tl, (tx - ox, cq(2 + 2.2 + .4) + (cq(3.84) - ch) / 2 - ox))
        card.alpha_composite(L, (pad, pad))
        cx, cy = cq(5) + cq(31), cq(22) + cq(h3 / 2)
        _put(out, card, (card.width / 2, card.height / 2), (cx, cy), s, 0, o)

    # --- captions
    op, dy = _rise(t, 1.7, .3)
    if op > 0:
        _cap(out, [("Comment ", False), (kw, True)], 4.2, cq(110), op, dy)
    op, dy = _rise(t, 2.4, .3)
    if op > 0:
        _cap(out, [(ctx.text(3, "to get all of these and more"), False)], 3.8, cq(122), op, dy)
    return out


# --------------------------------------------------------------------------- A11 magazine cover
_GOLD = (0xc8, 0xa9, 0x5d, 255)


@effect("A11", "Magazine cover", duration=4.8,
        texts=["OCTOBER 2026 · ISSUE NO. 3", "ON THE COVER", "Magazine|cover.", "COVER", "Shot in|one|take"])
def magazine_cover(img, t, ctx):
    """Gold frame, cover lines and a sticker over live footage. text 0 = dateline, 1 = kicker, 2 = headline
    (use | for a line break), 3 = giant masthead word, 4 = sticker lines (| separated, middle line italic)."""
    out = img.copy()
    fade = 1 - EASE(seg(t, 4.0, .3))
    if fade <= 0:
        return out
    mz = rgba(W, H)
    cache = ctx.cached("a11_text", dict)
    mono = font("mono", cq(1.9), 500)

    # frame draws in left -> right (clip-path inset(0 100% 0 0) -> 0)
    p = EASE(seg(t, .1, .9))
    if p > 0:
        fr = rrect((int(cq(63)), int(cq(87))), 0, (0, 0, 0, 0), _GOLD, int(cq(.3)), ss=1)
        fr = fr.crop((0, 0, max(1, int(fr.width * p)), fr.height))
        paste(mz, fr, (cq(3), cq(19)))

    op, dy = _rise(t, .7, .4)
    _line(mz, ctx.text(0, "OCTOBER 2026 · ISSUE NO. 3"), mono, cq(6), cq(22), cq(1.9), _GOLD, .12 * cq(1.9),
          opacity=op, dy=dy, layer_cache=cache)
    op, dy = _rise(t, 1.0, .4)
    _line(mz, ctx.text(1, "ON THE COVER"), mono, cq(6), cq(45), cq(1.9), _GOLD, .16 * cq(1.9), opacity=op, dy=dy,
          layer_cache=cache)

    serif12 = font("serif", cq(12), 400)
    sh = (0, 0, cq(1), (0, 0, 0, 0xb0))
    lines = ctx.text(2, "Magazine|cover.").split("|") if "|" in ctx.text(2, "Magazine|cover.") else \
        ctx.text(2, "Magazine|cover.").split(" ", 1)
    for i, s in enumerate(lines[:3]):
        op, dy = _rise(t, 1.1 + .25 * i, .45)
        _line(mz, s, serif12, cq(6), cq(50) + i * cq(12) * .95, cq(12) * .95, _WHITE, shadow=sh, opacity=op, dy=dy,
              layer_cache=cache)

    serif27 = font("serif", cq(27), 400)
    tr = -.02 * cq(27)
    x = cq(5)
    for i, ch in enumerate(ctx.text(3, "COVER")):
        adv = serif27.getlength(ch) + tr
        q = SPRING(seg(t, 1.6 + i * .07, .3))
        if ch != " " and q > 0:
            _line(mz, ch, serif27, x, cq(68), cq(27), (0xec, 0xe8, 0xdc, 255), opacity=clamp01(q),
                  dy=.4 * (1 - q) * cq(27), scale=.6 + .4 * q, layer_cache=cache)
        x += adv

    # barcode: repeating-linear-gradient(90deg, #fff 0 .4, transparent .4 .9, #fff .9 1.8, transparent 1.8 2.2)
    op = EASE(seg(t, 2.1, .4))
    if op > 0:
        bw, bh = int(cq(12)), int(cq(6))
        col = np.zeros(bw, np.uint8)
        for xx in range(bw):
            m = (xx / CQW_PX) % 2.2
            col[xx] = 255 if (m < .4 or .9 <= m < 1.8) else 0
        arr = np.zeros((bh, bw, 4), np.uint8)
        arr[..., :3] = 255
        arr[..., 3] = col[None, :]
        paste(mz, Image.fromarray(arr, "RGBA"), (cq(6), cq(96)), op)

    # sticker
    q = SPRING(seg(t, 2.3, .5))
    if q > 0:
        d = int(cq(13))
        stk = ellipse((d, d), _GOLD)
        small, ital = font("sans", cq(2.1), 600), font("serif", cq(3.4), 400, italic=True)
        ls = ctx.text(4, "Shot in|one|take").split("|")
        hs = [cq(2.1) * 1.05, cq(3.4), cq(2.1) * 1.05][: len(ls)]
        y = (d - sum(hs)) / 2
        for k, s in enumerate(ls[:3]):
            fnt = ital if k == 1 else small
            tl, ox, ch = _text(s, fnt, (0x16, 0x33, 0x2a, 255))
            paste(stk, tl, ((d - text_w(s, fnt)) / 2 - ox, y + (hs[k] - ch) / 2 - ox))
            y += hs[k]
        _put(mz, stk, (d / 2, d / 2), (cq(51) + d / 2, cq(24) + d / 2), .3 + .7 * q, lerp(-40, -10, q), clamp01(q))

    paste(out, mz, (0, 0), fade)
    return out


CQW_PX = W / 100.0


# --------------------------------------------------------------------------- A12 odometer recursion
def _nested_frame(img, w, h, border, radius, depth):
    """Footage in a cream-bordered rounded frame that contains a smaller copy of itself, `depth` times."""
    w, h = max(2, w), max(2, h)
    box = rrect((w, h), radius, (0xec, 0xe8, 0xdc, 255))
    border = min(border, (min(w, h) - 1) // 2)
    iw, ih = w - 2 * border, h - 2 * border
    if iw < 2 or ih < 2:
        return box
    inner = fit_cover(img, iw, ih).convert("RGBA")
    if depth > 0:
        cw = int(round(iw * .46))
        ch = int(round(cw * 16 / 9))
        child = _nested_frame(img, cw, ch, int(round(cq(.45))), cq(1), depth - 1)
        inner.alpha_composite(child, (int(round(iw * .06)), int(round(ih * .06))))
    inner.putalpha(rrect((iw, ih), max(0.0, radius - border), (255, 255, 255, 255)).getchannel("A"))
    box.alpha_composite(inner, (border, border))
    return box


@effect("A12", "Odometer recursion", duration=4.8, texts=["RAW TAKE", "0:24"])
def odometer_recursion(img, t, ctx):
    """Counter rolls to the take length, then the footage nests inside itself. text 0 = counter title,
    text 1 = final time (digits and colon, e.g. 0:24)."""
    out = img.copy()
    serif17, serif15 = font("serif", cq(17), 400), font("serif", cq(15), 400)
    stamp = ctx.text(1, "0:24")

    if t < 1.9:
        panel_w, dg_w, dg_h, gap = cq(63), cq(13), cq(19), cq(1.2)
        panel_h = cq(3 + 2.2 + 2.4 + 19 + 3.4)

        def build_static():
            base = rrect((int(panel_w), int(panel_h)), cq(3), (0x16, 0x33, 0x2a, 255))
            ttl = ctx.text(0, "RAW TAKE")
            f6 = font("mono", cq(2.2), 500)
            tl, ox, ch = _text(ttl, f6, _GOLD, .3 * cq(2.2))
            paste(base, tl, ((panel_w - text_w(ttl, f6, .3 * cq(2.2))) / 2 - ox, cq(3) + (cq(2.2) - ch) / 2 - ox))
            return drop_shadow(base, blur=cq(2), offset=(0, int(cq(1))), color=(0, 0, 0, 0x66))

        sh = ctx.cached("a12_panel", build_static)
        pad = (sh.width - int(panel_w)) // 2
        panel = sh.copy()

        # strip of digits, 2 cycles of 0-9, one pre-rendered column per digit slot
        def strip():
            s = Image.new("RGBA", (int(dg_w), int(dg_h * 20)), (0, 0, 0, 0))
            for r in range(20):
                ch = str(r % 10)
                tl, ox, th = _text(ch, serif17, (0xec, 0xe8, 0xdc, 255))
                paste(s, tl, ((dg_w - serif17.getlength(ch)) / 2 - ox, r * dg_h + (dg_h - th) / 2 - ox))
            return s
        st = ctx.cached("a12_strip", strip)

        items = [("c" if ch == ":" else "d", ch) for ch in stamp if ch == ":" or ch.isdigit()]
        colon_w = serif15.getlength(":")
        widths = [colon_w if k == "c" else dg_w for k, _ in items]
        total = sum(widths) + gap * (len(items) - 1)
        x = pad + (panel_w - total) / 2
        top = pad + cq(3 + 2.2 + 2.4)
        k = 0
        for (kind, ch), w in zip(items, widths):
            if kind == "c":
                tl, ox, th = _text(":", serif15, _GOLD)
                paste(panel, tl, (x - ox, top + cq(1) + (cq(15) - th) / 2 - ox))
            else:
                n = 10 + int(ch)
                prog = bezier(.2, .8, .2, 1)(seg(t, .3 + k * .18, 1.4))
                off = int(round(prog * n * dg_h))
                win = Image.new("RGBA", (int(dg_w), int(dg_h)), (0, 0, 0, 0))
                win.paste(st.crop((0, off, int(dg_w), off + int(dg_h))), (0, 0))
                well = rrect((int(dg_w), int(dg_h)), cq(1.6), (0x0e, 0x23, 0x1c, 255))
                well.alpha_composite(win)
                ImageDraw.Draw(well).rectangle((0, dg_h / 2, dg_w, dg_h / 2 + max(1, cq(.25)) - 1), fill=(0, 0, 0, 0x66))
                well.putalpha(rrect((int(dg_w), int(dg_h)), cq(1.6), _WHITE).getchannel("A"))
                paste(panel, well, (x, top))
                k += 1
            x += w + gap
        paste(out, panel, (cq(3) - pad, cq(10) - pad))

    s, o = _pop(t, 1.9, .4)
    if o > 0:
        w = int(cq(30))
        h = int(w * 16 / 9)
        fr = _nested_frame(img, w, h, int(round(cq(.9))), cq(2), 4)
        _put(out, fr, (w / 2, h / 2), (cq(3) + w / 2, cq(10) + h / 2), s, 0, o)
    return out
