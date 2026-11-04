"""Update embedded handoff and clean viewport in the actual open V06b project."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
for title,path in [('V06B • source','scripts/build_v06b_surface_ripples.py'),('V06B • plan','PLAN.md'),('V06B • process journal','PROCESS.md'),('V06B • lighting study','lighting-v06/README.md')]:
 t=bpy.data.texts.get(title) or bpy.data.texts.new(title);t.clear();t.write((R/path).read_text())
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.name.startswith('Room daylight • review only'):o.name='Room daylight • review only'
s=bpy.context.scene;s['surface_direction']='User confirmed surface ripples. V06b: about 6 mm starting pitch, .5 mm source amplitude; no added wave pieces.';s['appearance_gate']='Surface correction implemented. Overall composition, visible deck/returns and lower-fold glow remain unresolved.';s['manufacturing_gate']='Not ready: historical overlap failed; V06b self-intersections, thickness, print fit, thermal and load validation outstanding.';s['process_media']='09 actual live script-driven build; 11 actual Blender-window-only live viewport review. No audio.'
if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   v=a.spaces.active;v.overlay.show_overlays=False;v.show_gizmo=False;v.shading.type='SOLID';v.shading.color_type='MATERIAL';v.shading.show_shadows=True;v.shading.show_cavity=True;v.shading.cavity_type='BOTH';v.region_3d.view_location=(0,0,-.14);v.region_3d.view_distance=1.45;v.region_3d.view_rotation=Vector((.3,-1.8,-.85)).to_track_quat('Z','Y');v.region_3d.view_perspective='ORTHO'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v06b-surface-ripples.blend'),compress=True)
