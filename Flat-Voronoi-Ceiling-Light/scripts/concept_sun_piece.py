"""Sun Piece concept (v06): a piece of the sun's surface, after the user's chromosphere photo.
- Surface: short, broken, raised fibrils that bunch into rosettes and patches. Their direction comes from a field of
  7 main poles plus ~45 small ones (fixed low-discrepancy positions: irregular but reproducible).
- Outline: a rounded limb (a gentle curve, not a perfect circle) bristling with pointed spikes: a dense fringe of short
  spicules and a few tall flares. All spikes taper to a point; at most a slight bend, never a curl.
- Glow: limb-brightened like the photo, spikes bright because they are thin; amber palette.
Run:  Blender -b --python scripts/concept_sun_piece.py
Outputs: maps/sun-*.npy, renders/v06-sun-glow.png, renders/v06-sun-oblique.png, Sun-Piece-v06.blend"""
import bpy, bmesh, os, math
import numpy as np
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R, N, MU = 600.0, 1600, 1.05                       # R = canvas half-width (mm), 0.75 mm per pixel
px = 2*R/N
c = (np.arange(N) + 0.5) * px - R
X, Y = np.meshgrid(c, -c)
RR = np.hypot(X, Y); TH = np.arctan2(Y, X)
PHI = (1 + 5 ** 0.5) / 2

def smooth(e0, e1, x):
    t = np.clip((x - e0)/(e1 - e0), 0, 1); return t*t*(3 - 2*t)

def box_blur(a, r, passes=2):
    for _ in range(passes):
        for ax in (0, 1):
            cs = np.cumsum(np.pad(a, [(r+1, r) if i == ax else (0, 0) for i in range(2)], mode="edge"), axis=ax)
            a = (np.take(cs, range(2*r+1, cs.shape[ax]), axis=ax) - np.take(cs, range(0, cs.shape[ax]-2*r-1), axis=ax)) / (2*r+1)
    return a

def save_png(a, path):
    a = np.clip(a, 0, 1); h_, w_ = a.shape[:2]
    rgba = np.concatenate([a[::-1], np.ones((h_, w_, 1))], -1).astype(np.float32)
    img = bpy.data.images.new(os.path.basename(path), w_, h_, alpha=False)
    img.pixels.foreach_set(rgba.ravel()); img.filepath_raw = path; img.file_format = "PNG"; img.save(); return img

# ---------------- 1. body: rounded limb with a slow, gentle wobble ----------------
RB = 330.0
r_edge = RB * (1 + 0.035*np.sin(2*TH + 1.1) + 0.025*np.sin(3*TH + 2.3) + 0.012*np.sin(5*TH + 0.4))
body = RR < r_edge

# ---------------- 2. field: 7 main poles + 45 small ones (charges are multiples of 1/4 -> seamless lines) ----------------
M = 64                                               # denser strands, like the photo
poles = [(-120, 70, +1.50, +0.5), (165, -45, -1.25, -0.6), (70, 230, +0.75, -0.3),
         (-215, -175, -0.75, +0.6), (240, 170, -0.50, +0.3), (-55, -255, +0.50, -0.4), (-270, 120, -0.25, +0.2)]
a1, a2 = 0.7548776662466927, 0.5698402909980532      # R2 low-discrepancy sequence
n_small = 0; k = 1
while n_small < 45:
    u, v = (0.5 + k*a1) % 1, (0.5 + k*a2) % 1; k += 1
    x, y = (u*2 - 1) * 310, (v*2 - 1) * 310
    if math.hypot(x, y) > 305: continue
    if min(math.hypot(x - p[0], y - p[1]) for p in poles) < 45: continue
    q = (0.25 if (k*PHI) % 1 < 0.6 else 0.5) * (1 if k % 2 else -1)
    poles.append((x, y, q, 0.25*math.sin(k*1.7))); n_small += 1

psi = np.zeros((N, N)); chi = np.zeros((N, N)); Gx = np.zeros((N, N)); Gy = np.zeros((N, N))
core = np.zeros((N, N), bool)
for i, (x0, y0, q, s_tw) in enumerate(poles):
    dx, dy = X - x0, Y - y0; r2 = dx*dx + dy*dy + 1e-6; rr = np.sqrt(r2); th = np.arctan2(dy, dx)
    psi += q*th + s_tw*np.log(rr)
    chi += q*np.log(rr) - s_tw*th                  # runs ALONG the lines: used to break them into short fibrils
    Gx += (-q*dy + s_tw*dx) / r2; Gy += (q*dx + s_tw*dy) / r2
G = np.hypot(Gx, Gy) + 1e-9
logG = np.log(G)
le = smooth(np.percentile(logG[body], 5), np.percentile(logG[body], 99), logG)

