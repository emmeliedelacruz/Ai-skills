"""A13 Contact sheet hook, A14 Picture dive, A15 Live markup, A16 Projected film, A17 Reel feed.

Rebuilt from the preview CSS in video-effect-library.html (units in cqw via core.cq).
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .core import (EASE, EASE_OUT, H, W, bezier, cq, drop_shadow, effect, ellipse, fit_cover, font, gradient, keyframes,
                   lerp, paste, place, rgba, rrect, seg, steps, text_layer, text_w)


# --------------------------------------------------------------------------- local helpers
def _cover(img, w, h):
    return fit_cover(img, max(1, int(round(w))), max(1, int(round(h))))


def _line(out, txt, fnt, x, top, line_h, fill, tracking=0.0, opacity=1.0, dy=0.0):
    """Draw one CSS line box: glyph run centred vertically in a line of height line_h starting at `top`."""
    lay = text_layer(txt, fnt, fill, tracking, pad=0)
    paste(out, lay, (x, top + dy + (line_h - lay.height) / 2), opacity)
    return lay


def _css_chain(img, ops):
    """Apply CSS filter functions in the order given. ops = [("sepia", .45), ("contrast", .92), ...]."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = np.array([.2126, .7152, .0722], np.float32)
    sep = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]], np.float32)
    for name, v in ops:
        if name == "brightness":
            a = a * v
        elif name == "contrast":
            a = (a - .5) * v + .5
        elif name == "saturate":
            g = (a * lum).sum(-1, keepdims=True)
            a = g + (a - g) * v
        elif name == "grayscale":
            g = (a * lum).sum(-1, keepdims=True)
            a = a * (1 - v) + g * v
        elif name == "sepia":
            a = a * (1 - v) + np.clip(a @ sep.T, 0, 1.5) * v
        a = np.clip(a, 0, 1)
    return Image.fromarray((a * 255 + .5).astype(np.uint8))


# =========================================================================== A13
_C_W = (62 - 3 * 1.2) / 4          # grid cell width in cqw
_C_H = _C_W * 1.12                 # aspect-ratio 1/1.12
_CELL_DELAYS = [.7 + .1 * i for i in range(8)]


def _cell_rect(i):
    col, row = i % 4, i // 4
    return cq(4 + col * (_C_W + 1.2)), cq(44 + row * (_C_H + 1.2)), cq(_C_W), cq(_C_H)


def _sheet_static(ctx):
    base = Image.new("RGB", (W, H), (0x16, 0x33, 0x2a))
    cells = rrect((10, 10), 1)  # placeholder to warm up
    for i in range(16):
        x, y, w, h = _cell_rect(i)
        paste(base, rrect((int(round(w)), int(round(h))), cq(.6), (0x1f, 0x40, 0x33, 255)), (x, y))
    labels = rgba(W, H)
    f = font("mono", cq(1.5), 500)
    for i in range(16):
        x, y, w, h = _cell_rect(i)
        lay = text_layer(f"{i + 1:02d}", f, (0xc8, 0xa9, 0x5d, 255), pad=int(cq(.8)),
                         shadow=(0, 0, cq(.6) / 2, (0, 0, 0, 255)))
        asc, desc = f.getmetrics()
        pad = int(cq(.8))
        # label box: left .8cqw, bottom .4cqw of the cell (line-height normal)
        paste(labels, lay, (x + cq(.8) - pad - int(cq(.6)) * 0, y + h - cq(.4) - (asc + desc) - pad))
    return base, labels


