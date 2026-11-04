"""Export closed geometric fit-study sectors, WITHOUT final seam joints/retention."""
import bpy,bmesh,math,json,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');revision='v04a' if '--v04a' in sys.argv else 'v04';out=R/f'print-study-{revision}/modules';out.mkdir(parents=True,exist_ok=True)
layout=json.loads((R/'print-study-v04/piece-layout.json').read_text());obs=list(bpy.data.collections['V04 01 • FLUSH CLOUD / actual surfaces'].objects);report=[]
for k,ob in enumerate(obs):
 count=sum(x['band']==k+1 for x in layout)
 for part in range(count):
  a=part*math.tau/count;b=(part+1)*math.tau/count;theta=(a+b)/2;bm=bmesh.new();bm.from_mesh(ob.data)
  for angle,neg,pos in [(a,True,False),(b,False,True)]:
   normal=Vector((-math.sin(angle),math.cos(angle),0));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=normal,clear_inner=neg,clear_outer=pos,dist=.0000001)
   edges=[e for e in bm.edges if e.is_boundary]
   if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nm=sum(not e.is_manifold for e in bm.edges)
  rot=Matrix.Rotation(-theta+math.pi/2,4,'Z');bm.transform(rot)
  if not bm.verts:report.append(dict(band=k+1,part=part+1,error='empty'));bm.free();continue
  low=Vector(tuple(min(v.co[j] for v in bm.verts) for j in range(3)));high=Vector(tuple(max(v.co[j] for v in bm.verts) for j in range(3)))
  for v in bm.verts:v.co=(v.co-low)*1000
  bmesh.ops.triangulate(bm,faces=list(bm.faces));name=f'FIT-ONLY-band-{k+1:02d}-part-{part+1:02d}.stl'
  with (out/name).open('wb') as f:
   f.write(b'Geometric fit study only; final seam joints not included'.ljust(80,b'\0'));f.write(struct.pack('<I',len(bm.faces)))
   for face in bm.faces:
    vs=[v.co for v in face.verts];n=(vs[1]-vs[0]).cross(vs[2]-vs[0]).normalized();f.write(struct.pack('<12fH',*n,*vs[0],*vs[1],*vs[2],0))
  dims=(high-low)*1000;report.append(dict(file=name,band=k+1,part=part+1,bounds_mm=list(dims),non_manifold_edges=nm,within_350mm_cube=max(dims)<350,under_320mm_margin=max(dims)<320));bm.free()
(R/f'checks/{revision}-fit-module-check.json').write_text(json.dumps(report,indent=2));print(json.dumps({'parts':len(report),'outside_350mm':[x.get('file') for x in report if not x.get('within_350mm_cube',False)],'nonmanifold':[x.get('file') for x in report if x.get('non_manifold_edges',1)>0]}),flush=True)
