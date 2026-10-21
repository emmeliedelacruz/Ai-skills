"""Cards, drops and panels: A18 Giant captions, A19 File drop, A20 Eyedropper grade, B01 Orbit, B02 Couch wall."""
from __future__ import annotations

import math
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .core import (CQW, EASE, EASE_IN_OUT, SPRING, W, H, bezier, blur, clamp01, cq, css_filter, drop_shadow, effect,
                   ellipse, fit_cover, font, gradient, keyframes, lerp, paste, place, rgba, rrect, seg, text_layer,
                   text_w, with_opacity)

# --------------------------------------------------------------------------- local helpers
_POP = bezier(.2, 1.5, .4, 1)


def _tl(txt, fnt, fill, tracking=0.0, shadow=None, pad=0):
    return text_layer(txt, fnt, fill, tracking, pad=pad, shadow=shadow)


def _lh_off(fnt, line_h):
    """Top offset of the glyph box inside a CSS line box of height line_h (px)."""
    asc, desc = fnt.getmetrics()
    return (line_h - (asc + desc)) / 2


def _hex(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _xf_place(base, layer, x, y, origin=(.5, .5), scale=1.0, rot=0.0, opacity=1.0, tx=0.0, ty=0.0, off=(0, 0)):
    """CSS-like `transform: translate(tx,ty) rotate(rot) scale(scale)` with transform-origin, for a layer whose
    box top-left is (x, y). `off` is the offset of the box inside the layer (when the layer carries a shadow pad)."""
    bw, bh = layer.width - 2 * off[0], layer.height - 2 * off[1]
    cx, cy = x + bw / 2, y + bh / 2
    ox, oy = x + origin[0] * bw, y + origin[1] * bh
    vx, vy = (cx - ox) * scale, (cy - oy) * scale
    a = math.radians(rot)
    rx, ry = vx * math.cos(a) - vy * math.sin(a), vx * math.sin(a) + vy * math.cos(a)
    return place(base, layer, ox + rx + tx, oy + ry + ty, scale=scale, rot=rot, opacity=opacity)


def _shadowed(layer, blur_css, dy, alpha):
    """Bake a CSS box-shadow (0 dy blur color) under a layer. Returns (layer, pad) so callers can offset."""
    sh = drop_shadow(layer, blur=blur_css / 2, offset=(0, int(dy)), color=(0, 0, 0, alpha))
    pad = (sh.width - layer.width) // 2
    return sh, pad


def _crop_frame(img, cx, cy, zoom, w, h):
    """Crop a w:h window of the frame centred at (cx, cy) (0..1), `zoom` = fraction of frame width visible."""
    vw = W * zoom
    vh = vw * h / w
    x0 = min(max(cx * W - vw / 2, 0), W - vw)
    y0 = min(max(cy * H - vh / 2, 0), H - vh)
    return img.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((int(w), int(h)), Image.BICUBIC)


def _mean_color(img, cx, cy, half=.04):
    box = (int((cx - half) * W), int((cy - half * W / H) * H), int((cx + half) * W), int((cy + half * W / H) * H))
    px = img.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0))
    return px[:3]


def _color_blend(img_np, tint_rgb, alpha):
    """CSS mix-blend-mode: color of a flat tint over img (float 0..1 array HxWx3), at opacity alpha."""
    lum = lambda c: .3 * c[..., 0] + .59 * c[..., 1] + .11 * c[..., 2]  # noqa: E731
    cs = np.broadcast_to(np.array(tint_rgb[:3], np.float32) / 255.0, img_np.shape)
    d = (lum(img_np) - lum(cs))[..., None]
    c = cs + d
    l = lum(c)[..., None]
    n = c.min(-1, keepdims=True)
    x = c.max(-1, keepdims=True)
    c = np.where(n < 0, l + (c - l) * l / np.maximum(l - n, 1e-6), c)
    c = np.where(x > 1, l + (c - l) * (1 - l) / np.maximum(x - l, 1e-6), c)
    c = np.clip(c, 0, 1)
    return img_np * (1 - alpha) + c * alpha


