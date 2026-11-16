"""Build V15: one broad ribbon band rolling round a small ceiling disc.

Run:
  Blender -b -P scripts/build_v15_broad_ribbon.py -- [--render] [--draft]

Geometry comes from v15_broad_geometry.py (millimetres); Blender units are
metres. The LED strip sits in a low channel on the band's hidden top face and
shines at the ceiling. The band itself screens it from the room, and any
stretch that a sight-line test can still see is left without LEDs.
"""

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v15_broad_geometry as K  # noqa: E402

ROOT = HERE.parent
OUT = ROOT / "development-v15"
OUT.mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in ARGS
MM = 0.001
P = K.P

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


lamp_c = collection("01 · Lamp")
light_c = collection("02 · Hidden LEDs")
room_c = collection("03 · Room context (render only)")
cam_c = collection("04 · Cameras")


def mesh_object(name, verts, faces, coll, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def relink(ob, coll):
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)


# ---------------------------------------------------------------- materials
def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree, m.node_tree.nodes.new("ShaderNodeOutputMaterial")


def mat_ribbon():
    m, nt, out = node_mat("Ribbon · translucent warm-white PETG")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.96, 0.93, 0.87, 1)
    trans = nt.nodes.new("ShaderNodeBsdfTranslucent")
    trans.inputs["Color"].default_value = (1.0, 0.94, 0.84, 1)
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = 0.5
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.55
    mix2 = nt.nodes.new("ShaderNodeMixShader")
    mix2.inputs["Fac"].default_value = 0.05
    nt.links.new(diff.outputs[0], mix.inputs[1])
    nt.links.new(trans.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], mix2.inputs[1])
    nt.links.new(gloss.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (0.95, 0.9, 0.8, 1)
    return m


def mat_principled(name, color, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*color, 1)
    return m


def mat_led(strength):
    m, nt, out = node_mat("LED · 3000 K COB strip")
    em = nt.nodes.new("ShaderNodeEmission")
    em.name = "Emission"
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs["Temperature"].default_value = 3000
    nt.links.new(bb.outputs[0], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


M_RIBBON = mat_ribbon()
M_CHANNEL = mat_principled("LED channel · opaque white", (0.88, 0.87, 0.84), 0.5)
M_WHITE = mat_principled("Ceiling disc and posts · matte white", (0.88, 0.86, 0.82), 0.55)
M_CEILING = mat_principled("Ceiling · warm white plaster", (0.80, 0.74, 0.66), 0.9)
M_WALL = mat_principled("Wall · warm plaster", (0.72, 0.65, 0.56), 0.9)
M_LED = mat_led(700.0)
# Clear acrylic posts pass light, so they leave no dark spot on the band.
M_CLEAR = bpy.data.materials.new("Posts · clear acrylic rod")
M_CLEAR.use_nodes = True
_b = M_CLEAR.node_tree.nodes["Principled BSDF"]
_b.inputs["Transmission Weight"].default_value = 1.0
_b.inputs["Roughness"].default_value = 0.05
_b.inputs["IOR"].default_value = 1.49

# ---------------------------------------------------------------- ribbon solid
g = K.ribbon_grid(P)
V, Nn = g["V"], g["N"]
n, m = V.shape[:2]
half = P["thickness"] / 2
verts = np.concatenate([(V + Nn[:, None, :] * half).reshape(-1, 3),
                        (V - Nn[:, None, :] * half).reshape(-1, 3)]) * MM


def vid(side, i, j):
    return side * n * m + (i % n) * m + j


faces, face_station = [], []
for i in range(n):
    for j in range(m - 1):
        faces.append((vid(0, i, j), vid(0, i + 1, j), vid(0, i + 1, j + 1), vid(0, i, j + 1)))
        faces.append((vid(1, i, j), vid(1, i, j + 1), vid(1, i + 1, j + 1), vid(1, i + 1, j)))
        face_station += [i, i]
    for j, flip in ((0, True), (m - 1, False)):
        f = (vid(0, i, j), vid(1, i, j), vid(1, i + 1, j), vid(0, i + 1, j))
        faces.append(f if flip else f[::-1])
        face_station.append(i)
ribbon = mesh_object("Ribbon · one continuous broad band", verts, faces, lamp_c)
ribbon.data.materials.append(M_RIBBON)

# ---------------------------------------------------------------- ceiling disc and posts
cr, chh = P["canopy_r"] * MM, P["canopy_h"] * MM
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=cr, depth=chh, location=(0, 0, -chh / 2))
canopy = bpy.context.active_object
canopy.name = "Ceiling disc · Ø240 × 32 mm, only ceiling fixing"
relink(canopy, lamp_c)
bev = canopy.modifiers.new("Soft edge", "BEVEL")
bev.width = 0.005
bev.segments = 4
canopy.data.materials.append(M_WHITE)
canopy.data.shade_smooth()

cth = np.cos(P["lobes"] * g["t"])
inner_idx = [i for i in range(n) if cth[i] < cth[i - 1] and cth[i] <= cth[(i + 1) % n]]
posts, post_info = [], []
for i in inner_idx:
    # seat on the hidden top face, a little inside the centreline so the post
    # lands well within the disc
    seat = g["C"][i] - g["D"][i] * 34.0 + g["up"][i] * half
    top = -P["canopy_h"] + 2.0
    length = top - seat[2] + 3.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=P["post_r"] * MM, depth=length * MM,
                                        location=(seat[0] * MM, seat[1] * MM, (seat[2] - 3.0 + length / 2) * MM))
    post = bpy.context.active_object
    post.name = f"Post {len(posts) + 1} · hidden above the band"
    relink(post, lamp_c)
    post.data.materials.append(M_CLEAR)
    post.data.shade_smooth()
    posts.append(post)
    post_info.append(dict(radius_from_centre_mm=round(float(np.hypot(seat[0], seat[1]))),
                          exposed_length_mm=round(float(-P["canopy_h"] - seat[2]), 1)))

