"""V15 broad-ribbon knot: one wide band, lying nearly flat, rolling at the loops.

Target: the user's main reference (broad flowing ribbons, low profile, small
ceiling disc), in a rounder but irregular outline.

The band follows a (2,3) knot path: twice around the centre, three big outer
loops, three small inner loops under the ceiling disc, three crossings. With
so few crossings the band can be very wide. It lies flat where it passes over
or under itself and banks up at the loops, like a banked track, so its broad
faces show from below. Loop sizes, spacing, widths and bank angles all differ
so the outline is round but not regular.

All units are millimetres; z = 0 is the ceiling, negative is downward.
"""

import numpy as np

P = dict(
    samples=2400,
    across=181,
    lobes=3,
    r_inner=118.0,          # inner-loop centreline radius (under the ceiling disc)
    a=205.0,                # main loop amplitude
    b=36.0,                 # second harmonic: opens the inner loops so a wide flat band can turn
    warp=0.26,              # uneven angular spacing of the loops (radians)
    warp_phase=0.9,
    irregular=0.18,         # loop-to-loop size variation
    irregular_phase=2.1,
    grade_ease=0.35,
    h=46.0,                 # half the vertical gap where the band crosses itself
    z_out=-22.0,            # outer loops hang lower
    z_in=0.0,               # inner loops sit closer to the ceiling disc
    top_z=-20.0,            # highest skin point; inner loops pass under the 32 mm disc
    w_mid=205.0,
    w_lobe=30.0,            # outer loops wider, inner loops narrower
    bank_out=38.0,          # degrees: outer edge lifts at the outer loops
    bank_var=0.5,           # each loop banks differently
    bank_phase=4.0,
    twist=30.0,             # degrees of S-twist between loops and crossings
    twist_var=0.5,
    twist_phase=1.2,
    wave=12.0,              # mm height wave, different on each stretch
    wave_phase=0.3,
    bank_narrow=0.22,
    tilt_smooth=24,         # stations (about 45 mm) of smoothing on the tilt
    free_start=0.80,        # bank begins once strands are this far apart (x width)
    free_span=0.50,
    twist_start=0.65,
    twist_span=0.45,
    led_edge_inset=11.0,    # LED channel centre, measured in from the inner edge
    bank_in=14.0,           # degrees: gentle opposite bank under the disc
    grooves=20,
    groove_amp=0.55,
    groove_diag=34.0,       # mm of band length per groove of diagonal drift
    thickness=1.8,
    canopy_r=120.0,
    canopy_h=32.0,
    post_r=7.0,
    led_half=6.0,           # LED channel on the hidden top face: 12 mm wide
    led_depth=8.0,
)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def centreline(p=P):
    n, q = p["samples"], p["lobes"]
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    theta = q * t
    c = np.cos(theta)
    # sin(2t) terms are equal for both strands at one plan angle, so the two
    # strands stay paired while the loops spread unevenly round the circle.
    phi = 2 * t + p["warp"] * np.sin(2 * t + p["warp_phase"])
    base = p["r_inner"] + p["a"] * (c + 1) + p["b"] * (np.cos(2 * theta) - 1)
    eps = p["irregular"] * np.sin(t + p["irregular_phase"])
    r = p["r_inner"] + (base - p["r_inner"]) * (1 + eps)
    w = (p["w_mid"] + p["w_lobe"] * c) * (1 + 0.6 * eps * np.clip(c, 0, 1))

    # Where the two strands at one plan angle swap sides is a real crossing.
    # The loops are irregular, so these are found from the path itself.
    xy = np.column_stack((r * np.cos(phi), r * np.sin(phi)))
    ds = np.linalg.norm(np.roll(xy, -1, 0) - xy, axis=1)
    splan = np.r_[0, np.cumsum(ds)[:-1]]
    total = splan[-1] + ds[-1]
    dr = r - np.roll(r, -n // 2)             # > 0: this strand is the outer one
    cross = np.where(np.sign(dr) != np.sign(np.roll(dr, -1)))[0]
    frac = dr[cross] / (dr[cross] - np.roll(dr, -1)[cross])
    s_cross = splan[cross] + frac * ds[cross]
    assert len(cross) == 2 * q, "expected one crossing between each pair of loops"
    s_ext = np.r_[s_cross[-1] - total, s_cross, s_cross[0] + total]
    k = np.searchsorted(s_ext, splan, side="right") - 1
    u = (splan - s_ext[k]) / (s_ext[k + 1] - s_ext[k])
    # Over/under height at a near-constant grade along the plan path.
    e = p["grade_ease"]
    uu = np.linspace(0, 1, 2001)
    f = np.clip(np.minimum(uu, 1 - uu) / e, 0, 1)
    f = f * f * (3 - 2 * f)
    S = np.r_[0, np.cumsum((f[1:] + f[:-1]) / 2)]
    S /= S[-1]
    g = 1 - 2 * np.interp(np.clip(u, 0, 1), uu, S)
    g = np.where(k % 2 == 0, g, -g)

    # "free" is 0 while the two strands overlap in plan and 1 once they have
    # separated; bank, twist and waves only act where the band is free.
    # Separation is the true plan distance to the nearest point of the other
    # strand (which crosses to the other side at a crossing), in band widths.
    win = np.arange(-n // 4, n // 4)
    j = (np.arange(n)[:, None] + n // 2 + win[None, :]) % n
    sep = np.sqrt(((xy[:, None, :] - xy[j]) ** 2).sum(-1)).min(1) / w
    free = np.clip((sep - p["free_start"]) / p["free_span"], 0, 1)
    free = free * free * (3 - 2 * free)
    outer = dr > 0
    z = p["h"] * g + free * np.where(outer, p["z_out"], p["z_in"])
    bank_o = np.radians(p["bank_out"]) * (1 + p["bank_var"] * np.sin(t + p["bank_phase"]))
    psi = free * np.where(outer, bank_o, -np.radians(p["bank_in"]))
    # Rolling S-twist. A strand heading for an over-crossing lifts the edge
    # that faces the other strand, and one heading under drops it, so the
    # twist always opens the gap between them. Through each loop the band
    # therefore rolls from one tilt to the other.
    free_t = np.clip((sep - p["twist_start"]) / p["twist_span"], 0, 1)
    free_t = free_t * free_t * (3 - 2 * free_t)
    roll = 1 + p["twist_var"] * np.sin(t + p["twist_phase"])
    psi = psi + np.radians(p["twist"]) * roll * free_t * g * np.where(outer, -1.0, 1.0)
    z = z + p["wave"] * free * np.sin(2 * np.pi * u) * np.sin(t + p["wave_phase"])
    # Low-pass the tilt along the band so twists ease in and out without lumps.
    sig = p["tilt_smooth"]
    kk = np.arange(-4 * sig, 4 * sig + 1)
    ker = np.exp(-0.5 * (kk / sig) ** 2)
    ker /= ker.sum()
    kfull = np.zeros(n)
    kfull[kk % n] = ker
    psi = np.real(np.fft.ifft(np.fft.fft(psi) * np.fft.fft(kfull)))
    # A steeply banked loop is made a little narrower, which limits the depth.
    w = w * (1 - p["bank_narrow"] * np.clip(np.abs(psi) / np.radians(60), 0, 1) ** 2)
    C = np.column_stack((xy[:, 0], xy[:, 1], z))
    return t, phi, C, w, psi


def ribbon_grid(p=P):
    t, phi, C, w, psi = centreline(p)
    n = len(t)
    T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
    rhat = np.column_stack((np.cos(phi), np.sin(phi), np.zeros(n)))
    # Cross-slope is measured square to the path in plan (like a banked road),
    # so psi is the true tilt of the band wherever the path is heading.
    side = np.column_stack((T[:, 1], -T[:, 0], np.zeros(n)))
    side = _unit(side)
    side *= np.sign(np.einsum("ij,ij->i", side, rhat))[:, None]
    D = np.cos(psi)[:, None] * side + np.sin(psi)[:, None] * np.array([0, 0, 1.0])
    D -= np.einsum("ij,ij->i", D, T)[:, None] * T
    D = _unit(D)
    N = _unit(np.cross(T, D))
    up = N * np.sign(N[:, 2:3])             # normal on the hidden (ceiling) side
    v = np.linspace(0, 1, p["across"])
    edge = np.minimum(v, 1 - v)
    taper = np.clip(edge / 0.07, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    seg = np.linalg.norm(np.roll(C, -1, 0) - C, axis=1)
    s = np.r_[0, np.cumsum(seg)[:-1]]
    L = seg.sum()
    turns = round(L / p["groove_diag"])       # whole grooves of drift round the loop
    phase = p["grooves"] * v[None, :] + (turns * s / L)[:, None]
    groove = p["groove_amp"] * np.sin(2 * np.pi * phase) * taper[None, :]
    V = (C[:, None, :]
         + D[:, None, :] * ((v - 0.5)[None, :, None] * w[:, None, None])
         + N[:, None, :] * groove[:, :, None])
    shift = p["top_z"] - V[..., 2].max()
    V[..., 2] += shift
    C = C.copy()
    C[:, 2] += shift
    return dict(t=t, phi=phi, C=C, w=w, T=T, D=D, N=N, up=up, V=V, s=s, length=L, psi=psi)


def clearance(g, p=P, step=4, across_step=4, neighbour=60):
    """Smallest gap between non-neighbouring parts of the band surface (mm)."""
    V = g["V"][::step, ::across_step]
    n_s, m = V.shape[:2]
    pts = V.reshape(-1, 3).astype(np.float32)
    st = np.repeat(np.arange(n_s) * step, m)
    n = len(g["V"])
    best, where = np.inf, None
    for a in range(0, len(pts), 1500):
        A = pts[a:a + 1500]
        d = np.sqrt(((A[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
        ds = np.abs(st[a:a + 1500, None] - st[None, :])
        ds = np.minimum(ds, n - ds)
        d[ds < neighbour] = np.inf
        i = np.unravel_index(np.argmin(d), d.shape)
        if d[i] < best:
            best, where = float(d[i]), (int(st[a + i[0]]), int(st[i[1]]))
    return best - p["thickness"] - 2 * p["groove_amp"], where


def led_frame(g, p=P):
    """Channel frame on the hidden top face, along the band centreline."""
    # Along the radially inner edge: a dark hem there reads as the edge, while
    # a channel down the middle shows through the translucent band as a line.
    inset = (g["w"] / 2 - p["led_edge_inset"])[:, None]
    base = g["C"] - g["D"] * inset + g["up"] * (p["thickness"] / 2)
    return base, g["T"], g["up"], np.cross(g["T"], g["up"])


def channel_rings(g, idx, p=P, closed_ends=True):
    base, T, U, S = led_frame(g, p)
    a, d, wall, f = p["led_half"], p["led_depth"], 1.2, 1.2
    prof = np.array([(-a, 0), (a, 0), (a, d), (a - wall, d), (a - wall, f),
                     (-a + wall, f), (-a + wall, d), (-a, d)])
    rings = base[idx][:, None, :] + prof[None, :, 0:1] * S[idx][:, None, :] + prof[None, :, 1:2] * U[idx][:, None, :]
    led = np.array([(-4, f + 0.05), (4, f + 0.05), (4, f + 1.0), (-4, f + 1.0)])
    leds = base[idx][:, None, :] + led[None, :, 0:1] * S[idx][:, None, :] + led[None, :, 1:2] * U[idx][:, None, :]
    return rings, leds


def report(p=P):
    g = ribbon_grid(p)
    V = g["V"]
    slope = np.degrees(np.arcsin(np.abs(g["T"][:, 2])))
    seg = np.linalg.norm(np.roll(g["C"], -1, 0) - g["C"], axis=1)
    cl, where = clearance(g, p)
    return dict(
        band_length_mm=round(float(g["length"])),
        footprint_mm=[round(float(np.ptp(V[..., 0]))), round(float(np.ptp(V[..., 1])))],
        top_z=round(float(V[..., 2].max()), 1),
        lowest_z=round(float(V[..., 2].min()), 1),
        width_range_mm=[round(float(g["w"].min())), round(float(g["w"].max()))],
        max_slope_deg=round(float(slope.max()), 1),
        bank_range_deg=[round(float(np.degrees(g["psi"].min()))), round(float(np.degrees(g["psi"].max())))],
        clearance_mm=round(cl, 1), clearance_at=where,
        skin_area_m2=round(float(np.sum(seg * g["w"]) / 1e6), 3),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
