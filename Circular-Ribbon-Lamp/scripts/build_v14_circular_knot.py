"""Build V14: one continuous ribbon knot around a single centre canopy.

Run:
  Blender -b -P scripts/build_v14_circular_knot.py -- [--render] [--draft]

Geometry comes from v14_knot_geometry.py (millimetres). Blender units are
metres. Hidden LEDs sit in upward-facing channels on the top edge of the
upright lobe walls, so they wash the ceiling and the inside of the ribbon
without being visible from below.
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
import v14_knot_geometry as K  # noqa: E402

ROOT = HERE.parent
OUT = ROOT / "development-v14"
OUT.mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in ARGS
MM = 0.001
P = K.P

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"


def collection(name, hide_render=False):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    c.hide_render = hide_render
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


# ---------------------------------------------------------------- materials
def mat_ribbon():
    m = bpy.data.materials.new("Ribbon · translucent warm-white PETG")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.95, 0.90, 0.81, 1)
    trans = nt.nodes.new("ShaderNodeBsdfTranslucent")
    trans.inputs["Color"].default_value = (1.0, 0.90, 0.76, 1)
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = 0.45
    gloss.inputs["Color"].default_value = (1, 0.95, 0.88, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.52
    mix2 = nt.nodes.new("ShaderNodeMixShader")
    mix2.inputs["Fac"].default_value = 0.06
    nt.links.new(diff.outputs[0], mix.inputs[1])
    nt.links.new(trans.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], mix2.inputs[1])
    nt.links.new(gloss.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (0.93, 0.84, 0.68, 1)
    return m


def mat_principled(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*color, 1)
    return m


def mat_led(strength):
    m = bpy.data.materials.new("LED · 2700 K COB strip")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs["Temperature"].default_value = 2700
    nt.links.new(bb.outputs[0], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (1, 0.7, 0.4, 1)
    return m


M_RIBBON = mat_ribbon()
M_CHANNEL = mat_principled("LED channel · opaque white aluminium profile", (0.86, 0.85, 0.82), 0.5, 0.2)
M_CANOPY = mat_principled("Canopy · matte white", (0.88, 0.86, 0.82), 0.55)
M_CEILING = mat_principled("Ceiling · warm white plaster", (0.80, 0.73, 0.64), 0.9)
M_LED = mat_led(1600.0)

# ---------------------------------------------------------------- ribbon solid
g = K.ribbon_grid(P)
V = g["V"]                  # (n, m, 3) mid-surface with grooves
Nn = g["N"]                 # smooth sheet normal per station
n, m = V.shape[:2]
half = P["thickness"] / 2
outer = V + Nn[:, None, :] * half
inner = V - Nn[:, None, :] * half
verts = np.concatenate([outer.reshape(-1, 3), inner.reshape(-1, 3)]) * MM


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
ribbon = mesh_object("Ribbon · one continuous band", verts, faces, lamp_c)
ribbon.data.materials.append(M_RIBBON)

# ---------------------------------------------------------------- LED channels
ch_verts, ch_faces, led_verts, led_faces, channel_info = [], [], [], [], []
for idx in K.trough_segments(g, P):
    rings, led, L, led_len = K.trough_mesh(g, idx, P)
    base = len(ch_verts)
    k = rings.shape[1]
    ch_verts += list(rings.reshape(-1, 3) * MM)
    for i in range(len(rings) - 1):
        for j in range(k):
            a, b = base + i * k + j, base + i * k + (j + 1) % k
            ch_faces.append((a, b, b + k, a + k))
    # Solid end walls as four convex quads (floor, two walls, end plate); a concave
    # U-shaped n-gon triangulates incorrectly.
    last = base + (len(rings) - 1) * k
    for quad in ((0, 1, 4, 5), (1, 2, 3, 4), (0, 5, 6, 7), (5, 4, 3, 6)):
        ch_faces.append(tuple(base + j for j in quad)[::-1])
        ch_faces.append(tuple(last + j for j in quad))
    if len(led) > 1:
        lb = len(led_verts)
        led_verts += list(led.reshape(-1, 3) * MM)
        for i in range(len(led) - 1):
            for j in range(4):
                a, b = lb + i * 4 + j, lb + i * 4 + (j + 1) % 4
                led_faces.append((a, b, b + 4, a + 4))
        led_faces.append((lb + 3, lb + 2, lb + 1, lb))
        last = lb + (len(led) - 1) * 4
        led_faces.append((last, last + 1, last + 2, last + 3))
    mid = g["C"][idx[len(idx) // 2]]
    channel_info.append(dict(
        channel_length_mm=round(float(L)),
        led_length_mm=round(float(led_len)),
        plan_radius_mm=round(float(np.hypot(*mid[:2]))),
    ))
channels = mesh_object("LED channels · upward-facing, on lobe top edges", ch_verts, ch_faces, light_c, smooth=False)
channels.data.materials.append(M_CHANNEL)
leds = mesh_object("LED strips · 8 mm COB, 2700 K", led_verts, led_faces, light_c, smooth=False)
leds.data.materials.append(M_LED)
leds.visible_shadow = False

# ---------------------------------------------------------------- canopy
cr, chh = P["canopy_r"] * MM, P["canopy_h"] * MM
bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=cr, depth=chh, location=(0, 0, -chh / 2))
canopy = bpy.context.active_object
canopy.name = "Centre drum · Ø304 × 130 mm, only ceiling fixing"
for c in canopy.users_collection:
    c.objects.unlink(canopy)
lamp_c.objects.link(canopy)
bev = canopy.modifiers.new("Soft edge", "BEVEL")
bev.width = 0.008
bev.segments = 4
canopy.data.materials.append(M_CANOPY)
canopy.data.shade_smooth()

# Opal diffuser in the drum base: a soft downlight, so the centre glows like
# the ribbons instead of reading as a dark disc. The LED board sits inside.
M_OPAL = bpy.data.materials.new("Drum base · opal diffuser")
M_OPAL.use_nodes = True
_nt = M_OPAL.node_tree
_nt.nodes.clear()
_o = _nt.nodes.new("ShaderNodeOutputMaterial")
_e = _nt.nodes.new("ShaderNodeEmission")
_bb = _nt.nodes.new("ShaderNodeBlackbody")
_bb.inputs["Temperature"].default_value = 2700
_nt.links.new(_bb.outputs[0], _e.inputs["Color"])
_e.inputs["Strength"].default_value = 6.0
_d = _nt.nodes.new("ShaderNodeBsdfDiffuse")
_d.inputs["Color"].default_value = (0.95, 0.92, 0.86, 1)
_a = _nt.nodes.new("ShaderNodeAddShader")
_nt.links.new(_e.outputs[0], _a.inputs[0])
_nt.links.new(_d.outputs[0], _a.inputs[1])
_nt.links.new(_a.outputs[0], _o.inputs["Surface"])
bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=cr - 0.012, depth=0.002, location=(0, 0, -chh - 0.0006))
opal = bpy.context.active_object
opal.name = "Drum base · opal diffuser Ø280"
for c in opal.users_collection:
    c.objects.unlink(opal)
light_c.objects.link(opal)
opal.data.materials.append(M_OPAL)

# ---------------------------------------------------------------- room context
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0.0005))
ceiling = bpy.context.active_object
ceiling.name = "Ceiling (context)"
for c in ceiling.users_collection:
    c.objects.unlink(ceiling)
room_c.objects.link(ceiling)
ceiling.data.materials.append(M_CEILING)

world = bpy.data.worlds.new("Dim room")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.020, 0.015, 0.011, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# ---------------------------------------------------------------- checks
def bvh_of(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for ob in objs:
        tmp = bmesh.new()
        tmp.from_object(ob.evaluated_get(dg), dg)
        tmp.transform(ob.matrix_world)
        me = bpy.data.meshes.new("tmp")
        tmp.to_mesh(me)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        tmp.free()
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def checks():
    rep = {}
    rib_bvh = BVHTree.FromPolygons([tuple(v) for v in verts], faces, all_triangles=False)
    pairs = rib_bvh.overlap(rib_bvh)
    bad = 0
    for a, b in pairs:
        d = abs(face_station[a] - face_station[b])
        if min(d, n - d) > 3:
            bad += 1
    rep["ribbon_self_intersections"] = bad

    me = ribbon.data
    edges_count = {}
    for p in me.polygons:
        for e in p.edge_keys:
            edges_count[e] = edges_count.get(e, 0) + 1
    rep["ribbon_non_manifold_edges"] = sum(1 for c in edges_count.values() if c != 2)

    allv = np.array(verts) / MM
    chv = np.array(ch_verts) / MM
    rep["skin_top_below_ceiling_mm"] = round(float(-allv[:, 2].max()), 1)
    rep["channel_top_below_ceiling_mm"] = round(float(-chv[:, 2].max()), 1)
    rep["lowest_point_below_ceiling_mm"] = round(float(-allv[:, 2].min()), 1)
    rep["footprint_mm"] = [round(float(np.ptp(allv[:, 0]))), round(float(np.ptp(allv[:, 1])))]
    near = allv[allv[:, 2] > -P["canopy_h"]]
    rep["skin_min_radius_at_canopy_height_mm"] = round(float(np.hypot(near[:, 0], near[:, 1]).min()), 1) if len(near) else None
    nearc = chv[chv[:, 2] > -P["canopy_h"]]
    rep["channel_min_radius_at_canopy_height_mm"] = round(float(np.hypot(nearc[:, 0], nearc[:, 1]).min()), 1) if len(nearc) else None
    rep["canopy_radius_mm"] = P["canopy_r"]
    rep["canopy_depth_mm"] = P["canopy_h"]
    rep["min_gap_between_strand_centrelines_mm"] = round(float(g["gap"].min()), 1)
    slope = np.degrees(np.arcsin(np.abs(g["T"][:, 2])))
    rep["max_band_slope_deg"] = round(float(slope.max()), 1)
    rep["band_width_range_mm"] = [round(float(g["w"].min())), round(float(g["w"].max()))]
    seg = np.linalg.norm(np.roll(g["C"], -1, 0) - g["C"], axis=1)
    rep["band_length_mm"] = round(float(seg.sum()))
    area = float(np.sum(seg * g["w"])) / 1e6
    rep["skin_area_m2"] = round(area, 3)
    rep["skin_mass_kg_petg_1_27"] = round(area * P["thickness"] * 1.27, 2)

    # LED visibility from a room: eye positions 0.6-1.6 m below the ceiling,
    # out to 3.5 m away. A ray from the eye to an LED point must not hit any
    # lamp geometry first.
    occ = bvh_of([ribbon, channels, canopy])
    ledv = np.array(led_verts)
    samples = ledv[::23]
    eyes = []
    for drop in (0.6, 1.1, 1.6):
        for rad in (0.0, 0.4, 0.8, 1.2, 1.8, 2.5, 3.5):
            for ang in range(0, 360, 30 if rad else 360):
                a = math.radians(ang)
                eyes.append(Vector((rad * math.cos(a), rad * math.sin(a), -drop)))
    seen = 0
    total = 0
    seen_list = []
    for e in eyes:
        for s in samples:
            s = Vector(s) + Vector((0, 0, 0.0004))
            d = s - e
            dist = d.length
            hit = occ.ray_cast(e, d.normalized(), dist - 0.0006)
            total += 1
            if hit[0] is None:
                seen += 1
                if len(seen_list) < 12:
                    seen_list.append([round(x * 1000) for x in (*e, *s)])
    rep["led_direct_view_rays"] = dict(eye_positions=len(eyes), led_points=len(samples),
                                      rays=total, rays_reaching_led=seen,
                                      examples_eye_then_led_mm=seen_list)
    rep["led_channels"] = channel_info
    rep["led_total_length_mm"] = int(sum(c["led_length_mm"] for c in channel_info))
    return rep


report = checks()
(OUT / "Checks.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

# ---------------------------------------------------------------- cameras
def camera(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.01
    ob = bpy.data.objects.new(name, cd)
    cam_c.objects.link(ob)
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return ob


cams = [
    ("01-From-below", camera("Cam · from below", (0, 0.0001, -2.7), (0, 0, -0.12), 58), (1400, 1400)),
    ("02-Room-view", camera("Cam · room view", (0.55, -2.9, -1.15), (0, 0, -0.14), 50), (1700, 1000)),
    ("03-Oblique-below", camera("Cam · oblique", (1.25, -1.55, -1.7), (0, 0, -0.12), 45), (1400, 1200)),
    ("04-Centre-detail", camera("Cam · centre detail", (0.42, -0.70, -0.62), (0, 0.02, -0.12), 38), (1400, 1000)),
]
scene.camera = cams[0][1]

scene.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
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
scene.view_settings.exposure = 0.6
scene.render.image_settings.file_format = "PNG"

blend = OUT / ("Ribbon-Lamp-V14-Draft.blend" if DRAFT else "Ribbon-Lamp-V14-Circular-Knot.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))

if "--render" in ARGS:
    scale = 0.6 if DRAFT else 1.0
    for fname, cam, (rx, ry) in cams:
        scene.camera = cam
        scene.render.resolution_x = int(rx * scale)
        scene.render.resolution_y = int(ry * scale)
        scene.render.filepath = str(OUT / (fname + ("-draft" if DRAFT else "") + ".png"))
        bpy.ops.render.render(write_still=True)
    # Neutral shape view: LEDs off, soft even light, so the form can be judged
    M_LED.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.0
    _e.inputs["Strength"].default_value = 0.0
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.5, 0.45, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.camera = cams[2][1]
    scene.render.resolution_x = int(1400 * scale)
    scene.render.resolution_y = int(1200 * scale)
    scene.render.filepath = str(OUT / ("05-Shape-unlit" + ("-draft" if DRAFT else "") + ".png"))
    bpy.ops.render.render(write_still=True)
