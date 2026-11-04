"""One actual full-size wave/return fit sample, with closed cut faces; no final seam joint."""
import bpy,bmesh,json,math,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');out=R/'prototype-v06';out.mkdir(exist_ok=True)
facts=json.loads((R/'checks/v06-report.json').read_text());a=next(x for x in facts['attachments'] if x['band']==1);p=Vector(a['contact_mm'])/1000;theta=math.atan2(p.y,p.x);ob=bpy.data.objects['W01 • main perimeter wave'];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
for half in [.24,.20,.16,.12]:
 bm=bmesh.new();bm.from_mesh(me);bm.transform(ob.matrix_world)
 for angle,inner,outer in [(theta-half,True,False),(theta+half,False,True)]:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=(-math.sin(angle),math.cos(angle),0),clear_inner=inner,clear_outer=outer,dist=.0000001)
  edges=[e for e in bm.edges if e.is_boundary]
  if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.transform(Matrix.Rotation(-theta+math.pi/2,4,'Z'))
 low=Vector(tuple(min(v.co[j] for v in bm.verts) for j in range(3)));high=Vector(tuple(max(v.co[j] for v in bm.verts) for j in range(3)));dims=(high-low)*1000
 if max(dims)<310:break
 bm.free()
ev.to_mesh_clear();nonmanifold=sum(not e.is_manifold for e in bm.edges)
for v in bm.verts:v.co=(v.co-low)*1000
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update();bm.faces.ensure_lookup_table();tris=[tuple(v.index for v in f.verts) for f in bm.faces];verts=[v.co.copy() for v in bm.verts];tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
hit_pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(tris[i]).intersection(tris[j])];self_hits=len(hit_pairs)
print('HIT LOCATIONS', [list(sum((verts[v] for v in tris[i]),Vector())/3) for i,j in hit_pairs[:12]],flush=True)
name='SAMPLE-W01-folded-overlap-mm.stl'
with (out/name).open('wb') as f:
 f.write(b'V06 full-size fit and appearance sample; not a final production part'.ljust(80,b'\0'));f.write(struct.pack('<I',len(bm.faces)))
 for face in bm.faces:
  vv=[v.co for v in face.verts];n=(vv[1]-vv[0]).cross(vv[2]-vv[0]).normalized();f.write(struct.pack('<12fH',*n,*vv[0],*vv[1],*vv[2],0))
report=dict(file=name,bounds_mm=list(dims),nominal_scale='millimetres, full size',non_manifold_edges=nonmanifold,nonadjacent_triangle_pairs=self_hits,includes='Actual wave, integral reinforced return, two screw clearances and capped sector cuts',excluded='Final segment seam retention, slicer supports, validated print orientation and physical strength',selected_attachment=a)
(out/'sample-check.json').write_text(json.dumps(report,indent=2));bm.free()
# True-size receiver outline and two clearances, taken from the corresponding metal part.
receiver=bpy.data.objects[f'Receiver {a["band"]}.{a["sector"]} • paired lap'];rv=[v.co for v in receiver.data.vertices];lo=Vector((min(v.x for v in rv),min(v.y for v in rv),0));hi=Vector((max(v.x for v in rv),max(v.y for v in rv),0));W=(hi.x-lo.x)*1000;H=(hi.y-lo.y)*1000;holes=[]
for tool in a['hole_tools']:
 q=receiver.matrix_world.inverted()@bpy.data.objects[tool].location;holes.append(((q.x-lo.x)*1000,(hi.y-q.y)*1000))
circles=''.join(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="1.65"/>' for x,y in holes)
(out/'receiver-prototype-outline-mm.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.4f}mm" height="{H:.4f}mm" viewBox="0 0 {W:.4f} {H:.4f}"><g fill="none" stroke="black" stroke-width="0.1"><rect x="0.05" y="0.05" width="{W-.1:.4f}" height="{H-.1:.4f}"/>{circles}</g></svg>')
(out/'receiver-dimensions.json').write_text(json.dumps(dict(stock='3 mm aluminum, provisional prototype',outline_mm=[W,H],holes_mm=holes,hole_diameter_mm=3.3,capacity='Not load-rated; inspect fit and test before overhead use'),indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='selected_attachment'}),flush=True)
