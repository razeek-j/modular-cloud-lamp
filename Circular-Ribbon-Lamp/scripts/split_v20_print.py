"""Split V20 into printable pieces, orient them, pack build plates (Kobra S1 Max, 320 mm working box).

Run: Blender -b -P scripts/split_v20_print.py

Outputs in development-v20/Print-files: one STL per piece (print orientation, mm), the hub parts, 3MF plates,
and development-v20/Print-map.json (pieces, seams, studs, orientation, plates, totals).
"""

import json
import math
import sys
import zipfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v20_geometry as G  # noqa: E402
import v20_parts as PT  # noqa: E402

ROOT = HERE.parent
DEV = ROOT / "development-v20"
OUT = DEV / "Print-files"
OUT.mkdir(exist_ok=True)
for old in OUT.glob("*"):
    old.unlink()
P = G.P
BOX = 320.0
PIECE_MIN, PIECE_MAX = 90.0, 285.0
CHANNEL_S = (430.0, 700.0)         # blade developed length covered by the LED channel
SCREW_S = (9.0, 25.0)              # screw hole positions along the blade root tab
SCREW_D = 3.4
GAP = 8.0

petals = G.build_all()
byid = {p["id"]: p for p in petals}


def tris_of(p):
    verts, quads, kind = G.shell_faces(p)
    t = []
    for q in quads:
        t.append((q[0], q[1], q[2]))
        t.append((q[0], q[2], q[3]))
    return [tuple(v) for v in verts], t


trees = {}
for p in petals:
    v, t = tris_of(p)
    trees[p["id"]] = BVHTree.FromPolygons(v, t, epsilon=0.0)

# ---------------------------------------------------------------------------- seam placement hidden under neighbours
EYES = []
for drop in (900, 1300, 1700):
    for rad in (0, 700, 1400, 2200):
        for ang in range(0, 360, 30 if rad else 360):
            a = math.radians(ang)
            EYES.append(Vector((rad * math.cos(a), rad * math.sin(a), -float(drop))))
alltrees = list(trees.values())


# ---------------------------------------------------------------------------- studs between overlapping petals
DOWN, UP = Vector((0, 0, -1)), Vector((0, 0, 1))
tt = P["thickness"] / 2


def plan_grid(p):
    S = p["S"]
    return S[:, :, :2].reshape(-1, 2)


def find_studs():
    cands = {}
    for X in petals:                       # X is the candidate upper petal
        S, N = X["S"], X["N"]
        ns, nv = S.shape[:2]
        for Y in petals:                   # Y the candidate lower petal
            if X["id"] == Y["id"]:
                continue
            pts = []
            for i in range(8, ns - 8, 4):
                for j in range(2, nv - 2, 2):
                    if abs(N[i, j, 2]) < 0.82:
                        continue
                    vis = S[i, j] + N[i, j] * tt
                    o = Vector(vis) + Vector((0, 0, -0.3))
                    hit = trees[Y["id"]].ray_cast(o, DOWN, 40.0)
                    if hit[0] is None:
                        continue
                    gap = hit[3]
                    if not (6.0 <= gap <= 36.0):
                        continue
                    # lower-side margin: nearest grid point of Y in plan
                    d2 = ((plan_grid(Y) - np.array([hit[0][0], hit[0][1]])) ** 2).sum(1)
                    k = int(np.argmin(d2))
                    iL, jL = divmod(k, Y["S"].shape[1])
                    nsY, nvY = Y["S"].shape[:2]
                    if not (8 <= iL <= nsY - 9 and 3 <= jL <= nvY - 4) or abs(Y["N"][iL, jL, 2]) < 0.82:
                        continue
                    # nothing else between the two sheets
                    blocked = False
                    for oid, tr in trees.items():
                        if oid in (X["id"], Y["id"]):
                            continue
                        h2 = tr.ray_cast(Vector(hit[0]) + Vector((0, 0, 0.3)), UP, gap - 0.6)
                        if h2[0] is not None:
                            blocked = True
                            break
                    if blocked:
                        continue
                    vX = abs(j - (nv - 1) / 2) / ((nv - 1) / 2)
                    vL = abs(jL - (nvY - 1) / 2) / ((nvY - 1) / 2)
                    score = vX + vL + 0.02 * abs(gap - 14.0)
                    pts.append((score, tuple(hit[0]), gap, (i, j), (iL, jL)))
            if pts:
                cands[(X["id"], Y["id"])] = sorted(pts, key=lambda t: t[0])
    return cands


