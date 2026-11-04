import bpy,json,math
from pathlib import Path
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');deps=bpy.context.evaluated_depsgraph_get();outer=[];visible=[];highest=-1
for ob in bpy.data.objects:
 if ob.type not in {'MESH','CURVE'} or ob.name.startswith(('Ceiling backdrop','PATH','TOOL')):continue
 if ob.hide_render or ob.hide_get():visible.append(ob.name)
 ev=ob.evaluated_get(deps);me=ev.to_mesh()
 if me:
  for v in me.vertices:
   p=ob.matrix_world@v.co
   if math.hypot(p.x,p.y)>.112:
    highest=max(highest,p.z)
    if p.z>=-.002:outer.append((ob.name,list(p)))
  ev.to_mesh_clear()
facts=json.loads((R/'checks/v07-report.json').read_text());assert not outer, 'Geometry contacts ceiling outside central mount';assert not visible,'Physical objects hidden in review';assert facts['outer_ceiling_fixings']==0
report=dict(only_ceiling_contact_diameter_mm=220,central_fixings_xy_mm=facts['ceiling_fixings_xy_mm'],outside_centre_ceiling_contact_vertices=len(outer),minimum_ceiling_gap_outside_radius_112_mm=-highest*1000,hidden_physical_objects=visible,deck_objects=[o.name for o in bpy.data.objects if 'Light deck' in o.name or 'retaining skirt' in o.name],branch_roots=[b['points_mm'][0] for b in facts['branches']],attachment_count=len(facts['attachments']),strip_modules=len(facts['LEDs']),scope='Geometric ceiling-contact boundary and visibility flags only. Does not validate load capacity, pad union/retention, optics, manufacture or every surface clearance.')
assert not report['deck_objects'];(R/'checks/v07-centre-contact-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
