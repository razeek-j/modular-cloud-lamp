"""V18 braided ribbon wreath, built to the measured reference targets.

Measured targets (development-v17/Reference-comparison.md):
- ribbons stand upright most of the time and lie flat only at crossing nodes;
- one half-twist per 300-370 mm, centred on the nodes;
- four curve speeds: sweeps R > 500, waves R 150-210, end loops R 90-100
  turning about 200 deg, rolled lips R 45-55;
- width swells mid-span and necks at the nodes; widest on the hero ribbon.

Construction (deliberate, no random terms):
1. Plan. Three strands circle the ceiling disc, each weaving in and out
   radially, r = R0 + A cos(n theta + phase), like a plait wrapped into a wreath.
   The hero strand's two outer lobes are replaced by curled end loops that
   cross back over themselves (the reference's left and right ends).
2. Weave. Every crossing (between strands and within a loop) is a node.
   Over/under strictly alternates along every strand, as in a real plait.
3. Twist. Between nodes the ribbon makes one half-twist, dwelling upright
   in the middle of the span and passing flat through the nodes.
4. Width. Each span swells to the strand's peak width at mid-span and necks
   at the nodes.
5. Height. Nodes sit high or low by the weave; upright mid-spans sit centred
   in the depth band. A constrained smooth-spline solver keeps every layer apart.

Units: millimetres; z = 0 is the ceiling.
"""

import numpy as np

import v17_geometry as V17

_smoothstep = V17._smoothstep
lowpass = V17.lowpass
bspline_basis = V17.bspline_basis
crossings = V17.crossings
section = V17.section
solid_rings = V17.solid_rings
mid_surface = V17.mid_surface

STRANDS = [
    # Three closed ribbons from one curvature program each (hairpin end loops,
    # outward-bowing sweeps, short necks), laid like the reference's band: an upper
    # ribbon (A, the hero), a middle one (B) and a front one (C), fanned to
    # 0, +52 and -52 degrees so the outline becomes round (about 1,150 x 1,050 mm),
    # every crossing is 37 degrees or steeper, crossings are 138 mm or more apart,
    # and no three crossings form a triangle smaller than 245 mm (no cyclic tangle). place: (rotation, centre x, y).
    dict(name="A", sweep=440.0, R_sweep=900.0, R_loop=96.0, R_wave=190.0, wave_deg=24.0, ease=90.0,
         place=(0.0, 0.0, 220.0), w_peak=150.0, hand=1),
    dict(name="B", sweep=430.0, R_sweep=820.0, R_loop=100.0, R_wave=185.0, wave_deg=22.0, ease=85.0,
         place=(52.0, 80.0, -40.0), w_peak=132.0, hand=-1),
    dict(name="C", sweep=360.0, R_sweep=760.0, R_loop=92.0, R_wave=175.0, wave_deg=20.0, ease=80.0,
         place=(-52.0, 0.0, -220.0), w_peak=114.0, hand=1),
]

