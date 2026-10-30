import bpy,bmesh,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path('/Users/razeek/Projects/3D printing');out=root/'Support/Checks/assembly-fixes'
source=root/'Printable-taller/Lamp-taller-printable.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
segments=[o for o in s.objects if o.type=='MESH' and 'Segment' in o.name];stand=s.objects['LAMP_Full Stand'];carrier=s.objects['LAMP_Full Carrier']
def tree(o,dz=0):return BVHTree.FromPolygons([o.matrix_world@v.co+Vector((0,0,dz)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
trees={o.name:tree(o) for o in segments}
report={'checked_file':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'topology':{},'static_collisions':{},'sampled_insertion':{},'clip_openings':[]}
for o in [segments[0],carrier,stand]:
 bm=bmesh.new();bm.from_mesh(o.data)
 report['topology'][o.name]={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'volume_mm3':bm.calc_volume()};bm.free()
 assert report['topology'][o.name]['nonmanifold_edges']==0
 assert report['topology'][o.name]['degenerate_faces']==0
for o in [carrier,stand]:
 tr=tree(o);report['static_collisions'][o.name]={name:len(tr.overlap(st)) for name,st in trees.items()}
 assert not any(report['static_collisions'][o.name].values())
 hits=[]
 for dz in range(-120,1):
  tr=tree(o,dz)
  collisions={name:len(tr.overlap(st)) for name,st in trees.items()};collisions={k:v for k,v in collisions.items() if v}
  if collisions:hits.append({'z_offset_mm':dz,'intersections':collisions})
 report['sampled_insertion'][o.name]={'range_mm':[-120,0],'step_mm':1,'colliding_samples':hits}
 print(o.name,'insertion collisions',len(hits),flush=True)
 assert not hits
master=s.objects['LAMP_Full Segment 01'];ct=trees[master.name];hz=38.81687344913152
for sign in [-1,1]:
 rot=Matrix.Rotation(sign*math.pi/12,3,'Z')
 for z in [-hz,hz]:
  p=rot@Vector((125,-sign,z));size=[]
  for axis in [(1,0,0),(0,0,1)]:
   d=rot@Vector(axis);h=[ct.ray_cast(p,d*k,20) for k in [-1,1]]
   size.append(sum(a[3] for a in h) if all(a[0] is not None for a in h) else None)
  report['clip_openings'].append({'end':sign,'z_mm':z,'size_mm':size})
  assert all(v is not None and abs(v-5)<.02 for v in size)
segments.sort(key=lambda o:math.atan2(o.location.y,o.location.x))
report['neighbor_intersections']=[len(trees[a.name].overlap(trees[segments[(i+1)%12].name])) for i,a in enumerate(segments)]
assert not any(report['neighbor_intersections'])
assert not any('LED strip' in o.name for o in bpy.data.objects)
# Sync verified mechanical fixes into the taller visual proposal; retain all inspection views.
target=root/'Lamp-taller-proposal.blend';backup=root/'Archive/2026-10-30/Versions/Lamp-taller-proposal-before-assembly-fixes.blend'
assert not backup.exists(),'Backup already exists; inspect before re-running.'
shutil.copy2(target,backup)
for sc in list(bpy.data.scenes):
 if sc.name.startswith('05 • Print parts'):bpy.data.scenes.remove(sc)
report['changes']=['Stand uses six narrow vertical roots down to Z=-70 before widening below the shade.','Carrier passage inner radius is 102.5 mm; outer radius stays 107 mm.','Smoothed 134.2 mm cloud silhouette and 41.5 mm thin carrier retained.']
report['limits']='Discrete 1 mm insertion samples, not a continuous clearance proof. Printed tolerances, clip retention and stand strength still need physical fit tests.'
for name in ['START HERE - Lamp','Taller cloud profile - checks','Verified assembly fixes']:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write(json.dumps(report,indent=2))
bpy.context.window.scene=s;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(target))
report['updated_proposal_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
(out/'verification.json').write_text(json.dumps(report,indent=2))
print('VERIFIED_AND_SAVED',str(target),flush=True)
