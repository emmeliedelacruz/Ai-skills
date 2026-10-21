"""B13 Paper cut, B14 Doodle boil, B15 Vertigo, B16 Cover story, B17 Glass type.

All five cut the speaker out with the subject matte (ctx.mask(), white = subject) and put the
cut-out in front of a rebuilt background layer. Supply a real matte with --mask for production.
"""
import math
import re

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .core import (CQW, EASE, EASE_IN_OUT, EASE_OUT, SPRING, W, H, bezier, clamp01, cq, css_filter, drop_shadow, effect,
                   font, keyframes, lerp, paste, place, rgba, rrect, seg, text_layer, text_w, with_opacity, zoom)


# --------------------------------------------------------------------------- local helpers
def _cutout(img, m):
    out = img.convert("RGBA")
    out.putalpha(m.convert("L"))
    return out


def _shift(a, s, axis):
    """out[i] = a[i+s] along axis, zero padded."""
    out = np.zeros_like(a)
    n = a.shape[axis]
    if abs(s) >= n:
        return out
    src = [slice(None)] * a.ndim
    dst = [slice(None)] * a.ndim
    if s >= 0:
        src[axis], dst[axis] = slice(s, n), slice(0, n - s)
    else:
        src[axis], dst[axis] = slice(0, n + s), slice(-s, n)
    out[tuple(dst)] = a[tuple(src)]
    return out


def _max_window(a, length, axis):
    """max over offsets [0, length-1] using log-step doubling."""
    out, covered = a, 1
    while covered * 2 <= length:
        out = np.maximum(out, _shift(out, covered, axis))
        covered *= 2
    if covered < length:
        out = np.maximum(out, _shift(out, length - covered, axis))
    return out


def _dilate_square(mask, r):
    """Square dilation by r px (feMorphology dilate). mask: L image."""
    r = int(round(r))
    a = np.asarray(mask, dtype=np.uint8)
    for axis in (0, 1):
        a = _shift(_max_window(a, 2 * r + 1, axis), -r, axis)
    return Image.fromarray(a, "L")


def _dilate_cross(mask, r):
    """Union of the mask shifted up/down/left/right by r px (what four CSS drop-shadows make)."""
    r = int(round(r))
    a = np.asarray(mask, dtype=np.uint8)
    out = a
    for axis in (0, 1):
        out = np.maximum(out, np.maximum(_shift(a, r, axis), _shift(a, -r, axis)))
    return Image.fromarray(out, "L")


_TBL = {}


def _table(seed, o):
    k = (seed, o)
    if k not in _TBL:
        _TBL[k] = np.random.default_rng(seed * 131 + o * 17 + 5).random((64, 64))
    return _TBL[k]


def _vnoise(xs, ys, period_x, period_y, seed, octaves=2):
    """Smooth value noise in 0..1 (mean .5) sampled at pixel arrays xs, ys."""
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        tbl = _table(seed, o)
        gx, gy = xs / (period_x / 2 ** o), ys / (period_y / 2 ** o)
        x0, y0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
        fx, fy = gx - x0, gy - y0
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        n = ((tbl[x0 % 64, y0 % 64] * (1 - fx) + tbl[(x0 + 1) % 64, y0 % 64] * fx) * (1 - fy)
             + (tbl[x0 % 64, (y0 + 1) % 64] * (1 - fx) + tbl[(x0 + 1) % 64, (y0 + 1) % 64] * fx) * fy)
        total += n * amp
        norm += amp
        amp *= .5
    n = total / norm
    return .5 + (n - .5) * 2.2   # value noise is flatter than feTurbulence; stretch the spread


