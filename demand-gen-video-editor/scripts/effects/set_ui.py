"""Set 2, UI group: B03 UI world, B04 Frame break, B05 Digital zoom, B06 Phone mockup, B07 Checklist,
B08 Headline wall. Rebuilt from the preview CSS in video-effect-library.html (units are cqw via cq())."""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .core import (EASE, EASE_OUT, H, W, bezier, clamp01, cq, drop_shadow, effect, ellipse, font, fit_cover, keyframes,
                   lerp, paste, place, rgba, rrect, round_clip, seg, solid, text_layer, text_w, warp_quad, zoom,
                   with_opacity, adjust, blur, css_filter, SPRING)

WHITE = (255, 255, 255, 255)
YELLOW = (0xf5, 0xe6, 0x6a, 255)


# --------------------------------------------------------------------------- local helpers
def _hex(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _text(base, txt, fnt, x, y, *, line_h=None, align="left", fill=WHITE, tracking=0.0, opacity=1.0, shadow=None):
    """Draw one CSS-like line: (x, y) = left/centre/right edge and top of the line box (line_h = CSS line-height)."""
    if not txt or opacity <= 0.001:
        return
    lay = text_layer(txt, fnt, fill, tracking, shadow=shadow, pad=2)
    asc, desc = fnt.getmetrics()
    tw = math.ceil(text_w(txt, fnt, tracking))
    ox = (lay.width - tw) / 2
    oy = (lay.height - (asc + desc)) / 2
    lh = line_h or (asc + desc)
    ytop = y + (lh - (asc + desc)) / 2
    px = x if align == "left" else x - tw / 2 if align == "center" else x - tw
    paste(base, lay, (px - ox, ytop - oy), opacity)


def _lh(fnt, factor=None):
    asc, desc = fnt.getmetrics()
    return fnt.size * factor if factor else asc + desc


def _glow(blur_cq):
    """CSS text-shadow '0 0 Xcqw #000a' -> text_layer shadow tuple (sigma = radius / 2)."""
    return (0, 0, cq(blur_cq) / 2, (0, 0, 0, 170))


def _subject_box(ctx):
    """Subject bbox (x0, y0, x1, y1) in px from the matte (stand-in matte if none supplied). Cached on first call."""
    def f():
        m = np.asarray(ctx.mask()) > 127
        rows, cols = np.where(m.any(1))[0], np.where(m.any(0))[0]
        if len(rows) == 0:
            return (W * .2, H * .2, W * .8, H)
        return (cols[0], rows[0], cols[-1], rows[-1])
    return ctx.cached("subject_box", f)


def _crop_clip(img, ctx, k, w_cq, h_cq, radius_cq, border_cq=0.0, shadow=False):
    """A 'clip thumbnail' cut from the current frame around the subject; k varies the crop. RGBA layer."""
    x0, y0, x1, y1 = _subject_box(ctx)
    sh = (y1 - y0)
    var = [(1.0, 0), (.85, .06), (1.15, -.03), (.9, .1), (1.05, .02)][k % 5]
    ch = max(60, sh * .5 * var[0])
    cw = ch * w_cq / h_cq
    cx = (x0 + x1) / 2
    top = y0 - .05 * sh + var[1] * sh
    box = (int(cx - cw / 2), int(top), int(cx + cw / 2), int(top + ch))
    pw, ph = int(cq(w_cq)), int(cq(h_cq))
    tile = img.crop(box).resize((pw, ph), Image.BICUBIC)
    if k % 2:
        tile = css_filter(tile, brightness=.92, saturate=.8, contrast=1.05)
    bw = int(round(cq(border_cq)))
    if bw:
        lay = rrect((pw, ph), cq(radius_cq), WHITE)
        inner = round_clip(tile.resize((pw - bw * 2, ph - bw * 2), Image.BICUBIC), max(0, cq(radius_cq) - bw))
        lay.alpha_composite(inner, (bw, bw))
    else:
        lay = round_clip(tile, cq(radius_cq))
    return lay


def _dashed_rrect(size, radius, color, width, dash, gap, fill=None):
    """Dashed rounded-rect outline (CSS `border: Npx dashed`), RGBA, supersampled 3x."""
    ss = 3
    w, h = int(size[0]) * ss, int(size[1]) * ss
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r, wd = radius * ss, width * ss
    if fill:
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=fill)
    inset = wd / 2
    x0, y0, x1, y1 = inset, inset, w - 1 - inset, h - 1 - inset
    r2 = r - inset
    pts = []
    n = 24
    for cx, cy, a0 in ((x1 - r2, y0 + r2, -90), (x1 - r2, y1 - r2, 0), (x0 + r2, y1 - r2, 90), (x0 + r2, y0 + r2, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r2 * math.cos(a), cy + r2 * math.sin(a)))
    pts.append(pts[0])
    run, on = 0.0, True
    seg_pts = [pts[0]]
    dl, gl = dash * ss, gap * ss
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        pos = 0.0
        while pos < L:
            lim = (dl if on else gl) - run
            step = min(lim, L - pos)
            p0 = (a[0] + (b[0] - a[0]) * pos / L, a[1] + (b[1] - a[1]) * pos / L)
            p1 = (a[0] + (b[0] - a[0]) * (pos + step) / L, a[1] + (b[1] - a[1]) * (pos + step) / L)
            if on:
                d.line([p0, p1], fill=color, width=int(wd))
            pos += step
            run += step
            if run >= (dl if on else gl) - 1e-6:
                on, run = not on, 0.0
    return lay.resize((w // ss, h // ss), Image.LANCZOS)


def _star(d_px, color, rays=8):
    """Simple 'sparkle' burst used as the Claude mark: `rays` thick spokes."""
    ss = 4
    s = int(d_px) * ss
    lay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    c = s / 2
    for i in range(rays):
        a = math.pi * i / rays * 2
        dx, dy = math.cos(a) * c * .94, math.sin(a) * c * .94
        dr.line([(c, c), (c + dx, c + dy)], fill=color, width=max(2, int(s * .13)))
    dr.ellipse((c - s * .11, c - s * .11, c + s * .11, c + s * .11), fill=color)
    return lay.resize((int(d_px), int(d_px)), Image.LANCZOS)


def _check(d_px, color, width_px):
    ss = 4
    s = int(d_px) * ss
    lay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    pts = [(s * .22, s * .52), (s * .43, s * .72), (s * .78, s * .30)]
    dr.line(pts, fill=color, width=int(width_px * ss), joint="curve")
    for p in (pts[0], pts[2]):
        r = width_px * ss / 2
        dr.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)
    return lay.resize((int(d_px), int(d_px)), Image.LANCZOS)


def _rise(t, t0, dur=.3):
    """CSS rise keyframe: opacity 0->1 and translateY(3cqw)->0, ease. Returns (opacity, dy_px)."""
    p = EASE(seg(t, t0, dur))
    return p, (1 - p) * cq(3)


# =========================================================================== B03 UI world
@effect("B03", "UI world", duration=4.4,
        texts=["Claude", "Drop files here", "DROP CLIPS", "TRIGGER THE", "RAW CLIPS", "How can I help you today?", "/video-"])
def ui_world(img, t, ctx):
    """App UI fills the top 55% and the footage drops to the lower part; clips fall into a drop zone, then a prompt box
    types a command. Slots: 0 app name, 1 drop-zone hint, 2 first caption, 3 second caption (words after the first are
    dimmed), 4 tag on the prompt box, 5 placeholder, 6 typed command. Uses the subject matte (if any) to keep the head
    below the UI."""
    ui_h = int(cq(98))
    # footage underneath: shift down so the head clears the UI panel
    x0, y0, x1, y1 = _subject_box(ctx)
    oy = int(max(0, min(ui_h, ui_h + cq(18) - y0)))
    out = Image.new("RGB", (W, H), (20, 18, 16))
    out.paste(img, (0, oy))
    out = out.convert("RGBA")

    def static_ui():
        ui = solid(_hex("#f6f2e8"), (W, ui_h))
        # logo line
        f = font("serif", cq(5), 400)
        name = ctx.text(0, "Claude")
        tw = text_w(name, f)
        star_d = cq(4.4)
        total = star_d + cq(1) + tw
        xs = (W - total) / 2
        top = cq(10)
        paste(ui, _star(star_d, _hex("#d9633b")), (xs, top + (_lh(f) - star_d) / 2))
        _text(ui, name, f, xs + star_d + cq(1), top, fill=_hex("#2a2622"))
        return ui

    ui = ctx.cached("b03_ui", static_ui).copy()

    # ---- group A (drop zone + falling clips), vanishes at 1.1s
    a_op = 1 - EASE(seg(t, 1.1, .3))
    if a_op > .002:
        def dz():
            lay = _dashed_rrect((W - cq(10), cq(42)), cq(3), _hex("#c9c0ac"), cq(.4), cq(1.4), cq(1), fill=_hex("#fbf9f3"))
            f = font("sans", cq(3), 500)
            _text(lay, ctx.text(1, "Drop files here"), f, lay.width / 2, lay.height - cq(4) - _lh(f), align="center",
                  fill=_hex("#9b9282"))
            return lay
        ga = rgba(W, ui_h)
        paste(ga, ctx.cached("b03_dz", dz), (cq(5), cq(22)))
        for k, (left, dl, rot) in enumerate(((24, .1, -12), (40, .35, 8), (56, .6, -6))):
            lt = t - dl
            if lt <= 0:
                continue
            if lt < .48:
                p = bezier(.55, 0, 1, .45)(lt / .48)
                y, r = -50 * (1 - p), rot * (1 - p)
            elif lt < .624:
                y, r = -2 * EASE_OUT((lt - .48) / .144), 0
            else:
                y, r = -2 * (1 - clamp01((lt - .624) / .176)), 0
            th = _crop_clip(img, ctx, k, 11, 15, 1.2, .3)
            th = drop_shadow(th, cq(.8), (0, int(cq(.6))), (0, 0, 0, 68))
            place(ga, th, cq(left + 5.5), cq(34 + 7.5 + y), rot=r)
        paste(ui, ga, (0, 0), a_op)

    # ---- group B (prompt box), fades in at 1.1s
    b_op = EASE(seg(t, 1.1, .4))
    if b_op > .002:
        gb = rgba(W, ui_h)
        inp_w, inp_h = W - cq(10), cq(44)

        def box():
            lay = rrect((inp_w, inp_h), cq(3), WHITE)
            return drop_shadow(lay, cq(2), (0, int(cq(1))), (0, 0, 0, 34))
        sh = ctx.cached("b03_box", box)
        pad = (sh.width - int(inp_w)) // 2
        paste(gb, sh, (cq(5) - pad, cq(24) - pad))
        ix, iy = cq(5), cq(24)
        for k in range(5):
            th = _crop_clip(img, ctx, k, 9, 13, 1)
            paste(gb, th, (ix + cq(3) + k * cq(10.4), iy + cq(3)))
        # tag
        tf = font("sans", cq(2.2), 800)
        tag_txt = ctx.text(4, "RAW CLIPS")
        tw = text_w(tag_txt, tf)
        tg = rgba(tw + cq(2.4), _lh(tf) + cq(1.2), YELLOW)
        _text(tg, tag_txt, tf, cq(1.2), cq(.6), fill=_hex("#222222"))
        place(gb, tg, ix + inp_w - cq(4) - tg.width / 2, iy + cq(12) + tg.height / 2, rot=-2)
        # placeholder / typed text
        pf = font("sans", cq(3), 500)
        if t < 2.3:
            _text(gb, ctx.text(5, "How can I help you today?"), pf, ix + cq(3), iy + inp_h - cq(5) - _lh(pf), fill=_hex("#9b9282"))
        mf = font("mono", cq(3.2), 600)
        cmd = ctx.text(6, "/video-")
        full = cq(16)
        p = clamp01((t - 2.3) / .8)
        vis = math.floor(p * 7) / 7 if p < 1 else 1.0
        wv = int(full * vis)
        mh = _lh(mf)
        by = iy + inp_h - cq(5) - mh
        if wv > 0:
            tl = text_layer(cmd, mf, _hex("#2a2622"), pad=0)
            paste(gb, tl.crop((0, 0, min(wv, tl.width), tl.height)), (ix + cq(3), by))
        cw = max(2, int(cq(.35)))
        ImageDraw.Draw(gb).rectangle((ix + cq(3) + wv, by, ix + cq(3) + wv + cw - 1, by + mh), fill=_hex("#2a2622"))
        paste(ui, gb, (0, 0), b_op)

    out.alpha_composite(ui, (0, 0))
    out = out.convert("RGB")

    # ---- captions (outside the UI), top 108cqw
    cf = font("sans", cq(4.4), 800)
    tr = .04 * cq(4.4)
    y = cq(108)
    if 1.3 <= t < 2.4:
        _text(out, ctx.text(2, "DROP CLIPS"), cf, W / 2, y, align="center", tracking=tr, shadow=_glow(1.6))
    if t >= 2.4:
        words = ctx.text(3, "TRIGGER THE").split(" ", 1)
        w0 = text_w(words[0], cf, tr)
        w1 = text_w(" " + words[1], cf, tr) if len(words) > 1 else 0
        x = W / 2 - (w0 + w1) / 2
        _text(out, words[0], cf, x, y, tracking=tr, shadow=_glow(1.6))
        if len(words) > 1:
            _text(out, " " + words[1], cf, x + w0, y, tracking=tr, opacity=.55, shadow=_glow(1.6))
    return out


# =========================================================================== B04 Frame break
def _radial_bg():
    """radial-gradient(ellipse at 50% 45%, #2c302a, #0a0b09), farthest-corner."""
    ys, xs = np.mgrid[0:H, 0:W]
    rx, ry = W / 2 * math.sqrt(2), .55 * H * math.sqrt(2)
    d = np.clip(np.hypot((xs - W * .5) / rx, (ys - H * .45) / ry), 0, 1)[..., None]
    a, b = np.array([0x2c, 0x30, 0x2a], float), np.array([0x0a, 0x0b, 0x09], float)
    return Image.fromarray((a * (1 - d) + b * d).astype(np.uint8))


@effect("B04", "Frame break", duration=3.6, outro_fade=0)
def frame_break(img, t, ctx):
    """Footage sits in a small rounded social frame on a dark backdrop, then the frame scales up and its corners
    square off until it fills the screen. No text slots."""
    out = ctx.cached("b04_bg", _radial_bg).copy()
    s = keyframes(t, [(0, .9), (.39, 1), (1.17, 1), (2.21, 1.62), (2.6, 1.62)], bezier(.7, 0, .2, 1))
    op = keyframes(t, [(0, 0), (.39, 1)], bezier(.7, 0, .2, 1))
    pr = bezier(.7, 0, .2, 1)(seg(t, 0, 2.21))      # radius / border shrink over 0..85%
    radius, bw = cq(5) * (1 - pr), cq(.5) * (1 - pr)
    if op <= 0.001:
        return out
    bwd, bhd = int(round(cq(62) * s)), int(round(cq(110) * s))
    R, B = radius * s, bw * s
    box = rrect((bwd, bhd), max(R, 0.01), (68, 68, 68, 255))
    iw, ih = bwd - int(round(2 * B)), bhd - int(round(2 * B))
    inner = fit_cover(img, iw, ih)
    # overlay icons / name bar (vanish at 1.0s over .3s)
    ic = 1 - EASE(seg(t, 1.0, .3))
    if ic > .002:
        ov = rgba(iw, ih)
        od = ImageDraw.Draw(ov)
        d = cq(4.4) * s
        for i in range(3):
            cy = ih - cq(12) * s - d * (3 - i) - cq(2) * s * (2 - i)
            cx = iw - cq(2) * s - d
            ring = ellipse((int(d), int(d)), (0, 0, 0, 0), WHITE, max(1, int(cq(.5) * s)))
            ov.alpha_composite(ring, (int(cx), int(cy)))
        bar = rrect((int(cq(22) * s), int(cq(2.6) * s)), cq(1) * s, (255, 255, 255, 0x66))
        ov.alpha_composite(bar, (int(cq(3) * s), int(ih - cq(3) * s - bar.height)))
        inner = inner.convert("RGBA")
        inner.alpha_composite(with_opacity(ov, ic))
    inner = round_clip(inner.convert("RGB"), max(0.01, R - B))
    box.alpha_composite(inner, (int(round(B)), int(round(B))))
    paste(out, box, (W / 2 - bwd / 2, H / 2 - bhd / 2), op)
    return out


# =========================================================================== B05 Digital zoom
@effect("B05", "Digital zoom", duration=4.2, texts=["or know anything about", "video", "editing"])
def digital_zoom(img, t, ctx):
    """Fast punch-in (1.0 -> 1.7x about 50%/55%) with a blur kick, caption stacks in. Slots: 0 small lead-in line,
    1 first big word, 2 second big word (yellow)."""
    lt = t - .5
    sc = lerp(1, 1.7, bezier(.15, .9, .25, 1)(clamp01(lt / 1.8)))
    fb = bezier(.15, .9, .25, 1)
    if lt <= 0:
        sg = 0
    elif lt < .18:
        sg = 2 * fb(lt / .18)
    elif lt < .63:
        sg = 2 * (1 - fb((lt - .18) / .45))
    else:
        sg = 0
    out = zoom(img, sc, .5, .55)
    if sg > .05:
        out = blur(out, sg * W / 400)
    out = out.convert("RGB")

    small, big = font("sans", cq(4), 700), font("sans", cq(12), 800)
    y = cq(92)
    lh_s, lh_b = _lh(small), cq(12)
    op, dy = _rise(t, .2)
    _text(out, ctx.text(0, "or know anything about"), small, W / 2, y + dy, align="center", opacity=op, shadow=_glow(1.5))
    op, dy = _rise(t, 1.1)
    _text(out, ctx.text(1, "video"), big, W / 2, y + lh_s + dy, line_h=lh_b, align="center", opacity=op,
          tracking=-.02 * cq(12), shadow=_glow(2))
    op, dy = _rise(t, 1.8)
    _text(out, ctx.text(2, "editing"), big, W / 2, y + lh_s + lh_b + dy, line_h=lh_b, align="center", opacity=op,
          tracking=-.02 * cq(12), fill=YELLOW, shadow=_glow(2))
    return out


# =========================================================================== B06 Phone mockup
_PS = 1.5   # supersample factor for the flat phone before the perspective warp


def _phone_layer(ctx):
    def build():
        q = lambda v: cq(v) * _PS  # noqa: E731
        pw, ph = int(q(38)), int(q(78))
        lay = rrect((pw, ph), q(7), _hex("#2a2b2e"))                      # border colour 1cqw
        b = int(q(1))
        body = rrect((pw - 2 * b, ph - 2 * b), q(6), _hex("#0d0d0f"))
        ring = rrect((pw - 2 * b, ph - 2 * b), q(6), (0, 0, 0, 0), _hex("#555555"), max(1, int(q(.3))))
        body.alpha_composite(ring)
        lay.alpha_composite(body, (b, b))
        # screen: inset 1.2cqw inside the padding box
        so = b + int(q(1.2))
        sw, sh = pw - 2 * so, ph - 2 * so
        scr = rrect((sw, sh), q(5.6), _hex("#18191b"))
        f_hd = font("sans", q(2.2), 600)
        px = q(2.6)
        y = q(6)
        dot = int(q(3.4))
        scr.alpha_composite(ellipse((dot, dot), _hex("#e9d45a")), (int(px), int(y)))
        _text(scr, ctx.text(2, "Ads Assistant"), f_hd, px + dot + q(1.4), y + (dot - _lh(f_hd)) / 2, fill=_hex("#c9c9c9"))
        y += max(dot, _lh(f_hd)) + q(2)
        # message bubble
        f_s, f_b = font("sans", q(2), 500), font("sans", q(2.7), 600)
        inner_w = sw - 2 * px - 2 * q(2)
        lines = _wrap(ctx.text(4, "Pause Ad 3, move the budget to Ad 1"), f_b, inner_w)
        lb = q(2.7) * 1.25
        bh = q(2) * 2 + _lh(f_s) + q(1) + lb * len(lines)
        bub = rrect((int(sw - 2 * px), int(bh)), q(2), _hex("#26282b"))
        _text(bub, ctx.text(3, "Needs approval"), f_s, q(2), q(2), fill=_hex("#9a9a9a"))
        for i, ln in enumerate(lines):
            _text(bub, ln, f_b, q(2), q(2) + _lh(f_s) + q(1) + i * lb, line_h=lb)
        scr.alpha_composite(bub, (int(px), int(y)))
        y += bh + q(2)
        f_bt = font("sans", q(2.6), 700)
        bt = rrect((int(sw - 2 * px), int(_lh(f_bt) + q(2.8))), q(2), WHITE)
        _text(bt, ctx.text(5, "Approve"), f_bt, bt.width / 2, q(1.4), align="center", fill=_hex("#111111"))
        scr.alpha_composite(bt, (int(px), int(y)))
        lay.alpha_composite(scr, (so, so))
        return lay
    return ctx.cached("b06_phone", build)


def _wrap(txt, fnt, max_w):
    lines, cur = [], ""
    for w in txt.split():
        trial = (cur + " " + w).strip()
        if text_w(trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def _project(pts, cx, cy, ry_deg, rx_deg, d):
    ay, ax = math.radians(ry_deg), math.radians(rx_deg)
    out = []
    for x, y in pts:
        y1, z1 = y * math.cos(ax), y * math.sin(ax)
        x2, z2 = x * math.cos(ay) + z1 * math.sin(ay), -x * math.sin(ay) + z1 * math.cos(ay)
        w = 1 - z2 / d
        out.append((cx + x2 / w, cy + y1 / w))
    return out


@effect("B06", "Phone mockup", duration=4.4,
        texts=["all you", "need to", "Ads Assistant", "Needs approval", "Pause Ad 3, move the budget to Ad 1", "Approve"])
def phone_mockup(img, t, ctx):
    """Footage punched in 1.75x while a 3D-tilted phone with an approval notification slides in from the right and
    floats; two caption chunks rise in. Slots: 0-1 caption chunks, 2 app name, 3 notification label, 4 message,
    5 button."""
    out = zoom(img, 1.75, .38, .66).convert("RGBA")
    slide = (1 - bezier(.2, .8, .2, 1)(seg(t, .4, .9))) * cq(70)
    flt = 0.0
    if t > 1.3:
        ph_ = ((t - 1.3) / 2) % 2
        flt = -cq(2) * EASE_IN_OUT_alt(ph_ if ph_ <= 1 else 2 - ph_)
    cx, cy = cq(85), cq(34 + 39) + flt   # right:-4cqw, top:34cqw, 38x78cqw
    pw, ph = cq(38), cq(78)
    corners = [(-pw / 2, -ph / 2), (pw / 2, -ph / 2), (pw / 2, ph / 2), (-pw / 2, ph / 2)]
    dst = _project(corners, cx + slide, cy, -22, 4, cq(120))
    warped = warp_quad(_phone_layer(ctx), dst)
    # box-shadow 0 2cqw 6cqw #0009
    if slide < W:
        a = warped.getchannel("A")
        sh_a = ImageChops.offset(a, 0, int(cq(2))).filter(ImageFilter.GaussianBlur(cq(3))).point(lambda v: int(v * .6))
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.putalpha(sh_a)
        out.alpha_composite(sh)
        out.alpha_composite(warped)
    out = out.convert("RGB")
    # captions: inline spans at left 3cqw top 130cqw, 800 4.6cqw
    cf = font("sans", cq(4.6), 800)
    x = cq(3)
    for i in range(6):
        chunk = ctx.text(i, "") if i < 2 else ""
        if not chunk:
            continue
        op, dy = _rise(t, .3 + .7 * i)
        _text(out, chunk, cf, x, cq(130) + dy, opacity=op, shadow=_glow(1.6))
        x += text_w(chunk + " ", cf)
    return out


def EASE_IN_OUT_alt(p):
    return bezier(.42, 0, .58, 1)(p)


# =========================================================================== B07 Checklist
@effect("B07", "Checklist", duration=4.2, texts=["ALL YOU NEED TO DO", "Drop your clips", "Trigger the skill"])
def checklist(img, t, ctx):
    """Frosted-glass checklist panel over the footage: step 1 is ticked at 1.2s, labels replace placeholder bars at
    0.6s / 1.9s, the counter flips 0 of 3 -> 1 of 3. Slots: 0 panel heading, 1 step 1, 2 step 2."""
    pl, pt, pw = cq(6), cq(22), cq(88)
    pad = cq(3.6)
    hf = font("mono", cq(2), 500)
    htr = .14 * cq(2)
    hh = _lh(hf)
    row_h = cq(8)
    ph = pad * 2 + hh + cq(3) + row_h * 3
    out = img.convert("RGBA")
    box = (int(pl), int(pt), int(pl + pw), int(pt + ph))

    def panel_mask():
        return rrect((box[2] - box[0], box[3] - box[1]), cq(3), WHITE).getchannel("A")
    m = ctx.cached("b07_mask", panel_mask)
    # shadow outside the box: 0 1cqw 5cqw #0007
    sh_a = ImageChops.offset(Image.new("L", (W, H), 0), 0, 0)
    big = Image.new("L", (W, H), 0)
    big.paste(m, (box[0], box[1]))
    sh_a = ImageChops.offset(big, 0, int(cq(1))).filter(ImageFilter.GaussianBlur(cq(2.5))).point(lambda v: int(v * .44))
    sh_a = ImageChops.multiply(sh_a, ImageChops.invert(big))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(sh_a)
    out.alpha_composite(sh)
    # backdrop blur 6px + tint #17191a d9
    region = out.crop(box).convert("RGB").filter(ImageFilter.GaussianBlur(6 * W / 400))
    glass = Image.alpha_composite(region.convert("RGBA"), solid(_hex("#17191a", 217), region.size))
    out.paste(glass, (box[0], box[1]), m)
    out = out.convert("RGB")

    # header
    _text(out, "  " + ctx.text(0, "ALL YOU NEED TO DO"), hf, pl + pad, pt + pad, tracking=htr, fill=_hex("#9fa7a1"))
    d = cq(1.1)
    ov = ellipse((int(d), int(d)), _hex("#9fa7a1"))
    paste(out, ov, (pl + pad + (hf.getlength("M") + htr - d) / 2, pt + pad + (hh - d) / 2))
    _text(out, "1 of 3" if t >= 1.2 else "0 of 3", hf, pl + pw - pad, pt + pad, tracking=htr, align="right",
          fill=_hex("#9fa7a1"))

    rows_y = pt + pad + hh + cq(3)
    lf = font("sans", cq(4.8), 700)
    labels = [(ctx.text(1, "Drop your clips"), .6), (ctx.text(2, "Trigger the skill"), 1.9), (None, 9e9)]
    bar_w = (pw - pad * 2) * .55
    for i, (lab, tlab) in enumerate(labels):
        cy = rows_y + row_h * i + row_h / 2
        cd = int(cq(5))
        done = i == 0 and t >= 1.2
        circ = ellipse((cd, cd), YELLOW if done else (0, 0, 0, 0), YELLOW if done else _hex("#8a918c"), max(1, int(cq(.4))))
        paste(out, circ, (pl + pad, cy - cd / 2))
        if done:
            paste(out, _check(cd, _hex("#222222"), cq(.62)), (pl + pad, cy - cd / 2))
        if lab and t >= tlab:
            _text(out, lab, lf, pl + pad + cq(8), cy - _lh(lf) / 2)
        else:
            bar = rrect((int(bar_w), int(cq(2.2))), cq(1), (255, 255, 255, 0x26))
            paste(out, bar, (pl + pad + cq(8), cy - cq(1.1)))
    return out


# =========================================================================== B08 Headline wall
_NOTES = [  # left, top, width, rot, text slot default
    (6, 12, 40, -3, "Claude can edit everyone’s videos now"),
    (52, 8, 38, 3, "Claude edits your whole reel"),
    (4, 44, 44, 2, "Your next video editor is Claude"),
    (56, 42, 40, -2, "Yes, Claude can edit videos."),
]
_CHIPS = [(8, 34, -4, "claude edits videos"), (58, 70, 3, "your whole reel")]


def _note(text, w_cq):
    f = font("serif", cq(4.6), 400)
    padx, pady = cq(2.2), cq(2)
    lines = _wrap(text, f, cq(w_cq) - 2 * padx)
    lh = cq(4.6) * 1.1
    h = int(pady * 2 + lh * len(lines))
    lay = rgba(cq(w_cq), h, _hex("#f4efe3"))
    for i, ln in enumerate(lines):
        _text(lay, ln, f, padx, pady + i * lh, line_h=lh, fill=_hex("#1c1a17"))
    pin = int(cq(1.6))
    shadowed = drop_shadow(lay, cq(1), (0, int(cq(1))), (0, 0, 0, 102))
    sp = (shadowed.width - lay.width) // 2
    shadowed.alpha_composite(ellipse((pin, pin), _hex("#c24a3a")), (sp + lay.width // 2 - pin // 2, sp - pin // 2))
    return shadowed


def _chip(text):
    f = font("mono", cq(2.4), 500)
    lay = rrect((int(text_w(text, f) + cq(3.2)), int(_lh(f) + cq(2))), cq(1), _hex("#111111"))
    _text(lay, text, f, cq(1.6), cq(1))
    return lay


@effect("B08", "Headline wall", duration=4.4, needs_mask=True,
        texts=[n[4] for n in _NOTES] + [c[3] for c in _CHIPS])
def headline_wall(img, t, ctx):
    """Footage darkens and paper headline notes plus dark chips pop onto the wall behind the speaker, one every .28s.
    Needs the subject matte so notes sit behind the person. Slots 0-3 notes, 4-5 chips."""
    wall = css_filter(img, brightness=.7, saturate=.8)
    out = wall.convert("RGBA")
    items = []
    for i, (l, tp, w, r, dflt) in enumerate(_NOTES):
        items.append((i, ctx.cached(("b08n", i, ctx.text(i, dflt)), lambda i=i, w=w, d=dflt: _note(ctx.text(i, d), w)), l, tp, w, r))
    for j, (l, tp, r, dflt) in enumerate(_CHIPS):
        i = 4 + j
        items.append((i, ctx.cached(("b08c", i, ctx.text(i, dflt)), lambda i=i, d=dflt: _chip(ctx.text(i, d))), l, tp, None, r))
    for i, lay, l, tp, w, r in items:
        lt = t - (.3 + i * .28)
        if lt <= 0:
            continue
        p = SPRING(clamp01(lt / .35))
        sc = .4 + .6 * p
        op = clamp01(p * 1.0)
        if w:   # note: layer has a baked shadow margin on all sides
            sp = (lay.width - cq(w)) / 2
            cx, cy = cq(l) + cq(w) / 2, cq(tp) + (lay.height - 2 * sp) / 2
        else:
            cx, cy = cq(l) + lay.width / 2, cq(tp) + lay.height / 2
        place(out, lay, cx, cy, scale=sc, rot=r, opacity=op)
    base = out.convert("RGB")
    return Image.composite(img.convert("RGB"), base, ctx.mask().convert("L"))
