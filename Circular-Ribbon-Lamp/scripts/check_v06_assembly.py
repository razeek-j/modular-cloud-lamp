import bpy,bmesh,json,math
from pathlib import Path
from itertools import combinations
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get();rows=[];trees={};volume=0
objects=list(bpy.data.collections['V06 01 • LARGE ROLLED WAVES'].objects)+list(bpy.data.collections['V06 02 • IN-BETWEEN WAVES'].objects)
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
report=dict(meshes=rows,pairs=pairs,nominal_printed_skin_and_return_mass_kg_at_1270kg_m3=volume*1270,scope='Evaluated shade skins, reinforced returns and hole booleans. Pairwise intersections only; no self-intersection, wall-thickness, load or thermal acceptance.')
(R/'checks/v06-assembly-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
# Direct view of bare strip through all modeled covers is tested separately
# from whether the diffusing cover itself is visible (it is intentionally visible).
cameras=[Vector((0,0,-2.2))]+[Vector((2*math.cos(i*math.tau/8),2*math.sin(i*math.tau/8),z)) for z in [-.95,-.4] for i in range(8)]+[Vector((x*.22,y*.22,-1.5)) for x in [-2,-1,0,1,2] for y in [-2,-1,0,1,2]];sources=[]
for row in json.loads((R/'checks/v06-report.json').read_text())['LEDs']:
 probes=[]
 if row.get('orientation')=='VERTICAL_RING':
  radius=row['radius_mm']/1000-.00081
  for i in range(48):
   angle=(i+.37)*math.tau/48;normal=Vector((-math.cos(angle),-math.sin(angle),0))
   for dz in [-.0038,0,.0038]:probes.append((Vector((radius*math.cos(angle),radius*math.sin(angle),-.018+dz)),normal))
 else:
  emitter=bpy.data.objects[row['id']+' • 8 mm COB strip']
  for f in [-.49,-.25,0,.25,.49]:
   for x in [-.0038,0,.0038]:probes.append((emitter.matrix_world@Vector((x,row['length_mm']/1000*f,.00081)),Vector((0,0,1))))
 visible=[];tested=0
 for ci,cam in enumerate(cameras):
  for pi,(p,normal) in enumerate(probes):
   direction=cam-p
   if normal.dot(direction)<=0:continue
   tested+=1;hit,*rest=bpy.context.scene.ray_cast(deps,p+normal*.00002,direction.normalized(),distance=direction.length)
   if not hit:visible.append(dict(view=ci,probe=pi))
 sources.append(dict(id=row['id'],front_facing_probes=tested,exposed_probes=len(visible),exposed=visible))
(R/'checks/v06-source-visibility.json').write_text(json.dumps(dict(views=len(cameras),sources=sources,scope='Opaque ray-occlusion only. Diffusers are visible by design; actual glare and material transmission remain physical tests.'),indent=2));print('SOURCE',json.dumps(sources),flush=True)
