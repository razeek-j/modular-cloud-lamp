import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');s=bpy.context.scene
s.cycles.device='CPU';s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
for o in bpy.data.objects:
 if o.type=='LIGHT' and 'COB equivalent' in o.name:o.data.energy=0
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.4;s.view_settings.exposure=0
next(o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith('Room daylight • review only')).data.energy=30
cam=bpy.data.objects['CAM • warm room view'];cam.location=(-.20,-1.05,-.37);target=Vector((-.10,-.40,-.15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=58;s.camera=cam
s.render.filepath=str(R/'renders/v06b-surface-ripple-detail.png');bpy.ops.render.render(write_still=True)
