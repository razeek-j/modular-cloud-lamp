import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
cameras=[Vector((0,0,-2.2))]+[Vector((2*math.cos(t*math.tau/8),2*math.sin(t*math.tau/8),z)) for z in [-.95,-.40] for t in range(8)]
cameras += [Vector((x*.22,y*.22,-1.5)) for x in [-2,-1,0,1,2] for y in [-2,-1,0,1,2]]
rows=[];windows=[]
for row in json.loads((R/'checks/v05-report.json').read_text())['LEDs']:
 ident=row['id'];emitter=bpy.data.objects[ident+' • 8 mm COB strip'];normal=emitter.matrix_world.to_3x3()@Vector((0,0,1));L=.1;visible=[];tested=0
 for ci,cam in enumerate(cameras):
  for xi in range(107):
   x=L*(-.497+xi*.994/106)
   for y in [-.0038,-.0019,0,.0019,.0038]:
    p=emitter.matrix_world@Vector((x,y,.00081));direction=cam-p
    if normal.dot(direction)<=0:continue
    tested+=1;origin=p+normal*.00002;hit,where,n,face,ob,matrix=s.ray_cast(deps,origin,direction.normalized(),distance=direction.length)
    if not hit:visible.append(dict(view=ci,x_mm=x*1000,y_mm=y*1000))
 rows.append(dict(id=ident,front_facing_probes=tested,directly_exposed_probes=len(visible),exposed=visible))
 window=bpy.data.objects[ident+' • opal window • removable'];visible=[];tested=0
 for ci,cam in enumerate(cameras):
  for xi in range(107):
   x=.105*(-.497+xi*.994/106)
   for y in [-.0038,-.0019,0,.0019,.0038]:
    p=window.matrix_world@Vector((x,y,.00051));direction=cam-p
    if normal.dot(direction)<=0:continue
    tested+=1;hit,*rest=s.ray_cast(deps,p+normal*.00002,direction.normalized(),distance=direction.length)
    if not hit:visible.append(dict(view=ci,x_mm=x*1000,y_mm=y*1000))
 windows.append(dict(id=ident,front_facing_probes=tested,directly_exposed_probes=len(visible),exposed=visible))
(R/'checks/v05-source-visibility.json').write_text(json.dumps(dict(review_views=len(cameras),scope='535 sampled face points per module, separately for strip and opal window; direct underside, eight azimuths at two elevations and a 25-position underside grid. Opaque ray-occlusion check only; not glare, photometry, translucency or support concealment validation.',sources=rows,windows=windows),indent=2));print('SOURCE_VISIBILITY',json.dumps(dict(views=len(cameras),bare_strip_exposed=sum(x['directly_exposed_probes'] for x in rows),opal_windows_exposed=sum(x['directly_exposed_probes'] for x in windows))),flush=True)
