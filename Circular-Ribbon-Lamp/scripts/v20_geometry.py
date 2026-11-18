"""V20 spiral rosette: geometry (millimetres, z = 0 is the ceiling, lamp hangs at negative z).

Reading of the user's spiral picture (17 Nov 2026): blades with narrow tails start at a dark
vortex round a small dot and sweep clockwise (seen from below), widening into broad rounded
crescents; a second whorl of broader petals and a third whorl of detached ovals sit outside.
Every blade overlaps its inner neighbour like the leaves of an iris.

Construction (exact, no random terms). Each petal is a ruled strip:
- the plan path is a logarithmic spiral with a fixed pitch angle psi,
      rho(h) = rho_in + h cos(psi),  phi(h) = phi0 + sigma tan(psi) ln(rho / rho_in),
  walked by horizontal arc length h;
- the long profile is a slope program theta(s) over the developed length s
  (flat root tab, gentle descent, one rolled lip at the tip), integrated into h(s) and drop d(s);
- the width is a lens: a long taper on the root side, a rounded superellipse on the tip side;
- the cross-section is a constant-radius convex cup plus a small shingle tilt, so the free edge
  of each petal rides below the covered edge of its inner neighbour.
d = drop below the ceiling (positive down). The model uses z = -d.
"""

import math

import numpy as np

P = dict(
    thickness=1.4,
    sigma=1,                 # +1: phi grows outward (counter-clockwise from above = clockwise from below)
    flange_r=96.0,           # dark hub flange radius
    flange_d=(23.0, 31.0),   # flange top and bottom drop (8 mm ring: 5.5 mm insert pockets leave 2.5 mm)
    hub_r=75.0,              # hub drum radius
    cap_r=94.0, cap_d=(32.6, 38.0),
    dot_r=24.0,
    plate_r=80.0, plate_t=8.0,
    depth_limit=140.0,
    outline_limit=1200.0,
    cross_R=420.0,           # constant cross-section cup radius
)


def smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


# ---------------------------------------------------------------------------- the three whorls
WHORLS = {
    # B: inner blades. Radial tab under the hub flange, then a tail that hugs the vortex, then a flare.
    "B": dict(n=5, phase_deg=0.0, rho_in=70.0, L=820.0, d0=31.7,
              psi_knots=[(0, 50), (34, 50), (110, 82), (250, 76), (560, 62), (820, 60)],
              tab=34.0, tab_w=26.0,
              a0=4.8, a1=3.6, roll_len=82.0, roll_deg=58.0,
              W=225.0, asym=0.20, u_peak=0.78, q_root=2.4, q_tip=1.9,
              tan_beta=0.16),
    # M: outer blades. The same crescent form at a larger scale, tails starting under B's bellies.
    "M": dict(n=5, phase_deg=36.0, rho_in=318.0, L=700.0, d0=94.0,
              psi_knots=[(0, 80), (150, 80), (450, 70), (700, 64)],
              tab=0.0, tab_w=0.0,
              a0=2.4, a1=1.8, roll_len=88.0, roll_deg=60.0,
              W=250.0, asym=0.14, u_peak=0.62, q_root=2.0, q_tip=1.9, root="taper",
              tan_beta=0.13),
    # O: rim ovals, radiating from under the M lobes (lower than M so the studs hang from M), lipped at the edge.
    "O": dict(n=5, phase_deg=48.0, rho_in=450.0, L=200.0, d0=133.0,
              psi_knots=[(0, 50), (200, 45)],
              tab=0.0, tab_w=0.0,
              a0=1.4, a1=0.8, roll_len=76.0, roll_deg=56.0,
              W=150.0, asym=0.10, u_peak=0.52, q_root=2.2, q_tip=1.9, root="round",
              tan_beta=0.06),
}


def lens(u, up, q1, q2, root="taper"):
    """Width factor on u in [0, 1] with peak 1 at u = up. Root side: a long taper (sine) or a
    rounded superellipse; tip side: rounded superellipse. Both have zero slope at the peak."""
    u = np.asarray(u, float)
    out = np.zeros_like(u)
    a = u <= up
    xr = np.clip(u[a] / up, 0, 1)
    if root == "taper":
        out[a] = np.sin(0.5 * np.pi * xr) ** q1
    else:
        out[a] = (1.0 - (1.0 - xr) ** q1) ** (1.0 / q1)
    xt = np.clip((u[~a] - up) / (1 - up), 0, 1)
    out[~a] = (1.0 - xt ** q2) ** (1.0 / q2)
    return out


def sample_s(L, n):
    """Developed-length samples, denser at both ends where the outline turns quickly."""
    t = np.linspace(0, 1, n)
    return L * (0.55 * t + 0.45 * (0.5 - 0.5 * np.cos(np.pi * t)))


