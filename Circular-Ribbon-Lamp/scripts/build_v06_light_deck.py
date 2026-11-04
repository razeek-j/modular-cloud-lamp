"""V06: six independent wave sweeps; selected, modeled uplight rails.
Background drafts precede a recorded Blender viewport construction.
Use --batch for synchronous construction. New file; earlier revisions preserved.
"""
import bpy, math, json, sys, bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
BATCH='--batch' in sys.argv
C={};bands=[];sources=[];attachments=[]

def coll(name):
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);C[name]=c;return c
def move(o,c):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);return o
def material(name,col,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def cube(name,loc,size,col,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object,col);o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def tube(name,pts,r,col,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);col.objects.link(o);cu.materials.append(mat);return o
def view():
 for scr in bpy.data.screens:
  for ar in scr.areas:
   if ar.type=='VIEW_3D':
    v=ar.spaces.active;v.region_3d.view_location=(0,0,-.13);v.region_3d.view_distance=1.65;v.region_3d.view_rotation=Vector((.25,-1.8,-.9)).to_track_quat('Z','Y');v.region_3d.view_perspective='ORTHO';v.shading.color_type='MATERIAL';v.overlay.show_floor=False

def setup():
 
 for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
 for c in list(bpy.data.collections):
  bpy.data.collections.remove(c)
 s=bpy.context.scene;s.name='V06 • reference wave cloud / selective lighting';s.unit_settings.system='METRIC';s.unit_settings.length_unit='MILLIMETERS'
 for name in ['V06 01 • LARGE ROLLED WAVES','V06 02 • IN-BETWEEN WAVES','V06 03 • EDITABLE SECTION PATHS','V06 04 • CEILING CARRIER','V06 05 • SELECTED LED POCKETS','V06 06 • LOW VOLTAGE ROUTES','V06 07 • PRESENTATION','V06 08 • LIGHTING GUIDES']:coll(name)
 global PAPER,ALU,WHITE,WIRE,LED,PLASTER,OPAL
 PAPER=material('V06 • soft white washi / optical approximation',(.87,.845,.79),rough=.48);nt=PAPER.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.04
 tr=nt.nodes.new('ShaderNodeBsdfTranslucent');tr.inputs[0].default_value=(.9,.86,.76,1);mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.62;nt.links.new(p.outputs[0],mix.inputs[1]);nt.links.new(tr.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs[0])
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1900;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.000015;bump.inputs['Strength'].default_value=.1;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
 ALU=material('V06 • aluminum interior',(.65,.66,.67),.8,.35);WHITE=material('V06 • warm white carrier exterior',(.82,.80,.76),.1);WIRE=material('V06 • insulated low voltage route',(.80,.78,.73));PLASTER=material('V06 • plaster ceiling',(.78,.75,.69),rough=.85)
 LED=material('V06 • COB phosphor',(.95,.72,.31));p=LED.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.55,.20,1);p.inputs['Emission Strength'].default_value=0
 OPAL=material('V06 • opal cover / unmeasured diffusion',(.9,.9,.88),rough=.7);nt=OPAL.node_tree;tr=nt.nodes.new('ShaderNodeBsdfTranslucent');tr.inputs[0].default_value=(.85,.85,.82,1);nt.links.new(tr.outputs[0],nt.nodes.get('Material Output').inputs[0])
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.render.resolution_x=1050;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.82,.75,.63,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.08;s.view_settings.view_transform='AgX';s.view_settings.exposure=1.3
 view()

