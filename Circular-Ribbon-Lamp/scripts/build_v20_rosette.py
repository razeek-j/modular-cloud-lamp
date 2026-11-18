"""V20 spiral rosette: Blender scene, lights and renders.

Run: Blender -b -P scripts/build_v20_rosette.py -- [--draft] [--only NAME[,NAME]] [--palette] [--no-render]
"""

import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v20_geometry as G  # noqa: E402

OUT = HERE.parent / "development-v20"
OUT.mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in ARGS
PALETTE = "--palette" in ARGS
NORENDER = "--no-render" in ARGS
ONLY = None
if "--only" in ARGS:
    ONLY = ARGS[ARGS.index("--only") + 1].split(",")
MM = 0.001
P = G.P
LED_ON = "--led-off" not in ARGS

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = bpy.data.collections.new("V20 rosette")
scene.collection.children.link(coll)


# ------------------------------------------------------------------------------ materials
def principled(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def petal_mat(name, tint=(1.0, 0.92, 0.80), body=(0.96, 0.92, 0.84), tr_mix=0.62, lines=True):
    """Translucent washi-like PETG: diffuse + translucency, with faint printed layer lines along the ribbon."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (*body, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (*tint, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = tr_mix
    if lines:
        uv = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 2 * math.pi * 26
        cosn = nt.nodes.new("ShaderNodeMath")
        cosn.operation = "COSINE"
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.30
        bump.inputs["Distance"].default_value = 0.0004
        nt.links.new(uv.outputs["UV"], sep.inputs[0])
        nt.links.new(sep.outputs["X"], mul.inputs[0])
        nt.links.new(mul.outputs[0], cosn.inputs[0])
        nt.links.new(cosn.outputs[0], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], diff.inputs["Normal"])
        nt.links.new(bump.outputs["Normal"], tr.inputs["Normal"])
    nt.links.new(diff.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def emission(name, temp, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs["Temperature"].default_value = temp
    nt.links.new(bb.outputs[0], e.inputs["Color"])
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], o.inputs["Surface"])
    return m


M_PETAL = petal_mat("Petal · translucent warm-white PETG")
PAL = {"ivory": ((0.98, 0.93, 0.82), (0.96, 0.92, 0.82)),
       "terracotta": ((0.95, 0.55, 0.30), (0.80, 0.42, 0.24)),
       "sage": ((0.62, 0.74, 0.66), (0.50, 0.60, 0.54)),
       "sand": ((0.96, 0.78, 0.50), (0.88, 0.70, 0.45))}
CYCLE = {"B": ["ivory", "terracotta", "sage", "sand", "terracotta"],
         "M": ["sage", "ivory", "sand", "ivory", "sage"],
         "O": ["ivory", "terracotta", "sand", "ivory", "sage"]}
PAL_MATS = {k: petal_mat(f"Petal · {k}", tint=t, body=b, tr_mix=0.55) for k, (t, b) in PAL.items()}
M_STUD = petal_mat("Stud · solid translucent PETG (light pipe)", tint=(1.0, 0.94, 0.84), body=(0.97, 0.94, 0.88), tr_mix=0.93, lines=False)
M_METAL = principled("Hub · white powder coat", (0.86, 0.84, 0.80), 0.45)
M_DARK = principled("Hub cap · smoked graphite", (0.035, 0.03, 0.028), 0.35)
M_CEIL = principled("Ceiling · warm white", (0.80, 0.74, 0.66), 0.9)
M_WALL = principled("Walls · warm plaster", (0.78, 0.70, 0.60), 0.9)
M_LED = emission("LED strip 3000 K", 3000, 420.0)
M_DOT = emission("Centre dot · frosted lens", 2700, 55.0)


# ------------------------------------------------------------------------------ geometry helpers
def new_object(name, verts, faces, mat, uv=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    if uv is not None:
        layer = me.uv_layers.new(name="UVMap")
        loop_vi = np.zeros(len(me.loops), dtype=np.int32)
        me.loops.foreach_get("vertex_index", loop_vi)
        layer.data.foreach_set("uv", uv[loop_vi].ravel())
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def petal_object(p):
    """Render mesh of a petal: visible face, hidden face and rim as separate vertex sets (crisp rim)."""
    S, N = p["S"], p["N"]
    ns, nv = S.shape[:2]
    t = P["thickness"]
    vis = (S + N * (t / 2)) * MM
    hid = (S - N * (t / 2)) * MM
    verts, faces = [], []
    uvs = []
    uu, vv = np.meshgrid(np.linspace(0, 1, nv), np.linspace(0, 1, ns))
    base_uv = np.stack([uu, vv], axis=2).reshape(-1, 2)

    def grid(arr, flip):
        off = len(verts)
        verts.extend(arr.reshape(-1, 3))
        uvs.extend(base_uv)
        for i in range(ns - 1):
            for j in range(nv - 1):
                a, b, c, d = off + i * nv + j, off + (i + 1) * nv + j, off + (i + 1) * nv + j + 1, off + i * nv + j + 1
                faces.append((a, d, c, b) if flip else (a, b, c, d))

    flip = P["sigma"] > 0
    grid(vis, flip)
    grid(hid, not flip)
    # rim: perimeter loop, duplicated vertices
    loop = ([(0, j) for j in range(nv)] + [(i, nv - 1) for i in range(1, ns)]
            + [(ns - 1, j) for j in range(nv - 2, -1, -1)] + [(i, 0) for i in range(ns - 2, 0, -1)])
    off = len(verts)
    for (i, j) in loop:
        verts.append(vis[i, j])
        uvs.append((j / (nv - 1), i / (ns - 1)))
    for (i, j) in loop:
        verts.append(hid[i, j])
        uvs.append((j / (nv - 1), i / (ns - 1)))
    L = len(loop)
    for k in range(L):
        k2 = (k + 1) % L
        faces.append((off + k, off + L + k, off + L + k2, off + k2))
    if PALETTE:
        mat = PAL_MATS[CYCLE[p["whorl"]][p["index"] % 5]]
    else:
        mat = M_PETAL
    return new_object(f"Petal {p['id']}", verts, faces, mat, uv=np.array(uvs))


# ------------------------------------------------------------------------------ build
petals = G.build_all()
for p in petals:
    if ONLY and p["whorl"] not in ONLY and p["id"] not in ONLY:
        continue
    petal_object(p)


EXTRAS = OUT / "Lamp-frame-extras.npz"
extras = np.load(EXTRAS) if EXTRAS.exists() else None


def tri_object(name, tris, mat, angle=35.0, visible_camera=True):
    pts = np.asarray(tris).reshape(-1, 3) * MM
    uniq, inv = np.unique(np.round(pts, 6), axis=0, return_inverse=True)
    me = bpy.data.meshes.new(name)
    me.from_pydata(uniq.tolist(), [], inv.reshape(-1, 3).tolist())
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    ob.select_set(False)
    if not visible_camera:
        ob.visible_camera = False
        ob.visible_shadow = False
    return ob


# hub: ceiling plate (supplied metal canopy), printed body, smoked cap, frosted dot lens
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=P["plate_r"] * MM, depth=P["plate_t"] * MM,
                                    location=(0, 0, -P["plate_t"] / 2 * MM))
plate = bpy.context.active_object
plate.name = "Ceiling plate"
plate.data.materials.append(M_METAL)
if extras is not None:
    tri_object("Hub body", extras["hub_H1-hub-body"], M_METAL)
    tri_object("Hub cap (smoked)", extras["hub_H2-hub-cap"], M_DARK)
    tri_object("Centre dot (frosted lens)", extras["hub_H3-dot-lens"], M_DOT)
    if len(extras["stud"]):
        tri_object("Bond studs", extras["stud"], M_STUD, angle=60.0)
    if len(extras["chan"]):
        tri_object("LED channels (translucent PETG)", extras["chan"], M_PETAL, angle=60.0)

# LED strips: hub drum ring (radial light through the slot) and the five blade channels (8 mm COB, face up)
if LED_ON:
    n = 240
    verts, faces = [], []
    for k in range(n):
        a_ = 2 * math.pi * k / n
        for d in (9.0, 23.0):
            verts.append((76.0 * math.cos(a_) * MM, 76.0 * math.sin(a_) * MM, -d * MM))
    for k in range(n):
        k2 = (k + 1) % n
        faces.append((2 * k, 2 * k2, 2 * k2 + 1, 2 * k + 1))
    r1 = new_object("LED R1 hub ring", verts, faces, M_LED, smooth=False)
    r1.visible_camera = False
    r1.visible_shadow = False
    import v20_parts as PT  # noqa: E402
    for p in petals:
        if p["whorl"] != "B" or (ONLY and p["whorl"] not in ONLY and p["id"] not in ONLY):
            continue
        base, U, Sd, jc = PT.channel_frame(p)
        rows = [i for i in range(len(p["s"])) if 430.0 <= p["s"][i] <= 700.0]
        verts, faces = [], []
        for i in rows:
            c = base[i] + U[i] * (PT.CH_FLOOR + 0.5)
            verts.append(tuple((c - Sd[i] * 4.0) * MM))
            verts.append(tuple((c + Sd[i] * 4.0) * MM))
        for k in range(len(rows) - 1):
            faces.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
        st = new_object(f"LED strip {p['id']}", verts, faces, M_LED, smooth=False)
        st.visible_camera = False
        st.visible_shadow = False

# room
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0.0005))
bpy.context.active_object.name = "Ceiling"
bpy.context.active_object.data.materials.append(M_CEIL)
world = bpy.data.worlds.new("room")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.26, 0.21, 1)
for loc, rot in (((0, 2.6, -1.3), (math.pi / 2, 0, 0)), ((-2.8, 0, -1.3), (math.pi / 2, 0, math.pi / 2)),
                 ((2.8, 0, -1.3), (math.pi / 2, 0, math.pi / 2))):
    bpy.ops.mesh.primitive_plane_add(size=6, location=loc, rotation=rot)
    bpy.context.active_object.data.materials.append(M_WALL)


def camera(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    ob = bpy.data.objects.new(name, cd)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


el, dist = math.radians(17), 2.77
cams = [("00-Reference-camera", camera("ref", (0, -dist * math.cos(el), -0.16 - dist * math.sin(el)), (0, 0, -0.10), 75), (1280, 712)),
        ("01-From-below", camera("below", (0, 0.0001, -2.6), (0, 0, -0.09), 50), (1200, 1200)),
        ("02-Room-view", camera("room", (0.4, -1.6, -0.75), (0, 0, -0.09), 32), (1600, 1000)),
        ("03-Side", camera("side", (0, -3.2, -0.10), (0, 0, -0.07), 60), (1600, 700)),
        ("04-Oblique", camera("oblique", (1.2, -1.5, -0.62), (0, 0, -0.07), 38), (1500, 1000)),
        ("05-Hub-detail", camera("hub", (0.0, 0.0001, -0.80), (0, 0, -0.05), 45), (1200, 1200))]

scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = "GPU"
except Exception:
    pass
scene.cycles.samples = 40 if DRAFT else 192
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 14
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 12
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = float(ARGS[ARGS.index("--exposure") + 1]) if "--exposure" in ARGS else 0.9

suffix = "-palette" if PALETTE else ""
blend = OUT / f"Ribbon-Lamp-V20-Rosette{suffix}.blend"
if not DRAFT or "--save" in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
if not NORENDER:
    want = [a for a in ARGS if a.startswith("--cam=")]
    sel = {w[6:] for w in want}
    for fname, cam, (rx, ry) in cams:
        if sel and fname[:2] not in sel:
            continue
        scene.camera = cam
        scale = 0.5 if DRAFT else 1.0
        scene.render.resolution_x, scene.render.resolution_y = int(rx * scale), int(ry * scale)
        scene.render.filepath = str(OUT / (("draft-" if DRAFT else "") + f"{fname}{suffix}.png"))
        bpy.ops.render.render(write_still=True)
print("DONE")
