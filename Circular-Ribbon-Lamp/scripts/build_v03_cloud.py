"""V03: smooth stacked cloud bands. Live Bezier/Curve modifiers, no modeled fine ribs.
Background: blender -b v01.blend --python THIS -- --batch
UI: exec(compile(open(PATH).read(), PATH, 'exec'))
"""
import bpy, math, json, sys, bmesh
from pathlib import Path
from mathutils import Vector, Quaternion, kdtree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
BATCH='--batch' in sys.argv
P=[
 dict(name='01 Inner cloud • frame-supported',radius=.105,width=.160,z=-.135,phase=.2,wave=.021,roll=.75,offset=(-.016,.012)),
 dict(name='02 Cloud band • supported by 01',radius=.280,width=.160,z=-.166,phase=1.05,wave=.030,roll=.95,offset=(.012,-.016)),
 dict(name='03 Cloud band • supported by 02',radius=.455,width=.160,z=-.183,phase=2.1,wave=.034,roll=1.05,offset=(-.011,.013)),
 dict(name='04 Outer cloud • supported by 03',radius=.600,width=.110,z=-.183,phase=3.4,wave=.030,roll=1.13,offset=(.0,.0))]
C={}; bands=[]; attachments=[]

def col(name):
 c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); C[name]=c; return c

def move(o,c):
 for cc in list(o.users_collection): cc.objects.unlink(o)
 c.objects.link(o); return o