def wave(k):
 n=600 if k<3 else 240;m=48;verts=[];faces=[];closed=k<3
 params=[(.487,.174,.022,2,.25),(.299,.156,.014,-2,1.35),(.122,.126,.006,1,math.pi/3)]
 def section(u):
  if k<3:
   radius,width,rwave,turns,phase=params[k];t=u*math.tau;r=radius+rwave*math.sin(3*t+phase)+.005*math.sin(5*t-.4);center=Vector((r*math.cos(t),r*math.sin(t),-.124+.024*math.sin(5*t+phase+.6)+.009*math.sin(8*t+phase)));roll=turns*t+phase+[.45,.35,.40][k]*math.sin([3,4,3][k]*t+phase);w=width*(1+.08*math.sin(4*t+phase));return center,roll,w
  a0=[-.35,1.95,3.8][k-3];t=a0+u*[1.55,1.5,1.65][k-3];r=[.389,.390,.214][k-3]+.018*math.sin(math.tau*u+.5*k);center=Vector((r*math.cos(t),r*math.sin(t),-.123+.033*math.sin(math.tau*u+.8*k)));roll=math.pi*(1.6*u-.4)+.35*math.sin(math.tau*u+k);w=[.080,.076,.074][k-3]*(.25+.75*math.sin(math.pi*u)**.35);return center,roll,w
 for i in range(n+1):
  if closed and i==n:break
  u=i/n;center,roll,width=section(u);T=(section(u+.0002)[0]-section(u-.0002)[0]).normalized();H=Vector((-T.y,T.x,0)).normalized();Z=T.cross(H).normalized();D=H*math.cos(roll)+Z*math.sin(roll);N=T.cross(D).normalized()
  for j in range(m+1):
   a=j/m-.5;angle=.70+.12*math.sin(3*math.tau*u+.6*k);q=2*a*angle;radius=width/(2*angle);across=radius*math.sin(q);camber=radius*(1-math.cos(q))+.008*math.sin(math.pi*(a+.5))*math.sin(6*math.tau*u+.7*k);edgewave=.006*math.sin(7*math.tau*u+.8*k)*(abs(a)*2)**2
   verts.append(tuple(center+D*across+N*(camber+edgewave+.0018*min(1,width/.12)*math.sin(math.tau*(a+.5)*width/.030+.25*math.sin(3*math.tau*u))*math.sin(math.pi*(a+.5)))))
 for i in range(n):
  for j in range(m):
   q=i*(m+1)+j;other=((i+1)%n if closed else i+1)*(m+1)+j;faces.append((q,other,other+1,q+1))
 name=f'W{k+1:02d} • '+(['main perimeter wave','middle counter-wave','inner rolled wave','intermediate saddle A','intermediate saddle B','central short counterfold'][k]);me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);C['V06 01 • LARGE ROLLED WAVES' if k<3 else 'V06 02 • IN-BETWEEN WAVES'].objects.link(o);me.materials.append(PAPER)
 for f in me.polygons:f.use_smooth=True
 so=o.modifiers.new('Uniform provisional skin • 1.2 mm','SOLIDIFY');so.thickness=.0012;so.offset=0;so.use_even_offset=False
 o['shape_index']=k;o['shape_parameters']=json.dumps(params[k] if k<3 else {'arc_index':k-3,'definition':'section() in embedded V06 source'});o['source']='Edit section coordinates, roll and width in V06 source; path guides are references, not live deformers.';bands.append(o)
 cu=bpy.data.curves.new(name+' • sections','CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(47);sp.use_cyclic_u=closed
 for i,p in enumerate(sp.points):p.co=(*section(i/(48 if closed else 47))[0],1)
 path=bpy.data.objects.new('PATH '+name,cu);C['V06 03 • EDITABLE SECTION PATHS'].objects.link(path);path.hide_render=True;path.hide_set(True)
 view()

def normalize():
 pts=[v.co for o in bands for v in o.data.vertices];scale=.5993/max(math.hypot(v.x,v.y) for v in pts);lo=min(v.z for v in pts);hi=max(v.z for v in pts)
 for o in bands:
  for v in o.data.vertices:v.co.x*=scale;v.co.y*=scale;v.co.z=-.025+(v.co.z-hi)*(.230/(hi-lo))
  o.data.update()
 for o in C['V06 03 • EDITABLE SECTION PATHS'].objects:
  for sp in o.data.splines:
   for p in sp.points:p.co.x*=scale;p.co.y*=scale;p.co.z=-.025+(p.co.z-hi)*(.230/(hi-lo))
 bands[1].location.z=-.040
 bands[2].location.z=-.040
 bands[5].location.z=-.040
 # The upper folds clear the opaque/diffusing ceiling engine.
 for ob in bands:
  for v in ob.data.vertices:
   radius=math.hypot(v.co.x,v.co.y);blend=max(0,min(1,(.480-radius)/.045));blend=blend*blend*(3-2*blend);cap=-.055-ob.location.z
   smooth=cap-.006*math.log1p(math.exp(max(-60,min(60,(cap-v.co.z)/.006))))
   v.co.z=v.co.z*(1-blend)+smooth*blend
 # Offset/rotation choices come from the collision search, before light placement.
 path=R/'checks/v06-wave-adjustments.json'
 if path.exists():
  for row in json.loads(path.read_text()):
   if row['index']<len(bands):
    ob=bands[row['index']];ob.rotation_euler.z=row['rotation_rad'];ob.location.z=row['z_shift_m']


def presentation():
 cube('Ceiling backdrop',(0,0,.016),(30,30,.032),C['V06 07 • PRESENTATION'],PLASTER)
 for name,pos,target,lens in [('CAM • warm room view',(.60,-2.55,-.62),(0,0,-.15),58),('CAM • underside',(0,0,-2.25),(0,0,-.13),50),('CAM • service top',(1,-1,1.4),(0,0,-.05),52)]:
  d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);C['V06 07 • PRESENTATION'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 s=bpy.context.scene;s.camera=bpy.data.objects['CAM • warm room view']
 # Neutral photographic room fill. Switched off in LED-only render.
 d=bpy.data.lights.new('Room daylight • review only','AREA');d.energy=8;d.shape='DISK';d.size=2;o=bpy.data.objects.new(d.name,d);C['V06 07 • PRESENTATION'].objects.link(o);o.location=(1,-1,-1.8);o.rotation_euler=(Vector((0,0,-.12))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'checkpoints/v06-composition.blend'),compress=True)