def stud_visibility(loc, gap):
    """Fraction of room sight lines that reach the stud's mid-height unobstructed."""
    pnt = Vector((loc[0], loc[1], loc[2] + gap * 0.5))
    hit = 0
    for e in EYES:
        d = pnt - e
        L = d.length
        dn = d / L
        if not any(tr.ray_cast(e, dn, L - 0.6)[0] is not None for tr in alltrees):
            hit += 1
    return hit / len(EYES)


def choose_studs(cands, per_pair=2, spacing=46.0):
    chosen = []
    for (xid, yid), lst in cands.items():
        # re-rank the best geometric candidates by how little of the stud the room can see
        lst = sorted(lst, key=lambda t: t[0])[:50]
        ranked = []
        for score, loc, gap, ij, ijL in lst:
            vis = stud_visibility(loc, gap)
            ranked.append((score * 0.5 + vis * 4.0 + 0.02 * abs(gap - 14.0), loc, gap, ij, ijL, vis))
        ranked.sort(key=lambda t: t[0])
        lst = [(r[0], r[1], r[2], r[3], r[4]) for r in ranked]
        got = []
        for score, loc, gap, (i, j), (iL, jL) in lst:
            if all(np.hypot(loc[0] - g["x"], loc[1] - g["y"]) >= spacing for g in chosen if g["upper"] == xid or g["lower"] == yid
                   or True) and all(np.hypot(loc[0] - g["x"], loc[1] - g["y"]) >= spacing for g in got):
                got.append(dict(x=loc[0], y=loc[1], z=loc[2], upper=xid, lower=yid, gap=gap, iU=i, iL=iL))
                if len(got) >= per_pair:
                    break
        chosen += got
    return chosen


cands = find_studs()
studs = choose_studs(cands)
# merge studs that ended up closer than 36 mm (keep the lowest-gap)
studs.sort(key=lambda s: s["gap"])
kept = []
for s in studs:
    if all(np.hypot(s["x"] - k["x"], s["y"] - k["y"]) >= 36.0 for k in kept):
        kept.append(s)
studs = kept
for st_ in studs:
    st_["visible_fraction"] = round(stud_visibility((st_["x"], st_["y"], st_["z"]), st_["gap"]), 3)
print("studs", len(studs), "max visible fraction", max(s_["visible_fraction"] for s_ in studs),
      "mean", round(float(np.mean([s_["visible_fraction"] for s_ in studs])), 3))


def stud_mesh(s):
    L, U = trees[s["lower"]], trees[s["upper"]]

    def zb(px, py):
        h = L.ray_cast(Vector((px, py, 5.0)), DOWN, 400.0)
        return h[0][2] if h[0] is not None else s["z"]

    def zt(px, py):
        h = U.ray_cast(Vector((px, py, zb(px, py) + 0.2)), UP, 80.0)
        return h[0][2] if h[0] is not None else s["z"] + s["gap"]

    return PT.stud_tris(s["x"], s["y"], zb, zt)


def row_visibility(p, i):
    S, N = p["S"], p["N"]
    nv = S.shape[1]
    hit = tot = 0
    for fr in (-0.6, -0.2, 0.2, 0.6):
        j = int(round((nv - 1) / 2 * (1 + fr)))
        pnt = Vector(S[i, j] + N[i, j] * (tt + 0.8))
        for e in EYES:
            d = pnt - e
            L = d.length
            if L < 1e-3:
                continue
            tot += 1
            dn = d / L
            blocked = False
            for tr in alltrees:
                if tr.ray_cast(e, dn, L - 0.4)[0] is not None:
                    blocked = True
                    break
            if not blocked:
                hit += 1
    return hit / max(1, tot)