# ---------------------------------------------------------------- LED channel, pruned by sight lines
def channel_mesh(runs):
    cv, cf, lv, lf, info = [], [], [], [], []
    for idx in runs:
        rings, leds = K.channel_rings(g, idx, P)
        base, k = len(cv), rings.shape[1]
        cv += list(rings.reshape(-1, 3) * MM)
        closed = len(idx) == n
        count = len(rings)
        for i in range(count if closed else count - 1):
            for j in range(k):
                a = base + i * k + j
                b = base + i * k + (j + 1) % k
                a2 = base + ((i + 1) % count) * k + j
                b2 = base + ((i + 1) % count) * k + (j + 1) % k
                cf.append((a, b, b2, a2))
        inset = 0 if closed else 8
        if not closed:
            last = base + (count - 1) * k
            for quad in ((0, 1, 4, 5), (1, 2, 3, 4), (0, 5, 6, 7), (5, 4, 3, 6)):
                cf.append(tuple(base + j for j in quad)[::-1])
                cf.append(tuple(last + j for j in quad))
        strip = leds[inset:count - inset] if inset else leds
        lb = len(lv)
        lv += list(strip.reshape(-1, 3) * MM)
        sc = len(strip)
        for i in range(sc if closed else sc - 1):
            for j in range(4):
                a = lb + i * 4 + j
                b = lb + i * 4 + (j + 1) % 4
                a2 = lb + ((i + 1) % sc) * 4 + j
                b2 = lb + ((i + 1) % sc) * 4 + (j + 1) % 4
                lf.append((a, b, b2, a2))
        if not closed:
            lf.append((lb + 3, lb + 2, lb + 1, lb))
            e = lb + (sc - 1) * 4
            lf.append((e, e + 1, e + 2, e + 3))
        seg = np.linalg.norm(np.diff(g["C"][idx], axis=0), axis=1)
        info.append(dict(channel_length_mm=round(float(seg.sum())),
                         led_length_mm=round(float(seg[inset:len(seg) - inset].sum()))))
    return cv, cf, lv, lf, info


def bvh_from(verts_list, faces_list, objs=()):
    bm = bmesh.new()
    for vs, fs in zip(verts_list, faces_list):
        me = bpy.data.meshes.new("tmp")
        me.from_pydata([tuple(v) for v in vs], [], [tuple(f) for f in fs])
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        tmp = bmesh.new()
        tmp.from_object(ob.evaluated_get(dg), dg)
        tmp.transform(ob.matrix_world)
        me = bpy.data.meshes.new("tmp")
        tmp.to_mesh(me)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        tmp.free()
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


