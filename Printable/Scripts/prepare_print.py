"""Reproducible print preparation; millimetres. Leaves Lamp.blend unchanged."""
import bpy,bmesh,math,json,sys,struct,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'Printable'
sys.path.insert(0,str(ROOT/'Archive/2026-10-30/Earlier-work/blender-lamp'))
import build_lamp as base
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Lamp.blend'))
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
shade=[o for o in s.objects if o.type=='MESH' and 'Segment' in o.name]
carrier=s.objects['LAMP_Full Carrier'];stand=s.objects['LAMP_Full Stand'];old=stand.data
c=bpy.data.collections.new('Print preparation construction');s.collection.children.link(c)
new=base.annulus('Revised stand',105,3.4,-36,-31,c,mat=old.materials[0])
# Six flattened, vertical roots stay inside the shade's 4 mm radial passage.
# They broaden to 6 mm tubes only below the lowest shade surface (-52.3 mm).
def bez(a,b,c,d,n=36):
 a,b,c,d=map(Vector,[a,b,c,d]);return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in [i/n for i in range(n+1)]]
for k in range(3):
 th=k*2*math.pi/3;co=math.cos(th);si=math.sin(th)
 def xyz(x,y,z):return Vector((co*x-si*y,si*x+co*y,z))
 x=105*math.cos(math.radians(11));y=105*math.sin(math.radians(11))
 pts=[xyz(x,-y,z) for z in [-33,-36,-40,-45,-50,-53,-55]]
 pts+=bez(xyz(x,-y,-55),xyz(106,-18,-68),xyz(121,-5,-91),xyz(122,-5,-98))[1:]
 pts += [xyz(122,-5*math.cos(a),-98-5*math.sin(a)) for a in [i*math.pi/24 for i in range(1,25)]]
 pts += bez(xyz(122,5,-98),xyz(121,5,-91),xyz(106,18,-68),xyz(x,y,-55))[1:]
 pts += [xyz(x,y,z) for z in [-53,-50,-45,-40,-36,-33]]
 verts=[];faces=[];n=32
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
  radial=Vector((p.x,p.y,0)).normalized();u=(radial-tangent*radial.dot(tangent)).normalized();v=tangent.cross(u).normalized()
  a=1.3+1.7*max(0,min(1,(-p.z-55)/8))
  for j in range(n):
   t=2*math.pi*j/n;verts.append(p+a*math.cos(t)*u+3*math.sin(t)*v)
 for i in range(len(pts)-1):
  for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 faces += [tuple(reversed(range(n))),tuple((len(pts)-1)*n+j for j in range(n))]
 leg=base.mesh_object('Revised hairpin',verts,faces,c)
 base.boolean_apply(new,leg,'UNION');bpy.data.objects.remove(leg,do_unlink=True)
cut=base.oriented_box('Cable tunnel',97,113,-4,4,-38,-32.5,0,c)
base.boolean_apply(new,cut);bpy.data.objects.remove(cut,do_unlink=True);base.recalc(new.data)
new.data.name='Print revision - vertical clearance roots'
for o in bpy.data.objects:
 if o.data==old:o.data=new.data;o['Print revision']='Vertical 2.6 x 6 mm necks within shade passage; expand below shade.'
bpy.data.objects.remove(new,do_unlink=True);bpy.data.collections.remove(c);bpy.context.view_layer.update()
def topo(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);todo=set(bm.verts);cc=0
 while todo:
  cc+=1;q=[todo.pop()]
  while q:
   for e in q.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);q.append(v)
 r=dict(nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),components=cc,volume_mm3=bm.calc_volume(signed=True))
 bm.free();return r
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def intersect(a,b):
 temp=a.copy();temp.data=a.data.copy();s.collection.objects.link(temp)
 mod=temp.modifiers.new('Audit solid overlap','BOOLEAN');mod.object=b;mod.operation='INTERSECT';mod.solver='EXACT'
 ev=temp.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume());bm.free();ev.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);return v
# Extend the inner side of the underside passage by 0.5 mm so the backed
# wire channel can slide through; previously it caught during axial insertion.
master=shade[0];oldshade=master.data;master.data=master.data.copy()
cut=base.annulus('Insertion clearance cutter',102.755,.51,-70,7.8,s.collection)
base.boolean_apply(master,cut);bpy.data.objects.remove(cut,do_unlink=True);base.recalc(master.data)
for o in bpy.data.objects:
 if o.data==oldshade:o.data=master.data
