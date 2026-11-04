"""Script-driven live viewport review; changes viewing settings only, not physical supports."""
import bpy,math
from mathutils import Vector
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
areas=[a for a in bpy.context.screen.areas if a.type=='VIEW_3D']
for a in areas:
 v=a.spaces.active;v.overlay.show_overlays=False;v.show_gizmo=False;v.shading.type='SOLID';v.shading.light='STUDIO';v.shading.color_type='MATERIAL';v.shading.show_shadows=True;v.shading.show_cavity=True;v.shading.cavity_type='BOTH'
poses=[((0,0,-.14),1.6,(.30,-1.8,-.95)),((0,0,-.14),1.6,(-.65,-1.7,-.85)),((-.08,-.32,-.14),.70,(.12,-1.5,-.70)),((0,0,-.14),1.6,(.5,-1.8,-.75))]
index=0
def tick():
 global index
 if index>=len(poses):return None
 location,distance,direction=poses[index]
 for a in areas:
  v=a.spaces.active;v.region_3d.view_location=location;v.region_3d.view_distance=distance;v.region_3d.view_rotation=Vector(direction).to_track_quat('Z','Y');v.region_3d.view_perspective='ORTHO';a.tag_redraw()
 index+=1
 return 6 if index<len(poses) else None
tick();bpy.app.timers.register(tick,first_interval=6)