@effect("A13", "Contact sheet hook", duration=5.0, texts=["CONTACT SHEET"], outro_fade=0)
def contact_sheet(img, t, ctx):
    """Frames fill a numbered grid, #08 is picked and zooms to full screen. Slot 0 = grid title."""
    if t >= 3.11:
        return img
    base, labels = ctx.cached("a13_static", lambda: _sheet_static(ctx))
    out = img.copy()
    vis = 1 - seg(t, 3.0, .01)  # .cs13 vanishes at 3s
    if vis > 0:
        sheet = base.copy()
        # title: rise .4s ease @.2s
        p = EASE(seg(t, .2, .4))
        tf = font("serif", cq(9.5))
        _line(sheet, ctx.text(0, "CONTACT SHEET"), tf, cq(4), cq(24), cq(9.5), (0xec, 0xe8, 0xdc, 255),
              tracking=.02 * cq(9.5), opacity=p, dy=cq(3) * (1 - p))
        # thumbnails fade in 1..8
        cw, ch = int(round(cq(_C_W))), int(round(cq(_C_H)))
        thumb = _cover(img, cw, ch).convert("RGBA")
        for i in range(8):
            fp = EASE(seg(t, _CELL_DELAYS[i], .2))
            if fp > 0:
                x, y, _, _ = _cell_rect(i)
                paste(sheet, thumb, (x, y), fp)
        # clip-free: cells never overflow, labels on top
        sheet.paste(labels, (0, 0), labels)
        # cell 8 highlight outline (.5cqw, offset -.2cqw) fading in @1.7s
        hp = EASE(seg(t, 1.7, .4))
        if hp > 0:
            x, y, w, h = _cell_rect(7)
            m = cq(.3)
            ring = rrect((int(round(w + 2 * m)), int(round(h + 2 * m))), cq(.9), (0, 0, 0, 0),
                         outline=(0xc8, 0xa9, 0x5d, int(255 * hp)), width=max(1, int(round(cq(.5)))))
            sheet = sheet.convert("RGBA")
            sheet.alpha_composite(ring, (int(round(x - m)), int(round(y - m))))
            sheet = sheet.convert("RGB")
        out = Image.blend(out, sheet, vis) if vis < 1 else sheet
    # zoom-to-full box, 1s cubic-bezier(.6,0,.2,1) @2.1s (visible from 1% in)
    if t >= 2.11:
        z = bezier(.6, 0, .2, 1)(seg(t, 2.11, .99))
        x0, y0, w0, h0 = _cell_rect(7)
        x, y = lerp(x0, 0, z), lerp(y0, 0, z)
        w, h = lerp(w0, W, z), lerp(h0, H, z)
        paste(out, _cover(img, w, h).convert("RGBA"), (x, y))
    return out


# =========================================================================== A14
_DIVE_SCALE = bezier(.7, 0, .3, 1)


def _picture(img, k, shadow=True):
    """The picture frame (36x48cqw) containing footage and a smaller frame, rendered at k px per cqw."""
    bw, bh = int(round(36 * k)), int(round(48 * k))
    box = Image.new("RGBA", (bw, bh), (0x11, 0x11, 0x11, 255))
    ImageDraw.Draw(box).rectangle((int(.9 * k), int(.9 * k), bw - 1 - int(.9 * k), bh - 1 - int(.9 * k)),
                                  fill=(0xf4, 0xf1, 0xe8, 255))
    px, py = (.9 + 3) * k, (.9 + 3) * k
    pw, ph = bw - 2 * px, bh - 2 * py
    box.paste(_cover(img, pw, ph), (int(round(px)), int(round(py))))
    # inner frame: left 28% top 22% width 44%, aspect 3/4, border .5, padding 1.4
    ix, iy = px + .28 * pw, py + .22 * ph
    iw = .44 * pw
    ih = iw * 4 / 3
    d = ImageDraw.Draw(box)
    d.rectangle((int(ix), int(iy), int(ix + iw) - 1, int(iy + ih) - 1), fill=(0x11, 0x11, 0x11, 255))
    b = .5 * k
    d.rectangle((int(ix + b), int(iy + b), int(ix + iw - b) - 1, int(iy + ih - b) - 1), fill=(0xf4, 0xf1, 0xe8, 255))
    pad = (.5 + 1.4) * k
    box.paste(_cover(img, iw - 2 * pad, ih - 2 * pad), (int(round(ix + pad)), int(round(iy + pad))))
    if shadow:
        box = drop_shadow(box, blur=1.5 * k, offset=(0, int(k)), color=(0, 0, 0, 102))
    return box


