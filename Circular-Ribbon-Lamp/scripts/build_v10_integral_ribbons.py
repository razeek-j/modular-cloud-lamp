"""V10 close-ceiling ribbon lamp with joints formed in its printed panels."""
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
OUT = ROOT / "full-lamp-v10"
OUT.mkdir(exist_ok=True)
(OUT / "Print").mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "V10 | Three self-joining ribbons"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"
scene.world = bpy.data.worlds.new("Warm interior")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.56,.51,.46,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .13

# Opposite edges traced from the supplied underside view in V09.
# The reduced depth is derived in world(); the tight D curl was removed.
TRACES = {'A': ('Diagonal sweep and upper-right roll',
       True,
       26,
       [((183, 506, 178), (248, 631, 247)),
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
        ((204, 591, 153), (240, 665, 218))]),
 'B': ('Upper-left folded arch',
       True,
       15,
       [((228, 325, 110), (280, 344, 171)),
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
        ((252, 409, 90), (285, 377, 149))]),
 'C': ('Lower roll and foreground ribbon',
       True,
       21,
       [((345, 749, 183), (477, 669, 197)),
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
        ((388, 861, 162), (472, 721, 172))])}

def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result

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

def world(point,depth_scale,ceiling_gap):
    x, y, depth = point
    return np.array(((x - 762) * .001035, (y - 486) * .001035, -depth * depth_scale - ceiling_gap))

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

def grid_for(trace,depth_scale=.00060,ceiling_gap=.004,bow_factor=.010,pleat_amplitude=.00027):
    _, closed, pleats, controls = trace
    rails = np.array([[world(p,depth_scale,ceiling_gap) for p in section] for section in controls])
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
    bow = np.sin(np.pi * u)[None, :] * np.minimum(width * bow_factor, .007)[:, None]
    ripple = pleat_amplitude * np.cos(2 * np.pi * pleats * u) * np.sin(np.pi * u)**.35
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

def light(name, position, target, power, color, size, group=None):
    data = bpy.data.lights.new(name,'AREA')
    data.shape = 'DISK'
    data.size = size
    data.energy, data.color = power, color
    obj = bpy.data.objects.new(name, data)
    (group or studio).objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

