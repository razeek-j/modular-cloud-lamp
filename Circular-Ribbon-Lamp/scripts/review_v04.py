import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');revision='v04a' if '--v04a' in sys.argv else 'v04';s=bpy.context.scene;obs=list(bpy.data.collections['V04 01 • FLUSH CLOUD / actual surfaces'].objects);rows=[]
for o in obs:
 bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in remaining:remaining.remove(n);stack.append(n)
 rows.append(dict(name=o.name,components=components,non_manifold_edges=sum(not e.is_manifold for e in bm.edges),faces=len(bm.faces)));bm.free()
(R/f'checks/{revision}-mesh-check.json').write_text(json.dumps(rows,indent=2));print('MESH_CHECK',json.dumps(rows),flush=True)
s.cycles.device='CPU';s.cycles.samples=24;s.render.resolution_x=1050;s.render.resolution_y=750;s.render.resolution_percentage=100
s.camera=bpy.data.objects['CAM 01 • warm ceiling view'];s.camera.rotation_euler=(Vector((0,0,-.10))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/{revision}-flush-warm.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
 if o.type=='LIGHT':
  if 'preview only' in o.name:o.data.energy=0
  else:o.data.energy=40;o.data.color=(1,1,1)
s.view_settings.exposure=.2;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.3
s.camera=bpy.data.objects['CAM 02 • circular underside'];s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=str(R/f'renders/{revision}-flush-unlit.png');bpy.ops.render.render(write_still=True)
