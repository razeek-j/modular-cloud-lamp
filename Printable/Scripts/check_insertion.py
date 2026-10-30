import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
shade=[o for o in s.objects if 'Segment' in o.name and o.type=='MESH'];carrier=s.objects['LAMP_Full Carrier'];stand=s.objects['LAMP_Full Stand']
def tree(o,dz=0):return BVHTree.FromPolygons([o.matrix_world@v.co+Vector((0,0,dz)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
shade_trees={o.name:tree(o) for o in shade};r={}
for obj in [carrier,stand]:
 result=[]
 for dz in range(-100,1,2):
  tr=tree(obj,dz);hits={name:len(tr.overlap(st)) for name,st in shade_trees.items()};hits={k:v for k,v in hits.items() if v}
  if hits:result.append({'offset_z_mm':dz,'surface_pairs':hits})
 r[obj.name]={'sampled_from_below_mm':[-100,0],'step_mm':2,'colliding_samples':result}
(OUT/'Checks/insertion-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
