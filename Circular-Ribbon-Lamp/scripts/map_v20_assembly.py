"""Assembly map for the V20 print set (PNG, plan view from below): petals, seams, studs, LED channels, screws, plates.

Run: python3 scripts/map_v20_assembly.py
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v20_geometry as G  # noqa: E402
import v20_parts as PT  # noqa: E402

DEV = HERE.parent / "development-v20"
pm = json.loads((DEV / "Print-map.json").read_text())
petals = {p["id"]: p for p in G.build_all()}
COL = {"B": (150, 160, 150), "M": (214, 128, 72), "O": (226, 190, 130)}
W = 1240
S = 0.96
im = Image.new("RGB", (W + 360, W), (252, 250, 246))
d = ImageDraw.Draw(im, "RGBA")
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
except Exception:
    font = small = ImageFont.load_default()


def pt(x, y):
    return (W / 2 - x * S, W / 2 - y * S)        # seen from below: mirror x


# paint from the ceiling side down so lower (nearer) petals end up on top
quads = []
for p in petals.values():
    Sg = p["S"]
    ns, nv = Sg.shape[:2]
    for i in range(0, ns - 1, 2):
        for j in range(0, nv - 1, 2):
            q = [Sg[i, j], Sg[min(i + 2, ns - 1), j], Sg[min(i + 2, ns - 1), min(j + 2, nv - 1)], Sg[i, min(j + 2, nv - 1)]]
            quads.append((-np.mean([v[2] for v in q]), p["whorl"], q))
quads.sort(key=lambda t: t[0])
for z, wh, q in quads:
    d.polygon([pt(v[0], v[1]) for v in q], fill=COL[wh] + (255,))
# outlines
for p in petals.values():
    o = G.plan_outline(p)
    d.line([pt(x, y) for x, y in list(o) + [o[0]]], fill=(60, 60, 60, 200), width=1)
# hub
fr = G.P["flange_r"]
d.ellipse([pt(fr, fr), pt(-fr, -fr)], fill=(40, 36, 34, 255))
# LED channels
for p in petals.values():
    if p["whorl"] != "B":
        continue
    base, U, Sd, jc = PT.channel_frame(p)
    rows = [i for i in range(len(p["s"])) if 430.0 <= p["s"][i] <= 700.0]
    d.line([pt(*base[i][:2]) for i in rows], fill=(255, 205, 40, 255), width=5)
# seams: cut rows
for pid, sr in pm["seams"].items():
    p = petals[pid]
    for r in sr["rows"] or []:
        a = p["S"][r, 0]
        b = p["S"][r, -1]
        d.line([pt(*a[:2]), pt(*b[:2])], fill=(20, 20, 20, 255), width=3)
# studs
for st in pm["studs_list"]:
    x, y = pt(st["x"], st["y"])
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(40, 90, 200, 255), outline=(255, 255, 255, 255))
# screws
for pid, p in petals.items():
    if p["whorl"] != "B":
        continue
    for sv in (9.0, 25.0):
        i = int(np.argmin(abs(p["s"] - sv)))
        x, y = pt(*p["S"][i, p["S"].shape[1] // 2][:2])
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(230, 40, 40, 255))
# labels
for pid, p in petals.items():
    i = len(p["s"]) // 2
    x, y = pt(*p["S"][i, p["S"].shape[1] // 2][:2])
    d.text((x - 10, y - 8), pid, fill=(20, 20, 20, 255), font=font)
# legend
x0 = W + 20
d.text((x0, 30), "V20 assembly map", fill=(20, 20, 20, 255), font=font)
d.text((x0, 56), "seen from below (looking up)", fill=(90, 90, 90, 255), font=small)
items = [((150, 160, 150), "B  inner blades (5), root on hub"), ((214, 128, 72), "M  outer blades (5), hung from B"),
         ((226, 190, 130), "O  rim ovals (5), hung from M")]
y0 = 100
for c, t in items:
    d.rectangle([x0, y0, x0 + 24, y0 + 18], fill=c + (255,))
    d.text((x0 + 34, y0), t, fill=(20, 20, 20, 255), font=small)
    y0 += 30
d.line([(x0, y0 + 9), (x0 + 24, y0 + 9)], fill=(255, 205, 40, 255), width=5)
d.text((x0 + 34, y0), "LED channel (hidden face)", fill=(20, 20, 20, 255), font=small)
y0 += 30
d.line([(x0, y0 + 9), (x0 + 24, y0 + 9)], fill=(20, 20, 20, 255), width=3)
d.text((x0 + 34, y0), "half-lap seam (cut line)", fill=(20, 20, 20, 255), font=small)
y0 += 30
d.ellipse([x0 + 6, y0 + 3, x0 + 18, y0 + 15], fill=(40, 90, 200, 255))
d.text((x0 + 34, y0), "bond stud (%d)" % len(pm["studs_list"]), fill=(20, 20, 20, 255), font=small)
y0 += 30
d.ellipse([x0 + 9, y0 + 6, x0 + 15, y0 + 12], fill=(230, 40, 40, 255))
d.text((x0 + 34, y0), "M3 screw (10)", fill=(20, 20, 20, 255), font=small)
y0 += 50
t = pm["totals"]
for line in (f"{t['petal_pieces']} petal pieces + {t['hub_parts']} hub parts", f"{t['plates']} plates (320 mm box)",
             f"{t['mass_g_petg'] / 1000:.2f} kg PETG (all parts)", "all parts closed solids"):
    d.text((x0, y0), line, fill=(20, 20, 20, 255), font=small)
    y0 += 24
im.save(DEV / "Assembly-map.png")
print("saved", DEV / "Assembly-map.png")
