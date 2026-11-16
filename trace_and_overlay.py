import cv2
import numpy as np

# Load original image
im = cv2.imread('/Users/razeek/.gemini/antigravity/brain/4a61c6cc-fb23-4079-9099-70a8d3085dca/.user_uploaded/media_1794059533316_1ecf1034.jpg')
H, W = im.shape[:2]
cx, cy = 507, 330
scale = 1.200 / 771.0

def catmull(p, t, closed=True):
    n = len(p)
    i = int(np.floor(t))
    u = t - i
    if closed:
        p0 = p[(i - 1) % n]
        p1 = p[i % n]
        p2 = p[(i + 1) % n]
        p3 = p[(i + 2) % n]
    else:
        p0 = p[max(0, i - 1)]
        p1 = p[min(n - 1, i)]
        p2 = p[min(n - 1, i + 1)]
        p3 = p[min(n - 1, i + 2)]
    return 0.5 * (
        (2 * p1) +
        (-p0 + p2) * u +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * (u ** 2) +
        (-p0 + 3 * p1 - 3 * p2 + p3) * (u ** 3)
    )

def eval_spline(pts, num_samples=200, closed=True):
    pts = np.asarray(pts, float)
    n = len(pts)
    ts = np.linspace(0, n if closed else n - 1, num_samples, endpoint=not closed)
    return np.array([catmull(pts, t, closed) for t in ts])

# Detailed station points for outer and inner rails of each ribbon in pixel coords:
# Each station is (out_x, out_y, out_z_mm, in_x, in_y, in_z_mm)
# Note: z_mm is positive downward from ceiling (ceiling is 0)

# RIBBON B (Front-Right Big Crest & Lower-Right Roll):
STATIONS_B = [
    # Emerges from canopy at top-right
    (540, 275, 40, 520, 310, 50),
    (580, 200, 70, 545, 260, 80),
    (630, 130, 105, 580, 225, 115),
    (690, 70, 140, 630, 205, 150),
    (755, 45, 165, 680, 210, 175), # High crest apex
    (815, 60, 180, 735, 235, 190),
    (865, 115, 195, 785, 275, 200),
    (888, 190, 205, 815, 330, 205), # Outer right billow
    (890, 270, 210, 815, 400, 205),
    (865, 360, 205, 790, 460, 195),
    (815, 440, 190, 740, 495, 180),
    (745, 485, 175, 675, 495, 165), # Roll onset
    # Teardrop tuck / curl
    (670, 485, 160, 615, 480, 150),
    (605, 495, 165, 580, 530, 165),
    (575, 550, 180, 600, 590, 185),
    (600, 620, 200, 650, 625, 205),
    (655, 645, 205, 695, 610, 200),
    (710, 615, 195, 715, 550, 185),
    (705, 540, 175, 670, 515, 165),
    (650, 495, 150, 590, 490, 140),
    (575, 480, 120, 530, 460, 110),
    (530, 410, 80, 500, 390, 70),
    (520, 350, 45, 510, 335, 40)  # Re-enters canopy
]

# RIBBON A (Upper-Left Loop & Middle Cross):
STATIONS_A = [
    # Canopy top-left
    (485, 280, 40, 470, 305, 45),
    (430, 220, 65, 440, 260, 75),
    (360, 170, 95, 395, 225, 105),
    (285, 140, 130, 345, 205, 140),
    (210, 140, 155, 285, 205, 165), # Upper-left crest
    (155, 175, 170, 230, 230, 175),
    (145, 240, 175, 215, 280, 175),
    (175, 305, 165, 245, 330, 160),
    (230, 345, 150, 295, 355, 140),
    # Sweeping across middle under canopy
    (310, 365, 135, 365, 365, 125),
    (400, 375, 120, 440, 365, 110),
    (480, 375, 105, 510, 360, 95),
    (550, 365, 90, 560, 345, 80),
    (580, 335, 65, 565, 320, 60),
    (540, 300, 45, 525, 295, 40)
]

# RIBBON C (Lower Broad Loop):
STATIONS_C = [
    # Canopy bottom-left
    (480, 365, 40, 470, 350, 45),
    (410, 400, 70, 430, 380, 75),
    (320, 440, 105, 360, 410, 110),
    (230, 470, 140, 290, 430, 145),
    (160, 440, 165, 225, 430, 170),
    (125, 360, 180, 185, 375, 180), # Outer left sweep
    (135, 290, 175, 200, 325, 175),
    (180, 260, 165, 240, 300, 160),
    (250, 275, 150, 285, 340, 145),
    (270, 380, 145, 305, 440, 150),
    (280, 490, 155, 325, 515, 160),
    (320, 590, 170, 360, 565, 175),
    (380, 645, 180, 410, 580, 185), # Bottom lowest apex
    (460, 630, 180, 475, 560, 185),
    (540, 575, 170, 530, 520, 170),
    (605, 510, 150, 565, 475, 145),
    (640, 450, 120, 585, 430, 115),
    (630, 385, 85, 575, 380, 80),
    (575, 350, 50, 545, 340, 45)
]

# Draw splines onto image
overlay = im.copy()
colors = {
    'A': ((0, 255, 255), (0, 200, 200)),
    'B': ((0, 120, 255), (0, 80, 200)),
    'C': ((255, 150, 0), (200, 100, 0))
}

for name, stations in [('A', STATIONS_A), ('B', STATIONS_B), ('C', STATIONS_C)]:
    st = np.array(stations)
    out_spline = eval_spline(st[:, 0:2], 300, closed=False)
    in_spline = eval_spline(st[:, 3:5], 300, closed=False)
    col_out, col_in = colors[name]
    cv2.polylines(overlay, [np.int32(out_spline)], False, col_out, 2)
    cv2.polylines(overlay, [np.int32(in_spline)], False, col_in, 2)
    # Draw ribs across stations
    for row in st[::2]:
        cv2.line(overlay, (int(row[0]), int(row[1])), (int(row[3]), int(row[4])), (255, 255, 255), 1)

cv2.imwrite('/Users/razeek/Projects/3D printing/spline_overlay.jpg', overlay)
print('Saved spline_overlay.jpg')