EYES = []
for drop in (0.6, 0.85, 1.1, 1.35, 1.6):
    for rad in (0.0, 0.3, 0.6, 0.9, 1.2, 1.6, 2.0, 2.6, 3.5):
        for ang in range(0, 360, 20 if rad else 360):
            a = math.radians(ang)
            EYES.append(Vector((rad * math.cos(a), rad * math.sin(a), -drop)))

led_base, _, led_up, _ = K.led_frame(g, P)
LED_POINT = (led_base + led_up * 2.6) * MM          # just above the strip surface


def visible_stations(occluder, stations):
    seen = set()
    rays = 0
    for i in stations:
        s = Vector(LED_POINT[i])
        for e in EYES:
            d = s - e
            rays += 1
            if occluder.ray_cast(e, d.normalized(), d.length - 0.0004)[0] is None:
                seen.add(int(i))
                break
    return seen, rays


def runs_from_mask(mask, min_len):
    if mask.all():
        return [np.arange(n)]
    start = int(np.argmin(mask))
    runs, cur = [], []
    for k in range(n):
        i = (start + k) % n
        if mask[i]:
            cur.append(i)
        elif cur:
            runs.append(np.array(cur))
            cur = []
    if cur:
        runs.append(np.array(cur))
    return [r for r in runs if len(r) >= min_len]


# Pass 1: channel everywhere; find the stretches a room viewer could see.
all_idx = [np.arange(n)]
cv, cf, lv, lf, _ = channel_mesh(all_idx)
occ = bvh_from([verts, cv], [faces, cf], [canopy, *posts])
test_stations = range(0, n, 4)
seen, _ = visible_stations(occ, test_stations)
mask = np.ones(n, bool)
for i in seen:
    for d in range(-24, 25):                  # about 45 mm safety either side
        mask[(i + d) % n] = False
runs = runs_from_mask(mask, 70)
print('PASS1 visible', len(seen), 'of', len(test_stations), 'runs', [len(r) for r in runs])

# Pass 2: rebuild only the kept runs (with solid ends) and test again.
for _ in range(4):
    cv, cf, lv, lf, channel_info = channel_mesh(runs)
    occ = bvh_from([verts, cv], [faces, cf], [canopy, *posts])
    lit = np.concatenate([r[8:-8] for r in runs]) if runs else np.array([], int)
    seen, rays = visible_stations(occ, lit[::3])
    if not seen:
        break
    for i in seen:
        for d in range(-24, 25):
            mask[(i + d) % n] = False
    keep = np.zeros(n, bool)
    for r in runs:
        keep[r] = True
    runs = runs_from_mask(mask & keep, 70)

channels = mesh_object("LED channel · on the hidden top face", cv, cf, light_c, smooth=False)
channels.data.materials.append(M_RIBBON)      # printed as part of the band
leds = mesh_object("LED strips · 8 mm COB, 3000 K", lv, lf, light_c, smooth=False)
leds.data.materials.append(M_LED)

# ---------------------------------------------------------------- room context
bpy.ops.mesh.primitive_plane_add(size=7, location=(0, 0, 0.0005))
ceiling = bpy.context.active_object
ceiling.name = "Ceiling (context)"
relink(ceiling, room_c)
ceiling.data.materials.append(M_CEILING)
bpy.ops.mesh.primitive_plane_add(size=7, location=(0, 3.2, -1.4), rotation=(math.pi / 2, 0, 0))
wall = bpy.context.active_object
wall.name = "Back wall (context)"
relink(wall, room_c)
wall.data.materials.append(M_WALL)

world = bpy.data.worlds.new("Dim warm room")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.11, 0.095, 0.08, 1)