def cylinder(name,radius,depth,z,material,collection):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=radius,depth=depth,location=(0,0,z));o=move(bpy.context.object,collection);o.name=name;o.data.materials.append(material);return o

def annulus(name,outer,inner,z,thickness,material,collection):
 n=128;vv=[];ff=[]
 for h,radius in [(z-thickness/2,outer),(z-thickness/2,inner),(z+thickness/2,outer),(z+thickness/2,inner)]:
  vv.extend((radius*math.cos(i*math.tau/n),radius*math.sin(i*math.tau/n),h) for i in range(n))
 for i in range(n):
  j=(i+1)%n;ff.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);collection.objects.link(o);me.materials.append(material);return o

def lights():
 c=C['V06 05 • SELECTED LED POCKETS']
 # One shallow annular mixing chamber. The centre is a separate service canopy.
 annulus('Light deck • annular white rim',.450,.449,-.0175,.035,WHITE,c)
 annulus('Light deck • thin rear cover',.448,.112,-.001,.0008,WHITE,c)
 annulus('Light deck • first mixing film',.448,.112,-.020,.0004,OPAL,c)
 annulus('Light deck • opal mixing cover',.448,.112,-.035,.0010,OPAL,c)
 annulus('Light deck • inner opaque overlap seal',.116,.109,-.0345,.002,WHITE,c)
 annulus('Light deck • outer retaining lip',.452,.442,-.0365,.002,WHITE,c)
 # A single gentle ring bend follows the allowed out-of-plane tape direction.
 # Two short sections point up into the white reflector for a softer central fill.
 radius=2.8/math.tau
 annulus('Perimeter aluminum heat sleeve',radius+.0018,radius+.0008,-.018,.010,ALU,c)
 annulus('R01 • 8 mm COB strip',radius+.0008,radius-.0008,-.018,.008,LED,c)
 annulus('R01 • continuous thermal coupling lip',.449,radius+.0008,-.0125,.001,ALU,c)
 for i in range(48):
  angle=(i+.5)*math.tau/48;normal=Vector((-math.cos(angle),-math.sin(angle),0));loc=Vector(((radius-.0018)*math.cos(angle),(radius-.0018)*math.sin(angle),-.018));d=bpy.data.lights.new(f'R01.{i+1:02d} • COB equivalent','AREA');d.shape='RECTANGLE';d.size=2.8/48;d.size_y=.008;d.energy=(2.8*8/48)*.28;d.color=(1,.56,.25);o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=loc;o.rotation_euler=normal.to_track_quat('-Z','Y').to_euler()
 sources.append(dict(id='R01',zone='A perimeter cove',length_mm=2800,location_mm=[0,0,-18],radius_mm=radius*1000,orientation='VERTICAL_RING',normal='Radially inward',circuit='A',target='White mixing cavity and outer ribbon field',power_W=22.4))
 tube('Paired low voltage ring feed',[(.090,.015,-.006),(0,0,-.006),(radius,0,-.006),(radius,0,-.018)],.001,C['V06 06 • LOW VOLTAGE ROUTES'],WIRE)
 for i,x in enumerate([-.150,.150]):
  ident=f'F{i+1:02d}';loc=Vector((x,0,-.016));rail=cube(ident+' • aluminum heat rail',loc,(.020,.110,.002),c,ALU);pcb=cube(ident+' • 8 mm COB strip',loc+Vector((0,0,.0019)),(.008,.100,.0016),c,LED)
  d=bpy.data.lights.new(ident+' • COB equivalent','AREA');d.shape='RECTANGLE';d.size=.100;d.size_y=.008;d.energy=.8*.28;d.color=(1,.56,.25);o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=loc+Vector((0,0,.003));o.rotation_euler=(math.pi,0,math.pi/2)
  sources.append(dict(id=ident,zone='B reflected central fill',length_mm=100,location_mm=list(loc*1000),orientation='Y',normal=[0,0,1],circuit='B',target='White rear reflector, then central folds',power_W=.8))
  tube('Paired low voltage fill lead → '+ident,[(.090,.015,-.006),(x,0,-.006),(x,0,-.017)],.001,C['V06 06 • LOW VOLTAGE ROUTES'],WIRE)

