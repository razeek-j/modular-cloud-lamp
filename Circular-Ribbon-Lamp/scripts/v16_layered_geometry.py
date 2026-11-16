"""V16 layered ribbon: one broad band, three times round, three layers deep.

The user asked for more ribbon layers than V15. Here the band follows a
(3,4) knot path: it circles the centre three times, so every plan direction
holds three strands of the band, layered over each other. Four outer loops,
four inner loops under the ceiling disc, eight crossings.

On a (3,q) knot the three strands at one plan angle sit a third of a cycle
apart, so when two of them cross (one high, one low) the third is far away
radially. The band lies near flat at the crossings and banks and rolls in
the loops, as in V15.

All units are millimetres; z = 0 is the ceiling, negative is downward.
"""

import numpy as np

P = dict(
    samples=3600,
    across=151,
    turns=3,                # times round the centre = layers
    lobes=4,
    r_inner=122.0,
    a=198.0,
    b=20.0,
    warp=0.20,              # uneven loop spacing (radians)
    warp_phase=0.7,
    irregular=0.16,         # loop-to-loop size variation
    irregular_phase=2.4,
    h=54.0,                 # height amplitude of the over/under wave
    z_out=-18.0,
    z_in=-12.0,             # inner loops pass clear below the ceiling disc
    top_z=-20.0,
    w_mid=168.0,
    w_lobe=26.0,
    bank_out=36.0,          # degrees at the outer loops
    bank_var=0.5,
    bank_phase=4.0,
    bank_in=10.0,
    twist=34.0,             # degrees of rolling S-twist
    twist_var=0.5,
    twist_phase=1.2,
    free_start=0.60,        # tilt only once strands are this far apart in plan (x width)
    free_span=0.5,
    tilt_smooth=30,
    bank_narrow=0.2,
    grooves=16,
    groove_amp=0.55,
    groove_diag=34.0,
    thickness=1.8,
    canopy_r=100.0,
    canopy_h=32.0,
    post_r=7.0,
    led_half=6.0,
    led_depth=8.0,
    led_edge_inset=11.0,
)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _smooth(x, sig):
    n = len(x)
    kk = np.arange(-4 * sig, 4 * sig + 1)
    ker = np.exp(-0.5 * (kk / sig) ** 2)
    ker /= ker.sum()
    kfull = np.zeros(n)
    kfull[kk % n] = ker
    return np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(kfull)))


def centreline(p=P):
    n, q, m = p["samples"], p["lobes"], p["turns"]
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    theta = q * t
    c, s = np.cos(theta), np.sin(theta)
    # sin(m*t) terms are equal for all strands at one plan angle.
    phi = m * t + p["warp"] * np.sin(m * t + p["warp_phase"])
    base = p["r_inner"] + p["a"] * (c + 1) + p["b"] * (np.cos(2 * theta) - 1)
    eps = p["irregular"] * (0.8 * np.sin(t + p["irregular_phase"]) + 0.2 * np.sin(2 * t + 0.5))
    r = p["r_inner"] + (base - p["r_inner"]) * (1 + eps)
    w = (p["w_mid"] + p["w_lobe"] * c) * (1 + 0.6 * eps * np.clip(c, 0, 1))
    xy = np.column_stack((r * np.cos(phi), r * np.sin(phi)))

    # Plan distance to the nearest part of any other strand, in band widths.
    sep = np.full(n, np.inf)
    guard = n // (2 * m * q) * 3              # skip this strand's own neighbourhood
    idx = np.arange(n)
    for a0 in range(0, n, 600):
        sl = slice(a0, a0 + 600)
        d = np.sqrt(((xy[sl, None, :] - xy[None, :, :]) ** 2).sum(-1))
        gap = np.abs(idx[sl, None] - idx[None, :])
        gap = np.minimum(gap, n - gap)
        d[gap < guard] = np.inf
        sep[sl] = d.min(1)
    sep = sep / w
    free = np.clip((sep - p["free_start"]) / p["free_span"], 0, 1)
    free = free * free * (3 - 2 * free)

    out_w = np.clip(c, 0, 1) ** 2
    in_w = np.clip(-c, 0, 1) ** 2
    z = p["h"] * s + free * (p["z_out"] * out_w + p["z_in"] * in_w)
    bank_o = np.radians(p["bank_out"]) * (1 + p["bank_var"] * np.sin(t + p["bank_phase"]))
    psi = free * (bank_o * out_w - np.radians(p["bank_in"]) * in_w)
    # Rolling S-twist in the direction that keeps the three strands tangent
    # to one shared cross-section, so it opens gaps instead of closing them.
    roll = 1 + p["twist_var"] * np.sin(t + p["twist_phase"])
    psi = psi - np.radians(p["twist"]) * roll * free * np.sin(2 * theta)
    psi = _smooth(psi, p["tilt_smooth"])
    w = w * (1 - p["bank_narrow"] * np.clip(np.abs(psi) / np.radians(60), 0, 1) ** 2)
    C = np.column_stack((xy[:, 0], xy[:, 1], z))
    return t, phi, C, w, psi


