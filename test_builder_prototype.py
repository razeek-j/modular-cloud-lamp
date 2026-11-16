import numpy as np
import cv2

# Test station points and check projection onto reference image
ref = cv2.imread('/Users/razeek/.gemini/antigravity/brain/4a61c6cc-fb23-4079-9099-70a8d3085dca/.user_uploaded/media_1794059533316_1ecf1034.jpg')
H, W = ref.shape[:2]
cx, cy = 507, 330
scale = 1.200 / 771.0  # m per pixel

def to_px(x, y):
    px = int(round(cx + x / scale))
    py = int(round(cy - y / scale))
    return px, py

print("Coordinate converter ready")
