import cv2
import numpy as np

orig = cv2.imread('/Users/razeek/.gemini/antigravity/brain/4a61c6cc-fb23-4079-9099-70a8d3085dca/.user_uploaded/media_1794059533316_1ecf1034.jpg')
gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray, 172, 255, cv2.THRESH_BINARY)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# Measure distance transform inside clean
dist = cv2.distanceTransform(clean, cv2.DIST_L2, 5)

# For any point (x, y) on the ribbon centerline, local half-width is dist[y, x]!
# Local full width = 2 * dist[y, x]!
print("Distance transform ready")