bpy.context.view_layer.update()
st=tree(stand);ct=tree(carrier)
report={'source_sha256':hashlib.sha256((ROOT/'Lamp.blend').read_bytes()).hexdigest(),'units':'mm','topology':{o.name:topo(o) for o in [shade[0],carrier,stand]},'stand_shade_overlap_mm3':{},'carrier_shade_surface_pairs':{},'changes':['Stand rebuilt with 2.6 x 6 mm vertical necks above Z=-55; full 6 mm leg tubes below Z=-63. Original ring and cable exit dimensions retained.'],'shade_slot_revision':'Inner radial passage edge moved from 103.0 to 102.5 mm for carrier backing insertion clearance; outer edge remains 107 mm.','not_physically_verified':['material and heat resistance','actual LED, connector and cable fit','clip inserts and retention','load strength and tipping','assembly insertion path','printed dimensional tolerance']}
for sh in shade:
 report['stand_shade_overlap_mm3'][sh.name]=intersect(stand,sh) if st.overlap(tree(sh)) else 0
 report['carrier_shade_surface_pairs'][sh.name]=len(ct.overlap(tree(sh)))
report['stand_carrier_overlap_mm3']=intersect(stand,carrier)
assert all(r['nonmanifold_edges']==0 and r['components']==1 and r['volume_mm3']>0 for r in report['topology'].values()),report
assert max(report['stand_shade_overlap_mm3'].values())<.001,report
assert all(v==0 for v in report['carrier_shade_surface_pairs'].values()),report
# Static empty-shell centre of mass; support triangle from the three rounded feet.
parts=[*shade,carrier,stand]; weighted=Vector((0,0,0));total=0
for o in parts:
 me=o.data;me.calc_loop_triangles();vol=0;cent=Vector((0,0,0))
 for t in me.loop_triangles:
  a,b,c=[o.matrix_world@me.vertices[j].co for j in t.vertices];v=a.dot(b.cross(c))/6;vol+=v;cent+=(a+b+c)*(v/4)
 weighted+=cent;total+=vol
com=weighted/total
report['equal_density_empty_shell_com_mm']=list(com);report['approx_support_triangle_inradius_mm']=61;report['stability_note']='Empty equal-density shells only; LEDs, cable forces and actual masses are unknown. No load test.'
# Separate print scene: one of each, with appropriate planar faces on the bed.
p=bpy.data.scenes.new('05 • Print parts — one each');p.unit_settings.system='METRIC';p.unit_settings.scale_length=.001
printparts=[]
for idx,(src,name) in enumerate([(shade[0],'01_Shade_segment'),(carrier,'02_Middle_LED_carrier'),(stand,'03_Stand')]):
 o=bpy.data.objects.new(name,src.data.copy());p.collection.objects.link(o)
 o.matrix_world=src.matrix_world.copy()
 if idx==0:
  # Closed diaphragm outward normal is the normal of the largest planar face.
  face=max(src.data.polygons,key=lambda f:f.area);normal=src.matrix_world.to_3x3()@face.normal
  rotation=normal.rotation_difference(Vector((0,0,-1))).to_matrix().to_4x4();o.matrix_world=rotation@o.matrix_world
 elif idx==2:o.matrix_world=Matrix.Rotation(math.pi,4,'X')@o.matrix_world
 coords=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 offset=Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))
 o.matrix_world=Matrix.Translation(offset)@o.matrix_world
 coords=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles()
 with (OUT/'Models'/f'{name}.stl').open('wb') as f:
  f.write(name.encode().ljust(80,b'\0'));f.write(struct.pack('<I',len(o.data.loop_triangles)))
  for t in o.data.loop_triangles:
   a,b,c=[coords[j] for j in t.vertices];normal=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
 report.setdefault('print_parts',{})[name]={'dimensions_mm':list(hi-lo),'fits_U1_270mm':all(v<260 for v in hi-lo),'orientation':['Closed diaphragm down; open end up. Supports for internal brackets.','Brim down; 0.8 mm wall is delicate.','Upside down: flat ring down, feet up. Supports for curved leg tips.'][idx]}
 assert all(v<260 for v in hi-lo)
 # Separated for inspection; individual exports remain bed centred.
 o.location.x+=idx*290;printparts.append(o)
# Save revised editable copy and two previews.
bpy.context.window.scene=s;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lamp-printable.blend'))
for scene,filename,target,location,scale in [(s,'revised-assembly.png',(0,0,-25),(440,-550,290),420),(p,'three-print-parts.png',(290,0,35),(650,-650,470),850)]:
 bpy.context.window.scene=scene;d=bpy.data.cameras.new('Print preparation camera');cam=bpy.data.objects.new('Print preparation camera',d);scene.collection.objects.link(cam);cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.render.filepath=str(OUT/'Checks'/filename);bpy.ops.render.render(write_still=True)
(OUT/'Checks/geometry-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