def structure():
 c=C['V06 04 • CEILING CARRIER']
 # Opaque hollow canopy is inside the mixing deck's central opening.
 can=cylinder('Service canopy • Ø220 × 48 / hollow',.110,.048,-.024,WHITE,c);cut=cylinder('Canopy cutter',.108,.055,-.020,WHITE,c);bpy.context.view_layer.objects.active=can;mod=can.modifiers.new('Hollow canopy','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 cylinder('Service ceiling plate',.110,.002,-.001,WHITE,c)
 for a in [0,math.pi,math.pi/2,math.pi*1.5]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0025,depth=.012,location=(.110*math.cos(a),.110*math.sin(a),-.006));tool=bpy.context.object;tool.rotation_mode='QUATERNION';tool.rotation_quaternion=Vector((math.cos(a),math.sin(a),0)).to_track_quat('Z','Y');bpy.context.view_layer.objects.active=can;mod=can.modifiers.new('Concealed low-voltage exit','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
 cube('LPF-40-24 candidate • envelope',(0,.015,-.025),(.1625,.043,.032),c,ALU);cube('Two-channel 24 V dimmer • reserve',(0,-.043,-.016),(.055,.030,.014),c,WHITE)
 # Flat structural rails remain inside the lighting chamber, behind the opal cover.
 for i,y in enumerate([-.300,-.180,.180,.300]):cube('Internal carrier rail '+str(i+1),(0,y,-.004),(.700,.022,.004),c,WHITE)
 for x in [-.32,.32]:cube('Internal carrier cross rail '+str(x),(x,0,-.008),(.022,.620,.004),c,WHITE)
 for x in [-.20,.20]:cube('Internal inner-rail carrier '+str(x),(x,0,-.008),(.022,.360,.004),c,WHITE)
 for x in [-.15,.15]:
  for y in [-.053,.053]:tube('Reflected-fill rail support',[(math.copysign(.20,x),y,-.008),(x,y,-.017)],.002,c,WHITE)

 for x in [-.32,.32]:
  for y in [-.18,.18]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.00275,depth=.020,location=(x,y,-.005));tool=move(bpy.context.object,C['V06 08 • LIGHTING GUIDES']);tool.name='TOOL • provisional ceiling fixing clearance'
   for ob in list(c.objects)+[bpy.data.objects['Light deck • thin rear cover']]:
    if ob.type=='MESH' and ('carrier' in ob.name.lower() or 'rear cover' in ob.name):
     bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Provisional fixing clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name)
   tool.hide_render=True;tool.hide_set(True)

