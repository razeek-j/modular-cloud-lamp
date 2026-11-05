"""Reconstruct the complete lamp from the underside reference and export trial parts."""
import json
import math
import struct
import sys
from itertools import combinations
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "full-lamp-v09"
OUT.mkdir(exist_ok=True)
(OUT / "Print").mkdir(exist_ok=True)
FAST = "--draft" in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "V09 | Complete ribbon lamp"
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'MILLIMETERS'
scene.world = bpy.data.worlds.new("Warm interior")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.52, .44, .34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .12

# Opposite edges of each section in the underside image. The third coordinate
# is the inferred depth in mm below the ceiling; the photograph supplies XY.
# The folds roll toward the ceiling as they return behind a nearer surface.
TRACES = {
    "A": ("Diagonal sweep and upper-right roll", True, 26, [
        ((183, 506, 178), (248, 631, 247)),
        ((238, 400, 154), (323, 555, 239)),
        ((363, 372, 140), (464, 516, 235)),
        ((510, 378, 154), (587, 474, 236)),
        ((660, 322, 176), (718, 415, 241)),
        ((814, 184, 136), (851, 401, 240)),
        ((1008, 76, 108), (1015, 420, 240)),
        ((1163, 83, 112), (1138, 462, 251)),
        ((1286, 195, 125), (1204, 525, 258)),
        ((1334, 344, 139), (1237, 595, 251)),
        ((1306, 507, 137), (1224, 640, 224)),
        ((1210, 665, 105), (1176, 622, 159)),
        ((1086, 692, 71), (1097, 625, 111)),
        ((975, 661, 60), (993, 598, 94)),
        ((869, 596, 68), (902, 535, 92)),
        ((747, 597, 75), (765, 552, 99)),
        ((637, 556, 83), (649, 487, 103)),
        ((514, 601, 88), (526, 519, 116)),
        ((398, 656, 95), (448, 594, 135)),
        ((315, 724, 98), (325, 646, 153)),
        ((251, 674, 119), (284, 685, 181)),
        ((204, 591, 153), (240, 665, 218)),
    ]),
    "B": ("Upper-left folded arch", True, 15, [
        ((228, 325, 110), (280, 344, 171)),
        ((228, 240, 114), (320, 275, 178)),
        ((292, 173, 113), (377, 250, 177)),
        ((378, 143, 105), (445, 251, 158)),
        ((475, 173, 98), (505, 280, 142)),
        ((578, 245, 94), (551, 344, 121)),
        ((667, 314, 85), (610, 397, 112)),
        ((744, 363, 78), (654, 454, 104)),
        ((727, 428, 58), (645, 437, 72)),
        ((661, 472, 52), (613, 402, 70)),
        ((563, 460, 54), (566, 372, 77)),
        ((494, 413, 52), (467, 337, 72)),
        ((398, 432, 58), (379, 355, 80)),
        ((308, 464, 68), (313, 380, 103)),
        ((252, 409, 90), (285, 377, 149)),
    ]),
    "C": ("Lower roll and foreground ribbon", True, 21, [
        ((345, 749, 183), (477, 669, 197)),
        ((377, 640, 202), (475, 629, 242)),
        ((484, 561, 210), (610, 629, 273)),
        ((627, 531, 216), (724, 732, 273)),
        ((754, 554, 209), (832, 815, 257)),
        ((860, 609, 205), (942, 840, 246)),
        ((959, 664, 200), (1010, 834, 223)),
        ((1008, 716, 173), (1042, 818, 198)),
        ((1005, 797, 151), (974, 800, 164)),
        ((953, 839, 132), (896, 774, 133)),
        ((840, 877, 125), (791, 806, 119)),
        ((725, 946, 137), (685, 820, 132)),
        ((594, 967, 147), (576, 805, 146)),
        ((473, 937, 153), (504, 762, 159)),
        ((388, 861, 162), (472, 721, 172)),
    ]),
    "D": ("Inner counterfold and small curl", False, 14, []),
}