def knot_curve(s, knots):
    """Smootherstep interpolation through (s, value) knots; constant outside."""
    s = np.asarray(s, float)
    out = np.full_like(s, knots[0][1])
    for (s0, v0), (s1, v1) in zip(knots[:-1], knots[1:]):
        m = s >= s0
        out[m] = v1 if s1 <= s0 else v0 + (v1 - v0) * smoother((s[m] - s0) / (s1 - s0))
    return out


def theta_program(s, w):
    L = w["L"]
    tab, a0, a1 = w["tab"], math.radians(w["a0"]), math.radians(w["a1"])
    r0 = L - w["roll_len"]
    ar = -math.radians(w["roll_deg"])
    knots = [(0.0, 0.0), (tab, 0.0), (tab + 80.0, a0), (r0, a1), (L, ar)]
    th = np.zeros_like(s)
    for (s0, t0), (s1, t1) in zip(knots[:-1], knots[1:]):
        m = (s >= s0) & (s <= s1)
        if s1 > s0:
            th[m] = t0 + (t1 - t0) * smoother((s[m] - s0) / (s1 - s0))
    return th


def build_petal(w, index, ns=260, nv=33):
    """Mid-surface grid S[ns, nv, 3] (mm, z = -d), unit normals N facing the room (down),
    plus developed coordinates. index selects the rotation about the hub."""
    sg = P["sigma"]
    L = w["L"]
    s = sample_s(L, ns)
    th = theta_program(s, w)
    ds = np.gradient(s)
    h = np.concatenate([[0.0], np.cumsum(0.5 * (np.cos(th[1:]) + np.cos(th[:-1])) * np.diff(s))])
    dd = np.concatenate([[0.0], np.cumsum(0.5 * (np.sin(th[1:]) + np.sin(th[:-1])) * np.diff(s))])
    d_c = w["d0"] + dd
    # plan path: pitch angle psi follows a smooth knot program (hugging the hub, then flaring out)
    psi_s = np.radians(knot_curve(s, w["psi_knots"]))
    dh = np.diff(h)
    rho = np.empty_like(s)
    phi = np.empty_like(s)
    rho[0] = w["rho_in"]
    phi[0] = math.radians(w["phase_deg"] + index * 360.0 / w["n"])
    for k in range(len(s) - 1):
        pm = 0.5 * (psi_s[k] + psi_s[k + 1])
        rho[k + 1] = rho[k] + math.cos(pm) * dh[k]
        phi[k + 1] = phi[k] + sg * math.sin(pm) * dh[k] / (0.5 * (rho[k] + rho[k + 1]))
    psi = psi_s
    # plan tangent and the free-side normal (left of travel for sigma = +1)
    e_r = np.stack([np.cos(phi), np.sin(phi)], 1)
    e_p = np.stack([-np.sin(phi), np.cos(phi)], 1)
    tan = np.cos(psi)[:, None] * e_r + sg * np.sin(psi)[:, None] * e_p
    nrm = np.stack([-tan[:, 1], tan[:, 0]], 1) * sg       # +y side = free (overlapping) edge
    c_xy = rho[:, None] * e_r
    # width program
    tab = w["tab"]
    u = np.clip((s - tab) / (L - tab), 0, 1)
    e = lens(u, w["u_peak"], w["q_root"], w["q_tip"], w.get("root", "taper"))
    W = w["W"]
    wF = 0.5 * W * (1 + w["asym"]) * e
    wC = 0.5 * W * (1 - w["asym"]) * e
    if tab > 0:
        tw = w["tab_w"] / 2
        blend = smoother((s - tab * 0.8) / (tab * 0.2 + 1e-9)) if tab else 1
        wF = np.where(s <= tab, tw, np.maximum(tw, wF))
        wC = np.where(s <= tab, tw, np.maximum(tw, wC))
    wF = np.maximum(wF, 1.5)
    wC = np.maximum(wC, 1.5)
    v = np.linspace(-1, 1, nv)
    y = np.where(v[None, :] >= 0, v[None, :] * wF[:, None], v[None, :] * wC[:, None])   # [ns, nv]
    # cross-section: convex cup + shingle tilt (both ramp in after the tab)
    ramp = smoother((s - tab) / 90.0)[:, None] if tab else 1.0
    bank = (w["tan_beta"] * y - y * y / (2 * P["cross_R"])) * ramp
    d = d_c[:, None] + bank
    xy = c_xy[:, None, :] + y[:, :, None] * nrm[:, None, :]
    S = np.concatenate([xy, -d[:, :, None]], axis=2)
    # normals: handedness from the construction, so they stay continuous through the rolled lip
    ds_ = np.gradient(S, axis=0)
    dv_ = np.gradient(S, axis=1)
    N = -sg * np.cross(ds_, dv_)
    N /= np.maximum(np.linalg.norm(N, axis=2, keepdims=True), 1e-9)
    return dict(S=S, N=N, s=s, L=L, rho=rho, phi=phi, d_c=d_c, y=y, wF=wF, wC=wC, theta=th, h=h,
                whorl=None, index=index)


