import bpy,json,math
from mathutils import Vector
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
for key in ['Segment 01','Carrier','Stand']:
 o=next(o for o in s.objects if key in o.name and o.type=='MESH');vs=[o.matrix_world@v.co for v in o.data.vertices]
 print(key,'bounds',[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)],'verts',len(vs))
 if key=='Stand':
  for lo,hi in [(-38,-34),(-44,-38),(-50,-44),(-54,-50),(-58,-54)]:
   p=[v for v in vs if lo<=v.z<hi];print('radial',lo,hi,min(math.hypot(v.x,v.y) for v in p),max(math.hypot(v.x,v.y) for v in p))
 if key=='Segment 01':
  faces=sorted(o.data.polygons,key=lambda p:p.area,reverse=True)[:10]
  print('faces',[(p.area,tuple(o.matrix_world.to_3x3()@p.normal),tuple(o.matrix_world@p.center)) for p in faces])
