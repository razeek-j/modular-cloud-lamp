"""V17 "Borromean" ribbon lamp: three woven ribbon rings, deliberate curves.

Design rules (no random terms anywhere):

1. Plan. Each ribbon is a closed ellipse, so its plan curvature changes
   monotonically between four vertices and never wiggles. The three ellipses
   overlap in the classic Borromean arrangement: each pair crosses exactly
   twice. Their sizes step down by a constant ratio (1 : 0.9 : 0.81) and
   their centres sit at deliberately unequal angles, which makes the outline
   round but not regular.
2. Weave. The over/under order is cyclic: A passes over B, B over C, C over A.
   That is the Borromean rings pattern: no two rings are linked, yet the three
   cannot be separated. Each ring is therefore high on one side and low on the
   other, so its height is a single smooth wave, fitted with the two lowest
   Fourier harmonics only.
3. Lie. A ring lies flat where it passes over or under another ring, and
   rolls up into a leaning wall on its free outer arc, so its inside face
   shows like the hairpin loops in the reference.
4. Width. Width trades with tilt so the depth stays fixed: a ribbon lying flat
   is wide (up to 250 mm), and as it rolls up it narrows to the wall height
   (120 mm). The broad flat areas therefore fall in the woven middle.
5. Section. 1.8 mm skin with a rounded 3.2 mm bead along both edges, for a
   crisp finished edge and a stiffer ribbon.

Units: millimetres; z = 0 is the ceiling, negative is downward.
"""

import numpy as np

RINGS = [
    # name, centre angle (deg), centre distance, semi-axis a, b, ellipse rotation (deg),
    # flat width, wall lean (deg past vertical, top edge inward)
    dict(name="A", ang=96.0, d=237.0, a=403.0, b=336.0, rot=8.0, w_flat=195.0, hand=1, half_twists=3),
    dict(name="B", ang=222.0, d=224.0, a=363.0, b=302.0, rot=-28.0, w_flat=180.0, hand=-1, half_twists=3),
    dict(name="C", ang=338.0, d=213.0, a=327.0, b=272.0, rot=50.0, w_flat=165.0, hand=1, half_twists=3),
]
OVER = {("A", "B"), ("B", "C"), ("C", "A")}       # (upper, lower) at both crossings

P = dict(
    ds=3.0,
    solve=True,
    solve_rounds=4,
    solve_step=4,           # stations between solver samples (about 12 mm)
    solve_across=11,
    spline_pitch=85.0,      # mm of ribbon per height control point
    plan_touch=9.0,         # sample points this close in plan count as stacked
    layer_gap=18.0,         # mid-surface to mid-surface where ribbons stack
    bottom_limit=-155.0,
    track_weight=1.2,       # pull toward the designed weave heights
    seat_gap=8.0,           # ribbon top face to ceiling-disc underside at the seats
    w_core=105.0,           # flat width at the lamp centre
    r_core0=150.0,
    r_core1=330.0,
    scale=0.92,             # overall plan scale                # station spacing along each ring
    z_hi=-42.0,             # mid-surface of a flat ribbon passing over
    z_lo=-118.0,            # mid-surface of a flat ribbon passing under
    twist_ease=0.30,
    width_ease=0.30,        # width settles over the same stretch as the twist eases in
    w_twist=128.0,          # constant width through the half-twists
    wall_h=120.0,           # vertical extent of a standing wall
    top_limit=-20.0,        # nothing above this (ceiling gap)
    wall_lean=15.0,         # degrees past vertical; top edge leans inward
    r_wall0=330.0,          # rolling up starts beyond this radius from the lamp centre
    r_wall1=470.0,          # fully upright beyond this radius
    cross_clear=150.0,      # stay flat within this arc distance of a crossing
    thickness=1.8,
    bead_r=1.6,
    profile_n=48,           # stations across the flat part of the section
    canopy_r=130.0,
    canopy_h=30.0,
)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * x * (10 + x * (-15 + 6 * x))


def ellipse_plan(r, ds):
    u = np.linspace(0, 2 * np.pi, 20000, endpoint=False)
    th = np.radians(r["rot"])
    ca, sa = np.cos(th), np.sin(th)
    ex, ey = r["a"] * np.cos(u), r["b"] * np.sin(u)
    c = r["d"] * np.array([np.cos(np.radians(r["ang"])), np.sin(np.radians(r["ang"]))])
    x = c[0] + ca * ex - sa * ey
    y = c[1] + sa * ex + ca * ey
    seg = np.hypot(np.diff(np.r_[x, x[0]]), np.diff(np.r_[y, y[0]]))
    s = np.r_[0, np.cumsum(seg)[:-1]]
    L = seg.sum()
    n = int(round(L / ds))
    sn = np.linspace(0, L, n, endpoint=False)
    return np.column_stack((np.interp(sn, s, x, period=L), np.interp(sn, s, y, period=L))), L, c