P = dict(
    ds=3.0,
    loop_half=0.46,          # half-width of a loop window (radians of theta)
    loop_out=70.0,           # radial push of the loop (mm)
    loop_back=150.0,         # tangential reversal that closes the curl (mm)
    w_node=84.0,             # width at a node
    node_spacing=340.0,      # target span between twist nodes
    span_max=520.0,          # spans longer than this are split by extra nodes
    span_min=150.0,          # spans shorter than this stay flat (no twist)
    node_lean=45.0,         # lean from upright at a crossing node (degrees)
    mid_lean=25.0,          # lean from upright mid-span, alternating sides (degrees)
    width_smooth=50.0,      # mm, sigma of the width smoothing
    height_smooth=45.0,     # mm, sigma of the height smoothing
    lens_span=300.0,        # double crossings closer than this keep one ribbon on top
    free_lean=90.0,         # free (non-crossing) twist nodes lie flat
    hold_margin=28.0,       # extra lean hold beyond the geometric overlap (mm)
             # how long the ribbon dwells upright mid-span (0..1)
    top_limit=-22.0,
    bottom_limit=-186.0,
    z_hi=-56.0,              # node height when passing over
    z_lo=-146.0,             # node height when passing under
    layer_gap=20.0,
    plan_touch=9.0,
    spline_pitch=70.0,
    track_weight=1.0,
    solve_rounds=4,
    solve_step=4,
    solve_across=11,
    thickness=1.8,
    bead_r=1.6,
    profile_n=40,
    canopy_r=150.0,
    canopy_h=32.0,
)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def program(sp):
    """Curvature program of one half: list of (length, kappa_start, kappa_end).

    gentle outward-bowing sweep (R_sweep) -> ease -> inward neck (R_wave)
    -> ease -> hairpin end loop (R_loop) -> ease -> neck -> ease -> sweep.
    The loop's turn is whatever closes the half to exactly 180 degrees, so it
    overturns past 180 by the two necks, as in the reference's end loops."""
    ks, kl, kw = 1 / sp["R_sweep"], 1 / sp["R_loop"], -1 / sp["R_wave"]
    e = sp["ease"]
    a_s = sp["sweep"] / 2
    a_w = np.radians(sp["wave_deg"]) / abs(kw)
    fixed = 2 * (a_s * ks + e * (ks + kw) / 2 + a_w * kw + e * (kw + kl) / 2)
    a_l = (np.pi - fixed) / kl
    sp["_loop_turn_deg"] = float(np.degrees(a_l * kl + e * kl))   # arc plus half of each ease
    return [(a_s, ks, ks), (e, ks, kw), (a_w, kw, kw), (e, kw, kl), (a_l, kl, kl),
            (e, kl, kw), (a_w, kw, kw), (e, kw, ks), (a_s, ks, ks)]


def strand_plan(sp, p=P):
    """Closed plan curve built from the curvature program, evenly sampled."""
    ds = 0.25
    kap = []
    for L, k0, k1 in program(sp):
        m = max(2, int(round(L / ds)))
        kap.append(np.linspace(k0, k1, m, endpoint=False))
    kap = np.concatenate(kap)
    head = np.r_[0, np.cumsum(kap[:-1] * ds)]
    half = np.column_stack((np.cos(head), np.sin(head))) * ds
    pts = np.vstack((np.zeros(2), np.cumsum(half, 0)))
    delta = pts[-1]
    pts = pts[:-1] - delta / 2                    # point symmetry about the ribbon centre
    xy = np.vstack((pts, -pts))
    if "bend" in sp:
        # Bend the ribbon's long axis onto a circle round the disc, so the ribbon
        # follows the lamp's round outline: x along the axis becomes angle.
        Rc, th0 = sp["bend"]
        ang = np.radians(th0) + xy[:, 0] / Rc
        rad = Rc + xy[:, 1]
        xy = np.column_stack((rad * np.cos(ang), rad * np.sin(ang)))
    else:
        rot, cx, cy = sp["place"]
        t = np.radians(rot)
        R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        xy = xy @ R.T + np.array([cx, cy])
    seg = np.linalg.norm(np.roll(xy, -1, 0) - xy, axis=1)
    s = np.r_[0, np.cumsum(seg)[:-1]]
    L = seg.sum()
    n = int(round(L / p["ds"]))
    sn = np.linspace(0, L, n, endpoint=False)
    out = np.column_stack((np.interp(sn, s, xy[:, 0], period=L), np.interp(sn, s, xy[:, 1], period=L)))
    return out, L


def self_crossings(xy, min_gap=60):
    """Crossings of a closed polyline with itself (index fractions a < b)."""
    n = len(xy)
    A0, A1 = xy, np.roll(xy, -1, 0)
    da = A1 - A0
    res = []
    for j in range(n):
        db = da[j]
        den = da[:, 0] * db[1] - da[:, 1] * db[0]
        w = A0[j] - A0
        with np.errstate(divide="ignore", invalid="ignore"):
            ta = (w[:, 0] * db[1] - w[:, 1] * db[0]) / den
            tb = (w[:, 0] * da[:, 1] - w[:, 1] * da[:, 0]) / den
        hit = np.where((ta >= 0) & (ta < 1) & (tb >= 0) & (tb < 1))[0]
        for i in hit:
            gap = min(abs(i - j), n - abs(i - j))
            if i < j and gap > min_gap:
                res.append((i + ta[i], j + tb[i]))
    return res


