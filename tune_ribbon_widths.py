import cv2
import numpy as np

# Load original user image
im = cv2.imread('/Users/razeek/.gemini/antigravity/brain/4a61c6cc-fb23-4079-9099-70a8d3085dca/.user_uploaded/media_1794059533316_1ecf1034.jpg')
H, W = im.shape[:2]
cx, cy = 507, 330
scale = 1.200 / 771.0 # m per pixel

def catmull_3d(pts, t, closed=False):
    n = len(pts)
    i = int(np.floor(t))
    u = t - i
    if closed:
        p0 = pts[(i - 1) % n]
        p1 = pts[i % n]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
    else:
        p0 = pts[max(0, i - 1)]
        p1 = pts[min(n - 1, i)]
        p2 = pts[min(n - 1, i + 1)]
        p3 = pts[min(n - 1, i + 2)]
    return 0.5 * (
        (2 * p1) +
        (-p0 + p2) * u +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * (u ** 2) +
        (-p0 + 3 * p1 - 3 * p2 + p3) * (u ** 3)
    )

def eval_spline(pts, num_samples=300, closed=False):
    pts = np.asarray(pts, float)
    n = len(pts)
    ts = np.linspace(0, n if closed else n - 1, num_samples, endpoint=not closed)
    return np.array([catmull_3d(pts, t, closed) for t in ts])

# Let us precisely define the revised stations for A, B, and C with the exact variable widths
# Each station: (out_x, out_y, out_z_mm, in_x, in_y, in_z_mm)
# Note: z_mm is SHALLOW towards ceiling: ceiling is 0, depths are 15 mm to 95 mm max!

REVISED_B = [
    # Emerges from canopy at top-right
    (540, 275, 18, 515, 295, 22),
    (575, 205, 32, 535, 245, 38),
    (625, 135, 48, 565, 205, 54),
    (685, 75,  62, 605, 175, 68),
    (755, 45,  75, 655, 165, 80),  # High crest apex - fanning out to ~200mm
    (820, 60,  82, 715, 185, 85),
    (870, 115, 88, 775, 225, 88),
    (890, 190, 92, 810, 280, 88),  # Right billow
    (888, 270, 92, 815, 350, 85),
    (865, 355, 88, 795, 420, 80),
    (815, 435, 82, 755, 465, 75),  # Tapering as it rolls
    # Roll under into slender curl
    (755, 475, 75, 710, 485, 70),
    (690, 480, 70, 665, 480, 65),
    (635, 490, 68, 620, 520, 65),
    (605, 535, 72, 625, 570, 72),
    (615, 595, 80, 655, 605, 80),
    (660, 630, 85, 690, 605, 85),  # Slender curl bottom
    (705, 605, 80, 705, 565, 78),
    (695, 545, 70, 670, 535, 68),
    (650, 505, 58, 615, 495, 55),  # Tuck under
    (580, 480, 45, 550, 465, 40),
    (535, 410, 30, 515, 395, 28),
    (520, 350, 18, 510, 335, 15)   # Return to canopy
]

REVISED_A = [
    # Top-left loop & slender horizontal bridge
    (485, 280, 18, 470, 300, 22),
    (435, 225, 32, 440, 255, 38),
    (375, 175, 48, 395, 215, 54),
    (305, 145, 62, 340, 195, 66),
    (230, 140, 74, 280, 195, 78),
    (165, 165, 80, 220, 215, 82),  # Slender outer loop (~75mm width)
    (145, 230, 82, 195, 260, 82),
    (170, 290, 78, 220, 310, 78),
    (220, 330, 72, 265, 345, 70),
    # Slender horizontal bridge under canopy (leaving Contour 6 open!)
    (290, 355, 65, 330, 360, 62),
    (370, 370, 58, 410, 370, 55),  # Narrow ~70mm cross ribbon
    (450, 375, 50, 485, 370, 48),
    (525, 365, 40, 545, 350, 38),
    (565, 335, 28, 560, 320, 25),
    (535, 295, 18, 520, 290, 15)
]

REVISED_C = [
    # Lower broad sweep
    (480, 365, 18, 470, 350, 22),
    (415, 395, 32, 430, 380, 36),
    (335, 430, 48, 365, 410, 52),
    (245, 455, 62, 290, 430, 65),
    (175, 435, 74, 225, 425, 75),
    (130, 360, 80, 180, 370, 80),  # Outer left sweep
    (135, 300, 78, 190, 325, 78),
    (175, 270, 72, 225, 300, 72),
    (235, 280, 65, 265, 330, 65),
    (260, 370, 60, 290, 420, 62),
    (275, 475, 68, 310, 500, 70),
    (315, 575, 78, 350, 550, 80),
    (380, 642, 85, 415, 575, 88),  # Bottom apex - broad cradle (~140mm)
    (465, 630, 85, 485, 560, 88),
    (540, 575, 78, 540, 525, 78),  # Tapering towards right tuck
    (595, 515, 68, 575, 485, 65),
    (630, 450, 52, 595, 435, 48),
    (620, 385, 35, 580, 380, 32),
    (570, 350, 20, 545, 340, 16)
]

# Draw overlay and check against image
overlay = im.copy()
for name, stations, color in [('B', REVISED_B, (0, 165, 255)), ('A', REVISED_A, (0, 255, 255)), ('C', REVISED_C, (255, 180, 0))]:
    st = np.array(stations)
    out_pts = eval_spline(st[:, 0:2], 300, closed=False)
    in_pts  = eval_spline(st[:, 3:5], 300, closed=False)
    cv2.polylines(overlay, [np.int32(out_pts)], False, color, 2)
    cv2.polylines(overlay, [np.int32(in_pts)], False, color, 2)
    # Fill polygon semi-transparently to verify open holes:
    poly = np.vstack([out_pts, in_pts[::-1]])
    patch = overlay.copy()
    cv2.fillPoly(patch, [np.int32(poly)], color)
    cv2.addWeighted(patch, 0.35, overlay, 0.65, 0, overlay)

cv2.imwrite('/Users/razeek/Projects/3D printing/revised_overlay.jpg', overlay)
print('Saved revised_overlay.jpg')
