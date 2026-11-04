"""V04 flush cloud: integrated lap-return study and print division candidates.
No strength or production acceptance is implied by these concept pieces.
"""
import bpy,math,json,sys,bmesh,struct
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');BATCH='--batch' in sys.argv
if BATCH:bpy.ops.wm.open_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v03.blend'))
C={};bands=[];data={};out=R/'print-study-v04';out.mkdir(exist_ok=True)

def coll(name):
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);C[name]=c;return c

def move(o,c):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);return o

def box(name,lo,hi,c,material=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(Vector(lo)+Vector(hi))/2);o=move(bpy.context.object,c);o.name=name;o.scale=Vector(hi)-Vector(lo);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:o.data.materials.append(material)
 return o

def union(ob,tool):
 for obj in [ob,tool]:
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Integral return union','BOOLEAN');mod.operation='UNION';mod.solver='MANIFOLD';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)

def convert(ob):
 deps=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps));me.transform(ob.matrix_world);return me

def setup():
 global PAPER,METAL,data
 PAPER=bpy.data.materials.get('V03 • white washi optical study');METAL=bpy.data.materials.get('V03 • warm white concealed hardware')
 src=list(bpy.data.collections['V03 01 • CLOUD BANDS'].objects)
 coll('V04 01 • FLUSH CLOUD / actual surfaces');coll('V04 02 • INNER CEILING FRAME');coll('V04 03 • DIY LIGHTING STUDY');coll('V04 04 • PRINT DIVISION GUIDES');coll('V04 05 • JOINT TEST PAIR / not assembly')
 # Keep V03 live masters as references; visible V04 is the physically present geometry.
 for ob in src:
  me=convert(ob)
  for v in me.vertices:v.co.z=-.020+(v.co.z+.081)*(.180/.218)
  o=bpy.data.objects.new(ob.name.replace('cloud','cloud V04').replace('Cloud','Cloud V04'),me);C['V04 01 • FLUSH CLOUD / actual surfaces'].objects.link(o);bands.append(o)
  ob.hide_render=True;ob.hide_set(True)
 for key in ['V03 03 • ROOT FRAME','V03 04 • PAIRED INTERBAND SUPPORTS','V03 05 • WIRING ROUTE']:
  for o in list(bpy.data.collections[key].objects):bpy.data.objects.remove(o,do_unlink=True)
 data=json.loads((R/'checks/v03-report.json').read_text())
 bpy.context.scene.name='V04 • close-ceiling cloud / integrated overlap study'
 bpy.context.scene['status']='V04 design and print-division study; joints not physically validated'

def overlap_shape():
 # Extend the actual parent skin smoothly beneath the neighbouring band.
 # The connection reads as an overlapping fold, without an added cover plate.
 for zone in data['attachment_zones']:
  a=Vector(zone['a']);b=Vector(zone['b'])
  for p in [a,b]:p.z=-.020+(p.z+.081)*(.180/.218)
  d=b-a;d.z=0;dist=d.length;d.normalize();theta=math.atan2(a.y,a.x);rad=max(.10,math.hypot(a.x,a.y));sigma=.060/rad
  parent=bands[zone['parent']-1]
  for v in parent.data.vertices:
   p=v.co;da=(math.atan2(p.y,p.x)-theta+math.pi)%math.tau-math.pi;l=(p-a).dot(d)
   weight=math.exp(-(da/sigma)**2)*math.exp(-(l/.022)**2)
   p+=d*((dist+.010)*weight);p.z+=(b.z-a.z-.007)*weight
  parent.data.update()

def patch(name,points,width,thick):
 # A broad folded return, integrated into its band by a true mesh union.
 pts=[Vector(p) for p in points];direction=(pts[-1]-pts[0]);direction.z=0;direction.normalize();tangent=Vector((-direction.y,direction.x,0));verts=[]
 for i,p in enumerate(pts):
  T=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();N=T.cross(tangent).normalized()
  for z in [-thick/2,thick/2]:
   for w in [-width/2,width/2]:verts.append(tuple(p+tangent*w+N*z))
 faces=[(0,2,3,1)]
 for i in range(len(pts)-1):
  q=4*i;n=q+4;faces.extend([(q,n,n+1,q+1),(q+2,q+3,n+3,n+2),(q,q+2,n+2,n),(q+1,n+1,n+3,q+3)])
 q=4*(len(pts)-1);faces.append((q,q+1,q+3,q+2));me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);C['V04 01 • FLUSH CLOUD / actual surfaces'].objects.link(o);me.materials.append(PAPER);return o