def cut_with(ob,tool,apply=False):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Concealed clearance cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
 if apply:bpy.ops.object.modifier_apply(modifier=mod.name)

def mount_returns():
 # Continuous printed extensions of existing boundary edges, folded into
 # two-screw laps on receivers inside the light deck. No visible clip objects.
 c=C['V06 04 • CEILING CARRIER'];guides=C['V06 08 • LIGHTING GUIDES'];used=[];base_trees={};deps=bpy.context.evaluated_depsgraph_get()
 for other in bands:
  ev=other.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();base_trees[other.name]=BVHTree.FromPolygons([other.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=.001);ev.to_mesh_clear()
 for k,band in enumerate(bands):
  original=list(band.data.vertices);stride=49;n=600 if k<3 else 240;closed=k<3
  vv=[v.co.copy() for v in original];ff=[tuple(f.vertices) for f in band.data.polygons];weights=[.4]*len(vv);inv=band.matrix_world.inverted()
  for sector in range(3 if k<3 else 2):
   angle=sector*math.tau/(3 if k<3 else 2)+.4*k;candidates=[]
   for row in range(32,n-32):
    for edge in [0,48]:
     point=band.matrix_world@original[row*stride+edge].co;rad=math.hypot(point.x,point.y)
     if not .135<rad<.415 or point.z>-.054:continue
     if abs((math.atan2(point.y,point.x)-angle+math.pi)%math.tau-math.pi)>.90:continue
     if any((point.xy-q.xy).length<.080 for q in used):continue
     candidates.append((point.z,row,edge,point))
   if not candidates:continue
   chosen=None
   for candidate in sorted(candidates,key=lambda item:item[0],reverse=True):
    _,cr,ce,cp=candidate;prev=band.matrix_world@original[(cr-1)*stride+ce].co;nxt=band.matrix_world@original[(cr+1)*stride+ce].co;hs=max(4,min(28,round(.030/max((nxt-prev).length/2,.0005))));inside=Vector((-cp.x,-cp.y,0)).normalized();clear=True
    for rr in [cr-hs,cr,cr+hs]:
     origin=band.matrix_world@original[rr*stride+ce].co
     for lateral in [-.006,0,.006]:
      test=origin+inside*lateral+Vector((0,0,.003));distance=-.025-test.z
      if distance>0 and any(tree.ray_cast(test,Vector((0,0,1)),distance)[0] is not None for name,tree in base_trees.items() if name!=band.name):clear=False;break
     if not clear:break
    if clear:chosen=candidate;break
   if chosen is None:continue
   _,row,edge,p=chosen;used.append(p)
   before=band.matrix_world@original[(row-1)*stride+edge].co;after=band.matrix_world@original[(row+1)*stride+edge].co;step=(after-before).length/2;half=max(4,min(28,round(.030/max(step,.0005))));rows=range(row-half,row+half+1)
   T=after-before;T.z=0;T.normalize();inward=Vector((-p.x,-p.y,0)).normalized();last=[r*stride+edge for r in rows]
   for layer in range(3):
    line=[]
    for rr,old in zip(rows,last):
     base=band.matrix_world@original[rr*stride+edge].co;q=Vector((base.x,base.y,-.025))
     if layer==0:q=(base+q)/2-inward*.004*math.sin(math.pi*(rr-(row-half))/(2*half))
     elif layer==2:q+=inward*.010
     line.append(len(vv));vv.append(inv@q);weights.append(.8 if layer==0 else 1)
    for a,b,d,e in zip(last[:-1],last[1:],line[:-1],line[1:]):ff.append((b,a,d,e) if edge==0 else (a,b,e,d))
    last=line
   centre=Vector((p.x,p.y,-.028))+inward*.005;receiver=cube(f'Receiver {k+1}.{sector+1} • paired lap',centre,(2*half*step+.022,.040,.003),c,WHITE);receiver.rotation_euler.z=math.atan2(T.y,T.x)
   # Connect the receiver to the ceiling-mounted structural grid, above the LEDs.
   grid=[]
   for y in [-.300,-.180,.180,.300]:grid.append(Vector((max(-.35,min(.35,centre.x)),y,-.004)))
   for x in [-.32,.32]:grid.append(Vector((x,max(-.31,min(.31,centre.y)),-.004)))
   drop=centre.copy()
   for offset in [0,.028,-.028,.045,-.045]:
    trial=centre+Vector((0,offset,0));blocked=any(row.get('orientation')=='Y' and abs(trial.x-row['location_mm'][0]/1000)<.018 and abs(trial.y-row['location_mm'][1]/1000)<.060 for row in sources)
    if not blocked:drop=trial;break
   root=min(grid,key=lambda a:(a-drop).length_squared)
   bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0033,depth=.012,location=(drop.x,drop.y,-.020));film_tool=move(bpy.context.object,guides);film_tool.name='TOOL • internal film standoff clearance';cut_with(bpy.data.objects['Light deck • first mixing film'],film_tool,True);film_tool.hide_render=True;film_tool.hide_set(True)
   back=Vector((drop.x,drop.y,-.004));tube(f'Internal spreader {k+1}.{sector+1}',[root,back,drop,centre],.0025,c,WHITE)
   slot=cube('TOOL • return slot',Vector((p.x,p.y,-.035))-inward*.002,(2*half*step+.012,.016,.014),guides,WHITE);slot.rotation_euler.z=math.atan2(T.y,T.x);cut_with(bpy.data.objects['Light deck • opal mixing cover'],slot,True);slot.hide_render=True;slot.hide_set(True)
   holes=[]
   for sign in [-1,1]:
    xy=Vector((p.x,p.y,0))+inward*.005+T*min(.020,half*step*.65)*sign
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.00165,depth=.018,location=(xy.x,xy.y,-.025));tool=move(bpy.context.object,guides);tool.name='TOOL • M3 clearance';cut_with(receiver,tool,True);holes.append(tool);tool.hide_render=True;tool.hide_set(True)
    bolt=cylinder(f'Concealed M3 shank {k+1}.{sector+1}.{sign}',.0015,.012,-.0275,ALU,c);bolt.location.x=xy.x;bolt.location.y=xy.y
    head=cylinder('Concealed screw head',.00275,.002,-.0225,ALU,c);head.location.x=xy.x;head.location.y=xy.y
    nut=cylinder('Concealed retention nut',.0032,.0024,-.0307,ALU,c);nut.location.x=xy.x;nut.location.y=xy.y
   attachments.append(dict(band=k+1,sector=sector+1,contact_mm=list(p*1000),lap_width_mm=2*half*step*1000,lap_depth_mm=10,return_skin_mm=3,fasteners='Two provisional M3 clearances; dimensions and capacity unvalidated',hole_tools=[o.name for o in holes],seal_length_m=2*half*step+.026,seal_centre_mm=[p.x*1000,p.y*1000,-35],seal_yaw_rad=math.atan2(T.y,T.x)))
  me=bpy.data.meshes.new(band.name+' • integral folded returns');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();band.data=me;me.materials.append(PAPER)
  for f in me.polygons:f.use_smooth=True
  group=band.vertex_groups.new(name='Uniform skin and reinforced returns')
  for weight in [.4,.8,1]:group.add([i for i,w in enumerate(weights) if w==weight],weight,'REPLACE')
  solid=next(m for m in band.modifiers if m.type=='SOLIDIFY');solid.thickness=.003;solid.vertex_group=group.name;solid.thickness_vertex_group=0;solid.use_even_offset=False
  for a in attachments:
   if a['band']==k+1:
    for name in a['hole_tools']:cut_with(band,bpy.data.objects[name])
    gasket=cube('Opaque return-slot collar',Vector(a['seal_centre_mm'])/1000,(a['seal_length_m'],.034,.0012),c,WHITE);gasket.rotation_euler.z=a['seal_yaw_rad'];cut_with(gasket,band,True);gasket['status']='Nominal compliant light-seal geometry; material grade and fit require testing.'