def plan_seams(p, n_pieces, avoid_s):
    s = p["s"]
    L = p["L"]
    ns = len(s)
    rows = [i for i in range(6, ns - 6, 4)
            if all(abs(s[i] - a) > 18.0 for a in avoid_s)]
    cost = {i: row_visibility(p, i) for i in rows}
    # lips: seams in the strongly curved tip are harder to bond and to print
    w = G.WHORLS[p["whorl"]]
    for i in rows:
        if s[i] > L - w["roll_len"] - 10:
            cost[i] += 0.5
    best = None
    if n_pieces == 2:
        for r1 in rows:
            a, b = s[r1], L - s[r1]
            if PIECE_MIN <= a <= PIECE_MAX and PIECE_MIN <= b <= PIECE_MAX:
                c = cost[r1] + 1e-5 * ((a - b) ** 2)
                if best is None or c < best[0]:
                    best = (c, [r1])
    elif n_pieces == 3:
        for r1 in rows:
            for r2 in rows:
                if r2 <= r1:
                    continue
                a, b, c3 = s[r1], s[r2] - s[r1], L - s[r2]
                if all(PIECE_MIN <= x <= PIECE_MAX for x in (a, b, c3)):
                    c = cost[r1] + cost[r2] + 1e-5 * ((a - b) ** 2 + (b - c3) ** 2)
                    if best is None or c < best[0]:
                        best = (c, [r1, r2])
    elif n_pieces == 4:
        for r1 in rows:
            for r2 in rows:
                if r2 <= r1:
                    continue
                for r3 in rows:
                    if r3 <= r2:
                        continue
                    seg = [s[r1], s[r2] - s[r1], s[r3] - s[r2], L - s[r3]]
                    if all(PIECE_MIN <= x <= PIECE_MAX for x in seg):
                        c = cost[r1] + cost[r2] + cost[r3] + 1e-5 * sum((x - L / 4) ** 2 for x in seg)
                        if best is None or c < best[0]:
                            best = (c, [r1, r2, r3])
    return best[1] if best else None, {i: round(cost[i], 3) for i in (best[1] if best else [])}


# ---------------------------------------------------------------------------- hole cutting with Blender booleans
def cut_holes(tris, cutters):
    """Boolean-difference vertical cylinders (x, y, z0, z1, r) from a closed triangle soup."""
    pts = tris.reshape(-1, 3)
    uniq, inv = np.unique(np.round(pts, 5), axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3).tolist()
    me = bpy.data.meshes.new("piece")
    me.from_pydata(uniq.tolist(), [], faces)
    me.update()
    ob = bpy.data.objects.new("piece", me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    for k, (x, y, z0, z1, r) in enumerate(cutters):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=abs(z1 - z0), location=(x, y, (z0 + z1) / 2))
        cut = bpy.context.active_object
        mod = ob.modifiers.new(f"cut{k}", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cut
        mod.solver = "EXACT"
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cut, do_unlink=True)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me2 = ev.to_mesh()
    V = np.array([v.co[:] for v in me2.vertices])
    tri = []
    me2.calc_loop_triangles()
    for lt in me2.loop_triangles:
        tri.append([V[i] for i in lt.vertices])
    ev.to_mesh_clear()
    bpy.data.objects.remove(ob, do_unlink=True)
    return np.array(tri)


# ---------------------------------------------------------------------------- plan pieces
pieces = []
seam_report = {}
lamp_extras = {"stud": [], "chan": []}
for p in petals:
    L = p["L"]
    n_pieces = int(math.ceil(L / 270.0))
    avoid = []
    for s_ in studs:
        if s_["lower"] == p["id"]:
            avoid.append(p["s"][s_["iL"]])
        if s_["upper"] == p["id"]:
            avoid.append(p["s"][s_["iU"]])
    if p["whorl"] == "B":
        avoid += [G.WHORLS["B"]["tab"] + 6.0]
    seams, costs = ([], {}) if n_pieces == 1 else plan_seams(p, n_pieces, avoid)
    if seams is None and n_pieces > 1:
        seams, costs = plan_seams(p, n_pieces, [])
    seam_report[p["id"]] = dict(rows=seams, cost=costs)
    ns = len(p["s"])
    cuts = list(seams)
    ends = [int(np.argmax(p["s"] >= p["s"][c] + PT.LAP_LEN)) for c in cuts]
    n = len(cuts) + 1
    for k in range(n):
        start = 0 if k == 0 else cuts[k - 1] + 1
        stop = ns - 1 if k == n - 1 else ends[k]
        pieces.append(dict(petal=p["id"], whorl=p["whorl"], k=k + 1, n=n, a=start, b=stop,
                           own_a=0 if k == 0 else cuts[k - 1], own_b=ns - 1 if k == n - 1 else cuts[k],
                           cut_prev=None if k == 0 else cuts[k - 1], end_prev=None if k == 0 else ends[k - 1],
                           cut_next=None if k == n - 1 else cuts[k], end_next=None if k == n - 1 else ends[k]))
