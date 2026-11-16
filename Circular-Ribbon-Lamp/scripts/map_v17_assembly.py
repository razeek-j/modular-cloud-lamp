"""Assembly map for the V17 print set (PNG): pieces, seams, seats, hangers, LED runs."""
import json
import warnings
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

warnings.filterwarnings("ignore")
import v17_geometry as G

DEV = Path(__file__).resolve().parents[1] / "development-v17"
COL = {"A": (205, 120, 60), "B": (60, 125, 195), "C": (80, 160, 85)}
rings, crossings = G.build(G.P)
pm = json.loads((DEV / "Print-map.json").read_text())
bd = json.loads((DEV / "Build-data.json").read_text())
S, W = 0.85, 1100
im = Image.new("RGB", (W + 420, W), (252, 250, 246))
d = ImageDraw.Draw(im, "RGBA")
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
except Exception:
    font = small = ImageFont.load_default()


def P(x, y):
    # view from below: mirror x so the map matches what you see looking up
    return (W / 2 - x * S, W / 2 - y * S)


quads = []
for k, r in rings.items():
    M = G.mid_surface(r, 3)
    for i in range(0, len(M), 2):
        j = (i + 2) % len(M)
        quads.append((-M[i, :, 2].mean(), k, [M[i, 0], M[i, 2], M[j, 2], M[j, 0]]))
quads.sort(key=lambda q: q[0])            # from below: draw higher parts first
for z, k, q in quads:
    d.polygon([P(v[0], v[1]) for v in q], fill=COL[k] + (235,))
cr = G.P["canopy_r"]
d.ellipse([P(cr, cr), P(-cr, -cr)], outline=(90, 90, 90), width=2)
# LED runs
for run in bd["led_runs"]:
    r = rings[run["ring"]]
    pts = [P(*r["C"][i][:2]) for i in run["stations"]]
    d.line(pts, fill=(255, 210, 60, 255), width=5)
# seams and labels
for pc in pm["pieces"]:
    r = rings[pc["ring"]]
    a, b = pc["stations"]
    for i in (a,):
        c, D, w = r["C"][i], r["D"][i], r["w"][i]
        p0, p1 = c - D * w / 2, c + D * w / 2
        d.line([P(*p0[:2]), P(*p1[:2])], fill=(20, 20, 20), width=3)
    n = len(r["C"])
    mid = (a + ((b - a) % n) // 2) % n
    x, y = P(*r["C"][mid][:2])
    d.rounded_rectangle([x - 22, y - 12, x + 22, y + 12], 6, fill=(255, 255, 255, 230), outline=(30, 30, 30))
    d.text((x, y), pc["id"], fill=(20, 20, 20), font=small, anchor="mm")
for it in bd["seats"]:
    r = rings[it["ring"]]
    x, y = P(*r["C"][it["station"]][:2])
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(0, 0, 0))
for it in bd["hangers"]:
    r = rings[it["ring"]]
    x, y = P(*r["C"][it["station"]][:2])
    d.rectangle([x - 7, y - 7, x + 7, y + 7], outline=(0, 0, 0), width=3)
    d.line([P(0, 0), (x, y)], fill=(120, 120, 120, 160), width=2)
# legend
lx = W + 20
d.text((lx, 30), "V17 assembly map (seen from below)", fill=(20, 20, 20), font=font)
items = [("Ring A (largest)", COL["A"]), ("Ring B", COL["B"]), ("Ring C (smallest)", COL["C"])]
for k, (t, c) in enumerate(items):
    d.rectangle([lx, 70 + 30 * k, lx + 22, 88 + 30 * k], fill=c)
    d.text((lx + 32, 70 + 30 * k), t, fill=(20, 20, 20), font=small)
y0 = 170
for t in ["Black bar: seam (tab laps onto the next piece)", "Yellow: LED channel (hidden top face)",
          "Black dot: seat under the ceiling disc", "Square: hanger to a spider arm (grey line)",
          "Weave: A over B, B over C, C over A", "", f"{pm['totals']['pieces']} pieces · {pm['totals']['plates']} plates",
          f"about {pm['totals']['mass_g_petg'] / 1000:.2f} kg PETG (skin, tabs, bosses, channels)"]:
    d.text((lx, y0), t, fill=(40, 40, 40), font=small)
    y0 += 26
im.save(DEV / "Assembly-map.png")
print("saved")
