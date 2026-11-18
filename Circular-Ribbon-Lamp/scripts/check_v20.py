"""V20 geometry checks (run in Blender's Python):

  Blender -b -P scripts/check_v20.py -- [--write]

Reports intersections between petals, minimum gaps per overlapping pair, envelope (diameter and
depth), hub clearances and the clamp zones that should touch. --write stores Checks.json.
"""

import json
import sys
from pathlib import Path

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v20_geometry as G  # noqa: E402
import v20_parts as PT  # noqa: E402

OUT = HERE.parent / "development-v20"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
P = G.P


def tri_mesh(p):
    verts, quads, kind = G.shell_faces(p)
    tris = []
    for q in quads:
        tris.append((q[0], q[1], q[2]))
        tris.append((q[0], q[2], q[3]))
    return [tuple(v) for v in verts], tris


petals = G.build_all()
trees = {}
for p in petals:
    v, t = tri_mesh(p)
    trees[p["id"]] = BVHTree.FromPolygons(v, t, epsilon=0.0)

# hub solids as simple triangle boxes (cylinders)
def cyl_tree(r, d0, d1, seg=96):
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    v = [(r * np.cos(a), r * np.sin(a), -d0) for a in ang] + [(r * np.cos(a), r * np.sin(a), -d1) for a in ang]
    v += [(0, 0, -d0), (0, 0, -d1)]
    t = []
    for k in range(seg):
        k2 = (k + 1) % seg
        t += [(k, k2, seg + k2), (k, seg + k2, seg + k), (2 * seg, k2, k), (2 * seg + 1, seg + k, seg + k2)]
    return BVHTree.FromPolygons(v, t)


hub = {"flange": cyl_tree(P["flange_r"], *P["flange_d"]), "cap": cyl_tree(P["cap_r"], *P["cap_d"]),
       "drum": cyl_tree(P["hub_r"], P["plate_t"], P["flange_d"][1])}

res = dict(petals=len(petals))
# --- pairwise intersections and minimum gaps
inter, gaps = [], {}
ids = [p["id"] for p in petals]
byid = {p["id"]: p for p in petals}
samples = {}
for p in petals:
    S, N = p["S"], p["N"]
    t = P["thickness"]
    ns, nv = S.shape[:2]
    pts = []
    for i in range(0, ns, 3):
        for j in range(0, nv, 2):
            pts.append(S[i, j] + N[i, j] * t / 2)
            pts.append(S[i, j] - N[i, j] * t / 2)
    samples[p["id"]] = np.array(pts)
for a in range(len(ids)):
    for b in range(a + 1, len(ids)):
        A, B = ids[a], ids[b]
        ov = trees[A].overlap(trees[B])
        if ov:
            inter.append((A, B, len(ov)))
        # minimum distance A samples -> B tree and B samples -> A tree
        best = 1e9
        for X, Y in ((A, B), (B, A)):
            for pt in samples[X][::2]:
                loc, nrm, idx, dist = trees[Y].find_nearest(Vector(pt), 60.0)
                if loc is not None and dist < best:
                    best = dist
        if best < 60.0:
            gaps[f"{A}-{B}"] = round(float(best), 1)
res["intersecting_pairs"] = inter
res["min_gap_mm"] = gaps
if gaps:
    worst = sorted(gaps.items(), key=lambda kv: kv[1])[:12]
    res["tightest_pairs"] = worst
# --- envelope
allv = np.concatenate([samples[i] for i in ids])
rad = np.hypot(allv[:, 0], allv[:, 1])
res["max_radius_mm"] = round(float(rad.max()), 1)
res["diameter_mm"] = round(float(2 * rad.max()), 1)
res["top_drop_mm"] = round(float((-allv[:, 2]).min()), 1)
res["max_drop_mm"] = round(float((-allv[:, 2]).max()), 1)
# --- hub clearances for each petal (blade tabs lie on the flange underside by design)
hub_gap = {}
for p in petals:
    best = {k: 1e9 for k in hub}
    for pt in samples[p["id"]][::3]:
        for k, tr in hub.items():
            loc, nrm, idx, dist = tr.find_nearest(Vector(pt), 80.0)
            if loc is not None and dist < best[k]:
                best[k] = dist
    for k, v in best.items():
        if v < 80:
            hub_gap[f"{p['id']}-{k}"] = round(float(v), 1)
