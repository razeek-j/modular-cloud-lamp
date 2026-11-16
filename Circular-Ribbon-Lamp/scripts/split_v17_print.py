"""Split V17 into printable pieces, orient them, and pack build plates.

Run (needs Blender only for ray casting):
  Blender -b -P scripts/split_v17_print.py

Outputs in development-v17/Print/: one STL per piece (mm, already in print
orientation), 3MF plates for the Kobra S1 Max, Print-map.json and an
assembly map.
"""

import json
import math
import struct
import sys
import zipfile
from pathlib import Path

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import warnings  # noqa: E402
warnings.filterwarnings("ignore")
import v17_geometry as G  # noqa: E402

ROOT = HERE.parent
DEV = ROOT / "development-v17"
OUT = DEV / "Print-files"
OUT.mkdir(exist_ok=True)
P = G.P
BOX = 320.0                 # working box inside the Kobra S1 Max volume, mm
PIECE_MIN, PIECE_MAX = 150.0, 250.0
TAB_LEN, TAB_T, TAB_GAP = 16.0, 1.2, 0.2
BOSS_R, BOSS_HOLE, BOSS_H = 6.0, 2.1, 7.0       # M3 heat-set insert boss
CH_HALF, CH_DEPTH, CH_WALL, CH_FLOOR = 6.0, 8.0, 1.2, 1.2

rings, crossings = G.build(P)
data = json.loads((DEV / "Build-data.json").read_text())
SEC = G.section(P)
K = len(SEC)
H = K // 2


# ------------------------------------------------------------------ helpers
def hidden_normal(r):
    return r["N"] * np.sign(r["N"][:, 2:3] + 1e-9)


def sweep(rings_xyz, closed_section=True, cap=True):
    """Triangles of a swept closed section (stations, k, 3); handles section flips."""
    tris = []
    n, k = rings_xyz.shape[:2]
    for i in range(n - 1):
        a, b = rings_xyz[i], rings_xyz[i + 1]
        # choose the index shift that best aligns consecutive sections
        shift = 0
        if k == K and np.linalg.norm(a - b) > np.linalg.norm(a - np.roll(b, -H, 0)):
            shift = H
        b = np.roll(b, -shift, 0)
        for j in range(k if closed_section else k - 1):
            j2 = (j + 1) % k
            tris.append((a[j], a[j2], b[j2]))
            tris.append((a[j], b[j2], b[j]))
        rings_xyz[i + 1] = b
    if cap:
        for sec, flip in ((rings_xyz[0], True), (rings_xyz[-1], False)):
            c = sec.mean(0)
            for j in range(k):
                t = (c, sec[(j + 1) % k], sec[j]) if flip else (c, sec[j], sec[(j + 1) % k])
                tris.append(t)
    return tris