print("pieces", len(pieces))

# ---------------------------------------------------------------------------- build piece meshes
nv_all = petals[0]["S"].shape[1]
mid_cols = np.arange(int(round((nv_all - 1) / 2 * 0.22)), nv_all - int(round((nv_all - 1) / 2 * 0.22)))
for pc in pieces:
    p = byid[pc["petal"]]
    a, b = pc["a"], pc["b"]
    s = p["s"]
    T, g = tt, PT.LAP_GAP / 2
    rows, hv, hh = [], [], []
    for i in range(a, b + 1):
        rows.append(i)
        if pc["cut_prev"] is not None and i <= pc["end_prev"]:
            hv.append(-g); hh.append(-T)                  # hidden half of the lap at the start
        elif pc["cut_next"] is not None and i > pc["cut_next"]:
            hv.append(T); hh.append(g)                    # visible half of the lap at the end
        else:
            hv.append(T); hh.append(-T)                   # full skin (short ramps sit between the rows)
    tris, kinds = PT.shell_tris(p, rows, hv, hh)
    tris = tris.copy()
    # B root tab: clearance holes for the M3 screws that clamp it under the hub flange
    holes = []
    if pc["whorl"] == "B" and a == 0:
        mc = nv_all // 2
        for sv in SCREW_S:
            i = int(np.argmin(abs(s - sv)))
            x, y, z = p["S"][i, mc]
            holes.append((x, y, z - 6, z + 6, SCREW_D / 2))
        tris = cut_holes(tris, holes)
        kinds = None
    extra = []
    ex_kind = []
    # LED channel on the covered edge of the blade (B only)
    ch_len = 0.0
    if pc["whorl"] == "B":
        own_hi = pc["cut_next"] if pc["cut_next"] is not None else len(s) - 1
        rows_c = [i for i in range(a, own_hi + 1) if CHANNEL_S[0] <= s[i] <= CHANNEL_S[1]]
        if len(rows_c) > 6:
            rows = rows_c
            extra.append(PT.channel_tris(p, np.array(rows)))
            ex_kind.append("chan")
            ch_len = float(s[rows[-1]] - s[rows[0]])
    # studs on this piece (the piece holding the lower petal row)
    n_st = 0
    pc["studs"] = []
    for st in studs:
        if st["lower"] == p["id"] and pc["own_a"] <= st["iL"] < pc["own_b"] + (1 if pc["n"] == pc["k"] else 0):
            extra.append(stud_mesh(st))
            ex_kind.append("stud")
            n_st += 1
            pc["studs"].append([round(st["x"], 1), round(st["y"], 1), round(st["z"], 1), st["upper"]])
    if kinds is None:
        kinds = ["hid"] * len(tris)       # after a boolean cut the faces are re-triangulated: treat as hidden-face weight
        # re-derive kinds by normal direction relative to the petal's visible side
        nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        nz = nrm[:, 2] / np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)
        kinds = ["vis" if v < -0.3 else ("hid" if v > 0.3 else "rim") for v in nz]
    for kk, ee in zip(ex_kind, extra):
        lamp_extras[kk].append(ee)
    all_t = [tris] + extra
    all_k = [np.array(kinds)] + [np.array([k] * len(e)) for k, e in zip(ex_kind, extra)]
    pc["tris"] = np.concatenate(all_t)
    pc["kind"] = np.concatenate(all_k)
    pc["length_mm"] = round(float(s[pc["own_b"]] - s[pc["own_a"]]))
    pc["channel_mm"] = round(ch_len)
    pc["n_studs"] = n_st
    pc["holes"] = [[round(h[0], 1), round(h[1], 1)] for h in holes]
    mid = p["S"][(a + b) // 2, nv_all // 2]
    pc["mid"] = [round(float(x), 1) for x in mid]
    pc["id"] = f"{pc['petal']}-{pc['k']}"
    pc["open_edges"] = {"shell": PT.unmatched_edges(tris), **{k: PT.unmatched_edges(e) for k, e in zip(ex_kind, extra)}}

# ---------------------------------------------------------------------------- joint fit check: neighbouring pieces must not overlap
joint_checks = {}
by_petal = {}
for pc in pieces:
    by_petal.setdefault(pc["petal"], []).append(pc)
for pid, lst in by_petal.items():
    for A_, B_ in zip(lst[:-1], lst[1:]):
        def mk(pc_):
            m = pc_["tris"][(pc_["kind"] == "vis") | (pc_["kind"] == "hid") | (pc_["kind"] == "rim")].reshape(-1, 3)
            idx = [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(m) // 3)]
            return BVHTree.FromPolygons([tuple(v) for v in m], idx, epsilon=0.0)
        ov = mk(A_).overlap(mk(B_))
        # distance between the two lap faces: nearest approach of B's start lap to A's end lap
        joint_checks[f"{A_['id']}|{B_['id']}"] = len(ov)
print("joint overlaps (triangle pairs; 0 = clean):", {k: v for k, v in joint_checks.items() if v})

# ---------------------------------------------------------------------------- orientation and fit
def rot_to_z(u):
    u = u / np.linalg.norm(u)
    z = np.array([0, 0, 1.0])
    v = np.cross(u, z)
    c = float(np.dot(u, z))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


WEIGHT = {"vis": 1.0, "hid": 0.3, "rim": 0.1, "tab": 0.05, "stud": 0.05, "chan": 0.1}


def evaluate(tris, kind, R):
    t = tris @ R.T
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)
    area = ln / 2
    nz = nrm[:, 2] / ln
    zmin = t[:, :, 2].min()
    on_bed = t[:, :, 2].max(1) < zmin + 0.4
    over = (nz < -0.707) & ~on_bed
    res = {}
    for k in ("vis", "hid"):
        m = kind == k
        res[k] = float(area[over & m].sum() / max(area[m].sum(), 1e-9))
    w = np.array([WEIGHT[k] for k in kind])
    res["weighted"] = float((area * over * w).sum() / max((area * w).sum(), 1e-9))
    return res, t


for pc in pieces:
    tris, kind = pc["tris"], pc["kind"]
    main = tris[(kind == "vis") | (kind == "hid")].reshape(-1, 3)
    c = main.mean(0)
    u_, s_, vt = np.linalg.svd(main - c, full_matrices=False)
    e1, e2, e3 = vt[0], vt[1], vt[2]
    cand = []
    for th in range(-90, 91, 15):
        r = math.radians(th)
        for sg in (1, -1):
            cand.append((f"tilt{th:+d}{'' if sg > 0 else 'r'}", sg * (math.cos(r) * e3 + math.sin(r) * e2)))
    for ph in (-45, -30, -15, 15, 30, 45):
        r = math.radians(ph)
        for sg in (1, -1):
            cand.append((f"pitch{ph:+d}{'' if sg > 0 else 'r'}", sg * (math.cos(r) * e3 + math.sin(r) * e1)))
    best = None
    for name, u in cand:
        R = rot_to_z(u)
        res, t = evaluate(tris, kind, R)
        # best spin for the smallest footprint
        sp = None
        pts = t.reshape(-1, 3)
        for ang in range(0, 180, 3):
            a_ = math.radians(ang)
            Rz = np.array([[math.cos(a_), -math.sin(a_), 0], [math.sin(a_), math.cos(a_), 0], [0, 0, 1]])
            q = pts @ Rz.T
            ext = np.ptp(q, axis=0)
            key = (max(ext[0], ext[1]) > BOX, ext[0] * ext[1])
            if sp is None or key < sp[0]:
                sp = (key, Rz, ext)
        key, Rz, ext = sp
        height = ext[2]
        fits = max(ext[0], ext[1]) <= BOX and height <= 300.0
        short = max(min(ext[0], ext[1]), 1.0)
        # overhang on the visible face is worst, on the hidden face is tolerable (supports leave no mark);
        # tall, thin walls on a small footprint wobble and lift, so they are penalised
        score = (res["vis"] * 1.0 + res["hid"] * 0.6 + 0.6 * max(0.0, (height - 170.0) / 170.0)
                 + 0.4 * max(0.0, height / short - 1.3) + (0 if fits else 10.0))
        if best is None or score < best[0]:
            best = (score, name, R, Rz, ext, res, fits)
    score, name, R, Rz, ext, res, fits = best
    t = (tris @ R.T) @ Rz.T
    mn, mx = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    t = t - np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    pc["print_tris"] = t
    pc["orientation"] = name
    pc["overhang_visible"] = round(res["vis"], 3)
    pc["overhang_hidden"] = round(res["hid"], 3)
    pc["bbox_mm"] = [round(float(x)) for x in np.ptp(t.reshape(-1, 3), axis=0)]
    pc["fits"] = bool(fits)
    vol = np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6
    pc["mass_g"] = round(abs(float(vol)) / 1000 * 1.27)
    pc["open_edges"]["print_mesh"] = PT.unmatched_edges(t)
    PT.write_stl(OUT / f"{pc['id']}.stl", t, header=b"V20 rosette piece")
    print(pc["id"], pc["open_edges"], pc["length_mm"], pc["orientation"], pc["overhang_visible"], pc["overhang_hidden"], pc["bbox_mm"], pc["fits"], pc["mass_g"])

# ---------------------------------------------------------------------------- hub parts
hub_parts = []


def add_part(pid, name, tris, note, cutters=None):
    if cutters:
        tris = cut_holes(tris, cutters)
    mn, mx = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    PT.write_stl(OUT / f"{pid}.stl", tris - np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]]) if False else tris,
                 header=b"V20 rosette hub part")
    vol = abs(np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6)
    print("hub part", pid, "open edges", PT.unmatched_edges(tris), "bbox", np.round(mx - mn))
    hub_parts.append(dict(id=pid, name=name, note=note, open_edges=PT.unmatched_edges(tris), bbox_mm=[round(float(x)) for x in (mx - mn)],
                          mass_g=round(vol / 1000 * 1.27), tris=tris))


