"""Build and verify a full-scale W01 seam/lighting bench test from the V07 master."""
import json
import math
import struct
import sys
from itertools import combinations
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[1]
out = root / "prototype-v08"
out.mkdir(exist_ok=True)
(out / "Models").mkdir(exist_ok=True)
master = bpy.context.scene
band = bpy.data.objects["W01 • main perimeter wave"]
source = band.data
rows, stride = 600, 193
assert len(source.vertices) == rows * stride
assert abs(band.modifiers[0].thickness - .0012) < 1e-7

# Choose a broad, low fold whose room-facing side is mostly underneath.
def vertex(row, col):
    return source.vertices[(row % rows) * stride + col]

def point(row, col):
    base = math.floor(row)
    return band.matrix_world @ vertex(base, col).co.lerp(vertex(base + 1, col).co, row - base)

def normal(row, col):
    base = math.floor(row)
    return (band.matrix_world.to_3x3().inverted().transposed()
            @ vertex(base, col).normal.lerp(vertex(base + 1, col).normal, row - base)).normalized()

def basis(row):
    across = point(row, 170) - point(row, 22)
    tangent = (point(row + 2, 96) - point(row - 2, 96)).normalized()
    up = tangent.cross(across).normalized()
    return tangent, up if up.z > 0 else -up

def score(row):
    near = (row - 18, row, row + 18)
    smoothness = min(basis(index)[1].z for index in near)
    depth = -point(row, 96).z
    return smoothness - 4 * abs(depth - .155)

seam = max(range(rows), key=score)
datum = point(seam, 96)
sign = 1 if normal(seam, 96).z > 0 else -1

def arc_limit(length, direction):
    distance = 0
    for offset in range(1, 100):
        current = seam + offset * direction
        distance += (point(current, 96) - point(current - direction, 96)).length
        if distance >= length:
            return current
    raise RuntimeError("Ribbon arc selection failed")

def offset_rows(start, end):
    return [start, *range(math.floor(start) + 1, math.ceil(end)), end]

step = (point(seam + 1, 96) - point(seam - 1, 96)).length / 2
half_gap = .0001 / step
start, end = arc_limit(.135, -1), arc_limit(.135, 1)
scene = bpy.data.scenes.new("V08 | Bench assembly")
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'MILLIMETERS'
bpy.context.window.scene = scene