def crossings(pa, pb):
    """Plan intersections of two closed polylines: (index fraction in a, in b)."""
    A0, A1 = pa, np.roll(pa, -1, 0)
    B0, B1 = pb, np.roll(pb, -1, 0)
    out = []
    da = A1 - A0
    for j in range(len(pb)):
        db = B1[j] - B0[j]
        den = da[:, 0] * db[1] - da[:, 1] * db[0]
        w = B0[j] - A0
        with np.errstate(divide="ignore", invalid="ignore"):
            ta = (w[:, 0] * db[1] - w[:, 1] * db[0]) / den
            tb = (w[:, 0] * da[:, 1] - w[:, 1] * da[:, 0]) / den
        hit = np.where((ta >= 0) & (ta < 1) & (tb >= 0) & (tb < 1))[0]
        for i in hit:
            out.append((i + ta[i], j + tb[i]))
    return out


def fourier_fit(L, keys, harmonics=2):
    """Smoothest low-order periodic curve through (s, z) keys."""
    cols = [lambda s: np.ones_like(s)]
    pen = [0.0]
    for h in range(1, harmonics + 1):
        cols += [lambda s, h=h: np.cos(2 * np.pi * h * s / L), lambda s, h=h: np.sin(2 * np.pi * h * s / L)]
        pen += [float(h) ** 4] * 2
    s = np.array([k[0] for k in keys])
    z = np.array([k[1] for k in keys])
    A = np.column_stack([f(s) for f in cols])
    W = np.diag(np.array(pen) + 1e-9)
    # minimise c^T W c subject to A c = z
    K = np.block([[2 * W, A.T], [A, np.zeros((len(z), len(z)))]])
    sol = np.linalg.lstsq(K, np.r_[np.zeros(len(pen)), z], rcond=None)[0]
    coef = sol[:len(pen)]
    return lambda s: np.column_stack([f(np.asarray(s, float)) for f in cols]) @ coef


def hold_levels(name, s, L, keys, plans, p):
    """Hold each crossing level across the whole plan overlap with the partner
    ribbon, then ease (smootherstep, C2) between neighbouring holds."""
    xy = plans[name]["xy"]
    w_here = plans[name]["spec"]["w_flat"]
    holds = []
    for sk, zk, other in keys:
        oxy = plans[other]["xy"]
        reach = (w_here + plans[other]["spec"]["w_flat"]) / 2 + p["overlap_margin"]
        # stations of this ring whose centreline is within reach of the other ring
        d = np.sqrt(((xy[:, None, :] - oxy[None, ::4, :]) ** 2).sum(-1)).min(1)
        inside = d < reach
        i0 = int(round(sk / (L / len(xy)))) % len(xy)
        a = b = i0
        while inside[(a - 1) % len(xy)] and (i0 - a) < len(xy) // 2:
            a -= 1
        while inside[(b + 1) % len(xy)] and (b - i0) < len(xy) // 2:
            b += 1
        ds = L / len(xy)
        holds.append((a * ds, b * ds, zk))
    holds.sort()
    z = np.empty_like(s)
    m = len(holds)
    for i in range(m):
        a, b, zk = holds[i]
        na, nb, nz = holds[(i + 1) % m]
        if i == m - 1:
            na += L
            nb += L
        # hold
        for sh in (0, L, -L):
            sel = (s + sh >= a) & (s + sh <= b)
            z[sel] = zk
            g0, g1 = b, na
            sel = (s + sh > g0) & (s + sh < g1)
            u = (s[sel] + sh - g0) / max(g1 - g0, 1e-6)
            z[sel] = zk + (nz - zk) * _smoothstep(u)
    return z


def eased_ramp(u, e):
    """0 -> 1 with a constant rate in the middle and smootherstep-eased ends."""
    uu = np.linspace(0, 1, 2001)
    f = _smoothstep(np.minimum(uu, 1 - uu) / e)
    F = np.r_[0, np.cumsum((f[1:] + f[:-1]) / 2)]
    F /= F[-1]
    return np.interp(np.clip(u, 0, 1), uu, F)


