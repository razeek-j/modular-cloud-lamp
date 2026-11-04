"""V05: six independent wave sweeps; selected, modeled uplight rails.
Background drafts precede a recorded Blender viewport construction.
Use --batch for synchronous construction. New file; earlier revisions preserved.
"""
import bpy, math, json, sys, bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
BATCH='--batch' in sys.argv
C={};bands=[];sources=[]

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
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
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
 s=bpy.context.scene;s.name='V05 • reference wave cloud / selective lighting';s.unit_settings.system='METRIC';s.unit_settings.length_unit='MILLIMETERS'
 for name in ['V05 01 • LARGE ROLLED WAVES','V05 02 • IN-BETWEEN WAVES','V05 03 • EDITABLE SECTION PATHS','V05 04 • CEILING CARRIER','V05 05 • SELECTED LED POCKETS','V05 06 • LOW VOLTAGE ROUTES','V05 07 • PRESENTATION','V05 08 • LIGHTING GUIDES']:coll(name)
 global PAPER,ALU,WHITE,WIRE,LED,PLASTER,OPAL
 PAPER=material('V05 • soft white washi / optical approximation',(.87,.845,.79),rough=.48);nt=PAPER.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.04
 tr=nt.nodes.new('ShaderNodeBsdfTranslucent');tr.inputs[0].default_value=(.9,.86,.76,1);mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.62;nt.links.new(p.outputs[0],mix.inputs[1]);nt.links.new(tr.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs[0])
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1900;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.000015;bump.inputs['Strength'].default_value=.1;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
 ALU=material('V05 • aluminum interior',(.65,.66,.67),.8,.35);WHITE=material('V05 • warm white carrier exterior',(.82,.80,.76),.1);WIRE=material('V05 • insulated low voltage route',(.80,.78,.73));PLASTER=material('V05 • plaster ceiling',(.78,.75,.69),rough=.85)
 LED=material('V05 • COB phosphor',(.95,.72,.31));p=LED.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.55,.20,1);p.inputs['Emission Strength'].default_value=0
 OPAL=material('V05 • opal cover / unmeasured diffusion',(.9,.9,.88),rough=.7);nt=OPAL.node_tree;tr=nt.nodes.new('ShaderNodeBsdfTranslucent');tr.inputs[0].default_value=(.85,.85,.82,1);nt.links.new(tr.outputs[0],nt.nodes.get('Material Output').inputs[0])
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.render.resolution_x=1050;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.82,.75,.63,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.08;s.view_settings.view_transform='AgX';s.view_settings.exposure=1.3
 view()

