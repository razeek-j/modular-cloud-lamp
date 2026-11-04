import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
for title,path in [('V07 • source','scripts/build_v07_centre_mount.py'),('V07 • plan','PLAN.md'),('V07 • process journal','PROCESS.md'),('V07 • carrier and lighting','lighting-v07/README.md')]:
 t=bpy.data.texts.get(title) or bpy.data.texts.new(title);t.clear();t.write((R/path).read_text())
s=bpy.context.scene;s['design_constraint']='Only the compact central Ø220 canopy attaches to the ceiling. No broad base, outer ceiling fixings or perimeter ceiling rail.';s['remaining_work']='Carrier/optical-cell concealment, fabrication/retention, physical load/thermal tests and print package remain unfinished.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   v=a.spaces.active;v.overlay.show_overlays=False;v.show_gizmo=False;v.shading.type='SOLID';v.shading.color_type='MATERIAL';v.shading.show_cavity=True;v.region_3d.view_location=(0,0,-.14);v.region_3d.view_distance=1.45;v.region_3d.view_rotation=Vector((.3,-1.8,-.85)).to_track_quat('Z','Y');v.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v07-centre-mount.blend'),compress=True)
