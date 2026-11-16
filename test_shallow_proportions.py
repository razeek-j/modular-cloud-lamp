import numpy as np

cx_px, cy_px = 507, 330
scale_m_per_px = 1.200 / 771.0 # 1.5564 mm/px

def px_to_m(x_px, y_px, z_mm):
    x = (x_px - cx_px) * scale_m_per_px
    y = (cy_px - y_px) * scale_m_per_px
    z = -abs(z_mm) * 0.001 # Z is negative below ceiling (Z=0 is ceiling)
    return x, y, z

# Let's test the depth budget:
# Max depth is 95 mm below ceiling!
# That means z_mm goes from 15 mm to 95 mm max!
print("Shallow depth range: -15 mm to -95 mm (max drop 95 mm)")
