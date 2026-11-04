"""Place six straight recessed trays using geometry/visibility checks, not hidden objects."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
for key in ['V05 01 • LARGE ROLLED WAVES','V05 02 • IN-BETWEEN WAVES']:
 for ob in bpy.data.collections[key].objects:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();n=len(verts);verts.extend(ob.matrix_world@v.co for v in me.vertices);faces.extend([n+j for j in t.vertices] for t in me.loop_triangles);ev.to_mesh_clear()
shade=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0)
cameras=[Vector((0,0,-2.2))]+[Vector((2*math.cos(t*math.tau/8),2*math.sin(t*math.tau/8),z)) for z in [-.95,-.40] for t in range(8)]
box_faces=[(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
rows=[];previous=[]
seeds=[15,135,255,70,190,310]
for i in range(6):
 L=.3 if i<3 else .2;radius=.405 if i<3 else .21;best=None
 for dt in range(-30,31,10):
  angle=math.radians(seeds[i]+dt);yaw=angle+math.pi/2;tilt=155 if i<5 else -155;orient=Matrix.Rotation(yaw,3,'Z')@Matrix.Rotation(math.radians(tilt),3,'X')
  for dr in [-.04,-.02,0,.02,.04]:
   for z in [-.035,-.045,-.055,-.065,-.075,-.085]:
    r=radius+dr;loc=Vector((r*math.cos(angle),r*math.sin(angle),z));vv=[loc+orient@Vector((x,y,h)) for h in [-.0015,.021] for y in [-.0105,.0105] for x in [-L/2-.006,L/2+.006]];body=BVHTree.FromPolygons(vv,box_faces,all_triangles=True,epsilon=0);collisions=len(shade.overlap(body))+sum(len(t.overlap(body)) for t in previous)
    if collisions:continue
    # Bare tray underside should be covered by the folds in review views.
    visible=0;exposed=0;near=1
    for x in [-L*.48,-L*.24,0,L*.24,L*.48]:
     p=loc+orient@Vector((x,0,-.0016));nearest=shade.find_nearest(p)
     if nearest[0] is not None:near=min(near,nearest[3])
     for cam in cameras:
      ray=p-cam;dist=ray.length;hit=shade.ray_cast(cam,ray.normalized(),dist-.001)
      if hit[0] is None:visible+=1
    for x in [-L*.49,-L*.25,0,L*.25,L*.49]:
     for y in [-.0038,0,.0038]:
      local=Vector((x,y,.0028));p=loc+orient@local
      for cam in cameras:
       d=orient.transposed()@(cam-p)
       if d.z<=0:continue
       mouth=local+d*((.020-local.z)/d.z)
       if abs(mouth.y)>.008 or abs(mouth.x)>L/2+.003:continue
       ray=p-cam;hit=shade.ray_cast(cam,ray.normalized(),ray.length-.001)
       if hit[0] is None:exposed+=1
    # Keep approximately 12 mm or more from the luminous skin where possible.
    score=exposed*10000+visible*10+max(0,.012-near)*4000+abs(dt)*.06+abs(dr)*10+abs(z+.055)*4
    if best is None or score<best[0]:best=(score,loc,yaw,body,visible,near,dt,exposed)
 if best is None:raise RuntimeError('No collision-free tray for zone '+str(i+1))
 _,loc,yaw,body,visible,near,dt,exposed=best;previous.append(body);row=dict(id=f'L{i+1:02d}',length_m=L,location_m=list(loc),yaw_rad=yaw,tilt_deg=tilt,exposed_emitter_probes=exposed,tray_underside_visible_probes=visible,probes_total=85,sampled_nearest_skin_mm=near*1000,zone_seed_adjust_deg=dt);rows.append(row);print('RAIL',json.dumps(row),flush=True)
(R/'checks/v05-led-placements.json').write_text(json.dumps(rows,indent=2))
