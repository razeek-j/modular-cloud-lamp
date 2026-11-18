"""V19 concept render: ribbons wound round a flat ring at a constant pitch.

Run: Blender -b -P scripts/build_v19_wound_concept.py -- [--draft]
"""

import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v19_wound_geometry as G  # noqa: E402

OUT = HERE.parent / "development-v19"
OUT.mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in ARGS
MM = 0.001
P = G.P

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = bpy.data.collections.new("V19 concept")
scene.collection.children.link(coll)


def mesh(name, verts, faces, mat, smooth=True, uv=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    if uv is not None:
        layer = me.uv_layers.new(name="UVMap")
        layer.data.foreach_set("uv", np.array([uv[me.loops[i].vertex_index] for i in range(len(me.loops))]).ravel())
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def principled(name, color, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def ribbon_mat():
    m = bpy.data.materials.new("Ribbon · translucent warm-white PETG")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.96, 0.92, 0.84, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (1.0, 0.92, 0.80, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.6
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 2 * math.pi * 24
    cosn = nt.nodes.new("ShaderNodeMath")
    cosn.operation = "COSINE"
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
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


M_RIB = ribbon_mat()
M_WHITE = principled("Disc and core · matte white", (0.88, 0.86, 0.82), 0.55)
M_CEIL = principled("Ceiling", (0.80, 0.74, 0.66), 0.9)
M_LED = bpy.data.materials.new("LED 3000 K")
M_LED.use_nodes = True
_nt = M_LED.node_tree
_nt.nodes.clear()
_o = _nt.nodes.new("ShaderNodeOutputMaterial")
_e = _nt.nodes.new("ShaderNodeEmission")
_bb = _nt.nodes.new("ShaderNodeBlackbody")
_bb.inputs["Temperature"].default_value = 3000
_nt.links.new(_bb.outputs[0], _e.inputs["Color"])
_e.inputs["Strength"].default_value = 420.0
_nt.links.new(_e.outputs[0], _o.inputs["Surface"])

# ribbons: closed strips with thickness (offset along the tube normal)
t2 = P["thickness"] / 2
for rb in G.RIBBONS:
    S, N = G.ribbon_grid(rb, P)
    n, m = S.shape[:2]
    outer, inner = (S + N * t2) * MM, (S - N * t2) * MM
    verts = np.concatenate([outer.reshape(-1, 3), inner.reshape(-1, 3)])
    faces = []
    vid = lambda side, i, j: side * n * m + (i % n) * m + j
    for i in range(n):
        for j in range(m - 1):
            faces.append((vid(0, i, j), vid(0, i, j + 1), vid(0, i + 1, j + 1), vid(0, i + 1, j)))
            faces.append((vid(1, i, j), vid(1, i + 1, j), vid(1, i + 1, j + 1), vid(1, i, j + 1)))
        for j, flip in ((0, False), (m - 1, True)):
            f = (vid(0, i, j), vid(0, i + 1, j), vid(1, i + 1, j), vid(1, i, j))
            faces.append(f[::-1] if flip else f)
    uv = np.zeros((2 * n * m, 2))
    acr = np.tile(np.linspace(0, 1, m), n)
    uv[:n * m, 0] = acr
    uv[n * m:, 0] = acr
    mesh(f"Ribbon {rb['name']}", verts, faces, M_RIB, uv=uv)

# Light source along the ring core (a diffused LED rod, Ø10 mm). It lights the
# ribbons from inside, as in the photo. In the render it is hidden from the camera;
# in the real lamp it sits inside the winding and needs screening at the gaps.
th = np.linspace(0, 2 * np.pi, 600, endpoint=False)
c, t, nrm = G.ring(th, P)
seg = 12
ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
cv = []
for k in range(len(th)):
    for a_ in ang:
        cv.append(((c[k, 0] + nrm[k, 0] * 5 * math.cos(a_)) * MM, (c[k, 1] + nrm[k, 1] * 5 * math.cos(a_)) * MM,
                   (P["z_c"] + 5 * math.sin(a_)) * MM))
cf = []
for k in range(len(th)):
    k2 = (k + 1) % len(th)
    for j in range(seg):
        j2 = (j + 1) % seg
        cf.append((k * seg + j, k * seg + j2, k2 * seg + j2, k2 * seg + j))
core = mesh("Core LED rod (light source)", cv, cf, M_LED, smooth=True)
core.visible_camera = False
core.visible_shadow = False
# disc and spokes
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=P["canopy_r"] * MM, depth=P["canopy_h"] * MM,
                                    location=(0, 0, -P["canopy_h"] / 2 * MM))
disc = bpy.context.active_object
disc.data.materials.append(M_WHITE)
for ang in (math.radians(90), math.radians(210), math.radians(330)):
    k = int(ang / (2 * math.pi) * len(th)) % len(th)
    end = Vector((c[k, 0] * MM, c[k, 1] * MM, -0.020))
    start = Vector((0, 0, -0.020))
    mid = (start + end) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    sp = bpy.context.active_object
    sp.scale = ((end - start).length, 0.008, 0.004)
    sp.rotation_euler = (0, 0, math.atan2(end.y, end.x))
    sp.data.materials.append(M_WHITE)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.002, depth=(-0.020 - P["z_c"] * MM), location=(end.x, end.y, (-0.020 + P["z_c"] * MM) / 2))
    bpy.context.active_object.data.materials.append(M_WHITE)
    bpy.context.active_object.visible_camera = False

bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0.0005))
bpy.context.active_object.data.materials.append(M_CEIL)
world = bpy.data.worlds.new("room")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.26, 0.21, 1)
M_WALL = principled("Walls · warm plaster", (0.78, 0.70, 0.60), 0.9)
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


el, d = math.radians(17), 2.77
cams = [("00-Reference-camera", camera("ref", (0, -d * math.cos(el), -0.16 - d * math.sin(el)), (0, 0, -0.10), 75), (1280, 712)),
        ("01-From-below", camera("below", (0, 0.0001, -2.6), (0, 0, -0.09), 50), (1200, 1200)),
        ("02-Room-view", camera("room", (0.4, -1.6, -0.75), (0, 0, -0.09), 32), (1600, 1000))]
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
scene.cycles.samples = 48 if DRAFT else 160
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 10
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.9
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "Ribbon-Lamp-V19-Wound-Concept.blend"))
for fname, cam, (rx, ry) in cams:
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    scene.render.filepath = str(OUT / f"{fname}.png")
    bpy.ops.render.render(write_still=True)