# screw / insert positions: from the blade tab centrelines
screw_xy = []
for p in petals:
    if p["whorl"] == "B":
        for sv in SCREW_S:
            i = int(np.argmin(abs(p["s"] - sv)))
            screw_xy.append(p["S"][i, nv_all // 2, :2])
body = PT.revolve([(50, 31.0), (96, 31.0), (96, 23.0), (75, 23.0), (75, 11.0), (90, 11.0), (90, 8.0), (72, 8.0),
                   (72, 23.0), (50, 23.0)])
inserts = [(x, y, -31.0 + 2.8, -31.0 - 2.8 + 5.6 - 5.6, 2.1) for x, y in screw_xy]
inserts = [(x, y, -31.0 - 1.0, -31.0 + 5.5, 2.1) for x, y in screw_xy]
add_part("H1-hub-body", "Hub body (flange ring + drum + ceiling-plate flange)", body,
         "10 heat-set M3 insert pockets (Ø4.2 × 5.5) from the underside; 3 × M4 holes to the ceiling plate to be drilled on site.", inserts)
cap = PT.revolve([(22, 32.6), (94, 32.6), (94, 36.5), (88, 38.0), (22, 38.0)])
cap_cut = [(x, y, -32.6 + 1.0, -38.0 - 1.0, 1.7) for x, y in screw_xy]
add_part("H2-hub-cap", "Smoked hub cap (hides the blade tabs and ten M3 screws)", cap,
         "Print in smoked/black PETG. Ten Ø3.4 clearance holes (countersink on the bench) for M3 flat-head screws.", cap_cut)
lens = PT.revolve([(0, 46.0), (14, 44.8), (21, 41.0), (24, 38.0), (21.5, 38.0), (21.5, 32.6), (0, 32.6)])
add_part("H3-dot-lens", "Centre dot lens (frosted)", lens, "Print in natural/milky PETG at 100% infill; sits over a 1 W warm LED puck.")
for hp in hub_parts:
    pass

# ---------------------------------------------------------------------------- plates (shelf packing) and 3MF
everything = [dict(id=pc["id"], bbox_mm=pc["bbox_mm"], tris=pc["print_tris"], kind="petal piece") for pc in pieces]
for hp in hub_parts:
    t = hp["tris"].copy()
    mn, mx = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    t = t - np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    # hub parts print flat; flip the cap and body so the visible face is up
    everything.append(dict(id=hp["id"], bbox_mm=[round(float(x)) for x in (mx - mn)], tris=t, kind="hub part"))

order = sorted(everything, key=lambda e: -(e["bbox_mm"][0] * e["bbox_mm"][1]))
plates, cur, x, y, row_h = [], [], 0.0, 0.0, 0.0
for it in order:
    w, h = it["bbox_mm"][0] + GAP, it["bbox_mm"][1] + GAP
    if x + w > BOX + GAP:
        x, y, row_h = 0.0, y + row_h, 0.0
    if y + h > BOX + GAP:
        plates.append(cur)
        cur, x, y, row_h = [], 0.0, 0.0, 0.0
    cur.append((it, x + w / 2 - GAP / 2, y + h / 2 - GAP / 2))
    x += w
    row_h = max(row_h, h)
if cur:
    plates.append(cur)


def write_3mf(path, items):
    objs, build = [], []
    for oid, (it, cx, cy) in enumerate(items, start=1):
        t = it["tris"].reshape(-1, 3)
        vs, idx = np.unique(np.round(t, 4), axis=0, return_inverse=True)
        tri = idx.reshape(-1, 3)
        vxml = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in vs)
        txml = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tri if len({a, b, c}) == 3)
        objs.append(f'<object id="{oid}" name="{it["id"]}" type="model"><mesh><vertices>{vxml}</vertices>'
                    f'<triangles>{txml}</triangles></mesh></object>')
        build.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {cx + 15:.3f} {cy + 15:.3f} 0"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(objs)}</resources><build>{"".join(build)}</build></model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)


