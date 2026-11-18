"""V20 print-part geometry helpers (numpy only, millimetres): studs, lap tabs, LED channels, hub parts.

All functions return triangle arrays (n, 3, 3) with outward-facing windings, ready for STL.
"""

import math

import numpy as np

import v20_geometry as G

P = G.P
TAB_LEN, TAB_T, TAB_GAP = 16.0, 1.2, 0.2
STUD_R, STUD_GAP, STUD_EMBED = 4.5, 0.3, 0.6
CH_HALF, CH_DEPTH, CH_WALL, CH_FLOOR = 6.0, 8.0, 1.2, 1.2


def quads_to_tris(quads):
    out = []
    for q in quads:
        out.append((q[0], q[1], q[2]))
        out.append((q[0], q[2], q[3]))
    return out


LAP_LEN, LAP_GAP = 18.0, 0.15


def orient_consistent(tris):
    """Flip triangles so every shared edge is traversed in opposite directions, then make the volume positive."""
    from collections import defaultdict, deque
    tris = np.array(tris, float)
    pts = np.round(tris.reshape(-1, 3), 4)
    uniq, inv = np.unique(pts, axis=0, return_inverse=True)
    f = inv.reshape(-1, 3).copy()
    edge_faces = defaultdict(list)
    for fi, (a, b, c) in enumerate(f):
        for u, v in ((a, b), (b, c), (c, a)):
            edge_faces[(min(u, v), max(u, v))].append(fi)
    flipped = np.zeros(len(f), bool)
    seen = np.zeros(len(f), bool)

    def directed(fi):
        a, b, c = f[fi]
        if flipped[fi]:
            a, b, c = a, c, b
        return ((a, b), (b, c), (c, a))

    for start in range(len(f)):
        if seen[start]:
            continue
        seen[start] = True
        dq = deque([start])
        while dq:
            fi = dq.popleft()
            for (u, v) in directed(fi):
                nbrs = edge_faces[(min(u, v), max(u, v))]
                if len(nbrs) != 2:
                    continue
                gi = nbrs[0] if nbrs[1] == fi else nbrs[1]
                if seen[gi]:
                    continue
                seen[gi] = True
                # neighbour must traverse the edge as (v, u)
                if (u, v) in directed(gi):
                    flipped[gi] = True
                dq.append(gi)
    out = tris.copy()
    out[flipped] = out[flipped][:, [0, 2, 1], :]
    vol = np.einsum("ij,ij->i", out[:, 0], np.cross(out[:, 1], out[:, 2])).sum() / 6
    if vol < 0:
        out = out[:, [0, 2, 1], :]
    return out


def shell_tris(p, rows, hv, hh):
    """Closed-solid triangles of petal rows `rows` (list of row indices; a row may repeat to make a step).
    hv, hh: offsets of the visible / hidden face along the normal for each listed row.
    Returns tris (n,3,3) and kinds."""
    rows = np.asarray(rows)
    S, N = p["S"][rows], p["N"][rows]
    vis = S + N * np.asarray(hv)[:, None, None]
    hid = S + N * np.asarray(hh)[:, None, None]
    verts, quads, kind = G.shell_from_grids(vis, hid)
    tris, kinds = [], []
    for q, k in zip(quads, kind):
        for tri in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
            t = np.array([verts[tri[0]], verts[tri[1]], verts[tri[2]]])
            if np.linalg.norm(np.cross(t[1] - t[0], t[2] - t[0])) > 1e-9:
                tris.append(t)
                kinds.append(k)
    return orient_consistent(np.array(tris)), kinds


def slab(bot, top):
    """Closed solid between two point grids bot, top of shape (nr, nc, 3). Outward faces for a grid whose
    (row, col) order gives upward-facing winding on `top`."""
    nr, nc = bot.shape[:2]
    t = []

    def face(g, flip):
        for i in range(nr - 1):
            for j in range(nc - 1):
                a, b, c, d = g[i, j], g[i + 1, j], g[i + 1, j + 1], g[i, j + 1]
                if flip:
                    t.extend([(a, c, b), (a, d, c)])
                else:
                    t.extend([(a, b, c), (a, c, d)])

    face(top, False)
    face(bot, True)
    # four side walls (canonical frame: row = +x, col = +y, bot -> top = +z)
    for i in range(nr - 1):
        b0, b1, t0, t1 = bot[i, 0], bot[i + 1, 0], top[i, 0], top[i + 1, 0]          # y min, outward -y
        t.extend([(b0, b1, t1), (b0, t1, t0)])
        b0, b1, t0, t1 = bot[i, -1], bot[i + 1, -1], top[i, -1], top[i + 1, -1]      # y max, outward +y
        t.extend([(b0, t1, b1), (b0, t0, t1)])
    for j in range(nc - 1):
        b0, b1, t0, t1 = bot[0, j], bot[0, j + 1], top[0, j], top[0, j + 1]          # x min, outward -x
        t.extend([(b0, t1, b1), (b0, t0, t1)])
        b0, b1, t0, t1 = bot[-1, j], bot[-1, j + 1], top[-1, j], top[-1, j + 1]      # x max, outward +x
        t.extend([(b0, b1, t1), (b0, t1, t0)])
    return np.array(t)


def orient_solid(tris):
    """Make a closed triangle soup outward-facing (signed volume positive)."""
    v = np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6
    return tris if v >= 0 else tris[:, ::-1, :].copy()