def ribbon_grid(p=P):
    t, phi, C, w, psi = centreline(p)
    n = len(t)
    T = _unit(np.roll(C, -1, 0) - np.roll(C, 1, 0))
    rhat = np.column_stack((np.cos(phi), np.sin(phi), np.zeros(n)))
    side = _unit(np.column_stack((T[:, 1], -T[:, 0], np.zeros(n))))
    side *= np.sign(np.einsum("ij,ij->i", side, rhat))[:, None]
    D = np.cos(psi)[:, None] * side + np.sin(psi)[:, None] * np.array([0, 0, 1.0])
    D -= np.einsum("ij,ij->i", D, T)[:, None] * T
    D = _unit(D)
    N = _unit(np.cross(T, D))
    up = N * np.sign(N[:, 2:3])
    v = np.linspace(0, 1, p["across"])
    edge = np.minimum(v, 1 - v)
    taper = np.clip(edge / 0.07, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    seg = np.linalg.norm(np.roll(C, -1, 0) - C, axis=1)
    s = np.r_[0, np.cumsum(seg)[:-1]]
    L = seg.sum()
    drift = round(L / p["groove_diag"])
    phase = p["grooves"] * v[None, :] + (drift * s / L)[:, None]
    groove = p["groove_amp"] * np.sin(2 * np.pi * phase) * taper[None, :]
    V = (C[:, None, :]
         + D[:, None, :] * ((v - 0.5)[None, :, None] * w[:, None, None])
         + N[:, None, :] * groove[:, :, None])
    shift = p["top_z"] - V[..., 2].max()
    V[..., 2] += shift
    C = C.copy()
    C[:, 2] += shift
    return dict(t=t, phi=phi, C=C, w=w, T=T, D=D, N=N, up=up, V=V, s=s, length=L, psi=psi)


def clearance(g, p=P, step=4, across_step=4, neighbour=150):
    """Smallest gap between non-neighbouring parts of the band surface (mm)."""
    V = g["V"][::step, ::across_step]
    n_s, m = V.shape[:2]
    pts = V.reshape(-1, 3).astype(np.float32)
    st = np.repeat(np.arange(n_s) * step, m)
    n = len(g["V"])
    best, where = np.inf, None
    for a in range(0, len(pts), 1200):
        A = pts[a:a + 1200]
        d = np.sqrt(((A[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
        ds = np.abs(st[a:a + 1200, None] - st[None, :])
        ds = np.minimum(ds, n - ds)
        d[ds < neighbour] = np.inf
        i = np.unravel_index(np.argmin(d), d.shape)
        if d[i] < best:
            best, where = float(d[i]), (int(st[a + i[0]]), int(st[i[1]]))
    return best - p["thickness"] - 2 * p["groove_amp"], where


def led_frame(g, p=P):
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


def report(p=P, step=6):
    g = ribbon_grid(p)
    V = g["V"]
    seg = np.linalg.norm(np.roll(g["C"], -1, 0) - g["C"], axis=1)
    cl, where = clearance(g, p, step=step, across_step=step)
    return dict(
        band_length_mm=round(float(g["length"])),
        footprint_mm=[round(float(np.ptp(V[..., 0]))), round(float(np.ptp(V[..., 1])))],
        lowest_z=round(float(V[..., 2].min()), 1),
        width_range_mm=[round(float(g["w"].min())), round(float(g["w"].max()))],
        max_slope_deg=round(float(np.degrees(np.arcsin(np.abs(g["T"][:, 2]).max()))), 1),
        bank_range_deg=[round(float(np.degrees(g["psi"].min()))), round(float(np.degrees(g["psi"].max())))],
        clearance_mm=round(cl, 1), clearance_at=where,
        skin_area_m2=round(float(np.sum(seg * g["w"]) / 1e6), 3),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(report()))
