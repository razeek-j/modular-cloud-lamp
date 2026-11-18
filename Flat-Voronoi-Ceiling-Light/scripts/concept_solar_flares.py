"""Solar Flares concept (v05): v04's field-line fins, but no circle. The outline comes from the field:
a lumpy body that bulges around the sunspots, plus flare tails that peel off along field lines and taper to points.
Run:  Blender -b --python scripts/concept_solar_flares.py
Outputs: maps/flares-*.npy, renders/v05-flares-glow.png, renders/v05-flares-oblique.png, Solar-Flares-v05.blend
Fins face the room (printed fins-up, flat back on the bed); skin 0.6-2.8 mm white PLA, glow simulated."""
import bpy, bmesh, os, math
import numpy as np
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R, N, MU = 640.0, 1600, 1.05                            # R = half-width of the working canvas (mm)
px = 2*R/N
c = (np.arange(N) + 0.5) * px - R
X, Y = np.meshgrid(c, -c)
RR = np.hypot(X, Y); TH = np.degrees(np.arctan2(Y, X)) % 360
def smooth(e0, e1, x):
    t = np.clip((x - e0)/(e1 - e0), 0, 1); return t*t*(3 - 2*t)

# --- poles: deliberate, asymmetric. charges are multiples of 1/40 so the field lines close without seams ---
M = 40                                                # field lines per unit charge
# (x, y, charge q, twist s): twist makes the lines spiral into each sunspot like a whirlpool
poles = [(-120,  70, +1.50, +0.9), (165, -45, -1.25, -1.1), (70, 245, +0.75, -0.6),
         (-235, -195, -0.75, +1.2), (270, 200, -0.50, +0.5), (-55, -275, +0.50, -0.8), (-300, 140, -0.25, +0.35)]
psi = np.zeros((N, N)); phi = np.zeros((N, N)); Ex = np.zeros((N, N)); Ey = np.zeros((N, N))
core = np.zeros((N, N), bool); ring = np.zeros((N, N))
for (px_, py_, q, s_tw) in poles:
    dx, dy = X - px_, Y - py_; r2 = dx*dx + dy*dy + 1e-6; rr = np.sqrt(r2)
    psi += q * np.arctan2(dy, dx) + s_tw * np.log(rr); phi += q * np.log(rr)
    Ex += (-q * dy + s_tw * dx) / r2; Ey += (q * dx + s_tw * dy) / r2      # gradient of psi
    rc = 16 + 12*abs(q)                               # sunspot crater radius
    core |= rr < rc
    ring = np.maximum(ring, (1 - smooth(0.6, 2.2, np.abs(rr - rc))) * (6 + 6*abs(q)))   # low lip, not a button
E = np.hypot(Ex, Ey) + 1e-9

def box_blur(a, r, passes=2):
    for _ in range(passes):
        for ax in (0, 1):
            cs = np.cumsum(np.pad(a, [(r+1, r) if i == ax else (0, 0) for i in range(2)], mode="edge"), axis=ax)
            a = (np.take(cs, range(2*r+1, cs.shape[ax]), axis=ax) - np.take(cs, range(0, cs.shape[ax]-2*r-1), axis=ax)) / (2*r+1)
    return a

# --- outline 1: calm body = soft union of a core and small swells where sunspots sit near the edge ---
body = RR < 330
for (px_, py_, q, s_tw) in poles:
    for f_ in np.linspace(0.45, 1.0, 12):                     # capsule from the sunspot back toward the centre: never an island
        body |= np.hypot(X - px_*f_, Y - py_*f_) < 30 + 16*abs(q)
body = box_blur(body.astype(float), 30) > 0.5

# --- outline 2: flare tails, traced along the real field direction from the body edge ---
def field(x, y):
    gx = gy = 0.0
    for (px_, py_, q, s_tw) in poles:
        dx, dy = x - px_, y - py_; r2 = dx*dx + dy*dy + 1e-6
        gx += (-q*dy + s_tw*dx) / r2; gy += (q*dx + s_tw*dy) / r2
    t = np.array([-gy, gx]); return t / (np.linalg.norm(t) + 1e-12)       # along the line (perpendicular to grad psi)

def in_body(x, y):
    i, j = int((x + R) / px), int((R - y) / px)
    return 0 <= i < N and 0 <= j < N and body[j, i]

def edge_point(ang):
    a = math.radians(ang)
    for rr_ in np.arange(120, R - 5, px):
        if not in_body(rr_*math.cos(a), rr_*math.sin(a)): return rr_*math.cos(a), rr_*math.sin(a), a
    return None

# (centre angle deg, length mm, strands, spread deg, root half-width mm, curl deg at the tip) - deliberately uneven
flares = [(12, 380, 3, 9, 42, +130), (64, 200, 2, 6, 26, -80), (112, 150, 2, 4, 18, +60), (155, 420, 4, 12, 50, -170),
          (214, 180, 2, 5, 24, +95), (283, 330, 3, 8, 38, +140), (330, 140, 2, 4, 18, -70)]