def _dashed_rrect(size, inset, radius, width, dash, gap, color, ss=3):
    """Dashed rounded-rect outline (RGBA)."""
    w, h = int(size[0]), int(size[1])
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    x0, y0, x1, y1 = inset, inset, w - inset, h - inset
    r = radius
    pts = []

    def arc(cx, cy, a0, a1):
        n = 14
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    pts.append((x0 + r, y0)); pts.append((x1 - r, y0)); arc(x1 - r, y0 + r, -90, 0)
    pts.append((x1, y1 - r)); arc(x1 - r, y1 - r, 0, 90)
    pts.append((x0 + r, y1)); arc(x0 + r, y1 - r, 90, 180)
    pts.append((x0, y0 + r)); arc(x0 + r, y0 + r, 180, 270)
    pts.append(pts[0])
    # walk the path, alternating dash/gap
    acc, on, target = 0.0, True, dash
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        seg_len = math.hypot(bx - ax, by - ay)
        if seg_len == 0:
            continue
        pos = 0.0
        while pos < seg_len:
            step = min(target - acc, seg_len - pos)
            if on:
                p0 = (ax + (bx - ax) * pos / seg_len, ay + (by - ay) * pos / seg_len)
                p1 = (ax + (bx - ax) * (pos + step) / seg_len, ay + (by - ay) * (pos + step) / seg_len)
                d.line([(p0[0] * ss, p0[1] * ss), (p1[0] * ss, p1[1] * ss)], fill=color, width=max(1, int(width * ss)))
            pos += step
            acc += step
            if acc >= target - 1e-6:
                acc, on = 0.0, not on
                target = dash if on else gap
    return big.resize((w, h), Image.LANCZOS)


# --- tiny SVG path flattener (M m L l H h V v A a Z z) for the eyedropper icon
def _svg_polylines(d):
    toks = re.findall(r"[a-zA-Z]|-?\d*\.?\d+(?:e-?\d+)?", d)
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    subs, cur = [], []

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v

    def arc(x0, y0, rx, ry, phi, fa, fs, x1, y1):
        if rx == 0 or ry == 0:
            return [(x1, y1)]
        phi = math.radians(phi)
        dx2, dy2 = (x0 - x1) / 2, (y0 - y1) / 2
        x1p = math.cos(phi) * dx2 + math.sin(phi) * dy2
        y1p = -math.sin(phi) * dx2 + math.cos(phi) * dy2
        lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
        if lam > 1:
            s = math.sqrt(lam); rx *= s; ry *= s
        num_ = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
        den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
        co = math.sqrt(max(0, num_ / den)) * (-1 if fa == fs else 1)
        cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
        cx = math.cos(phi) * cxp - math.sin(phi) * cyp + (x0 + x1) / 2
        cy = math.sin(phi) * cxp + math.cos(phi) * cyp + (y0 + y1) / 2
        ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)  # noqa: E731
        th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
        dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
        if not fs and dth > 0:
            dth -= 2 * math.pi
        elif fs and dth < 0:
            dth += 2 * math.pi
        out = []
        n = 24
        for k in range(1, n + 1):
            a = th1 + dth * k / n
            out.append((cx + rx * math.cos(a) * math.cos(phi) - ry * math.sin(a) * math.sin(phi),
                        cy + rx * math.cos(a) * math.sin(phi) + ry * math.sin(a) * math.cos(phi)))
        return out

    while i < len(toks):
        if re.match(r"[a-zA-Z]", toks[i]):
            cmd = toks[i]; i += 1
        c = cmd
        rel = c.islower()
        cu = c.upper()
        if cu == "Z":
            cur.append((sx, sy)); subs.append(cur); cur = []; x, y = sx, sy
            continue
        if cu == "M":
            nx, ny = num(), num()
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            if cur:
                subs.append(cur)
            cur = [(x, y)]; sx, sy = x, y
            cmd = "l" if rel else "L"
        elif cu == "L":
            nx, ny = num(), num()
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            cur.append((x, y))
        elif cu == "H":
            nx = num(); x = x + nx if rel else nx; cur.append((x, y))
        elif cu == "V":
            ny = num(); y = y + ny if rel else ny; cur.append((x, y))
        elif cu == "A":
            rx, ry, phi, fa, fs = num(), num(), num(), int(num()), int(num())
            nx, ny = num(), num()
            tx_, ty_ = (x + nx, y + ny) if rel else (nx, ny)
            cur.extend(arc(x, y, rx, ry, phi, fa, fs, tx_, ty_))
            x, y = tx_, ty_
    if cur:
        subs.append(cur)
    return subs


