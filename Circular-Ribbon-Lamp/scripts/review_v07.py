import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');s=bpy.context.scene;s.cycles.samples=20;s.cycles.device='CPU';s.render.resolution_x=1050;s.render.resolution_y=720;s.render.resolution_percentage=100
cam=bpy.data.objects['CAM • warm room view'];s.camera=cam
s.render.filepath=str(R/'renders/v07-centre-warm.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
 if o.type=='LIGHT' and 'COB equivalent' in o.name:o.data.energy=0
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.45;s.view_settings.exposure=0
next(o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith('Room daylight')).data.energy=30
s.render.filepath=str(R/'renders/v07-centre-unlit.png');bpy.ops.render.render(write_still=True)
cam.data.type='ORTHO';cam.data.ortho_scale=1.4;cam.location=(0,0,-2);cam.rotation_euler=(Vector((0,0,-.13))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/v07-centre-below.png');bpy.ops.render.render(write_still=True)
# Technical cutaway explicitly omits skins and ceiling to explain the central load route.
for o in bpy.data.objects:
 if o.name.startswith(('W01','W02','W03','W04','W05','W06','Ceiling backdrop')) and o.type=='MESH':o.hide_render=True
cam.data.ortho_scale=1.15;cam.location=(.9,-1,1.3);cam.rotation_euler=(Vector((0,0,-.12))-cam.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.lights.new('Cutaway studio','AREA');d.energy=80;d.size=2;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(0,-.5,1.8);o.rotation_euler=(Vector((0,0,-.1))-o.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/v07-centre-carrier-cutaway.png');bpy.ops.render.render(write_still=True)
