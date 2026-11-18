"""Quick painter's-algorithm preview of V20 from below (plan view), side by side with the user's picture.

Run: python3 scripts/v20_preview.py [out.png]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v20_geometry as G  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "development-v20" / "preview-below.png"
OUT.parent.mkdir(exist_ok=True, parents=True)

PAL = {"ivory": (238, 226, 200), "orange": (214, 128, 72), "sage": (140, 160, 150), "tan": (226, 190, 130)}
CYCLE = {"B": ["ivory", "orange", "sage", "tan", "orange"],
         "M": ["sage", "ivory", "tan", "ivory", "sage"],
         "O": ["ivory", "orange", "tan", "ivory", "sage"]}

petals = G.build_all()
SZ = 1000
scale = SZ / 1300.0
img = Image.new("RGB", (SZ, SZ), (20, 18, 17))
dr = ImageDraw.Draw(img)
polys = []
for p in petals:
    col = np.array(PAL[CYCLE[p["whorl"]][p["index"] % 5]], float)
    S, N = p["S"], p["N"]
    ns, nv = S.shape[:2]
    light = np.array([0.25, 0.35, -0.9])
    light /= np.linalg.norm(light)
    for i in range(0, ns - 1, 2):
        for j in range(0, nv - 1, 2):
            q = [S[i, j], S[min(i + 2, ns - 1), j], S[min(i + 2, ns - 1), min(j + 2, nv - 1)], S[i, min(j + 2, nv - 1)]]
            q = np.array(q)
            d = -q[:, 2].mean()
            n = N[i, j]
            sh = 0.55 + 0.45 * abs(np.dot(n, light))
            polys.append((d, q, col * sh))
polys.sort(key=lambda t: t[0])
for d, q, c in polys:
    pts = [(SZ / 2 - x * scale, SZ / 2 - y * scale) for x, y, _ in q]
    dr.polygon(pts, fill=tuple(int(v) for v in c))
# hub
cx = cy = SZ / 2
dr.ellipse([cx - G.P["flange_r"] * scale, cy - G.P["flange_r"] * scale, cx + G.P["flange_r"] * scale,
            cy + G.P["flange_r"] * scale], fill=(36, 30, 28))
dr.ellipse([cx - 24 * scale, cy - 24 * scale, cx + 24 * scale, cy + 24 * scale], fill=(240, 150, 70))
ref = Image.open("/private/tmp/claude-501/-Users-razeek-Projects-3D-printing/5c2b4e9c-d9e2-4c02-9e0c-4a734bdae3c5/images/1.png").convert("RGB").resize((SZ, SZ))
both = Image.new("RGB", (2 * SZ, SZ))
both.paste(ref, (0, 0))
both.paste(img, (SZ, 0))
both.save(OUT)
print("saved", OUT)
# stats
for p in petals[:: 5]:
    S = p["S"]
    r = np.hypot(S[:, :, 0], S[:, :, 1])
    d = -S[:, :, 2]
    print(p["id"], "rho %.0f-%.0f" % (r.min(), r.max()), "d %.0f-%.0f" % (d.min(), d.max()),
          "sweep %.0f deg" % np.degrees(abs(p["phi"][-1] - p["phi"][0])), "L %.0f" % p["L"],
          "h_end %.0f" % p["h"][-1])