@effect("A14", "Picture dive", duration=4.8, outro_fade=0)
def picture_dive(img, t, ctx):
    """Footage inside a picture frame that itself holds a smaller framed copy; zoom through the frame."""
    u = (t - .2) / 3.0
    if u <= 0 or u >= 1:
        return img
    sc = keyframes(u, [(0, .9), (.1, 1), (.3, 1), (1, 5)], _DIVE_SCALE)
    op = keyframes(u, [(0, 0), (.1, 1), (.88, 1), (1, 0)], _DIVE_SCALE)
    if op <= 0.002:
        return img
    k = CQ = cq(1) * sc
    box = _picture(img, k, shadow=sc < 2.5)
    out = img.copy()
    paste(out, box, (cq(50) - box.width / 2, cq(62) - box.height / 2), op)
    return out


# =========================================================================== A15
def _bez(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        s = i / n
        a, b, c, d = (1 - s) ** 3, 3 * (1 - s) ** 2 * s, 3 * (1 - s) * s ** 2, s ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def _head(pts, frac_len):
    """First `frac_len` of the polyline's length (absolute length in the polyline's units)."""
    out, acc = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:]):
        seg_l = math.dist(a, b)
        if acc + seg_l >= frac_len:
            r = (frac_len - acc) / seg_l if seg_l else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            return out
        out.append(b)
        acc += seg_l
    return out


def _plen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def _markup_geometry(cx, cy):
    th = math.radians(-4)
    rx, ry = 19, 27
    ell = []
    for i in range(241):
        a = 2 * math.pi * i / 240
        x, y = rx * math.cos(a), ry * math.sin(a)
        ell.append((cx + x * math.cos(th) - y * math.sin(th), cy + x * math.sin(th) + y * math.cos(th)))
    dx, dy = cx - 50, cy - 102
    s = lambda p: (p[0] + dx, p[1] + dy)
    arrow = [[s(p) for p in _bez((25, 79), (23, 87), (29, 90), (36, 89))],
             [s((36, 89)), s((31, 84))], [s((36, 89)), s((31, 94))]]
    return ell, arrow


def _stroke(layer_draw, pts, w, color, ox, oy, ss, scale=1.0):
    P = [((x * W / 100 - ox) * ss, (y * W / 100 - oy) * ss) for x, y in pts]
    if len(P) < 2:
        return
    layer_draw.line(P, fill=color, width=int(round(w * ss)), joint="curve")
    r = w * ss / 2
    for x, y in (P[0], P[-1]):
        layer_draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