plate_info = []
for k, items in enumerate(plates, start=1):
    fname = f"Plate-{k:02d}.3mf"
    write_3mf(OUT / fname, items)
    plate_info.append(dict(file=fname, parts=[it["id"] for it, _, _ in items]))

pmap = dict(
    working_box_mm=BOX, shell_mm=P["thickness"], piece_length_range_mm=[PIECE_MIN, PIECE_MAX],
    joint=dict(seam="half-lap (scarf) joint, each side keeps half the skin thickness over the lap, so the skin stays 1.4 mm through the seam", lap_length_mm=PT.LAP_LEN, glue_gap_mm=PT.LAP_GAP),
    studs=dict(count=len(studs), diameter_mm=2 * PT.STUD_R, top_gap_mm=PT.STUD_GAP,
               visible_fraction_max=max(s_["visible_fraction"] for s_ in studs),
               visible_fraction_mean=round(float(np.mean([s_["visible_fraction"] for s_ in studs])), 3),
               note="integral studs on the lower petal, conformal flat top 0.3 mm under the upper petal; bond with solvent cement or PETG-safe CA gel"),
    blade_root=dict(screw_hole_mm=SCREW_D, positions_s_mm=list(SCREW_S), note="two M3 clearance holes per blade tab; heat-set inserts in the hub body"),
    led_channel=dict(width_mm=2 * PT.CH_HALF, depth_mm=PT.CH_DEPTH, s_range_mm=list(CHANNEL_S), where="hidden face of each B blade, covered edge"),
    pieces=[{k: v for k, v in pc.items() if k not in ("tris", "print_tris", "kind")} for pc in pieces],
    hub_parts=[{k: v for k, v in hp.items() if k != "tris"} for hp in hub_parts],
    studs_list=[{k: (round(v, 1) if isinstance(v, float) else v) for k, v in s.items()} for s in studs],
    seams=seam_report,
    joint_overlap_pairs={k: v for k, v in joint_checks.items()},
    plates=plate_info,
    totals=dict(
        petal_pieces=len(pieces), hub_parts=len(hub_parts), plates=len(plates),
        mass_g_petg=int(sum(pc["mass_g"] for pc in pieces) + sum(hp["mass_g"] for hp in hub_parts)),
        all_fit=all(pc["fits"] for pc in pieces),
        max_overhang_visible=max(pc["overhang_visible"] for pc in pieces),
        max_overhang_hidden=max(pc["overhang_hidden"] for pc in pieces),
    ),
)
(DEV / "Print-map.json").write_text(json.dumps(pmap, indent=1))
np.savez_compressed(DEV / "Lamp-frame-extras.npz", **{k: (np.concatenate(v) if v else np.zeros((0, 3, 3))) for k, v in lamp_extras.items()},
                    **{f"hub_{hp['id']}": hp["tris"] for hp in hub_parts})
print("PRINT " + json.dumps(pmap["totals"]))