def wave(k):
 n=600 if k<3 else 240;m=48;verts=[];faces=[];closed=k<3
 params=[(.487,.174,.022,3,.25),(.299,.156,.014,-2,1.35),(.122,.126,.006,2,math.pi/3)]
 def section(u):
  if k<3:
   radius,width,rwave,turns,phase=params[k];t=u*math.tau;r=radius+rwave*math.sin(3*t+phase)+.005*math.sin(5*t-.4);center=Vector((r*math.cos(t),r*math.sin(t),-.124+.024*math.sin(5*t+phase+.6)+.009*math.sin(8*t+phase)));base_roll=[3,-3,2][k]*t+phase;roll=base_roll-.85*math.sin(base_roll);w=width*(1+.08*math.sin(4*t+phase));return center,roll,w
  a0=[-.35,1.95,3.8][k-3];t=a0+u*[1.55,1.5,1.65][k-3];r=[.389,.390,.214][k-3]+.018*math.sin(math.tau*u+.5*k);center=Vector((r*math.cos(t),r*math.sin(t),-.123+.033*math.sin(math.tau*u+.8*k)));roll=math.pi*(1.6*u-.4)+.35*math.sin(math.tau*u+k);w=[.080,.076,.074][k-3]*(.25+.75*math.sin(math.pi*u)**.35);return center,roll,w
 for i in range(n+1):
  if closed and i==n:break
  u=i/n;center,roll,width=section(u);T=(section(u+.0002)[0]-section(u-.0002)[0]).normalized();H=Vector((-T.y,T.x,0)).normalized();Z=T.cross(H).normalized();D=H*math.cos(roll)+Z*math.sin(roll);N=T.cross(D).normalized()
  for j in range(m+1):
   a=j/m-.5;gate=max(0,min(1,(math.cos(roll)-.15)/.45));gate=gate*gate*(3-2*gate);angle=.65+1.70*gate;q=2*a*angle;radius=width/(2*angle);across=radius*math.sin(q);camber=radius*(1-math.cos(q))+.008*math.sin(math.pi*(a+.5))*math.sin(6*math.tau*u+.7*k);edgewave=.006*math.sin(7*math.tau*u+.8*k)*(abs(a)*2)**2
   verts.append(tuple(center+D*across+N*(camber+edgewave+.0035*math.sin(4*math.tau*(a+.5)+.25*math.sin(3*math.tau*u))*math.sin(math.pi*(a+.5)))))
 for i in range(n):
  for j in range(m):
   q=i*(m+1)+j;other=((i+1)%n if closed else i+1)*(m+1)+j;faces.append((q,other,other+1,q+1))
 name=f'W{k+1:02d} • '+(['main perimeter wave','middle counter-wave','inner rolled wave','intermediate saddle A','intermediate saddle B','central short counterfold'][k]);me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);C['V05 01 • LARGE ROLLED WAVES' if k<3 else 'V05 02 • IN-BETWEEN WAVES'].objects.link(o);me.materials.append(PAPER)
 for f in me.polygons:f.use_smooth=True
 so=o.modifiers.new('Uniform provisional skin • 1.2 mm','SOLIDIFY');so.thickness=.0012;so.offset=0;so.use_even_offset=True
 o['shape_index']=k;o['shape_parameters']=json.dumps(params[k] if k<3 else {'arc_index':k-3,'definition':'section() in embedded V05 source'});o['source']='Edit section coordinates, roll and width in V05 source; path guides are references, not live deformers.';bands.append(o)
 cu=bpy.data.curves.new(name+' • sections','CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(47);sp.use_cyclic_u=closed
 for i,p in enumerate(sp.points):p.co=(*section(i/(48 if closed else 47))[0],1)
 path=bpy.data.objects.new('PATH '+name,cu);C['V05 03 • EDITABLE SECTION PATHS'].objects.link(path);path.hide_render=True;path.hide_set(True)
 view()

def normalize():
 pts=[v.co for o in bands for v in o.data.vertices];scale=.5993/max(math.hypot(v.x,v.y) for v in pts);lo=min(v.z for v in pts);hi=max(v.z for v in pts)
 for o in bands:
  for v in o.data.vertices:v.co.x*=scale;v.co.y*=scale;v.co.z=-.025+(v.co.z-hi)*(.230/(hi-lo))
  o.data.update()
 for o in C['V05 03 • EDITABLE SECTION PATHS'].objects:
  for sp in o.data.splines:
   for p in sp.points:p.co.x*=scale;p.co.y*=scale;p.co.z=-.025+(p.co.z-hi)*(.230/(hi-lo))
 bands[2].location.z=-.025
 # Offset/rotation choices come from the collision search, before light placement.
 path=R/'checks/v05-wave-adjustments.json'
 if path.exists():
  for row in json.loads(path.read_text()):
   if row['index']<len(bands):
    ob=bands[row['index']];ob.rotation_euler.z=row['rotation_rad'];ob.location.z=row['z_shift_m']


def presentation():
 cube('Ceiling backdrop',(0,0,.016),(30,30,.032),C['V05 07 • PRESENTATION'],PLASTER)
 for name,pos,target,lens in [('CAM • warm room view',(.25,-1.9,-.96),(0,0,-.13),48),('CAM • underside',(0,0,-2.25),(0,0,-.13),50),('CAM • service top',(1,-1,1.4),(0,0,-.05),52)]:
  d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);C['V05 07 • PRESENTATION'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 s=bpy.context.scene;s.camera=bpy.data.objects['CAM • warm room view']
 # Neutral photographic room fill. Switched off in LED-only render.
 d=bpy.data.lights.new('Room daylight • review only','AREA');d.energy=8;d.shape='DISK';d.size=2;o=bpy.data.objects.new(d.name,d);C['V05 07 • PRESENTATION'].objects.link(o);o.location=(1,-1,-1.8);o.rotation_euler=(Vector((0,0,-.12))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'checkpoints/v05-composition.blend'),compress=True)

