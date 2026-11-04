"""Pairwise triangle intersections; does not measure minimum clearance or retention."""
import bpy, json
from itertools import combinations
from pathlib import Path
from mathutils.bvhtree import BVHTree

root=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
objects=list(bpy.data.collections['V04 01 • FLUSH CLOUD / actual surfaces'].objects)
trees={}
for ob in objects:
    me=ob.data
    me.calc_loop_triangles()
    verts=[ob.matrix_world@v.co for v in me.vertices]
    trees[ob.name]=BVHTree.FromPolygons(verts,[list(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=0)
rows=[]
for a,b in combinations(objects,2):
    rows.append(dict(a=a.name,b=b.name,intersecting_triangle_pairs=len(trees[a.name].overlap(trees[b.name]))))
report=dict(scope='Actual V04 band meshes including integral returns; pairwise only, no minimum clearance or self-intersection check.',pairs=rows)
(root/'checks/v04-intersections.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