_PIPETTE = ["m2 22 1-1h3l9-9", "M3 21v-3l9-9",
            "m15 6 3.4-3.4a2.1 2.1 0 1 1 3 3L18 9l.4.4a2.1 2.1 0 1 1-3 3l-3.8-3.8a2.1 2.1 0 1 1 3-3z"]


def _pipette_icon(size_px, ss=4):
    """Lucide pipette, 2-unit white round stroke, no fill, on a 24-unit viewBox -> RGBA layer."""
    n = int(size_px * ss)
    big = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    k = n / 24.0
    wd = max(1, int(2 * k))
    for path in _PIPETTE:
        for poly in _svg_polylines(path):
            pts = [(px * k, py * k) for px, py in poly]
            d.line(pts, fill=(255, 255, 255, 255), width=wd, joint="curve")
            for px, py in pts[:: max(1, len(pts) // 40)] + [pts[0], pts[-1]]:
                d.ellipse((px - wd / 2, py - wd / 2, px + wd / 2, py + wd / 2), fill=(255, 255, 255, 255))
    return big.resize((int(size_px), int(size_px)), Image.LANCZOS)


# =========================================================================== A18
@effect("A18", "Giant captions", duration=4.6, texts=["GIANT", "captions."], outro_fade=0)
def giant_captions(img, t, ctx):
    """A small caption chip pops in, then becomes a stacked title block (sans word + serif italic word) that fades out.
    text0 = the heavy sans word (also the chip), text1 = the serif italic second line."""
    word, second = ctx.text(0, "GIANT"), ctx.text(1, "captions.")
    out = img.copy()

    # chip: left 34cqw top 72cqw, 800 8cqw/1, tracking -.02em, padding 1cqw 2.4cqw; pop .3s @.2s, gone at 1s
    if .2 <= t < 1.0:
        f = font("sans", cq(8), 800)
        tr = -.02 * cq(8)
        tw = text_w(word, f, tr)
        bw, bh = tw + cq(4.8), cq(8) + cq(2)
        box = rrect((int(bw), int(bh)), 0, _hex("#16332a"))
        lay = _tl(word, f, _hex("#ece8dc"), tr)
        paste(box, lay, (cq(2.4), cq(1) + _lh_off(f, cq(8))))
        p = _POP(seg(t, .2, .3))
        _xf_place(out, box, cq(34), cq(72), scale=lerp(.4, 1, p), opacity=clamp01(p))

    # banner: left 3cqw top 14cqw, padding 3 4 4, rotate(-1.2deg), origin 20% 90%, pop .55s @1s, vanish .3s @3.8s
    if t >= 1.0:
        def build():
            f1 = font("sans", cq(17), 800)
            f2 = font("serif", cq(17), 400, italic=True)
            t1, t2 = _tl(word, f1, _hex("#ece8dc"), -.03 * cq(17)), _tl(second, f2, _hex("#c8a95d"))
            lh = cq(17) * .9
            w = max(t1.width, t2.width) + cq(8)
            h = cq(3) + lh * 2 + cq(4)
            box = rrect((int(w), int(h)), 0, _hex("#16332a"))
            paste(box, t1, (cq(4), cq(3) + _lh_off(f1, lh)))
            paste(box, t2, (cq(4), cq(3) + lh + _lh_off(f2, lh)))
            return box
        box = ctx.cached("a18_banner", build)
        p = _POP(seg(t, 1.0, .55))
        op = clamp01(p) * (1 - EASE(seg(t, 3.8, .3)))
        _xf_place(out, box, cq(3), cq(14), origin=(.2, .9), scale=lerp(.3, 1, p), rot=-1.2, opacity=op)
    return out


# =========================================================================== A19
@effect("A19", "File drop", duration=4.6,
        texts=["A1C5E028-9919-490F-93DD-7E5F98782750.MP4", "0:25 · 29.4 MB · 1080×1920",
               "Drop raw footage", "0:25", " of raw footage"])
def file_drop(img, t, ctx):
    """A file card drops into a dashed drop panel, which swaps for a phone frame (your footage) with a callout.
    text0 = file name, text1 = file meta line, text2 = drop-zone hint, text3 = bold callout part, text4 = rest of callout."""
    out = img.copy()
    name, meta, hint = ctx.text(0), ctx.text(1), ctx.text(2)

    def build_panel():
        dw, dh = int(cq(62)), int(cq(84))
        dz = rrect((dw, dh), cq(3), _hex("#16332a"))
        paste(dz, _dashed_rrect((dw, dh), cq(2), cq(2), max(1, cq(.25)), cq(1.1), cq(.8), _hex("#ece8dc", 85)))
        # hint (download arrow + text); sits where the card lands, so the card covers it
        hf = font("sans", cq(2.6), 500)
        ht = _tl(hint, hf, _hex("#ece8dc", 150))
        paste(dz, ht, ((dw - ht.width) / 2, cq(42) - cq(1)))
        ar = ImageDraw.Draw(dz)
        cx, cy = dw / 2, cq(42) - cq(5.5)
        s = cq(1.6)
        col = _hex("#ece8dc", 150)
        ar.line([(cx, cy - s), (cx, cy + s * .6)], fill=col, width=max(2, int(cq(.35))))
        ar.line([(cx - s * .7, cy - s * .1), (cx, cy + s * .7), (cx + s * .7, cy - s * .1)], fill=col, width=max(2, int(cq(.35))))
        ar.line([(cx - s, cy + s * 1.2), (cx + s, cy + s * 1.2)], fill=col, width=max(2, int(cq(.35))))
        return dz

    def build_card():
        cw = int(cq(52))
        pad = cq(2.4)
        thumb_w, thumb_h = int(cq(10)), int(cq(12))
        nf = font("sans", cq(2.4), 700)
        mf = font("mono", cq(1.8), 500)
        avail = cw - pad * 2 - thumb_w - cq(2)
        # word-break:break-all
        lines, cur = [], ""
        for ch in name:
            if text_w(cur + ch, nf) <= avail:
                cur += ch
            else:
                lines.append(cur); cur = ch
        if cur:
            lines.append(cur)
        nh = cq(2.4) * 1.15
        text_h = nh * len(lines) + cq(.8) + (mf.getmetrics()[0] + mf.getmetrics()[1])
        ch_ = int(max(thumb_h, text_h) + pad * 2)
        card = rrect((cw, ch_), cq(2), (255, 255, 255, 255))
        th = _crop_frame(img_ref[0], .5, .33, .42, thumb_w, thumb_h)
        card_th = Image.new("RGBA", (thumb_w, thumb_h))
        card_th.paste(th.convert("RGBA"))
        m = rrect((thumb_w, thumb_h), cq(1)).getchannel("A")
        card_th.putalpha(m)
        card.alpha_composite(card_th, (int(pad), int((ch_ - thumb_h) / 2)))
        tx0 = pad + thumb_w + cq(2)
        y0 = (ch_ - text_h) / 2
        for k, ln in enumerate(lines):
            lay = _tl(ln, nf, _hex("#14211b"))
            paste(card, lay, (tx0, y0 + k * nh + _lh_off(nf, nh)))
        paste(card, _tl(meta, mf, _hex("#6b716e")), (tx0, y0 + nh * len(lines) + cq(.8)))
        return card

    img_ref = [img]
    panel = ctx.cached("a19_panel", build_panel)
    card = ctx.cached("a19_card_" + name + meta, build_card)

    # drop panel + card, fading together at 1.8s (.3s ease)
    pan_op = 1 - EASE(seg(t, 1.8, .3))
    if pan_op > 0:
        pl = panel.copy()
        # card is positioned inside the panel (left 5cqw, top 34cqw); fall .9s linear @.2s, 0%/100% opacity 1
        q = seg(t, .2, .9)
        if q < .6:
            ty = lerp(-60, 0, bezier(.55, 0, 1, .45)(q / .6)) * CQW
            rot = lerp(-6, 0, bezier(.55, 0, 1, .45)(q / .6))
        elif q < .75:
            ty, rot = lerp(0, -3, bezier(0, 0, .58, 1)((q - .6) / .15)) * CQW, 0
        else:
            ty, rot = lerp(-3, 0, (q - .75) / .25) * CQW, 0
        csh, off = _shadowed(card, cq(3), cq(1), 153)
        # draw into a panel-sized canvas with room for the card flying above the panel
        pad_top = int(cq(70))
        canvas = Image.new("RGBA", (pl.width, pl.height + pad_top), (0, 0, 0, 0))
        canvas.alpha_composite(pl, (0, pad_top))
        _xf_place(canvas, csh, cq(5), cq(34) + pad_top, rot=rot, ty=ty, off=(off, off))
        out.paste(with_opacity(canvas, pan_op), (int(cq(3)), int(cq(22) - pad_top)), with_opacity(canvas, pan_op))

    # phone frame with footage, pop .45s @1.9s
    if t >= 1.9:
        def build_phone():
            pw = int(cq(52))
            ph = int(round(pw * 16 / 9))
            bw = max(1, int(round(cq(.9))))
            frame = rrect((pw, ph), cq(5), _hex("#0e1a15"))
            inner = (pw - 2 * bw, ph - 2 * bw)
            vid = fit_cover(img_ref[0], inner[0], inner[1]).convert("RGBA")
            vid.putalpha(rrect(inner, max(1, cq(5) - bw)).getchannel("A"))
            frame.alpha_composite(vid, (bw, bw))
            rf = font("mono", cq(1.9), 700)
            rt = _tl("● REC", rf, (255, 255, 255, 255))
            bx = rrect((int(rt.width + cq(2.8)), int(rf.getmetrics()[0] + rf.getmetrics()[1] + cq(1.2))), cq(1), _hex("#16332a"))
            paste(bx, rt, (cq(1.4), cq(.6)))
            frame.alpha_composite(bx, (pw - bw - int(cq(2)) - bx.width, bw + int(cq(2))))
            return frame
        phone = build_phone()  # footage changes every frame, so no cache
        p = _POP_14(seg(t, 1.9, .45))
        _xf_place(out, phone, cq(8), cq(17), scale=lerp(.4, 1, p), opacity=clamp01(p))

    # callout pill: left 12cqw top 98cqw, rise .3s @2.4s
    if t >= 2.4:
        def build_cc():
            f_r, f_b = font("sans", cq(4), 500), font("sans", cq(4), 800)
            b = ctx.text(3, "0:25"); rest = ctx.text(4, " of raw footage")
            lb, lr = _tl(b, f_b, _hex("#16332a")), _tl(rest, f_r, _hex("#16332a"))
            lh = cq(4) * 1.2
            w, h = lb.width + lr.width + cq(4.8), lh + cq(2.4)
            pill = rrect((int(w), int(h)), cq(2.2), (255, 255, 255, 255))
            paste(pill, lb, (cq(2.4), cq(1.2) + _lh_off(f_b, lh)))
            paste(pill, lr, (cq(2.4) + lb.width, cq(1.2) + _lh_off(f_r, lh)))
            return pill
        pill = ctx.cached("a19_cc" + ctx.text(3) + ctx.text(4), build_cc)
        p = EASE(seg(t, 2.4, .3))
        paste(out, pill, (cq(12), cq(98) + cq(3) * (1 - p)), opacity=p)
    return out


_POP_14 = bezier(.2, 1.4, .4, 1)


# =========================================================================== A20
_SW = [("SHIRT", .50, .84, .90), ("WALL", .12, .22, 1.25), ("MAT", .15, .93, 1.60), ("CAP", .50, .27, 1.95), ("SKIN", .50, .38, 2.30)]


def _grade_params(p):
    return dict(saturate=lerp(1, .6, p), brightness=lerp(1, .78, p), contrast=lerp(1, 1.1, p))


def _grade_img(img, p):
    out = css_filter(img, **_grade_params(p))
    a = _color_blend(np.asarray(out, np.float32) / 255.0, _hex("#46667a"), .4 * p)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


@effect("A20", "Eyedropper grade", duration=5.2, texts=["SAMPLED", "GRADE", "SHIRT", "WALL", "MAT", "CAP", "SKIN"])
def eyedropper_grade(img, t, ctx):
    """Palette card slides in, an eyedropper samples five colours from the frame, then the shot regrades to a cool
    desaturated palette and the swatches update. text0/1 = card headings, text2-6 = the five swatch labels."""
    pg = EASE(seg(t, 3.1, 1.0))
    out = _grade_img(img, pg) if pg > 0 else img.copy()

    # sampled colours come from the actual frame; after-colours are the same colours pushed through the grade
    def sample():
        res = []
        for k, (lab, cx, cy, d) in enumerate(_SW):
            a = _mean_color(img, cx, cy)
            b = _grade_img(Image.new("RGB", (8, 8), a), 1.0).getpixel((0, 0))
            res.append((a, b))
        return res
    cols = ctx.cached("a20_cols", sample)

    # card: left 3cqw right 3cqw top 118cqw, slide in .5s @.2s from translateX(110%)
    def build_card():
        cw = int(cq(94))
        hf = font("mono", cq(1.9), 500)
        hlh = hf.getmetrics()[0] + hf.getmetrics()[1]
        ch_ = int(cq(3) + hlh + cq(2.4) + cq(7) * 2 + cq(2.4) + cq(3))
        return rrect((cw, ch_), cq(3), _hex("#ece8dc")), hlh
    base_card, hlh = ctx.cached("a20_base", build_card)
    card = base_card.copy()
    hf = font("mono", cq(1.9), 500)
    tr = .16 * cq(1.9)
    paste(card, _tl(ctx.text(0, "SAMPLED"), hf, _hex("#16332a", 153), tr), (cq(3), cq(3)))
    grade_t = _tl(ctx.text(1, "GRADE"), hf, _hex("#16332a", 153), tr)
    dot = cq(1.6)
    dots_w = 3 * (cq(.6) + dot)
    gx = card.width - cq(3) - (grade_t.width + hf.getlength(" ") + tr + dots_w)
    paste(card, grade_t, (gx, cq(3)))
    dx = gx + grade_t.width + hf.getlength(" ") + tr
    on = t >= 3.1
    base_y = cq(3) + hf.getmetrics()[0]
    for _ in range(3):
        dx += cq(.6)
        paste(card, ellipse((int(dot), int(dot)), _hex("#16332a") if on else _hex("#16332a", 51)), (dx, base_y - dot))
        dx += dot

    # swatch grid
    cwid = (cq(94) - cq(6) - 2 * cq(1.4)) / 3
    row0 = cq(3) + hlh + cq(2.4)
    for k, (lab, cx, cy, d) in enumerate(_SW):
        c, r = k % 3, k // 3
        sx, sy = cq(3) + c * (cwid + cq(1.4)), row0 + r * (cq(7) + cq(2.4))
        p = _POP(seg(t, d, .3))
        if p <= 0 and t < d:
            continue
        a, b = cols[k]
        q = EASE(seg(t, 3.1, .6))
        col = tuple(int(lerp(a[i], b[i], q)) for i in range(3)) + (255,)
        item = Image.new("RGBA", (int(cwid), int(cq(7))), (0, 0, 0, 0))
        sw = rrect((int(cq(7)), int(cq(7))), cq(1.4), col, _hex("#16332a", 34), max(1, int(cq(.2))))
        item.alpha_composite(sw, (0, 0))
        hx = "#%02X%02X%02X" % (b if t >= 3.1 else a)
        item.alpha_composite(_tl(hx, font("mono", cq(2.2), 700), _hex("#16332a")), (int(cq(7) + cq(1.4)), int(cq(.6))))
        item.alpha_composite(_tl(ctx.text(2 + k, lab), font("mono", cq(1.6), 500), _hex("#16332a", 153), .1 * cq(1.6)),
                             (int(cq(7) + cq(1.4)), int(cq(4.2))))
        _xf_place(card, item, sx, sy, scale=lerp(.4, 1, p), opacity=clamp01(p))

    slide = bezier(.2, .8, .2, 1)(seg(t, .2, .5))
    csh, off = _shadowed(card, cq(4), cq(1), 153)
    _xf_place(out, csh, cq(3), cq(118), tx=lerp(1.1 * card.width, 0, slide), off=(off, off))

    # sampled-colour dot (left 38cqw top 106cqw) pops @1.5s, vanishes @3.1s
    p = _POP(seg(t, 1.5, .3))
    op = clamp01(p) * (1 - EASE(seg(t, 3.1, .3)))
    if op > 0:
        fpc = cols[4][0]  # the SKIN sample, like the preview's pink dot
        dsz = int(cq(8))
        dotl = ellipse((dsz, dsz), fpc + (255,), (255, 255, 255, 255), max(1, int(cq(.4))))
        _xf_place(out, dotl, cq(38), cq(106), scale=lerp(.4, 1, p), opacity=op)

    # eyedropper icon: 9cqw, eym 3s ease-in-out @.5s
    q = seg(t, .5, 3.0)
    ex = keyframes(q, [(0, 70), (.35, 46), (.65, 30), (1, 30)], EASE_IN_OUT)
    ey = keyframes(q, [(0, 90), (.35, 134), (.65, 150), (1, 150)], EASE_IN_OUT)
    eo = keyframes(q, [(0, 0), (.10, 1), (.65, 1), (1, 0)], EASE_IN_OUT)
    if eo > 0:
        icon = ctx.cached("a20_icon", lambda: _pipette_icon(cq(9)))
        ish, off = _shadowed(icon, cq(.6), cq(.3), 170)
        paste(out, ish, (cq(ex) - off, cq(ey) - off), opacity=eo)
    return out


# =========================================================================== B01
_ORB = [("#c9a07a", "#5a4636", .5, .33), ("#7f95b0", "#23303f", .30, .36), ("#a8b08a", "#3b4430", .66, .30),
        ("#c98a8a", "#4a2a2a", .44, .42), ("#9a8fc0", "#2b2540", .58, .38)]


def _alt(s, period=2.0):
    """Progress 0..1 of an infinite alternate animation of `period` seconds at local time s (s may be negative-shifted)."""
    it, u = divmod(s / period, 1.0)
    return u if int(it) % 2 == 0 else 1 - u


@effect("B01", "Orbit", duration=4.6, texts=["and you can get the", "cool girl"], needs_mask=True)
def orbit(img, t, ctx):
    """Five clip cards orbit the speaker, passing behind and in front, with a serif caption on top.
    text0 = small lead-in line, text1 = big serif italic words. Needs a subject matte."""
    base = css_filter(img, saturate=.8, brightness=.95)

    def build_cards():
        cards = []
        cw, chh = int(cq(14)), int(cq(23))
        for k, (c0, c1, cx, cy) in enumerate(_ORB):
            g = gradient((cw, chh), _hex(c0), _hex(c1), 160)
            card = Image.new("RGBA", (cw, chh))
            card.alpha_composite(g)
            card_rgb = card.convert("RGB")
            card = Image.blend(card_rgb, _crop_frame(img_ref[0], cx, cy, .55, cw, chh), .55).convert("RGBA")
            bw = max(1, int(cq(.5)))
            fr = rrect((cw, chh), cq(2), (0, 0, 0, 0), (255, 255, 255, 255), bw)
            m = rrect((cw, chh), cq(2)).getchannel("A")
            card.putalpha(m)
            card.alpha_composite(fr)
            dsz = int(cq(5))
            card.alpha_composite(ellipse((dsz, dsz), (255, 255, 255, 102)), ((cw - dsz) // 2, (chh - dsz) // 2))
            sh, pad = _shadowed(card, cq(3), cq(1), 153)
            cards.append((sh, pad))
        return cards
    img_ref = [img]
    cards = build_cards()  # cheap (5 small layers); rebuilt per frame so crops track the live footage

    items = []
    for k, (sh, pad) in enumerate(cards):
        sx = t + .8 * k
        sy = t + .8 * k + 1
        px, py = EASE_IN_OUT(_alt(sx)), EASE_IN_OUT(_alt(sy))
        tx = lerp(-34, 34, px)
        mt = lerp(-14, 14, py)
        sc = lerp(.72, 1.1, py)
        z = int(round(lerp(1, 3, py)))
        items.append((z, k, sh, pad, 50 + tx - 7, 108 + mt, sc))
    items.sort(key=lambda r: (r[0], r[1]))

    out = base
    for z, k, sh, pad, lx, ly, sc in items:
        if z <= 2:
            _xf_place(out, sh, cq(lx), cq(ly), scale=sc, off=(pad, pad))
    out = Image.composite(img, out, ctx.mask())
    for z, k, sh, pad, lx, ly, sc in items:
        if z > 2:
            _xf_place(out, sh, cq(lx), cq(ly), scale=sc, off=(pad, pad))

    # caption: top 42cqw, rise .6s @.2s
    p = EASE(seg(t, .2, .6))
    _caption(out, [(ctx.text(0, "and you can get the"), font("sans", cq(3.6), 600), (255, 255, 255, 255), 0, None, cq(.75)),
                   (ctx.text(1, "cool girl"), font("serif", cq(14), 400, italic=True), _hex("#e8d28a"), cq(14), None, cq(1))],
             cq(42) + cq(3) * (1 - p), p)
    return out


def _caption(out, lines, top, opacity, blur_sigma=0.0):
    """Centred stack of text lines (text, font, fill, line_height_px or 0 for `normal`, tracking, shadow_sigma) with a
    soft 0 0 blur #0008 shadow, starting at `top` px."""
    y = top
    for txt, fnt, fill, lh, tr, sig in lines:
        asc, desc = fnt.getmetrics()
        lh = lh or (asc + desc)
        lay = text_layer(txt, fnt, fill, tr or 0.0, pad=0, shadow=(0, 0, sig, (0, 0, 0, 136)))
        m = int(abs(0) + abs(0) + sig * 3)
        tw = text_w(txt, fnt, tr or 0.0)
        lay = blur(lay, blur_sigma) if blur_sigma else lay
        paste(out, lay, ((W - tw) / 2 - m, y + _lh_off(fnt, lh) - m), opacity=opacity)
        y += lh
    return out


# =========================================================================== B02
@effect("B02", "Couch wall", duration=3.8, texts=["selling a", "course"], needs_mask=True)
def couch_wall(img, t, ctx):
    """A wall of video tiles pops in behind the speaker, then a big caption blurs in.
    text0 = small lead-in, text1 = big heavy word. Needs a subject matte."""
    out = css_filter(img, brightness=.8)
    tw_ = (92 - 3 * 1.4) / 4
    th_ = tw_ * 12 / 9
    wd, ht = int(cq(tw_)), int(cq(th_))
    tint_pairs = [("#6c7a86", "#2c3238"), ("#9a8a74", "#3a3128"), ("#6f8fb8", "#223046")]
    crops = [(.5, .33), (.35, .30), (.62, .36), (.45, .28), (.55, .40), (.30, .42), (.68, .30), (.5, .45), (.4, .35),
             (.6, .27), (.33, .33), (.57, .38)]
    for i in range(12):
        r, c = divmod(i, 4)
        p = _POP(seg(t, .2 + i * .07, .35))
        if t < .2 + i * .07:
            continue
        n = i + 1
        pair = tint_pairs[2] if n % 4 == 3 else tint_pairs[1] if n % 3 == 2 else tint_pairs[0]
        tile = Image.new("RGBA", (wd, ht))
        g = gradient((wd, ht), _hex(pair[0]), _hex(pair[1]), 160).convert("RGB")
        cx, cy = crops[i]
        tile = Image.blend(g, _crop_frame(img, cx, cy, .42, wd, ht), .55).convert("RGBA")
        tile.putalpha(rrect((wd, ht), cq(1)).getchannel("A"))
        bar = rrect((int(wd * .76), max(2, int(ht * .08))), cq(1), (255, 255, 255, 153))
        tile.alpha_composite(bar, (int(wd * .12), int(ht * .80 - bar.height)))
        _xf_place(out, tile, cq(4) + c * (tw_ + 1.4) * CQW, cq(10) + r * (th_ + 1.4) * CQW, scale=lerp(.4, 1, p), opacity=clamp01(p))
    out = Image.composite(img, out, ctx.mask())

    q = EASE(seg(t, 1.0, .6))
    if q > 0:
        _caption(out, [(ctx.text(0, "selling a"), font("sans", cq(5), 700), (255, 255, 255, 255), 0, None, cq(.75)),
                       (ctx.text(1, "course"), font("sans", cq(14), 800), (255, 255, 255, 255), cq(14), -.02 * cq(14), cq(1))],
                 cq(98), q, blur_sigma=cq(1.6) * (1 - q))
    return out