# The small return rotates continuously about the centreline. A narrower
# shoulder at the tight tip keeps the inside radius open in the print mesh.
small_roll = [
    (827,478,112,43,14), (871,442,132,58,23), (946,435,160,59,35),
    (1010,454,181,58,38), (1048,493,203,55,34), (1024,548,219,80,37),
    (967,598,246,88,30), (915,659,270,82,19), (907,725,290,78,12),
    (930,793,289,79,15), (975,845,284,78,26), (1030,852,275,64,34),
    (1070,821,262,49,29), (1066,785,242,35,29), (1036,774,262,30,24),
    (992,761,256,27,18), (954,755,252,21,12),
]
for i, (x, y, depth, width, roll) in enumerate(small_roll):
    a = small_roll[max(0, i-1)]
    b = small_roll[min(len(small_roll)-1, i+1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    scale = width / (2 * math.hypot(dx, dy))
    TRACES["D"][3].append(((x-dy*scale, y+dx*scale, depth-roll/2),
                           (x+dy*scale, y-dx*scale, depth+roll/2)))

def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result

skins = collection("01 · Complete numbered ribbon panels")
joints = collection("02 · Rear splice plates")
canopy = collection("03 · Centre canopy and metal mounting plate")
carrier = collection("04 · Metal branch and saddle layout")
optics = collection("05 · Selected COB stations")
wires = collection("06 · 24 V loom, inside the carrier routes")
studio = collection("07 · Ceiling and review cameras")

def material(name, color, metal=0, translucent=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1)
    principled.inputs["Metallic"].default_value = metal
    principled.inputs["Roughness"].default_value = .57
    if translucent:
        diffuse = nodes.new("ShaderNodeBsdfTranslucent")
        diffuse.inputs[0].default_value = (*color, 1)
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = translucent
        links.new(principled.outputs[0], mix.inputs[1])
        links.new(diffuse.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], nodes.get("Material Output").inputs[0])
    return mat

paper = material("Washi ivory / uncalibrated PETG appearance", (.94, .90, .80), translucent=.47)
splice_mat = material("Clear PETG rear parts / optical approximation", (.95, .93, .87))
nt = splice_mat.node_tree
transparent = nt.nodes.new("ShaderNodeBsdfTransparent")
transparent.inputs[0].default_value = (.95,.95,.95,1)
mix = nt.nodes.new("ShaderNodeMixShader")
mix.inputs[0].default_value = .79
nt.links.new(nt.nodes.get("Principled BSDF").outputs[0],mix.inputs[1])
nt.links.new(transparent.outputs[0],mix.inputs[2])
nt.links.new(mix.outputs[0],nt.nodes.get("Material Output").inputs[0])
metal = material("Opaque warm white hardware", (.76, .73, .66), .35)
white = material("Ivory centre cap", (.89, .84, .73))
ceiling_mat = material("Warm matte ceiling", (.68, .56, .45))
led_mat = material("Non-emissive tape package", (.96, .69, .29))

def world(point):
    x, y, depth = point
    return np.array(((x - 762) * .001035, (y - 486) * .001035, -depth * .001))

def catmull(points, t, closed):
    index = math.floor(t)
    u = t - index
    if closed:
        p0, p1, p2, p3 = (points[i % len(points)] for i in range(index - 1, index + 3))
    else:
        p0, p1, p2, p3 = (points[max(0, min(i, len(points) - 1))] for i in range(index - 1, index + 3))
    return .5 * ((2 * p1) + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u**2
                 + (-p0 + 3 * p1 - 3 * p2 + p3) * u**3)

def unit(values):
    return values / np.linalg.norm(values, axis=-1, keepdims=True)

def grid_for(trace):
    _, closed, pleats, controls = trace
    rails = np.array([[world(p) for p in section] for section in controls])
    span = len(controls) if closed else len(controls) - 1
    nrows, ncols = span * 12 + 1, pleats * 6 + 1
    ts = np.linspace(0, span, nrows)
    u = np.linspace(0, 1, ncols)
    edges = np.array([catmull(rails, t, closed) for t in ts])
    a, b = edges[:, 0], edges[:, 1]
    tangent = np.gradient((a + b) / 2, axis=0)
    normals = unit(np.cross(tangent, b - a))
    base = a[:, None] * (1 - u[None, :, None]) + b[:, None] * u[None, :, None]
    width = np.linalg.norm(b - a, axis=1)
    bow = np.sin(np.pi * u)[None, :] * np.minimum(width * .022, .007)[:, None]
    ripple = .00034 * np.cos(2 * np.pi * pleats * u) * np.sin(np.pi * u)**.35
    base += normals[:, None, :] * bow[:, :, None]
    derivatives = np.gradient(base, axis=(0, 1))
    normal = unit(np.cross(*derivatives))
    base += normal * ripple[None, :, None]
    if closed:
        base[-1] = base[0]
        normal[-1] = normal[0] = unit(normal[0] + normal[-1])
    return base, normal

def mesh_object(name, vertices, faces, group, mat, smooth=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    if mat:
        mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = smooth
    return obj

def shell(name, grid, normal, low, high, group, mat):
    rows, cols, _ = grid.shape
    layer = rows * cols
    vertices = np.concatenate(((grid + normal * low).reshape(-1, 3),
                               (grid + normal * high).reshape(-1, 3)))
    faces = []
    for row in range(rows - 1):
        for col in range(cols - 1):
            a = row * cols + col
            face = (a, a + cols, a + cols + 1, a + 1)
            faces.extend((tuple(reversed(face)), tuple(index + layer for index in face)))
    boundary = [*range(cols), *range(2 * cols - 1, layer, cols),
                *range(layer - 2, layer - cols - 1, -1),
                *range(layer - 2 * cols, 0, -cols)]
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        faces.append((a, b, b + layer, a + layer))
    obj = mesh_object(name, vertices.tolist(), faces, group, mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), name
    assert bm.calc_volume(signed=True) > 0, name
    bm.to_mesh(obj.data)
    bm.free()
    for poly in obj.data.polygons[-len(boundary):]:
        poly.use_smooth = False
    return obj

def box(name, position, dimensions, group, mat, axes=None):
    origin = Vector(position)
    rotation = Matrix.Identity(3) if axes is None else Matrix(axes).transposed()
    corners = [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
               (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]
    vertices = [origin + rotation @ Vector([p * size / 2 for p, size in zip(c, dimensions)]) for c in corners]
    faces = [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    return mesh_object(name, vertices, faces, group, mat, False)

def cylinder(name, position, radius, depth, group, mat, count=96):
    x, y, z = position
    coords = [(x + radius * math.cos(i * math.tau / count),
               y + radius * math.sin(i * math.tau / count), z + h)
              for h in (-depth / 2, depth / 2) for i in range(count)]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2*count))]
    faces.extend((i, (i+1)%count, (i+1)%count+count, i+count) for i in range(count))
    return mesh_object(name, coords, faces, group, mat, False)

def camera(name, position, scale, target=(0,0,-.14), direct=False):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = position
    if direct:
        obj.rotation_euler = (math.pi, 0, 0)
    else:
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

def light(name, position, target, power, color, size, group=studio):
    data = bpy.data.lights.new(name,'AREA')
    data.shape = 'DISK'
    data.size = size
    data.energy, data.color = power, color
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

def bvh(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons([v.co for v in obj.data.vertices],
                                [tuple(t.vertices) for t in obj.data.loop_triangles], all_triangles=True)

grids = {key: grid_for(trace) for key, trace in TRACES.items()}
masters = {}
for key, (grid, normal) in grids.items():
    # The draft seam removes a tiny strip where a closed loop wraps.
    master = shell(f"{key} · {TRACES[key][0]}", grid[:-1] if TRACES[key][1] else grid,
                   normal[:-1] if TRACES[key][1] else normal, -.00065, .00065, skins, paper)
    masters[key] = master

box("Ceiling datum", (0,0,.014), (5,5,.028), studio, ceiling_mat)
plate = cylinder("Central ceiling plate • Ø220", (0,0,-.002), .110, .004, canopy, metal)
cap = cylinder("Removable ivory centre face", (0,0,-.158), .091, .009, canopy, white)
below = camera("01 · Directly below — reference angle", (.002,.035,-2), 1.57, direct=True)
angle = camera("02 · Room angle", (.54,-1.8,-1.22), 1.55)
service = camera("03 · Rear service angle", (.65,.75,1.6), 1.58)
review_fill = light("Room bounce / review", (-.4,-.2,-1.3), (0,0,-.1), 27, (1,.82,.64), 1.4)
scene.camera = below
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12 if FAST else 42
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = (930,620) if FAST else (1440,960)
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'

for a, b in combinations(masters, 2):
    ta, tb = bvh(masters[a]), bvh(masters[b])
    hits = ta.overlap(tb)
    if hits:
        print("SKIN OVERLAP", a, b, len(hits), flush=True)
        for i, j in hits[::max(1, len(hits)//8)][:9]:
            tri = masters[a].data.loop_triangles[i]
            p = sum((masters[a].data.vertices[v].co for v in tri.vertices), Vector()) / 3
            print("   ", tuple(round(q,1) for q in (p.x/.001035+762,p.y/.001035+486,-p.z*1000)), flush=True)
for key, obj in masters.items():
    tree = bvh(obj)
    ids = [set(t.vertices) for t in obj.data.loop_triangles]
    hits = [(i,j) for i,j in tree.overlap(tree) if i < j and ids[i].isdisjoint(ids[j])]
    if hits:
        from collections import Counter
        cols = grids[key][0].shape[1]
        n = len(obj.data.vertices) // 2
        def coords(tri):
            return tuple(round(sum(((v % n)//cols if k == 0 else (v % n)%cols) for v in tri.vertices)/3) for k in (0,1))
        details = [(coords(obj.data.loop_triangles[i]), coords(obj.data.loop_triangles[j])) for i,j in hits]
        print("GROUPS", key, Counter((round(x[0]/12),round(y[0]/12)) for x,y in details).most_common(32), flush=True)
        print("SKIN SELF", key, len(hits), flush=True)
        for i, _ in hits[::max(1,len(hits)//8)][:9]:
            tri = obj.data.loop_triangles[i]
            p = sum((obj.data.vertices[v].co for v in tri.vertices), Vector()) / 3
            print("   ", tuple(round(q,1) for q in (p.x/.001035+762,p.y/.001035+486,-p.z*1000)), flush=True)

if "--geometry" in sys.argv:
    sys.exit(0)

if FAST:
    scene.render.filepath = "/tmp/ribbon-v09/silhouette.png"
    bpy.ops.render.render(write_still=True)
    sys.exit(0)

# Plan seams on the complete shape. Prefer coverage by a nearer fold and
# standing on an end. Broad sections can rotate diagonally on the print bed.
master_trees = {key: bvh(obj) for key, obj in masters.items()}
UP = Vector((0, 0, 1))

def sample_rows(grid, indices):
    lo = np.floor(indices).astype(int)
    hi = np.minimum(lo + 1, len(grid) - 1)
    blend = (np.asarray(indices) - lo)[:, None, None]
    return grid[lo] * (1 - blend) + grid[hi] * blend

def visible_from(point, direction, trees):
    return not any(tree.ray_cast(Vector(point), direction, 2)[0] is not None for tree in trees)

def trial_orientation(grid):
    middle = grid.shape[1] // 2
    tangent = unit(grid[1, middle] - grid[0, middle])
    span = grid[0, -1] - grid[0, 0]
    span = unit(span - np.dot(span, tangent)*tangent)
    face = unit(np.cross(tangent, span))
    best = None
    for tilt in (0, -22, 22, -45, 45):
        t = math.radians(tilt)
        z = tangent * math.cos(t) + face * math.sin(t)
        y = np.cross(z, span)
        for turn in (0, 35, 45, 55, 90):
            a = math.radians(turn)
            x1 = math.cos(a) * span + math.sin(a) * y
            y1 = np.cross(z, x1)
            basis = np.stack((x1, y1, z), axis=1)
            extents = np.ptp(grid.reshape(-1, 3) @ basis, axis=0)
            max_axis = max(extents)
            if max_axis > .319:
                continue
            # Permit diagonal parts while favouring a near-vertical surface.
            score = max_axis + .0012 * abs(tilt) + .003 * bool(turn)
            if best is None or score < best[0]:
                best = (score, basis, extents)
    return best

def write_stl(obj, name, basis=None):
    obj.data.calc_loop_triangles()
    coords = np.array([list(v.co) for v in obj.data.vertices])
    if basis is not None:
        coords = coords @ basis
    low = coords.min(axis=0)
    high = coords.max(axis=0)
    size = (high - low) * 1000
    assert max(size) <= 322, (name, size)
    coords -= ((high[0] + low[0]) / 2, (high[1] + low[1]) / 2, low[2])
    coords *= 1000
    filename = name + ".stl"
    triangles = obj.data.loop_triangles
    with (OUT / "Print" / filename).open("wb") as output:
        output.write(b"V09 ribbon lamp | millimetres".ljust(80, b"\0"))
        output.write(struct.pack("<I", len(triangles)))
        for tri in triangles:
            a, b, c = (coords[i] for i in tri.vertices)
            direction = np.cross(b-a,c-a)
            length = np.linalg.norm(direction)
            if length < 1e-14:
                raise RuntimeError(f"Degenerate triangle in {name}")
            normal = direction / length
            output.write(struct.pack("<12fH", *normal, *a, *b, *c, 0))
    return dict(file=filename, size_mm=[round(float(value), 2) for value in size],
                triangles=len(triangles))

def split_schedule(key, grid):
    closed = TRACES[key][1]
    span = len(grid) - 1
    nodes = list(range(0, span, 4))
    cols = np.linspace(4, grid.shape[1]-5, 9, dtype=int)
    other_trees = [tree for name, tree in master_trees.items() if name != key]
    costs = {}
    coverage = {}
    for i in nodes:
        coverage[i] = sum(not visible_from(point - (0,0,.002), -UP, other_trees)
                          for point in grid[i, cols])
        forward = unit(grid[min(i+1,span),len(grid[i])//2] - grid[max(0,i-1),len(grid[i])//2])
        width = np.linalg.norm(grid[i,0] - grid[i,-1])
        costs[i] = .035*(9-coverage[i]) + .44*width + .07*abs(forward[2])
    if closed:
        # Select the wrap on a narrow rear return; avoid the prominent front sweep.
        anchor = min(nodes, key=costs.get)
        nodes = sorted(i if i >= anchor else i+span for i in nodes) + [anchor+span]
        work = np.concatenate((grid[:-1],grid))
    else:
        nodes += [span]
        work = grid
    middle = work[:,work.shape[1]//2]
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(middle,axis=0),axis=1))]
    best = {nodes[0]: (0, [])}
    for start_index, start in enumerate(nodes[:-1]):
        if start not in best:
            continue
        for end in nodes[start_index+1:]:
            length = arc[end]-arc[start]
            if length > .385:
                break
            if length < .064:
                continue
            # Coarse screening on the full longitudinal grid, including both edges.
            cross = np.r_[np.arange(0, work.shape[1], 8), work.shape[1]-1]
            orientation = trial_orientation(work[start:end+1, cross])
            if orientation is None:
                continue
            score = best[start][0] + 1 + (0 if end == nodes[-1] else costs[end % span])
            if end not in best or score < best[end][0]:
                best[end] = (score, [*best[start][1], (start,end,orientation[1])])
    if nodes[-1] not in best:
        raise RuntimeError(f"No full bed-size schedule for ribbon {key}")
    return best[nodes[-1]][1], coverage

exports = []
assembly = {}
printed = []
for key, (grid, normals) in grids.items():
    schedule, coverage = split_schedule(key, grid)
    span = len(grid)-1
    closed = TRACES[key][1]
    if closed:
        grid = np.concatenate((grid[:-1],grid))
        normals = np.concatenate((normals[:-1],normals))
    items = []
    seams = [start for start, _, _ in schedule if closed or start > 0]
    for number, (start,end,orientation) in enumerate(schedule,1):
        centre = grid.shape[1]//2
        half_first = .00009 / np.linalg.norm(grid[start+1,centre] - grid[start,centre])
        half_last = .00009 / np.linalg.norm(grid[end-1,centre] - grid[end,centre])
        start_gap = half_first if closed or start > 0 else 0
        end_gap = half_last if closed or end < span else 0
        rows = [start + start_gap, *range(start+1,end), end-end_gap]
        name = f"{key}{number:02d}"
        obj = shell(f"{name} · {TRACES[key][0]}", sample_rows(grid,rows),
                    sample_rows(normals,rows), -.00065, .00065, skins, paper)
        printed.append(obj)
        record = write_stl(obj, name, orientation)
        record.update(type="ribbon", band=key, number=number, start_row=start%span,
                      end_row=end%span if closed else end)
        exports.append(record)
        items.append(record)
    for number, row in enumerate(seams,1):
        # Each seam gets two conformal rear straps near the edges. The narrow
        # attachment faces keep the exposed centre of the ribbon single-wall.
        # Wrap rows at the start of the closed band if required.
        row0 = row + span if closed and row < 6 else row
        centre = grid.shape[1]//2
        before, after = row0, row0
        while before > 0 and np.linalg.norm(grid[row0,centre]-grid[before,centre]) < .016:
            before -= 1
        while after < len(grid)-1 and np.linalg.norm(grid[row0,centre]-grid[after,centre]) < .016:
            after += 1
        for letter, location in zip("io",(.075,.925)):
            if key=="C" and number==3 and letter=="o":
                location=.78
            col = round((grid.shape[1]-1)*location)
            pitch = np.linalg.norm(grid[row0,col+1]-grid[row0,col-1])/2
            radius = max(2,round(.006 / pitch))
            cols = slice(max(1,col-radius),min(grid.shape[1]-1,col+radius+1))
            norm = normals[row0,col]
            rear = 1 if norm[2] > 0 else -1
            limits = sorted((rear*.00083, rear*.00198))
            # If the normal rotates across the seam, use the centre-of-pad
            # rear orientation consistently on both halves.
            name = f"{key}-J{number:02d}{letter}"
            obj = shell(name, grid[before:after+1,cols], normals[before:after+1,cols],
                        *limits, joints, splice_mat)
            printed.append(obj)
            z = norm * rear
            x = unit(grid[min(row0+1,len(grid)-1),col] - grid[max(0,row0-1),col])
            x = unit(x - np.dot(x,z)*z)
            record = write_stl(obj, name, np.stack((x,np.cross(z,x),z),axis=1))
            record.update(type="splice", band=key, seam=number, row=row%span,
                          edge="inner label i" if letter=="i" else "outer label o")
            exports.append(record)
    assembly[key] = dict(name=TRACES[key][0], panels=items,
                         seam_rows=[r%span for r in seams],
                         seam_coverage=[coverage[r%span] for r in seams],
                         closed=closed)
    print("PRINT SCHEDULE", key, len(items), len(seams), flush=True)

for obj in masters.values():
    bpy.data.objects.remove(obj,do_unlink=True)
panel_objects = [obj for obj in printed if obj.name[1:3].isdigit()]
panel_trees = [bvh(obj) for obj in panel_objects]

def front_cover(point, views, trees):
    return sum(not visible_from(point, view, trees) for view in views)

def highest_skin(x, y):
    origin = Vector((x,y,-.002))
    hits = [tree.ray_cast(origin,-UP,.36)[0] for tree in panel_trees]
    return max((p.z for p in hits if p is not None), default=None)

# Recess two short stations in tighter folds; keep one longer wash in the wide roll.
angles = (0, math.pi/2, math.pi, 3*math.pi/2)
station_views = [-UP, *(Vector((math.cos(a)*.50, math.sin(a)*.50,-.866)) for a in angles),
                 *(Vector((math.cos(a)*.707, math.sin(a)*.707,-.707)) for a in angles),
                 *(Vector((math.cos(a)*.85, math.sin(a)*.85,-.527)) for a in angles)]
room_view = (angle.location-Vector((0,0,-.14))).normalized()
stations = []
for index,(px,py,preferred,length) in enumerate(
        ((403,444,-.21,.100),(1077,276,.10,.200),(696,654,.36,.100)),1):
    reference = Vector(world((px,py,0)))
    best = None
    for dx in (-.055,-.028,0,.028,.055):
        for dy in (-.055,-.028,0,.028,.055):
            centre = reference + Vector((dx,dy,0))
            for da in (-.63,-.32,0,.32,.63):
                t = preferred + da
                x_axis = Vector((math.cos(t),math.sin(t),0))
                y_axis = UP.cross(x_axis)
                half = length/2+.006
                footprint = [centre+x_axis*(half*x)+y_axis*y
                             for x in (-1,-.68,-.33,0,.33,.68,1) for y in (-.012,.012)]
                heights = [highest_skin(p.x,p.y) for p in footprint]
                if any(z is None for z in heights):
                    continue
                for recess in (.023,.037,.050,.061):
                    z = max(heights) + recess
                    if z > -.036:
                        continue
                    points = [Vector((p.x,p.y,z)) for p in footprint]
                    if any(visible_from(point,-UP,panel_trees) for point in points):
                        continue
                    coverage = sum(front_cover(p,station_views,panel_trees) for p in points)
                    side_cover = sum(not visible_from(p,room_view,panel_trees) for p in points)
                    score = coverage+2*side_cover + 60*recess - 45*math.hypot(dx,dy) - 3*abs(da)
                    if best is None or score > best[0]:
                        best = score,Vector((centre.x,centre.y,z)),x_axis,y_axis,coverage,side_cover,recess
    if best is None:
        raise RuntimeError(f"Could not screen LED station {index}")
    _,origin,x_axis,y_axis,coverage,side_cover,recess = best
    axes = (x_axis,y_axis,UP)
    width = length+.012
    shields = [box(f"L{index} • aluminum heat bed",origin,(width,.024,.002),optics,metal,axes)]
    for side in (-1,1):
        shields.append(box(f"L{index} • opaque side lip",origin+y_axis*.011*side+UP*.005,
                           (width,.002,.012),optics,metal,axes))
        shields.append(box(f"L{index} • opaque end cap",origin+x_axis*(width/2-.001)*side+UP*.005,
                           (.002,.020,.012),optics,metal,axes))
    box(f"L{index} • COB tape {length*1000:.0f} mm",origin+UP*.0018,(length,.008,.0016),optics,led_mat,axes)
    # Use a luminous area proxy at the actual strip, pointing into the real ceiling.
    proxy = light(f"L{index} • upward photometric proxy",origin+UP*.0027,origin+UP,
                  2.3 if index==2 else 1.7,(1,.68,.36),length,optics)
    proxy.data.shape = 'RECTANGLE'
    proxy.data.size_y = .008
    shield_trees = [bvh(obj) for obj in shields]
    rays = 0
    for x in (-.99,-.50,0,.50,.99):
        for y in (-.0038,0,.0038):
            p = origin+x_axis*(x*length/2)+y_axis*y+UP*.0027
            for elevation in (0,-10,-30,-60,-90):
                e = math.radians(elevation)
                for azimuth in range(0,360,10):
                    a = math.radians(azimuth)
                    ray = Vector((math.cos(a)*math.cos(e),math.sin(a)*math.cos(e),math.sin(e)))
                    assert not visible_from(p,ray,shield_trees), (index,x,y,elevation,azimuth)
                    rays += 1
    stations.append(dict(id=f"L{index}",origin=origin,axes=axes,emitter_rays_blocked=rays,
                         housing_samples_screened=coverage,housing_samples_total=14*len(station_views),
                         oblique_camera_samples_screened=side_cover,oblique_camera_samples_total=14,
                         nominal_tape_mm=round(length*1000),recess_above_highest_skin_mm=round(recess*1000)))
    print("STATION",index,list(origin),coverage,side_cover,flush=True)

def wire_curve(name, points, radius, group, mat):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for v,p in zip(spline.points,points):
        v.co = (*p,1)
    obj = bpy.data.objects.new(name,curve)
    group.objects.link(obj)
    curve.materials.append(mat)
    return obj

def annular(name, profile, group, mat, count=120):
    vertices = [(r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z)
                for r,z in profile for i in range(count)]
    faces = [(j*count+i,j*count+(i+1)%count,k*count+(i+1)%count,k*count+i)
             for j in range(len(profile)) for k in [(j+1)%len(profile)] for i in range(count)]
    obj = mesh_object(name,vertices,faces,group,mat,False)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    return obj

def difference(obj, cutter):
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Clearance","BOOLEAN")
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

# Removable slip cover. The skirt screws enter from the side; the face stays plain.
bpy.data.objects.remove(cap,do_unlink=True)
profile = [(.091,-.163),(.091,-.1545),(.091,-.1505),(.091,-.143),
           (.0883,-.143),(.0883,-.1505),(.0883,-.1545),(.0883,-.160)]
ring_size = 240
vertices = [(r*math.cos(i*math.tau/ring_size),r*math.sin(i*math.tau/ring_size),z)
            for r,z in profile for i in range(ring_size)]
slots = [round(angle*ring_size/math.tau)-1 for angle in
         (math.pi/6,5*math.pi/6,3*math.pi/2)]
open_segments = {i for start in slots for i in (start,start+1)}
faces = [(j*ring_size+i,j*ring_size+(i+1)%ring_size,
          (j+1)*ring_size+(i+1)%ring_size,(j+1)*ring_size+i)
         for j in range(len(profile)-1) for i in range(ring_size)
         if not (j in (1,5) and i in open_segments)]
for start in slots:
    for col in range(start,start+2):
        for a,b in ((1,6),(5,2)):
            faces.append((a*ring_size+col,a*ring_size+col+1,
                          b*ring_size+col+1,b*ring_size+col))
    for col in (start,start+2):
        faces.append(tuple(row*ring_size+col for row in (1,2,5,6)))
faces.extend((tuple(reversed(range(ring_size))),tuple(range(7*ring_size,8*ring_size))))
cap = mesh_object("E · Printed centre face and slip skirt",vertices,faces,canopy,white,False)
bm = bmesh.new()
bm.from_mesh(cap.data)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(cap.data)
bm.free()

body = annular("Stepped metal canopy and cover keeper",
               [(.0875,-.156),(.0875,-.149),(.053,-.149),(.053,-.005),
                (.051,-.005),(.051,-.151),(.0855,-.151),(.0855,-.156)],canopy,metal)
hub = cylinder("Central metal branch hub",(0,0,-.026),.068,.004,canopy,metal)
for x,y in ((-.067,-.050),(.067,-.050),(0,.081),(0,0)):
    cut = cylinder("Tool · plate hole",(x,y,-.002),.0034 if x or y else .007,.012,canopy,metal,48)
    difference(plate,cut)
box("24 V driver envelope · accessible behind cap",(-.006,.007,-.083),(.065,.033,.026),canopy,metal)
box("One 24 V star connection · three pairs",(0,-.032,-.107),(.035,.017,.012),canopy,white)
cap.data.calc_loop_triangles()
exports.append(dict(write_stl(cap,"E-Centre-cover"),type="cover"))

# Solve three centre-rooted routes on a small grid behind the projected shade.
# A route can be reduced to straight fabrication runs only where the full
# interpolated segment clears the skin. A short sleeve port serves each route.
from functools import lru_cache
from heapq import heappop, heappush

STEP = .012

def grid_xy(node):
    return node[0]*STEP,node[1]*STEP

def node_of(p):
    return round(p.x/STEP),round(p.y/STEP)

@lru_cache(maxsize=None)
def route_cell(node):
    x,y = grid_xy(node)
    radius = math.hypot(x,y)
    if radius < .075:
        return -.026,True
    h = [highest_skin(x+dx,y+dy) for dx,dy in ((0,0),(.007,0),(-.007,0),(0,.007),(0,-.007))]
    z = max((p for p in h if p is not None),default=-.140)
    return max(-.090,z+.021), h[0] is not None

def segment_clear(p,q,clearance=.008,step=.006):
    side=UP.cross(q-p)
    if side.length<1e-6:
        side=Vector((1,0,0))
    side=side.normalized()*.007
    count=max(2,math.ceil((q-p).length/step))
    for i in range(count+1):
        c=p.lerp(q,i/count)
        for point in (c,c+side,c-side):
            surface=highest_skin(point.x,point.y)
            if surface is not None and point.z < surface+clearance:
                return False
    return True

def get_route(goal):
    anchor = goal.copy()
    anchor.z = 0
    anchor = anchor.normalized()*.045
    anchor.z = -.026
    start = node_of(anchor)
    last = node_of(goal)
    queue = [(0,0,start)]
    costs = {start:0}
    previous = {}
    while queue:
        _, cost, node = heappop(queue)
        if cost != costs[node]:
            continue
        if node == last:
            break
        z,_ = route_cell(node)
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
            nxt = (node[0]+dx,node[1]+dy)
            if abs(nxt[0])>51 or abs(nxt[1])>45:
                continue
            nz,covered = route_cell(nxt)
            if nz > -.014:
                continue
            if abs(nz-z)>.012 and not segment_clear(Vector((*grid_xy(node),z)),
                                                        Vector((*grid_xy(nxt),nz))):
                continue
            move = math.hypot(dx,dy) + 7*abs(nz-z)/STEP + (0 if covered else 26)
            total = cost + move
            if total < costs.get(nxt,float('inf')):
                costs[nxt] = total
                previous[nxt] = node
                heappush(queue,(total+math.dist(nxt,last),total,nxt))
    if last != start and last not in previous:
        raise RuntimeError(f"Could not route to {goal}")
    path = [last]
    while path[-1] != start:
        path.append(previous[path[-1]])
    points = [anchor] + [Vector((*grid_xy(node),route_cell(node)[0])) for node in reversed(path)]
    points.append(Vector((goal.x,goal.y,goal.z+.007)))
    # Consolidate adjacent runs with room for the 12 × 10 mm tube.
    def straight(start,end):
        if not segment_clear(start,end):
            return False
        for i in range(1, math.ceil((end-start).length/.007)):
            p = start.lerp(end,i/math.ceil((end-start).length/.007))
            if math.hypot(p.x,p.y) < .073:
                continue
            nominal, covered = route_cell(node_of(p))
            if not covered or p.z < nominal-.004:
                return False
        return True
    reduced = [points[0]]
    i = 0
    while i < len(points)-1:
        j = min(i+16,len(points)-1)
        while j > i+1 and not straight(points[i],points[j]):
            j -= 1
        reduced.append(points[j])
        i = j
    return [p for i,p in enumerate(reduced) if i==0 or (p-reduced[i-1]).length>.001]

def tube(name, p, q, width=.012, depth=.010, wall=.0012, group=carrier):
    along = (q-p).normalized()
    flat = UP.cross(along)
    if flat.length < .01:
        flat = Vector((1,0,0))
    flat.normalize()
    normal = along.cross(flat).normalized()
    vertices = []
    for point in (p,q):
        for w,h in ((width/2,depth/2),(width/2-wall,depth/2-wall)):
            vertices.extend(point + flat*w*x + normal*h*y for x,y in ((-1,-1),(1,-1),(1,1),(-1,1)))
    faces = []
    for i in range(4):
        j = (i+1)%4
        faces.extend(((i,j,j+8,i+8),(i+4,i+12,j+12,j+4),
                      (i,i+4,j+4,j),(i+8,j+8,j+12,i+12)))
    return mesh_object(name,vertices,faces,group,metal,False)

def room_screened_branch(origin):
    # The low branch crosses two separate folds. Route it in XYZ so the
    # carrier can turn behind their overlap without showing through the gap.
    from itertools import product
    visual_trees=[*panel_trees,bvh(cap),bvh(body)]
    step=.012
    root=Vector((-.028,.035,-.026))
    target=origin+UP*.007
    def key(p):
        return tuple(round(v/step) for v in p)
    def point(k):
        return Vector(tuple(v*step for v in k))
    first,last=key(root),key(target)
    moves=[move for move in product((-1,0,1),repeat=3) if any(move)]
    @lru_cache(maxsize=None)
    def cost_at(k):
        x,y,z=point(k)
        h=highest_skin(x,y)
        if h is not None and z<h+.010:
            return None
        p=Vector((x,y,z))
        below_loss=sum(visible_from(p+offset,-UP,visual_trees)
                       for offset in (Vector(),Vector((.005,0,0)),Vector((-.005,0,0))))
        side_loss=sum(visible_from(p+offset,room_view,visual_trees)
                      for offset in (Vector(),Vector((.005,0,0)),Vector((-.005,0,0))))
        return 5*below_loss+6*side_loss
    queue=[(0,0,first)]
    costs={first:0}
    parent={}
    while queue:
        _,value,k=heappop(queue)
        if costs[k]!=value:
            continue
        if k==last:
            break
        for d in moves:
            nxt=tuple(a+b for a,b in zip(k,d))
            if not (-19<=nxt[0]<=15 and -4<=nxt[1]<=28 and -19<=nxt[2]<=-2):
                continue
            loss=cost_at(nxt)
            if loss is None:
                continue
            score=value+math.sqrt(sum(v*v for v in d))+loss
            if score<costs.get(nxt,float("inf")):
                costs[nxt]=score
                parent[nxt]=k
                heappush(queue,(score+math.dist(nxt,last),score,nxt))
    if last not in parent:
        return get_route(origin)
    points=[last]
    while points[-1]!=first:
        points.append(parent[points[-1]])
    route=[root,*[point(k) for k in reversed(points[1:-1])],target]
    def screened(a,b):
        if not segment_clear(a,b,clearance=.010,step=.003):
            return False
        n=max(2,math.ceil((a-b).length/.005))
        for i in range(1,n):
            p=a.lerp(b,i/n)
            for v in (-UP,room_view):
                if visible_from(p,v,visual_trees):
                    return False
        return True
    result=[route[0]]
    i=0
    while i<len(route)-1:
        j=len(route)-1
        while j>i+1 and not screened(route[i],route[j]):
            j-=1
        result.append(route[j])
        i=j
    return result


route_reports = []
carrier_segments = []
for index,station in enumerate(stations,1):
    goal=station["origin"]
    route=room_screened_branch(goal) if index==3 else get_route(goal)
    # Check the actual tube, including its corners where a steep segment
    # can graze a fold between centreline samples. Lift shared joints.
    for iteration in range(8):
        members=[]
        bad=set()
        for j,(p,q) in enumerate(zip(route,route[1:]),1):
            if (q-p).length<.001:
                continue
            obj=tube(f"B{index}.{j:02} • hollow aluminum branch envelope",p,q)
            members.append((p,q,obj,index))
            member_tree=bvh(obj)
            if any(member_tree.overlap(tree) for tree in panel_trees):
                bad.update(i for i in (j-1,j) if 0<i<len(route)-1)
        if not bad:
            carrier_segments.extend(members)
            break
        for _,_,obj,_ in members:
            bpy.data.objects.remove(obj,do_unlink=True)
        for j in bad:
            route[j].z=min(-.014,route[j].z+.009)
    else:
        raise RuntimeError(f"Unable to clear full tube for branch {index}")
    # The three roots start on the inner hub and cross the stepped sleeve.
    exit_index = next(i for i,p in enumerate(route) if p.xy.length >= .053)
    q = route[exit_index]
    p = route[exit_index-1]
    crossing = p
    for f in np.linspace(0,1,20):
        crossing = p.lerp(q,float(f))
        if crossing.xy.length >= .053:
            break
    cut = box("Tool · protected branch sleeve port",crossing,(.048,.037,.035),canopy,metal)
    difference(body,cut)
    station_origin = station["origin"]
    feed_direction=station["axes"][0]
    sign=1 if feed_direction.dot(-station_origin)>0 else -1
    end=station_origin+feed_direction*sign*(station["nominal_tape_mm"]*.0005+.008)
    wire_curve(f"L{index} • paired 24 V feed inside B{index}",
               [Vector((0,-.032,-.106)),Vector((0,-.032,-.026)),*route,
                end+UP*.003,end+UP*.011,
                end-feed_direction*sign*.010+UP*.011,
                end-feed_direction*sign*.010+UP*.003],.0012,wires,metal)
    # Short removable station fixing between tube and back of the heat bed.
    fastener_p = station_origin+UP*.001
    fastener_q = route[-1]
    if (fastener_q-fastener_p).length>.001:
        tube(f"L{index} • station fastener envelope",fastener_p,fastener_q,.008,.008,.001)
    route_reports.append(dict(id=f"B{index}", points_mm=[[round(v*1000,1) for v in p] for p in route],
                              destination=f"L{index}"))

def segment_nearest(point, p, q):
    along = q-p
    fraction = max(0,min(1,(point-p).dot(along)/along.length_squared))
    return p + along*fraction

def nonadjacent_hits(obj,tree):
    ids = [set(tri.vertices) for tri in obj.data.loop_triangles]
    return sum(1 for i,j in tree.overlap(tree) if i<j and ids[i].isdisjoint(ids[j]))

anchors = []
splice_trees = [bvh(obj) for obj in printed if "-J" in obj.name]
for key,(grid,normals) in grids.items():
    candidates = []
    centre = grid.shape[1]//2
    for row in range(6,len(grid)-6,3):
        if any(np.linalg.norm(grid[row,centre]-grid[r,centre]) < .028 for r in assembly[key]["seam_rows"]):
            continue
        for col in (round(centre*.45),round(centre*1.55)):
            q = Vector(grid[row,col])
            n = Vector(normals[row,col])
            if abs(n.z)<.53:
                continue
            if n.z<0:
                n.negate()
            if q.xy.length < .108:
                continue
            top = q+n*.007
            choices = [(segment_nearest(top,p1,q1),branch) for p1,q1,_,branch in carrier_segments]
            p,branch = min(choices,key=lambda item:(item[0]-top).length_squared)
            if p.z < top.z+.003 or (p-top).length > .190:
                continue
            if any(tree.ray_cast(top,(p-top).normalized(),(p-top).length-.002)[0] is not None
                   for tree in panel_trees):
                continue
            screened = front_cover(top,station_views,panel_trees)
            spur_views = sum(visible_from(p.lerp(top,u),view,panel_trees)
                             for u in (.15,.35,.55,.75,.95) for view in (room_view,-UP))
            candidates.append(((p-top).length + .018*(len(station_views)-screened) +
                               .075*spur_views,row,col,p,branch))
    accepted = []
    for _,row,col,p,branch in sorted(candidates,key=lambda item:item[0]):
        q = Vector(grid[row,col])
        if any((q-other).length < .090 for other in accepted):
            continue
        n = Vector(normals[row,col])
        rear = 1 if n.z>0 else -1
        n *= rear
        first,last = row,row
        while first>0 and np.linalg.norm(grid[first,col]-grid[row,col])<.015:
            first-=1
        while last<len(grid)-1 and np.linalg.norm(grid[last,col]-grid[row,col])<.015:
            last+=1
        if any(first-1 <= r <= last+1 for r in assembly[key]["seam_rows"]):
            continue
        pitch = np.linalg.norm(grid[row,col+1]-grid[row,col-1])/2
        reach = max(3,round(.009/pitch))
        cols = slice(max(1,col-reach),min(grid.shape[1]-1,col+reach+1))
        limits = sorted((rear*.00083,rear*.0061))
        label = f"{key}-M{len(accepted)+1:02d}"
        pad = shell(label,grid[first:last+1,cols],normals[first:last+1,cols],*limits,joints,splice_mat)
        pad_tree=bvh(pad)
        if any(pad_tree.overlap(tree) for tree in splice_trees+panel_trees):
            bpy.data.objects.remove(pad,do_unlink=True)
            continue
        pad_top=q+n*.006
        spur=None
        if (p-pad_top).length>.003:
            spur=tube(f"{label} • carrier spur to B{branch}",p,pad_top+n*.002,.008,.008,.001)
            spur_tree=bvh(spur)
            if any(spur_tree.overlap(tree) for tree in panel_trees):
                bpy.data.objects.remove(spur,do_unlink=True)
                bpy.data.objects.remove(pad,do_unlink=True)
                continue
        x = Vector(grid[row+1,col]-grid[row-1,col])
        x = (x-n*x.dot(n)).normalized()
        y = n.cross(x).normalized()
        for side in (-1,1):
            hole = q+x*.007*side+n*.0048
            cutter = cylinder("Tool · M3 pilot recess",hole,.00145,.006,carrier,metal,32)
            rotation = UP.rotation_difference(n)
            for vertex in cutter.data.vertices:
                vertex.co = hole + rotation @ (vertex.co-hole)
            difference(pad,cutter)
        if nonadjacent_hits(pad,bvh(pad)):
            if spur:
                bpy.data.objects.remove(spur,do_unlink=True)
            bpy.data.objects.remove(pad,do_unlink=True)
            continue
        printed.append(pad)
        for side in (-1,1):
            bolt = cylinder(f"{label} • short M3 envelope",q+x*.007*side+n*.006,.0015,.007,carrier,metal,24)
            pivot = q+x*.007*side+n*.006
            for vertex in bolt.data.vertices:
                vertex.co = pivot + rotation @ (vertex.co-pivot)
        box(f"{label} • perforated aluminum saddle envelope",pad_top+n*.001,
            (.025,.008,.002),carrier,metal,(x,y,n))
        export = write_stl(pad,label,np.stack((np.array(x),np.array(y),np.array(n)),axis=1))
        span=len(grid)-1
        panel = next((part["file"][:-4] for part in assembly[key]["panels"]
                     if (part["start_row"]<=row<=part["end_row"] if part["start_row"]<=part["end_row"]
                         else row>=part["start_row"] or row<=part["end_row"])),None)
        assert panel
        export.update(type="mount pad",band=key,panel=panel,row=row,column=col)
        exports.append(export)
        anchors.append(dict(id=label,panel=panel,branch=f"B{branch}",
                            location_mm=[round(v*1000,1) for v in q]))
        accepted.append(q)
        if len(accepted)==(3 if key in "AC" else 2):
            break
    print("SADDLES",key,len(accepted),flush=True)
    assert len(accepted)>=2, f"Insufficient carrier seats for {key}"

def solid_check(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), obj.name
    remaining = set(bm.verts)
    nodes = [remaining.pop()]
    while nodes:
        for edge in nodes.pop().link_edges:
            for v in edge.verts:
                if v in remaining:
                    remaining.remove(v)
                    nodes.append(v)
    assert not remaining, obj.name
    assert bm.calc_volume(signed=True)>0, obj.name
    bm.free()
    tree = bvh(obj)
    return tree,nonadjacent_hits(obj,tree)

check_objects = [*printed,cap]
trees = {}
self_errors = {}
for obj in check_objects:
    trees[obj],count = solid_check(obj)
    if count:
        self_errors[obj.name] = count
bounds = {obj:np.array([list(v.co) for v in obj.data.vertices]) for obj in check_objects}
bounds = {obj:(points.min(axis=0),points.max(axis=0)) for obj,points in bounds.items()}
overlaps = {}
for a,b in combinations(check_objects,2):
    if np.any(bounds[a][1]<bounds[b][0]) or np.any(bounds[b][1]<bounds[a][0]):
        continue
    n=len(trees[a].overlap(trees[b]))
    if n:
        overlaps[f"{a.name} vs {b.name}"]=n
hardware_crossings = {}
for obj in [*carrier.objects,*optics.objects,body,plate,hub]:
    if obj.type!='MESH':
        continue
    htree=bvh(obj)
    count=sum(len(htree.overlap(tree)) for tree in panel_trees)
    if count:
        hardware_crossings[obj.name]=count
print("SELF CHECK",self_errors,flush=True)
print("PRINTED OVERLAP",overlaps,flush=True)
print("HARDWARE VS SKINS",hardware_crossings,flush=True)

for station in stations:
    station["position_mm"]=[round(v*1000,1) for v in station.pop("origin")]
    axis,_,_=station.pop("axes")
    station["heading_degrees"]=round(math.degrees(math.atan2(axis.y,axis.x)),1)

outer=np.concatenate([np.array([list(v.co) for v in o.data.vertices]) for o in panel_objects])
data = dict(
    shade_extents_mm=[round(float(v*1000),1) for v in np.ptp(outer,axis=0)],
    drop_from_ceiling_mm=round(float(-outer[:,2].min()*1000),1),
    panel_count=len(panel_objects), print_count=len(exports), bands=assembly, prints=exports,
    lighting=dict(nominal_voltage=24,parallel_tape_runs=stations,central_connection="single serviceable star split",
                  copper_routes=route_reports),
    attachments=anchors,self_intersections=self_errors,printed_pairwise_overlaps=overlaps,
    carrier_skin_intersections=hardware_crossings,
    nominal_skin_thickness_mm=1.3,nominal_seam_gap_mm=.18,
)
(OUT/"Build-map.json").write_text(json.dumps(data,indent=2)+"\n")
print("FULL SUMMARY",data["shade_extents_mm"],data["drop_from_ceiling_mm"],data["print_count"],flush=True)

reference = bpy.data.images.load(str(ROOT/"prototype-v08/underside-reference.png"))
reference.name = "Reference • underside supplied by user"
reference.pack()
reference.use_fake_user = True
code = bpy.data.texts.new("V09 • editable ribbon trace source")
code.write(Path(__file__).read_text())
scene["Lighting"] = "Two 100 mm and one 200 mm COB strips. Paired low-voltage conductors return inside the three hollow branches to a single centre split."
scene["Fabrication"] = "All printed pieces are numbered. See the paired build map and print package. Metal section sizes, adhesive and overhead retention require physical validation."
scene.camera = below
scene.view_settings.exposure = 0
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            view = area.spaces.active
            view.overlay.show_overlays=False
            view.shading.color_type='MATERIAL'
            view.region_3d.view_location=(.002,.030,-.17)
            view.region_3d.view_distance=1.61
            view.region_3d.view_rotation=below.rotation_euler.to_quaternion()
            view.region_3d.view_perspective='ORTHO'

bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Ribbon-Lamp-V09-Full.blend"),compress=True)
if "--render" in sys.argv:
    for name,view,fill,hide_ceiling in (
        ("01-Directly-below-lit",below,8.0,False),
        ("02-Oblique-lit",angle,8.0,False),
        ("03-Directly-below-unlit",below,27.0,False),
        ("04-Service-side",service,34.0,True),
    ):
        scene.camera=view
        review_fill.data.energy=fill
        bpy.data.objects["Ceiling datum"].hide_render=hide_ceiling
        for obj in optics.objects:
            if obj.type=='LIGHT':
                obj.hide_render='unlit' in name or hide_ceiling
        if hide_ceiling:
            light("Service review fill",(.3,.5,1), (0,0,-.1), 65,(1,.92,.80),1.3)
        scene.render.filepath=str(OUT/(name+".png"))
        bpy.ops.render.render(write_still=True)
