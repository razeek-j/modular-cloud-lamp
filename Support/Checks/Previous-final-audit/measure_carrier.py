import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['02 • Full 360 Assembly'];bpy.context.window.scene=s;bpy.context.view_layer.update()
o=s.objects['LAMP_Full Carrier']
t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
r={}
for z in [-30.5,-29,-20,-10,0,3,6]:
 for angle in [0,90]:
  a=math.radians(angle);d=Vector((math.cos(a),math.sin(a),0));p=Vector((0,0,z));hits=[]
  for i in range(6):
   h=t.ray_cast(p,d,150)
   if h[0] is None:break
   hits.append(round(math.hypot(h[0].x,h[0].y),4));p=h[0]+d*.001
  r[f'z={z},angle={angle}']=hits
print(json.dumps(r,indent=2))
