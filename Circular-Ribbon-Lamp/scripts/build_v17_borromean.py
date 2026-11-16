"""Build V17: three woven Moebius ribbons in the Borromean pattern.

Run:
  Blender -b -P scripts/build_v17_borromean.py -- [--render] [--draft]

Geometry: v17_geometry.py (millimetres). Blender units are metres.
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
import warnings  # noqa: E402
warnings.filterwarnings("ignore")
import v17_geometry as G  # noqa: E402

ROOT = HERE.parent
OUT = ROOT / "development-v17"
OUT.mkdir(exist_ok=True)
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in ARGS
MM = 0.001
P = G.P

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


lamp_c = collection("01 · Ribbons and mount")
light_c = collection("02 · Hidden LEDs")
room_c = collection("03 · Room context (render only)")
cam_c = collection("04 · Cameras")


def relink(ob, coll):
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)


def mesh_object(name, verts, faces, coll, smooth=True, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    if uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        loop_uv = np.array([uvs[me.loops[i].vertex_index] for i in range(len(me.loops))]).ravel()
        layer.data.foreach_set("uv", loop_uv)
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


# ---------------------------------------------------------------- materials
def mat_ribbon():
    m = bpy.data.materials.new("Ribbon · translucent warm-white PETG, printed layer texture")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.96, 0.92, 0.85, 1)
    trans = nt.nodes.new("ShaderNodeBsdfTranslucent")
    trans.inputs["Color"].default_value = (1.0, 0.93, 0.82, 1)
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = 0.45
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.55
    mix2 = nt.nodes.new("ShaderNodeMixShader")
    mix2.inputs["Fac"].default_value = 0.05
    # Printed layer lines along the ribbon (shader only; the model is smooth)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 2 * math.pi * 26
    cos = nt.nodes.new("ShaderNodeMath")
    cos.operation = "COSINE"
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.0004
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], mul.inputs[0])
    nt.links.new(mul.outputs[0], cos.inputs[0])
    nt.links.new(cos.outputs[0], bump.inputs["Height"])
    for sh in (diff, trans, gloss):
        nt.links.new(bump.outputs["Normal"], sh.inputs["Normal"])
    nt.links.new(diff.outputs[0], mix.inputs[1])
    nt.links.new(trans.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], mix2.inputs[1])
    nt.links.new(gloss.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (0.96, 0.92, 0.85, 1)
    return m


def mat_principled(name, color, rough=0.6, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    m.diffuse_color = (*color, 1)
    return m


def mat_led(strength):
    m = bpy.data.materials.new("LED · 3000 K COB, CRI 90+")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.name = "Emission"
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs["Temperature"].default_value = 3000
    nt.links.new(bb.outputs[0], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


M_RIBBON = mat_ribbon()
M_WHITE = mat_principled("Ceiling disc · matte white", (0.88, 0.86, 0.82), 0.55)
M_CLEAR = mat_principled("Seats and pads · clear PETG", (0.95, 0.95, 0.95), 0.08, 1.0)
M_CEILING = mat_principled("Ceiling · warm white plaster", (0.80, 0.74, 0.66), 0.9)
M_WALL = mat_principled("Wall · warm plaster", (0.74, 0.67, 0.58), 0.9)
M_LED = mat_led(1100.0)

# ---------------------------------------------------------------- ribbons
rings, crossings = G.build(P)
sec = G.section(P)
K = len(sec)
H = K // 2                     # half-turn of the section = Moebius flip
ring_objs, ring_data = {}, {}
for name, r in rings.items():
    R = G.solid_rings(r, P)                      # (n, K, 3) mm
    n = len(R)
    verts = (R.reshape(-1, 3) * MM)
    faces, station = [], []
    flips = 0
    for i in range(n):
        i2 = (i + 1) % n
        shift = 0
        if np.dot(r["D"][i], r["D"][i2]) < 0:
            shift = H
            flips += 1
        for j in range(K):
            a = i * K + j
            b = i * K + (j + 1) % K
            a2 = i2 * K + (j + shift) % K
            b2 = i2 * K + (j + 1 + shift) % K
            faces.append((a, b, b2, a2))
            station.append(i)
    # UV: x across the ribbon (for the layer-line shader), y along it
    uvs = np.zeros((n * K, 2))
    across = []
    for kind, a, b in sec:
        across.append((a + 1) / 2 if kind == "f" else (1.0 if kind == "b+" else 0.0))
    across = np.array(across)
    for i in range(n):
        uvs[i * K:(i + 1) * K, 0] = across
        uvs[i * K:(i + 1) * K, 1] = r["s"][i] / 1000.0
    ob = mesh_object(f"Ribbon {name} · Moebius band", verts, faces, lamp_c, uvs=uvs)
    ob.data.materials.append(M_RIBBON)
    ring_objs[name] = ob
    ring_data[name] = dict(verts=verts, faces=faces, station=station, n=n, flips=flips)

# ---------------------------------------------------------------- ceiling disc, seats and crossing pads
cr, chh = P["canopy_r"] * MM, P["canopy_h"] * MM
bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=cr, depth=chh, location=(0, 0, -chh / 2))
canopy = bpy.context.active_object
canopy.name = f"Ceiling disc · Ø{2 * P['canopy_r']:.0f} × {P['canopy_h']:.0f} mm, the only ceiling fixing"
relink(canopy, lamp_c)
bev = canopy.modifiers.new("Soft edge", "BEVEL")
bev.width = 0.005
bev.segments = 4
canopy.data.materials.append(M_WHITE)
canopy.data.shade_smooth()


def up_face_point(r, i, v=0.0):
    """Point on the ceiling-facing skin at station i, across position v (-0.5..0.5)."""
    N = r["N"][i] * np.sign(r["N"][i][2])
    return r["C"][i] + r["D"][i] * (v * (r["w"][i] - 2 * P["bead_r"])) + N * (P["thickness"] / 2)


def cylinder(name, p0, p1, radius, mat, coll):
    p0, p1 = Vector(p0 * MM), Vector(p1 * MM)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius * MM, depth=d.length,
                                        location=(p0 + p1) / 2)
    ob = bpy.context.active_object
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.name = name
    relink(ob, coll)
    ob.data.materials.append(mat)
    ob.data.shade_smooth()
    return ob


seats, seat_info = [], []
for name, r in rings.items():
    # seat: the station whose ceiling-facing skin is nearest the disc centre
    M = G.mid_surface(r, 21)
    rr = np.hypot(M[..., 0], M[..., 1])
    i, j = np.unravel_index(np.argmin(rr), rr.shape)
    v = np.linspace(-0.5, 0.5, 21)[j]
    v = float(np.clip(v, -0.3, 0.3))
    base = up_face_point(r, i, v)
    top = np.array([base[0], base[1], -P["canopy_h"] + 1.0])
    seats.append(cylinder(f"Seat {name} · hidden standoff to the disc", base - np.array([0, 0, 1.0]), top, 9.0,
                          M_CLEAR, lamp_c))
    seat_info.append(dict(ring=name, station=int(i), across=v, radius_from_centre_mm=round(float(np.hypot(*base[:2]))),
                          length_mm=round(float(top[2] - base[2]), 1)))

# Hidden support spider: slim ceiling-white arms in the gap between the ribbon
# tops and the ceiling, each carrying one ribbon at a high, ceiling-facing spot
# through a short hanger. Seats under the disc plus two hangers per ring give
# every ring three supports.
M_SPIDER = mat_principled("Spider · ceiling-white powder-coated aluminium", (0.80, 0.74, 0.66), 0.7)
ARM_W, ARM_T, ARM_Z = 12.0, 5.0, -6.0          # mm; arm top 6 mm below the ceiling
hangers, hanger_info, arms = [], [], []
for name, r in rings.items():
    n = len(r["C"])
    U = r["N"] * np.sign(r["N"][:, 2:3])
    top = r["C"][:, 2] + 0.5 * r["w"] * np.abs(r["D"][:, 2])
    rr = np.hypot(r["C"][:, 0], r["C"][:, 1])
    ok = (U[:, 2] > 0.9) & (rr > 230) & (rr < 470)
    score = np.where(ok, r["C"][:, 2] + 0.02 * rr, -np.inf)    # high and far out
    picks = []
    for _ in range(2):
        i = int(np.argmax(score))
        if not np.isfinite(score[i]):
            break
        picks.append(i)
        q = np.arange(n)
        dd = np.minimum(np.abs(q - i), n - np.abs(q - i)) * (r["L"] / n)
        score[dd < 450] = -np.inf
    for i in picks:
        base = up_face_point(r, i, 0.0)
        z_arm = ARM_Z - ARM_T
        hangers.append(cylinder(f"Hanger {name} · 6 mm rod", base - np.array([0, 0, 0.5]),
                                np.array([base[0], base[1], z_arm + 0.5]), 3.0, M_SPIDER, lamp_c))
        # arm from the disc rim to above the hanger
        ang = math.atan2(base[1], base[0])
        r0 = P["canopy_r"] - 25.0
        L_arm = float(np.hypot(base[0], base[1])) + 8.0 - r0
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        arm = bpy.context.active_object
        arm.scale = (L_arm * MM, ARM_W * MM, ARM_T * MM)
        cx = (r0 + L_arm / 2)
        arm.location = (cx * math.cos(ang) * MM, cx * math.sin(ang) * MM, (ARM_Z - ARM_T / 2) * MM)
        arm.rotation_euler = (0, 0, ang)
        arm.name = f"Arm {name} · {ARM_W:.0f} × {ARM_T:.0f} mm aluminium flat bar"
        relink(arm, lamp_c)
        arm.data.materials.append(M_SPIDER)
        arms.append(arm)
        hanger_info.append(dict(ring=name, station=int(i), radius_from_centre_mm=round(float(np.hypot(*base[:2]))),
                                hanger_length_mm=round(float(z_arm - base[2]), 1), arm_length_mm=round(L_arm)))

# ---------------------------------------------------------------- LED channel on the hidden top face, inner edge
A_HALF, A_DEPTH, WALL, FLOOR = 6.0, 8.0, 1.2, 1.2
PROF = np.array([(-A_HALF, 0), (A_HALF, 0), (A_HALF, A_DEPTH), (A_HALF - WALL, A_DEPTH), (A_HALF - WALL, FLOOR),
                 (-A_HALF + WALL, FLOOR), (-A_HALF + WALL, A_DEPTH), (-A_HALF, A_DEPTH)])
LEDQ = np.array([(-4, FLOOR + 0.05), (4, FLOOR + 0.05), (4, FLOOR + 1.0), (-4, FLOOR + 1.0)])


def led_frame(r):
    n = len(r["C"])
    side = np.column_stack((r["T"][:, 1], -r["T"][:, 0], np.zeros(n)))
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    side *= np.sign(np.einsum("ij,ij->i", side[:, :2], r["C"][:, :2] - r["centre"]))[:, None]
    inner = -np.sign(np.einsum("ij,ij->i", r["D"], side))[:, None] * r["D"]      # towards the ring centre
    U = r["N"] * np.sign(r["N"][:, 2:3])
    base = r["C"] + inner * (r["w"] / 2 - 14.0)[:, None] + U * (P["thickness"] / 2)
    S = np.cross(r["T"], U)
    return base, U, S


def channel_mesh(runs):
    cv, cf, lv, lf, info = [], [], [], [], []
    for name, idx in runs:
        r = rings[name]
        base, U, S = led_frame(r)
        rings_ = base[idx][:, None, :] + PROF[None, :, 0:1] * S[idx][:, None, :] + PROF[None, :, 1:2] * U[idx][:, None, :]
        leds = base[idx][:, None, :] + LEDQ[None, :, 0:1] * S[idx][:, None, :] + LEDQ[None, :, 1:2] * U[idx][:, None, :]
        b0, k = len(cv), rings_.shape[1]
        cv += list(rings_.reshape(-1, 3) * MM)
        cnt = len(rings_)
        for i in range(cnt - 1):
            for j in range(k):
                a, b = b0 + i * k + j, b0 + i * k + (j + 1) % k
                cf.append((a, b, b + k, a + k))
        last = b0 + (cnt - 1) * k
        for quad in ((0, 1, 4, 5), (1, 2, 3, 4), (0, 5, 6, 7), (5, 4, 3, 6)):
            cf.append(tuple(b0 + j for j in quad)[::-1])
            cf.append(tuple(last + j for j in quad))
        strip = leds[6:cnt - 6]
        l0 = len(lv)
        lv += list(strip.reshape(-1, 3) * MM)
        sc = len(strip)
        for i in range(sc - 1):
            for j in range(4):
                a, b = l0 + i * 4 + j, l0 + i * 4 + (j + 1) % 4
                lf.append((a, b, b + 4, a + 4))
        lf.append((l0 + 3, l0 + 2, l0 + 1, l0))
        e = l0 + (sc - 1) * 4
        lf.append((e, e + 1, e + 2, e + 3))
        seg = np.linalg.norm(np.diff(r["C"][idx], axis=0), axis=1)
        info.append(dict(ring=name, channel_length_mm=round(float(seg.sum())),
                         led_length_mm=round(float(seg[6:len(seg) - 6].sum()))))
    return cv, cf, lv, lf, info


def bvh_of(vert_lists, face_lists, objs=()):
    bm = bmesh.new()
    for vs, fs in zip(vert_lists, face_lists):
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
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


EYES = []
for drop in (0.6, 0.85, 1.1, 1.35, 1.6):
    for rad in (0.0, 0.3, 0.6, 0.9, 1.2, 1.6, 2.0, 2.6, 3.5):
        for ang in range(0, 360, 20 if rad else 360):
            a = math.radians(ang)
            EYES.append(Vector((rad * math.cos(a), rad * math.sin(a), -drop)))


def runs_from_mask(name, mask, min_len=40):
    n = len(mask)
    if mask.all():
        return [(name, np.arange(n))]
    start = int(np.argmin(mask))
    runs, cur = [], []
    for k in range(n):
        i = (start + k) % n
        if mask[i]:
            cur.append(i)
        elif cur:
            runs.append((name, np.array(cur)))
            cur = []
    if cur:
        runs.append((name, np.array(cur)))
    return [x for x in runs if len(x[1]) >= min_len]


masks = {}
for name, r in rings.items():
    U = r["N"] * np.sign(r["N"][:, 2:3])
    masks[name] = U[:, 2] > 0.85                 # only where the top face really faces the ceiling
ring_bvh_inputs = ([d["verts"] for d in ring_data.values()], [d["faces"] for d in ring_data.values()])
for rnd in range(5):
    runs = [x for name in rings for x in runs_from_mask(name, masks[name])]
    cv, cf, lv, lf, channel_info = channel_mesh(runs)
    occ = bvh_of(ring_bvh_inputs[0] + [cv], ring_bvh_inputs[1] + [cf], [canopy, *seats, *hangers, *arms])
    seen = 0
    tested = 0
    rays = 0
    for name, idx in runs:
        base, U, _ = led_frame(rings[name])
        pts = (base + U * 2.6) * MM
        for i in idx[6:-6:3]:
            tested += 1
            s = Vector(pts[i])
            for e in EYES:
                d = s - e
                rays += 1
                if occ.ray_cast(e, d.normalized(), d.length - 0.0004)[0] is None:
                    seen += 1
                    for q in range(-20, 21):
                        masks[name][(i + q) % len(masks[name])] = False
                    break
    print(f"LED round {rnd}: tested {tested}, visible {seen}")
    if seen == 0:
        break
channels = mesh_object("LED channels · on the ceiling-facing skin", cv, cf, light_c, smooth=False)
channels.data.materials.append(M_RIBBON)
leds = mesh_object("LED strips · 8 mm COB 3000 K", lv, lf, light_c, smooth=False)
leds.data.materials.append(M_LED)

# ---------------------------------------------------------------- room context
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0.0005))
ceiling = bpy.context.active_object
ceiling.name = "Ceiling (context)"
relink(ceiling, room_c)
ceiling.data.materials.append(M_CEILING)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 3.4, -1.4), rotation=(math.pi / 2, 0, 0))
wall = bpy.context.active_object
wall.name = "Back wall (context)"
relink(wall, room_c)
wall.data.materials.append(M_WALL)
world = bpy.data.worlds.new("Dim warm room")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.10, 0.085, 0.07, 1)


# ---------------------------------------------------------------- checks
def checks():
    rep = {}
    # self and pairwise intersections of the ribbon solids
    bad_self, bad_pair = 0, 0
    trees = {}
    for name, d in ring_data.items():
        t = BVHTree.FromPolygons([tuple(v) for v in d["verts"]], d["faces"])
        trees[name] = t
        n = d["n"]
        for a, b in t.overlap(t):
            q = abs(d["station"][a] - d["station"][b])
            if min(q, n - q) > 3:
                bad_self += 1
    names = list(trees)
    for i in range(3):
        for j in range(i + 1, 3):
            bad_pair += len(trees[names[i]].overlap(trees[names[j]]))
    rep["ribbon_self_intersections"] = bad_self
    rep["ribbon_pairwise_intersections"] = bad_pair
    nm = 0
    for ob in ring_objs.values():
        cnt = {}
        for poly in ob.data.polygons:
            for e in poly.edge_keys:
                cnt[e] = cnt.get(e, 0) + 1
        nm += sum(1 for c in cnt.values() if c != 2)
    rep["ribbon_non_manifold_edges"] = nm
    rep["moebius_flips_per_ring"] = {k: d["flips"] for k, d in ring_data.items()}
    gap, who, where = G.clearance(rings, P, step=2)
    rep["min_gap_between_ribbons_mm"] = round(gap, 1)
    allv = np.vstack([d["verts"] for d in ring_data.values()]) / MM
    rep["footprint_mm"] = [round(float(np.ptp(allv[:, 0]))), round(float(np.ptp(allv[:, 1])))]
    rep["top_below_ceiling_mm"] = round(float(-allv[:, 2].max()), 1)
    rep["depth_below_ceiling_mm"] = round(float(-allv[:, 2].min()), 1)
    rep["seats"] = seat_info
    rep["hangers"] = hanger_info
    # how much of the spider a room viewer can see (it is ceiling-coloured)
    occ2 = bvh_of(ring_bvh_inputs[0], ring_bvh_inputs[1], [canopy])
    vis = tot = 0
    for arm in arms:
        mw = arm.matrix_world
        for t in np.linspace(-0.45, 0.45, 10):
            pnt = mw @ Vector((t, 0, -0.55))
            for e in EYES[::5]:
                d = pnt - e
                tot += 1
                if occ2.ray_cast(e, d.normalized(), d.length - 0.0005)[0] is None:
                    vis += 1
    rep["spider_visible_fraction_of_sight_lines"] = round(vis / max(tot, 1), 3)
    # mass and balance (skin area x thickness x PETG density), per ring
    tot_m, mom = 0.0, np.zeros(2)
    rep["rings"] = {}
    for name, r in rings.items():
        seg = np.linalg.norm(np.roll(r["C"], -1, 0) - r["C"], axis=1)
        area = seg * r["w"]
        mass = float(area.sum() * P["thickness"] * 1.27e-6)
        cxy = (area[:, None] * r["C"][:, :2]).sum(0) / area.sum()
        tot_m += mass
        mom += mass * cxy
        C = r["C"]
        d1 = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / 2
        d2 = np.roll(C, -1, 0) - 2 * C + np.roll(C, 1, 0)
        kap = np.linalg.norm(np.cross(d1, d2), axis=1) / np.linalg.norm(d1, axis=1) ** 3
        rep["rings"][name] = dict(length_mm=round(float(r["L"])), width_mm=[round(float(r["w"].min())), round(float(r["w"].max()))],
                                  tightest_bend_radius_mm=round(float(1 / kap.max())), skin_mass_kg=round(mass, 2))
    rep["skin_mass_kg_petg"] = round(tot_m, 2)
    rep["centre_of_mass_offset_mm"] = [round(float(x)) for x in mom / tot_m]
    rep["led_sight_line_test"] = dict(eye_positions=len(EYES), led_points_tested=tested, rays_cast=rays,
                                     led_points_visible=seen)
    rep["led_channels"] = channel_info
    rep["led_total_length_mm"] = int(sum(c["led_length_mm"] for c in channel_info))
    rep["solver"] = dict(G.SOLVE_INFO)
    return rep


report = checks()
(OUT / "Build-data.json").write_text(json.dumps(dict(
    led_runs=[dict(ring=name, stations=[int(x) for x in idx]) for name, idx in runs],
    seats=seat_info, hangers=hanger_info), indent=1))
(OUT / "Checks.json").write_text(json.dumps(report, indent=2))
print("CHECKS " + json.dumps({k: v for k, v in report.items() if k not in ("led_channels", "hangers", "seats")}))


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


CAMS = [
    ("01-Room-view", camera("Cam · room view (reference angle)", (0.05, -1.12, -0.62), (0, 0, -0.08), 30), (1700, 1000)),
    ("02-From-below", camera("Cam · from below", (0, 0.0001, -2.6), (0, 0, -0.08), 50), (1400, 1400)),
    ("03-Side", camera("Cam · low side", (-2.6, -0.6, -0.42), (0, 0, -0.08), 55), (1700, 800)),
    ("04-Oblique", camera("Cam · oblique below", (1.35, -1.45, -1.35), (0, 0, -0.09), 40), (1500, 1200)),
    ("05-Twist-detail", camera("Cam · twist detail", (0.2, -1.25, -0.5), (0.05, -0.38, -0.09), 40), (1500, 1100)),
]
scene.camera = CAMS[0][1]
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
scene.cycles.samples = 32 if DRAFT else 192
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 10
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.55
scene.render.image_settings.file_format = "PNG"

blend = OUT / ("Ribbon-Lamp-V17-Draft.blend" if DRAFT else "Ribbon-Lamp-V17-Borromean.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend))

if "--render" in ARGS:
    scale = 0.55 if DRAFT else 1.0
    suffix = "-draft" if DRAFT else ""
    for fname, cam, (rx, ry) in CAMS:
        scene.camera = cam
        scene.render.resolution_x = int(rx * scale)
        scene.render.resolution_y = int(ry * scale)
        scene.render.filepath = str(OUT / (fname + suffix + ".png"))
        bpy.ops.render.render(write_still=True)
    M_LED.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.0
    bg.inputs["Color"].default_value = (0.55, 0.5, 0.45, 1)
    scene.camera = CAMS[0][1]
    scene.render.resolution_x = int(1700 * scale)
    scene.render.resolution_y = int(1000 * scale)
    scene.render.filepath = str(OUT / ("06-Shape-unlit" + suffix + ".png"))
    bpy.ops.render.render(write_still=True)
