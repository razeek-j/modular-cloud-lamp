"""Room render of the Voronoi Moon: disc 40 mm below the ceiling, hidden up-light ring = floating halo.
Run after build_moon_concept.py:  Blender -b --python scripts/render_halo_room.py"""
import bpy, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = "MILLIMETERS"
R, GAP, DEPTH, CEIL = 450, 40, 45, 2700

def mat(name, color=None, emit=None, img=None, strength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    if img:
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1/(2*R), -1/(2*R), 1); mp.inputs["Location"].default_value = (0.5, 0.5, 0)
        ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(img); ti.extension = "CLIP"
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs[1].default_value = strength
        nt.links.new(tc.outputs["Object"], mp.inputs[0]); nt.links.new(mp.outputs[0], ti.inputs[0])
        nt.links.new(ti.outputs[0], e.inputs[0]); nt.links.new(e.outputs[0], o.inputs[0])
    elif emit:
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (*emit, 1); e.inputs[1].default_value = strength
        nt.links.new(e.outputs[0], o.inputs[0])
    else:
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Roughness"].default_value = 0.9; nt.links.new(b.outputs[0], o.inputs[0])
    return m

# room 5 x 4 m
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, CEIL)); c = bpy.context.object; c.scale = (5000, 4000, 1)
c.data.materials.append(mat("Ceiling", (0.82, 0.8, 0.77)))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2000, CEIL/2), rotation=(math.pi/2, 0, 0)); w = bpy.context.object; w.scale = (5000, CEIL, 1)
w.data.materials.append(mat("Wall", (0.55, 0.5, 0.45)))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); f = bpy.context.object; f.scale = (5000, 4000, 1)
f.data.materials.append(mat("Floor", (0.25, 0.18, 0.13)))

# disc body
zb = CEIL - GAP - DEPTH
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=R, depth=DEPTH, location=(0, 0, zb + DEPTH/2))
body = bpy.context.object; body.data.materials.append(mat("Rim", (0.9, 0.9, 0.88)))
# glowing moon face, a hair below the body
bpy.ops.mesh.primitive_circle_add(vertices=256, radius=R - 0.5, fill_type="NGON", location=(0, 0, zb - 0.3))
face = bpy.context.object
face.data.materials.append(mat("Moon", img=os.path.join(OUT, "renders", "02-moon-on.png"), strength=2.2))
# hidden halo ring on top of the disc, emitting toward the ceiling
bpy.ops.mesh.primitive_torus_add(major_radius=R - 40, minor_radius=4, location=(0, 0, zb + DEPTH + 8))
halo = bpy.context.object; halo.data.materials.append(mat("Halo", emit=(1.0, 0.78, 0.5), strength=120))
# central mount stem (hidden)
bpy.ops.mesh.primitive_cylinder_add(radius=60, depth=GAP, location=(0, 0, CEIL - GAP/2))
bpy.context.object.data.materials.append(mat("Mount", (0.85, 0.85, 0.85)))

cam = bpy.data.cameras.new("cam"); cam.lens = 24; cam.clip_start = 10; cam.clip_end = 20000
co = bpy.data.objects.new("Cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (-1500, -2600, 1500)
d = (0 - co.location[0], 0 - co.location[1], zb - co.location[2])
import mathutils
co.rotation_euler = mathutils.Vector(d).to_track_quat("-Z", "Y").to_euler()

wd = bpy.data.worlds.new("w"); wd.use_nodes = True; wd.node_tree.nodes["Background"].inputs[0].default_value = (0.003, 0.003, 0.005, 1)
sc.world = wd
sc.render.engine = "CYCLES"; sc.cycles.samples = 96; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = 0.0
sc.render.filepath = os.path.join(OUT, "renders", "04-halo-room.png")
bpy.ops.render.render(write_still=True)

# ---- make the saved .blend friendly to open in Blender (render above is unaffected) ----
from mathutils import Matrix, Vector
names = {"Circle": "Moon-Face", "Cylinder": "Disc-Body", "Cylinder.001": "Ceiling-Mount", "Torus": "Halo-LED-Ring",
         "Plane": "Room-Ceiling", "Plane.001": "Room-Wall", "Plane.002": "Room-Floor", "Cam": "Render-Camera"}
for old_n, new_n in names.items():
    if old_n in bpy.data.objects: bpy.data.objects[old_n].name = new_n
# 1. metres: 1 Blender unit = 1 m, still displayed in mm. Blender's default view range/zoom then just work.
S = 0.001
for ob in bpy.data.objects:
    if ob.type == "MESH":
        ob.data.transform(Matrix.Scale(S, 4) @ ob.matrix_world); ob.matrix_world = Matrix.Identity(4)
    else:
        ob.location = ob.location * S
if co.data: co.data.clip_start *= S; co.data.clip_end *= S
sc.unit_settings.scale_length = 1.0; sc.unit_settings.length_unit = "MILLIMETERS"
for n in bpy.data.materials["Moon"].node_tree.nodes:      # moon picture must follow the new size
    if n.type == "MAPPING": n.inputs["Scale"].default_value = (1/(2*R*S), -1/(2*R*S), 1)
# 2. room lives in its own collection, hidden in the viewport but still rendered
room = bpy.data.collections.new("Room"); sc.collection.children.link(room)
for n in ("Room-Ceiling", "Room-Wall", "Room-Floor"):
    ob = bpy.data.objects[n]
    for c in list(ob.users_collection): c.objects.unlink(ob)
    room.objects.link(ob)
bpy.context.view_layer.layer_collection.children["Room"].hide_viewport = True
# 3. open in Material Preview, looking up at the lamp from a corner of the room
target = Vector((0, 0, (CEIL - GAP - DEPTH/2) * S)); eye = Vector((-1.6, -2.2, 1.2))
for screen in bpy.data.screens:
    for area in screen.areas:
        for sp in area.spaces:
            if sp.type == "VIEW_3D":
                sp.shading.type = "MATERIAL"
                r = sp.region_3d; r.view_perspective = "PERSP"; r.view_location = target
                r.view_distance = (target - eye).length; r.view_rotation = (eye - target).to_track_quat("Z", "Y")   # viewport looks along its -Z from the eye
for img in bpy.data.images:                      # moon picture travels inside the .blend
    if img.source == "FILE" and not img.packed_file: img.pack()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Voronoi-Moon-v02.blend"))
