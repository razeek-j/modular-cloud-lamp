"""Render concept views and report digital geometry facts; never validates physical fitness."""
import bpy
import json
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree

ROOT=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use=d.type=='METAL'
    s.cycles.device='GPU'
except Exception:
    s.cycles.device='CPU'
s.cycles.samples=48
s.render.resolution_x=1200
s.render.resolution_y=860
s.render.resolution_percentage=100

bands=list(bpy.data.collections['01 RIBBONS — editable surfaces'].objects)
trees={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                                [tuple(p.vertices) for p in o.data.polygons]) for o in bands}
intersections=[]
for i,a in enumerate(bands):
    for b in bands[i+1:]:
        count=len(trees[a.name].overlap(trees[b.name]))
        intersections.append({'a':a.name,'b':b.name,'surface_triangle_overlap_pairs':count})
report={'check':'Pairwise ribbon base surface intersections',
        'limitations':'Digital surface check only; excludes skin, self-intersection, support and print/physical validation',
        'results':intersections}
(ROOT/'checks/surface-intersections.json').write_text(json.dumps(report,indent=2))
print('SURFACE CHECK',json.dumps(report),flush=True)

s.camera=bpy.data.objects['CAM 01 • warm ceiling view']
s.render.filepath=str(ROOT/'renders/01-warm-ceiling-concept.png')
bpy.ops.render.render(write_still=True)

if '--hero-only' not in sys.argv:
    for o in bpy.data.collections['05 LIGHTING — artistic preview'].objects:
        if 'preview only' in o.name:
            o.data.energy=0
        elif 'fill' in o.name:
            o.data.energy=40
            o.data.color=(1,1,1)
    s.world.node_tree.nodes.get('Background').inputs[1].default_value=.40
    s.view_settings.exposure=.2
    s.render.resolution_x=1200
    s.render.resolution_y=1200
    s.camera=bpy.data.objects['CAM 02 • circular underside']
    s.render.filepath=str(ROOT/'renders/02-unlit-circular-underside.png')
    bpy.ops.render.render(write_still=True)

print('RENDER COMPLETE',flush=True)