# ---------------- 3. fibrils: field lines chopped into short staggered dashes ----------------
D = 2*np.pi / M
line_id = np.round(psi / D)
f = (psi / D) % 1.0
dist = np.minimum(f, 1 - f) * D / G                           # mm to the nearest line
Dc = 0.55                                                     # dash period in chi units
phase = (line_id * PHI) % 1.0                                 # each line's dashes start at a different place -> staggered
g = (chi / Dc + phase) % 1.0
duty = 0.45 + 0.3 * ((line_id * 0.381966) % 1.0)              # dash length varies line to line
along = np.minimum(g / duty, 1.0)                             # 0..1 along a dash, 1 = gap
dash = (g < duty) * np.sin(np.pi * np.clip(along, 0, 1)) ** 0.6   # pointed ends on every fibril
w = 1.3 + 0.6*le
fin = (1 - smooth(w/2 - 0.35, w/2 + 0.35, dist)) * dash
strand = fin * smooth(0.02, 0.2, le)                         # 0..1: where a fibril runs
height = strand * (1.2 + 2.3*le)                              # low ridges on the face: texture by day, no shadow lines at night
# mottling: darker patches where the field is weak (between rosettes), like the photo's dark cells
mottle = box_blur(le, 18, 2)

# ---------------- 4. pointed spikes: short spicule fringe + a few tall flares ----------------
spike_h = np.zeros((N, N)); spike_m = np.zeros((N, N))
def edge_at(ang):
    return RB * (1 + 0.035*math.sin(2*ang + 1.1) + 0.025*math.sin(3*ang + 2.3) + 0.012*math.sin(5*ang + 0.4))

def spike(ang, L, w0, tilt_deg, bend_deg):
    re = edge_at(ang) - 1.2*w0 - 2.0                               # root starts inside the body: no bulb
    x, y = re*math.cos(ang), re*math.sin(ang)
    d = ang + math.radians(tilt_deg); s_ = 0.0; step = 1.0
    while s_ < L:
        frac_ = s_ / L
        wv = w0 * (1 - frac_) ** 1.05                              # straight taper to a sharp point
        if wv < 0.35: break
        i0, j0 = int((x + R)/px), int((R - y)/px); rp = int(wv/px) + 2
        if not (rp < i0 < N - rp and rp < j0 < N - rp): break
        js, is_ = slice(j0 - rp, j0 + rp + 1), slice(i0 - rp, i0 + rp + 1)
        dd = np.hypot(X[js, is_] - x, Y[js, is_] - y)
        m = 1 - smooth(wv - 0.4, wv + 0.4, dd)
        spike_m[js, is_] = np.maximum(spike_m[js, is_], m)
        spike_h[js, is_] = np.maximum(spike_h[js, is_], m * (1.0 + 0.25*wv) * np.clip(1 - dd/(wv + 1e-6), 0, 1) ** 0.5)  # low spine
        d += math.radians(bend_deg) * step / L                    # gentle, constant bend: never a curl
        x += step*math.cos(d); y += step*math.sin(d); s_ += step

n_fringe = 420                                                     # fine glowing hair, not thorns
for k in range(n_fringe):
    ang = 2*math.pi * (k + 0.45*math.sin(k*2.39)) / n_fringe
    t = (k * PHI) % 1.0
    busy = 0.5 + 0.5*math.cos(ang - math.radians(25))               # longer, denser spicules toward the active side
    L = 5 + (10 + 30*busy) * t**2.0
    spike(ang, L, 1.1 + 1.4*t, 14*math.sin(k*0.77), 10*math.sin(k*1.31))
# tall flares: slim, uneven, clustered toward one side like an active region
for ang_d, L, w0, tilt, bend in [(8, 210, 10, -6, 12), (22, 120, 7, 9, -9), (41, 165, 8, -3, 14), (63, 85, 5, 6, -8),
                                 (128, 70, 5, 5, -10), (205, 110, 6, -8, -12), (322, 140, 7, 7, -13), (347, 95, 6, -5, 9)]:
    spike(math.radians(ang_d), L, w0, tilt, bend)

inside = body | (spike_m > 0.5)
rim = body & ~(box_blur(body.astype(float), 3) > 0.97)
height = np.where(body, height, 0)
height = np.maximum(height, spike_h)
height[rim] = np.maximum(height[rim], 5.0)
height[~inside] = 0
np.save(os.path.join(OUT, "maps", "sun-height.npy"), height.astype(np.float32))