def eased_keys(s, L, keys):
    """Height through the crossing keys, eased with smootherstep (C2, level at each key)."""
    ks = sorted(keys)
    sk = np.array([k[0] for k in ks])
    zk = np.array([k[1] for k in ks])
    sk_ext = np.r_[sk[-1] - L, sk, sk[0] + L]
    zk_ext = np.r_[zk[-1], zk, zk[0]]
    j = np.searchsorted(sk_ext, s, side="right") - 1
    u = (s - sk_ext[j]) / (sk_ext[j + 1] - sk_ext[j])
    return zk_ext[j] + (zk_ext[j + 1] - zk_ext[j]) * _smoothstep(u)


def periodic_spline(s, L, keys):
    """Periodic C2 cubic spline through the crossing keys (no level shelves)."""
    ks = sorted(keys)
    x = np.array([k[0] for k in ks])
    y = np.array([k[1] for k in ks])
    m = len(x)
    h = np.diff(np.r_[x, x[0] + L])
    A = np.zeros((m, m))
    r = np.zeros(m)
    for i in range(m):
        hp, hn = h[i - 1], h[i]
        A[i, i - 1] += hp
        A[i, i] += 2 * (hp + hn)
        A[i, (i + 1) % m] += hn
        r[i] = 6 * ((y[(i + 1) % m] - y[i]) / hn - (y[i] - y[i - 1]) / hp)
    M = np.linalg.solve(A, r)
    j = np.searchsorted(x, s % L, side="right") - 1          # -1 means the wrap span
    j = np.where(j < 0, m - 1, j)
    x0 = x[j]
    t = (s - x0) % L
    hj = h[j]
    y0, y1 = y[j], y[(j + 1) % m]
    M0, M1 = M[j], M[(j + 1) % m]
    return (M0 * (hj - t) ** 3 / (6 * hj) + M1 * t ** 3 / (6 * hj)
            + (y0 / hj - M0 * hj / 6) * (hj - t) + (y1 / hj - M1 * hj / 6) * t)


def lowpass(x, sigma):
    n = len(x)
    k = np.arange(-int(4 * sigma), int(4 * sigma) + 1)
    ker = np.exp(-0.5 * (k / sigma) ** 2)
    ker /= ker.sum()
    full = np.zeros(n)
    full[k % n] = ker
    return np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(full)))


