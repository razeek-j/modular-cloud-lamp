import numpy as np

cx_px, cy_px = 507, 330
scale_m_per_px = 1.200 / 771.0

def px_to_m(x_px, y_px, z_mm):
    x = (x_px - cx_px) * scale_m_per_px
    y = (cy_px - y_px) * scale_m_per_px
    z = -abs(z_mm) * 0.001
    return x, y, z

from tune_ribbon_widths import REVISED_A, REVISED_B, REVISED_C, catmull_3d

for name, st in [('B', REVISED_B), ('A', REVISED_A), ('C', REVISED_C)]:
    pts_out = np.array([px_to_m(s[0], s[1], s[2]) for s in st])
    pts_in  = np.array([px_to_m(s[3], s[4], s[5]) for s in st])
    num_rows = len(st) * 16
    ts = np.linspace(0, len(st) - 1, num_rows)
    r_out = np.array([catmull_3d(pts_out, t, False) for t in ts])
    r_in  = np.array([catmull_3d(pts_in,  t, False) for t in ts])
    widths = np.linalg.norm(r_out - r_in, axis=1) * 1000.0 # in mm
    z_min = min(r_out[:, 2].min(), r_in[:, 2].min()) * 1000.0
    z_max = max(r_out[:, 2].max(), r_in[:, 2].max()) * 1000.0
    print(f'Ribbon {name}:')
    print(f'   Width range: min={widths.min():.1f} mm, max={widths.max():.1f} mm, mean={widths.mean():.1f} mm')
    print(f'   Depth range (Z below ceiling): from {z_max:.1f} mm to {z_min:.1f} mm (total drop {-z_min:.1f} mm)')