res["hub_gaps_mm"] = hub_gap
# --- skin area and mass
area = {}
for p in petals:
    S = p["S"]
    a = np.linalg.norm(np.cross(S[1:, :-1] - S[:-1, :-1], S[:-1, 1:] - S[:-1, :-1]), axis=2).sum()
    area[p["id"]] = a
res["skin_area_m2"] = round(sum(area.values()) / 1e6, 3)
res["skin_mass_kg_petg_1.27"] = round(sum(area.values()) * P["thickness"] * 1.27e-6, 2)
# --- plan coverage and layer count seen from below (rays up from z = -300)
n = 220
xs = np.linspace(-600, 600, n)
layers = np.zeros((n, n), int)
up = Vector((0, 0, 1))
for iy, y in enumerate(xs):
    for ix, x in enumerate(xs):
        if x * x + y * y > 600 * 600:
            continue
        o = Vector((x, y, -400.0))
        c = 0
        for tr in trees.values():
            if tr.ray_cast(o, up)[0] is not None:
                c += 1
        layers[iy, ix] = c
inside = np.array([[(x * x + y * y) <= 600 * 600 for x in xs] for y in xs])
# the hub flange covers the centre
flange = np.array([[(x * x + y * y) <= P["flange_r"] ** 2 for x in xs] for y in xs])
open_frac = float(((layers == 0) & inside & ~flange).sum() / max(1, (inside & ~flange).sum()))
res["plan_open_fraction_outside_hub"] = round(open_frac, 3)
res["mean_layers"] = round(float(layers[inside & ~flange].mean()), 2)
res["layer_histogram"] = {int(k): int(((layers == k) & inside & ~flange).sum()) for k in range(0, 5)}
# --- LED sight-line test: strips in the blade channels (hidden face, covered edge) and on the hub drum
strip_pts = []
for p in petals:
    if p["whorl"] != "B":
        continue
    base, U, Sd, jc = PT.channel_frame(p)
    for i in range(len(p["s"])):
        if 430.0 <= p["s"][i] <= 700.0:
            strip_pts.append(base[i] + U[i] * (PT.CH_FLOOR + 0.6))
for k in range(0, 360, 6):
    a = np.radians(k)
    for d in (12.0, 20.0):
        strip_pts.append(np.array([76.0 * np.cos(a), 76.0 * np.sin(a), -d]))
strip_pts = np.array(strip_pts)
eyes = []
for drop in (900, 1300, 1700):
    for rad in (0, 700, 1400, 2200):
        for ang in range(0, 360, 30 if rad else 360):
            a = np.radians(ang)
            eyes.append(Vector((rad * np.cos(a), rad * np.sin(a), -float(drop))))
hub_trees = list(hub.values())
vis_hits = rays = 0
vis_by_group = {"channel": 0, "hub": 0}
n_ch = len(strip_pts) - 120
for k, pt in enumerate(strip_pts[::2]):
    P_ = Vector(pt)
    for e in eyes:
        d = P_ - e
        L = d.length
        dn = d / L
        rays += 1
        blocked = any(tr.ray_cast(e, dn, L - 0.8)[0] is not None for tr in trees.values())
        if not blocked:
            blocked = any(tr.ray_cast(e, dn, L - 0.8)[0] is not None for tr in hub_trees)
        if not blocked:
            vis_hits += 1
            vis_by_group["channel" if (2 * k) < n_ch else "hub"] += 1
res["led_sightline"] = dict(rays=rays, eye_positions=len(eyes), strip_points=len(strip_pts), visible_rays=vis_hits,
                            visible_by_group=vis_by_group)
if "--write" in ARGS:
    (OUT / "Checks-geometry.json").write_text(json.dumps(res, indent=1))
print("CHECK " + json.dumps(res))