def _mesh_warp(layer, dxy_fn, origin=(0, 0), cell=36):
    """Displace a layer like feDisplacementMap: out(p) = in(p + d(p)). dxy_fn gets global px coords."""
    w, h = layer.size
    xs = list(range(0, w, cell)) + [w]
    ys = list(range(0, h, cell)) + [h]
    gx, gy = np.meshgrid(np.array(xs, float), np.array(ys, float))
    dx, dy = dxy_fn(gx + origin[0], gy + origin[1])
    sx, sy = gx + dx, gy + dy
    data = []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            data.append(((xs[i], ys[j], xs[i + 1], ys[j + 1]),
                         (sx[j, i], sy[j, i], sx[j + 1, i], sy[j + 1, i],
                          sx[j + 1, i + 1], sy[j + 1, i + 1], sx[j, i + 1], sy[j, i + 1])))
    return layer.transform((w, h), Image.MESH, data, Image.BILINEAR)


def _skew_scale(img, skew_deg, scale, blur_px):
    """CSS `skewX(a) scale(s)` about the centre, then blur(): used for the glass ripple."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    tn = math.tan(math.radians(skew_deg))
    s = scale
    out = img.transform((w, h), Image.AFFINE,
                        (1 / s, -tn / s, cx - cx / s + tn * cy / s, 0, 1 / s, cy - cy / s), resample=Image.BICUBIC)
    return out.filter(ImageFilter.GaussianBlur(blur_px)) if blur_px > .3 else out


def _tile_mask(box, poly_pct, ss=3):
    """Polygon clip (CSS clip-path percentages) as an L mask of box size."""
    w, h = box
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x / 100 * w * ss, y / 100 * h * ss) for x, y in poly_pct], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def _stripes(size, angle_deg, a_len, a_col, b_len, b_col, ss=2):
    """CSS repeating-linear-gradient(angle, A 0 a_len, B a_len b_len) with hard stops; colours RGBA tuples."""
    w, h = int(size[0] * ss), int(size[1] * ss)
    a = math.radians(angle_deg)
    dx, dy = math.sin(a), -math.cos(a)
    length = abs(w * dx) + abs(h * dy)
    ys, xs = np.mgrid[0:h, 0:w]
    pos = ((xs - w / 2) * dx + (ys - h / 2) * dy) + length / 2
    period = (a_len + b_len) * ss
    m = np.mod(pos, period)
    first = (m < a_len * ss)[..., None]
    arr = np.where(first, np.array(a_col, np.uint8), np.array(b_col, np.uint8)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((int(size[0]), int(size[1])), Image.LANCZOS)


def _gblur(a, sigma):
    """Separable gaussian on a float array (H, W[, C]) with edge replication."""
    r = int(math.ceil(sigma * 3))
    k = np.exp(-(np.arange(-r, r + 1) ** 2) / (2 * sigma ** 2))
    k /= k.sum()
    for axis in (0, 1):
        pad = [(0, 0)] * a.ndim
        pad[axis] = (r, r)
        p = np.pad(a, pad, mode="edge")
        n = a.shape[axis]
        out = np.zeros_like(a)
        for i, kv in enumerate(k):
            sl = [slice(None)] * a.ndim
            sl[axis] = slice(i, i + n)
            out += kv * p[tuple(sl)]
        a = out
    return a


def _plate(img, m):
    """Rough clean plate: fill the subject area with colours diffused in from the surroundings
    (normalised blur at 1/8 res, float maths so no banding)."""
    sw, sh = W // 8, H // 8
    small = np.asarray(img.resize((sw, sh), Image.BILINEAR), np.float32)
    mk = _dilate_square(m.resize((sw, sh), Image.BILINEAR), 3)
    k = 1.0 - np.asarray(mk, np.float32) / 255.0
    num1, den1 = _gblur(small * k[..., None], 3), _gblur(k, 3)[..., None]
    num2, den2 = _gblur(small * k[..., None], 12), _gblur(k, 12)[..., None]
    f1 = num1 / np.maximum(den1, 1e-4)
    f2 = num2 / np.maximum(den2, 1e-4)
    wgt = np.clip(den1 / .15, 0, 1)
    fill = f1 * wgt + f2 * (1 - wgt)
    fill_img = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8), "RGB").resize((W, H), Image.BICUBIC)
    soft = _dilate_square(m, cq(1.2)).filter(ImageFilter.GaussianBlur(cq(.8)))
    return Image.composite(fill_img, img, soft)


# --------------------------------------------------------------------------- B13 Paper cut
_PAPER = (0xf1, 0xec, 0xe0)
_BL_POLY = [(0, 4), (12, 0), (40, 3), (72, 0), (100, 5), (98, 40), (100, 78), (96, 100), (60, 97), (30, 100), (2, 96), (4, 50)]
_YL_POLY = [(0, 8), (18, 0), (50, 5), (80, 0), (100, 10), (96, 50), (100, 92), (70, 100), (30, 96), (4, 100), (8, 50)]
_RANSOM = [((0x2b, 0x3f, 0xb0), (255, 255, 255)), ((0xec, 0xe8, 0xdc), (0x11, 0x11, 0x11)),
           ((0x11, 0x11, 0x11), (255, 255, 255)), ((0xec, 0xe8, 0xdc), (0x11, 0x11, 0x11))]
POP = bezier(.2, 1.4, .4, 1)


def _paper_bg():
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = _PAPER
    a[..., 3] = 255
    step = cq(5)
    lw = 2
    line = np.array([0, 0, 0, 255], np.float32)
    img = Image.fromarray(a, "RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x = 0.0
    while x < W:
        d.rectangle((int(x), 0, int(x) + lw - 1, H), fill=(0, 0, 0, 15))
        x += step
    y = 0.0
    while y < H:
        d.rectangle((0, int(y), W, int(y) + lw - 1), fill=(0, 0, 0, 15))
        y += step
    img.alpha_composite(ov)
    return img.convert("RGB")


def _b13_layers(ctx):
    L = {}
    bw, bh = int(cq(58)), int(cq(62))
    bl = _stripes((bw, bh), 115, cq(.6), (0x6f, 0x86, 0xd9, 255), cq(.9), (0xa7, 0xb7, 0xf0, 255))
    bl.putalpha(ImageChops.multiply(bl.getchannel("A"), _tile_mask((bw, bh), _BL_POLY)))
    L["bl"] = (bl, cq(6), cq(8))
    yw, yh = int(cq(66)), int(cq(60))
    yl = Image.new("RGBA", (yw, yh), (0xf3, 0xe0, 0x4a, 255))
    yl.putalpha(_tile_mask((yw, yh), _YL_POLY))
    L["yl"] = (yl, cq(30), cq(74))
    hw, hh = int(cq(26)), int(cq(22))
    L["hx"] = (_stripes((hw, hh), 60, cq(.5), (0x7a, 0x8f, 0xd0, 255), cq(.7), (0, 0, 0, 0)), cq(58), cq(78))
    pw, ph = int(cq(14)), int(cq(12))
    pk = _stripes((pw, ph), 45, cq(.5), (0xe8, 0x5a, 0x7a, 255), cq(.8), (0, 0, 0, 0))
    pk.putalpha(ImageChops.multiply(pk.getchannel("A"), rrect((pw, ph), cq(1)).getchannel("A")))
    L["pk"] = (pk, cq(62), cq(108))
    # "× ✱" in brick red
    xw, xh = int(cq(18)), int(cq(7))
    xm = Image.new("RGBA", (xw, xh), (0, 0, 0, 0))
    red = (0xb2, 0x40, 0x2f, 255)
    f = font("sans", cq(5.2), 700)
    xt = text_layer("×", f, red, pad=0)
    xm.alpha_composite(xt, (0, int((xh - xt.height) / 2)))
    ax, ay, ar = int(cq(10.5)), xh // 2, cq(1.7)
    big = Image.new("RGBA", (xw * 3, xh * 3), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    for k in range(3):
        a = math.radians(90 + k * 60)
        bd.line((ax * 3 - math.cos(a) * ar * 3, ay * 3 - math.sin(a) * ar * 3,
                 ax * 3 + math.cos(a) * ar * 3, ay * 3 + math.sin(a) * ar * 3), fill=red, width=int(cq(.7) * 3))
    xm.alpha_composite(big.resize((xw, xh), Image.LANCZOS))
    L["xm"] = (xm, cq(8), cq(78))
    return L


def _paste_sticker(out, img, m):
    """Cut-out at scale 1.5 (origin 30% 100%) with a white 'paper' border and soft drop shadow, pasted onto out."""
    zi = zoom(img, 1.5, .3, 1.0)
    zm = zoom(m.convert("L"), 1.5, .3, 1.0)
    edge = _dilate_cross(zm, cq(.7))
    half = edge.resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(cq(1.6) / 2))
    shadow = half.resize((W, H), Image.BILINEAR).point(lambda v: int(v * .4))
    out.paste((0, 0, 0), (0, int(cq(1))), shadow)
    out.paste((255, 255, 255), (0, 0), edge)
    out.paste(zi, (0, 0), zm)


@effect("B13", "Paper cut", duration=4.6, texts=["100%"], needs_mask=True)
def paper_cut(img, t, ctx):
    """Speaker as a white-bordered sticker on a paper collage; ransom-note letters spell the text and get circled.
    text 0 = ransom-note headline (one tile per character)."""
    bg = ctx.cached("b13bg", _paper_bg)
    out = bg.copy()
    L = ctx.cached("b13layers", lambda: _b13_layers(ctx))

    def popped(key, delay, dur, bez):
        layer, x, y = L[key]
        p = seg(t, delay, dur)
        if p <= 0:
            return
        e = bez(p)
        place(out, layer, x + layer.width / 2, y + layer.height / 2, scale=lerp(.4, 1, e), opacity=clamp01(e))

    popped("bl", .1, .4, POP)
    popped("yl", .4, .4, POP)
    for k in ("hx", "pk", "xm"):
        popped(k, .7, .3, EASE)

    # ransom-note letters
    word = ctx.text(0, "100%")
    tw, th = int(cq(9)), int(cq(11))
    f = font("serif", cq(8))
    for i, ch in enumerate(word):
        p = seg(t, 1.1 + i * .25, .25)
        if p <= 0:
            continue
        e = SPRING(p)
        bgc, fg = _RANSOM[i % 4]
        tile = rrect((tw, th), 0, bgc + (255,))
        tl = text_layer(ch, f, fg + (255,), pad=0)
        tile.alpha_composite(tl, (int((tw - tl.width) / 2), int((th - tl.height) / 2)))
        tile = drop_shadow(tile, blur=cq(1), offset=(0, int(cq(.5))), color=(0, 0, 0, 68))
        cx = cq(8) + i * (tw + cq(.8)) + tw / 2
        cy = cq(12) + th / 2
        place(out, tile, cx, cy, scale=lerp(.4, 1, e), opacity=clamp01(e))

    # red hand-drawn ellipse, dash-offset reveal from 3 o'clock, clockwise, tilted -2deg
    p = EASE_OUT(seg(t, 2.3, .6))
    if p > 0:
        n = max(2, int(120 * p))
        pts = []
        rot = math.radians(-2)
        for k in range(n + 1):
            th_ = 2 * math.pi * p * k / n
            ex, ey = 22.5 * math.cos(th_), 8.5 * math.sin(th_)
            rx = ex * math.cos(rot) - ey * math.sin(rot)
            ry = ex * math.sin(rot) + ey * math.cos(rot)
            pts.append((cq(3 + 24 + rx), cq(7 + 10 + ry)))
        x0, y0 = int(cq(0)), int(cq(2))
        ov = Image.new("RGBA", (W * 2, int(cq(40)) * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.line([(x * 2, (y - y0) * 2) for x, y in pts], fill=(0xd3, 0x3a, 0x3a, 255), width=int(cq(.7) * 2), joint="curve")
        ov = ov.resize((W, int(cq(40))), Image.LANCZOS)
        paste(out, ov, (0, y0))

    _paste_sticker(out, img, ctx.mask())
    return out


# --------------------------------------------------------------------------- B14 Doodle boil
def _parse_path(d):
    """Tiny SVG path parser (M m h v l c z, relative or absolute) -> list of (points, closed)."""
    toks = re.findall(r"[MmHhVvLlCcZz]|-?\d*\.?\d+", d)
    subs, cur, pos, start, i, cmd = [], [], (0.0, 0.0), (0.0, 0.0), 0, None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v

    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "zZ":
                if cur:
                    cur.append(start)
                    subs.append(cur)
                    cur = []
                pos = start
                continue
        rel = cmd.islower()
        c = cmd.lower()
        if c == "m":
            if cur:
                subs.append(cur)
            x, y = num(), num()
            pos = (pos[0] + x, pos[1] + y) if rel else (x, y)
            start = pos
            cur = [pos]
            cmd = "l" if rel else "L"
        elif c == "l":
            x, y = num(), num()
            pos = (pos[0] + x, pos[1] + y) if rel else (x, y)
            cur.append(pos)
        elif c == "h":
            x = num(); pos = (pos[0] + x, pos[1]) if rel else (x, pos[1]); cur.append(pos)
        elif c == "v":
            y = num(); pos = (pos[0], pos[1] + y) if rel else (pos[0], y); cur.append(pos)
        elif c == "c":
            v = [num() for _ in range(6)]
            p0 = pos
            if rel:
                p1, p2, p3 = (p0[0] + v[0], p0[1] + v[1]), (p0[0] + v[2], p0[1] + v[3]), (p0[0] + v[4], p0[1] + v[5])
            else:
                p1, p2, p3 = (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
            for k in range(1, 17):
                u = k / 16
                x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
                y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
                cur.append((x, y))
            pos = p3
    if cur:
        subs.append(cur)
    return subs


def _partial(subs, frac):
    """Polylines covering the first `frac` of the total drawn length (stroke-dashoffset reveal)."""
    lens = [sum(math.dist(a, b) for a, b in zip(s, s[1:])) for s in subs]
    budget = sum(lens) * frac
    out = []
    for s in subs:
        pts = [s[0]]
        for a, b in zip(s, s[1:]):
            seg_len = math.dist(a, b)
            if budget <= 0:
                break
            if seg_len <= budget:
                pts.append(b)
                budget -= seg_len
            else:
                k = budget / seg_len
                pts.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
                budget = 0
        if len(pts) > 1:
            out.append(pts)
        if budget <= 0:
            break
    return out


U = 12.0  # px per preview SVG unit (viewBox 90 wide -> 1080 px)
_DOODLES = [
    ("M8 24 h18 v13 h-18z M8 24 l3 -5 h18 l-3 5 M14 19 l-3 5 M20 19 l-3 5 M26 19 l-3 5", (0xff, 0x9d, 0xb4), .4, .6),
    ("M62 26 c-3 -5 -10 -2 -6 4 l6 6 l6 -6 c4 -6 -3 -9 -6 -4z", (0xff, 0x9d, 0xb4), .9, .5),
    ("M68 44 h10 v10 h-10z", (255, 255, 255), 1.3, .5),
]


@effect("B14", "Doodle boil", duration=4.2, needs_mask=True)
def doodle_boil(img, t, ctx):
    """Dimmed shot, speaker outlined with a wobbling white line plus pink/white hand-drawn doodles that draw on."""
    step = int(t / .1) % 6
    out = css_filter(img, brightness=.45, saturate=.7)
    m = ctx.mask()
    out.paste(img, (0, 0), m)

    # boiling outline: ring around the matte (dilate .7 units, minus matte), displaced by animated noise
    ring = ImageChops.subtract(_dilate_square(m, .7 * U), m)
    s1 = 2.4 * U
    ring = _mesh_warp(ring, lambda x, y: (s1 * (_vnoise(x, y, 200, 200, step + 1) - .5),
                                          s1 * (_vnoise(x, y, 200, 200, step + 101) - .5)))
    white = Image.new("RGB", (W, H), (255, 255, 255))
    out.paste(white, (0, 0), ring)

    # doodles: stroke reveal, then the second boil displacement
    box = (int(4 * U), int(14 * U), int(86 * U), int(60 * U))
    ss = 2
    lay = Image.new("RGBA", ((box[2] - box[0]) * ss, (box[3] - box[1]) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    drew = False
    for path, col, t0, dur in _DOODLES:
        p = EASE_OUT(seg(t, t0, dur))
        if p <= 0:
            continue
        drew = True
        width = int(.7 * U * ss)
        for pts in _partial(_parse_path(path), p):
            xy = [((x * U - box[0]) * ss, (y * U - box[1]) * ss) for x, y in pts]
            d.line(xy, fill=col + (255,), width=width, joint="curve")
            for (x, y) in (xy[0], xy[-1]):
                d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=col + (255,))
    if drew:
        lay = lay.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
        s2 = 1.6 * U
        lay = _mesh_warp(lay, lambda x, y: (s2 * (_vnoise(x, y, 170, 170, step + 2) - .5),
                                            s2 * (_vnoise(x, y, 170, 170, step + 102) - .5)), origin=(box[0], box[1]),
                         cell=24)
        paste(out, lay, (box[0], box[1]))
    return out


# --------------------------------------------------------------------------- B15 Vertigo
@effect("B15", "Vertigo", duration=4.8, texts=["SUCK", "AT", "DESIGN"], needs_mask=True)
def vertigo(img, t, ctx):
    """Dolly zoom: the background pushes in 1x->1.6x (and back) about 50%/72% while the speaker stays put.
    text 0.. = caption words that rise in one by one (last word is highlighted yellow)."""
    m = ctx.mask()
    plate = _plate(img, m)
    tau = t % 4.8
    s = 1 + .6 * EASE_IN_OUT(tau / 2.4) if tau < 2.4 else 1.6 - .6 * EASE_IN_OUT((tau - 2.4) / 2.4)
    out = zoom(plate, s, .5, .72)
    out.paste(img, (0, 0), m)

    words = [w for w in ctx.texts if w] or ["SUCK", "AT", "DESIGN"]
    f = font("sans", cq(5.4), 800)
    gap = cq(2)
    widths = [text_w(w, f) for w in words]
    total = sum(widths) + gap * (len(words) - 1)
    asc, desc = f.getmetrics()
    x = (W - total) / 2
    for i, w in enumerate(words):
        p = EASE(seg(t, .2 + .5 * i, .3))
        col = (0xf5, 0xe6, 0x6a, 255) if i == len(words) - 1 and len(words) > 1 else (255, 255, 255, 255)
        if p > 0:
            lay = text_layer(w, f, col, pad=int(cq(3)), shadow=(0, 0, cq(1.6), (0, 0, 0, 170)))
            place(out, lay, x + widths[i] / 2, cq(100) + (asc + desc) / 2 + cq(3) * (1 - p), opacity=p)
        x += widths[i] + gap
    return out


# --------------------------------------------------------------------------- B16 Cover story
LP = bezier(.2, 1.2, .3, 1)


@effect("B16", "Cover story", duration=4.0, texts=["EDIT"], needs_mask=True)
def cover_story(img, t, ctx):
    """Giant serif masthead letters pop in behind the speaker under a thin rule. text 0 = masthead word."""
    out = css_filter(img, saturate=.85)
    paste(out, rgba(int(W - 2 * cq(5)), max(2, int(cq(.3))), (0xf3, 0xee, 0xe3, 0x88)), (cq(5), cq(8)))

    word = ctx.text(0, "EDIT")
    size = cq(38)
    f = font("serif", size)
    tr = .02 * size
    total = text_w(word, f, tr)
    if total > W * .94:                       # keep long words on screen
        size *= W * .94 / total
        f = font("serif", size)
        tr = .02 * size
        total = text_w(word, f, tr)
    x = (W - total) / 2
    cy0 = cq(44) + size / 2
    for i, ch in enumerate(word):
        adv = f.getlength(ch) + tr
        p = LP(seg(t, .4 + i * .18, .5))
        if p > 0 and ch != " ":
            lay = text_layer(ch, f, (0xf3, 0xee, 0xe3, 255), pad=int(cq(4)), shadow=(0, 0, cq(3), (0, 0, 0, 68)))
            place(out, lay, x + adv / 2 - tr / 2, cy0 + .4 * size * (1 - p), scale=.6 + .4 * p, opacity=clamp01(p))
        x += adv
    out.paste(img, (0, 0), ctx.mask())
    return out


# --------------------------------------------------------------------------- B17 Glass type
def _glass_layers(word):
    size = cq(19)
    f = font("sans", size, 800)
    wd = text_w(word, f)
    if wd > W * .9:
        size *= W * .9 / wd
        f = font("sans", size, 800)
    asc, desc = f.getmetrics()
    y0 = cq(90)
    top, bot = int(y0 - asc - cq(6)), int(y0 + desc + cq(6))
    rh = bot - top
    base = Image.new("L", (W, rh), 0)
    ImageDraw.Draw(base).text((W / 2, y0 - top), word, font=f, fill=255, anchor="ms")
    outer = Image.new("L", (W, rh), 0)
    ImageDraw.Draw(outer).text((W / 2, y0 - top), word, font=f, fill=255, anchor="ms", stroke_width=2)
    inner = base.filter(ImageFilter.MinFilter(5))
    ring = ImageChops.subtract(outer, inner)
    # fill: white, opacity .6 (top of text box) -> .1 (bottom)
    ys = np.arange(rh)[:, None]
    g = np.clip((ys - (y0 - top - asc)) / (asc + desc), 0, 1)
    fa = (np.asarray(base, np.float32) / 255.0) * (.6 + (.1 - .6) * g)
    sa = (np.asarray(ring, np.float32) / 255.0) * .75
    a = fa + sa * (1 - fa)
    layer = np.zeros((rh, W, 4), np.uint8)
    layer[..., :3] = 255
    layer[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    layer = Image.fromarray(layer, "RGBA")

    sc = 3 * CQW   # feDisplacementMap scale 3 (user units == cqw)

    def disp(x, y):
        n = _vnoise(x, y, 1 / .012 * CQW, 1 / .02 * CQW, 3, 2)
        return sc * (n - .5), sc * (n - .5)

    layer = _mesh_warp(layer, disp, origin=(0, top))
    cover = _mesh_warp(outer, disp, origin=(0, top))
    return layer, cover, top


@effect("B17", "Glass type", duration=4.4, texts=["DESIGN"], needs_mask=True)
def glass_type(img, t, ctx):
    """Frosted-glass lettering behind the speaker; the whole frame ripples at 2.6s. text 0 = lettering."""
    layer, cover, top = ctx.cached("b17", lambda: _glass_layers(ctx.text(0, "DESIGN")))
    out = img.copy()
    p = EASE(seg(t, .3, .8))
    if p > 0:
        dy = int(round(cq(3) * (1 - p)))
        region = out.crop((0, top - dy, W, top - dy + layer.height))
        frost = region.filter(ImageFilter.GaussianBlur(cq(1.1)))
        cov = cover.point(lambda v: int(v * p))
        region = Image.composite(frost, region, cov)
        region = region.convert("RGBA")
        region.alpha_composite(with_opacity(layer, p))
        out.paste(region.convert("RGB"), (0, top - dy))
    out.paste(img, (0, 0), ctx.mask())

    r = t - 2.6
    if 0 < r < 1.2:
        sk = keyframes(r, [(0, 0), (.36, 3), (.72, -3), (1.2, 0)], EASE_IN_OUT)
        sc = keyframes(r, [(0, 1), (.36, 1.03), (.72, 1.05), (1.2, 1)], EASE_IN_OUT)
        bl = keyframes(r, [(0, 0), (.36, 1.5), (.72, 2), (1.2, 0)], EASE_IN_OUT) * cq(.3)
        out = _skew_scale(out, sk, sc, bl)
    return out
