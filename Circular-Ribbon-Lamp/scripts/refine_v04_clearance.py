"""Cut receiving relief at inter-band folds; preserve V04 as the source checkpoint."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
from itertools import combinations
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
bands=sorted(bpy.data.collections['V04 01 • FLUSH CLOUD / actual surfaces'].objects,key=lambda o:o.name)
results=[]
for parent,child in zip(bands,bands[1:]):
    cutter=child.copy();cutter.data=child.data.copy();bpy.context.scene.collection.objects.link(cutter)
    bm=bmesh.new();bm.from_mesh(cutter.data);bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.0005
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutter.data);bm.free()
    bpy.context.view_layer.objects.active=parent
    mod=parent.modifiers.new('Receiving relief • nominal 0.50 mm offset','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
for ob in bands:
    bm=bmesh.new();bm.from_mesh(ob.data);remaining=set(bm.verts);n=0;groups=[]
    while remaining:
        n+=1;stack=[remaining.pop()];group=set(stack)
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in remaining:remaining.remove(w);stack.append(w);group.add(w)
        groups.append(group)
    removed=0
    if len(groups)>1:
        groups.sort(key=len,reverse=True)
        scrap=set().union(*groups[1:])
        if len(scrap)<len(groups[0])*.002:
            removed=len(scrap);bmesh.ops.delete(bm,geom=list(scrap),context='VERTS');n=1;bm.to_mesh(ob.data)
    boundary=[e for e in bm.edges if e.is_boundary]
    filled=0
    # Repair only microscopic Boolean pinholes, never bridge a designed opening.
    if boundary and len(boundary)<=3 and all(e.calc_length()<.0001 for e in boundary):
        filled=len(bmesh.ops.holes_fill(bm,edges=boundary,sides=3).get('faces',[]))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data)
    results.append(dict(name=ob.name,components=n,non_manifold_edges=sum(not e.is_manifold for e in bm.edges),faces=len(bm.faces),trim_scrap_vertices_removed=removed,microscopic_pinhole_faces=filled))
    bm.free()
trees={}
for ob in bands:
    me=ob.data;me.calc_loop_triangles();trees[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=0)
pairs=[dict(a=a.name,b=b.name,intersecting_triangle_pairs=len(trees[a.name].overlap(trees[b.name]))) for a,b in combinations(bands,2)]
report=dict(meshes=results,pairs=pairs,scope='Receiving relief from expanded neighbouring shell; not a measured minimum clearance, wall thickness or joint-strength validation.')
(R/'checks/v04-clearance-refinement.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if all(x['components']==1 and x['non_manifold_edges']==0 for x in results) and not any(x['intersecting_triangle_pairs'] for x in pairs):
    bpy.context.scene['clearance_revision']='V04a receiving relief; nominal 0.50 mm normal-offset cutter. Final wall and load tests outstanding.'
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v04a-clearance.blend'),compress=True)
