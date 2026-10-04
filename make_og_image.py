"""Generate the Open Graph / social share card for Global Photoshoots.

Facebook, LinkedIn, WhatsApp and X all reject SVG for og:image, so the share
card has to be a real PNG. Run this once (or after editing the copy below) to
regenerate assets/og-cover.png:

    python make_og_image.py
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG = (7, 9, 14)
CYAN = (56, 189, 248)
VIOLET = (139, 92, 246)
WHITE = (255, 255, 255)
SLATE = (148, 163, 184)

FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu", "/System/Library/Fonts"]


def font(candidates, size):
    for name in candidates:
        for d in FONT_DIRS:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


BOLD = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "Helvetica.ttc"]
REG = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def diagonal_gradient(size, c1, c2):
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    denom = float((w - 1) + (h - 1)) or 1.0
    for y in range(h):
        for x in range(w):
            px[x, y] = lerp(c1, c2, (x + y) / denom)
    return img


def radial_glow(size, center, radius, color, strength=0.55):
    """Soft radial light blob composited in screen-ish fashion."""
    w, h = size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        val = int(255 * strength * (1 - t) ** 1.6)
        d.ellipse(
            [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
            fill=val,
        )
    layer = layer.filter(ImageFilter.GaussianBlur(60))
    tint = Image.new("RGB", (w, h), color)
    return tint, layer


def text(draw, xy, s, f, fill, anchor="la", spacing=8):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor, spacing=spacing)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "assets", "og-cover.png")

    base = Image.new("RGB", (W, H), BG)

    # Two coloured glows for depth, composited with screen blending.
    glows = [
        ((int(W * 0.14), int(H * 0.22)), int(W * 0.46), CYAN),
        ((int(W * 0.88), int(H * 0.86)), int(W * 0.44), VIOLET),
    ]
    for center, radius, color in glows:
        tint, mask = radial_glow((W, H), center, radius, color)
        base = Image.composite(
            Image.blend(base, tint, 0.85), base, mask
        )

    # Faint grid, matching the site's background texture
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 64):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 7), width=1)
    for y in range(0, H, 64):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 7), width=1)
    base = Image.alpha_composite(base.convert("RGBA"), grid).convert("RGB")

    d = ImageDraw.Draw(base)

    # Accent bar
    d.rounded_rectangle([88, 92, 88 + 96, 100], radius=4, fill=CYAN)

    f_eyebrow = font(REG, 25)
    f_h1 = font(BOLD, 74)
    f_h2 = font(BOLD, 74)
    f_body = font(REG, 30)
    f_pill = font(BOLD, 25)
    f_foot = font(REG, 24)

    text(d, (88, 132), "GLOBAL PHOTOSHOOTS", f_eyebrow, CYAN)

    text(d, (88, 186), "Commercial AI", f_h1, WHITE)
    text(d, (88, 268), "Photoshoots & Video", f_h2, WHITE)

    text(
        d,
        (88, 386),
        "8K packshots  ·  lookbooks  ·  cinematic reels",
        f_body,
        SLATE,
    )
    text(
        d,
        (88, 432),
        "Delivered in 24–48 hours.  Full commercial rights.",
        f_body,
        SLATE,
    )

    # Offer pills
    px = 88
    for label in ("From $249", "24–48h delivery", "100% IP transfer"):
        pw = int(d.textlength(label, font=f_pill)) + 52
        d.rounded_rectangle([px, 508, px + pw, 558], radius=25, fill=(16, 20, 32), outline=(94, 108, 132), width=2)
        text(d, (px + 26, 533), label, f_pill, WHITE, anchor="lm")
        px += pw + 18

    text(d, (88, 590), "global-photoshoots.vercel.app", f_foot, SLATE)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()