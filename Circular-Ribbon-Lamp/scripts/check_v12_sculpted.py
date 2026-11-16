import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
from itertools import combinations
from pathlib import Path
out=Path(bpy.data.filepath).resolve().parent
obs=[o for o in bpy.data.collections['01 · Broad sculpted ribbons'].objects if o.type=='MESH']
trees={};triangles={};checks={}
for o in obs:
    bm=bmesh.new();bm.from_mesh(o.data)
    checks[o.name]={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_cm3':bm.calc_volume()*1e6}
    bm.free();o.data.calc_loop_triangles()
    triangles[o.name]=[tuple(t.vertices) for t in o.data.loop_triangles]
    trees[o.name]=BVHTree.FromPolygons([v.co for v in o.data.vertices],triangles[o.name],all_triangles=True)
    pairs=[(i,j) for i,j in trees[o.name].overlap(trees[o.name]) if i<j and set(triangles[o.name][i]).isdisjoint(triangles[o.name][j])]
    checks[o.name]['nonadjacent_self_intersections']=len(pairs)
    cols=65 if 'Draft' in bpy.data.filepath else 121
    cells=len(o.data.vertices)//2
    checks[o.name]['self_parameters']=[[[round((triangles[o.name][h][0]%cells)//cols/16,2),(triangles[o.name][h][0]%cells)%cols] for h in (i,j)] for i,j in pairs[::max(1,len(pairs)//8)][:8]]
    checks[o.name]['self_intersection_samples_mm']=[list(sum((o.data.vertices[k].co for k in triangles[o.name][i]),start=o.location.copy())/3*1000) for i,j in pairs[::max(1,len(pairs)//8)][:8]]
pairchecks={}
for a,b in combinations(obs,2):
    hits=trees[a.name].overlap(trees[b.name]);pairchecks[a.name[0]+b.name[0]]={'triangle_intersections':len(hits),'samples_mm':[]}
    for i,j in hits[::max(1,len(hits)//10)][:10]:
        p=sum((a.data.vertices[k].co for k in triangles[a.name][i]),start=a.location.copy())/3
        pairchecks[a.name[0]+b.name[0]]['samples_mm'].append([round(x*1000,1) for x in p])
report={'skins':checks,'pairs':pairchecks}
(out/'Intersection-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