def lights():
 # Thirteen straight 100 mm modules in five concealed, rolled-back fold pockets.
 # Each points into its own ribbon back; the centre uses borrowed light.
 deps=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
 for ob in bands:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();q=len(vv);vv.extend(ob.matrix_world@v.co for v in me.vertices);ff.extend([q+j for j in t.vertices] for t in me.loop_triangles);ev.to_mesh_clear()
 shade=BVHTree.FromPolygons(vv,ff,all_triangles=True,epsilon=0);previous=[]
 box_faces=[(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
 cameras=[Vector((0,0,-2.2))]+[Vector((2*math.cos(t*math.tau/8),2*math.sin(t*math.tau/8),z)) for z in [-.95,-.40] for t in range(8)]
 zone_specs=[(0,15,3),(0,135,3),(0,255,3),(1,70,2),(1,220,2)]
 for zi,(parent,seed,count) in enumerate(zone_specs):
  band=bands[parent];stride=49;n=600;rad=[.487,.299,.122][parent]
  for module in range(count):
   target_angle=math.radians(seed)+(module-(count-1)/2)*.120/rad;best=None
   for da in sorted(range(-80,81,2),key=abs):
    t=target_angle+math.radians(da);row=round((t%math.tau)/math.tau*n)%n
    middle=band.matrix_world@band.data.vertices[row*stride+24].co
    before=band.matrix_world@band.data.vertices[((row-1)%n)*stride+24].co;after=band.matrix_world@band.data.vertices[((row+1)%n)*stride+24].co;X=(after-before).normalized();across=(band.matrix_world@band.data.vertices[row*stride+36].co)-(band.matrix_world@band.data.vertices[row*stride+12].co);cup_normal=X.cross(across).normalized()
    if cup_normal.z<.85:continue
    for j in [24,12,36,6,42]:
     target=band.matrix_world@band.data.vertices[row*stride+j].co
     if not -.265<target.z<-.025:continue
     for sign in [1]:
      normal=-cup_normal;Y=normal.cross(X).normalized();orient=Matrix((X,Y,normal)).transposed()
      for distance in [.025,.030,.035,.045,.055,.065]:
       loc=target-normal*distance
       corners=[loc+orient@Vector((x,y,z)) for z in [-.0015,.016] for y in [-.0105,.0105] for x in [-.056,.056]]
       if max(v.z for v in corners)>-.012 or min(v.z for v in corners)<-.270:continue
       if any(math.hypot(v.x,v.y)<.112 and v.z>-.046 for v in corners):continue
       body=BVHTree.FromPolygons(corners,box_faces,all_triangles=True,epsilon=.001)
       if shade.overlap(body) or any(tree.overlap(body) for tree in previous):continue
       good=0;lengths=[]
       for x in [-.046,-.023,0,.023,.046]:
        p=loc+orient@Vector((x,0,.0155));hit=shade.ray_cast(p,normal,.13)
        if hit[0] is not None and hit[3]>.008:good+=1;lengths.append(hit[3])
       if good<5:continue
       seen=0
       for xx in [-.055,0,.055]:
        for yy in [-.010,.010]:
         for zz in [-.0016,.0155]:
          p=loc+orient@Vector((xx,yy,zz))
          for cam in cameras:
           ray=p-cam;hit=shade.ray_cast(cam,ray.normalized(),ray.length-.001)
           if hit[0] is None:seen+=1
       score=seen*1000+(5-good)*100+abs(da)*.12+abs(j-24)*.02+abs(distance-.035)*10
       if best is None or score<best[0]:best=(score,loc,orient,body,good,lengths,target,seen)
    if best is not None and best[-1]==0:break
   if best is None:raise RuntimeError('No free 100 mm pocket in zone '+str(zi+1))
   score,loc,orient,body,good,lengths,target,seen=best;previous.append(body);name=f'L{zi+1:02d}.{module+1}';L=.1;c=C['V05 05 • SELECTED LED POCKETS']
   def local(tag,xyz,size,mat):
    o=cube(name+' • '+tag,loc+orient@Vector(xyz),size,c,mat);o.rotation_euler=orient.to_euler();return o
   base=local('aluminum tray / opaque back',(0,0,0),(.110,.020,.002),WHITE)
   local('reflective bed',(0,0,.0011),(.106,.016,.0002),ALU);local('8 mm COB strip',(0,0,.0019),(.100,.008,.0016),LED)
   for sign in [-1,1]:
    local('recess side '+str(sign),(0,sign*.009,.007),(.110,.002,.014),WHITE)
    local('recess end '+str(sign),(sign*.054,0,.007),(.002,.020,.014),WHITE)
    local('return visor '+str(sign),(0,sign*.006,.014),(.106,.004,.001),WHITE)
   local('opal window • removable',(0,0,.006),(.105,.008,.001),OPAL)
   d=bpy.data.lights.new(name+' • shielded COB equivalent','AREA');d.shape='RECTANGLE';d.size=.100;d.size_y=.008;d.energy=.8*.28;d.color=(1,.56,.25);ob=bpy.data.objects.new(d.name,d);c.objects.link(ob);ob.location=loc+orient@Vector((0,0,.003));ob.rotation_euler=(orient@Matrix.Rotation(math.pi,3,'X')).to_euler();ob['preview_note']='Uncalibrated radiant equivalent, not measured strip photometry.'
   base['zone']=f'L{zi+1:02d}';base['strip_length_mm']=100
   sources.append(dict(id=name,zone=f'L{zi+1:02d}',length_mm=100,location_mm=[v*1000 for v in loc],orientation_matrix=[list(row) for row in orient],normal=list(orient@Vector((0,0,1))),circuit='A' if zi<3 else 'B',target=band.name,target_point_mm=[v*1000 for v in target],power_W=.8,visible_tray_back_probes=seen,tray_back_probe_total=204,normal_rays_hitting_shade=good,normal_ray_tests=5,first_skin_ray_distances_mm=[d*1000 for d in lengths]));print('POCKET',name,'tray probes',seen,'/204; target rays',good,'/5',flush=True)

def structure():
 c=C['V05 04 • CEILING CARRIER']
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.110,depth=.045,location=(0,0,-.0225));can=move(bpy.context.object,c);can.name='Service canopy • Ø220 × 45 / hollow';can.data.materials.append(WHITE)
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.108,depth=.05,location=(0,0,-.018));cut=bpy.context.object;bpy.context.view_layer.objects.active=can;mod=can.modifiers.new('2 mm wall and floor','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.110,depth=.002,location=(0,0,-.001));cap=move(bpy.context.object,c);cap.name='Ceiling service plate';cap.data.materials.append(WHITE)
 cube('LPF-16-24 candidate • 148 × 40 × 32 envelope',(0,.015,-.025),(.148,.040,.032),c,ALU)
 cube('Two-channel secondary dimmer • reserved envelope',(0,-.043,-.016),(.055,.030,.014),c,WHITE)
 for zone in sorted(set(p['zone'] for p in sources)):
  members=[p for p in sources if p['zone']==zone];q=sum((Vector(p['location_mm'])/1000 for p in members),Vector())/len(members);mid=Vector((q.x*.55,q.y*.55,-.018));end=q+Vector((0,0,.007));tube(f'Carrier trunk to {zone}',[(0,0,-.012),mid,end],.003,c,WHITE)
  tube(f'24V pair trunk → {zone}',[(.035,.025,-.012),mid+Vector((0,0,.004)),end+Vector((0,0,.002))],.0015,C['V05 06 • LOW VOLTAGE ROUTES'],WIRE)
  for p in members:
   rear=Vector(p['location_mm'])/1000-Vector(p['normal'])*.004
   tube('Short carrier branch → '+p['id'],[end,rear],.002,c,WHITE)
   tube('Paired jumper → '+p['id'],[end+Vector((0,0,.004)),rear+Vector((0,0,.003))],.001,C['V05 06 • LOW VOLTAGE ROUTES'],WIRE)

def finish():
 deps=bpy.context.evaluated_depsgraph_get();vv=[]
 for o in bands:
  ev=o.evaluated_get(deps);me=ev.to_mesh();vv.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 facts=dict(revision='V05 independent rolled waves',bounds_mm={'min':[min(p[j] for p in vv)*1000 for j in range(3)],'max':[max(p[j] for p in vv)*1000 for j in range(3)]},radial_diameter_mm=max(math.hypot(p.x,p.y) for p in vv)*2000,LEDs=sources,total_strip_m=sum(x['length_mm'] for x in sources)/1000,total_LED_power_W=sum(x['power_W'] for x in sources),status='Appearance and selected-lighting development; collision, source concealment and mechanical seating require review.')
 (R/'checks/v05-report.json').write_text(json.dumps(facts,indent=2))
 for title,path in [('V05 • source',R/'scripts/build_v05_waves.py'),('V05 • plan',R/'PLAN.md')]:
  t=bpy.data.texts.get(title) or bpy.data.texts.new(title);t.clear();t.write(path.read_text())
 image=bpy.data.images.load(str(R/'references/design-reference.jpg'),check_existing=True);image.pack()
 bpy.context.scene['status']=facts['status'];view();bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v05-waves.blend'),compress=True);print('V05',json.dumps({'ribbons':len(bands),'LED_modules':len(sources),'strip_m':facts['total_strip_m'],'power_W':facts['total_LED_power_W'],'bounds_mm':facts['bounds_mm']}),flush=True)

steps=[setup]+[lambda k=k:wave(k) for k in range(6)]+[normalize,presentation,lights,structure,finish]
idx=0
def tick():
 global idx
 try:
  steps[idx]();idx+=1
  for s in bpy.data.screens:
   for a in s.areas:a.tag_redraw()
  return 3 if idx<len(steps) else None
 except Exception:
  import traceback;(R/'checks/v05-error.txt').write_text(traceback.format_exc());traceback.print_exc();return None
if BATCH:
 for fn in steps:fn()
else:
 if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
 bpy.app.timers.register(tick,first_interval=2)