tails_soft = np.zeros((N, N))
for fi, (ang, L, ns, spread, w0, curl) in enumerate(flares):
    for k in range(ns):
        u = (k - (ns - 1)/2) / max(1, (ns - 1)/2)                         # -1 .. 1 across the bundle
        Lk = L * (0.5 + 0.5*math.cos(u*1.25)**2) * (1.0 if k % 2 == 0 else 0.82)
        wk = w0 * (0.75 + 0.25*math.cos(u*1.2))
        ck = math.radians(curl) * (1.0 + 0.35*u)                          # neighbouring strands curl a little differently
        ep = edge_point(ang + u*spread)
        if ep is None: continue
        x, y, a = ep; x -= 6*math.cos(a); y -= 6*math.sin(a)             # start just inside -> fused root
        t0 = field(x, y); sgn = 1.0 if t0 @ np.array([math.cos(a), math.sin(a)]) >= 0 else -1.0
        s_ = 0.0; left = False; prev = None
        while s_ < Lk:
            t = field(x, y) * sgn
            if prev is not None and t @ prev < 0: t = -t                  # keep marching the same way
            xm, ym = x + t[0], y + t[1]; tm = field(xm, ym) * sgn
            if tm @ t < 0: tm = -tm
            prev = tm
            phi_c = ck * (s_ / Lk) ** 1.6                                   # curl grows toward the tip, like a flame wisp
            cs_, sn_ = math.cos(phi_c), math.sin(phi_c)
            tr = np.array([cs_*tm[0] - sn_*tm[1], sn_*tm[0] + cs_*tm[1]])
            x, y = x + 2.0*tr[0], y + 2.0*tr[1]; s_ += 2.0
            if abs(x) > R - 12 or abs(y) > R - 12: break
            ib = in_body(x, y)
            if not ib: left = True
            elif left and s_ > 0.6*Lk: break                                 # arched back into the body late: a prominence loop
            w = max(1.2, wk * max(0.0, 1 - s_/Lk) ** 1.15)
            i0, j0 = int((x + R)/px), int((R - y)/px); rpx = int(w/px) + 3
            js, is_ = slice(max(0, j0-rpx), j0+rpx+1), slice(max(0, i0-rpx), i0+rpx+1)
            d = np.hypot(X[js, is_] - x, Y[js, is_] - y)
            tails_soft[js, is_] = np.maximum(tails_soft[js, is_], 1 - smooth(w - 0.7, w + 0.7, d))
tails = tails_soft > 0.5
inside = box_blur((body | tails).astype(float), 5) > 0.5                 # rounded roots and tips
logE = np.log(E); le = smooth(np.percentile(logE[inside], 5), np.percentile(logE[inside], 99), logE)  # 0 weak .. 1 strong

# --- field-line fins: distance (mm) to the nearest line of psi = k * 2pi/M ---
D = 2*np.pi / M
f = (psi / D) % 1.0
dist = np.minimum(f, 1 - f) * D / E
major = (np.round(psi / D).astype(int) % 4) == 0          # every 4th line taller -> hierarchy
w = np.where(major, 2.0, 1.4)
fin = 1 - smooth(w/2 - 0.35, w/2 + 0.35, dist)
fade = np.maximum(smooth(0.0, 0.25, le), box_blur(tails.astype(float), 8)) * (1 - 0.5*core)  # fins stay alive along the tails
h_line = np.where(major, 9 + 17*le, 4 + 9*le)              # taller close to the poles
height = fin * h_line * fade
height = np.maximum(height, ring)                          # crater walls around each sunspot
height[core] = np.minimum(height[core], 0.0)
height[~inside] = 0
rim = inside & ~(box_blur(inside.astype(float), 4) > 0.97)  # thin lip that follows the new outline
height[rim] = np.maximum(height[rim], 7.0)

# --- diffuser skin: thinnest where the field is strongest -> light flares from the sunspots ---
skin = 2.8 - 2.2 * le ** 0.8
skin[core] = 0.6
np.save(os.path.join(OUT, "maps", "flares-height.npy"), height.astype(np.float32))
np.save(os.path.join(OUT, "maps", "flares-skin.npy"), skin.astype(np.float32))

def save_png(a, path):
    a = np.clip(a, 0, 1); h_, w_ = a.shape[:2]
    rgba = np.concatenate([a[::-1], np.ones((h_, w_, 1))], -1).astype(np.float32)
    img = bpy.data.images.new(os.path.basename(path), w_, h_, alpha=False)
    img.pixels.foreach_set(rgba.ravel()); img.filepath_raw = path; img.file_format = "PNG"; img.save(); return img

