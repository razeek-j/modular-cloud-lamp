"""Small live presentation edit, recorded separately from the geometry build."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')

def step_one():
    # Remove the presentation ceiling's edge from the hero camera's field of view.
    ceiling=bpy.data.objects['Presentation ceiling • hide in viewport']
    ceiling.scale=(5,5,5)
    bpy.data.objects['CAM 02 • circular underside'].location=(.001,-.001,-2.5)
    bpy.data.objects['CAM 02 • circular underside'].data.lens=44
    bpy.context.scene['progress']='Presentation refinement • complete underside framing'
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.region_3d.view_rotation=Vector((0,0,-1)).to_track_quat('Z','Y')
            sp.region_3d.view_distance=1.8
    bpy.app.timers.register(step_two,first_interval=5)

def step_two():
    # Inspect rib detail from below; this is a viewport inspection, not a geometry edit.
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.region_3d.view_rotation=Vector((1.3,-1.8,-1.1)).to_track_quat('Z','Y')
            sp.region_3d.view_distance=1.65
    bpy.app.timers.register(save,first_interval=5)

def save():
    for name,filename in [('START HERE • project plan','PLAN.md'),('PROCESS • journal','PROCESS.md'),
                          ('SOURCE • build_concept.py','scripts/build_concept.py'),
                          ('PROJECT INSTRUCTIONS • recording','AGENTS.md')]:
        t=bpy.data.texts.get(name) or bpy.data.texts.new(name)
        t.clear()
        t.write((ROOT/filename).read_text())
    bpy.context.scene['progress']='Concept v01 • silhouette review; support concealment unresolved'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Circular-Ribbon-Concept-v01.blend'),compress=True)

if bpy.context.area and bpy.context.area.type=='CONSOLE':
    bpy.context.area.type='VIEW_3D'
bpy.app.timers.register(step_one,first_interval=3)