def build(p=P, rings=RINGS):
    plans = {}
    for r in rings:
        r = dict(r, d=r["d"] * p["scale"], a=r["a"] * p["scale"], b=r["b"] * p["scale"])
        xy, L, c = ellipse_plan(r, p["ds"])
        plans[r["name"]] = dict(xy=xy, L=L, centre=c, spec=r, ds=L / len(xy))
    # crossings and over/under keys
    keys = {k: [] for k in plans}
    cross_list = []
    names = list(plans)
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = names[i], names[j]
            for fa, fb in crossings(plans[a]["xy"], plans[b]["xy"]):
                up = a if (a, b) in OVER else b
                sa, sb = fa * plans[a]["ds"], fb * plans[b]["ds"]
                keys[a].append((sa, p["z_hi"] if up == a else p["z_lo"], b))
                keys[b].append((sb, p["z_hi"] if up == b else p["z_lo"], a))
                pt = plans[a]["xy"][int(fa) % len(plans[a]["xy"])]
                cross_list.append(dict(rings=(a, b), upper=up, xy=[round(float(pt[0])), round(float(pt[1]))],
                                       s={a: sa, b: sb}))
    out = {}
    for k, pl in plans.items():
        xy, L = pl["xy"], pl["L"]
        n = len(xy)
        s = np.arange(n) * pl["ds"]
        # Height: a blend of the C2 spline (keeps flowing through crossings) and
        # the eased curve (level at crossings, no overshoot on the long arc).
        z_keys = eased_keys(s, L, [kk[:2] for kk in keys[k]])
        # Half-twist on the long free arc: the ribbon lies flat at both ends of
        # that arc and rolls over once (0 -> 180 deg) in between, so each ring
        # is a Moebius band. Flat everywhere else, including every crossing.
        ks = sorted(kk[0] for kk in keys[k])
        gaps = [((ks[(i + 1) % len(ks)] - ks[i]) % L, ks[i]) for i in range(len(ks))]
        g_len, g_start = max(gaps)
        u = ((s - g_start) % L - p["cross_clear"]) / (g_len - 2 * p["cross_clear"])
        # Even rhythm of half-twists: constant twist rate with eased ends.
        hand = pl["spec"]["hand"]
        psi = hand * np.pi * pl["spec"]["half_twists"] * eased_ramp(u, p["twist_ease"])
        roll = np.abs(np.sin(psi))
        # width trades with tilt so the vertical extent stays at the wall height
        sin_t = np.abs(np.sin(psi))
        # Slimmer at the heart of the lamp, broadening outward like a petal.
        rr = np.hypot(xy[:, 0], xy[:, 1])
        w_flat = p["w_core"] + (pl["spec"]["w_flat"] - p["w_core"]) * _smoothstep(
            (rr - p["r_core0"]) / (p["r_core1"] - p["r_core0"]))
        w = w_flat - (w_flat - p["wall_h"]) * _smoothstep(sin_t / 0.92)
        # Through the twisting arc the width is constant, so the edges sweep as
        # clean helices instead of pulsing; it is wider only where the ribbon lies flat.
        plateau_w = _smoothstep(np.minimum(u, 1 - u) / p["width_ease"]) * ((u > 0) & (u < 1))
        w = (1 - plateau_w) * w + plateau_w * p["w_twist"]
        w = lowpass(w, sigma=30.0 / p["ds"])
        # On the twisting arc the centreline holds the middle of the depth band,
        # so every half-twist turns about a level axis (no bobbing).
        z_mid = 0.5 * (p["top_limit"] + p["bottom_limit"])
        plateau = _smoothstep(np.minimum(u, 1 - u) / 0.12) * ((u > 0) & (u < 1))
        z = (1 - plateau) * z_keys + plateau * z_mid
        C = np.column_stack((xy, z))
        T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
        # outward side direction (away from the ring's own centre), square to the path
        side = _unit(np.column_stack((T[:, 1], -T[:, 0], np.zeros(n))))
        outward = xy - pl["centre"]
        side *= np.sign(np.einsum("ij,ij->i", side[:, :2], outward))[:, None]
        D = np.cos(psi)[:, None] * side + np.sin(psi)[:, None] * np.array([0, 0, 1.0])
        D -= np.einsum("ij,ij->i", D, T)[:, None] * T
        D = _unit(D)
        N = _unit(np.cross(T, D))
        out[k] = dict(C=C, T=T, D=D, N=N, w=w, psi=psi, s=s, L=L, keys=keys[k], centre=pl["centre"], z_target=z.copy(),
                      twist=(g_start, g_len), moebius=True)
    if p["solve"]:
        for _ in range(p["solve_rounds"]):
            solve_heights(out, p)
            refresh_frames(out, plans)
    return out, cross_list


SOLVE_INFO = {}