def tube(p0, axis, r_out, r_in, h, seg=40):
    axis = axis / np.linalg.norm(axis)
    e1 = np.cross(axis, [1, 0, 0])
    if np.linalg.norm(e1) < 0.1:
        e1 = np.cross(axis, [0, 1, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    tris = []
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    def ring(rad, z):
        return [p0 + axis * z + rad * (math.cos(a) * e1 + math.sin(a) * e2) for a in ang]
    ob, ot, ib, it = ring(r_out, 0), ring(r_out, h), ring(r_in, 0), ring(r_in, h)
    for j in range(seg):
        j2 = (j + 1) % seg
        tris += [(ob[j], ob[j2], ot[j2]), (ob[j], ot[j2], ot[j])]           # outer wall
        tris += [(ib[j], it[j2], ib[j2]), (ib[j], it[j], it[j2])]           # inner wall
        tris += [(ot[j], ot[j2], it[j2]), (ot[j], it[j2], it[j])]           # top
        tris += [(ob[j], ib[j2], ob[j2]), (ob[j], ib[j], ib[j2])]           # bottom
    return tris


def write_stl(path, tris):
    tris = np.asarray(tris, dtype=np.float64)
    with open(path, "wb") as f:
        f.write(b"V17 ribbon lamp piece".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            nrm = np.cross(t[1] - t[0], t[2] - t[0])
            ln = np.linalg.norm(nrm)
            nrm = nrm / ln if ln > 0 else nrm
            f.write(struct.pack("<12fH", *nrm, *t[0], *t[1], *t[2], 0))


# ------------------------------------------------------------------ visibility of a seam from the room
EYES = []
for drop in (0.6, 1.1, 1.6):
    for rad in (0.0, 0.6, 1.2, 2.0, 3.0):
        for ang in range(0, 360, 30 if rad else 360):
            a = math.radians(ang)
            EYES.append(Vector((rad * math.cos(a) * 1000, rad * math.sin(a) * 1000, -drop * 1000)))

all_tris = []
for r in rings.values():
    R = G.solid_rings(r, P)
    all_tris += sweep(R.copy(), cap=False)
verts = np.array(all_tris).reshape(-1, 3)
occ = BVHTree.FromPolygons([tuple(v) for v in verts], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(all_tris))])


def seam_visibility(r, i):
    """Fraction of room sight lines that reach the room-facing side of the seam."""
    U = hidden_normal(r)[i]
    hits = tot = 0
    for v in (-0.35, 0.0, 0.35):
        pnt = r["C"][i] + r["D"][i] * (v * r["w"][i]) - U * (P["thickness"] / 2 + 0.3)
        pv = Vector(pnt)
        for e in EYES:
            d = pv - e
            tot += 1
            if occ.ray_cast(e, d.normalized(), d.length - 0.6)[0] is None:
                hits += 1
    return hits / tot


# ------------------------------------------------------------------ choose seams per ring (dynamic programming round the loop)
plan = {}
for name, r in rings.items():
    n = len(r["C"])
    ds = r["L"] / n
    U = hidden_normal(r)
    avoid = np.zeros(n, bool)
    for item in data["seats"] + data["hangers"]:
        if item["ring"] == name:
            for q in range(-8, 9):
                avoid[(item["station"] + q) % n] = True
    cand = [i for i in range(0, n, 3) if abs(r["N"][i][2]) > 0.55 and not avoid[i]]
    cost = {i: seam_visibility(r, i) + 0.15 * (1 - abs(r["N"][i][2])) for i in cand}
    lo_st, hi_st = int(PIECE_MIN / ds), int(PIECE_MAX / ds)
    best = None
    starts = sorted(cand, key=lambda i: cost[i])[:12]
    for s0 in starts:
        # positions measured from s0 going round
        order = sorted(cand, key=lambda i: (i - s0) % n)
        pos = {i: (i - s0) % n for i in order}
        INF = 1e9
        dp = {s0: (0.0, None)}
        for i in order[1:] + [s0]:
            pi = pos[i] if i != s0 or len(dp) == 0 else n
            bestv = (INF, None)
            for j, (v, _) in dp.items():
                pj = pos[j] if j != s0 else 0
                gap = pi - pj
                if lo_st <= gap <= hi_st and v < INF:
                    c = v + cost[i]
                    if c < bestv[0]:
                        bestv = (c, j)
            if i == s0:
                if bestv[1] is not None and (best is None or bestv[0] < best[0]):
                    seq, j = [], bestv[1]
                    while j is not None and j != s0:
                        seq.append(j)
                        j = dp[j][1]
                    best = (bestv[0], [s0] + seq[::-1])
            elif bestv[1] is not None:
                dp[i] = bestv
    assert best, f"no seam plan for ring {name}"
    plan[name] = sorted(best[1])

# ------------------------------------------------------------------ build pieces
led_runs = {}
for run in data["led_runs"]:
    led_runs.setdefault(run["ring"], []).append(np.array(run["stations"]))


def led_frame(r):
    n = len(r["C"])
    side = np.column_stack((r["T"][:, 1], -r["T"][:, 0], np.zeros(n)))
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    side *= np.sign(np.einsum("ij,ij->i", side[:, :2], r["C"][:, :2] - r["centre"]))[:, None]
    inner = -np.sign(np.einsum("ij,ij->i", r["D"], side))[:, None] * r["D"]
    U = hidden_normal(r)
    base = r["C"] + inner * (r["w"] / 2 - 14.0)[:, None] + U * (P["thickness"] / 2)
    return base, U, np.cross(r["T"], U)


CH_PROF = np.array([(-CH_HALF, -0.4), (CH_HALF, -0.4), (CH_HALF, CH_DEPTH), (CH_HALF - CH_WALL, CH_DEPTH),
                    (CH_HALF - CH_WALL, CH_FLOOR), (-CH_HALF + CH_WALL, CH_FLOOR), (-CH_HALF + CH_WALL, CH_DEPTH),
                    (-CH_HALF, CH_DEPTH)])


def channel_tris(r, idx):
    base, U, S = led_frame(r)
    rr = base[idx][:, None, :] + CH_PROF[None, :, 0:1] * S[idx][:, None, :] + CH_PROF[None, :, 1:2] * U[idx][:, None, :]
    tris = []
    for i in range(len(idx) - 1):
        for j in range(8):
            j2 = (j + 1) % 8
            tris += [(rr[i, j], rr[i, j2], rr[i + 1, j2]), (rr[i, j], rr[i + 1, j2], rr[i + 1, j])]
    for sec, flip in ((rr[0], True), (rr[-1], False)):
        for quad in ((0, 1, 4, 5), (1, 2, 3, 4), (0, 5, 6, 7)):      # the U outline, as three convex quads
            q = [sec[x] for x in quad]
            if flip:
                q = q[::-1]
            tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
    # closed end plates (separate overlapping shells) so the channel ends are walled
    for i, sgn in ((idx[0], 1.0), (idx[-1], -1.0)):
        o = base[i] + r["T"][i] * sgn * 0.9      # inset 0.3 mm so no corner coincides with the cap
        tris += box(o, S[i], U[i], r["T"][i], (-CH_HALF, CH_HALF), (-0.4, CH_DEPTH), (-0.6, 0.6))
    return tris


def box(o, ex, ey, ez, rx, ry, rz):
    c = [o + ex * x + ey * y + ez * z for x in rx for y in ry for z in rz]   # 8 corners, index = 4x+2y+z
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for f in faces:
        q = [c[k] for k in f]
        tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
    return tris


def tab_tris(r, i_seam, direction):
    """Lap tab on the hidden face, reaching TAB_LEN past the seam onto the next piece."""
    n = len(r["C"])
    ds = r["L"] / n
    steps = int(round(TAB_LEN / ds))
    idx = [(i_seam + direction * q) % n for q in range(-1, steps + 1)]
    U = hidden_normal(r)
    halfw = r["w"] / 2 - P["bead_r"] - 1.0
    secs = []
    for q, i in enumerate(idx):
        own = q == 0                      # first station sits on its own piece: no gap, fused
        z0 = P["thickness"] / 2 + (0.0 if own else TAB_GAP)
        c = r["C"][i]
        d, u = r["D"][i], U[i]
        hw = halfw[i]
        secs.append([c - d * hw + u * z0, c + d * hw + u * z0, c + d * hw + u * (z0 + TAB_T), c - d * hw + u * (z0 + TAB_T)])
    secs = np.array(secs)
    tris = []
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        if np.dot(r["D"][idx[i]], r["D"][idx[i + 1]]) < 0:
            b = b[[1, 0, 3, 2]]
            secs[i + 1] = b
        for j in range(4):
            j2 = (j + 1) % 4
            tris += [(a[j], a[j2], b[j2]), (a[j], b[j2], b[j])]
    for sec, flip in ((secs[0], True), (secs[-1], False)):
        q = list(sec[::-1]) if flip else list(sec)
        tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
    return tris


pieces = []
for name, seams in plan.items():
    r = rings[name]
    n = len(r["C"])
    ds = r["L"] / n
    U = hidden_normal(r)
    R = G.solid_rings(r, P)
    for pi, a in enumerate(seams):
        b = seams[(pi + 1) % len(seams)]
        span = (b - a) % n
        idx = np.array([(a + q) % n for q in range(span + 1)])
        tris = sweep(R[idx].copy())
        # tab at the far end of this piece, lapping onto the next piece
        tris += tab_tris(r, b, +1)
        # bosses for seats and hangers that fall on this piece
        bosses = []
        for item in data["seats"] + data["hangers"]:
            if item["ring"] == name and (item["station"] - a) % n <= span:
                i = item["station"]
                v = item.get("across", 0.0)
                p0 = r["C"][i] + r["D"][i] * (v * (r["w"][i] - 2 * P["bead_r"])) + U[i] * (P["thickness"] / 2 - 0.4)
                tris += tube(p0, U[i], BOSS_R, BOSS_HOLE, BOSS_H + 0.4)
                bosses.append("seat" if item in data["seats"] else "hanger")
        # LED channel share
        led_len = 0.0
        for run in led_runs.get(name, []):
            inside = [s for s in run if (s - a) % n <= span]
            if len(inside) > 3:
                ii = np.array(inside)
                tris += channel_tris(r, ii)
                led_len += (len(ii) - 1) * ds
        tris = np.array(tris)
        pieces.append(dict(id=f"{name}{pi + 1:02d}", ring=name, stations=[int(a), int(b)],
                           length_mm=round(span * ds), tris=tris, bosses=bosses,
                           led_channel_mm=round(led_len), mid=r["C"][idx[len(idx) // 2]].tolist(),
                           D=r["D"][idx].mean(0), N=U[idx].mean(0)))


# ------------------------------------------------------------------ orientation and fit
def rot_to(a, b=np.array([0, 0, 1.0])):
    a = a / np.linalg.norm(a)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def overhang(tris, Rm):
    t = tris @ Rm.T
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    area = np.linalg.norm(nrm, axis=1) / 2
    nz = nrm[:, 2] / np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)
    zmin = t[:, :, 2].min()
    on_bed = t[:, :, 2].max(1) < zmin + 0.4
    over = (nz < -0.707) & ~on_bed
    return float(area[over].sum()), float(area.sum())


for pc in pieces:
    tris = pc["tris"]
    cands = []
    D, N = pc["D"], pc["N"]
    for name_, d in (("edge", D), ("edge", -D), ("flat", N), ("flat", -N)):
        if np.linalg.norm(d) < 1e-3:
            continue
        for tilt in (0, 15, 30):
            for sgn in (1, -1):
                if tilt == 0 and sgn == -1:
                    continue
                ax = np.cross(d, N if name_ == "edge" else D)
                if np.linalg.norm(ax) < 1e-6:
                    continue
                ax /= np.linalg.norm(ax)
                th = math.radians(tilt * sgn)
                dd = d * math.cos(th) + np.cross(ax, d) * math.sin(th)
                Rm = rot_to(-dd)              # build direction: dd points down to the bed... use -dd as up
                ov, tot = overhang(tris, Rm)
                # bonus for edge-standing (layer lines run along the ribbon)
                score = ov / tot - (0.08 if name_ == "edge" else 0)
                cands.append((score, ov / tot, name_, tilt * sgn, Rm))
    cands.sort(key=lambda c: c[0])
    score, ovf, mode, tilt, Rm = cands[0]
    t = tris @ Rm.T
    # spin about Z for the smallest footprint
    best = None
    for ang in range(0, 180, 1):
        a = math.radians(ang)
        Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        tt = t @ Rz.T
        ext = np.ptp(tt.reshape(-1, 3), axis=0)
        key = (max(ext[0], ext[1]) > BOX, ext[0] * ext[1])     # fit first, then smallest footprint
        if best is None or key < best[0]:
            best = (key, Rz, ext)
    Rz = best[1]
    t = t @ Rz.T
    mn = t.reshape(-1, 3).min(0)
    mx = t.reshape(-1, 3).max(0)
    t = t - np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    ext = np.ptp(t.reshape(-1, 3), axis=0)
    pc.update(print_tris=t, mode=("standing on its edge" if mode == "edge" else "lying on its face"),
              tilt_deg=tilt, overhang_fraction=round(ovf, 3), bbox_mm=[round(float(x)) for x in ext],
              fits=bool(max(ext[0], ext[1]) <= BOX and ext[2] <= BOX))
    write_stl(OUT / f"{pc['id']}.stl", t)
    # skin volume estimate (closed meshes): divergence theorem
    v = np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6
    pc["volume_cm3"] = round(abs(float(v)) / 1000, 1)
    pc["mass_g_petg"] = round(abs(float(v)) / 1000 * 1.27)

# ------------------------------------------------------------------ plates (shelf packing on the 320 mm working box) and 3MF
order = sorted(pieces, key=lambda p: -p["bbox_mm"][1])
plates, cur, x, y, row_h = [], [], 0.0, 0.0, 0.0
GAP = 8.0
for pc in order:
    w, h = pc["bbox_mm"][0] + GAP, pc["bbox_mm"][1] + GAP
    if x + w > BOX + GAP:
        x, y, row_h = 0.0, y + row_h, 0.0
    if y + h > BOX + GAP:
        plates.append(cur)
        cur, x, y, row_h = [], 0.0, 0.0, 0.0
    cur.append((pc, x + w / 2 - GAP / 2, y + h / 2 - GAP / 2))
    x += w
    row_h = max(row_h, h)
if cur:
    plates.append(cur)


def write_3mf(path, items):
    objs, build = [], []
    for oid, (pc, cx, cy) in enumerate(items, start=1):
        t = pc["print_tris"].reshape(-1, 3)
        vs, idx = np.unique(np.round(t, 4), axis=0, return_inverse=True)
        tri = idx.reshape(-1, 3)
        vxml = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in vs)
        txml = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tri if len({a, b, c}) == 3)
        objs.append(f'<object id="{oid}" name="{pc["id"]}" type="model"><mesh><vertices>{vxml}</vertices>'
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
    plate_info.append(dict(file=fname, pieces=[pc["id"] for pc, _, _ in items]))

# ------------------------------------------------------------------ map
pmap = dict(
    working_box_mm=BOX, piece_length_range_mm=[PIECE_MIN, PIECE_MAX],
    joint=dict(type="bonded lap tab on the ceiling-facing skin", tab_length_mm=TAB_LEN, tab_thickness_mm=TAB_T,
               glue_gap_mm=TAB_GAP, registration="tab edges sit between the edge beads"),
    bosses=dict(type="M3 heat-set insert boss", outer_d_mm=2 * BOSS_R, hole_d_mm=2 * BOSS_HOLE, height_mm=BOSS_H),
    led_channel=dict(width_mm=2 * CH_HALF, depth_mm=CH_DEPTH, note="printed with the piece on the ceiling-facing skin"),
    pieces=[{k: v for k, v in pc.items() if k not in ("tris", "print_tris", "D", "N")} for pc in pieces],
    plates=plate_info,
    totals=dict(pieces=len(pieces), plates=len(plates),
                mass_g_petg=int(sum(pc["mass_g_petg"] for pc in pieces)),
                all_fit=all(pc["fits"] for pc in pieces),
                max_overhang_fraction=max(pc["overhang_fraction"] for pc in pieces)),
)
(DEV / "Print-map.json").write_text(json.dumps(pmap, indent=1))
print("PRINT " + json.dumps(pmap["totals"]))
for pc in pieces:
    print(pc["id"], pc["length_mm"], pc["mode"], pc["tilt_deg"], pc["overhang_fraction"], pc["bbox_mm"], pc["fits"], pc["mass_g_petg"], pc["bosses"], pc["led_channel_mm"])