# --- flat glow preview (light passing straight through skin + fin) ---
light = np.exp(-MU * (skin + height))
for _ in range(2):
    light = (light + np.roll(light, 1, 0) + np.roll(light, -1, 0) + np.roll(light, 1, 1) + np.roll(light, -1, 1)) / 5
light = (light / light[inside].max()) ** (1/2.2)
warm = np.array([1.0, 0.86, 0.66]); hot = np.array([1.0, 0.97, 0.9])
col = light[..., None] * (warm + (hot - warm) * le[..., None])
halo = box_blur(inside.astype(float), 30, 3) * 1.6 * ~inside       # light spilling onto the ceiling around the outline
bg = np.array([0.018, 0.018, 0.022]) + halo[..., None] * np.array([0.55, 0.40, 0.25])
glow = np.where(inside[..., None], col, bg)
save_png(glow, os.path.join(OUT, "renders", "v05-flares-glow.png"))
glow_tex = os.path.join(OUT, "maps", "flares-emission.png"); save_png(np.where(inside[..., None], col, 0), glow_tex)

# --- 3D relief (metres) for an oblique render from below ---
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
S = 0.001
step = 1                                                   # full 0.75 mm mesh so thin fins stay clean
hs = height[::step, ::step]; xs = X[::step, ::step]; ys = Y[::step, ::step]; ins = inside[::step, ::step]
n = hs.shape[0]
me = bpy.data.meshes.new("Solar-Flares")
verts = np.stack([xs*S, ys*S, -hs*S], -1).reshape(-1, 3)   # fins hang down toward the room
idx = np.arange(n*n).reshape(n, n)
a, b, c2, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
keep = (ins[:-1, :-1] & ins[:-1, 1:] & ins[1:, 1:] & ins[1:, :-1]).ravel()
quads = np.stack([a, d, c2, b], -1).reshape(-1, 4)[keep]
me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
me.loops.add(len(quads)*4); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
me.polygons.add(len(quads)); me.polygons.foreach_set("loop_start", (np.arange(len(quads))*4).astype(np.int32))
me.update(calc_edges=True)
me.validate()
uv = me.uv_layers.new(name="UV")
uvs = np.stack([(xs/(2*R) + 0.5), (ys/(2*R) + 0.5)], -1).reshape(-1, 2)
uv.data.foreach_set("uv", uvs[quads.ravel()].astype(np.float32).ravel())
for p in me.polygons: p.use_smooth = True
ob = bpy.data.objects.new("Solar-Flares", me); sc.collection.objects.link(ob)
# remove the far-off unused vertices outside the disc
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bm.to_mesh(me); bm.free()

m = bpy.data.materials.new("Solar-Glow"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputMaterial"); mix = nt.nodes.new("ShaderNodeAddShader")
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 2.4
ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(glow_tex); ti.image.pack()
bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); bs.inputs["Base Color"].default_value = (0.92, 0.9, 0.86, 1)
bs.inputs["Roughness"].default_value = 0.6
for nm in ("Subsurface Weight",):
    if nm in bs.inputs: bs.inputs[nm].default_value = 0.4
nt.links.new(ti.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], mix.inputs[0]); nt.links.new(bs.outputs[0], mix.inputs[1])
nt.links.new(mix.outputs[0], outn.inputs[0]); ob.data.materials.append(m)

# ceiling + hidden halo ring
CEIL = 0.04
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, CEIL))
cm = bpy.data.materials.new("Ceiling"); cm.use_nodes = True
cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.78, 0.75, 1)
bpy.context.object.data.materials.append(cm)
# no ring: the glowing sheet also lights the ceiling behind it, so the halo follows the flare outline

cam = bpy.data.cameras.new("cam"); cam.lens = 32
co = bpy.data.objects.new("Render-Camera", cam); sc.collection.objects.link(co); sc.camera = co
eye = Vector((-0.75, -1.0, -1.05)); tgt = Vector((0.0, 0.0, -0.01))
co.location = eye; co.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
w_ = bpy.data.worlds.new("w"); w_.use_nodes = True; w_.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.004, 0.006, 1)
sc.world = w_
sc.render.engine = "CYCLES"; sc.cycles.samples = 64; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1100
sc.view_settings.view_transform = "AgX"
sc.render.filepath = os.path.join(OUT, "renders", "v05-flares-oblique.png")
bpy.ops.render.render(write_still=True)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == "VIEW_3D":
                sp.shading.type = "MATERIAL"; r3 = sp.region_3d
                r3.view_location = tgt; r3.view_distance = (eye - tgt).length
                r3.view_rotation = (eye - tgt).to_track_quat("Z", "Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Solar-Flares-v05.blend"))
ys_, xs_ = np.nonzero(inside)
print("DONE verts", len(me.vertices), "extent mm %.0f x %.0f" % ((xs_.max()-xs_.min())*px, (ys_.max()-ys_.min())*px))