def build(p=P, strands=STRANDS):
    plans = {}
    for sp in strands:
        xy, L = strand_plan(sp, p)
        plans[sp["name"]] = dict(xy=xy, L=L, spec=sp, ds=L / len(xy))
    names = list(plans)
    # ---- every crossing: (name_a, s_a, name_b, s_b)
    events = []
    for i in range(len(names)):
        for j in range(i, len(names)):
            a, b = names[i], names[j]
            if a == b:
                cr = self_crossings(plans[a]["xy"])
            else:
                cr = crossings(plans[a]["xy"], plans[b]["xy"])
            for fa, fb in cr:
                events.append((a, fa * plans[a]["ds"], b, fb * plans[b]["ds"]))
    # ---- alternating over/under: parity along every strand
    occ = {k: [] for k in names}            # (s, event index, which end 0/1)
    for e, (a, sa, b, sb) in enumerate(events):
        occ[a].append((sa, e, 0))
        occ[b].append((sb, e, 1))
    for k in occ:
        occ[k].sort()
    # x[e] = 1 means end 0 (strand events[e][0]) is over.
    # Hard rule: a "lens" (the same two ribbons crossing twice in quick succession,
    # overlapping all the way between) keeps the same ribbon on top for both.
    # Soft rule: otherwise over/under alternates along each ribbon, like a plait.
    # With few crossings every pattern is checked and the best one kept.
    E = len(events)
    pairs = []                       # (e1, w1, e2, w2, lens?)
    for k, lst in occ.items():
        m = len(lst)
        for q in range(m):
            (s1, e1, w1), (s2, e2, w2) = lst[q], lst[(q + 1) % m]
            if e1 == e2:
                continue
            pset1 = {events[e1][0], events[e1][2]}
            pset2 = {events[e2][0], events[e2][2]}
            ds_ = (s2 - s1) % plans[k]["L"]
            lens = pset1 == pset2 and len(pset1) == 2 and ds_ < p["lens_span"]
            pairs.append((e1, w1, e2, w2, lens))
    best = None
    for code in range(2 ** E):
        bits = [(code >> e) & 1 for e in range(E)]
        bad_hard = bad_soft = 0
        for e1, w1, e2, w2, lens in pairs:
            o1, o2 = bits[e1] ^ w1, bits[e2] ^ w2          # 1 = this strand over? (w=0: end 0)
            o1, o2 = 1 - o1 if w1 else o1, 1 - o2 if w2 else o2
            if lens and o1 != o2:
                bad_hard += 1
            if not lens and o1 == o2:
                bad_soft += 1
        key = (bad_hard, bad_soft)
        if best is None or key < best[0]:
            best = (key, bits)
    x = {e: best[1][e] for e in range(E)}
    conflicts = best[0]
    lens_events = set()
    for e1, w1, e2, w2, lens in pairs:
        if lens:
            lens_events |= {e1, e2}
    keys = {k: [] for k in names}           # (s, over?, hold mm)
    cross_list = []
    for e, (a, sa, b, sb) in enumerate(events):
        a_over = bool(x[e])
        # hold the lean over the whole overlap: half the other ribbon's neck width
        # divided by the sine of the crossing angle, plus a margin
        xa, xb = plans[a]["xy"], plans[b]["xy"]
        ia, ib = int(sa / plans[a]["ds"]) % len(xa), int(sb / plans[b]["ds"]) % len(xb)
        ta = xa[(ia + 3) % len(xa)] - xa[ia - 3]
        tb = xb[(ib + 3) % len(xb)] - xb[ib - 3]
        sin_t = np.sqrt(max(1e-4, 1 - (abs(ta @ tb) / np.linalg.norm(ta) / np.linalg.norm(tb)) ** 2))
        hold = min(140.0, p["w_node"] / (2 * sin_t) + p["hold_margin"])
        keys[a].append((sa, a_over, hold, b if e in lens_events else None))
        keys[b].append((sb, not a_over, hold, a if e in lens_events else None))
        pt = plans[a]["xy"][int(sa / plans[a]["ds"]) % len(plans[a]["xy"])]
        cross_list.append(dict(strands=(a, b), upper=a if a_over else b, xy=[round(float(pt[0])), round(float(pt[1]))],
                               s={a: sa} if a == b else {a: sa, b: sb}))
    out = {}
    for k, pl in plans.items():
        xy, L, sp = pl["xy"], pl["L"], pl["spec"]
        n = len(xy)
        s = np.arange(n) * pl["ds"]
        # ---- nodes: crossings plus extra twist nodes on long spans
        node_s = sorted(kk[0] for kk in keys[k])
        node_z = {kk[0]: (p["z_hi"] if kk[1] else p["z_lo"]) for kk in keys[k]}
        node_h = {kk[0]: kk[2] for kk in keys[k]}
        node_lens = {kk[0]: (kk[3], kk[1]) for kk in keys[k]}
        full = []
        for q in range(len(node_s)):
            a, b = node_s[q], node_s[(q + 1) % len(node_s)]
            span = (b - a) % L
            full.append((a, node_z[a], True, node_h[a], node_lens[a]))
            if span > p["span_max"]:
                m = int(round(span / p["node_spacing"]))
                for t in range(1, m):
                    full.append(((a + span * t / m) % L, None, False, 0.0, (None, None)))
        full.sort()
        ns = np.array([f[0] for f in full])
        # ---- lean, width and target height per span.
        # At each node the ribbon necks and leans 45 deg, alternately one way and
        # the other; mid-span it stands upright at full width (a rocking roll).
        psi = np.zeros(n)
        w = np.full(n, float(p["w_node"]))
        zt = np.zeros(n)
        # crossing nodes lean node_lean from upright (alternating sides); free twist
        # nodes on long stretches roll right over to flat, so the ribbon twists through
        node_psi = []
        for q in range(len(ns)):
            side_ = 1 if q % 2 == 0 else -1
            lean = p["node_lean"] if full[q][2] else p["free_lean"]
            node_psi.append(np.radians(90 + sp["hand"] * lean * side_))
        ext = np.r_[ns, ns[0] + L]
        z_mid = 0.5 * (p["top_limit"] + p["bottom_limit"])
        for q in range(len(ns)):
            a, b = ext[q], ext[q + 1]
            span = b - a
            sel = ((s - a) % L) < span
            u = ((s[sel] - a) % L) / span
            pa, pb = node_psi[q], node_psi[(q + 1) % len(ns)]
            # hold the lean for node_hold mm either side of each node, then roll upright
            h = full[q][3]
            h2 = full[(q + 1) % len(full)][3]
            free = span - h - h2
            la, lb = full[q][4], full[(q + 1) % len(full)][4]
            in_lens = la[0] is not None and la == lb          # same partner, same side: hold right across
            if in_lens:
                free = 0.0
            if free > 40:
                v = np.clip((u * span - h) / free, 0, 1)
                up = np.sin(np.pi * v) ** 2
            else:
                v = np.clip((u * span - h) / max(free, 1.0), 0, 1) if free > 0 else (u > 0.5).astype(float)
                up = np.zeros_like(u)
            # lean and height both hold through each overlap and change only in the free part
            base_psi = pa + (pb - pa) * _smoothstep(v)
            # mid-span the ribbon rolls to a lean of mid_lean, alternating sides
            mid = np.pi / 2 + sp["hand"] * np.radians(p["mid_lean"]) * (1 if q % 2 == 0 else -1)
            psi[sel] = (1 - up) * base_psi + up * mid
            w[sel] = up ** 0.75            # swell profile, scaled below after smoothing
            za = full[q][1]
            zb = full[(q + 1) % len(full)][1]
            z_a = za if za is not None else z_mid
            z_b = zb if zb is not None else z_mid
            base = z_a + (z_b - z_a) * _smoothstep(v)
            zt[sel] = (1 - up) * base + up * z_mid
        turns = 0
        # end loops taper the width about 25 % toward their apex (where plan radius is tight)
        d1 = (np.roll(xy, -1, 0) - np.roll(xy, 1, 0)) / (2 * pl["ds"])
        d2 = (np.roll(xy, -1, 0) - 2 * xy + np.roll(xy, 1, 0)) / pl["ds"] ** 2
        kp = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3
        in_loop = lowpass((kp > 1 / 130).astype(float), 25.0)
        loopf = 1 - 0.25 * in_loop
        # width changes slowly (no scalloped edges): smooth the swell profile over ~150 mm
        w = p["w_node"] + (sp["w_peak"] - p["w_node"]) * np.clip(lowpass(w, p["width_smooth"] / pl["ds"]), 0, 1) * loopf
        zt = lowpass(zt, p["height_smooth"] / pl["ds"])
        psi = lowpass(psi, 30.0 / pl["ds"])
        C = np.column_stack((xy, zt))
        out[k] = dict(C=C, w=w, psi=psi, s=s, L=L, z_target=zt.copy(), keys=keys[k], nodes=full,
                      centre=np.zeros(2), spec=sp, half_turns=turns)
        refresh(out[k])
    for _ in range(p["solve_rounds"]):
        solve_heights(out, p)
        for r in out.values():
            refresh(r)
    return out, dict(crossings=cross_list, parity_conflicts=conflicts)


