import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get()
obs=sorted(list(bpy.data.collections['V05 01 • LARGE ROLLED WAVES'].objects)+list(bpy.data.collections['V05 02 • IN-BETWEEN WAVES'].objects),key=lambda o:o.name)
data=[]
for ob in obs:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();data.append(([ob.matrix_world@v.co if len(data)<3 else v.co.copy() for v in me.vertices],[list(t.vertices) for t in me.loop_triangles]));ev.to_mesh_clear()
trees=[BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0) for v,f in data[:3]]
print('MAIN PAIRS',[len(trees[i].overlap(trees[j])) for i in range(3) for j in range(i+1,3)],flush=True)
rows=[]
for index in range(3,6):
 verts,faces=data[index];best=None
 choices=sorted([(z*.005,math.radians(a*5)) for z in range(-12,13) for a in range(-8,9)],key=lambda p:abs(p[0])*3+abs(p[1])*.015)
 for z,angle in choices:
  if min(v.z for v in verts)+z<-.270 or max(v.z for v in verts)+z>-.025:continue
  rot=Matrix.Rotation(angle,3,'Z');vv=[rot@v+Vector((0,0,z)) for v in verts];tree=BVHTree.FromPolygons(vv,faces,all_triangles=True,epsilon=0)
  count=sum(len(tree.overlap(t)) for t in trees)
  score=count*1000+abs(z)*3+abs(angle)*.015
  if best is None or score<best[0]:best=(score,z,angle,tree,count)
  if count==0:break
 _,z,angle,tree,count=best;trees.append(tree);obs[index].location.z=z;obs[index].rotation_euler.z=angle;row=dict(index=index,z_shift_m=z,rotation_rad=angle,pairwise_triangle_hits=count);rows.append(row);print('PLACED',row,flush=True)
(R/'checks/v05-wave-adjustments.json').write_text(json.dumps(rows,indent=2))