def laps():
 report=[]
 for zone in data['attachment_zones']:
  k=zone['parent']-1;a=Vector(zone['a']);b=Vector(zone['b']);
  for p in [a,b]:p.z=-.020+(p.z+.081)*(.180/.218)
  d=b-a;d.z=0;d.normalize();mid=(a+b)/2;top=max(a.z,b.z)+.018
  # Mating shelves overlap 20 mm; complementary 1.5 mm layers total 3 mm.
  left=[a-d*.012,a-d*.006+Vector((0,0,.002)),Vector((a.x,a.y,top)),Vector((mid.x,mid.y,top))+d*.010]
  right=[b+d*.012,b+d*.006+Vector((0,0,.002)),Vector((b.x,b.y,top+.00175)),Vector((mid.x,mid.y,top+.00175))-d*.010]
  for index,points in [(k,left),(k+1,right)]:
   anchor=min(bands[index].data.vertices,key=lambda v:(v.co-points[0]).length_squared).co.copy();points[0]=anchor;points[1]=anchor.lerp(points[2],.35)
   tool=patch(f'Integrated folded lap {k+1}-{k+2} sector {zone["sector"]}',points,.024,.0015);union(bands[index],tool)
  report.append(dict(parent=k+1,child=k+2,overlap_mm=20,upper_shelf_clearance_mm=.25,retention='Upper-side retention to be finalized after joint tests; not a rated bonded joint'))
 data['v04_laps']=report

def frame():
 c=C['V04 02 • INNER CEILING FRAME']
 box('Ceiling mounting plate • DIY aluminum stock',(-.08,-.06,-.004),(.08,.06,0),c,METAL)
 # Concealed short rails end inside the inner band return region; no radial clip grid.
 for i in range(3):
  t=i*math.tau/3+.35;loc=Vector((.092*math.cos(t),.092*math.sin(t),-.045));a=Vector((.045*math.cos(t),.045*math.sin(t),-.004));delta=loc-a
  ob=box(f'Inner frame neck {i+1}',(-.006,-.002,-delta.length/2),(.006,.002,delta.length/2),c,METAL);ob.location=(a+loc)/2;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=delta.to_track_quat('Z','Y')
 # A removable concealed reflector is a DIY optical study, not a visible ornament.
 c=C['V04 03 • DIY LIGHTING STUDY'];m=bpy.data.materials.new('V04 • satin aluminum reflector');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.65,.63,.58,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.28
 for i in range(3):
  a=i*math.tau/3;ob=box(f'DIY reflector insert {i+1} • above inner folds',(-.06,-.01,-.0005),(.06,.01,.0005),c,m);ob.location=(.09*math.cos(a),.09*math.sin(a),-.027);ob.rotation_euler.z=a+math.pi/2
 for o in bpy.data.objects:
  if o.type=='LIGHT' and 'Warm bounce' in o.name:o.location.z=-.045

def stl(ob,path):
 me=ob.data;me.calc_loop_triangles()
 with path.open('wb') as f:
  f.write(b'V04 design test; not load rated'.ljust(80,b'\0'));f.write(struct.pack('<I',len(me.loop_triangles)))
  for tri in me.loop_triangles:
   p=[ob.matrix_world@me.vertices[i].co*1000 for i in tri.vertices];n=(p[1]-p[0]).cross(p[2]-p[0]).normalized();f.write(struct.pack('<12fH',*n,*p[0],*p[1],*p[2],0))

def coupons():
 c=C['V04 05 • JOINT TEST PAIR / not assembly']
 # These are generic retention/clearance test geometries, distinct from the curved joints.
 a=box('TEST A • lower half lap',(.85,0,0),(.900,.024,.003),c,PAPER);cut=box('cut',(.878,-.001,.0015),(.901,.025,.004),c);bpy.context.view_layer.objects.active=a;m=a.modifiers.new('Step cut','BOOLEAN');m.operation='DIFFERENCE';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 b=box('TEST B • upper half lap',(.85,.04,0),(.900,.064,.003),c,PAPER);cut=box('cut',(.849,.039,-.001),(.872,.065,.00175),c);bpy.context.view_layer.objects.active=b;m=b.modifiers.new('Step cut','BOOLEAN');m.operation='DIFFERENCE';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 for ob in [a,b]:
  # Export separately, translated to bed origin; keep out of assembled render.
  ob.data.transform(ob.matrix_world);ob.matrix_world.identity();mins=Vector(tuple(min(v.co[j] for v in ob.data.vertices) for j in range(3)))
  for v in ob.data.vertices:v.co-=mins
  stl(ob,out/(('lap-test-A' if ob==a else 'lap-test-B')+'.stl'));ob.hide_render=True;ob.hide_set(True)

