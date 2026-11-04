"""V07: only the central canopy attaches to the ceiling. New revision from pre-deck rippled skins.
Carrier sections, joints and lighting are development geometry, not rated fabrication details.
"""
import bpy,math,json,bmesh,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
bpy.ops.wm.open_mainfile(filepath=str(R/'checkpoints/v06b-composition.blend'))
s=bpy.context.scene;s.name='V07 • centre-only ceiling attachment'
for c in bpy.data.collections:
 if c.name.startswith('V06B'):c.name=c.name.replace('V06B','V07',1)
bands=sorted([o for o in bpy.data.objects if o.name.startswith(('W01','W02','W03','W04','W05','W06')) and o.type=='MESH'],key=lambda o:o.name)
PAPER=bands[0].data.materials[0]
def mat(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.48;return m
WHITE=mat('V07 • ivory carrier finish',(.86,.85,.82),.1);METAL=mat('V07 • internal aluminum',(.61,.63,.65),.75);WIRE=mat('V07 • insulated paired loom',(.82,.81,.77));LED=mat('V07 • COB tape',(.95,.75,.40));OPAL=mat('V07 • optical window / unmeasured',(.90,.90,.88));nt=OPAL.node_tree;tr=nt.nodes.new('ShaderNodeBsdfTranslucent');tr.inputs[0].default_value=(.9,.88,.84,1);nt.links.new(tr.outputs[0],nt.nodes.get('Material Output').inputs[0])
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
CARRIER=collection('V07 04 • CENTRE ROOTED CARRIER');OPTICS=collection('V07 05 • SELECTED FOLD LIGHTS');JOINTS=collection('V07 06 • BACK SIDE SADDLES');ROUTES=collection('V07 07 • LOW VOLTAGE ROUTES');TOOLS=collection('V07 08 • CONSTRUCTION TOOLS')
def move(o,c):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);return o
def box(name,p,size,c,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=move(bpy.context.object,c);o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
def cylinder(name,p,r,depth,c,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=p);o=move(bpy.context.object,c);o.name=name;o.data.materials.append(material);return o
def line(name,pts,r,c,material):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,q in zip(sp.points,pts):p.co=(*q,1)
 o=bpy.data.objects.new(name,cu);c.objects.link(o);cu.materials.append(material);return o
def hollow_branch(name,pts):
 # Continuous rectangular hollow envelope. Bend/splice fabrication is not finalized.
 vv=[];ff=[]
 for i,p in enumerate(pts):
  tangent=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];tangent.z=0;tangent.normalize();side=Vector((-tangent.y,tangent.x,0))
  for w,h in [(.009,.008),(.0075,.0065)]:
   for x,z in [(-w,-h),(w,-h),(w,h),(-w,h)]:vv.append(tuple(p+side*x+Vector((0,0,z))))
 for i in range(len(pts)-1):
  for layer in [0,4]:
   for j in range(4):
    q=i*8+layer+j;n=i*8+layer+(j+1)%4;ff.append((q,n,n+8,q+8) if layer==0 else (n,q,q+8,n+8))
 for end in [0,(len(pts)-1)*8]:
  for j in range(4):ff.append((end+j,end+(j+1)%4,end+4+(j+1)%4,end+4+j))
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);CARRIER.objects.link(o);me.materials.append(WHITE);o['section']='18 × 16 × 1.5 mm provisional hollow envelope, not a selected/rated fabricated member';return o
# Build physical skin trees before adding supports.
deps=bpy.context.evaluated_depsgraph_get();trees={};surface={}
for ob in bands:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();trees[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
 # Authoring mesh centre samples give stable tangent and normal directions.
 stride=193 if ob['shape_index']<3 else 97;rows=600 if ob['shape_index']<3 else 241;points=[]
 for i in range(2,rows-2,3):
  j=stride//2;q=ob.matrix_world@ob.data.vertices[i*stride+j].co;t=(ob.matrix_world@ob.data.vertices[(i+1)*stride+j].co-ob.matrix_world@ob.data.vertices[(i-1)*stride+j].co).normalized();across=(ob.matrix_world@ob.data.vertices[i*stride+j+2].co-ob.matrix_world@ob.data.vertices[i*stride+j-2].co).normalized();normal=t.cross(across).normalized()
  if normal.z<0:normal=-normal
  points.append((q,t,normal))
 surface[ob.name]=points
# Compact central ceiling contact only: no outer anchors or backing plate.
plate=cylinder('ONLY CEILING CONTACT • central Ø220 plate',(0,0,-.001),.110,.002,CARRIER,WHITE)
can=cylinder('Central service canopy • Ø220 × 48',(0,0,-.024),.110,.048,CARRIER,WHITE);cut=cylinder('TOOL • canopy interior',(0,0,-.020),.108,.052,TOOLS,WHITE);bpy.context.view_layer.objects.active=can;mod=can.modifiers.new('Hollow accessible canopy','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
hub=cylinder('Central metal carrier hub',(0,0,-.044),.095,.004,CARRIER,METAL)
ceiling_points=[(x,y) for x in [-.065,.065] for y in [-.055,.055]]
for x,y in ceiling_points:
 tool=cylinder('TOOL • central ceiling fixing',(x,y,-.004),.00325,.020,TOOLS,WHITE)
 for target in [plate,hub]:
  bpy.context.view_layer.objects.active=target;mod=target.modifiers.new('Provisional centre fixing clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(tool,do_unlink=True)
 cylinder('Provisional centre fixing head',(x,y,-.047),.0055,.003,CARRIER,METAL);cylinder('Central load tie',(x,y,-.022),.004,.040,CARRIER,METAL)
box('Driver fit envelope • existing LPF-40-24 candidate',(0,.018,-.023),(.1625,.043,.032),CARRIER,METAL);box('24 V controller space reservation',(0,-.041,-.014),(.055,.030,.014),CARRIER,WHITE)
# Radial routing follows the upper envelope of existing folds, with a penalty for crossing open gaps.
angles=144;radials=[.110+i*.0125 for i in range(32)];height=[];owners=[]
for r in radials:
 row=[];who=[]
 for j in range(angles):
  a=j*math.tau/angles;origin=Vector((r*math.cos(a),r*math.sin(a),-.005));hits=[]
  for name,tree in trees.items():
   h,n,idx,dist=tree.ray_cast(origin,Vector((0,0,-1)),.5)
   if h is not None:hits.append((h.z,name))
  z,name=max(hits) if hits else (-.120,None);row.append(z);who.append(name)
 height.append(row);owners.append(who)
paths=[];branch_records=[]
for branch,target in enumerate([.15,2.20,4.30]):
 cost=[];parents=[]
 for i,r in enumerate(radials):
  cc=[];pp=[]
  for j in range(angles):
   a=j*math.tau/angles;delta=(a-target+math.pi)%math.tau-math.pi;base=(0 if owners[i][j] else 15)+delta*delta*.30+(300 if abs(delta)>.80 else 0)
   if i==0:cc.append(base+(0 if abs(delta)<math.tau/angles/2+.0001 else 100000));pp.append(j)
   else:
    choices=[(cost[-1][(j+d)%angles]+d*d*.025,(j+d)%angles) for d in range(-3,4)];v,prev=min(choices);cc.append(base+v);pp.append(prev)
  cost.append(cc);parents.append(pp)
 j=min((j for j in range(angles) if abs((j*math.tau/angles-target+math.pi)%math.tau-math.pi)<.35),key=lambda j:cost[-1][j]);indices=[j]
 for i in range(len(radials)-1,0,-1):j=parents[i][j];indices.append(j)
 indices.reverse();pts=[]
 for i,(r,j) in enumerate(zip(radials,indices)):
  a=j*math.tau/angles;z=min(-.016,height[i][j]+.012);pts.append(Vector((r*math.cos(a),r*math.sin(a),z)))
 # Never extend a primary carrier into the ceiling; only the central plate contacts it.
 start=pts[0].normalized();root=Vector((pts[0].x,pts[0].y,0)).normalized()*.083;root.z=-.044;pts.insert(0,root)
 hollow_branch(f'Branch B{branch+1} • centre to upper folds',pts);paths.append(pts);branch_records.append(dict(id=f'B{branch+1}',points_mm=[list(p*1000) for p in pts],open_gap_cells=sum(owners[i][j] is None for i,j in enumerate(indices)),fabrication='Provisional shaped hollow envelope; bend/splice joints, section sizing and capacity unvalidated'))
 line('Paired 24 V route B'+str(branch+1),[p+Vector((0,0,.005)) for p in pts],.001,ROUTES,WIRE)
# Each ribbon has an explicit paired attachment to the centre-rooted carrier.
attachments=[];pad_objects={ob.name:[] for ob in bands}
for ob in bands:
 candidates=[]
 for q,t,n in surface[ob.name]:
  if n.z<.55:continue
  for b,pts in enumerate(paths):
   nearest=min(pts,key=lambda p:(p-q).length_squared);score=(nearest-q).length+.15*max(0,q.z+.070);candidates.append((score,q,t,n,b,nearest))
 chosen=[]
 for item in sorted(candidates,key=lambda x:x[0]):
  if all((item[1]-v[1]).length>.110 for v in chosen):chosen.append(item)
  if len(chosen)==(3 if ob['shape_index']<3 else 1):break
 for seat,item in enumerate(chosen):
  _,q,t,n,b,nearest=item;name=f'{ob.name[:3]} / B{b+1} / S{seat+1}';top=q+n*.010
  # Short attachment bridge and paired retention; no long deck-hanging tongues.
  line('Hidden carrier connection • '+name,[nearest,top],.0035,CARRIER,WHITE)
  seat_tops=[]
  for sign in [-1,1]:
   p=q+t*.012*sign
   hit,hit_normal,_,_=trees[ob.name].ray_cast(Vector((p.x,p.y,-.005)),Vector((0,0,-1)),.5)
   if hit is not None:p=hit
   boss=cylinder('Back-side reinforcement study • '+name,p+n*.0035,.0065,.009,JOINTS,PAPER);boss.rotation_euler=n.to_track_quat('Z','Y').to_euler();pad_objects[ob.name].append(boss)
   stud=cylinder('Concealed saddle stud • '+name,p+n*.009,.0015,.010,CARRIER,METAL);stud.rotation_euler=n.to_track_quat('Z','Y').to_euler();seat_tops.append(p+n*.010)
  line('Paired saddle crossbar • '+name,[seat_tops[0],top,seat_tops[1]],.003,CARRIER,WHITE)
  attachments.append(dict(band=ob.name,branch=f'B{b+1}',location_mm=list(q*1000),pair_spacing_mm=24,status='Paired saddle/stud placement study; seating, integral pad union, retention and creep not finalized'))
# Selected fold-light stations. The tape stays straight in 100 mm modules.
lights=[];used=[]
for ob in bands[:3]:
 candidates=[]
 for q,t,n in surface[ob.name]:
  if n.z<.78 or q.z>-.080:continue
  nearest=min((p for pts in paths for p in pts),key=lambda p:(p-q).length_squared);candidates.append(((nearest-q).length,q,t,n,nearest))
 count=0
 for _,q,t,n,nearest in sorted(candidates,key=lambda v:v[0]):
  if any((q-p).length<.140 for p in used):continue
  for side in [-1,1]:
   # Two separated 100 mm modules form a station, bridged by wire rather than bending tape sideways.
   p=q+t*(.055*side)+n*.037;X=t;Z=n;Y=Z.cross(X).normalized();X=Y.cross(Z).normalized();rot=__import__('mathutils').Matrix(((X.x,Y.x,Z.x),(X.y,Y.y,Z.y),(X.z,Y.z,Z.z))).to_4x4();rot.translation=p
   ident=f'L{len(lights)+1:02d}'
   def cell(name,local,size,material):
    o=box(ident+' • '+name,p+X*local[0]+Y*local[1]+Z*local[2],size,OPTICS,material);o.rotation_euler=rot.to_euler();return o
   cell('aluminum heat bed',(0,0,.001),(.104,.022,.002),WHITE)
   for y in [-.0105,.0105]:cell('opaque side lip',(0,y,-.004),(.104,.0015,.010),WHITE)
   for x in [-.051,.051]:cell('opaque end lip',(x,0,-.004),(.002,.022,.010),WHITE)
   cell('8 mm COB strip',(0,0,-.001),(.100,.008,.0016),LED);cell('opal optical window',(0,0,-.009),(.100,.019,.0008),OPAL)
   data=bpy.data.lights.new(ident+' • COB equivalent','AREA');data.shape='RECTANGLE';data.size=.100;data.size_y=.008;data.energy=.8*.28;data.color=(1,.56,.25);lo=bpy.data.objects.new(data.name,data);OPTICS.objects.link(lo);lo.location=p-Z*.002;lo.rotation_euler=rot.to_euler()
   line('Light station carrier • '+ident,[nearest,p+Z*.003],.0025,CARRIER,WHITE);line('Paired low voltage feed • '+ident,[nearest+Vector((0,0,.005)),p+Z*.003],.001,ROUTES,WIRE)
   lights.append(dict(id=ident,band=ob.name,length_mm=100,power_W=.8,position_mm=list(p*1000),aim=list(-Z),status='Fold backlight cell placement; source/tray visibility and temperatures unvalidated'))
  used.append(q);count+=1
  if count==2:break
# Only three carrier/loom ports in the side wall of the compact canopy.
for i,pts in enumerate(paths):
 point=min(pts,key=lambda p:abs(math.hypot(p.x,p.y)-.110));port=box('TOOL • central branch port',point,(.034,.030,.040),TOOLS,WHITE);port.rotation_euler.z=math.atan2(point.y,point.x)
 bpy.context.view_layer.objects.active=can;mod=can.modifiers.new('Central carrier exit '+str(i+1),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=port;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(port,do_unlink=True)
# Everything physical remains enabled. No broad deck is included, even hidden.
for ob in bpy.data.objects:
 if ob.type in {'MESH','CURVE'} and not ob.name.startswith(('PATH','TOOL')):ob.hide_render=False;ob.hide_set(False)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   v=a.spaces.active;v.overlay.show_overlays=False;v.show_gizmo=False;v.shading.color_type='MATERIAL';v.region_3d.view_location=(0,0,-.14);v.region_3d.view_distance=1.5;v.region_3d.view_rotation=Vector((.3,-1.8,-.85)).to_track_quat('Z','Y');v.region_3d.view_perspective='ORTHO'
s.camera=bpy.data.objects['CAM • warm room view'];s.cycles.samples=24;s.render.resolution_x=1050;s.render.resolution_y=720
facts=dict(revision='V07 centre-only mounting',ceiling_contact_diameter_mm=220,ceiling_fixings_xy_mm=[[x*1000,y*1000] for x,y in ceiling_points],outer_ceiling_fixings=0,backing_plate=False,branches=branch_records,attachments=attachments,LEDs=lights,total_strip_m=len(lights)*.1,total_strip_power_W=len(lights)*.8,limits='Centre-only connection implemented. Carrier, saddle seating/retention, fabrication, optics, thermal and structural capacity remain development studies. No production STL released.')
(R/'checks/v07-report.json').write_text(json.dumps(facts,indent=2));s['status']=facts['limits'];s['only_ceiling_attachment']='Central Ø220 canopy/plate. No outer fixings or light deck.'
for title,path in [('V07 • source','scripts/build_v07_centre_mount.py'),('V07 • plan','PLAN.md')]:
 txt=bpy.data.texts.get(title) or bpy.data.texts.new(title);txt.clear();txt.write((R/path).read_text())
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v07-centre-mount.blend'),compress=True);print('V07 SAVED',len(attachments),'saddle zones',len(lights),'100 mm light modules',flush=True)