def build_all(ns=None):
    out = []
    for name, w in WHORLS.items():
        for i in range(w["n"]):
            p = build_petal(w, i)
            p["whorl"] = name
            p["id"] = f"{name}{i + 1}"
            out.append(p)
    return out


def shell_faces(p, t=None, with_edges=True):
    """Vertices and quads of the closed shell of a petal (visible face, hidden face, rim).
    Returns (verts, quads, kind) where kind tags each quad: 'vis', 'hid', 'rim'."""
    t = P["thickness"] if t is None else t
    S, N = p["S"], p["N"]
    ns, nv = S.shape[:2]
    vis = S + N * (t / 2)
    hid = S - N * (t / 2)
    verts = np.concatenate([vis.reshape(-1, 3), hid.reshape(-1, 3)])
    n = ns * nv
    vid = lambda side, i, j: side * n + i * nv + j
    quads, kind = [], []
    flip = P["sigma"] > 0          # grid winding (s, v) faces away from the room when sigma = +1
    for i in range(ns - 1):
        for j in range(nv - 1):
            q0 = (vid(0, i, j), vid(0, i + 1, j), vid(0, i + 1, j + 1), vid(0, i, j + 1))
            q1 = (vid(1, i, j), vid(1, i, j + 1), vid(1, i + 1, j + 1), vid(1, i + 1, j))
            quads.append(q0[::-1] if flip else q0)
            kind.append("vis")
            quads.append(q1[::-1] if flip else q1)
            kind.append("hid")
    if with_edges:
        loop = ([(0, j) for j in range(nv)] + [(i, nv - 1) for i in range(1, ns)]
                + [(ns - 1, j) for j in range(nv - 2, -1, -1)] + [(i, 0) for i in range(ns - 2, 0, -1)])
        for k in range(len(loop)):
            (i0, j0), (i1, j1) = loop[k], loop[(k + 1) % len(loop)]
            quads.append((vid(0, i0, j0), vid(1, i0, j0), vid(1, i1, j1), vid(0, i1, j1)))
            kind.append("rim")
    return verts, quads, kind


def shell_from_grids(vis, hid):
    """Closed shell between a visible-face grid and a hidden-face grid (ns, nv, 3 each).
    Returns verts (2*ns*nv, 3), quads and kinds; windings face outward for sigma = +1 grids built as in build_petal."""
    ns, nv = vis.shape[:2]
    verts = np.concatenate([vis.reshape(-1, 3), hid.reshape(-1, 3)])
    n = ns * nv
    vid = lambda side, i, j: side * n + i * nv + j
    flip = P["sigma"] > 0
    quads, kind = [], []
    for i in range(ns - 1):
        for j in range(nv - 1):
            q0 = (vid(0, i, j), vid(0, i + 1, j), vid(0, i + 1, j + 1), vid(0, i, j + 1))
            q1 = (vid(1, i, j), vid(1, i, j + 1), vid(1, i + 1, j + 1), vid(1, i + 1, j))
            quads.append(q0[::-1] if flip else q0)
            kind.append("vis")
            quads.append(q1[::-1] if flip else q1)
            kind.append("hid")
    loop = ([(0, j) for j in range(nv)] + [(i, nv - 1) for i in range(1, ns)]
            + [(ns - 1, j) for j in range(nv - 2, -1, -1)] + [(i, 0) for i in range(ns - 2, 0, -1)])
    for k in range(len(loop)):
        (i0, j0), (i1, j1) = loop[k], loop[(k + 1) % len(loop)]
        quads.append((vid(0, i0, j0), vid(1, i0, j0), vid(1, i1, j1), vid(0, i1, j1)))
        kind.append("rim")
    return verts, quads, kind


def plan_outline(p):
    """Closed plan-view outline (x, y) of the petal."""
    S = p["S"]
    ns, nv = S.shape[:2]
    pts = ([S[0, j, :2] for j in range(nv)] + [S[i, nv - 1, :2] for i in range(1, ns)]
           + [S[ns - 1, j, :2] for j in range(nv - 2, -1, -1)] + [S[i, 0, :2] for i in range(ns - 2, 0, -1)])
    return np.array(pts)
