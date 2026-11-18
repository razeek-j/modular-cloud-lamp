"""Voronoi Moon concept (v02): lithophane moon inside Voronoi cells + floating halo.
Run:  Blender -b --python scripts/build_moon_concept.py
Outputs maps/ (thickness map, rib mask) and renders/02..04.
Light transmission is simulated with Beer-Lambert (white PLA, mu ~ 1.05 /mm); it is a preview, not a photo."""
import bpy, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..")
R = 450.0            # disc radius mm
PX = 0.6             # mm per pixel of the maps
N = int(round(2*R/PX))
T_MIN, T_MAX = 0.6, 3.0   # diffuser skin thickness range (mm), relief on the hidden back side
RIB = 1.2                 # rib width mm
RIM = 3.0                 # outer rim wall mm
N_CELLS = 450
MU = 1.05                 # attenuation of white PLA, 1/mm
os.makedirs(os.path.join(OUT, "maps"), exist_ok=True); os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)

def save_png(arr, path, rgb=None):
    """arr: (N,N) or (N,N,3) floats 0..1, row 0 = top of the picture."""
    a = np.clip(arr, 0, 1)
    if a.ndim == 2: a = np.stack([a]*3, -1)
    h, w = a.shape[:2]
    rgba = np.concatenate([a[::-1], np.ones((h, w, 1))], -1).astype(np.float32)
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False, float_buffer=False)
    img.pixels.foreach_set(rgba.ravel()); img.filepath_raw = path; img.file_format = "PNG"; img.save()
    return img

# --- 1. moon face, orthographic near side, from NASA LROC colour map ---------------
src = bpy.data.images.load(os.path.join(OUT, "references", "lroc_color_poles_2k.tif"))
W, Hh = src.size
tex = np.empty(W*Hh*4, np.float32); src.pixels.foreach_get(tex)
tex = tex.reshape(Hh, W, 4)[..., :3].mean(-1)          # row 0 = south (bottom)
c = (np.arange(N) + 0.5) * PX - R                         # mm
X, Y = np.meshgrid(c, -c)                                  # row 0 = top (north)
r2 = (X**2 + Y**2) / R**2
inside = r2 < 1.0
xs, ys = X / R, Y / R
zs = np.sqrt(np.clip(1 - xs**2 - ys**2, 0, 1))
lat, lon = np.arcsin(np.clip(ys, -1, 1)), np.arctan2(xs, zs)
u = (lon / (2*np.pi) + 0.5) * (W - 1); v = (lat / np.pi + 0.5) * (Hh - 1)
u0, v0 = np.floor(u).astype(int), np.floor(v).astype(int)
fu, fv = u - u0, v - v0
u1, v1 = np.clip(u0+1, 0, W-1), np.clip(v0+1, 0, Hh-1)
moon = (tex[v0, u0]*(1-fu)*(1-fv) + tex[v0, u1]*fu*(1-fv) + tex[v1, u0]*(1-fu)*fv + tex[v1, u1]*fu*fv)
lo, hi = np.percentile(moon[inside], [0.5, 99.7])
b = np.clip((moon - lo) / (hi - lo), 0, 1) ** 0.85          # 0 = dark mare, 1 = bright highland
b[~inside] = 0
save_png(b, os.path.join(OUT, "maps", "moon-face.png"))

# lithophane thickness: thin = bright.  Solve exp(-mu t) so brightness maps linearly to light out.
tr_min, tr_max = math.exp(-MU*T_MAX), math.exp(-MU*T_MIN)
target = tr_min + (tr_max - tr_min) * b**1.3          # full thickness range, no clipping in the dark seas
thick = -np.log(np.clip(target, tr_min, tr_max)) / MU
thick[~inside] = 0

# --- 2. Voronoi ribs: golden-angle seeds, Lloyd relaxed on a coarse grid ---------------
rng = np.random.default_rng(7)                       # fixed seed: organic but reproducible
S = rng.uniform(-R, R, (N_CELLS*2, 2)); S = S[(S**2).sum(1) < (R-10)**2][:N_CELLS]
g = np.linspace(-R, R, 300); GX, GY = np.meshgrid(g, g); m = GX**2 + GY**2 < R**2
P = np.stack([GX[m], GY[m]], 1)
for _ in range(4):                                  # light relaxation keeps sizes varied
    lab = np.argmin(((P[:, None, :] - S[None]) ** 2).sum(-1), 1)
    cnt = np.bincount(lab, minlength=N_CELLS)
    for d in range(2):
        s = np.bincount(lab, P[:, d], N_CELLS)
        S[:, d] = np.where(cnt > 0, s / np.maximum(cnt, 1), S[:, d])
np.save(os.path.join(OUT, "maps", "sites.npy"), S)

# distance to nearest Voronoi edge per pixel, chunked
pts = np.stack([X[inside], Y[inside]], 1)
edge = np.empty(len(pts), np.float32)
for i in range(0, len(pts), 15000):
    q = pts[i:i+15000]
    d2 = ((q[:, None, :] - S[None]) ** 2).sum(-1)
    idx = np.argpartition(d2, 1, 1)[:, :2]
    a, bb = S[idx[:, 0]], S[idx[:, 1]]
    swap = d2[np.arange(len(q)), idx[:, 0]] > d2[np.arange(len(q)), idx[:, 1]]
    a2 = np.where(swap[:, None], bb, a); b2 = np.where(swap[:, None], a, bb)
    n = b2 - a2
    edge[i:i+15000] = ((q - (a2 + b2) / 2) * n).sum(1) / np.linalg.norm(n, axis=1) * -1
edge_map = np.full((N, N), 99.0, np.float32); edge_map[inside] = np.abs(edge)
rib = edge_map < RIB / 2
rim = np.sqrt(X**2 + Y**2) > R - RIM
wall = (rib | rim) & inside
np.save(os.path.join(OUT, "maps", "thickness.npy"), thick.astype(np.float32))
np.save(os.path.join(OUT, "maps", "walls.npy"), wall)

# --- 3. simulated views (seen from below) ------------------------------------------------
warm = np.array([1.0, 0.93, 0.82])
trans = np.exp(-MU * thick)
trans[wall] = 0.012                     # 25 mm white rib ~ opaque, faint glow only
on = trans / tr_max
# light spreads ~1 mm sideways inside the PLA skin: soften like a real lithophane
for _ in range(3):
    on = (on + np.roll(on, 1, 0) + np.roll(on, -1, 0) + np.roll(on, 1, 1) + np.roll(on, -1, 1)) / 5
on = on ** (1/2.2)                                   # linear light -> display
bg = np.array([0.035, 0.037, 0.045])
on_rgb = np.where(inside[..., None], on[..., None] * warm, bg)
save_png(on_rgb, os.path.join(OUT, "renders", "02-moon-on.png"))

off = np.full((N, N), 0.86)
off -= 0.10 * (1 - np.clip(edge_map / 1.6, 0, 1)) * inside          # faint shadow lines of ribs
off -= 0.02 * (thick - T_MIN) / (T_MAX - T_MIN) * inside              # barely-there ghost of the moon
light = np.array([0.93, 0.93, 0.92])
off_rgb = np.where(inside[..., None], off[..., None] * light, np.array([0.55, 0.55, 0.56]))
save_png(off_rgb, os.path.join(OUT, "renders", "03-moon-off.png"))
print("STATS cells", N_CELLS, "px", N, "thick", float(thick[inside].min()), float(thick[inside].max()),
      "wall_frac", float(wall[inside].mean()))