def group(name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection

parts = group("01  PRINT · shade and rear splices")
hardware = group("02  BENCH · opaque metal channel and tape")
stage = group("03  REVIEW · cameras and bounce board")

def material(name, color, metal=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = .57
    return mat

paper = band.data.materials[0]
aluminum = material("V08 | Opaque aluminum / ivory outer finish", (.80, .77, .69), .55)
board_material = material("V08 | Matte white bounce board", (.83, .81, .76))
tape_material = material("V08 | COB tape envelope", (.88, .53, .15))

def shell(name, indices, columns, low, high, smooth=True):
    vertices = []
    for depth in (low, high):
        for row in indices:
            for col in columns:
                vertices.append(point(row, col) - datum + normal(row, col) * sign * depth)
    width, height = len(columns), len(indices)
    count = width * height
    faces = []
    for r in range(height - 1):
        for c in range(width - 1):
            i = r * width + c
            face = (i, i + width, i + width + 1, i + 1)
            faces.extend((face, tuple(index + count for index in reversed(face))))
    boundary = [*range(width), *range(2 * width - 1, count, width),
                *range(count - 2, count - width - 1, -1),
                *range(count - 2 * width, 0, -width)]
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        faces.append((a, b, b + count, a + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(edge.is_manifold and edge.is_contiguous for edge in bm.edges)
    unseen = set(bm.verts)
    pending = [unseen.pop()]
    while pending:
        for edge in pending.pop().link_edges:
            for v in edge.verts:
                if v in unseen:
                    unseen.remove(v)
                    pending.append(v)
    assert not unseen
    assert bm.calc_volume(signed=True) > 0
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    parts.objects.link(obj)
    mesh.materials.append(paper)
    if smooth:
        for poly in mesh.polygons[:len(faces) - len(boundary)]:
            poly.use_smooth = True
    return obj

a = shell("01 Ribbon A", offset_rows(start, seam - half_gap), range(stride), -.0006, .0006)
b = shell("02 Ribbon B", offset_rows(seam + half_gap, end), range(stride), -.0006, .0006)
# Matching backs follow the exact same ripple grid with a 0.15 mm nominal bond line.
splice_start, splice_end = arc_limit(.021, -1), arc_limit(.021, 1)
splices = [
    shell("03 Rear splice inner", offset_rows(splice_start, splice_end), range(24, 43), .00075, .00315),
    shell("04 Rear splice outer", offset_rows(splice_start, splice_end), range(150, 169), .00075, .00315),
]
tangent, up = basis(seam)
along = Vector((tangent.x, tangent.y, 0)).normalized()
across = Vector((-along.y, along.x, 0))
vertical = Vector((0, 0, 1))
channel_rotation = Matrix((along, across, vertical)).transposed().to_quaternion()
# Opaque trough opens toward the white board. The metal floor is also the tape's heat spreader.
channel_centre = Vector((0, 0, .035))

def box(name, position, size, collection, mat, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rotation
    obj.data.materials.append(mat)
    return obj

def channel(name, x, y, z, size, mat=aluminum):
    return box(name, channel_centre + along * x + across * y + vertical * z,
               size, hardware, mat, channel_rotation)

floor = channel("Aluminum floor / heat spreader · 120 × 24", 0, 0, 0, (.120, .024, .002))
shields = [floor]
for side in (-1, 1):
    shields.append(channel("Opaque side lip", 0, side * .011, .0055, (.120, .002, .011)))
    shields.append(channel("Opaque end cap", side * .059, 0, .0055, (.002, .020, .011)))
tape = channel("100 mm COB tape · faces the bounce board", 0, 0, .0018,
               (.100, .008, .0016), tape_material)
board_z = -datum.z
assert board_z > .055
board = box("White bounce board · at V07 ceiling datum", (0, 0, board_z + .006),
            (.550, .550, .012), stage, board_material)

def light(name, position, direction, energy, color, width, depth):
    data = bpy.data.lights.new(name, 'AREA')
    data.shape = 'RECTANGLE'
    data.size, data.size_y = width, depth
    data.energy, data.color = energy, color
    obj = bpy.data.objects.new(name, data)
    stage.objects.link(obj)
    obj.location = position
    obj.rotation_euler = Vector(direction).to_track_quat('-Z', 'Y').to_euler()
    return obj

led = light("100 mm upward optical proxy", channel_centre + vertical * .0027,
            (0, 0, 1), .224, (1, .57, .29), .100, .008)
fill = light("Unlit inspection fill", (0, -.22, -.35), (0, .22, .35),
             4.0, (1, .92, .80), .38, .25)

def camera(name, position, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    obj = bpy.data.objects.new(name, data)
    stage.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    return obj

under = camera("01 · Room side", across * .18 + along * .085 - vertical * .41, (0, 0, .015), .410)
rear = camera("02 · Rear joint and lighting", across * .28 - along * .15 + vertical * .31, (0, 0, .023), .415)
scene.camera = under
scene.world = bpy.data.worlds.new("V08 | Neutral ambient")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.36, .34, .31, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .065
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1000, 760
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene["purpose"] = "Full-scale optical and seam bench test. V07 full fixture is the separate original scene."

def tree(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                [tuple(t.vertices) for t in obj.data.loop_triangles],
                                all_triangles=True, epsilon=0)

bpy.context.view_layer.update()
print_objects = [a, b, *splices]
trees = {o: tree(o) for o in [*print_objects, *shields, tape]}
for part in print_objects:
    vertex_ids = [set(triangle.vertices) for triangle in part.data.loop_triangles]
    intersections = [(i, j) for i, j in trees[part].overlap(trees[part])
                     if i < j and vertex_ids[i].isdisjoint(vertex_ids[j])]
    assert not intersections, (part.name, len(intersections))
for first, second in combinations(print_objects, 2):
    assert not trees[first].overlap(trees[second]), (first.name, second.name)
for part in print_objects:
    for item in [*shields, tape]:
        assert not trees[part].overlap(trees[item]), (part.name, item.name)

# Sample straight sightlines from the emitter to the hemisphere at/below its plane.
# This ignores the shade on purpose, isolating the opaque trough's contribution.
ray_count = 0
for x in (-.049, -.025, 0, .025, .049):
    for y in (-.0039, 0, .0039):
        origin = channel_centre + along * x + across * y + vertical * .0027
        for elevation in (0, -5, -15, -30, -45, -60, -75, -90):
            e = math.radians(elevation)
            for azimuth in range(0, 360, 5):
                angle = math.radians(azimuth)
                direction = Vector((math.cos(angle) * math.cos(e),
                                    math.sin(angle) * math.cos(e), math.sin(e)))
                assert any(trees[shield].ray_cast(origin, direction, .5)[0] is not None
                           for shield in shields), (x, y, elevation, azimuth)
                ray_count += 1

def export_stl(obj, print_z, print_x):
    print_x = (print_x - print_z * print_z.dot(print_x)).normalized()
    print_y = print_z.cross(print_x)
    coords = [Vector((v.co.dot(print_x), v.co.dot(print_y), v.co.dot(print_z))) * 1000
              for v in obj.data.vertices]
    low = Vector(tuple(min(v[axis] for v in coords) for axis in range(3)))
    high = Vector(tuple(max(v[axis] for v in coords) for axis in range(3)))
    size = high - low
    shift = Vector(((high.x + low.x) / 2, (high.y + low.y) / 2, low.z))
    coords = [v - shift for v in coords]
    assert max(size) < 320
    filename = obj.name.replace(' ', '_') + '.stl'
    triangles = obj.data.loop_triangles
    with (out / "Models" / filename).open('wb') as file:
        file.write(b'V08 bench prototype | millimetres'.ljust(80, b'\0'))
        file.write(struct.pack('<I', len(triangles)))
        for tri in triangles:
            p, q, r = (coords[index] for index in tri.vertices)
            n = (q - p).cross(r - p).normalized()
            file.write(struct.pack('<12fH', *n, *p, *q, *r, 0))
    return dict(file=filename, extents_mm=[round(value, 2) for value in size],
                triangles=len(triangles))

# Stand both skins on their cut ends to keep most of the broad face clear.
exports = [export_stl(a, basis(seam)[0] * -1, across),
           export_stl(b, basis(seam)[0], across)]
exports.extend(export_stl(obj, normal(seam, col) * sign, tangent)
               for obj, col in zip(splices, (33, 159)))
report = dict(seam_row=seam, arc_rows=[start, end], nominal_seam_gap_mm=.2,
              splice_bond_line_mm=.15, wall_mm=1.2, splice_wall_mm=2.4,
              tape_to_bounce_board_mm=round((board_z - .0377) * 1000, 1),
              sampled_direct_source_rays_blocked=ray_count,
              checked_pairwise_intersections=0, non_adjacent_self_intersections=0,
              exports=exports)
(out / "geometry-check.json").write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)

# Keep the original fixture and the new reference accessible in this editable copy.
master.name = "V07 | Full fixture context"
sys.path.insert(0, str(root / "scripts"))
from plan_v08_cuts import plan_cuts
cut_map = plan_cuts(master, out)
print(f"Draft full-shade cut map: {cut_map['part_count']} pieces", flush=True)
reference_path = out / "underside-reference.png"
if reference_path.exists():
    reference = bpy.data.images.load(str(reference_path), check_existing=True)
    reference.name = "Reference | requested underside view"
    reference.pack()
    reference.use_fake_user = True
text = bpy.data.texts.new("V08 | Build source")
text.write(Path(__file__).read_text())
cut_source = bpy.data.texts.new("V08 | Cut planning source")
cut_source.write((root / "scripts" / "plan_v08_cuts.py").read_text())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            view = area.spaces.active
            view.overlay.show_overlays = False
            view.shading.color_type = 'MATERIAL'
            view.region_3d.view_location = (0, 0, .020)
            view.region_3d.view_distance = .48
            view.region_3d.view_rotation = rear.rotation_euler.to_quaternion()
            view.region_3d.view_perspective = 'ORTHO'
bpy.ops.object.select_all(action='DESELECT')
# Hide only the removable bench board in the working viewport for access from above.
board.hide_set(True)
fill.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / "Ribbon-V08-fold-prototype.blend"), compress=True)

if '--render' in sys.argv:
    for name, view, board_visible, lit in (
        ("v08-bounce-room-side", under, True, True),
        ("v08-rear-assembly", rear, False, False),
    ):
        scene.camera = view
        board.hide_render = not board_visible
        led.hide_render = not lit
        fill.hide_render = lit
        scene.render.filepath = str(out / (name + ".png"))
        bpy.ops.render.render(write_still=True)