def mat(name,color,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.6; p.inputs['Metallic'].default_value=metal; return m

def view(bottom=False):
 for scr in bpy.data.screens:
  for a in scr.areas:
   if a.type=='VIEW_3D':
    sp=a.spaces.active; sp.region_3d.view_location=(0,0,-.16); sp.region_3d.view_distance=1.7
    sp.region_3d.view_rotation=Vector((0,0,-1) if bottom else (1.3,-1.8,-1.1)).to_track_quat('Z','Y')
    sp.region_3d.view_perspective='ORTHO'; sp.shading.type='SOLID'; sp.shading.color_type='MATERIAL'; sp.overlay.show_floor=False
 bpy.ops.object.select_all(action='DESELECT')

def setup():
 for o in list(bpy.data.objects):
  if o.type not in {'LIGHT','CAMERA'} and not o.name.startswith('Presentation ceiling') and o.type!='EMPTY': bpy.data.objects.remove(o,do_unlink=True)
 for key in ['V03 01 • CLOUD BANDS','V03 02 • EDITABLE PATHS','V03 03 • ROOT FRAME','V03 04 • PAIRED INTERBAND SUPPORTS','V03 05 • WIRING ROUTE','V03 06 • REFERENCE GUIDES']: col(key)
 global PAPER,METAL,WIRE
 PAPER=mat('V03 • white washi optical study',(.84,.82,.76)); nt=PAPER.node_tree; p=nt.nodes.get('Principled BSDF'); p.inputs['Subsurface Weight'].default_value=.05
 translucent=nt.nodes.new('ShaderNodeBsdfTranslucent'); translucent.inputs['Color'].default_value=(.86,.82,.71,1)
 mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.38; nt.links.new(p.outputs[0],mix.inputs[1]); nt.links.new(translucent.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
 noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=1700; noise.inputs['Detail'].default_value=2
 bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15; bump.inputs['Distance'].default_value=.000025; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 PAPER['note']='Shader-only washi mood preview. No displacement or modeled fine ribs; not a measured printed texture.'
 METAL=mat('V03 • warm white concealed hardware',(.74,.73,.68),.15); WIRE=mat('V03 • white low voltage wire',(.7,.7,.65))
 s=bpy.context.scene; s.name='V03 • stacked cloud / washi'; s['status']='Appearance and support-chain concept; not print-ready'
 s['surface_direction']='Smooth skins; intrinsic printing layers to be tested. Washi shader is preview only.'
 view()

def band(k):
 p=P[k]; curve=bpy.data.curves.new(p['name']+' • live path','CURVE'); curve.dimensions='3D'; curve.resolution_u=32; curve.twist_mode='Z_UP'; curve.use_stretch=True; curve.use_deform_bounds=True
 sp=curve.splines.new('BEZIER'); sp.bezier_points.add(23); sp.use_cyclic_u=True
 for i,b in enumerate(sp.bezier_points):
  t=math.tau*i/24; rr=p['radius']+.008*math.sin(3*t+.2)+.004*math.sin(5*t-.3)
  b.co=(rr*math.cos(t),rr*math.sin(t),p['z']+p['wave']*math.sin(3*t+p['phase']))
  b.tilt=p['roll']*math.sin(3*t+p['phase']+.65)+.23*math.sin(2*t-p['phase']); b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
 path=bpy.data.objects.new(f'PATH {k+1:02d} • edit points / tilt to reshape band',curve); C['V03 02 • EDITABLE PATHS'].objects.link(path); path.hide_render=True; path.hide_set(True)
 L=sp.calc_length(resolution=64); n=480; m=10; vv=[]; ff=[]
 for i in range(n+1):
  for j in range(m+1): vv.append((L*i/n,(j/m-.5)*p['width'],0))
 for i in range(n):
  for j in range(m):
   q=i*(m+1)+j; ff.append((q,q+m+1,q+m+2,q+1))
 me=bpy.data.meshes.new(p['name']+' • smooth master'); me.from_pydata(vv,[],ff); me.update(); ob=bpy.data.objects.new(p['name'],me); C['V03 01 • CLOUD BANDS'].objects.link(ob); me.materials.append(PAPER)
 for f in me.polygons:f.use_smooth=True
 mod=ob.modifiers.new('LIVE PATH • edit linked Bezier points and tilt','CURVE'); mod.object=path; mod.deform_axis='POS_X'
 weld=ob.modifiers.new('Close loop seam','WELD'); weld.merge_threshold=.00004
 solid=ob.modifiers.new('Provisional skin • 1.2 mm','SOLIDIFY'); solid.thickness=.0012; solid.offset=0
 ob['load_parent']='Ceiling root frame' if k==0 else P[k-1]['name']; ob['surface']='No modeled ribs; no displaced print lines'; ob['path']=path.name; bands.append(ob); bpy.context.view_layer.update(); view()

def tube(name,pts,r,c,material):
 d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.bevel_depth=r; d.bevel_resolution=3; sp=d.splines.new('POLY'); sp.points.add(len(pts)-1)
 for b,p in zip(sp.points,pts):b.co=(*p,1)
 o=bpy.data.objects.new(name,d); c.objects.link(o); d.materials.append(material); o['engineering_status']='Concept section only; capacity unvalidated'; return o

def beam(name,a,b,w,h,c):
 a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2); o=move(bpy.context.object,c); o.name=name; o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('X','Z'); o.scale=((b-a).length,w,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(METAL); return o

def normalize():
 deps=bpy.context.evaluated_depsgraph_get(); vv=[]
 for ob in bands:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();vv.extend([ob.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
 xy=.599/max(math.hypot(v.x,v.y) for v in vv);lo=min(v.z for v in vv);hi=max(v.z for v in vv);zz=.218/(hi-lo);shift=-.299-lo*zz
 for ob in bands+list(C['V03 02 • EDITABLE PATHS'].objects):ob.scale=(xy,xy,zz);ob.location.z=shift
 bpy.context.view_layer.update()

def structure():
 root=C['V03 03 • ROOT FRAME']; links=C['V03 04 • PAIRED INTERBAND SUPPORTS']; wires=C['V03 05 • WIRING ROUTE']
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.09,depth=.025,location=(0,0,-.0125)); o=move(bpy.context.object,root); o.name='Ceiling canopy • frame anchor';o.data.materials.append(METAL)
 tube('Inner metal carrier ring',[(.115*math.cos(i*math.tau/120),.115*math.sin(i*math.tau/120),-.105) for i in range(121)],.003,root,METAL)
 for i in range(3):
  t=i*math.tau/3+.35; a=Vector((.06*math.cos(t),.06*math.sin(t),-.025)); b=Vector((.115*math.cos(t),.115*math.sin(t),-.105));beam(f'Root frame neck {i+1}',a,b,.012,.004,root)
 deps=bpy.context.evaluated_depsgraph_get()
 coords=[]
 for ob in bands:
  ev=ob.evaluated_get(deps); me=ev.to_mesh(); coords.append([ob.matrix_world@v.co for v in me.vertices]); ev.to_mesh_clear()
 # Choose closest upper-region skin points within each angular sector. These are
 # conceptual paired attachment zones, not proof of hidden or manufacturable joints.
 for k in range(1,4):
  for sector in range(3):
   angle=sector*math.tau/3+.4*k; candidates=[]
   prev=[v for v in coords[k-1] if v.z<-.075]
   kd=kdtree.KDTree(len(prev))
   for q,v in enumerate(prev):kd.insert(v,q)
   kd.balance()
   for v in coords[k]:
    da=abs((math.atan2(v.y,v.x)-angle+math.pi)%math.tau-math.pi)
    if da<.78 and v.z<-.075:
     near,ind,dist=kd.find(v); candidates.append((dist,near.copy(),v.copy()))
   dist,a,b=min(candidates,key=lambda x:x[0]); tangent=Vector((-math.sin(angle),math.cos(angle),0))
   for sign in [-1,1]:
    delta=tangent*.008*sign; beam(f'{k:02d}→{k+1:02d} sector {sector+1} paired tab {sign}',a+delta,b+delta,.009,.003,links)
   tube(f'Low-voltage link {k} / {sector+1}',[a+Vector((0,0,.003)),b+Vector((0,0,.003))],.001,wires,WIRE)
   attachments.append(dict(parent=k,child=k+1,sector=sector+1,span_mm=dist*1000,a=list(a),b=list(b)))
 # Root-to-band attachment interfaces to make the support chain traceable.
 for j in range(3):
  t=j*math.tau/3+.35; a=Vector((.115*math.cos(t),.115*math.sin(t),-.105)); b=min(coords[0],key=lambda p:(p-a).length_squared);beam(f'Root ring to inner band seat {j+1}',a,b,.015,.004,root)
 view()

def finish():
 s=bpy.context.scene; s.camera=bpy.data.objects['CAM 01 • warm ceiling view']; s.camera.location=(1.15,-1.85,-.98); s.camera.rotation_euler=(Vector((0,0,-.16))-s.camera.location).to_track_quat('-Z','Y').to_euler()
 # All structural objects remain enabled for rendering.
 deps=bpy.context.evaluated_depsgraph_get(); volumes=[]; mins=[1e9]*3; maxs=[-1e9]*3
 for o in bands:
  ev=o.evaluated_get(deps); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); volume=abs(bm.calc_volume(signed=True)); volumes.append(volume*abs(o.matrix_world.determinant())); bm.free()
  for v in me.vertices:
   vworld=o.matrix_world@v.co
   for j in range(3): mins[j]=min(mins[j],vworld[j]); maxs[j]=max(maxs[j],vworld[j])
  ev.to_mesh_clear()
 report={'revision':'V03 stacked cloud','bounds_mm':{'min':[x*1000 for x in mins],'max':[x*1000 for x in maxs]},'nominal_skin_mass_kg_at_1270kg_m3':sum(volumes)*1270,'attachment_zones':attachments,'render_hardware_enabled':True,'skin_mm':1.2,'modeled_fine_ribs':False,'live_curve_modifiers':True,'unvalidated':['concealment from all angles','joint retention and capacity','creep and temperature','physical texture','print segmentation','wire routing and real LED layout']}
 (R/'checks/v03-report.json').write_text(json.dumps(report,indent=2))
 for name,path in [('V03 • source',R/'scripts/build_v03_cloud.py'),('V03 • process journal',R/'PROCESS.md')]:
  tx=bpy.data.texts.get(name) or bpy.data.texts.new(name);tx.clear();tx.write(path.read_text())
 s['support_chain']='Ceiling → inner ring frame → band 01 → band 02 → band 03 → band 04; 3 conceptual paired zones per interface. Hardware not rated.'
 view(); bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v03.blend'),compress=True)
 print('V03_REPORT',json.dumps(report),flush=True)

steps=[setup,lambda:band(0),lambda:band(1),lambda:band(2),lambda:band(3),normalize,structure,finish]; idx=0

def tick():
 global idx
 try:
  steps[idx]();idx+=1
  for scr in bpy.data.screens:
   for a in scr.areas:a.tag_redraw()
  return 4.0 if idx<len(steps) else None
 except Exception:
  import traceback; (R/'checks/v03-error.txt').write_text(traceback.format_exc());traceback.print_exc();return None
if BATCH:
 for fn in steps:fn()
else:
 if bpy.context.area and bpy.context.area.type=='CONSOLE':bpy.context.area.type='VIEW_3D'
 bpy.app.timers.register(tick,first_interval=3)