@effect("A15", "Live markup", duration=4.6, texts=["markup", "50,102"])
def live_markup(img, t, ctx):
    """Footage goes B&W, a hand-drawn circle is drawn round the subject and a note appears with an arrow.
    Slot 0 = note text; slot 1 = circle centre 'cx,cy' in cqw (default 50,102, i.e. the face in a 9:16 talking head)."""
    bw = EASE(seg(t, .2, .4))
    if bw >= 1:   # settled state: Rec.709 grayscale then contrast 1.15, via matrix + LUT (fast)
        out = img.convert("RGB", (.2126, .7152, .0722, 0) * 3).point([min(255, max(0, int((i / 255 - .5) * 1.15 * 255 + 127.5 + .5))) for i in range(256)] * 3)
    else:
        out = _css_chain(img, [("grayscale", bw), ("contrast", 1 + .15 * bw)]) if bw > 0 else img.copy()
    try:
        cx, cy = [float(v) for v in ctx.text(1, "50,102").split(",")]
    except ValueError:
        cx, cy = 50.0, 102.0
    ell, arrow = ctx.cached(("a15geo", cx, cy), lambda: _markup_geometry(cx, cy))
    col = (0xd9, 0x66, 0x7a, 255)
    pe = EASE_OUT(seg(t, .6, .8))
    pa = EASE_OUT(seg(t, 1.9, .5))
    if pe > 0 or pa > 0:
        allp = ell + [p for a in arrow for p in a]
        m = 2.5
        x0 = min(p[0] for p in allp) - m
        y0 = min(p[1] for p in allp) - m
        x1 = max(p[0] for p in allp) + m
        y1 = max(p[1] for p in allp) + m
        ox, oy = x0 * W / 100, y0 * W / 100
        ss = 2
        lay = Image.new("RGBA", (int((x1 - x0) * W / 100 * ss), int((y1 - y0) * W / 100 * ss)), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        sw = cq(.9)
        if pe > 0:
            _stroke(d, _head(ell, pe * _plen(ell)), sw, col, ox, oy, ss)
        if pa > 0:
            total = sum(_plen(a) for a in arrow)  # all subpaths draw their first pa*total length together
            for a in arrow:
                _stroke(d, _head(a, pa * total), sw, col, ox, oy, ss)
        lay = lay.resize((lay.width // ss, lay.height // ss), Image.LANCZOS)
        paste(out, lay, (ox, oy))
    # note: Caveat 700 15cqw, left 6cqw top 62cqw, rotate -6deg, rise .4s ease @1.5s
    np_ = EASE(seg(t, 1.5, .4))
    if np_ > 0:
        f = font("hand", cq(15), 700)
        lay = text_layer(ctx.text(0, "markup"), f, col, pad=int(cq(1)))
        cxn = cq(6 + (cx - 50)) + text_w(ctx.text(0, "markup"), f) / 2
        cyn = cq(62 + (cy - 102)) + cq(7.5) + cq(3) * (1 - np_)
        place(out, lay, cxn, cyn, rot=-6, opacity=np_)
    return out


# =========================================================================== A16
_FLICKER = [(0, .15), (7, .5), (13, .1), (31, .3), (33, .6), (35, .1), (62, .4), (64, .1), (88, .55), (90, .15)]
_SCR1 = [  # (start%, left%, visible) steps(1,end): value held from its keyframe to the next
    (0, 12, 1), (10, 70, 1), (22, 33, 0), (30, 84, 1), (48, 20, 0), (60, 58, 1), (78, 9, 1)]
_SCR2 = [(0, 80, 0), (15, 41, 1), (35, 6, 0), (52, 63, 1), (70, 27, 1)]
_GRAIN_KF = [(0, 0, 0), (.2, -5, 3), (.4, 4, -6), (.6, -3, 5), (.8, 6, 2), (1, 0, 0)]


def _held(table, pct):
    cur = table[0]
    for row in table:
        if pct >= row[0]:
            cur = row
    return cur


def _softlight_lut(cs, alpha):
    x = np.arange(256, dtype=np.float64) / 255
    if cs <= .5:
        B = x - (1 - 2 * cs) * x * (1 - x)
    else:
        D = np.where(x <= .25, ((16 * x - 12) * x + 4) * x, np.sqrt(x))
        B = x + (2 * cs - 1) * (D - x)
    return list(np.clip(((1 - alpha) * x + alpha * B) * 255 + .5, 0, 255).astype(np.uint8))


def _film_static(ctx):
    # vignette multiplier: radial-gradient(ellipse farthest-corner, transparent 50%, #000b 100%)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xs - W / 2) / (W / 2 * math.sqrt(2)), (ys - H / 2) / (H / 2 * math.sqrt(2)))
    vg = 1 - (0xbb / 255) * np.clip((d - .5) / .5, 0, 1)
    # grain tile (30cqw), fractal-noise-like alpha; tiled with margin so a window crop = scrolled bg
    tile = int(round(cq(30)))
    rng = np.random.default_rng(3)
    base = rng.normal(0, 1, (200, 200)).astype(np.float32)
    base = np.asarray(Image.fromarray(((base - base.min()) / np.ptp(base) * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(.6)), dtype=np.float32)
    base = (base - base.mean()) / (base.std() + 1e-6)
    n = Image.fromarray(np.clip(base * 40 + 128, 0, 255).astype(np.uint8)).resize((tile, tile), Image.BICUBIC)
    n = (np.asarray(n, dtype=np.float32) - 128) / 40
    alpha = np.clip(.5 + .15 * n, 0, 1) * .9 * .3      # svg alpha .9, layer opacity .3
    big = np.tile(alpha, (H // tile + 2, W // tile + 2))
    return vg.astype(np.float32), big, tile


def _sprockets(ctx, step):
    def build():
        strip_w = int(round(cq(6)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for sx in (0, W - strip_w):
            d.rectangle((sx, 0, sx + strip_w - 1, H - 1), fill=(5, 5, 5, 255))
            y = cq(3) * step + cq(3) - cq(9) * 2
            while y < H:
                d.rectangle((sx + int(round(cq(1.6))), int(round(y)), sx + strip_w - int(round(cq(1.6))) - 1,
                             int(round(y + cq(3))) - 1), fill=(0xef, 0xe9, 0xd8, 255))
                y += cq(9)
        return lay
    return ctx.cached(("a16spr", step), build)


@effect("A16", "Projected film", duration=5.0)
def projected_film(img, t, ctx):
    """Sepia projector look: flickering warm light, scrolling sprocket borders, scratches, grain, vignette."""
    vg, big, tile = ctx.cached("a16static", lambda: _film_static(ctx))
    out = _css_chain(img, [("sepia", .45), ("contrast", .92), ("brightness", 1.04), ("saturate", .85)])
    # flicker: soft-light #ffa850, opacity steps over 1.7s
    pct = (t % 1.7) / 1.7 * 100
    a = [v for s, v in _FLICKER if pct >= s][-1]
    lut = _softlight_lut(1.0, a) + _softlight_lut(0xa8 / 255, a) + _softlight_lut(0x50 / 255, a)
    out = out.point(lut)
    # sprocket strips (steps(3) every .6s)
    step = int((t % .6) / .2)
    out = out.convert("RGBA")
    out.alpha_composite(_sprockets(ctx, step))
    # scratches
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sc)
    sw = max(1, int(round(cq(.18))))
    for table, per in ((_SCR1, 3.3), (_SCR2, 3.3)):
        _, left, vis = _held(table, (t % per) / per * 100)
        if vis:
            x = int(round(W * left / 100))
            sd.rectangle((x, 0, x + sw - 1, H - 1), fill=(255, 255, 255, 0x88))
    out.alpha_composite(sc)
    a_rgb = np.asarray(out.convert("RGB"), dtype=np.float32)
    # grain: screen-blended noise, scrolls in 5-step jumps over .5s (box inset -20%)
    ph = (t % .5) / .5
    jump = lambda p: steps(p, 5)
    dxp = keyframes(ph, [(f, x) for f, x, _ in _GRAIN_KF], jump) / 100 * cq(140)
    dyp = keyframes(ph, [(f, y) for f, _, y in _GRAIN_KF], jump) / 100 * (H * 1.4)
    ox = int(round(cq(20) - dxp)) % tile
    oy = int(round(H * .2 - dyp)) % tile
    k = big[oy:oy + H, ox:ox + W, None]
    a_rgb = a_rgb + (255 - a_rgb) * k
    a_rgb *= vg[..., None]
    return Image.fromarray(np.clip(a_rgb + .5, 0, 255).astype(np.uint8))


# =========================================================================== A17
_FEED_EASE = bezier(.5, 0, .2, 1)
_BLUR_PX = W / 195.0   # the preview tile is ~195px wide; css blur(Npx) there scales to this many px at 1080


def _star(size, color, points=16, inner=.55):
    ss = 3
    s = int(size * ss)
    lay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    pts = []
    for i in range(points * 2):
        r = (s / 2) * (1 if i % 2 == 0 else inner)
        a = math.pi * i / points - math.pi / 2
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    ImageDraw.Draw(lay).polygon(pts, fill=color)
    return lay.resize((int(size), int(size)), Image.LANCZOS)


def _feed_panel(ctx):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.clip(np.hypot((xs - .3 * W) / (1.2 * W), (ys - .4 * H) / (.8 * H)), 0, 1)[..., None]
    c0 = np.array([0x3b, 0x1d, 0x12], np.float32)
    c1 = np.array([0x15, 0x0b, 0x07], np.float32)
    panel = Image.fromarray((c0 * (1 - d) + c1 * d).astype(np.uint8)).convert("RGBA")
    orange = (0xe9, 0x75, 0x4f, 255)
    cream = (0xf1, 0xec, 0xe0, 255)
    white = (255, 255, 255, 255)
    # app icon + search ring
    paste(panel, rrect((int(cq(32)), int(cq(32))), cq(7), white), (cq(12), cq(10)))
    paste(panel, _star(cq(16), orange), (cq(12 + 8), cq(10 + 8)))
    paste(panel, ellipse((int(cq(5)), int(cq(5))), (0, 0, 0, 0), white, int(cq(.6))), (cq(91), cq(6)))
    # headline block
    kf = font("mono", cq(2.5), 500)
    kicker = ctx.text(0, "// NO HUMAN TOUCHED")
    asc, desc = kf.getmetrics()
    _line(panel, kicker, kf, cq(5), cq(62), asc + desc, orange, tracking=.14 * cq(2.5))
    hf = font("sans", cq(15), 800)
    top = cq(62) + asc + desc + cq(2)
    lh = cq(15) * .95
    for i, (slot, dflt, col) in enumerate([(1, "CLAUDE", cream), (2, "EDITED", cream), (3, "THIS", orange)]):
        _line(panel, ctx.text(slot, dflt), hf, cq(5), top + i * lh, lh, col, tracking=-.03 * cq(15))
    # action column
    lf = font("sans", cq(2), 600)
    labels = [ctx.text(5, "12.9K"), ctx.text(6, "13.7K"), ctx.text(7, "187"), ctx.text(8, "5,833")]
    lasc, ldesc = lf.getmetrics()
    lh2 = lasc + ldesc
    colw = max(max(cq(5.4), text_w(s, lf)) for s in labels)
    y = cq(104)
    right = cq(97)
    for s in labels:
        cxm = right - colw / 2
        paste(panel, ellipse((int(cq(5.4)), int(cq(5.4))), (0, 0, 0, 0), white, int(cq(.6))), (cxm - cq(5.4) / 2, y))
        _line(panel, s, lf, cxm - text_w(s, lf) / 2, y + cq(5.4) + cq(.8), lh2, white)
        y += cq(5.4) + cq(.8) + lh2 + cq(3)
    # bottom row: avatar, name, "Paid partnership" (flex, centred on y = 177.78 - 6 - 3.5 cqw)
    cy = cq(177.78 - 6 - 3.5)
    av = gradient((int(cq(7)), int(cq(7))), (0x7b, 0xb8, 0x9a), (0x2f, 0x6a, 0x53), 135)
    av.putalpha(ellipse(av.size).getchannel("A"))
    paste(panel, av, (cq(4), cy - cq(3.5)))
    nf = font("sans", cq(3), 700)
    x = cq(4 + 7 + 2)
    nm = ctx.text(4, "creator")
    nasc, ndesc = nf.getmetrics()
    _line(panel, nm, nf, x, cy - (nasc + ndesc) / 2, nasc + ndesc, white)
    x += text_w(nm, nf) + cq(2 + 2)
    sf = font("sans", cq(2.2), 500)
    sasc, sdesc = sf.getmetrics()
    _line(panel, "Paid partnership", sf, x, cy - (sasc + sdesc) / 2, sasc + sdesc, (0xcf, 0xc8, 0xba, 255))
    return panel


@effect("A17", "Reel feed", duration=4.4,
        texts=["// NO HUMAN TOUCHED", "CLAUDE", "EDITED", "THIS", "creator", "12.9K", "13.7K", "187", "5,833"],
        outro_fade=0)
def reel_feed(img, t, ctx):
    """Cut to a social-feed UI that swipes up over the footage and out the top with a blur.
    Slots: 0 kicker, 1-3 headline lines (3rd is accent colour), 4 creator name, 5-8 the four side-rail counts."""
    u = t / 3.2
    if u >= 1:
        return img
    ty = keyframes(u, [(0, 1), (.1, 0), (.78, 0), (.92, -1), (1, -1)], _FEED_EASE)
    bl = keyframes(u, [(0, 6), (.1, 0), (.78, 0), (.92, 8), (1, 0)], _FEED_EASE) * _BLUR_PX
    if abs(ty) >= 1:
        return img
    panel = ctx.cached("a17panel", lambda: _feed_panel(ctx))
    out = img.copy()
    y = int(round(ty * H))
    if bl > 0.5:
        pad = int(bl * 3)
        half = Image.new("RGBA", (W // 2, (H + 2 * pad) // 2), (0, 0, 0, 0))
        half.paste(panel.resize((W // 2, H // 2), Image.BILINEAR), (0, pad // 2))
        half = half.filter(ImageFilter.GaussianBlur(bl / 2))
        lay = half.resize((W, half.height * 2), Image.BILINEAR)
        paste(out, lay, (0, y - pad))
    else:
        paste(out, panel, (0, y))
    return out
