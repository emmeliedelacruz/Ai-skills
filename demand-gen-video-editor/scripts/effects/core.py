"""Shared toolkit for the Video Effect Library renderers.

Every effect is a pure function of time:  fx(img, t, ctx) -> PIL.Image (RGB, 1080x1920)

  img  the source frame (already scaled/cropped to 1080x1920)
  t    seconds since the effect started (0 .. effect duration)
  ctx  Ctx: texts, subject matte, caches, helpers

Units: the HTML previews are laid out in `cqw` (1cqw = 1% of frame width). Use cq(n)
to convert, so numbers copied from the preview CSS (left:4cqw, font:19cqw ...) carry
over unchanged. The frame is 100cqw wide and 177.78cqw tall.

Register an effect with @effect("A05", "Grade slider", duration=5.0, texts=[...]).
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1080, 1920
CQW = W / 100.0
HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"


def cq(v: float) -> float:
    """Preview units (cqw) -> pixels."""
    return v * CQW


# --------------------------------------------------------------------------- easing
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def seg(t: float, t0: float, dur: float) -> float:
    """Progress 0..1 of a segment that starts at t0 and lasts dur seconds."""
    return clamp01((t - t0) / dur) if dur > 0 else (1.0 if t >= t0 else 0.0)


def lerp(a: float, b: float, p: float) -> float:
    return a + (b - a) * p


def bezier(x1: float, y1: float, x2: float, y2: float):
    """CSS cubic-bezier(x1,y1,x2,y2) as a function p -> eased p. Copy curves straight from the CSS."""
    def f(p: float) -> float:
        p = clamp01(p)
        lo, hi = 0.0, 1.0
        u = p
        for _ in range(30):
            x = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u ** 2 * x2 + u ** 3
            if abs(x - p) < 1e-5:
                break
            if x < p:
                lo = u
            else:
                hi = u
            u = (lo + hi) / 2
        return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3
    return f


EASE = bezier(.25, .1, .25, 1)
EASE_IN = bezier(.42, 0, 1, 1)
EASE_OUT = bezier(0, 0, .58, 1)
EASE_IN_OUT = bezier(.42, 0, .58, 1)
SPRING = bezier(.2, 1.6, .4, 1)  # overshoot used by the preview "pop" animations


def linear(p: float) -> float:
    return clamp01(p)


def steps(p: float, n: int) -> float:
    """CSS steps(n, end)."""
    return math.floor(clamp01(p) * n) / n if p < 1 else 1.0


def keyframes(t: float, frames: list[tuple[float, float]], ease=linear) -> float:
    """Piecewise interpolation. frames = [(time, value), ...] sorted by time; ease applies per span."""
    if t <= frames[0][0]:
        return frames[0][1]
    for (t0, v0), (t1, v1) in zip(frames, frames[1:]):
        if t <= t1:
            return lerp(v0, v1, ease(seg(t, t0, t1 - t0)))
    return frames[-1][1]


# --------------------------------------------------------------------------- fonts
_FONT_CACHE: dict = {}

_SYSTEM = {
    "sans": ["/usr/share/fonts/opentype/inter/Inter-{w}.otf", "/usr/share/fonts/truetype/liberation/LiberationSans-{b}.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans{bb}.ttf"],
    "serif": ["/usr/share/fonts/truetype/liberation/LiberationSerif-{i}.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
    "mono": ["/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{w}.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono{bb}.ttf"],
    "courier": ["/usr/share/fonts/truetype/liberation/LiberationMono-{b}.ttf"],
    "hand": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"],
}
_WNAME = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold",
          700: "Bold", 800: "ExtraBold", 900: "Black"}


def font(family: str, size: float, weight: int = 700, italic: bool = False) -> ImageFont.FreeTypeFont:
    """family: sans (Inter Tight) | serif (Instrument Serif) | hand (Caveat) | mono (JetBrains Mono) | courier (Courier Prime).

    Prefers the Google Fonts in ./fonts (run fetch_fonts.py), then falls back to system fonts.
    """
    key = (family, round(size), weight, italic)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    f = None
    size_i = max(1, int(round(size)))
    try:
        if family == "sans":
            p = FONT_DIR / ("InterTight-Italic[wght].ttf" if italic else "InterTight[wght].ttf")
            f = ImageFont.truetype(str(p), size_i)
            f.set_variation_by_axes([weight])
        elif family == "serif":
            p = FONT_DIR / ("InstrumentSerif-Italic.ttf" if italic else "InstrumentSerif-Regular.ttf")
            f = ImageFont.truetype(str(p), size_i)
        elif family == "hand":
            f = ImageFont.truetype(str(FONT_DIR / "Caveat[wght].ttf"), size_i)
            f.set_variation_by_axes([max(400, min(700, weight))])
        elif family == "courier":
            f = ImageFont.truetype(str(FONT_DIR / ("CourierPrime-Bold.ttf" if weight >= 600 else "CourierPrime-Regular.ttf")), size_i)
        elif family == "mono":
            f = ImageFont.truetype(str(FONT_DIR / "JetBrainsMono[wght].ttf"), size_i)
            f.set_variation_by_axes([max(100, min(800, weight))])
    except Exception:  # noqa: BLE001
        f = None
    if f is None:
        wn = _WNAME.get(weight, "Bold")
        for tpl in _SYSTEM.get(family, _SYSTEM["sans"]):
            path = tpl.format(w=wn, b="Bold" if weight >= 600 else "Regular", bb="-Bold" if weight >= 600 else "",
                              i="Italic" if italic else "Regular")
            if os.path.exists(path):
                try:
                    f = ImageFont.truetype(path, size_i)
                    break
                except Exception:  # noqa: BLE001
                    continue
    if f is None:
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf" if weight >= 600 else "DejaVuSans.ttf", size_i)
        except Exception:  # noqa: BLE001
            f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def text_w(txt: str, fnt, tracking: float = 0.0) -> float:
    """Advance width in px. tracking is in px per glyph (CSS letter-spacing)."""
    return sum(fnt.getlength(c) + tracking for c in txt) if tracking else fnt.getlength(txt)


def text_layer(txt: str, fnt, fill=(255, 255, 255, 255), tracking: float = 0.0, stroke: int = 0,
               stroke_fill=(0, 0, 0, 255), pad: int = 4, shadow: tuple | None = None) -> Image.Image:
    """Render one line of text on a transparent RGBA layer, tight to the ink plus pad.

    shadow = (dx, dy, blur, (r,g,b,a)) draws a soft drop shadow like CSS text-shadow.
    """
    asc, desc = fnt.getmetrics()
    w = int(math.ceil(text_w(txt, fnt, tracking))) + pad * 2 + stroke * 2
    h = asc + desc + pad * 2 + stroke * 2
    extra = 0
    if shadow:
        extra = int(abs(shadow[0]) + abs(shadow[1]) + shadow[2] * 3)
    lay = Image.new("RGBA", (w + extra * 2, h + extra * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ox, oy = pad + stroke + extra, pad + stroke + extra
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        _draw_text(sd, (ox + shadow[0], oy + shadow[1]), txt, fnt, shadow[3], tracking)
        sh = sh.filter(ImageFilter.GaussianBlur(shadow[2]))
        lay = Image.alpha_composite(lay, sh)
        d = ImageDraw.Draw(lay)
    _draw_text(d, (ox, oy), txt, fnt, fill, tracking, stroke, stroke_fill)
    return lay


def _draw_text(d, xy, txt, fnt, fill, tracking=0.0, stroke=0, stroke_fill=(0, 0, 0, 255)):
    x, y = xy
    if not tracking:
        d.text((x, y), txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        return
    for c in txt:
        d.text((x, y), c, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += fnt.getlength(c) + tracking


def wrap(txt: str, fnt, max_w: float, tracking: float = 0.0) -> list[str]:
    lines, cur = [], ""
    for word in txt.split():
        trial = (cur + " " + word).strip()
        if text_w(trial, fnt, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------- shapes
def rgba(w: int, h: int, color=(0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (int(w), int(h)), color)


def rrect(size, radius: float, fill=(255, 255, 255, 255), outline=None, width: int = 0, ss: int = 3) -> Image.Image:
    """Anti-aliased rounded rectangle layer (RGBA)."""
    w, h = int(size[0]), int(size[1])
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=radius * ss, fill=fill,
                        outline=outline, width=int(width * ss))
    return big.resize((w, h), Image.LANCZOS)


def ellipse(size, fill=(255, 255, 255, 255), outline=None, width: int = 0, ss: int = 3) -> Image.Image:
    w, h = int(size[0]), int(size[1])
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse((0, 0, w * ss - 1, h * ss - 1), fill=fill, outline=outline, width=int(width * ss))
    return big.resize((w, h), Image.LANCZOS)


def vgradient(size, top, bottom) -> Image.Image:
    """Vertical linear gradient, RGBA. top/bottom are (r,g,b[,a])."""
    w, h = int(size[0]), int(size[1])
    top = np.array(list(top) + [255] * (4 - len(top)), float)
    bottom = np.array(list(bottom) + [255] * (4 - len(bottom)), float)
    t = np.linspace(0, 1, h)[:, None, None]
    arr = (top * (1 - t) + bottom * t).astype(np.uint8)
    arr = np.broadcast_to(arr, (h, w, 4)).copy()
    return Image.fromarray(arr, "RGBA")


def gradient(size, c0, c1, angle_deg: float = 180) -> Image.Image:
    """Linear gradient at a CSS angle (180 = top->bottom, 90 = left->right), RGBA."""
    w, h = int(size[0]), int(size[1])
    a = math.radians(angle_deg)
    dx, dy = math.sin(a), -math.cos(a)
    ys, xs = np.mgrid[0:h, 0:w]
    proj = (xs - w / 2) * dx + (ys - h / 2) * dy
    span = abs(w * dx) + abs(h * dy)
    t = np.clip(proj / span + 0.5, 0, 1)[..., None]
    c0 = np.array(list(c0) + [255] * (4 - len(c0)), float)
    c1 = np.array(list(c1) + [255] * (4 - len(c1)), float)
    return Image.fromarray((c0 * (1 - t) + c1 * t).astype(np.uint8), "RGBA")


def radial(size, inner, outer, center=(0.5, 0.5), radius: float = 0.75) -> Image.Image:
    w, h = int(size[0]), int(size[1])
    ys, xs = np.mgrid[0:h, 0:w]
    d = np.hypot((xs - w * center[0]) / (w * radius), (ys - h * center[1]) / (w * radius))
    t = np.clip(d, 0, 1)[..., None]
    c0 = np.array(list(inner) + [255] * (4 - len(inner)), float)
    c1 = np.array(list(outer) + [255] * (4 - len(outer)), float)
    return Image.fromarray((c0 * (1 - t) + c1 * t).astype(np.uint8), "RGBA")


def solid(color, size=(W, H)) -> Image.Image:
    c = tuple(color) + (255,) * (4 - len(color))
    return Image.new("RGBA", (int(size[0]), int(size[1])), c)


# --------------------------------------------------------------------------- compositing
def with_opacity(layer: Image.Image, opacity: float) -> Image.Image:
    if opacity >= 0.999:
        return layer
    layer = layer.convert("RGBA")
    a = layer.getchannel("A").point(lambda v: int(v * max(0.0, opacity)))
    out = layer.copy()
    out.putalpha(a)
    return out


def paste(base: Image.Image, layer: Image.Image, xy=(0, 0), opacity: float = 1.0) -> Image.Image:
    """Alpha-composite layer onto base at xy (top-left). Mutates and returns base. Clips off-canvas safely."""
    if opacity <= 0.001:
        return base
    layer = with_opacity(layer.convert("RGBA"), opacity)
    base.paste(layer, (int(round(xy[0])), int(round(xy[1]))), layer)
    return base


def place(base: Image.Image, layer: Image.Image, cx: float, cy: float, scale: float = 1.0, rot: float = 0.0,
          opacity: float = 1.0, resample=Image.BICUBIC) -> Image.Image:
    """Paste layer centred on (cx, cy) after scaling and rotating (degrees, CSS clockwise-positive)."""
    if scale <= 0.001 or opacity <= 0.001:
        return base
    lay = layer.convert("RGBA")
    if abs(scale - 1) > 1e-3:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), resample)
    if abs(rot) > 1e-3:
        lay = lay.rotate(-rot, resample=Image.BICUBIC, expand=True)
    return paste(base, lay, (cx - lay.width / 2, cy - lay.height / 2), opacity)


def over_rgba(base: Image.Image, layer: Image.Image) -> Image.Image:
    """Full-canvas RGBA overlay on an RGB base -> new RGB image."""
    out = base.convert("RGBA")
    out.alpha_composite(layer.convert("RGBA"))
    return out.convert("RGB")


def drop_shadow(layer: Image.Image, blur: float = 12, offset=(0, 8), color=(0, 0, 0, 120)) -> Image.Image:
    """Return layer with a soft shadow baked under it (canvas grows to fit)."""
    pad = int(blur * 3 + max(abs(offset[0]), abs(offset[1])))
    out = Image.new("RGBA", (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, color[:3] + (0,))
    alpha = Image.new("L", out.size, 0)
    alpha.paste(layer.getchannel("A"), (pad + offset[0], pad + offset[1]))
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
    alpha = alpha.point(lambda v: int(v * color[3] / 255))
    sh.putalpha(alpha)
    out = Image.alpha_composite(out, sh)
    out.alpha_composite(layer, (pad, pad))
    return out


def mask_paste(base: Image.Image, top: Image.Image, mask: Image.Image) -> Image.Image:
    """Composite `top` over `base` where mask (L, 255 = show top) is set."""
    return Image.composite(top.convert("RGB"), base.convert("RGB"), mask.convert("L"))


# --------------------------------------------------------------------------- footage ops
def zoom(img: Image.Image, scale: float, cx: float = 0.5, cy: float = 0.5, dx: float = 0, dy: float = 0) -> Image.Image:
    """Scale the frame about (cx, cy) in 0..1 coordinates, keeping the frame size. dx/dy shift in px after zoom."""
    if abs(scale - 1) < 1e-4 and not dx and not dy:
        return img
    w, h = img.size
    # output(x,y) = input( (x - ox)/scale + ox ) with ox = cx*w
    ox, oy = cx * w, cy * h
    a = 1.0 / scale
    c = ox - ox * a - dx * a
    f = oy - oy * a - dy * a
    return img.transform((w, h), Image.AFFINE, (a, 0, c, 0, a, f), resample=Image.BICUBIC)


def blur(img: Image.Image, radius: float) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius)) if radius > 0.3 else img


def adjust(img: Image.Image, brightness: float = 1.0, contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    return img


def grayscale(img: Image.Image, contrast: float = 1.0) -> Image.Image:
    g = img.convert("L").convert("RGB")
    return ImageEnhance.Contrast(g).enhance(contrast) if contrast != 1.0 else g


def tint(img: Image.Image, color, amount: float) -> Image.Image:
    """Mix a flat colour over the image (amount 0..1)."""
    return Image.blend(img.convert("RGB"), Image.new("RGB", img.size, tuple(color[:3])), clamp01(amount))


def sepia(img: Image.Image, amount: float = 1.0) -> Image.Image:
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    m = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]], dtype=np.float32)
    s = np.clip(a @ m.T, 0, 255)
    out = a * (1 - amount) + s * amount
    return Image.fromarray(out.astype(np.uint8))


def vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    w, h = img.size
    ys, xs = np.mgrid[0:h, 0:w]
    d = np.hypot((xs - w / 2) / (w / 2), (ys - h / 2) / (h / 2)) / math.sqrt(2)
    f = 1 - strength * np.clip(d, 0, 1) ** 2
    a = np.asarray(img, dtype=np.float32) * f[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def css_filter(img: Image.Image, brightness: float = 1.0, saturate: float = 1.0, sepia_amt: float = 0.0,
               contrast: float = 1.0, grayscale_amt: float = 0.0, hue_deg: float = 0.0) -> Image.Image:
    """CSS filter() chain in the CSS order: brightness, saturate, sepia, contrast, grayscale. Copy values from the preview CSS."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    a = a * brightness
    if saturate != 1.0:
        g = (a * np.array([.2126, .7152, .0722], np.float32)).sum(-1, keepdims=True)
        a = g + (a - g) * saturate
    if sepia_amt:
        m = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]], np.float32)
        s = a @ m.T
        a = a * (1 - sepia_amt) + s * sepia_amt
    if contrast != 1.0:
        a = (a - 0.5) * contrast + 0.5
    if grayscale_amt:
        g = (a * np.array([.2126, .7152, .0722], np.float32)).sum(-1, keepdims=True)
        a = a * (1 - grayscale_amt) + g * grayscale_amt
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def grain(img: Image.Image, amount: float = 0.08, seed: int = 0) -> Image.Image:
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 255 * amount, (img.height, img.width, 1)).astype(np.float32)
    a = np.asarray(img.convert("RGB"), dtype=np.float32) + n
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Scale to cover w x h, centre crop."""
    s = max(w / img.width, h / img.height)
    r = img.resize((max(w, int(round(img.width * s))), max(h, int(round(img.height * s)))), Image.BICUBIC)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def round_clip(img: Image.Image, radius: float) -> Image.Image:
    """Clip an RGB image to rounded corners -> RGBA."""
    out = img.convert("RGBA")
    m = rrect(img.size, radius, (255, 255, 255, 255)).getchannel("A")
    out.putalpha(m)
    return out


def perspective_coeffs(src_pts, dst_pts):
    """Coefficients for Image.transform(..., Image.PERSPECTIVE): maps dst -> src. Points are 4 (x, y) corners."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp_quad(layer: Image.Image, dst_pts, out_size=(W, H)) -> Image.Image:
    """Warp an RGBA layer so its corners (TL, TR, BR, BL) land on dst_pts (full-canvas RGBA out)."""
    w, h = layer.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    co = perspective_coeffs(src, dst_pts)
    return layer.transform(out_size, Image.PERSPECTIVE, co, resample=Image.BICUBIC)