def bspline_basis(s, L, K):
    """Periodic uniform cubic B-spline basis matrix (len(s) x K)."""
    u = (s / L * K) % K
    i = np.floor(u).astype(int)
    t = u - i
    w = np.column_stack(((1 - t) ** 3 / 6, (3 * t ** 3 - 6 * t ** 2 + 4) / 6,
                         (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6, t ** 3 / 6))
    B = np.zeros((len(s), K))
    for c in range(4):
        np.add.at(B, (np.arange(len(s)), (i - 1 + c) % K), w[:, c])
    return B


def refresh_frames(out, plans):
    for k, r in out.items():
        C, psi = r["C"], r["psi"]
        n = len(C)
        T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
        side = _unit(np.column_stack((T[:, 1], -T[:, 0], np.zeros(n))))
        side *= np.sign(np.einsum("ij,ij->i", side[:, :2], C[:, :2] - plans[k]["centre"]))[:, None]
        D = np.cos(psi)[:, None] * side + np.sin(psi)[:, None] * np.array([0, 0, 1.0])
        D -= np.einsum("ij,ij->i", D, T)[:, None] * T
        D = _unit(D)
        r.update(T=T, D=D, N=_unit(np.cross(T, D)))


def solve_heights(out, p):
    """Smoothest centreline heights (periodic cubic B-splines) that keep every
    woven overlap at least p['layer_gap'] apart in the Borromean order, the top
    under p['top_limit'] and the bottom above p['bottom_limit']."""
    names = list(out)
    basis, offs, cols = {}, {}, {}
    col0 = 0
    samp = {}
    for k in names:
        r = out[k]
        n = len(r["C"])
        K = max(8, int(round(r["L"] / p["spline_pitch"])))
        st = np.arange(0, n, p["solve_step"])
        v = np.linspace(-0.5, 0.5, p["solve_across"])
        pts = r["C"][st][:, None, :] + r["D"][st][:, None, :] * (v[None, :, None] * r["w"][st][:, None, None])
        off = pts[..., 2] - r["C"][st][:, None, 2]             # height of each point above the centreline
        B = bspline_basis(r["s"][st], r["L"], K)
        basis[k] = (B, K, st)
        samp[k] = (pts[..., :2].reshape(-1, 2), off.reshape(-1), np.repeat(np.arange(len(st)), len(v)))
        cols[k] = col0
        col0 += K
    # initial coefficients: least-squares fit of the current heights
    c = np.zeros(col0)
    for k in names:
        B, K, st = basis[k]
        c[cols[k]:cols[k] + K] = np.linalg.lstsq(B, out[k]["C"][st, 2], rcond=None)[0]
    rows, lo = [], []                        # each constraint: row . c >= lo
    for a in names:
        for b in names:
            if (a, b) not in OVER:
                continue
            pa, oa, ia = samp[a]
            pb, ob, ib = samp[b]
            for s0 in range(0, len(pa), 2000):
                d = np.sqrt(((pa[s0:s0 + 2000, None] - pb[None]) ** 2).sum(-1))
                ii, jj = np.where(d < p["plan_touch"])
                for i, j in zip(ii + s0, jj):
                    row = np.zeros(col0)
                    Ba, Ka, _ = basis[a]
                    Bb, Kb, _ = basis[b]
                    row[cols[a]:cols[a] + Ka] += Ba[ia[i]]
                    row[cols[b]:cols[b] + Kb] -= Bb[ib[j]]
                    rows.append(row)
                    lo.append(p["layer_gap"] - oa[i] + ob[j])
    for k in names:                          # depth band
        B, K, st = basis[k]
        pk, ok, ik = samp[k]
        top_off = np.full(len(st), -np.inf)
        bot_off = np.full(len(st), np.inf)
        rmin = np.full(len(st), np.inf)
        np.maximum.at(top_off, ik, ok)
        np.minimum.at(bot_off, ik, ok)
        np.minimum.at(rmin, ik, np.hypot(pk[:, 0], pk[:, 1]))
        for i in range(len(st)):
            # under the ceiling disc the ribbon must pass below it by the seat gap
            limit = p["top_limit"] if rmin[i] > p["canopy_r"] + 20 else -(p["canopy_h"] + p["seat_gap"])
            row = np.zeros(col0)
            row[cols[k]:cols[k] + K] = -B[i]
            rows.append(row)
            lo.append(-(limit - p["bead_r"] - top_off[i]))
            row = np.zeros(col0)
            row[cols[k]:cols[k] + K] = B[i]
            rows.append(row)
            lo.append(p["bottom_limit"] + p["bead_r"] - bot_off[i])
    A = np.array(rows)
    lo = np.array(lo)
    # roughness: second differences of the control values, scaled per ring
    R = []
    for k in names:
        B, K, st = basis[k]
        h = out[k]["L"] / K
        for i in range(K):
            row = np.zeros(col0)
            row[cols[k] + (i - 1) % K] += 1 / h ** 2
            row[cols[k] + i] -= 2 / h ** 2
            row[cols[k] + (i + 1) % K] += 1 / h ** 2
            R.append(row)
    R = np.array(R) * 1e4
    # follow the designed weave heights (high over, low under) where clearance allows
    Tm, tz = [], []
    for k in names:
        B, K, st = basis[k]
        row = np.zeros((len(st), col0))
        row[:, cols[k]:cols[k] + K] = B
        Tm.append(row)
        tz.append(out[k]["z_target"][st])
    Tm = np.vstack(Tm) * p["track_weight"]
    tz = np.concatenate(tz) * p["track_weight"]
    active = np.zeros(len(lo), bool)
    for it in range(60):
        viol = A @ c - lo
        new = viol < 0.5
        if it and not (new & ~active).any():
            break
        active |= new
        M = np.vstack([R, Tm, 30 * A[active]])
        rhs = np.r_[np.zeros(len(R)), tz, 30 * (lo[active] + 1.0)]
        c = np.linalg.lstsq(M, rhs, rcond=None)[0]
    viol = A @ c - lo
    for k in names:
        r = out[k]
        Bf = bspline_basis(r["s"], r["L"], basis[k][1])
        r["C"][:, 2] = Bf @ c[cols[k]:cols[k] + basis[k][1]]
    SOLVE_INFO.update(constraints=len(lo), worst_violation_mm=round(float(min(viol.min(), 0)), 2))
    return out


def section(p=P):
    """Closed section: (v across in units of half-width offset mm, n normal mm), and a flag for skin."""
    t2, br = p["thickness"] / 2, p["bead_r"]
    m = p["profile_n"]
    top = [(x, t2) for x in np.linspace(-1, 1, m)]
    bead_r = [(1, 0)]
    pts = []
    # top face from left to right, right bead, bottom face back, left bead
    for x, y in top:
        pts.append(("f", x, y))
    for a in np.linspace(np.pi / 2 - 0.5, -np.pi / 2 + 0.5, 9):
        pts.append(("b+", np.cos(a) * br, np.sin(a) * br))
    for x in np.linspace(1, -1, m):
        pts.append(("f", x, -t2))
    for a in np.linspace(-np.pi / 2 - 0.5, -3 * np.pi / 2 + 0.5, 9):
        pts.append(("b-", np.cos(a) * br, np.sin(a) * br))
    return pts


def solid_rings(ring, p=P, idx=None):
    """Section rings in world coordinates: (stations, k, 3)."""
    C, D, N, w = ring["C"], ring["D"], ring["N"], ring["w"]
    if idx is None:
        idx = np.arange(len(C))
    sec = section(p)
    half = (w[idx] / 2 - p["bead_r"])[:, None]
    res = np.empty((len(idx), len(sec), 3))
    for k, (kind, a, b) in enumerate(sec):
        if kind == "f":
            off = D[idx] * (a * half)
            res[:, k] = C[idx] + off + N[idx] * b
        elif kind == "b+":
            res[:, k] = C[idx] + D[idx] * (half + a) + N[idx] * b
        else:
            res[:, k] = C[idx] - D[idx] * (half - a) + N[idx] * b
    return res


def mid_surface(ring, across=41):
    v = np.linspace(-0.5, 0.5, across)
    return ring["C"][:, None, :] + ring["D"][:, None, :] * (v[None, :, None] * ring["w"][:, None, None])


def clearance(rings, p=P, step=3):
    """Smallest surface-to-surface gap between different rings, and within a ring (mm)."""
    pts, owner, st = [], [], []
    for k, r in rings.items():
        M = mid_surface(r, 21)[::step]
        pts.append(M.reshape(-1, 3))
        owner += [k] * M.shape[0] * M.shape[1]
        st.append(np.repeat(np.arange(0, len(r["C"]), step), M.shape[1]))
    pts = np.vstack(pts).astype(np.float32)
    owner = np.array(owner)
    st = np.concatenate(st)
    best = (np.inf, None)
    for a in range(0, len(pts), 1500):
        A = pts[a:a + 1500]
        d = np.sqrt(((A[:, None] - pts[None]) ** 2).sum(-1))
        same = owner[a:a + 1500, None] == owner[None]
        d[same] = np.inf
        i = np.unravel_index(np.argmin(d), d.shape)
        if d[i] < best[0]:
            best = (float(d[i]), (owner[a + i[0]], owner[i[1]]), pts[a + i[0]].round().tolist())
    gap = best[0] - p["thickness"] - 2 * (p["bead_r"] - p["thickness"] / 2)
    return gap, best[1], best[2]


def report(p=P):
    rings, cl = build(p)
    allp = np.vstack([mid_surface(r, 21).reshape(-1, 3) for r in rings.values()])
    gap, who, where = clearance(rings, p)
    curv = {}
    for k, r in rings.items():
        C = r["C"]
        d1 = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2 * p["ds"])
        d2 = (np.roll(C, -1, 0) - 2 * C + np.roll(C, 1, 0)) / p["ds"] ** 2
        kap = np.linalg.norm(np.cross(d1, d2), axis=1) / np.linalg.norm(d1, axis=1) ** 3
        curv[k] = dict(min_radius_mm=round(float(1 / kap.max())), length_mm=round(float(r["L"])),
                       width=[round(float(r["w"].min())), round(float(r["w"].max()))],
                       crossings=len(r["keys"]))
    return dict(
        footprint_mm=[round(float(np.ptp(allp[:, 0]))), round(float(np.ptp(allp[:, 1])))],
        top_z=round(float(allp[:, 2].max()), 1), lowest_z=round(float(allp[:, 2].min()), 1),
        min_gap_between_rings_mm=round(gap, 1), gap_between=who, gap_at=where,
        rings=curv, crossings=len(cl), solver=dict(SOLVE_INFO),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
