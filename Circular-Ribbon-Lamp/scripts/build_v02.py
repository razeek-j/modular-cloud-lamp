import bpy, math
from mathutils import Vector
from pathlib import Path
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
bpy.ops.wm.open_mainfile(filepath=str(R/'Circular-Ribbon-Concept-v01.blend'))
for cname in ['01 RIBBONS — editable surfaces','03 SUPPORT — provisional metal','04 LED CARRIERS — provisional']:
 c=bpy.data.collections[cname]
 for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
shade=bpy.data.materials['Ivory diffusion • optical approximation']
coll=bpy.data.collections['01 RIBBONS — editable surfaces']
guides=bpy.data.collections.new('V02 • editable ribbon path guides'); bpy.context.scene.collection.children.link(guides)
for k in range(6):
 angle=k*math.tau/6 + [0,.08,-.09,.04,-.07,.09][k]
 a,b=math.cos(angle),math.sin(angle)
 def point(t):
  u=.28+.25*math.cos(t); v=.155*math.sin(t)+.025*math.sin(2*t+k*.7)
  return Vector((u*a-v*b,u*b+v*a,-.17+.037*math.sin(2*t+k*.9)+(0.025 if k%2==0 else -.025)))
 curve=bpy.data.curves.new('Ribbon %02d center path'%(k+1),'CURVE'); curve.dimensions='3D'; curve.resolution_u=24
 s=curve.splines.new('BEZIER'); s.bezier_points.add(7)
 for i,p in enumerate(s.bezier_points):
  p.co=point(.12+i*(5.85/7)); p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
 path=bpy.data.objects.new('Guide %02d • editable Bezier'%(k+1),curve); guides.objects.link(path); path.hide_render=True; path.hide_set(True)
 N=240; M=100; verts=[]; faces=[]
 for i in range(N):
  t=.12+i*5.85/(N-1); c=point(t); tang=(point(t+.001)-point(t-.001)).normalized(); side=Vector((-tang.y,tang.x,0)).normalized(); up=tang.cross(side).normalized(); roll=.85*math.sin(t*1.4+k*.8); D=math.cos(roll)*side+math.sin(roll)*up; norm=tang.cross(D).normalized(); width=.13+.025*math.sin(t+k*.4)
  for j in range(M+1):
   f=j/M-.5; bump=.00015*((1+math.cos(math.tau*f*width/.0035))/2)**3
   verts.append(tuple(c+f*width*D+bump*norm))
 for i in range(N-1):
  for j in range(M):
   q=i*(M+1)+j; faces.append((q,q+M+1,q+M+2,q+1))
 me=bpy.data.meshes.new('V02 ribbon surface %02d'%(k+1)); me.from_pydata(verts,[],faces); me.update()
 ob=bpy.data.objects.new('V02 ribbon %02d • concept surface'%(k+1),me); coll.objects.link(ob); ob.data.materials.append(shade)
 for p in me.polygons: p.use_smooth=True
 mod=ob.modifiers.new('Concept skin 1.2 mm','SOLIDIFY'); mod.thickness=.0012; mod.offset=0
 ob['guide']=path.name; ob['warning']='Guide is a reference; mesh is generated and does not update when guide is edited.'
sc=bpy.context.scene; sc['design_status']='V02 rough composition study • no support engineering or print validation'
sc['known_limitations']='Ribbon intersections, continuous load paths, concealed attachment points, supports, segmentation and physical tests NOT yet resolved.'
for scr in bpy.data.screens:
 for ar in scr.areas:
  if ar.type=='VIEW_3D': ar.spaces.active.region_3d.view_location=(0,0,-.16); ar.spaces.active.region_3d.view_distance=1.7
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Concept-v02-WIP.blend'),compress=True)
sc.render.resolution_percentage=60; sc.cycles.samples=20; sc.cycles.device='CPU'; sc.render.filepath=str(R/'renders/03-v02-wip-warm.png'); bpy.ops.render.render(write_still=True)
