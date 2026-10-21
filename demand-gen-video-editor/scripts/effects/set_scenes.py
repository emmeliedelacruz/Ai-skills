"""Set 2 scene effects: B09 Zoom-through cut, B10 Chart grow, B11 Pull-back reveal, B12 Green screen.

Rebuilt from the CSS in video-effect-library.html (u9..u12). Units are cqw via core.cq().
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from .core import (EASE, EASE_OUT, H, W, bezier, clamp01, cq, drop_shadow, effect, ellipse, fit_cover, font,
                   gradient, keyframes, lerp, paste, place, rgba, rrect, seg, solid, text_layer, text_w, zoom)

# 1 preview px (the preview stage is ~195px wide) in output px; used only for CSS `blur(Npx)` values.
_PX = W / 195.0


# --------------------------------------------------------------------------- local helpers
def _lh(fnt):
    """CSS `line-height: normal` height of a PIL font."""
    a, d = fnt.getmetrics()
    return a + d


def _text(base, txt, fnt, x, y, fill=(255, 255, 255, 255), tracking=0.0, shadow=None, anchor="l", opacity=1.0):
    """Paste one line with its line box top at y. anchor l/m/r puts x at left/centre/right. Returns the text width."""
    pad = int(cq(1))
    extra = int(abs(shadow[0]) + abs(shadow[1]) + shadow[2] * 3) if shadow else 0
    lay = text_layer(txt, fnt, fill, tracking, pad=pad, shadow=shadow)
    tw = text_w(txt, fnt, tracking)
    left = x - (tw / 2 if anchor == "m" else tw if anchor == "r" else 0)
    paste(base, lay, (left - pad - extra, y - pad - extra), opacity)
    return tw


def _shadow_card(base, x, y, layer, offset, css_blur, color):
    """Paste an RGBA layer with a CSS box-shadow (offset px, blur radius px, RGBA colour) under it at (x, y)."""
    sig = css_blur / 2.0
    pad = int(sig * 3 + max(abs(offset[0]), abs(offset[1])))
    lay = drop_shadow(layer, blur=sig, offset=offset, color=color)
    paste(base, lay, (x - pad, y - pad))


def _hue_sat(img, hue_deg=0.0, sat=1.0):
    """CSS hue-rotate() then saturate()."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    c, s = math.cos(math.radians(hue_deg)), math.sin(math.radians(hue_deg))
    m = np.array([
        [.213 + c * .787 - s * .213, .715 - c * .715 - s * .715, .072 - c * .072 + s * .928],
        [.213 - c * .213 + s * .143, .715 + c * .285 + s * .140, .072 - c * .072 - s * .283],
        [.213 - c * .213 - s * .787, .715 - c * .715 + s * .715, .072 + c * .928 + s * .072]], np.float32)
    a = a @ m.T
    if sat != 1.0:
        g = (a * np.array([.2126, .7152, .0722], np.float32)).sum(-1, keepdims=True)
        a = g + (a - g) * sat
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def _fast_blur(img, sigma):
    """Gaussian blur that stays quick for huge sigma (blurs a downscaled copy)."""
    if sigma < 0.4:
        return img
    if sigma <= 10:
        return img.filter(ImageFilter.GaussianBlur(sigma))
    f = max(2, int(sigma / 5))
    small = img.resize((max(2, W // f), max(2, H // f)), Image.BOX)
    small = small.filter(ImageFilter.GaussianBlur(sigma / f))
    return small.resize(img.size, Image.BICUBIC)


def _scale_filters(img, brightness):
    if brightness >= 0.999:
        return img
    return img.point(lambda v: int(v * brightness)) if img.mode == "L" else \
        Image.fromarray((np.asarray(img, dtype=np.float32) * brightness).clip(0, 255).astype(np.uint8))


# --------------------------------------------------------------------------- B09
_ZZ = bezier(.6, 0, .9, .4)
_BZ = EASE


@effect("B09", "Zoom-through cut", duration=4.2, texts=["you can get the", "cool girl", "aesthetic"], outro_fade=0.25)
def zoom_through_cut(img, t, ctx):
    """Dive into a dark spot (30-46x zoom, blur, dim) then land on a mirrored, hue-shifted second shot.
    Text slots: 0 small lead-in line, 1 big serif italic word, 2 small tag line (stacked caption, gone by 1.9s)."""
    # second shot: mirrored, 1.12x, hue-rotate(18) saturate(.9); bz 3.0-4.0s eases from 1.45x + blur(5px)
    zb_src = ctx.cached("b09_zb", lambda: _hue_sat(ImageOps.mirror(img), 18, .9))
    bp = _BZ(seg(t, 3.0, 1.0))
    zb = zoom(zb_src, lerp(1.45, 1.12, bp))
    zb = _fast_blur(zb, lerp(5, 0, bp) * _PX)

    # first shot: zz 0.5s..3.1s, per-property keyframes at 0 / 92% / 100%
    T0, DUR = .5, 2.6
    k92 = T0 + DUR * .92
    if t < k92:
        p = _ZZ(seg(t, T0, k92 - T0))
        scale, blur_px, bright, op = 1 + 29 * p, 8 * p, 1 - .7 * p, 1.0
    else:
        p = _ZZ(seg(t, k92, T0 + DUR - k92))
        scale, blur_px, bright, op = lerp(30, 46, p), lerp(8, 12, p), lerp(.3, .1, p), 1 - p
    if op <= 0.002:
        out = zb.copy()
    else:
        za = zoom(img, scale, .48, .68)
        # filter acts in local space, then the transform scales it: screen blur = blur * scale
        za = _fast_blur(za, blur_px * scale * _PX if scale > 1.01 else blur_px * _PX)
        za = _scale_filters(za, bright)
        out = Image.blend(zb, za, op) if op < 0.999 else za

    # caption: rise .5s ease @.1s (opacity + translateY 3cqw), vanish .3s @1.6s
    a = EASE(seg(t, .1, .5)) * (1 - seg(t, 1.6, .3))
    if a > 0.002:
        dy = (1 - EASE(seg(t, .1, .5))) * cq(3)
        s1, s2, s3 = ctx.text(0, "you can get the"), ctx.text(1, "cool girl"), ctx.text(2, "aesthetic")
        f1, f2, f3 = font("sans", cq(3.6), 600), font("serif", cq(14), 400, italic=True), font("sans", cq(3), 500)
        sh1 = (0, 0, cq(1.5) / 2, (0, 0, 0, 136))
        sh2 = (0, 0, cq(2) / 2, (0, 0, 0, 136))
        y = cq(42) + dy
        _text(out, s1, f1, W / 2, y, (255, 255, 255, 255), shadow=sh1, anchor="m", opacity=a)
        y += _lh(f1)
        _text(out, s2, f2, W / 2, y + (cq(14) - _lh(f2)) / 2, (0xe8, 0xd2, 0x8a, 255), shadow=sh2, anchor="m", opacity=a)
        y += cq(14)
        _text(out, s3, f3, W / 2, y, (255, 255, 255, 204), anchor="m", opacity=a)
    return out


# --------------------------------------------------------------------------- B10
_PATH10 = [(8, 128), (30, 120), (44, 124), (62, 96), (82, 70), (90, 56)]
_POP = bezier(.2, 1.5, .4, 1)


def _chart_static(ctx):
    lay = rgba(W, H)
    d = ImageDraw.Draw(lay)
    for x in range(10, 95, 14):
        d.line((cq(x), cq(14), cq(x), cq(150)), fill=(255, 255, 255, 0x22), width=max(1, int(round(cq(.25)))))
    f = font("mono", cq(3), 500)
    for x, ch in zip(range(10, 95, 14), "MTWTFSS"):
        tw = text_w(ch, f)
        d.text((cq(x) - tw / 2, cq(12) - f.getmetrics()[0]), ch, font=f, fill=(255, 255, 255, 0xaa))
    return lay


def _partial_path(frac):
    pts = [(cq(x), cq(y)) for x, y in _PATH10]
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    goal = sum(segs) * frac
    out, acc = [pts[0]], 0.0
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if acc + L <= goal:
            out.append(b)
            acc += L
        else:
            r = (goal - acc) / L
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            break
    return out


@effect("B10", "Chart grow", duration=4.2, texts=["SCALE ↗"], outro_fade=0.25)
def chart_grow(img, t, ctx):
    """Footage punched in 1.8x and dimmed; a weekday grid and a glowing yellow line chart draw across, a tag pops on.
    Text slot 0: the tag on the chart (default 'SCALE ↗')."""
    out = zoom(img, 1.8, .46, .68)
    out = _scale_filters(out, .8)
    out = out.convert("RGBA")
    out.alpha_composite(ctx.cached("b10_static", lambda: _chart_static(ctx)))

    frac = EASE_OUT(seg(t, .5, 1.6))
    if frac > 0.002:
        pts = _partial_path(frac)
        ss, pad = 2, int(cq(5))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
        bw, bh = int(max(xs)) + pad - x0, int(max(ys)) + pad - y0
        big = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
        bd = ImageDraw.Draw(big)
        sp = [((x - x0) * ss, (y - y0) * ss) for x, y in pts]
        lw = cq(1.2) * ss
        col = (0xf5, 0xe6, 0x6a, 255)
        bd.line(sp, fill=col, width=int(lw), joint="curve")
        r = lw / 2
        for (x, y) in (sp[0], sp[-1]):
            bd.ellipse((x - r, y - r, x + r, y + r), fill=col)
        line = big.resize((bw, bh), Image.LANCZOS)
        glow = Image.new("RGBA", line.size, col[:3] + (0,))
        glow.putalpha(line.getchannel("A").filter(ImageFilter.GaussianBlur(cq(1.6) / 2)))
        out.alpha_composite(glow, (x0, y0))
        out.alpha_composite(line, (x0, y0))
    out = out.convert("RGB")

    # tag pops in at 1.8s (scale .4 -> 1 with overshoot)
    p = seg(t, 1.8, .3)
    if p > 0:
        e = _POP(p)
        f = font("sans", cq(3.4), 800)
        txt = ctx.text(0, "SCALE ↗")
        w, h = int(text_w(txt, f) + cq(5.2)), int(_lh(f) + cq(2.4))
        tag = rrect((w, h), min(cq(3), h / 2), (0xf5, 0xe6, 0x6a, 255))
        tl = text_layer(txt, f, (0x11, 0x11, 0x11, 255), pad=0)
        paste(tag, tl, (cq(2.6), cq(1.2)))
        place(out, tag, cq(44) + w / 2, cq(30) + h / 2, scale=max(.01, lerp(.4, 1, e)), opacity=clamp01(e))
    return out


# --------------------------------------------------------------------------- B11
_PBK = bezier(.6, 0, .2, 1)
_ITEMS11 = ["Transcribed 1 clip", "Picked the take", "Cut 3 shots", "Captions added", "Rendered 150 frames"]
_K = 2  # base scene is drawn at 2x so the 2x start of the pull-back stays sharp


def _u(v):
    return cq(v) * _K


def _scene11_base():
    base = Image.new("RGB", (W * _K, H * _K), (0xef, 0xec, 0xe2))
    dot = ellipse((int(_u(2)), int(_u(2))), (0xcf, 0xc9, 0xba, 255))
    for i in range(3):
        base.paste(dot.convert("RGB"), (int(_u(4 + i * 3.2)), int(_u(5))), dot.getchannel("A"))
    fa = font("sans", _u(2.4), 600)
    _text(base, "Assistant", fa, _u(96) - text_w("Assistant", fa), _u(4.6), (0x6b, 0x66, 0x5a, 255))
    # video box shadow (box-shadow 0 1cqw 3cqw #0003); the footage itself is pasted per frame
    box = rrect((int(_u(50)), int(_u(89))), _u(1.5), (0, 0, 0, 255))
    _shadow_card(base, int(_u(44)), int(_u(26)), box, (0, int(_u(1))), _u(3), (0, 0, 0, 0x33))
    # timeline card
    tl = rrect((int(_u(90)), int(_u(12))), _u(1.4), (255, 255, 255, 255))
    stripes = rgba(int(_u(84)), int(_u(6)))
    sd = ImageDraw.Draw(stripes)
    x = 0.0
    while x < 84:
        sd.rectangle((_u(x), 0, _u(min(x + 1, 84)), stripes.height), fill=(0x3f, 0x6f, 0xf0, int(255 * .85)))
        x += 1.6
    stripes.putalpha(ImageChops_multiply(stripes.getchannel("A"), rrect(stripes.size, _u(.6)).getchannel("A")))
    paste(tl, stripes, (_u(3), _u(3)))
    _shadow_card(base, int(_u(4)), int(_u(124)), tl, (0, int(_u(.6))), _u(2), (0, 0, 0, 0x22))
    return base


def ImageChops_multiply(a, b):
    return Image.fromarray((np.asarray(a, np.float32) * np.asarray(b, np.float32) / 255).astype(np.uint8))


def _checklist11(done, items):
    """Checklist card at 2x with `done` items ticked."""
    w, h = int(_u(36)), int(_u(2 + 2.42 + 2 + 4.2 * 5 + 2 - 1.8 + 1.8))
    card = rrect((w, h), _u(1.6), (255, 255, 255, 255))
    ink = (0x2a, 0x26, 0x22, 255)
    fh = font("sans", _u(2), 600)
    y = _u(2)
    x = _u(2)
    x += _text(card, "● Working on", fh, x, y + (_u(2.42) - _lh(fh)) / 2, ink) + _u(1)
    fb = font("sans", _u(1.4), 600)
    bw, bh = int(text_w("NOW", fb) + _u(1.6)), int(_lh(fb) + _u(.6))
    badge = rrect((bw, bh), _u(.6), (0x3f, 0x6f, 0xf0, 255))
    paste(badge, text_layer("NOW", fb, (255, 255, 255, 255), pad=0), (_u(.8), _u(.3)))
    paste(card, badge, (x, y + (_u(2.42) - bh) / 2))
    y += _u(2.42 + 2)
    fi = font("sans", _u(2.2), 600)
    for i, txt in enumerate(items):
        on = i < done
        d = int(_u(2.4))
        circ = ellipse((d, d), (0x3c, 0xae, 0x6a, 255) if on else (255, 255, 255, 255),
                       (0x3c, 0xae, 0x6a, 255) if on else (0xc9, 0xc4, 0xb6, 255), int(_u(.3)))
        paste(card, circ, (_u(2), y))
        _text(card, txt, fi, _u(2 + 2.4 + 1.2), y + (_u(2.4) - _lh(fi)) / 2, ink if on else (0x9b, 0x96, 0x89, 255))
        y += _u(2.4 + 1.8)
    return card


@effect("B11", "Pull-back reveal", duration=5.0,
        texts=["a skill with", "Transcribed 1 clip", "Picked the take", "Cut 3 shots", "Captions added", "Rendered 150 frames"],
        outro_fade=0.25)
def pull_back_reveal(img, t, ctx):
    """The footage starts zoomed 2x inside an editor window, pulls back to reveal the app: Assistant checklist ticking
    off steps (from 2.5s) and a render timeline. Text slots: 0 caption on the video, 1-5 the five checklist steps."""
    base = ctx.cached("b11_base", _scene11_base).copy()
    done = sum(1 for i in range(5) if t >= 2.5 + i * .3)
    items = [ctx.text(i + 1, _ITEMS11[i]) for i in range(5)]
    card = ctx.cached(("b11_card", done, tuple(items)), lambda: _checklist11(done, items))
    _shadow_card(base, int(_u(4)), int(_u(44)), card, (0, int(_u(.6))), _u(2), (0, 0, 0, 0x33))

    bw, bh = int(_u(50)), int(_u(89))
    vid = fit_cover(img, bw, bh).convert("RGBA")
    f = font("sans", _u(4.4), 800)
    cap = ctx.text(0, "a skill with")
    _text(vid, cap, f, bw / 2, bh - _u(10) - _lh(f), (255, 255, 255, 255), shadow=(0, 0, _u(1.4) / 2, (0, 0, 0, 0xaa)),
          anchor="m")
    mask = ctx.cached("b11_vmask", lambda: rrect((bw, bh), _u(1.5)).getchannel("A"))
    base.paste(vid.convert("RGB"), (int(_u(44)), int(_u(26))), mask)

    # pbx: scale 2 -> 1 about (69cqw, 70.5cqw), .6s..2.4s
    s = lerp(2, 1, _PBK(seg(t, .6, 1.8)))
    ox, oy = cq(69), cq(70.5)
    x0, y0 = ox * (1 - 1 / s), oy * (1 - 1 / s)
    x1, y1 = ox + (W - ox) / s, oy + (H - oy) / s
    return base.resize((W, H), Image.LANCZOS, box=(x0 * _K, y0 * _K, x1 * _K, y1 * _K))


# --------------------------------------------------------------------------- B12
_GKW = bezier(.6, 0, .3, 1)


def _burst(size, color):
    """Eight-spoke star used for the preview's '✺' glyph."""
    ss = 4
    d = int(size * ss)
    lay = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    c = d / 2
    for k in range(8):
        a = math.pi * k / 4
        x, y = math.cos(a) * d * .46, math.sin(a) * d * .46
        dr.line((c, c, c + x, c + y), fill=color, width=max(2, int(d * .13)))
        r = d * .065
        dr.ellipse((c + x - r, c + y - r, c + x + r, c + y + r), fill=color)
    dr.ellipse((c - d * .13, c - d * .13, c + d * .13, c + d * .13), fill=color)
    return lay.resize((int(size), int(size)), Image.LANCZOS)


def _scene12():
    """Purple gradient backdrop + the Claude-style focus-timer card."""
    bg = gradient((W, H), (0x7a, 0x49, 0xf5), (0x2b, 0x2f, 0xd1), 180).convert("RGB")
    ink = (0x2a, 0x26, 0x22, 255)
    fs = lambda size, w=600: font("sans", cq(size), w)
    pad = cq(2.6)
    cx0, cy0, cw = cq(5), cq(7), cq(90)
    # --- measure
    f_tm, f_sp, f_u = font("mono", cq(4.4), 700), fs(2.4), fs(2, 700)
    h_tm = _lh(f_tm) + cq(3.2)
    f_itm = fs(2.4)
    h_itm = _lh(f_itm) + cq(3.2)
    f_h4 = font("serif", cq(7.6), 400)
    f_in = fs(2.6, 500)
    h_in = max(_lh(f_in), cq(5)) + cq(4)
    y = pad  # inside the card
    y_tb = y
    y += cq(1.8) + cq(2)
    y_tm = y
    y += h_tm + cq(1.4)
    y_i1 = y
    y += h_itm + cq(1.4)
    y_i2 = y
    y += h_itm + cq(3)
    y_h4 = y
    y += cq(7.6) + cq(2)
    y_in = y
    y += h_in + pad
    ch = int(y)
    card = rrect((int(cw), ch), cq(2), (0xf7, 0xf4, 0xec, 255))
    for i in range(3):
        d = int(cq(1.8))
        paste(card, ellipse((d, d), (0xd8, 0xd2, 0xc2, 255)), (pad + i * (cq(1.8) + cq(1.2)), y_tb))
    # timer bar
    tw_ = int(cw - pad * 2)
    tm = rrect((tw_, int(h_tm)), cq(1.4), (0x1f, 0x1d, 0x1a, 255))
    x = cq(2)
    x += _text(tm, "49:57", f_tm, x, (h_tm - _lh(f_tm)) / 2, (255, 255, 255, 255)) + cq(2)
    _text(tm, "Write the sales page", f_sp, x, (h_tm - _lh(f_sp)) / 2, (0xd9, 0xd3, 0xc4, 255))
    ub = rrect((int(text_w("End sprint", f_u) + cq(2.8)), int(_lh(f_u) + cq(1.6))), cq(1), (0xe0, 0x40, 0x5a, 255))
    paste(ub, text_layer("End sprint", f_u, (255, 255, 255, 255), pad=0), (cq(1.4), cq(.8)))
    paste(tm, ub, (tw_ - cq(2) - ub.width, (h_tm - ub.height) / 2))
    paste(card, tm, (pad, y_tm))
    for yy, txt in ((y_i1, "Record 2 reels"), (y_i2, "Send the newsletter")):
        it = rrect((tw_, int(h_itm)), cq(1.2), (0xef, 0xea, 0xdd, 255))
        _text(it, txt, f_itm, cq(2), (h_itm - _lh(f_itm)) / 2, (0x6a, 0x64, 0x58, 255))
        paste(card, it, (pad, yy))
    # h4: star + headline, centred, line-height 1
    h4 = "Everything else waits."
    star = int(cq(5))
    total = star + cq(1) + text_w(h4, f_h4)
    x = (cw - total) / 2
    a, d = f_h4.getmetrics()
    base_y = y_h4 + (cq(7.6) - (a + d)) / 2 + a
    paste(card, _burst(star, (0xd9, 0x63, 0x3b, 255)), (x, base_y - cq(2.6) - star / 2))
    _text(card, h4, f_h4, x + star + cq(1), base_y - a, ink)
    # input
    inp = rrect((tw_, int(h_in)), cq(2), (255, 255, 255, 255))
    _text(inp, "What should I work on?", f_in, cq(2.4), (h_in - _lh(f_in)) / 2, (0x9b, 0x96, 0x89, 255))
    b = int(cq(5))
    paste(inp, ellipse((b, b), (0xd9, 0x63, 0x3b, 255)), (tw_ - cq(2.4) - b, (h_in - b) / 2))
    _shadow_card(card, int(pad), int(y_in), inp, (0, int(cq(.4))), cq(1.6), (0, 0, 0, 0x22))
    _shadow_card(bg, int(cx0), int(cy0), card, (0, int(cq(1.4))), cq(5), (0, 0, 0, 0x55))
    return bg


@effect("B12", "Green screen", duration=4.4, texts=["you need", "edits"], needs_mask=True, outro_fade=0.25)
def green_screen(img, t, ctx):
    """Speaker stands in front of a green backdrop that wipes upward (1.0-1.9s) to reveal an app UI; a caption pill
    rises in at 1.8s. Needs the subject matte. Text slots: 0 pill text, 1 highlighted (yellow) word."""
    out = ctx.cached("b12_scene", _scene12).copy()
    gp = _GKW(seg(t, 1.0, .9))
    gh = int(round(H * (1 - gp)))
    if gh > 0:
        out.paste(Image.new("RGB", (W, gh), (0x12, 0xc2, 0x5a)), (0, 0))

    # person cut-out: scale(1.35) about bottom centre
    person = zoom(img, 1.35, .5, 1.0)
    pm = zoom(ctx.mask(), 1.35, .5, 1.0)
    out.paste(person, (0, 0), pm)

    # caption pill: rise .3s ease @1.8s (centred; the preview's translateX(-50%) is overridden by its keyframe)
    p = EASE(seg(t, 1.8, .3))
    if p > 0.002:
        f = font("sans", cq(4.6), 800)
        s0, s1 = ctx.text(0, "you need"), ctx.text(1, "edits")
        w0 = text_w(s0 + " ", f)
        w = int(w0 + text_w(s1, f) + cq(4.8))
        h = int(_lh(f) + cq(2.4))
        pill = rrect((w, h), cq(2), (0x11, 0x11, 0x11, 255))
        _text(pill, s0, f, cq(2.4), cq(1.2), (255, 255, 255, 255))
        _text(pill, s1, f, cq(2.4) + w0, cq(1.2), (0xf5, 0xe6, 0x6a, 255))
        paste(out, pill, (W / 2 - w / 2, cq(100) + (1 - p) * cq(3)), p)
    return out
