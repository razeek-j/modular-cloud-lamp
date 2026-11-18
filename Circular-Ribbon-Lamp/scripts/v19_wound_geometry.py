"""V19 concept: ribbons wound around a flat ring at a constant pitch.

Reading of the reference: the ribbons are wound around a flat, closed ring
(like ribbon wound round a doughnut). That one rule explains the photo:
- the underside passes give evenly spaced broad bellies along the front;
- where a ribbon wraps round the ring's outer edge it rolls over in a curl,
  and at the far ends of the oval these curls read as loops;
- seen from below, the top passes slant the other way through the gaps, so
  the crossings form a regular X pattern;
- width looks different in different places: a band wound on a flat ring is
  broad on the flat underside and narrow where it rolls round the edge.

Construction (exact, no random terms):
- ring centreline: an ellipse (rounder than the reference's band);
- ring cross-section ("tube"): a flat ellipse, wide and shallow;
- ribbon i is the strip of the tube surface between two helices:
  tube angle phi in [q*theta + phase_i - half_i, q*theta + phase_i + half_i],
  so the ribbons wind at one constant pitch and never touch;
- ribbons have deliberately different widths (half_i), widest first.

Units: millimetres; z = 0 is the ceiling.
"""

import numpy as np

P = dict(
    a=470.0, b=290.0,          # ring centreline ellipse semi-axes (an oval, rounder than the photo's band)
    tube_r=105.0,              # tube half-width (radial)
    tube_z=74.0,               # tube half-height: nearly round, so outer passes stand up as broad bellies
    z_c=-96.0,                 # tube centre height (top 22 mm below the ceiling)
    q=4,                       # wraps of each ribbon round the tube per lap
    n_theta=2400, n_across=41,
    thickness=1.8,
    canopy_r=150.0, canopy_h=32.0,
    core_w=14.0, core_h=8.0,   # hidden core ring (carries the LEDs) at the tube centre
)

RIBBONS = [
    # name, phase (fraction of a turn), half-band in tube angle (radians)
    dict(name="A", phase=0.0, half=1.05),     # wide ribbon, 128-182 mm
    dict(name="B", phase=0.5, half=0.75),     # narrower ribbon, 101-143 mm
]


def ring(theta, p=P):
    """Ring centreline point, unit tangent and outward horizontal normal."""
    x, y = p["a"] * np.cos(theta), p["b"] * np.sin(theta)
    dx, dy = -p["a"] * np.sin(theta), p["b"] * np.cos(theta)
    t = np.column_stack((dx, dy)) / np.hypot(dx, dy)[:, None]
    nrm = np.column_stack((t[:, 1], -t[:, 0]))                 # outward for a CCW ellipse
    return np.column_stack((x, y)), t, nrm


def tube_point(theta, phi, p=P):
    c, t, nrm = ring(theta, p)
    rr = p["tube_r"] * np.cos(phi)
    zz = p["tube_z"] * np.sin(phi)
    xy = c + nrm * rr[:, None]
    return np.column_stack((xy, p["z_c"] + zz))


def tube_normal(theta, phi, p=P):
    """Outward surface normal of the tube (flat ellipse cross-section)."""
    c, t, nrm = ring(theta, p)
    nr = np.cos(phi) / p["tube_r"]
    nz = np.sin(phi) / p["tube_z"]
    v = np.column_stack((nrm * nr[:, None], nz))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def ribbon_grid(rb, p=P):
    th = np.linspace(0, 2 * np.pi, p["n_theta"], endpoint=False)
    v = np.linspace(-1, 1, p["n_across"])
    TH = np.repeat(th, len(v))
    PHI = (p["q"] * TH + 2 * np.pi * rb["phase"] + np.tile(v, len(th)) * rb["half"])
    S = tube_point(TH, PHI, p).reshape(len(th), len(v), 3)
    N = tube_normal(TH, PHI, p).reshape(len(th), len(v), 3)
    return S, N


def report(p=P):
    out = {}
    allp = []
    for rb in RIBBONS:
        S, N = ribbon_grid(rb, p)
        allp.append(S.reshape(-1, 3))
        acr = np.linalg.norm(S[:, -1] - S[:, 0], axis=1)
        out[rb["name"]] = dict(width_mm=[round(float(acr.min())), round(float(acr.max()))],
                               length_mm=round(float(np.linalg.norm(np.diff(S[:, len(S[0]) // 2], axis=0), axis=1).sum())))
    allp = np.vstack(allp)
    out["footprint_mm"] = [round(float(np.ptp(allp[:, 0]))), round(float(np.ptp(allp[:, 1])))]
    out["top_z"] = round(float(allp[:, 2].max()), 1)
    out["lowest_z"] = round(float(allp[:, 2].min()), 1)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
