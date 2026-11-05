"""Check centre footprint and sample what is directly visible in the room cameras."""
from collections import Counter
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
canopy = bpy.data.collections["02 · Compact centre mount and removable face"]
lighting = bpy.data.collections["03 · Three enclosed central lights and loom"]
radius = 0
for obj in [*canopy.objects, *lighting.objects]:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    radius = max(radius, *(math.hypot(*(evaluated.matrix_world @ vertex.co).xy)
                           for vertex in mesh.vertices))
    evaluated.to_mesh_clear()
assert radius <= .10501, radius
results = {}
for cam in sorted((o for o in scene.objects if o.type == "CAMERA"), key=lambda o:o.name):
    matrix = cam.matrix_world
    direction = -matrix.col[2].xyz
    scale = cam.data.ortho_scale
    seen = Counter()
    for row in range(128):
        for col in range(192):
            x = ((col + .5) / 192 - .5) * scale
            y = ((row + .5) / 128 - .5) * scale * 2 / 3
            hit, _, _, _, obj, _ = scene.ray_cast(deps, matrix @ Vector((x,y,0)), direction)
            if hit and (obj.name in lighting.objects or
                        (obj.name in canopy.objects and ("collar" in obj.name.lower() or "keeper" in obj.name.lower()))):
                seen[obj.name] += 1
    results[cam.name] = dict(rays=192*128,direct_hits=dict(seen))
data = dict(hardware_max_radius_mm=round(radius*1000,2), camera_sampling=results)
(Path(bpy.data.filepath).parent/"View-check.json").write_text(json.dumps(data,indent=2)+"\n")
print(json.dumps(data,indent=2))
