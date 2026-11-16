"""Plan and elevation sketch of the V17 ribbons (PNG), for design review."""
import sys
import numpy as np
from PIL import Image, ImageDraw
import v17_geometry as G

COL = {"A": (214, 120, 60), "B": (60, 130, 200), "C": (90, 170, 90)}


def sketch(path, p=G.P):
    rings, cl = G.build(p)
    S, off = 0.6, 380
    im = Image.new("RGB", (1520, 760), (250, 248, 244))
    d = ImageDraw.Draw(im, "RGBA")
    # plan (left)
    def P(x, y):
        return (off + x * S, 380 - y * S)
    d.ellipse([P(-p["canopy_r"], p["canopy_r"]), P(p["canopy_r"], -p["canopy_r"])], outline=(120, 120, 120), width=2)
    # draw lower things first: sort strips by z
    quads = []
    for k, r in rings.items():
        M = G.mid_surface(r, 3)
        for i in range(0, len(M), 2):
            j = (i + 2) % len(M)
            quads.append((M[i, :, 2].mean(), k, [M[i, 0], M[i, 2], M[j, 2], M[j, 0]]))
    quads.sort(key=lambda q: q[0])
    for z, k, q in quads:
        shade = int(np.clip((z + 160) / 150 * 255, 0, 255))
        c = COL[k]
        fill = tuple(int(c[t] * (0.45 + 0.55 * shade / 255)) for t in range(3)) + (255,)
        d.polygon([P(v[0], v[1]) for v in q], fill=fill)
    for c in cl:
        x, y = c["xy"]
        d.ellipse([P(x - 6, y + 6), P(x + 6, y - 6)], outline=(0, 0, 0), width=2)
    # elevation (right): view from -y, x horizontal, z vertical
    ox, oz = 1140, 120
    def E(x, z):
        return (ox + x * S, oz - z * S * 1.6)
    d.line([E(-600, 0), E(600, 0)], fill=(90, 90, 90), width=2)
    pts = []
    for k, r in rings.items():
        M = G.mid_surface(r, 9)
        for i in range(0, len(M), 2):
            j = (i + 2) % len(M)
            for a in range(8):
                q = [M[i, a], M[i, a + 1], M[j, a + 1], M[j, a]]
                pts.append((-np.mean([v[1] for v in q]), k, q))
    pts.sort(key=lambda q: q[0])
    for depth, k, q in pts:
        c = COL[k]
        d.polygon([E(v[0], v[2]) for v in q], fill=c + (60,))
    for z in (-50, -100, -150):
        d.line([E(-600, z), E(-580, z)], fill=(90, 90, 90))
        d.text(E(-640, z + 4), f"{z}", fill=(60, 60, 60))
    d.text((20, 20), "V17 plan (darker = lower)  circles: crossings", fill=(30, 30, 30))
    d.text((800, 20), "Elevation from the front (depth exaggerated 1.6x)", fill=(30, 30, 30))
    im.save(path)


if __name__ == "__main__":
    sketch(sys.argv[1])
