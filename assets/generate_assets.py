#!/usr/bin/env python3
"""Generate abstract tech background images for the AI weekly deck (PIL, local only)."""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)
W, H = 1280, 720


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(draw, c1, c2, diagonal=True):
    for y in range(H):
        x_ratio = (y / H) if not diagonal else (y / H)
        draw.line([(0, y), (W, y)], fill=lerp(c1, c2, x_ratio))


def circuit(draw, rng, color, n=26):
    """Random circuit-board traces."""
    for _ in range(n):
        x, y = rng.randint(-40, W), rng.randint(-40, H)
        pts = [(x, y)]
        for _ in range(rng.randint(3, 7)):
            dx, dy = rng.choice([(60, 0), (-60, 0), (0, 60), (0, -60)])
            nx, ny = pts[-1][0] + dx, pts[-1][1] + dy
            pts.append((nx, ny))
        draw.line(pts, fill=color, width=rng.choice([1, 1, 2]))
        # node dots at joints
        for px, py in pts[1::2]:
            r = rng.choice([2, 3])
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)


def neural(draw, rng, color, n=14):
    """Layered neural-net dots and links."""
    layers = []
    lx = 80
    while lx < W - 60:
        k = rng.randint(3, 6)
        layers.append([(lx, int(H * (i + 1) / (k + 1)) + rng.randint(-18, 18)) for i in range(k)])
        lx += rng.randint(160, 240)
    for a, b in zip(layers, layers[1:]):
        for p in a:
            for q in rng.sample(b, min(len(b), 3)):
                draw.line([p, q], fill=color, width=1)
    for layer in layers:
        for p in layer:
            r = 5
            draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def waves(draw, rng, color, n=9):
    """Signal / audio waves."""
    for k in range(n):
        amp = rng.randint(18, 70)
        y0 = rng.randint(60, H - 60)
        ph = rng.uniform(0, math.tau)
        freq = rng.uniform(0.006, 0.016)
        pts = [(x, y0 + amp * math.sin(ph + x * freq)) for x in range(0, W, 8)]
        draw.line(pts, fill=color, width=2)


def glow_disk(img, cx, cy, r, color):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -6):
        alpha = int(90 * (1 - i / r))
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    img.alpha_composite(layer)


SPECS = {
    # P1 封面：减速 vs 加速的对撞——左暖橙（刹车）右青色（加速）光晕 + 速度线
    "bg-cover": dict(seed=101, base=((26, 14, 8), (6, 14, 20)), motif="cover"),
    "bg-p2": dict(seed=202, base=((6, 12, 24), (10, 18, 30)), motif="neural"),
    "bg-p3": dict(seed=303, base=((4, 18, 22), (6, 10, 26)), motif="circuit"),
    "bg-p4": dict(seed=404, base=((10, 12, 26), (6, 16, 22)), motif="neural"),
    "bg-p5": dict(seed=505, base=((20, 12, 6), (8, 12, 24)), motif="cover"),
    "bg-p6": dict(seed=606, base=((22, 8, 18), (10, 8, 22)), motif="waves"),
    "bg-p7": dict(seed=707, base=((6, 14, 18), (14, 8, 24)), motif="circuit"),
    "bg-p8": dict(seed=808, base=((4, 16, 16), (8, 10, 24)), motif="waves"),
    "bg-p9": dict(seed=909, base=((8, 12, 22), (12, 16, 28)), motif="neural"),
    "bg-p10": dict(seed=1010, base=((14, 12, 26), (4, 14, 18)), motif="waves"),
}

for name, spec in SPECS.items():
    rng = random.Random(spec["seed"])
    c1, c2 = spec["base"]
    img = Image.new("RGBA", (W, H))
    gradient(ImageDraw.Draw(img), c1, c2)

    motif = spec["motif"]
    teal = (94, 234, 212)
    amber = (251, 191, 36)
    pink = (244, 114, 182)
    faint = (70, 100, 120)

    if motif == "cover":
        glow_disk(img, int(W * 0.22), int(H * 0.42), 300, amber)
        glow_disk(img, int(W * 0.80), int(H * 0.5), 330, teal)
        d = ImageDraw.Draw(img)
        # speed lines from both sides
        for _ in range(38):
            y = rng.randint(0, H)
            x0 = rng.randint(0, 180)
            ln = rng.randint(120, 420)
            d.line([(x0, y), (x0 + ln, y)], fill=amber + (rng.randint(30, 80),), width=1)
        for _ in range(38):
            y = rng.randint(0, H)
            x1 = W - rng.randint(0, 180)
            ln = rng.randint(120, 420)
            d.line([(x1 - ln, y), (x1, y)], fill=teal + (rng.randint(30, 80),), width=1)
    elif motif == "circuit":
        d = ImageDraw.Draw(img)
        circuit(d, rng, faint + (110,), n=34)
        glow_disk(img, rng.randint(200, 1000), rng.randint(150, 550), 200, teal)
    elif motif == "neural":
        d = ImageDraw.Draw(img)
        neural(d, rng, faint + (130,))
        glow_disk(img, rng.randint(200, 1000), rng.randint(150, 550), 190, teal)
        if rng.random() > 0.5:
            glow_disk(img, rng.randint(200, 1000), rng.randint(150, 550), 150, pink)
    else:  # waves
        d = ImageDraw.Draw(img)
        waves(d, rng, faint + (120,), n=12)
        glow_disk(img, rng.randint(200, 1000), rng.randint(150, 550), 200, teal)

    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.convert("RGB").save(OUT / f"{name}.png", optimize=True)
    print("saved", OUT / f"{name}.png")
