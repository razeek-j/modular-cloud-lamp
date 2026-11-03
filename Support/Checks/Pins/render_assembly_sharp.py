import bpy, bmesh, math, sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path("/Users/razeek/Projects/3D printing")
OUT_CHECKS = ROOT / "Support" / "Checks" / "Pins"
sys.path.append(str(OUT_CHECKS))
import build_all_pins as bp

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'Lamp-taller-proposal.blend'))
s = bpy.data.scenes['01 • Complete lamp']
bpy.context.window.scene = s

theta = math.pi / 12
origin = Vector((125 * math.cos(theta), 125 * math.sin(theta), 38.81687))

pin = bp.build_bidirectional_snap_pin("Assembly_Pin")

radial = Vector((math.cos(theta), math.sin(theta), 0))
normal = Vector((-math.sin(theta), math.cos(theta), 0))
z_axis = Vector((0, 0, 1))

R = Matrix((
    (normal.x, radial.x, z_axis.x),
    (normal.y, radial.y, z_axis.y),
    (normal.z, radial.z, z_axis.z)
)).to_4x4()
T_shift = Matrix.Translation(Vector((0, 0, -2.3)))
T_world = Matrix.Translation(origin)
pin.matrix_world = T_world @ R @ T_shift

mat_pin = bpy.data.materials.new("Mat_Assembly_Pin")
mat_pin.diffuse_color = (0.1, 0.65, 0.95, 1.0)
pin.data.materials.append(mat_pin)

# Keep Segment 01 solid white, and make Segment 02 wireframe/transparent or hide outer shell
mat_shade1 = bpy.data.materials.new("Mat_Shade1")
mat_shade1.diffuse_color = (0.95, 0.95, 0.96, 1.0)
s.objects['LAMP_Full Segment 01'].data.materials.clear()
s.objects['LAMP_Full Segment 01'].data.materials.append(mat_shade1)

mat_shade2 = bpy.data.materials.new("Mat_Shade2")
mat_shade2.diffuse_color = (0.85, 0.85, 0.88, 1.0)
s.objects['LAMP_Full Segment 02'].data.materials.clear()
s.objects['LAMP_Full Segment 02'].data.materials.append(mat_shade2)

for o in s.objects:
    if o.name not in ['LAMP_Full Segment 01', 'LAMP_Full Segment 02', pin.name]:
        o.hide_render = True

s.render.engine = 'BLENDER_WORKBENCH'
s.render.resolution_x = 1600
s.render.resolution_y = 1000
d = s.display.shading
d.light = 'STUDIO'
d.color_type = 'MATERIAL'
d.show_shadows = True
d.show_cavity = True
d.cavity_type = 'BOTH'
d.curvature_ridge_factor = 1.6
d.curvature_valley_factor = 1.2

# Look from inside the shade looking towards the seam and bracket
# Origin is at radius 125, angle 15 deg.
# Inside is towards center (0, 0)
cam_pos = origin - radial * 28.0 + Vector((0, 0, 18.0)) + normal * 12.0
cam_data = bpy.data.cameras.new("Sharp_Camera")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 36.0
cam_obj = bpy.data.objects.new("Sharp_Camera", cam_data)
s.collection.objects.link(cam_obj)
cam_obj.location = cam_pos
cam_obj.rotation_euler = (origin - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()
s.camera = cam_obj

w = bpy.data.worlds.new('world_sharp')
w.color = (0.07, 0.08, 0.10)
s.world = w

out_img = OUT_CHECKS / "joint-assembly-sharp.png"
s.render.filepath = str(out_img)
bpy.ops.render.render(write_still=True)
print("Saved:", out_img.name)