def refresh(r):
    """Frames from centreline, roll and the radial side direction."""
    C, psi = r["C"], r["psi"]
    n = len(C)
    T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
    side = _unit(np.column_stack((T[:, 1], -T[:, 0], np.zeros(n))))
    # keep the side direction continuous along the strand (not tied to the centre)
    for i in range(1, n):
        if np.dot(side[i], side[i - 1]) < 0:
            side[i] = -side[i]
    D = np.cos(psi)[:, None] * side + np.sin(psi)[:, None] * np.array([0, 0, 1.0])
    D -= np.einsum("ij,ij->i", D, T)[:, None] * T
    D = _unit(D)
    r.update(T=T, D=D, N=_unit(np.cross(T, D)))


SOLVE_INFO = {}


def solve_heights(out, p):
    """Smoothest heights that keep woven layers apart; the upper ribbon at each
    stacked spot is the one whose designed height is higher there."""
    names = list(out)
    basis, cols, samp = {}, {}, {}
    col0 = 0
    for k in names:
        r = out[k]
        n = len(r["C"])
        K = max(8, int(round(r["L"] / p["spline_pitch"])))
        st = np.arange(0, n, p["solve_step"])
        v = np.linspace(-0.5, 0.5, p["solve_across"])
        pts = r["C"][st][:, None, :] + r["D"][st][:, None, :] * (v[None, :, None] * r["w"][st][:, None, None])
        off = pts[..., 2] - r["C"][st][:, None, 2]
        B = bspline_basis(r["s"][st], r["L"], K)
        basis[k] = (B, K, st)
        samp[k] = (pts[..., :2].reshape(-1, 2), off.reshape(-1), np.repeat(np.arange(len(st)), len(v)),
                   r["z_target"][st])
        cols[k] = col0
        col0 += K
    c = np.zeros(col0)
    for k in names:
        B, K, st = basis[k]
        c[cols[k]:cols[k] + K] = np.linalg.lstsq(B, out[k]["C"][st, 2], rcond=None)[0]
    rows, lo, kind = [], [], []
    for ia_, a in enumerate(names):
        for b in names[ia_:]:
            pa, oa, ia, ta = samp[a]
            pb, ob, ib, tb = samp[b]
            n_a = len(basis[a][2])
            for s0 in range(0, len(pa), 2000):
                d = np.sqrt(((pa[s0:s0 + 2000, None] - pb[None]) ** 2).sum(-1))
                ii, jj = np.where(d < p["plan_touch"])
                for i, j in zip(ii + s0, jj):
                    si, sj = ia[i], ib[j]
                    if a == b:
                        gap = abs(si - sj)
                        if min(gap, n_a - gap) * p["solve_step"] * (out[a]["L"] / len(out[a]["C"])) < 120:
                            continue
                        if si > sj:
                            continue
                    up_is_a = ta[si] >= tb[sj]
                    row = np.zeros(col0)
                    Ba, Ka, _ = basis[a]
                    Bb, Kb, _ = basis[b]
                    sign = 1 if up_is_a else -1
                    row[cols[a]:cols[a] + Ka] += sign * Ba[si]
                    row[cols[b]:cols[b] + Kb] -= sign * Bb[sj]
                    rows.append(row)
                    lo.append(p["layer_gap"] - sign * (oa[i] - ob[j]))
                    kind.append("self" if a == b else "pair")
    for k in names:
        B, K, st = basis[k]
        pk, ok, ik, _ = samp[k]
        top_off = np.full(len(st), -np.inf)
        bot_off = np.full(len(st), np.inf)
        rmin = np.full(len(st), np.inf)
        np.maximum.at(top_off, ik, ok)
        np.minimum.at(bot_off, ik, ok)
        np.minimum.at(rmin, ik, np.hypot(pk[:, 0], pk[:, 1]))
        for i in range(len(st)):
            limit = p["top_limit"] if rmin[i] > p["canopy_r"] + 15 else -(p["canopy_h"] + 6.0)
            row = np.zeros(col0)
            row[cols[k]:cols[k] + K] = -B[i]
            rows.append(row)
            lo.append(-(limit - p["bead_r"] - top_off[i]))
            kind.append("top")
            row = np.zeros(col0)
            row[cols[k]:cols[k] + K] = B[i]
            rows.append(row)
            lo.append(p["bottom_limit"] + p["bead_r"] - bot_off[i])
            kind.append("bottom")
    A = np.array(rows)
    lo = np.array(lo)
    R, Tm, tz = [], [], []
    for k in names:
        B, K, st = basis[k]
        h = out[k]["L"] / K
        for i in range(K):
            row = np.zeros(col0)
            row[cols[k] + (i - 1) % K] += 1 / h ** 2
            row[cols[k] + i] -= 2 / h ** 2
            row[cols[k] + (i + 1) % K] += 1 / h ** 2
            R.append(row)
        row = np.zeros((len(st), col0))
        row[:, cols[k]:cols[k] + K] = B
        Tm.append(row)
        tz.append(out[k]["z_target"][st])
    R = np.array(R) * 1e4
    Tm = np.vstack(Tm) * p["track_weight"]
    tz = np.concatenate(tz) * p["track_weight"]
    active = np.zeros(len(lo), bool)
    for it in range(80):
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
    kind = np.array(kind)
    SOLVE_INFO.update(constraints=len(lo), worst_violation_mm=round(float(min(viol.min(), 0)), 2),
                      worst_by_kind={k: round(float(viol[kind == k].min()), 1) for k in set(kind)},
                      count_by_kind={k: int((kind == k).sum()) for k in set(kind)})


