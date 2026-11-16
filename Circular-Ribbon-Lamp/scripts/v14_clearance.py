"""Minimum clearance between non-neighbouring parts of the V14 band (mm)."""
import numpy as np
import v14_knot_geometry as K


def clearance(p=K.P, step=4, across_step=4, neighbour=40):
    g = K.ribbon_grid(p)
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
    # sheet surfaces are thickness/2 + groove away from the mid-surface
    return best - p["thickness"] - 2 * p["groove_amp"], where


if __name__ == "__main__":
    print(clearance())