# --------------------------------------------------------------------------- context
class Ctx:
    """Per-render state handed to every effect."""

    def __init__(self, texts: list[str], fps: float, duration: float, mask_reader=None, seed: int = 7):
        self.texts = texts
        self.fps = fps
        self.duration = duration
        self.w, self.h = W, H
        self._mask_reader = mask_reader
        self.has_mask = mask_reader is not None
        self._cache: dict = {}
        self.rng = np.random.default_rng(seed)
        self.t_abs = 0.0   # seconds since the start of the clip (not the effect)
        self.frame_idx = 0

    def text(self, i: int, default: str = "") -> str:
        return self.texts[i] if i < len(self.texts) and self.texts[i] != "" else default

    def cached(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def mask(self, t_abs: float | None = None) -> Image.Image:
        """Subject matte, mode L, 255 = subject. Uses the supplied --mask video, else a soft centre-column
        stand-in (good enough to preview; supply a real matte for production)."""
        if self._mask_reader is not None:
            return self._mask_reader(self.t_abs if t_abs is None else t_abs)
        return self.cached("fallback_mask", self._fallback_mask)

    def _fallback_mask(self) -> Image.Image:
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.ellipse((W * .30, H * .24, W * .70, H * .52), fill=255)                  # head
        d.rounded_rectangle((W * .12, H * .46, W * .88, H * 1.05), radius=W * .18, fill=255)  # torso
        return m.filter(ImageFilter.GaussianBlur(6))


# --------------------------------------------------------------------------- registry
EFFECTS: dict = {}


class EffectSpec:
    def __init__(self, id, name, fn, duration, texts, needs_mask, outro_fade):
        self.id, self.name, self.fn, self.duration, self.texts = id, name, fn, duration, texts
        self.needs_mask, self.outro_fade = needs_mask, outro_fade


def effect(id: str, name: str, duration: float, texts: list[str] | None = None, needs_mask: bool = False,
           outro_fade: float = 0.25):
    """Register fn(img, t, ctx) -> Image.

    duration     effect length in seconds (the preview loop length is a good default)
    texts        default copy slots, read with ctx.text(i, default)
    needs_mask   True if the effect cuts out the subject (ctx.mask())
    outro_fade   the renderer crossfades back to the untouched footage over the last N seconds so the
                 effect never pops off; set 0 for effects that already end on clean footage
    """
    def deco(fn):
        EFFECTS[id] = EffectSpec(id, name, fn, duration, texts or [], needs_mask, outro_fade)
        return fn
    return deco