def bvh(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons([v.co for v in obj.data.vertices],
                                [tuple(t.vertices) for t in obj.data.loop_triangles], all_triangles=True)


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
        output.write(b"V10 ribbon lamp | millimetres".ljust(80, b"\0"))
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

def nonadjacent_hits(obj,tree):
    ids = [set(tri.vertices) for tri in obj.data.loop_triangles]
    return sum(1 for i,j in tree.overlap(tree) if i<j and ids[i].isdisjoint(ids[j]))

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

def visible_from(point, direction, trees):
    return not any(tree.ray_cast(Vector(point), direction, 2)[0] is not None for tree in trees)

skins = collection("01 · Numbered ribbon panels with integral laps")
canopy = collection("02 · Compact centre mount and removable face")
lighting = collection("03 · Three enclosed central lights and loom")
studio = collection("04 · Review cameras and ceiling")
paper = material("Milky PETG appearance",(.94,.90,.80),translucent=.47)
ivory = material("Opaque ivory centre",(.92,.88,.78))
metal = material("Aluminum, white finish",(.82,.79,.71),.35)
tape = material("COB tape package",(.92,.71,.31))
ceiling = material("Warm matte ceiling",(.68,.57,.46))
UP=Vector((0,0,1))

def smooth_shell(key):
    points, normals = grids[key]
    return shell(key,points[:-1],normals[:-1],-.0008,.0008,skins,paper)

grids={key:grid_for(trace) for key,trace in TRACES.items()}
# Affine compression keeps the exact crease topology of the earlier arch.
arch,arch_normal=grid_for(TRACES["B"],.001,0,.022,.00034)
arch[...,2]=arch[...,2]*.60-.003
arch_normal[...,2]*=.60
grids["B"]=(arch,arch_normal)
grids["C"][0][...,2]+=.027
masters={key:smooth_shell(key) for key in grids}
trees={key:bvh(obj) for key,obj in masters.items()}
for key,obj in masters.items():
    print("SKIN",key,"self",nonadjacent_hits(obj,trees[key]),flush=True)
    if "--probe" in sys.argv:
        cols=grids[key][0].shape[1]
        size=len(obj.data.vertices)//2
        ids=[set(t.vertices) for t in obj.data.loop_triangles]
        problems=[tuple(round(sum((v%size)//cols for v in ids[k])/3) for k in (i,j))
                  for i,j in trees[key].overlap(trees[key]) if i<j and ids[i].isdisjoint(ids[j])]
        from collections import Counter
        print(Counter((round(x/12),round(y/12)) for x,y in problems),flush=True)
for a,b in combinations(grids,2):
    print("SKINS",a,b,"pair",len(trees[a].overlap(trees[b])),flush=True)

# Explore rear overlaps and the centre before choosing contact lands.
if "--probe" in sys.argv:
    for a,b in (("A","B"),("A","C"),("B","C")):
        points,normals=grids[a]
        pairs=[]
        for r in range(2,len(points)-2,2):
            for c in range(7,points.shape[1]-8,4):
                p=Vector(points[r,c])
                n=Vector(normals[r,c])
                if abs(n.z)<.45:
                    continue
                for d in (-UP,UP):
                    hit,h_norm,_,dist=trees[b].ray_cast(p+d*.0012,d,.085)
                    if hit is not None and abs(h_norm.z)>.45:
                        pairs.append((dist,r,c,list(p),list(hit),list(d)))
        picked=[]
        for dist,r,c,p,h,d in sorted(pairs,key=lambda x:x[0]):
            if any((Vector(p)-Vector(o[3])).length<.090 for o in picked):
                continue
            picked.append((dist,r,c,p,h,d))
        print("PROBE",a,b,[(round(t[0]*1000,1),t[1],t[2],*[list(round(v*1000,1) for v in q) for q in t[3:5]],t[5][2]) for t in picked[:12]],flush=True)
    for key,(points,normals) in grids.items():
        candidates=[]
        for row in range(2,len(points)-2,2):
            for c in range(4,points.shape[1]-4,4):
                p=Vector(points[row,c])
                n=Vector(normals[row,c])
                if p.xy.length<.100 and abs(n.z)>.24:
                    candidates.append((p.xy.length,row,c,p))
        chosen=[]
        for data in sorted(candidates,key=lambda x:x[0]):
            if any((data[-1]-other[-1]).length<.034 for other in chosen):
                continue
            chosen.append(data)
        print("ROOT",key,[(r,c,[round(v*1000,1) for v in p]) for _,r,c,p in chosen[:12]],flush=True)
    sys.exit(0)

previous=json.loads((ROOT/"full-lamp-v09/Build-map.json").read_text())
divisions={key:[p["start_row"] for p in previous["bands"][key]["panels"]] for key in "ABC"}
# Keep the rear A/C pass out of the visible centre face, with two closed loop
# joints moved away from the centre fastener seats.
divisions["C"][2]=19

BASE=.0008
LAP=.012
GAP=.00013
PATCH_CLEAR=.0006
if "--mount-probe" in sys.argv:
    for key,(grid,normals) in grids.items():
        spots=[]
        for row in range(2,len(grid)-2):
            for col in range(4,grid.shape[1]-4,2):
                p=Vector(grid[row,col])
                if not .046<p.xy.length<.090 or p.z<-.111 or abs(normals[row,col,2])<.30:
                    continue
                hits=[band for band,tree in trees.items()
                      if tree.ray_cast(p+UP*.008,UP,-p.z-.008)[0] is not None]
                if hits:
                    continue
                if min(abs(row-s) for s in divisions[key])<2:
                    continue
                spots.append((p.xy.length,row,col,p))
        chosen=[]
        for item in sorted(spots):
            if any((item[-1]-x[-1]).length<.024 for x in chosen):
                continue
            chosen.append(item)
        print("MOUNT OPTIONS",key,[(r,c,[round(v*1000,1) for v in p]) for _,r,c,p in chosen[:14]],flush=True)
    sys.exit(0)
MOUNT_POINTS={key:[] for key in grids}
STACKS=[]
for row,col in ((46,6),(50,6)):
    c=Vector(grids["C"][0][row,col])
    a,_,_,_=trees["A"].ray_cast(c+UP*.002,UP,.076)
    if a is None:
        raise RuntimeError("Centre C/A shared seat missed")
    MOUNT_POINTS["A"].append(a)
    MOUNT_POINTS["C"].append(c)
    STACKS.append((c.xy,("A","C")))
for target in ((-.028,-.079),(-.072,-.032)):
    choices=[]
    for row in range(82,115):
        for col in range(4,grids["B"][0].shape[1]-4,2):
            p=Vector(grids["B"][0][row,col])
            if not .065<p.xy.length<.094 or (p.xy-Vector(target)).length>.035:
                continue
            if any((p.xy-xy).length<.025 for xy,_ in STACKS):
                continue
            fits=True
            for i in range(16):
                a=i*math.tau/16
                q=Vector((p.x+.0068*math.cos(a),p.y+.0068*math.sin(a),.001))
                h,normal,_,_=trees["B"].ray_cast(q,-UP,.120)
                if h is None or abs(normal.z)<.32 or abs(h.z-p.z)>.011:
                    fits=False
                    break
            if fits:
                choices.append(((p.xy-Vector(target)).length,p))
    if not choices:
        raise RuntimeError(f"No centre B land near {target}")
    b=min(choices,key=lambda item:item[0])[1]
    MOUNT_POINTS["B"].append(b)
    STACKS.append((b.xy,("B",)))

panel_records=[]
exports=[]
panels={}
root_seats=[]
contact_records=[]
contacts={key:[] for key in grids}

def row_at(grid,row):
    pos=row%(len(grid)-1)
    index=math.floor(pos)
    f=pos-index
    return grid[index]*(1-f)+grid[index+1]*f

def arc_distances(grid):
    middle=grid[:,grid.shape[1]//2]
    length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(middle,axis=0),axis=1))]
    span=len(grid)-1
    rows=np.arange(3*span+1)-span
    arc=np.r_[length[:-1]-length[-1], length[:-1], length+length[-1]]
    return rows,arc

def sample_positions(start,end):
    return [start,*range(math.floor(start)+1,math.ceil(end)),end]

def find_integral_land(lower,upper,centre):
    grid,normals=grids[lower]
    candidates=[]
    for row in range(1,len(grid)-1):
        for col in range(6,grid.shape[1]-6,2):
            p=Vector(grid[row,col])
            if (p.xy-Vector(centre)).length>.070 or abs(normals[row,col,2])<.42:
                continue
            seams=divisions[lower]
            if min((Vector(grid[s,grid.shape[1]//2])-Vector(grid[row,grid.shape[1]//2])).length
                   for s in seams)<.020:
                continue
            # A solid hidden overlap must surround the complete mating land.
            heights=[]
            for dx,dy in ((0,0),(-.008,0),(.008,0),(0,.007),(0,-.007),
                          (-.006,-.005),(-.006,.005),(.006,-.005),(.006,.005)):
                x,y=p.x+dx,p.y+dy
                start=Vector((x,y,p.z-.024))
                lo,n,_,_=trees[lower].ray_cast(start,UP,.048)
                if lo is None or abs(n.z)<.32:
                    break
                hit,n,_,distance=trees[upper].ray_cast(lo+UP*.003,UP,.040)
                if hit is None or abs(n.z)<.30:
                    break
                heights.append((hit-lo).z)
            if len(heights)==9:
                score=max(heights)+.15*(p.xy-Vector(centre)).length
                candidates.append((score,p))
    if not candidates:
        raise RuntimeError(f"No integral contact region {lower} to {upper}")
    return min(candidates,key=lambda item:item[0])[1]

# Each local contact is built into the lower ribbon's own rear wall.
for lo,hi,where in (("A","B",(-.49,-.10)),("C","A",(-.37,.137))):
    p=find_integral_land(lo,hi,where)
    contacts[lo].append((hi,p))
    contact_records.append(dict(lower=lo,upper=hi,xy_mm=[round(v*1000,1) for v in p.xy],
                                nominal_clearance_mm=PATCH_CLEAR*1000))
    print("INTEGRAL LAND",lo,hi,tuple(round(v*1000,1) for v in p),flush=True)

def contour_for(key,first,last):
    grid,normals=grids[key]
    span=len(grid)-1
    rows,arc=arc_distances(grid)
    s_arc,e_arc=np.interp([first,last],rows,arc)
    if last+8>rows[-1]:
        rows=np.r_[rows,np.arange(rows[-1]+1,rows[-1]+span+1)]
        arc=np.r_[arc,arc[-1]+arc[1:span+1]-arc[0]]
    def t(length):
        return float(np.interp(length,arc,rows))
    def sign(row):
        return 1 if float(row_at(normals,row)[len(normals[0])//2,2])>0 else -1
    sign1,sign2=sign(first),sign(last)
    a=t(s_arc+GAP)
    b=t(s_arc+LAP+GAP)
    c=t(e_arc-GAP)
    d=t(e_arc+LAP-GAP)
    front1=.00038-GAP
    back2=.00038+GAP
    outer=.003
    sections=((a,b,-outer if sign1>0 else -front1,front1 if sign1>0 else outer),
              (b,c,-outer,outer),
              (c,d,back2 if sign2>0 else -outer,outer if sign2>0 else -back2))
    return sections,(sign1,sign2), (s_arc,e_arc)


def root_weight(radius):
    v=np.clip((1-radius)/.36,0,1)
    return v*v*(3-2*v)

def lap_mesh(name,key,start,end):
    grid,normals=grids[key]
    sections,senses,seam_arc=contour_for(key,start,end)
    width=grid.shape[1]
    arc_rows,arc=arc_distances(grid)
    mount_locations=MOUNT_POINTS[key]
    verts=[]
    faces=[]
    rows={}

    def grid_row(row,offset):
        address=(row,offset)
        if address in rows:
            return rows[address]
        line=row_at(grid,row)
        direction=row_at(normals,row)
        distance=np.interp(row,arc_rows,arc)
        seam=int(abs(distance-seam_arc[1])<abs(distance-seam_arc[0]))
        sense=senses[seam]
        local=distance-seam_arc[seam]
        taper=max(0,min(1,(.030-abs(local-.005))/.013))
        outer=abs(offset)>.002
        gain=.00093*taper if outer and sense*offset>0 else 0
        depth=math.copysign(BASE,offset) if outer else offset
        coords=line+direction*(depth+sense*gain)
        if outer:
            for col,point in enumerate(coords):
                if depth*direction[col,2]<=0:
                    continue
                pos=Vector(point)
                for m in mount_locations:
                    r=((pos.x-m.x)/.013)**2+((pos.y-m.y)/.012)**2
                    if r<1:
                        coords[col,2]+=.0055*root_weight(math.sqrt(r))
                for upper,p in contacts[key]:
                    r=((pos.x-p.x)/.013)**2+((pos.y-p.y)/.010)**2
                    if r>=1:
                        continue
                    hit,_,_,_=trees[upper].ray_cast(Vector(coords[col])+UP*.001,UP,.050)
                    if hit is not None:
                        coords[col,2]+=root_weight(math.sqrt(r))*max(0,hit.z-PATCH_CLEAR-coords[col,2])
        result=len(verts)
        verts.extend(coords.tolist())
        rows[address]=result
        return result

    def face_between(a,b):
        for col in range(width-1):
            faces.append((a+col,a+col+1,b+col+1,b+col))

    for k,(first,last,lo,hi) in enumerate(sections):
        positions=sample_positions(first,last)
        for left,right in zip(positions,positions[1:]):
            face_between(grid_row(left,lo),grid_row(right,lo))
            face_between(grid_row(right,hi),grid_row(left,hi))
            before=sections[k-1][2:] if k and left==first else ()
            after=sections[k+1][2:] if k<len(sections)-1 and right==last else ()
            before=sorted(v for v in before if lo<v<hi)
            after=sorted(v for v in after if lo<v<hi)
            outline=[grid_row(left,lo),grid_row(right,lo),
                     *(grid_row(right,x) for x in after),grid_row(right,hi),grid_row(left,hi),
                     *(grid_row(left,x) for x in reversed(before))]
            for c in (0,width-1):
                indices=[i+c for i in outline]
                if len(indices)==4:
                    faces.append(tuple(indices))
                else:
                    centre=np.mean([verts[i] for i in indices],axis=0)
                    q=len(verts)
                    verts.append(centre.tolist())
                    faces.extend((q,a,b) for a,b in zip(indices,indices[1:]+indices[:1]))
        if k:
            _,_,prev_lo,prev_hi=sections[k-1]
            for old,new in ((prev_lo,lo),(prev_hi,hi)):
                if old!=new:
                    face_between(grid_row(first,old),grid_row(first,new))
        else:
            face_between(grid_row(first,hi),grid_row(first,lo))
        if k==len(sections)-1:
            face_between(grid_row(last,lo),grid_row(last,hi))
    obj=mesh_object(name,verts,faces,skins,paper)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), name
    bm.to_mesh(obj.data)
    bm.free()
    return obj

for key,cuts in divisions.items():
    grid,normals=grids[key]
    span=len(grid)-1
    start=cuts[0]
    unwrapped=[row if row>=start else row+span for row in cuts]+[start+span]
    for number,(s,e) in enumerate(zip(unwrapped,unwrapped[1:]),1):
        ident=f"{key}{number:02d}"
        obj=lap_mesh(ident+" · integral lap",key,s,e)
        obj["assembly_order"]=f"{key} {number} of {len(cuts)}"
        obj["join"]="Integral 12 mm half-lap. Mate to next panel on the bench."
        panels[ident]=obj
        panel_records.append(dict(id=ident,band=key,first=s%span,last=e%span,raw_start=s,raw_end=e))
    print("PANELS",key,len(cuts),flush=True)

if "--laps" in sys.argv:
    for name,obj in panels.items():
        t=bvh(obj)
        errors=nonadjacent_hits(obj,t)
        if errors:
            idx=[set(tri.vertices) for tri in obj.data.loop_triangles]
            points=[]
            for i,j in t.overlap(t):
                if i>=j or not idx[i].isdisjoint(idx[j]):
                    continue
                triangle=obj.data.loop_triangles[i]
                p=sum((obj.data.vertices[v].co for v in triangle.vertices),Vector())/3
                points.append(tuple(round(v*1000,1) for v in p))
            print("LAP SELF",name,errors,points[::max(1,len(points)//5)],flush=True)
    for (na,a),(nb,b) in combinations(panels.items(),2):
        n=len(bvh(a).overlap(bvh(b)))
        if n:
            print("LAP PAIR",na,nb,n,flush=True)
    sys.exit(0)

def object_hit(obj,x,y,z=.001,ray=-UP,limit=.220):
    return bvh(obj).ray_cast(Vector((x,y,z)),ray,limit)[0]

def seat_for(key,xy):
    for ident,obj in panels.items():
        if ident[0]!=key:
            continue
        hit=object_hit(obj,*xy)
        if hit is not None:
            return ident,hit
    raise RuntimeError(f"Missing centre seat on {key} at {list(xy)}")

ceiling_plate=annular("Only ceiling contact · Ø210 metal plate",
                      [(.105,0),(.105,-.004),(.072,-.004),(.072,0)],canopy,metal,144)

def sleeve(name,xy,lo,hi,outer=.0054,inner=.00235):
    if hi-lo<.001:
        return None
    obj=annular(name,[(outer,lo),(outer,hi),(inner,hi),(inner,lo)],canopy,metal,48)
    shift=Vector((*xy,0))
    for v in obj.data.vertices:
        v.co+=shift
    return obj

for number,(xy,stack) in enumerate(STACKS,1):
    if xy.length>.098:
        raise RuntimeError("Centre fastener outside the cover")
    if xy.length<.077:
        # Integral local metal lug on the inside edge of the ceiling ring.
        lug=cylinder(f"Canopy inner seat {number}",(*xy,-.003),.009,.004,canopy,metal,56)
    seats=[]
    for key in stack:
        ident,hit=seat_for(key,xy)
        part=panels[ident]
        rear=[]
        front=[]
        t=bvh(part)
        for radius in (.0024,.0037,.0052,.0058):
            for k in range(24):
                angle=k*math.tau/24
                x,y=xy.x+radius*math.cos(angle),xy.y+radius*math.sin(angle)
                high=t.ray_cast(Vector((x,y,.001)),-UP,.185)[0]
                low=t.ray_cast(Vector((x,y,-.210)),UP,.205)[0]
                if high is not None:
                    rear.append(high.z)
                if low is not None:
                    front.append(low.z)
        assert len(rear)==len(front)==96,(ident,"seat too close to edge")
        def cut_bore(facets,phase,triangulate):
            centre=Vector((*xy,0))
            if triangulate:
                bm=bmesh.new()
                bm.from_mesh(part.data)
                bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
                bm.to_mesh(part.data)
                bm.free()
            cutter=cylinder("Tool · centre bore",(*xy,hit.z-.003),.00225,.027,canopy,metal,facets)
            if phase:
                rotation=Matrix.Rotation(phase,3,"Z")
                for v in cutter.data.vertices:
                    v.co=centre+rotation@(v.co-centre)
            difference(part,cutter)
            bm=bmesh.new()
            bm.from_mesh(part.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000009)
            bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000005)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bm.to_mesh(part.data)
            bm.free()
        if ident=="A02":
            source=part.data.copy()
            for i,(facets,phase) in enumerate(((40,0),(48,.026),(32,.089),(64,.043))):
                if i:
                    old=part.data
                    part.data=source.copy()
                    bpy.data.meshes.remove(old)
                cut_bore(facets,phase,True)
                if not nonadjacent_hits(part,bvh(part)):
                    break
            bpy.data.meshes.remove(source)
        else:
            cut_bore(40,0,False)
        seats.append(dict(panel=ident,rear=max(rear),front=min(front)))
    upper=max(seats,key=lambda d:d["rear"])
    lowest=min(seats,key=lambda d:d["front"])
    sleeve(f"Centre collar {number} · upper standoff",xy,upper["rear"]+.0010,-.004)
    if len(seats)==2:
        sleeve(f"Centre collar {number} · stack spacer",xy,
               lowest["rear"]+.0004,upper["front"]-.0004)
    z0=lowest["front"]-.003
    cylinder(f"Centre collar {number} · M4 shank envelope",
             (*xy,(z0-.004)/2),.00195,-.004-z0,canopy,metal,32)
    cylinder(f"Centre collar {number} · recessed head envelope",
             (*xy,z0-.001),.0038,.002,canopy,metal,40)
    root_seats.append(dict(id=f"H{number}",xy_mm=[round(v*1000,1) for v in xy],
                           stack=[d["panel"] for d in seats]))
for azimuth in (15,135,255):
    a=math.radians(azimuth)
    x,y=.093*math.cos(a),.093*math.sin(a)
    cut=cylinder("Tool · ceiling clearance",(x,y,-.002),.0034,.014,canopy,metal,48)
    difference(ceiling_plate,cut)

# Flat centre face and integral blind receiver. Its whole fixture stays inside
# the projected centre disc, so the compact canopy is the only hardware volume.
def centre_cover():
    n=144
    profile=[(.103,-.122),(.103,-.109),(.100,-.109),(.100,-.119),
             (.015,-.119),(.015,-.102),(.0064,-.102),(.0064,-.117)]
    verts=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z)
           for r,z in profile for i in range(n)]
    faces=[(a*n+i,a*n+(i+1)%n,(a+1)*n+(i+1)%n,(a+1)*n+i)
           for a in range(len(profile)-1) for i in range(n)]
    faces.extend((tuple(reversed(range(n))),tuple(range(7*n,8*n))))
    obj=mesh_object("E01 · Plain removable centre face",verts,faces,canopy,ivory,False)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    return obj

cover=centre_cover()
cylinder("Centre cover threaded keeper envelope",(0,0,-.105),.0059,.022,canopy,metal,56)
cylinder("Centre keeper support",(0,0,-.081),.007,.029,canopy,metal,56)
box("24 V driver fit volume",(-.010,.012,-.069),(.058,.026,.018),canopy,metal)
box("Central parallel splitter",(0,-.018,-.074),(.029,.013,.010),lighting,ivory)

# All three emitters are upward-facing within the same opaque centre assembly.
# The lid of the canopy is also the visible baffle from below.
lights=[]
for number,azimuth in enumerate((0,120,240),1):
    a=math.radians(azimuth)
    radial=Vector((math.cos(a),math.sin(a),0))
    tangent=UP.cross(radial)
    centre=radial*.047-UP*.041
    axes=(tangent,-radial,UP)
    shields=[box(f"L{number} · central aluminum bed",centre,(.112,.015,.002),
                 lighting,metal,axes)]
    for side in (-1,1):
        shields.append(box(f"L{number} · recessed side wall",centre+radial*.007*side+UP*.005,
                           (.112,.002,.012),lighting,metal,axes))
        shields.append(box(f"L{number} · opaque end stop",centre+tangent*.055*side+UP*.005,
                           (.002,.013,.012),lighting,metal,axes))
    box(f"L{number} · 100 mm tape inside canopy",centre+UP*.0018,
        (.100,.008,.0016),lighting,tape,axes)
    proxy=light(f"L{number} · ceiling bounce proxy",centre+UP*.0027,centre+UP,
                3.1,(1,.70,.43),.100,lighting)
    proxy.data.shape="RECTANGLE"
    proxy.data.size_y=.008
    shield_trees=[bvh(obj) for obj in shields]
    ray_count=0
    for u in (-.049,-.025,0,.025,.049):
        for v in (-.0038,0,.0038):
            p=centre+tangent*u+radial*v+UP*.0027
            for tilt in (0,-10,-30,-60,-90):
                e=math.radians(tilt)
                for angle in range(0,360,10):
                    q=math.radians(angle)
                    direction=Vector((math.cos(q)*math.cos(e),math.sin(q)*math.cos(e),math.sin(e)))
                    assert not visible_from(p,direction,shield_trees)
                    ray_count+=1
    end=centre+tangent*.054
    wire_curve(f"L{number} · paired wire wholly inside centre",
               [Vector((0,-.018,-.074)),radial*.029-UP*.059,end-UP*.008,end+UP*.002],
               .0011,lighting,metal)
    lights.append(dict(id=f"L{number}",strip_mm=100,position_mm=[round(v*1000,1) for v in centre],
                       shielded_rays=ray_count))
# One compact metal sleeve screens the four central collar fasteners.
# The wall has close-fitting windows formed by the actual shade crossings.
def screened_canopy():
    count=168
    rings=34
    low,high=-.1085,-.017
    radii=(.0995,.1025)
    shade=[bvh(obj) for obj in panels.values()]
    active=set()
    def ring_angle(i):
        return math.tau*i/count
    for i in range(count):
        for j in range(rings):
            cut=False
            for fi in (-.22,.50,1.22):
                a=ring_angle(i+fi)
                d=Vector((math.cos(a),math.sin(a),0))
                for fj in (-1.15,0,.5,1,2.15):
                    z=low+(high-low)*(j+fj)/rings
                    p=d*(radii[0]-.006)+UP*z
                    if any(tree.ray_cast(p,d,.017)[0] is not None for tree in shade):
                        cut=True
                        break
                if cut:
                    break
            if not cut:
                active.add((i,j))
    vertices=[]
    faces=[]
    index={}
    def node(ri,i,j):
        i=i%count
        key=ri,i,j
        if key not in index:
            a=ring_angle(i)
            r=radii[ri]
            index[key]=len(vertices)
            vertices.append((r*math.cos(a),r*math.sin(a),low+(high-low)*j/rings))
        return index[key]
    for i,j in sorted(active):
        corners=((i,j),(i+1,j),(i+1,j+1),(i,j+1))
        faces.extend(tuple(node(ri,*k) for k in corners) for ri in (0,1))
        for a,b,neighbor in zip(corners,corners[1:]+corners[:1],
                                 ((i,j-1),((i+1)%count,j),(i,j+1),((i-1)%count,j))):
            if neighbor not in active:
                faces.append((node(0,*a),node(0,*b),node(1,*b),node(1,*a)))
    obj=mesh_object("Opaque centre sleeve · ribbon pass-throughs",vertices,faces,canopy,ivory,False)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    return obj
shroud=screened_canopy()

for obj in masters.values():
    bpy.data.objects.remove(obj,do_unlink=True)

def oriented_basis(obj,key,start,end):
    grid,_=grids[key]
    coords=np.array([list(v.co) for v in obj.data.vertices])
    frame_candidates=[]
    for row in (start,(start+end)//2,end-1):
        points=row_at(grid,row)
        centre=len(points)//2
        z=unit(row_at(grid,row+1)[centre]-points[centre])
        x=unit(points[-1]-points[0]-z*np.dot(points[-1]-points[0],z))
        y=np.cross(z,x)
        frame_candidates.append((x,y,z))
    best=None
    for x,y,z in frame_candidates:
        for pitch in (0,15,-15,30,-30,45,-45,60,-60):
            angle=math.radians(pitch)
            up=z*math.cos(angle)+y*math.sin(angle)
            right=np.cross(up,x)
            for yaw in range(0,91,9):
                angle=math.radians(yaw)
                span=x*math.cos(angle)+right*math.sin(angle)
                basis=np.stack((span,np.cross(up,span),up),axis=1)
                size=np.ptp(coords@basis,axis=0)
                if max(size)>.320:
                    continue
                score=max(size)+.0008*abs(pitch)+.007*bool(yaw)
                if best is None or score<best[0]:
                    best=(score,basis)
    if best is None:
        raise RuntimeError(f"No print orientation: {obj.name}")
    return best[1]

panel_trees={}
errors={}
for item in panel_records:
    name=item["id"]
    obj=panels[name]
    panel_trees[name],issues=solid_check(obj)
    if issues:
        errors[name]=issues
    record=write_stl(obj,name,oriented_basis(obj,item["band"],item["raw_start"],item["raw_end"]))
    exports.append(record)
exports.append(write_stl(cover,"E01-Centre-face"))
cover_tree,cover_self=solid_check(cover)
if cover_self:
    errors["E01"]=cover_self
printed_crossings={}
for (a,ta),(b,tb) in combinations([*panel_trees.items(),("E01",cover_tree)],2):
    hit=ta.overlap(tb)
    if hit:
        printed_crossings[f"{a}/{b}"]=len(hit)
hardware_crossings={}
for obj in [*canopy.objects,*lighting.objects]:
    if obj==cover or obj.type!="MESH":
        continue
    t=bvh(obj)
    for key,tree in panel_trees.items():
        count=len(t.overlap(tree))
        if count:
            hardware_crossings[f"{obj.name}/{key}"]=count
print("SELF CHECK",errors,flush=True)
print("PANEL CROSSINGS",printed_crossings,flush=True)
print("CANOPY CROSSINGS",hardware_crossings,flush=True)

ceiling_surface=box("Ceiling backdrop",(0,0,.012),(5,5,.024),studio,ceiling)
below=camera("01 · Directly below",(.002,.036,-2),1.57,direct=True)
side=camera("02 · Low ceiling side",(.50,-1.9,-.59),1.48,target=(0,.025,-.085))
other=camera("03 · Opposite low angle",(-.35,1.9,-.61),1.49,target=(0,.025,-.085))
scene.camera=below
fill=light("Neutral room fill",(-.36,-.23,-1.2),(0,0,-.06),6,(1,.87,.72),1.4)
scene.render.engine="CYCLES"
scene.cycles.samples=28
scene.cycles.use_denoising=True
scene.render.resolution_x=1200
scene.render.resolution_y=800
scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX"

extent_points=np.array([list(v.co) for obj in panels.values() for v in obj.data.vertices])
metadata=dict(dimensions_mm=[round(float(x*1000),1) for x in np.ptp(extent_points,axis=0)],
              ceiling_drop_mm=round(float(-extent_points[:,2].min()*1000),1),
              printed_parts=len(exports),shade_panels=len(panels),printed=exports,panels=panel_records,
              centre_seats=root_seats,inter_ribbon_contacts=contact_records,lap_length_mm=LAP*1000,
              nominal_seam_gap_mm=GAP*2000,nominal_skin_mm=BASE*2000,
              stations=lights,self_intersections=errors,panel_pair_intersections=printed_crossings,
              canopy_shade_intersections=hardware_crossings)
(OUT/"Build-map.json").write_text(json.dumps(metadata,indent=2)+"\n")
print("V10 SUMMARY",metadata["printed_parts"],metadata["dimensions_mm"],metadata["ceiling_drop_mm"],flush=True)

reference=bpy.data.images.load(str(ROOT/"prototype-v08/underside-reference.png"))
reference.name="User reference · supplied underside"
reference.use_fake_user=True
reference.pack()
text=bpy.data.texts.new("V10 editable trace and lap source")
text.write(Path(__file__).read_text())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            view=area.spaces.active
            view.overlay.show_overlays=False
            view.shading.color_type="MATERIAL"
            view.region_3d.view_location=(.002,.036,-.10)
            view.region_3d.view_distance=1.6
            view.region_3d.view_rotation=below.rotation_euler.to_quaternion()
            view.region_3d.view_perspective="ORTHO"
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Ribbon-Lamp-V10-Integral.blend"),compress=True)
if "--render" in sys.argv:
    for file,view in (("01-Below",below),("02-Low-side",side),("03-Opposite-low-side",other)):
        scene.camera=view
        scene.render.filepath=str(OUT/(file+".png"))
        bpy.ops.render.render(write_still=True)