def ventilation():
 # Fine continuous shadow reveals replace conspicuous rectangular rim slots.
 rim=bpy.data.objects['Light deck • annular white rim'];c=C['V06 04 • CEILING CARRIER'];guides=C['V06 08 • LIGHTING GUIDES']
 for z in [-.00425,-.03075]:
  tool=annulus('TOOL • shadow-line vent',.456,.444,z,.0015,WHITE,guides);cut_with(rim,tool,True);bpy.data.objects.remove(tool,do_unlink=True)
  for i in range(16):
   a=i*math.tau/16;bridge=cube('Rim bridge',(.4495*math.cos(a),.4495*math.sin(a),z),(.0014,.005,.0035),c,WHITE);bridge.rotation_euler.z=a;bpy.context.view_layer.objects.active=rim;mod=rim.modifiers.new('Continuous rim with vent bridges','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=bridge;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(bridge,do_unlink=True)
 annulus('Upper vent light baffle',.441,.439,-.008,.012,WHITE,c);annulus('Lower vent light baffle',.441,.439,-.028,.012,WHITE,c)
 annulus('Lower vent concealing skirt',.452,.451,-.032,.008,WHITE,c)
 for i in range(8):
  a=i*math.tau/8;tab=cube('Retaining-skirt bridge',(.4505*math.cos(a),.4505*math.sin(a),-.0335),(.004,.006,.002),c,WHITE);tab.rotation_euler.z=a

def finish():
 deps=bpy.context.evaluated_depsgraph_get();vv=[]
 for o in bands:
  ev=o.evaluated_get(deps);me=ev.to_mesh();vv.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 facts=dict(revision='V06 wave cloud / ceiling light deck',bounds_mm={'min':[min(p[j] for p in vv)*1000 for j in range(3)],'max':[max(p[j] for p in vv)*1000 for j in range(3)]},radial_diameter_mm=max(math.hypot(p.x,p.y) for p in vv)*2000,attachments=attachments,LEDs=sources,total_strip_m=sum(x['length_mm'] for x in sources)/1000,total_LED_power_W=sum(x['power_W'] for x in sources),status='Wave-cloud, light-deck and integral-lap development concept. See digital checks; physical optical, thermal and load tests outstanding.')
 (R/'checks/v06-report.json').write_text(json.dumps(facts,indent=2))
 for title,path in [('V06 • source',R/'scripts/build_v06_light_deck.py'),('V06 • plan',R/'PLAN.md')]:
  t=bpy.data.texts.get(title) or bpy.data.texts.new(title);t.clear();t.write(path.read_text())
 image=bpy.data.images.load(str(R/'references/design-reference.jpg'),check_existing=True);image.pack()
 bpy.context.scene['status']=facts['status'];view();bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v06-light-deck.blend'),compress=True);print('V06',json.dumps({'ribbons':len(bands),'LED_modules':len(sources),'strip_m':facts['total_strip_m'],'power_W':facts['total_LED_power_W'],'bounds_mm':facts['bounds_mm']}),flush=True)

steps=[setup]+[lambda k=k:wave(k) for k in range(6)]+[normalize,presentation,lights,structure,mount_returns,ventilation,finish]
idx=0
def tick():
 global idx
 try:
  steps[idx]();idx+=1
  for s in bpy.data.screens:
   for a in s.areas:a.tag_redraw()
  return 3 if idx<len(steps) else None
 except Exception:
  import traceback;(R/'checks/v06-error.txt').write_text(traceback.format_exc());traceback.print_exc();return None
if BATCH:
 for fn in steps:fn()
else:
 if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
 bpy.app.timers.register(tick,first_interval=2)
