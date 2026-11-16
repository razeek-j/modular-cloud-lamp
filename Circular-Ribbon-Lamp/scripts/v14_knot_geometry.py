"""V14 circular ribbon knot: one continuous band, pure numpy geometry.

The band follows a (2,5) torus-knot style path squashed to a shallow ceiling
profile. Because the path circles the centre twice, every plan direction holds
exactly two strands (parameters t and t+pi). The ribbon's width direction is
set perpendicular to the line joining those two strands, so the two strands'
cross-sections are always parallel and cannot collide: they stand as walls at
the lobes and lie flat where they cross over each other. That roll is what
gives the rolling-wave look of the reference.

All units are millimetres; z = 0 is the ceiling, negative is downward.
"""

import numpy as np

P = dict(
    samples=2400,          # stations along the closed band (even)
    across=181,            # stations across the width
    lobes=5,
    r_inner=157.0,         # inner-lobe centreline radius (touches canopy)
    a=191.0,               # main lobe amplitude
    b=10.0,                # second harmonic: softens inner turns
    grade_ease=0.35,
    w_soft=6.0,
    lift=20.0,             # extra room for climbing strands (adds depth)
    h=72.0,                # half the vertical gap where strands cross
    top_z=-22.0,           # level top line of the skin, below the ceiling
    w_mid=130.0,
    w_lobe=40.0,           # outer lobes wider, inner lobes narrower
    irregular=0.12,        # gentle lobe-to-lobe variation (outer lobes only)
    grooves=22,            # continuous surface grooves across the width
    groove_amp=0.55,
    thickness=1.8,
    canopy_r=152.0,        # centre drum: ceiling fixing, driver, ribbon seats
    canopy_h=130.0,        # reaches the inner-lobe walls (tops ~100 mm down)
    trough_half=6.0,       # hidden LED channel: 12 mm wide
    trough_depth=10.0,
    trough_floor=1.5,
    trough_vertical=0.70,  # channel only where the band stands as a wall
    trough_max_grade=15.0, # degrees; channel only where its top edge is near level
    trough_lean_deg=35.0,  # opening leans toward the lamp centre
)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def centreline(p=P):
    n, q = p["samples"], p["lobes"]
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c, c2, s = np.cos(q * t), np.cos(2 * q * t), np.sin(q * t)
    base = p["r_inner"] + p["a"] * (c + 1) + p["b"] * (c2 - 1)
    # Variation scales only the distance beyond the inner lobe, so the canopy
    # contact radius stays exact while outer lobes become slightly irregular.
    eps = p["irregular"] * (np.sin(t + 0.4) * 0.7 + np.sin(3 * t + 1.9) * 0.3)
    r = p["r_inner"] + (base - p["r_inner"]) * (1 + eps)
    phi = 2 * t
    h = p["h"] * (1 + 0.04 * np.cos(t + 0.8))
    w = p["w_mid"] + p["w_lobe"] * c
    w = w * (1 + 0.5 * eps * (c > 0) * c)
    # Over/under height profile. Each strand is highest at one crossing and
    # lowest at the next. Between them the height changes at a near-constant
    # grade measured along the plan path. A sine in t would put the steepest
    # descent in the tight inner lobes, where the plan path is shortest.
    xy = np.column_stack((r * np.cos(phi), r * np.sin(phi)))
    ds = np.linalg.norm(np.roll(xy, -1, 0) - xy, axis=1)
    splan = np.r_[0, np.cumsum(ds)[:-1]]
    total = splan[-1] + ds[-1]
    theta = q * t
    k_of = np.floor((theta - np.pi / 2) / np.pi).astype(int)    # half-cycle index
    tk = (np.pi / 2 + np.arange(-1, 2 * q + 1) * np.pi) / q
    wrap = np.floor(tk / (2 * np.pi))
    sk = np.interp(tk - wrap * 2 * np.pi, np.r_[t, 2 * np.pi], np.r_[splan, total]) + wrap * total
    k0 = k_of + 1
    u = (splan - sk[k0]) / (sk[k0 + 1] - sk[k0])
    e = p["grade_ease"]
    uu = np.linspace(0, 1, 2001)
    f = np.clip(np.minimum(uu, 1 - uu) / e, 0, 1)
    f = f * f * (3 - 2 * f)
    S = np.r_[0, np.cumsum((f[1:] + f[:-1]) / 2)]
    S /= S[-1]
    g = 1 - 2 * np.interp(np.clip(u, 0, 1), uu, S)
    g = np.where(k_of % 2 == 0, g, -g)     # k even: over -> under
    zoff = h * g
    rhat_xy = np.column_stack((np.cos(phi), np.sin(phi)))
    # The two strands at each plan angle. Their width direction depends only
    # on the offset between them, so dz_unit (vertical share of the width) is
    # known before the heights are placed.
    dr = r - np.roll(r, -n // 2)
    dz = zoff - np.roll(zoff, -n // 2)
    dz_unit = np.abs(dr) / np.hypot(dr, dz)
    # One constant stack centre, so the top line is level and no extra dives
    # appear. A strand narrows slightly while climbing to an over-crossing so
    # its upper edge never rises above that line.
    margin = p["thickness"] / 2 + p["groove_amp"]
    half_lobe = 0.5 * w.max() + p["lift"]
    w_fit = 2 * (half_lobe - zoff) / np.maximum(dz_unit, 1e-3)
    sm = p["w_soft"]
    w = -sm * np.logaddexp(-w / sm, -w_fit / sm)
    zc = p["top_z"] - half_lobe - margin
    C = np.column_stack((r * rhat_xy[:, 0], r * rhat_xy[:, 1], zc + zoff))
    return t, phi, C, w


def frames(C, phi):
    n = len(C)
    T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
    Q = np.roll(C, -n // 2, 0)           # the other strand at the same angle
    rhat = np.column_stack((np.cos(phi), np.sin(phi), np.zeros(n)))
    d = C - Q
    dr = np.einsum("ij,ij->i", d, rhat)
    dz = d[:, 2]
    D = -dz[:, None] * rhat + dr[:, None] * np.array([0, 0, 1.0])
    D -= np.einsum("ij,ij->i", D, T)[:, None] * T
    D = _unit(D)
    N = _unit(np.cross(T, D))
    return T, D, N, np.hypot(dr, dz)


def ribbon_grid(p=P):
    t, phi, C, w = centreline(p)
    T, D, N, gap = frames(C, phi)
    v = np.linspace(0, 1, p["across"])
    edge = np.minimum(v, 1 - v)
    taper = np.clip(edge / 0.07, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    groove = p["groove_amp"] * np.sin(2 * np.pi * p["grooves"] * v) * taper
    V = (C[:, None, :]
         + D[:, None, :] * ((v - 0.5)[None, :, None] * w[:, None, None])
         + N[:, None, :] * groove[None, :, None])
    # Final level: the highest skin point sits exactly on the top line.
    shift = p["top_z"] - V[..., 2].max()
    V[..., 2] += shift
    C = C.copy()
    C[:, 2] += shift
    return dict(t=t, phi=phi, C=C, w=w, T=T, D=D, N=N, gap=gap, V=V)


def trough_segments(g, p=P):
    """Stations where the band is a near-vertical wall get an upward LED channel."""
    # Upper-edge path and its grade. A channel that climbs steeply can be
    # looked into lengthwise from across the room, so channels stay on the
    # near-level crest of each outer lobe.
    E = g["C"] + g["D"] * (np.sign(g["D"][:, 2]) * g["w"] / 2)[:, None]
    dE = np.roll(E, -1, 0) - np.roll(E, 1, 0)
    grade = np.degrees(np.arctan2(np.abs(dE[:, 2]), np.linalg.norm(dE[:, :2], axis=1)))
    vertical = (np.abs(g["D"][:, 2]) > p["trough_vertical"]) & (grade < p["trough_max_grade"])
    n = len(vertical)
    start = np.argmin(vertical)            # begin scanning from a non-wall station
    segs, cur = [], []
    for k in range(n):
        i = (start + k) % n
        if vertical[i]:
            cur.append(i)
        elif cur:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    out = []
    for s in segs:
        idx = np.array(s)
        L = np.sum(np.linalg.norm(np.diff(g["C"][idx], axis=0), axis=1))
        r_mid = np.hypot(*g["C"][idx[len(idx) // 2], :2])
        if L > 80 and r_mid > 300:     # outer lobes only; inner lobes seat on the drum
            out.append(idx)
    return out


def trough_profile(scale_n=1.0, scale_u=1.0, p=P):
    """Closed U profile in (normal, up) coordinates; opening faces the ceiling."""
    a, f, d = p["trough_half"], p["trough_floor"], p["trough_depth"]
    wall = 1.2
    pts = [(-a, -f), (a, -f), (a, d), (a - wall, d), (a - wall, 0.0),
           (-a + wall, 0.0), (-a + wall, d), (-a, d)]
    return np.array([(x * scale_n, y * scale_u if y > 0 else y) for x, y in pts])


def trough_mesh(g, idx, p=P):
    C, D, N, w = g["C"][idx], g["D"][idx], g["N"][idx], g["w"][idx]
    s = np.sign(D[:, 2])[:, None]
    E = C + D * s * (w / 2)[:, None]
    # The channel opening always faces straight up (world Z, made square to
    # the path), even where the wall leans, so no line of sight from the room
    # below can reach into it.
    # The opening faces up and leans inward toward the lamp centre, so the
    # strip washes the ceiling and the inner faces of the band at the same
    # time. The outer wall of the lobe screens it from the room.
    T = g["T"][idx]
    Zp = np.array([0, 0, 1.0]) - T[:, 2:3] * T
    Zp /= np.linalg.norm(Zp, axis=1, keepdims=True)
    inward = np.column_stack((-E[:, 0], -E[:, 1], np.zeros(len(E))))
    inward -= np.einsum("ij,ij->i", inward, T)[:, None] * T
    inward -= np.einsum("ij,ij->i", inward, Zp)[:, None] * Zp
    inward /= np.linalg.norm(inward, axis=1, keepdims=True)
    lean = np.radians(p["trough_lean_deg"])
    U = Zp * np.cos(lean) + inward * np.sin(lean)
    N = np.cross(T, U)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(E, axis=0), axis=1))]
    L = seg[-1]
    ramp = np.clip(np.minimum(seg, L - seg) / 30.0, 0, 1)
    ramp = ramp * ramp * (3 - 2 * ramp)
    rings = []
    for i in range(len(idx)):
        # Width tapers into the edge but the walls keep full height to the end,
        # so the channel cannot be looked into lengthwise.
        prof = trough_profile(0.25 + 0.75 * ramp[i], 1.0, p)
        rings.append(E[i] + np.outer(prof[:, 0], N[i]) + np.outer(prof[:, 1], U[i]))
    rings = np.array(rings)
    # LED strip: 8 x 1 mm on the channel floor, stopping 35 mm short of each end
    led_mask = (seg > 35) & (seg < L - 35)
    li = np.where(led_mask)[0]
    led = []
    for i in li:
        sq = np.array([(-4, 0.05), (4, 0.05), (4, 1.0), (-4, 1.0)])
        led.append(E[i] + np.outer(sq[:, 0], N[i]) + np.outer(sq[:, 1], U[i]))
    return rings, np.array(led), L, (seg[li[-1]] - seg[li[0]]) if len(li) else 0.0


def report(p=P):
    g = ribbon_grid(p)
    V = g["V"]
    t = g["t"]
    seglen = np.linalg.norm(np.diff(np.vstack((g["C"], g["C"][:1])), axis=0), axis=1)
    rplan = np.linalg.norm(V[..., :2], axis=-1)
    troughs = trough_segments(g, p)
    tr = [trough_mesh(g, i, p) for i in troughs]
    tr_top = max(r[0][..., 2].max() for r in tr)
    # minimum distance between the two strands' sheets minus their half-widths
    # projected on the joining line (they are parallel by construction)
    return dict(
        band_length_mm=float(seglen.sum()),
        plan_diameter_mm=float(2 * rplan.max()),
        extent_x_mm=float(V[..., 0].max() - V[..., 0].min()),
        extent_y_mm=float(V[..., 1].max() - V[..., 1].min()),
        skin_top_z=float(V[..., 2].max()),
        trough_top_z=float(tr_top),
        lowest_z=float(V[..., 2].min()),
        min_strand_gap_mm=float(g["gap"].min()),
        inner_radius_mm=float(rplan.min()),
        width_range_mm=(float(g["w"].min()), float(g["w"].max())),
        skin_area_m2=float(np.sum(seglen * g["w"]) / 1e6),
        led_channels=len(troughs),
        led_lengths_mm=[round(float(x[3])) for x in tr],
    )


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2))
