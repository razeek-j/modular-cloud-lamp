import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');s=bpy.context.scene
s.cycles.device='CPU';s.cycles.samples=24;s.render.resolution_x=1050;s.render.resolution_y=750;s.render.resolution_percentage=100
s.render.filepath=str(R/'renders/04-v03-washi-warm.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
 if o.type=='LIGHT':
  if 'preview only' in o.name:o.data.energy=0
  else:o.data.energy=40;o.data.color=(1,1,1)
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.3;s.view_settings.exposure=.2
s.camera=bpy.data.objects['CAM 02 • circular underside'];s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=str(R/'renders/05-v03-washi-unlit.png');bpy.ops.render.render(write_still=True)
# Actual surface crossing check, reporting failures rather than hiding them.
deps=bpy.context.evaluated_depsgraph_get();obs=list(bpy.data.collections['V03 01 • CLOUD BANDS'].objects);trees={}
for o in obs:
 ev=o.evaluated_get(deps);me=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
results=[]
for i,a in enumerate(obs):
 for b in obs[i+1:]:results.append({'a':a.name,'b':b.name,'intersecting_triangle_pairs':len(trees[a.name].overlap(trees[b.name]))})
(R/'checks/v03-intersections.json').write_text(json.dumps(results,indent=2))
s.cycles.samples=12;s.render.resolution_x=600;s.render.resolution_y=420
cam=bpy.data.objects['CAM 01 • warm ceiling view'];s.camera=cam
for i in range(8):
 a=math.tau*i/8;cam.location=(2*math.cos(a),2*math.sin(a),-1.1);cam.rotation_euler=(Vector((0,0,-.17))-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(R/f'renders/v03-review-{i:02d}.png');bpy.ops.render.render(write_still=True)
