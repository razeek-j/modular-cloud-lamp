import bpy,bmesh,json,math
from pathlib import Path
from itertools import combinations
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get();rows=[];trees={};volume=0
objects=list(bpy.data.collections['V07 01 • LARGE ROLLED WAVES'].objects)+list(bpy.data.collections['V07 02 • IN-BETWEEN WAVES'].objects)
for ob in objects:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);left=set(bm.verts);parts=[]
 while left:
  group={left.pop()};stack=list(group)
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in left:left.remove(v);group.add(v);stack.append(v)
  parts.append(len(group))
 vol=abs(bm.calc_volume(signed=True))*abs(ob.matrix_world.determinant());volume+=vol
 trees[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=0)
 rows.append(dict(name=ob.name,components=len(parts),component_vertex_counts=parts,non_manifold_edges=sum(not e.is_manifold for e in bm.edges),volume_m3=vol,faces=len(bm.faces)));bm.free();ev.to_mesh_clear()
pairs=[dict(a=a.name,b=b.name,triangle_intersections=len(trees[a.name].overlap(trees[b.name]))) for a,b in combinations(objects,2)]
report=dict(meshes=rows,pairs=pairs,nominal_printed_skin_mass_kg_at_1270kg_m3=volume*1270,scope='Evaluated ripple skins only; separate V07 carrier and saddle studies excluded. Pairwise intersections only; no self-intersection, wall-thickness, load or thermal acceptance.')
(R/'checks/v07-assembly-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
