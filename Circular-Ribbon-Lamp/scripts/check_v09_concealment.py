"""Sample first-hit geometry from the two room review cameras."""
import collections, json
from pathlib import Path
import bpy
from mathutils import Vector
s=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
groups={'04 · Metal branch and saddle layout':'carrier',
        '05 · Selected COB stations':'LED channels',
        '06 · 24 V loom, inside the carrier routes':'wire'}
report={}
for cam in [bpy.data.objects["01 · Directly below — reference angle"],bpy.data.objects["02 · Room angle"]]:
    counts=collections.Counter()
    names=collections.Counter()
    m=cam.matrix_world
    direction=-m.col[2].xyz
    for row in range(162):
        for col in range(243):
            x = ((col + .5) / 243 - .5) * cam.data.ortho_scale
            y = ((row + .5) / 162 - .5) * cam.data.ortho_scale * 2 / 3
            p = m @ Vector((x, y, 0))
            hit,where,n,i,obj,matrix=s.ray_cast(deps,p,direction)
            if hit:
                tags=[groups[c.name] for c in obj.users_collection if c.name in groups]
                if tags:
                    counts.update(tags)
                    names[obj.name]+=1
    report[cam.name]={'rays':162*243,'first_hit_hardware':dict(counts),'objects':dict(names)}
print(json.dumps(report,indent=2))
(Path(bpy.data.filepath).parent/'View-check.json').write_text(json.dumps(report,indent=2)+"\n")