def clearance(rings, p=P, step=3, self_gap=150.0):
    """Smallest gap between surfaces of different strands, or far-apart parts of one strand."""
    pts, owner, st = [], [], []
    for k, r in rings.items():
        M = mid_surface(r, 21)[::step]
        pts.append(M.reshape(-1, 3))
        owner += [k] * M.shape[0] * M.shape[1]
        st.append(np.repeat(np.arange(0, len(r["C"]), step) * (r["L"] / len(r["C"])), M.shape[1]))
    pts = np.vstack(pts).astype(np.float32)
    owner = np.array(owner)
    st = np.concatenate(st)
    Ls = {k: r["L"] for k, r in rings.items()}
    Lown = np.array([Ls[o] for o in owner])
    best = (np.inf, None, None)
    for a in range(0, len(pts), 1500):
        A = pts[a:a + 1500]
        d = np.sqrt(((A[:, None] - pts[None]) ** 2).sum(-1))
        same = owner[a:a + 1500, None] == owner[None]
        sd = np.abs(st[a:a + 1500, None] - st[None])
        sd = np.minimum(sd, Lown[None] - sd)
        d[same & (sd < self_gap)] = np.inf
        i = np.unravel_index(np.argmin(d), d.shape)
        if d[i] < best[0]:
            best = (float(d[i]), (owner[a + i[0]], owner[i[1]]), pts[a + i[0]].round().tolist())
    gap = best[0] - p["thickness"] - 2 * (p["bead_r"] - p["thickness"] / 2)
    return gap, best[1], best[2]