# ---------------------------------------------------------------- checks
def checks():
    rep = {}
    tree = BVHTree.FromPolygons([tuple(v) for v in verts], faces)
    bad = 0
    for a, b in tree.overlap(tree):
        d = abs(face_station[a] - face_station[b])
        if min(d, n - d) > 3:
            bad += 1
    rep["ribbon_self_intersections"] = bad
    count = {}
    for poly in ribbon.data.polygons:
        for e in poly.edge_keys:
            count[e] = count.get(e, 0) + 1
    rep["ribbon_non_manifold_edges"] = sum(1 for c in count.values() if c != 2)
    cl, _ = K.clearance(g, P, step=3, across_step=3, neighbour=150)
    rep["min_clearance_between_separate_parts_mm"] = round(cl, 1)
    allv = np.array(verts) / MM
    chv = np.array(cv) / MM
    rep["footprint_mm"] = [round(float(np.ptp(allv[:, 0]))), round(float(np.ptp(allv[:, 1])))]
    rep["skin_top_below_ceiling_mm"] = round(float(-allv[:, 2].max()), 1)
    rep["channel_top_below_ceiling_mm"] = round(float(-chv[:, 2].max()), 1)
    rep["lowest_point_below_ceiling_mm"] = round(float(-allv[:, 2].min()), 1)
    under = allv[np.hypot(allv[:, 0], allv[:, 1]) < P["canopy_r"] + 2]
    rep["gap_under_ceiling_disc_mm"] = round(float(-P["canopy_h"] - under[:, 2].max()), 1) if len(under) else None
    rep["band_length_mm"] = round(float(g["length"]))
    rep["band_width_range_mm"] = [round(float(g["w"].min())), round(float(g["w"].max()))]
    rep["bank_range_deg"] = [round(float(np.degrees(g["psi"].min()))), round(float(np.degrees(g["psi"].max())))]
    rep["max_band_slope_deg"] = round(float(np.degrees(np.arcsin(np.abs(g["T"][:, 2]).max()))), 1)
    seg = np.linalg.norm(np.roll(g["C"], -1, 0) - g["C"], axis=1)
    area = float(np.sum(seg * g["w"])) / 1e6
    rep["skin_area_m2"] = round(area, 3)
    rep["skin_mass_kg_petg_1_27"] = round(area * P["thickness"] * 1.27, 2)
    rep["posts"] = post_info
    rep["led_sight_line_test"] = dict(eye_positions=len(EYES), led_stations_tested=int(len(lit[::3])),
                                     rays_cast=int(rays), led_stations_visible=len(seen))
    rep["led_channels"] = channel_info
    rep["led_total_length_mm"] = int(sum(c["led_length_mm"] for c in channel_info))
    return rep


report = checks()
(OUT / "Checks.json").write_text(json.dumps(report, indent=2))
print("CHECKS " + json.dumps({k: v for k, v in report.items() if k != "led_channels"}))

# ---------------------------------------------------------------- cameras and render
def camera(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.01
    ob = bpy.data.objects.new(name, cd)
    cam_c.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


cams = [
    ("01-Room-view", camera("Cam · room view", (0.25, -2.35, -1.02), (0, 0, -0.12), 42), (1700, 1050)),
    ("02-From-below", camera("Cam · from below", (0, 0.0001, -2.7), (0, 0, -0.12), 52), (1400, 1400)),
    ("03-Oblique-below", camera("Cam · oblique", (1.35, -1.5, -1.45), (0, 0, -0.12), 42), (1500, 1200)),
    ("04-Close-fold", camera("Cam · close fold", (0.95, -0.95, -0.55), (0.25, -0.1, -0.12), 40), (1500, 1100)),
]
scene.camera = cams[0][1]
scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = "GPU"
except Exception:
    pass
scene.cycles.samples = 32 if DRAFT else 160
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 10
scene.cycles.transmission_bounces = 8
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.3
scene.render.image_settings.file_format = "PNG"

blend = OUT / ("Ribbon-Lamp-V15-Draft.blend" if DRAFT else "Ribbon-Lamp-V15-Broad-Ribbon.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))

if "--render" in ARGS:
    scale = 0.55 if DRAFT else 1.0
    suffix = "-draft" if DRAFT else ""
    for fname, cam, (rx, ry) in cams:
        scene.camera = cam
        scene.render.resolution_x = int(rx * scale)
        scene.render.resolution_y = int(ry * scale)
        scene.render.filepath = str(OUT / (fname + suffix + ".png"))
        bpy.ops.render.render(write_still=True)
    # Shape only: LEDs off, even light
    M_LED.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.0
    bg.inputs["Color"].default_value = (0.55, 0.5, 0.45, 1)
    scene.camera = cams[2][1]
    scene.render.resolution_x = int(1500 * scale)
    scene.render.resolution_y = int(1200 * scale)
    scene.render.filepath = str(OUT / ("05-Shape-unlit" + suffix + ".png"))
    bpy.ops.render.render(write_still=True)