# ---------------- 5. glow: limb brightening + thin bright spikes + hot sunspots ----------------
limb = 1 - box_blur(body.astype(float), 40, 3)                  # 0 deep inside .. ~0.5 at the edge
skin = 2.6 - 0.9*mottle - 1.4*strand - 2.2*np.clip(limb*2, 0, 1)**1.2   # strands carved thin on the back -> they glow
skin = np.where(body, skin, 0.7)                                 # spikes: thin, bright
skin = np.clip(skin, 0.6, 3.0)
np.save(os.path.join(OUT, "maps", "sun-skin.npy"), skin.astype(np.float32))
light = np.exp(-MU * skin)
for _ in range(2):
    light = (light + np.roll(light, 1, 0) + np.roll(light, -1, 0) + np.roll(light, 1, 1) + np.roll(light, -1, 1)) / 5
light = light / light[inside].max()
# amber palette: deep orange in the dim strands -> white-gold at the hottest
t_ = np.clip(light, 0, 1)[..., None]
dim = np.array([0.42, 0.12, 0.02]); mid = np.array([1.0, 0.52, 0.12]); hot = np.array([1.0, 0.95, 0.82])
col = np.where(t_ < 0.55, dim + (mid - dim) * (t_ / 0.55), mid + (hot - mid) * ((t_ - 0.55) / 0.45))
col = col ** (1/1.6)
halo = box_blur(inside.astype(float), 34, 3) * 1.5 * ~inside
bg = np.array([0.012, 0.014, 0.03]) + halo[..., None] * np.array([0.75, 0.35, 0.08])
glow = np.where(inside[..., None], col, bg)
save_png(glow, os.path.join(OUT, "renders", "v06-sun-glow.png"))
glow_tex = os.path.join(OUT, "maps", "sun-emission.png"); save_png(np.where(inside[..., None], col, 0), glow_tex)

# ---------------- 6. 3D relief (metres), fins/spines face the room ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; S = 0.001
n = N; idx = np.arange(n*n).reshape(n, n)
verts = np.stack([X*S, Y*S, -height*S], -1).reshape(-1, 3)
a, b, c2, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
keep = (inside[:-1, :-1] & inside[:-1, 1:] & inside[1:, 1:] & inside[1:, :-1]).ravel()
quads = np.stack([a, d, c2, b], -1).reshape(-1, 4)[keep]
used = np.unique(quads); remap = -np.ones(n*n, np.int64); remap[used] = np.arange(len(used))
quads = remap[quads]; verts = verts[used]
me = bpy.data.meshes.new("Sun-Piece")
me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
me.loops.add(len(quads)*4); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
me.polygons.add(len(quads)); me.polygons.foreach_set("loop_start", (np.arange(len(quads))*4).astype(np.int32))
me.update(calc_edges=True); me.validate()
uv = me.uv_layers.new(name="UV")
uvall = np.stack([(X/(2*R) + 0.5), (Y/(2*R) + 0.5)], -1).reshape(-1, 2)[used]
uv.data.foreach_set("uv", uvall[quads.ravel()].astype(np.float32).ravel())
me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
ob = bpy.data.objects.new("Sun-Piece", me); sc.collection.objects.link(ob)

m = bpy.data.materials.new("Sun-Glow"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputMaterial"); add = nt.nodes.new("ShaderNodeAddShader")
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.1
ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(glow_tex); ti.image.pack()
bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); bs.inputs["Base Color"].default_value = (0.35, 0.18, 0.08, 1)
bs.inputs["Roughness"].default_value = 0.55
nt.links.new(ti.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(bs.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], outn.inputs[0]); ob.data.materials.append(m)

bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0.04))
cm = bpy.data.materials.new("Ceiling"); cm.use_nodes = True
cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.78, 0.75, 1)
bpy.context.object.data.materials.append(cm)

cam = bpy.data.cameras.new("cam"); cam.lens = 30
co = bpy.data.objects.new("Render-Camera", cam); sc.collection.objects.link(co); sc.camera = co
eye = Vector((-0.7, -0.95, -1.0)); tgt = Vector((0.0, 0.0, -0.01))
co.location = eye; co.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
w_ = bpy.data.worlds.new("w"); w_.use_nodes = True; w_.node_tree.nodes["Background"].inputs[0].default_value = (0.003, 0.003, 0.006, 1)
sc.world = w_
sc.render.engine = "CYCLES"; sc.cycles.samples = 64; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1100
sc.view_settings.view_transform = "AgX"
sc.render.filepath = os.path.join(OUT, "renders", "v06-sun-oblique.png")
bpy.ops.render.render(write_still=True)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == "VIEW_3D":
                sp.shading.type = "MATERIAL"; r3 = sp.region_3d
                r3.view_location = tgt; r3.view_distance = (eye - tgt).length
                r3.view_rotation = (eye - tgt).to_track_quat("Z", "Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Sun-Piece-v06.blend"))
ys_, xs_ = np.nonzero(inside)
print("DONE poles", len(poles), "verts", len(verts), "extent mm %.0f x %.0f" % ((xs_.max()-xs_.min())*px, (ys_.max()-ys_.min())*px))
