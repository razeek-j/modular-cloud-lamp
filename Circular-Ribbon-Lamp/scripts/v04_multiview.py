import bpy,math,json,bmesh,sys
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');revision='v04a' if '--v04a' in sys.argv else 'v04';s=bpy.context.scene;cam=bpy.data.objects['CAM 01 • warm ceiling view'];s.camera=cam;s.cycles.device='CPU';s.cycles.samples=12;s.render.resolution_percentage=100;s.render.resolution_x=600;s.render.resolution_y=420
coords=[];vol=0
for ob in bpy.data.collections['V04 01 • FLUSH CLOUD / actual surfaces'].objects:
 coords.extend([ob.matrix_world@v.co for v in ob.data.vertices]);bm=bmesh.new();bm.from_mesh(ob.data);vol+=abs(bm.calc_volume(signed=True))*abs(ob.matrix_world.determinant());bm.free()
p=R/f'checks/{revision}-report.json';d=json.loads(p.read_text())
if 'attachment_zones' in d:d['reference_v03_attachment_zones']=d.pop('attachment_zones')
if 'nominal_skin_mass_kg_at_1270kg_m3' in d:d['source_v03_skin_mass_kg']=d.pop('nominal_skin_mass_kg_at_1270kg_m3')
d['source_solidify_input_mm']=d.pop('skin_mm',d.get('source_solidify_input_mm',1.2));d['live_curve_modifiers']=False;d['hidden_v03_curve_masters_retained']=True
d['wall_note']='Evaluated transformed skins; final uniform manufacturing thickness remains to be established.'
d['nominal_current_skin_mass_kg_at_1270kg_m3']=vol*1270;d['bounds_mm']={'min':[min(v[j] for v in coords)*1000 for j in range(3)],'max':[max(v[j] for v in coords)*1000 for j in range(3)]};p.write_text(json.dumps(d,indent=2))
for o in bpy.data.objects:
 if o.type=='LIGHT':
  if 'preview only' in o.name:o.data.energy=0
  else:o.data.energy=40;o.data.color=(1,1,1)
s.view_settings.exposure=.2;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.3
for i in range(8):
 a=i*math.tau/8;cam.location=(2*math.cos(a),2*math.sin(a),-1);cam.rotation_euler=(Vector((0,0,-.1))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/{revision}-review-{i:02d}.png');bpy.ops.render.render(write_still=True)
