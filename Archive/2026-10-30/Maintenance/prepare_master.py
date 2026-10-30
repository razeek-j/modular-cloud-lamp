import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('/Users/razeek/Projects/3D printing')
source=root/'lamp-thin-carrier-v09.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
rename={'02 • Full 360 Assembly':'01 • Complete lamp','01 • Cutaway View (Inside Visible)':'02 • Shade inspection','03 • Carrier, Stand and LED Strip Only':'03 • Stand and LED carrier','04 • V09 thin carrier detail':'04 • Thin carrier detail'}
for a,b in rename.items():bpy.data.scenes[a].name=b
if bpy.data.scenes.get('Scene') and not bpy.data.scenes['Scene'].objects:bpy.data.scenes.remove(bpy.data.scenes['Scene'])
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
assert sum(o.type=='MESH' and 'Segment' in o.name for o in s.objects)==12
assert all(s.objects.get(n) for n in ['LAMP_Full Carrier','LAMP_Full Stand','LAMP_Full LED strip'])
assert len({o.data.as_pointer() for o in bpy.data.objects if o.type=='MESH' and o.data.name.startswith('LAMP V09 thin carrier')})==1
for o in s.objects:o.select_set(False)
rotation=(Vector((0,0,-25))-Vector((440,-550,290))).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=(0,0,-25)
   area.spaces.active.region_3d.view_distance=470
   area.spaces.active.region_3d.view_rotation=rotation
   area.spaces.active.region_3d.view_perspective='ORTHO'
   area.spaces.active.shading.color_type='MATERIAL'
   area.spaces.active.overlay.show_overlays=False
note=bpy.data.texts.new('START HERE - Lamp')
note.write('Working file: Lamp.blend\nAll lamp components are stored in this file; no external linked libraries.\nScenes: complete assembly; shade inspection; stand and carrier; thin carrier detail.\nLatest carrier: 0.8 mm wall, narrow bottom glue rim, backed 2 mm-deep cable channel.\nKnown unresolved issue: three stand leg roots intersect the shade. This is a draft, not yet print-ready.\nDimensions are photo-derived estimates; real clip, wiring and print clearances need testing.\n')
assert len(bpy.data.libraries)==0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Lamp.blend'))
report={'master':'Lamp.blend','scenes':{sc.name:[o.name for o in sc.objects if o.type=='MESH'] for sc in bpy.data.scenes},'external_libraries':len(bpy.data.libraries),'source':'lamp-thin-carrier-v09.blend','geometry_changed':False}
(root/'Support/master-inventory.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
