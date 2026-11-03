"""Render clean presentation images of the pin models and assembly."""
import bpy, bmesh, math, sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path("/Users/razeek/Projects/3D printing")
OUT_CHECKS = ROOT / "Support" / "Checks" / "Pins"
sys.path.append(str(OUT_CHECKS))
import build_all_pins as bp

def setup_render_scene(width=1600, height=900):
    bp.reset()
    s = bpy.context.scene
    s.render.engine = 'BLENDER_WORKBENCH'
    s.render.resolution_x = width
    s.render.resolution_y = height
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    
    d = s.display.shading
    d.light = 'STUDIO'
    d.color_type = 'MATERIAL'
    d.show_shadows = True
    d.show_cavity = True
    d.cavity_type = 'BOTH'
    d.curvature_ridge_factor = 1.4
    d.curvature_valley_factor = 1.0
    d.background_type = 'WORLD'
    
    w = bpy.data.worlds.new('pin_world')
    w.color = (0.08, 0.09, 0.11)
    s.world = w
    return s

def add_camera(pos, target, ortho_scale=50.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(pos)
    direction = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_obj
    return cam_obj

def make_mat(name, color, roughness=0.3):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = roughness
    return m

def render_overview():
    s = setup_render_scene(1600, 900)
    
    # 1. BiDirectional Pin
    p1 = bp.build_bidirectional_snap_pin("Pin_BiDir")
    p1.location = Vector((-28.0, 0, 0))
    p1.rotation_euler = (math.radians(35), math.radians(15), math.radians(-30))
    m1 = make_mat("Mat_BiDir", (0.2, 0.65, 0.95)) # Vibrant Blue
    p1.data.materials.append(m1)
    
    # 2. Two-Piece Socket & Latch
    fem = bp.build_two_piece_female("Fem_Sock")
    male = bp.build_two_piece_male("Male_Latch")
    fem.location = Vector((-4.0, 0, 0))
    male.location = Vector((10.0, 0, 0))
    fem.rotation_euler = (math.radians(35), math.radians(15), math.radians(-30))
    male.rotation_euler = (math.radians(35), math.radians(15), math.radians(-30))
    m_fem = make_mat("Mat_Fem", (0.95, 0.5, 0.15)) # Orange
    m_male = make_mat("Mat_Male", (0.95, 0.75, 0.15)) # Amber Gold
    fem.data.materials.append(m_fem)
    male.data.materials.append(m_male)
    
    # 3. Alignment Dowel
    dow = bp.build_alignment_dowel("Pin_Dowel")
    dow.location = Vector((30.0, 0, 0))
    dow.rotation_euler = (math.radians(35), math.radians(15), math.radians(-30))
    m_dow = make_mat("Mat_Dow", (0.25, 0.8, 0.5)) # Mint Green
    dow.data.materials.append(m_dow)
    
    add_camera((60, -90, 75), (5, 0, 0), ortho_scale=80.0)
    
    out_img = OUT_CHECKS / "pin-designs-overview.png"
    s.render.filepath = str(out_img)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered overview: {out_img.name}")

def render_joint_cutaway():
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
    mat_pin.diffuse_color = (0.2, 0.65, 0.95, 1.0)
    pin.data.materials.append(mat_pin)
    
    # Hide other objects
    for o in s.objects:
        if o.name not in ['LAMP_Full Segment 01', 'LAMP_Full Segment 02', pin.name]:
            o.hide_render = True
            
    mat_shade = bpy.data.materials.new("Mat_Shade")
    mat_shade.diffuse_color = (0.92, 0.92, 0.92, 0.6)
    for seg_name in ['LAMP_Full Segment 01', 'LAMP_Full Segment 02']:
        o = s.objects[seg_name]
        o.data.materials.clear()
        o.data.materials.append(mat_shade)
        
    s.render.engine = 'BLENDER_WORKBENCH'
    s.render.resolution_x = 1600
    s.render.resolution_y = 1000
    d = s.display.shading
    d.light = 'STUDIO'
    d.color_type = 'MATERIAL'
    d.show_shadows = True
    d.show_cavity = True
    d.cavity_type = 'BOTH'
    d.curvature_ridge_factor = 1.4
    d.curvature_valley_factor = 1.0
    
    # Position camera inside looking at the bracket joint
    # The brackets are at radius 125, inside looking outwards
    cam_pos = origin + Vector((-35, -25, 20))
    add_camera(cam_pos, origin, ortho_scale=40.0)
    
    out_img = OUT_CHECKS / "joint-assembly-preview.png"
    s.render.filepath = str(out_img)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered joint assembly: {out_img.name}")

if __name__ == '__main__':
    render_overview()
    render_joint_cutaway()