def measure(rings, p=P):
    """Numbers to compare with the measured reference targets."""
    rep = {}
    tilt_all = []
    for k, r in rings.items():
        ds = r["L"] / len(r["C"])
        tilt = np.degrees(np.arcsin(np.clip(np.abs(r["D"][:, 2]), 0, 1)))
        tilt_all.append(tilt)
        xy = r["C"][:, :2]
        d1 = (np.roll(xy, -1, 0) - np.roll(xy, 1, 0)) / (2 * ds)
        d2 = (np.roll(xy, -1, 0) - 2 * xy + np.roll(xy, 1, 0)) / ds ** 2
        kap = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3
        rad = 1 / np.maximum(kap, 1e-9)
        C = r["C"]
        e1 = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2 * ds)
        e2 = (np.roll(C, -1, 0) - 2 * C + np.roll(C, 1, 0)) / ds ** 2
        k3 = np.linalg.norm(np.cross(e1, e2), axis=1) / np.linalg.norm(e1, axis=1) ** 3
        spans = []
        ns = sorted(f[0] for f in r["nodes"])
        for q in range(len(ns)):
            spans.append((ns[(q + 1) % len(ns)] - ns[q]) % r["L"])
        rep[k] = dict(
            length_mm=round(float(r["L"])),
            width_mm=[round(float(r["w"].min())), round(float(r["w"].max()))],
            nodes=len(ns), span_mm=[round(min(spans)), round(float(np.median(spans))), round(max(spans))],
            half_turns=int(r["half_turns"]),
            plan_radius_share=dict(
                lip_under_60=round(float((rad < 60).mean()), 3),
                loop_60_130=round(float(((rad >= 60) & (rad < 130)).mean()), 3),
                wave_130_300=round(float(((rad >= 130) & (rad < 300)).mean()), 3),
                sweep_over_300=round(float((rad >= 300).mean()), 3)),
            tightest_plan_radius_mm=round(float(rad.min())),
            tightest_3d_radius_mm=round(float(1 / k3.max())),
        )
    t = np.concatenate(tilt_all)
    rep["stance"] = dict(flat_under_25=round(float((t < 25).mean()), 2), leaning=round(float(((t >= 25) & (t < 55)).mean()), 2),
                         upright_over_55=round(float((t >= 55).mean()), 2))
    allp = np.vstack([mid_surface(r, 21).reshape(-1, 3) for r in rings.values()])
    rep["footprint_mm"] = [round(float(np.ptp(allp[:, 0]))), round(float(np.ptp(allp[:, 1])))]
    rep["top_z"] = round(float(allp[:, 2].max()), 1)
    rep["lowest_z"] = round(float(allp[:, 2].min()), 1)
    return rep


if __name__ == "__main__":
    import json
    import warnings
    warnings.filterwarnings("ignore")
    rings, info = build()
    gap = clearance(rings)
    print(json.dumps(dict(measure=measure(rings), gap=gap, crossings=len(info["crossings"]),
                          parity_conflicts=info["parity_conflicts"], solver=SOLVE_INFO), indent=1))
