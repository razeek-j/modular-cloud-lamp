import bpy, json
from mathutils import Vector
from pathlib import Path
out=Path('/Users/razeek/Projects/3D printing/output/lamp-final-audit')
r={'file':bpy.data.filepath,'scenes':[]}
for s in bpy.data.scenes:
 bpy.context.window.scene=s;bpy.context.view_layer.update()
 k=s.unit_settings.scale_length*1000
 d={'name':s.name,'units':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'mm_per_unit':k,'objects':[]}
 for o in s.objects:
  if o.type not in ['MESH','CURVE']:continue
  corners=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(p[i] for p in corners) for i in range(3)];hi=[max(p[i] for p in corners) for i in range(3)]
  d['objects'].append({'name':o.name,'type':o.type,'mesh':o.data.name,'vertices':len(o.data.vertices) if o.type=='MESH' else None,
   'dimensions_mm':[(b-a)*k for a,b in zip(lo,hi)],'min_mm':[v*k for v in lo],'max_mm':[v*k for v in hi],
   'location':list(o.location),'scale':list(o.scale),'hidden_render':o.hide_render,'modifiers':[m.type for m in o.modifiers]})
 r['scenes'].append(d)
(out/'inventory.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
