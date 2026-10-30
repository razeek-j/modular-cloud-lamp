import bpy,bmesh,json
from pathlib import Path
s=bpy.data.scenes['02 • Full 360 Assembly'];bpy.context.window.scene=s;bpy.context.view_layer.update()
stand=s.objects['LAMP_Full Stand'];carrier=s.objects['LAMP_Full Carrier'];out=Path('/Users/razeek/Projects/3D printing/output/lamp-final-audit')
r={}
for target in [s.objects['LAMP_Full Segment 01'],s.objects['LAMP_Full Segment 05'],s.objects['LAMP_Full Segment 09'],carrier]:
 o=stand.copy();o.data=stand.data.copy();s.collection.objects.link(o)
 mod=o.modifiers.new('Read only interference audit','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=target
 dep=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dep);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
 r[target.name]={'intersection_volume_mm3':abs(bm.calc_volume(signed=True)),'faces':len(bm.faces),'vertices':len(bm.verts)}
 print(target.name,r[target.name],flush=True)
 bm.free();ev.to_mesh_clear();bpy.data.objects.remove(o,do_unlink=True)
(out/'interference-volumes.json').write_text(json.dumps(r,indent=2))