def divisions():
 # Compute print-sized surface candidates from the original live-curve grids.
 # Keep geometric seams separate from the unproven structural lap design.
 src=list(bpy.data.collections['V03 01 • CLOUD BANDS'].objects);rows=[]
 for k,orig in enumerate(src):
  clone=orig.copy();clone.data=orig.data.copy();bpy.context.scene.collection.objects.link(clone)
  for mod in list(clone.modifiers):
   if mod.type!='CURVE':clone.modifiers.remove(mod)
  deps=bpy.context.evaluated_depsgraph_get();ev=clone.evaluated_get(deps);me=ev.to_mesh();vv=[clone.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();bpy.data.objects.remove(clone,do_unlink=True)
  for v in vv:v.z=-.020+(v.z+.081)*(.180/.218)
  stride=11;n=480
  # Find the lowest count whose largest oriented sampled bounding box fits a 310 mm envelope.
  for count in range(3,33):
   maxdim=0;chunks=[]
   for q in range(count):
    i0=round(q*n/count);i1=round((q+1)*n/count);pts=vv[i0*stride:(i1+1)*stride];center=sum(pts,Vector())/len(pts);theta=math.atan2(center.y,center.x);ca,sa=math.cos(theta),math.sin(theta)
    local=[Vector((-p.x*sa+p.y*ca,p.x*ca+p.y*sa,p.z)) for p in pts];sizes=[max(p[j] for p in local)-min(p[j] for p in local) for j in range(3)];maxdim=max(maxdim,max(sizes));chunks.append((q,i0,i1,sizes))
   if maxdim<.310:break
  for q,i0,i1,sizes in chunks:
   rows.append(dict(band=k+1,piece=q+1,pieces_in_band=count,oriented_surface_bounds_mm=[round(s*1000,2) for s in sizes],allowance='Surface only; 40 mm printer margin reserved. Final joints/supports/orientation not included.'))
  # Division guides are on the exact evaluated skin, not actual exported manufacturing modules.
  for q in range(count):
   row=round(q*n/count);pts=vv[row*stride:(row+1)*stride];cu=bpy.data.curves.new('Print split','CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
   for p,v in zip(sp.points,pts):p.co=(*v,1)
   ob=bpy.data.objects.new(f'GUIDE • band {k+1} piece boundary {q+1}/{count}',cu);C['V04 04 • PRINT DIVISION GUIDES'].objects.link(ob);ob.hide_render=True;ob.hide_set(True)
 data['print_division_candidates']=rows
 (out/'piece-layout.json').write_text(json.dumps(rows,indent=2))

def finish():
 data['revision']='V04 flush/interlap study';data['status']='Appearance, integrated-return and print-layout study; not manufacturing or overhead-load validated';data['floating_gap_removed']=True;data['target_skin_highest_mm']=-20;data['target_skin_lowest_mm']=-200;data['visible_clip_objects']=0
 data['reference_v03_attachment_zones']=data.pop('attachment_zones',[])
 data['source_v03_skin_mass_kg']=data.pop('nominal_skin_mass_kg_at_1270kg_m3',None)
 data['source_solidify_input_mm']=data.pop('skin_mm',1.2)
 data['live_curve_modifiers']=False
 data['hidden_v03_curve_masters_retained']=True
 data['wall_note']='Evaluated transformed skins; final uniform manufacturing thickness remains to be established.'
 coords=[];volume=0
 for ob in bands:
  coords.extend(ob.matrix_world@v.co for v in ob.data.vertices)
  bm=bmesh.new();bm.from_mesh(ob.data);volume+=abs(bm.calc_volume(signed=True))*abs(ob.matrix_world.determinant());bm.free()
 data['bounds_mm']={'min':[min(v[j] for v in coords)*1000 for j in range(3)],'max':[max(v[j] for v in coords)*1000 for j in range(3)]}
 data['nominal_current_skin_mass_kg_at_1270kg_m3']=volume*1270
 data['not_validated']=['Lap returns may be exposed from some views','Boolean connectivity and interface fit','Frame-to-inner-band seating','Upper-side retention specification','Print divisions do not yet contain final manufacturing joints','Physical print/creep/temperature tests']
 (R/'checks/v04-report.json').write_text(json.dumps(data,indent=2))
 s=bpy.context.scene;s['status']=data['status'];s['load_path']='Integral overlapping returns are conceptual. Final retention and root seating remain unvalidated.'
 for txt in ['START HERE • project plan','V04 • source']:
  t=bpy.data.texts.get(txt) or bpy.data.texts.new(txt);t.clear();t.write((R/('PLAN.md' if txt.startswith('START') else 'scripts/build_v04_flush.py')).read_text())
 for scr in bpy.data.screens:
  for ar in scr.areas:
   if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_location=(0,0,-.10);ar.spaces.active.region_3d.view_rotation=Vector((1.3,-1.8,-.85)).to_track_quat('Z','Y');ar.spaces.active.region_3d.view_distance=1.65
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v04-flush.blend'),compress=True)

steps=[setup,overlap_shape,laps,frame,coupons,divisions,finish];idx=0

def tick():
 global idx
 try:
  steps[idx]();idx+=1
  for scr in bpy.data.screens:
   for ar in scr.areas:ar.tag_redraw()
  return 4 if idx<len(steps) else None
 except Exception:
  import traceback;(R/'checks/v04-error.txt').write_text(traceback.format_exc());traceback.print_exc();return None
if BATCH:
 for fn in steps:fn()
else:
 if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
 bpy.app.timers.register(tick,first_interval=3)
