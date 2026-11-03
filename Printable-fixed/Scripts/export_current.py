"""Export and audit the current fixed Blender source without modifying its geometry."""
import bpy,bmesh,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Printable-fixed';SOURCE=ROOT/'Lamp-taller-proposal.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
scale=s.unit_settings.scale_length*1000;assert abs(scale-1)<1e-5,scale
shade=sorted([o for o in s.objects if o.type=='MESH' and 'Segment' in o.name],key=lambda o:o.name)
master=s.objects['LAMP_Full Segment 01'];carrier=s.objects['LAMP_Full Carrier'];stand=s.objects['LAMP_Full Stand'];allobjs=[*shade,carrier,stand]
meshes={}
for o in allobjs:
 ev=o.evaluated_get(dep);me=ev.to_mesh();meshes[o.name]=me.copy();ev.to_mesh_clear()
def pts(o,dz=0):return [(o.matrix_world@v.co)*scale+Vector((0,0,dz)) for v in meshes[o.name].vertices]
def tree(o,dz=0):return BVHTree.FromPolygons(pts(o,dz),[tuple(p.vertices) for p in meshes[o.name].polygons])
def bounds(points):return [[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)]
def topo(o):
 bm=bmesh.new();bm.from_mesh(meshes[o.name]);todo=set(bm.verts);cc=0
 while todo:
  cc+=1;stack=[todo.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);stack.append(v)
 r={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'components':cc,'signed_volume_mm3':bm.calc_volume()};bm.free();return r
r={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'geometry_modified':False,'topology':{o.name:topo(o) for o in [master,carrier,stand]},'assembly_dimensions_mm':{},'static_surface_crossings':{},'sampled_insertion':{},'clip_openings_mm':[],'exported_parts':{}}
for o in [master,carrier,stand]:r['assembly_dimensions_mm'][o.name]=[b-a for a,b in bounds(pts(o))]
trees={o.name:tree(o) for o in shade}
for o in [carrier,stand]:
 r['static_surface_crossings'][o.name]={k:len(tree(o).overlap(t)) for k,t in trees.items()};hits=[]
 for dz in range(-120,1):
  tr=tree(o,dz);pairs={k:len(tr.overlap(t)) for k,t in trees.items()};pairs={k:v for k,v in pairs.items() if v}
  if pairs:hits.append({'offset_mm':dz,'surface_pairs':pairs})
 r['sampled_insertion'][o.name]={'step_mm':1,'range_mm':[-120,0],'colliding_samples':hits}
 print(o.name,'insertion:',len(hits),'colliding samples',flush=True)
r['neighbor_surface_crossings']=[len(trees[a.name].overlap(trees[shade[(i+1)%len(shade)].name])) for i,a in enumerate(shade)]
for sign in [-1,1]:
 rot=Matrix.Rotation(sign*math.pi/12,3,'Z')
 for z in [-38.81687344913152,38.81687344913152]:
  p=rot@Vector((125,-sign,z));size=[]
  for axis in [(1,0,0),(0,0,1)]:
   d=rot@Vector(axis);h=[trees[master.name].ray_cast(p,d*k,20) for k in [-1,1]];size.append(sum(v[3] for v in h) if all(v[0] is not None for v in h) else None)
  r['clip_openings_mm'].append({'end':sign,'z_mm':z,'width_height_mm':size})
for i,(o,name) in enumerate([(master,'01_Shade_segment'),(carrier,'02_Middle_LED_carrier'),(stand,'03_Stand')]):
 mesh=meshes[o.name];coords=pts(o);R=Matrix.Identity(3)
 if i==0:
  face=max(mesh.polygons,key=lambda p:p.area);n=(o.matrix_world.to_3x3()@face.normal).normalized();R=n.rotation_difference(Vector((0,0,-1))).to_matrix()
 elif i==2:R=Matrix.Rotation(math.pi,3,'X')
 coords=[R@v for v in coords];b=bounds(coords);shift=Vector((-(b[0][0]+b[0][1])/2,-(b[1][0]+b[1][1])/2,-b[2][0]));coords=[v+shift for v in coords];mesh.calc_loop_triangles();floor=0
 for tri in mesh.loop_triangles:
  a,b1,c=[coords[j] for j in tri.vertices]
  if max(a.z,b1.z,c.z)<.02:floor+=abs((b1-a).cross(c-a).z)/2
 dest=OUT/'Models'/f'{name}.stl'
 with dest.open('wb') as f:
  f.write(name.encode().ljust(80,b'\0'));f.write(struct.pack('<I',len(mesh.loop_triangles)))
  for tri in mesh.loop_triangles:
   a,b1,c=[coords[j] for j in tri.vertices];n=(b1-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*n,*a,*b1,*c,0))
 dims=[hi-lo for lo,hi in b];assert max(dims)<260
 r['exported_parts'][name]={'dimensions_mm':dims,'coplanar_bed_contact_area_mm2_within_0_02mm':floor,'stl_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'triangles':len(mesh.loop_triangles),'orientation':['Closed end down, open end up','Bottom rim down','Stand support ring down, legs up'][i]}
r['physical_limits']=['Actual filament/nozzle calibration and bed adhesion','Hole dimensional accuracy and clip retention','Removal of internal same-material supports','Actual cable/LED dimensions and heat','Strength and tipping under real load']
(OUT/'Checks/source-and-fit-audit.json').write_text(json.dumps(r,indent=2))
assert all(t['nonmanifold_edges']==0 and t['degenerate_faces']==0 and t['components']==1 and t['signed_volume_mm3']>0 for t in r['topology'].values())
assert not any(r['neighbor_surface_crossings'])
assert all(not any(t.values()) for t in r['static_surface_crossings'].values())
assert all(not t['colliding_samples'] for t in r['sampled_insertion'].values())
assert all(all(x is not None and abs(x-5)<.02 for x in h['width_height_mm']) for h in r['clip_openings_mm'])
print(json.dumps(r,indent=2))
