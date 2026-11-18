"""Three creative directions for the Ø900 flat light, as backlit glow previews (simulated white PLA).
Run:  Blender -b --python scripts/concepts_v03.py   ->  renders/v03-A-diatom.png, -B-gyroid.png, -C-sunflower.png, v03-concepts.png
Each concept defines a thickness/opacity field; light out = exp(-mu * PLA path length)."""
import bpy, os, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
N, R, MU = 900, 450.0, 1.05
c = (np.arange(N) + 0.5) * (2*R/N) - R
X, Y = np.meshgrid(c, -c)
RR = np.hypot(X, Y); TH = np.arctan2(Y, X) % (2*np.pi)
inside = RR < R - 2
warm = np.array([1.0, 0.9, 0.76])

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t*t*(3 - 2*t)

def save_png(a, path):
    a = np.clip(a, 0, 1); h, w = a.shape[:2]
    rgba = np.concatenate([a[::-1], np.ones((h, w, 1))], -1).astype(np.float32)
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False)
    img.pixels.foreach_set(rgba.ravel()); img.filepath_raw = path; img.file_format = "PNG"; img.save()

def soften(a, n=2):
    for _ in range(n):
        a = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
    return a

def finish(path_len, name, rim_glow=True):
    light = np.exp(-MU * path_len)
    light = soften(light / light[inside].max())
    img = (light ** (1/2.2))[..., None] * warm
    bg = np.zeros((N, N, 3)) + np.array([0.02, 0.02, 0.025])
    if rim_glow:  # hidden halo on the ceiling around the disc
        halo = np.exp(-np.clip(RR - R, 0, None) / 45.0) * (RR >= R - 2)
        bg = bg + halo[..., None] * np.array([0.55, 0.42, 0.28])
    img = np.where(inside[..., None], img, bg)
    save_png(img, os.path.join(OUT, "renders", name)); return img

# ---------- A. Diatom (Arachnoidiscus): radial ribs that branch outward, rings of glowing pores ----------
r = RR / R
edges = [0.13]
while edges[-1] < 0.95: edges.append(edges[-1] * 1.17 + 0.012)
edges[-1] = 0.955
path = np.full((N, N), 3.2)                          # base skin, dim
for i in range(len(edges) - 1):
    r0, r1 = edges[i], edges[i+1]
    band = (r >= r0) & (r < r1)
    nrib = 18 * 2 ** min(3, int(math.log2(r0 / 0.13 + 1e-9) / 0.85 + 1e-9))
    u = (r - r0) / (r1 - r0)
    off = 0.5 * (i % 2)
    v = (TH * nrib / (2*np.pi) + off) % 1.0
    w_arc = r0 * 2*np.pi / nrib; m = max(1, round(w_arc / (r1 - r0) * 0.9))
    vs = (v * m) % 1.0
    d = np.hypot((u - 0.5) / 0.42, (vs - 0.5) / 0.40)          # pore shape
    pore = 0.55 + 2.4 * smooth(0.35, 1.0, d)                    # thin centre = bright gem
    sec_rib = np.minimum(vs, 1 - vs) * (r1 - r0) * R < 0.7      # thin secondary ribs
    pri_rib = np.minimum(v, 1 - v) * w_arc * R < 1.4            # main radial ribs
    ring = np.minimum(u, 1 - u) * (r1 - r0) * R < 1.1
    p = pore.copy(); p[sec_rib] = 6; p[pri_rib | ring] = 25
    path[band] = p[band]
# central rosette: 12 petals inside two rings
cen = r < edges[0]
petal = np.abs(np.cos(6 * TH)) ** 0.6
pr = 0.6 + 2.6 * smooth(0.0, 1.0, np.abs(r / edges[0] - 0.55 - 0.3 * petal) * 3)
pr[(np.abs(r - edges[0] * 0.35) * R < 1.0) | (r < 0.02)] = 25
path[cen] = pr[cen]
path[r > 0.955] = 25 * (1 - smooth(0.955, 0.99, r[r > 0.955])) + 2.0   # solid rim with fine glow edge
striae = (np.abs(((TH * 360 / (2*np.pi)) % 1.0) - 0.5) < 0.18) & (r > 0.962) & (r < 0.985)
path[striae] = 1.2
A = finish(path, "v03-A-diatom.png")

# ---------- B. Graded gyroid lattice: 3D labyrinth, light weaves through tilted walls ----------
Dz, nz = 36.0, 48
period = 22 + 26 * (RR / R) ** 1.3                    # tight centre, open rim
k = 2*np.pi / period
acc = np.zeros((N, N))
for zi in range(nz):
    z = (zi + 0.5) * Dz / nz
    g = np.sin(k*X)*np.cos(k*Y) + np.sin(k*Y)*np.cos(k*z) + np.sin(k*z)*np.cos(k*X)
    acc += (np.abs(g) < 0.32) * (Dz / nz)             # wall occupancy along the light path
B = finish(acc * 0.55 + 0.8, "v03-B-gyroid.png")

# ---------- C. Sunflower: golden-angle seed cells, glow graded across the 21 spiral arms -> vortex ----------
ns = 1800; ga = math.pi * (3 - math.sqrt(5))
ii = np.arange(ns); rs = (R - 14) * np.sqrt((ii + 0.6) / ns)
S = np.stack([rs*np.cos(ii*ga), rs*np.sin(ii*ga)], 1)
phase = (ii % 21) / 21.0                                   # position across the 21 spiral arms
spacing = (R - 14) * math.sqrt(math.pi / ns)              # mean seed spacing (mm)
pts = np.stack([X[inside], Y[inside]], 1)
d1 = np.empty(len(pts)); edge = np.empty(len(pts)); idx1 = np.empty(len(pts), int)
for k0 in range(0, len(pts), 8000):
    q = pts[k0:k0+8000]
    dd = ((q[:, None, :] - S[None]) ** 2).sum(-1)
    two = np.argpartition(dd, 1, 1)[:, :2]
    a_, b_ = dd[np.arange(len(q)), two[:, 0]], dd[np.arange(len(q)), two[:, 1]]
    first = np.where(a_ <= b_, two[:, 0], two[:, 1]); second = np.where(a_ <= b_, two[:, 1], two[:, 0])
    s1, s2 = S[first], S[second]
    nvec = s2 - s1
    edge[k0:k0+8000] = -((q - (s1 + s2)/2) * nvec).sum(1) / np.linalg.norm(nvec, axis=1)
    d1[k0:k0+8000] = np.sqrt(np.minimum(a_, b_)); idx1[k0:k0+8000] = first
seed_glow = 0.45 + 1.5 * phase[idx1] ** 1.5                # skin thins arm by arm -> swirling vortex
grow = 0.8 + 0.5 * (np.hypot(pts[:, 0], pts[:, 1]) / R)     # centre seeds a touch brighter
pl = seed_glow * grow + 2.2 * smooth(0.25, 0.85, d1 / (spacing * 0.55))
pl[edge < 0.7] = 25
path = np.full((N, N), 25.0); path[inside] = pl
C = finish(path, "v03-C-sunflower.png")

gap = np.zeros((N, 30, 3)) + 0.02
save_png(np.concatenate([A, gap, B, gap, C], 1), os.path.join(OUT, "renders", "v03-concepts.png"))
print("DONE")