def lap_tab(p, b_row, s_cut, cols):
    """Bonded lap tab on the hidden face: fused to the piece before the cut, hovering TAB_GAP over the next piece."""
    s = p["s"]
    rows = np.where((s >= s_cut - 6.0) & (s <= s_cut + TAB_LEN))[0]
    rows = rows[rows < len(s)]
    S, N = p["S"][np.ix_(rows, cols)], p["N"][np.ix_(rows, cols)]
    g = np.where(s[rows] <= s_cut + 1e-6, -0.25, TAB_GAP)[:, None, None]
    t = P["thickness"] / 2
    bot = S - N * (t + g)
    top = bot - N * TAB_T
    return orient_solid(slab(bot, top))


CH_PROF = np.array([(-CH_HALF, -0.4), (CH_HALF, -0.4), (CH_HALF, CH_DEPTH), (CH_HALF - CH_WALL, CH_DEPTH),
                    (CH_HALF - CH_WALL, CH_FLOOR), (-CH_HALF + CH_WALL, CH_FLOOR), (-CH_HALF + CH_WALL, CH_DEPTH),
                    (-CH_HALF, CH_DEPTH)])


def channel_frame(p, col_y_frac=-0.72):
    """Channel base points, up (hidden-side) direction and side direction along a petal, on the covered edge."""
    S, N = p["S"], p["N"]
    ns, nv = S.shape[:2]
    # choose the grid column nearest the requested fraction of the covered half-width
    jc = int(round((nv - 1) / 2 * (1 + col_y_frac)))
    base = S[:, jc] - N[:, jc] * (P["thickness"] / 2)
    U = -N[:, jc]
    T = np.gradient(S[:, jc], axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    Sd = np.cross(T, U)
    Sd /= np.linalg.norm(Sd, axis=1, keepdims=True)
    return base, U, Sd, jc


def channel_tris(p, rows, col_y_frac=-0.72):
    base, U, Sd, jc = channel_frame(p, col_y_frac)
    rr = base[rows][:, None, :] + CH_PROF[None, :, 0:1] * Sd[rows][:, None, :] + CH_PROF[None, :, 1:2] * U[rows][:, None, :]
    t = []
    for i in range(len(rows) - 1):
        for j in range(8):
            j2 = (j + 1) % 8
            t.extend([(rr[i, j], rr[i, j2], rr[i + 1, j2]), (rr[i, j], rr[i + 1, j2], rr[i + 1, j])])
    for sec, flip in ((rr[0], True), (rr[-1], False)):
        for quad in ((0, 1, 4, 5), (1, 2, 3, 4), (0, 5, 6, 7)):
            q = [sec[x] for x in quad]
            if flip:
                q = q[::-1]
            t.extend([(q[0], q[1], q[2]), (q[0], q[2], q[3])])
    return orient_solid(np.array(t))


def stud_tris(x, y, z_bot_fn, z_top_fn, n=20):
    """Vertical stud: conformal bottom (embedded in the lower sheet) and top (STUD_GAP under the upper sheet)."""
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    b, t = [], []
    for a in ang:
        px, py = x + STUD_R * math.cos(a), y + STUD_R * math.sin(a)
        b.append((px, py, z_bot_fn(px, py) - STUD_EMBED))
        t.append((px, py, z_top_fn(px, py) - STUD_GAP))
    cb = np.mean(b, axis=0)
    ct = np.mean(t, axis=0)
    tris = []
    for k in range(n):
        k2 = (k + 1) % n
        tris.extend([(b[k], b[k2], t[k2]), (b[k], t[k2], t[k]), (ct, t[k], t[k2]), (cb, b[k2], b[k])])
    return orient_solid(np.array(tris))


def revolve(profile, seg=120):
    """Solid of revolution about z. profile = closed polygon of (r, d); d is drop below the ceiling (z = -d)."""
    prof = np.array(profile, float)
    # orient the polygon so the swept solid is outward-facing: test by signed volume afterwards
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    n = len(prof)
    ring = lambda a: [(r * math.cos(a), r * math.sin(a), -d) for r, d in prof]
    rings = [ring(a) for a in ang]
    tris = []
    for k in range(seg):
        k2 = (k + 1) % seg
        for j in range(n):
            j2 = (j + 1) % n
            a, b, c, d = rings[k][j], rings[k][j2], rings[k2][j2], rings[k2][j]
            if prof[j, 0] < 1e-9 and prof[j2, 0] < 1e-9:
                continue
            if prof[j, 0] < 1e-9:
                tris.append((a, b, c))
            elif prof[j2, 0] < 1e-9:
                tris.append((a, c, d))
            else:
                tris.extend([(a, b, c), (a, c, d)])
    return orient_solid(np.array(tris))


def write_stl(path, tris, header=b"V20 rosette lamp part"):
    import struct
    tris = np.asarray(tris, dtype=np.float64)
    with open(path, "wb") as f:
        f.write(header.ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            nrm = np.cross(t[1] - t[0], t[2] - t[0])
            ln = np.linalg.norm(nrm)
            nrm = nrm / ln if ln > 0 else nrm
            f.write(struct.pack("<12fH", *nrm, *t[0], *t[1], *t[2], 0))


def unmatched_edges(tris):
    """Number of directed edges without an opposite partner (0 for a closed, consistently wound mesh)."""
    from collections import Counter
    pts = np.round(np.asarray(tris).reshape(-1, 3), 3)
    uniq, inv = np.unique(pts, axis=0, return_inverse=True)
    f = inv.reshape(-1, 3)
    c = Counter()
    for a, b, d in f:
        if a == b or b == d or a == d:
            continue
        c[(a, b)] += 1
        c[(b, d)] += 1
        c[(d, a)] += 1
    return sum(1 for (a, b), n in c.items() if c.get((b, a), 0) != n)
