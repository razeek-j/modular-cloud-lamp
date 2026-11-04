import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from itertools import combinations
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');s=bpy.context.scene;s.cycles.device='CPU';s.cycles.samples=20
s.render.resolution_x=1050;s.render.resolution_y=720;s.render.resolution_percentage=100
s.camera=bpy.data.objects['CAM • warm room view'];s.render.filepath=str(R/'renders/v06-waves-warm.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
 if o.type=='LIGHT' and 'COB equivalent' in o.name:o.data.energy=0
 if o.type=='MESH':
  for mat in o.data.materials:
   if mat and mat.name.startswith('V06 • COB'):
    mat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=0
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
s.view_settings.exposure=0
bpy.data.objects['Room daylight • review only'].data.energy=30
s.render.filepath=str(R/'renders/v06-waves-unlit.png');bpy.ops.render.render(write_still=True)
trees={};rows=[];objects=list(bpy.data.collections['V06 01 • LARGE ROLLED WAVES'].objects)+list(bpy.data.collections['V06 02 • IN-BETWEEN WAVES'].objects);deps=bpy.context.evaluated_depsgraph_get()
for ob in objects:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();verts=[ob.matrix_world@v.co for v in me.vertices];trees[ob.name]=BVHTree.FromPolygons(verts,[list(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=0);ev.to_mesh_clear()
for a,b in combinations(objects,2):rows.append(dict(a=a.name,b=b.name,pairs=len(trees[a.name].overlap(trees[b.name]))))
(R/'checks/v06-intersections.json').write_text(json.dumps(rows,indent=2));print('INTERSECTIONS',json.dumps(rows),flush=True)
