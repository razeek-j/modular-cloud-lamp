"""Blender concept authoring. Run from Blender's Python console or with --background.

UI: exec(compile(open(PATH).read(), PATH, 'exec'))
Background: blender -b --factory-startup --python PATH -- --batch
The UI run performs the genuine build in spaced steps for screen recording.
"""
import bpy
import math
import json
import sys
import traceback
from pathlib import Path
from mathutils import Vector

ROOT = Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
TAU = math.tau
BATCH = '--batch' in sys.argv
CONFIG = {
    'diameter_mm': 1200,
    'skin_mm': 1.2,
    'rib_pitch_mm': 3.2,
    'rib_relief_mm': 0.22,
    'bands': [
        dict(name='01 Outer flowing ribbon', radius=.480, width=.184, radial_wave=.023,
             z=-.160, z_wave=.024, lobes=3, phase=.25, twist=2, roll=.25),
        dict(name='02 Middle counterflow ribbon', radius=.302, width=.180, radial_wave=.022,
             z=-.166, z_wave=.025, lobes=3, phase=1.40, twist=-2, roll=1.45),
        dict(name='03 Inner folded ribbon', radius=.144, width=.112, radial_wave=.012,
             z=-.142, z_wave=.019, lobes=2, phase=.65, twist=1, roll=.75),
    ],
}
COL = {}
RIBBONS = []
MATS = {}


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    COL[name] = c
    return c


def move_to(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def simple_material(name, color, metallic=0, rough=.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    return m


def setup():
    # User requested a new project; current visible scene is the default startup cube.
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.users == 0 or c.name == 'Collection':
            bpy.data.collections.remove(c)
    s = bpy.context.scene
    s.name = '01 — Ribbon ceiling shade • concept'
    s.unit_settings.system = 'METRIC'
    s.unit_settings.length_unit = 'MILLIMETERS'
    s.unit_settings.scale_length = 1
    for name in ['01 RIBBONS — editable surfaces', '02 CANOPY',
                 '03 SUPPORT — provisional metal', '04 LED CARRIERS — provisional',
                 '05 LIGHTING — artistic preview', '06 PRESENTATION',
                 '07 GUIDES — not manufacturing geometry', '08 REFERENCE']:
        collection(name)
    MATS['shade'] = simple_material('Ivory diffusion • optical approximation', (.82,.77,.65), rough=.43)
    m = MATS['shade']
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Subsurface Weight'].default_value = .08
    p.inputs['Subsurface Radius'].default_value = (.004,.002,.001)
    trans = nt.nodes.new('ShaderNodeBsdfTranslucent')
    trans.inputs['Color'].default_value = (.86,.80,.67,1)
    mix = nt.nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .42
    nt.links.new(p.outputs['BSDF'], mix.inputs[1])
    nt.links.new(trans.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes.get('Material Output').inputs['Surface'])
    MATS['canopy'] = simple_material('Warm porcelain canopy',(.77,.74,.67),rough=.36)
    MATS['metal'] = simple_material('Powder coated support • warm white',(.72,.71,.66),metallic=.2,rough=.4)
    MATS['alu'] = simple_material('LED carrier • brushed aluminum',(.56,.58,.59),metallic=.8,rough=.3)
    MATS['ceiling'] = simple_material('Warm plaster',(.70,.65,.55),rough=.86)
    MATS['guide'] = simple_material('Guide grey',(.20,.26,.30))
    # The exact 1200 mm envelope is a guide, not an added physical ring.
    curve = bpy.data.curves.new('1200 mm circular envelope', 'CURVE')
    curve.dimensions = '3D'
    sp = curve.splines.new('POLY')
    sp.points.add(255)
    for i,p in enumerate(sp.points):
        a=TAU*i/256
        p.co=(.6*math.cos(a),.6*math.sin(a),-.16,1)
    sp.use_cyclic_u = True
    obj=bpy.data.objects.new('GUIDE • Ø1200 mm',curve)
    COL['07 GUIDES — not manufacturing geometry'].objects.link(obj)
    obj.hide_render=True
    obj.hide_set(True)
    s['design_status']='STAGE 1 — concept; not print ready'
    s['target_diameter_mm']=1200
    s['lighting_note']='Artistic preview, not a measured PETG or photometric simulation.'
    viewport()


def center_frame(t, p, flat=False):
    q=p['lobes']*t+p['phase']
    r=p['radius']+(0 if flat else p['radial_wave']*math.sin(q))
    z=p['z']+(0 if flat else p['z_wave']*math.sin(q+.65))
    C=Vector((r*math.cos(t),r*math.sin(t),z))
    # Project radial axis into the plane perpendicular to the local tangent.
    dr=0 if flat else p['radial_wave']*p['lobes']*math.cos(q)
    dz=0 if flat else p['z_wave']*p['lobes']*math.cos(q+.65)
    T=Vector((dr*math.cos(t)-r*math.sin(t),dr*math.sin(t)+r*math.cos(t),dz)).normalized()
    radial=Vector((math.cos(t),math.sin(t),0))
    R=(radial-T*radial.dot(T)).normalized()
    V=R.cross(T).normalized()
    roll=0 if flat else p['twist']*t+p['roll']+.20*math.sin(q)
    D=math.cos(roll)*R+math.sin(roll)*V
    N=T.cross(D).normalized()
    width=p['width']*(1 if flat else 1+.09*math.sin(q+.4))
    return C,D,N,width


def build_band(p, ribbed=False, flat=False):
    nt=640 if ribbed else 320
    nu=192 if ribbed else 20
    vertices=[]
    faces=[]
    for i in range(nt):
        t=TAU*i/nt
        C,D,N,w=center_frame(t,p,flat)
        for j in range(nu+1):
            f=j/nu-.5
            across=f*w
            relief=0
            if ribbed:
                # Longitudinal fine ribs: consistent base skin plus shallow rounded crests.
                edge_fade=min(1, (1-abs(f)*2)*20)
                relief=CONFIG['rib_relief_mm']/1000 * ((1+math.cos(TAU*f*p['width']/(CONFIG['rib_pitch_mm']/1000)))/2)**3*edge_fade
            vertices.append(tuple(C+across*D+relief*N))
    stride=nu+1
    for i in range(nt):
        nxt=(i+1)%nt
        for j in range(nu):
            faces.append((i*stride+j,nxt*stride+j,nxt*stride+j+1,i*stride+j+1))
    mesh=bpy.data.meshes.new(p['name']+' • editable grid')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(p['name'],mesh)
    COL['01 RIBBONS — editable surfaces'].objects.link(obj)
    obj.data.materials.append(MATS['shade'])
    for poly in mesh.polygons:
        poly.use_smooth=True
    solid=obj.modifiers.new('Skin • provisional 1.2 mm','SOLIDIFY')
    solid.thickness=CONFIG['skin_mm']/1000
    solid.offset=0
    solid.use_even_offset=True
    obj['concept_only']=True
    obj['parameters']=json.dumps(p)
    obj['editing']='Surface mesh remains editable. Rebuild dimensions/twists with scripts/build_concept.py; guides are reference only.'
    return obj


def replace_band(index, ribbed=False, flat=False):
    name=CONFIG['bands'][index]['name']
    old=bpy.data.objects.get(name)
    if old:
        oldmesh=old.data
        bpy.data.objects.remove(old,do_unlink=True)
        if oldmesh.users==0:
            bpy.data.meshes.remove(oldmesh)
    obj=build_band(CONFIG['bands'][index],ribbed,flat)
    return obj


def viewport():
    quat=Vector((1.3,-1.8,-1.1)).to_track_quat('Z','Y')
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active
                sp.region_3d.view_location=(0,0,-.155)
                sp.region_3d.view_distance=1.65
                sp.region_3d.view_rotation=quat
                sp.region_3d.view_perspective='ORTHO'
                sp.clip_start=.001
                sp.clip_end=100
                sp.overlay.show_floor=False
                sp.overlay.show_axis_x=False
                sp.overlay.show_axis_y=False
                sp.shading.type='SOLID'
                sp.shading.color_type='MATERIAL'
                sp.shading.light='STUDIO'
                sp.shading.studiolight_rotate_z=.3
                sp.shading.show_cavity=True
                sp.shading.cavity_type='BOTH'
                sp.shading.curvature_ridge_factor=1.2
                sp.shading.curvature_valley_factor=1.0
                sp.shading.background_type='WORLD'
                sp.shading.show_shadows=True
    bpy.ops.object.select_all(action='DESELECT')


def cylinder(name,radius,depth,z,material,col):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=(0,0,z))
    o=move_to(bpy.context.object,col)
    o.name=name
    o.data.materials.append(material)
    bevel=o.modifiers.new('Soft machined edges','BEVEL')
    bevel.width=.002
    bevel.segments=3
    for poly in o.data.polygons:
        poly.use_smooth=True
    return o


def beam(name,a,b,width,depth,material,col):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2)
    o=move_to(bpy.context.object,col)
    o.name=name
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=(b-a).to_track_quat('X','Z')
    o.scale=((b-a).length,width,depth)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    bevel=o.modifiers.new('Edge radius','BEVEL')
    bevel.width=.001
    bevel.segments=2
    o['status']='Provisional carrier; hardware and loads unverified'
    return o


def support():
    can=COL['02 CANOPY']
    cylinder('Ceiling canopy • Ø230 mm',.115,.032,-.016,MATS['canopy'],can)
    cylinder('Canopy lower rim',.109,.005,-.034,MATS['canopy'],can)
    sc=COL['03 SUPPORT — provisional metal']
    cylinder('Central mounting hub • indicative',.060,.010,-.052,MATS['metal'],sc)
    for i in range(6):
        a=TAU*i/6+.15
        beam(f'Metal arm {i+1:02d} • indicative',(.045*math.cos(a),.045*math.sin(a),-.049),
             (.445*math.cos(a),.445*math.sin(a),-.065),.012,.005,MATS['metal'],sc)
    lc=COL['04 LED CARRIERS — provisional']
    for i in range(9):
        a=TAU*i/9+.25
        r=.35 if i%2 else .425
        center=Vector((r*math.cos(a),r*math.sin(a),-.095))
        tangent=Vector((-math.sin(a),math.cos(a),0))*.045
        beam(f'LED aluminum rail {i+1:02d} • indicative',center-tangent,center+tangent,.012,.004,MATS['alu'],lc)


def light(name,loc,target,energy,color,size,col):
    d=bpy.data.lights.new(name,'AREA')
    d.energy=energy
    d.color=color
    d.shape='DISK'
    d.size=size
    o=bpy.data.objects.new(name,d)
    col.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.hide_set(True)
    return o


def camera(name,loc,target,lens=50):
    d=bpy.data.cameras.new(name)
    d.lens=lens
    d.clip_start=.01
    d.clip_end=50
    o=bpy.data.objects.new(name,d)
    COL['06 PRESENTATION'].objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.hide_set(True)
    return o


def presentation():
    s=bpy.context.scene
    lc=COL['05 LIGHTING — artistic preview']
    for i in range(12):
        a=TAU*i/12+.10
        r=.37 if i%2 else .22
        light(f'Warm bounce {i+1:02d} • preview only',
              (r*math.cos(a),r*math.sin(a),-.075),
              ((r+.05)*math.cos(a),(r+.05)*math.sin(a),-.23),
              2.2,(1.0,.59,.29),.12,lc)
    light('Ceiling wash • preview only',(0,0,-.07),(0,0,.03),4,(1,.62,.32),.25,lc)
    light('Room soft fill',(0,-1.8,-1.7),(0,0,-.13),18,(.80,.87,1),2.4,lc)
    light('Side soft fill',(1.7,.8,-.9),(0,0,-.13),10,(1,.88,.72),1.8,lc)
    bpy.ops.mesh.primitive_plane_add(size=30,location=(0,0,.008))
    plane=move_to(bpy.context.object,COL['06 PRESENTATION'])
    plane.name='Presentation ceiling • hide in viewport'
    plane.data.materials.append(MATS['ceiling'])
    plane.hide_set(True)
    hero=camera('CAM 01 • warm ceiling view',(1.15,-1.85,-1.05),(0,0,-.145),52)
    camera('CAM 02 • circular underside',(.001,-.001,-2.5),(0,0,-.15),44)
    camera('CAM 03 • support layout',(.85,-1.35,.95),(0,0,-.14),52)
    s.camera=hero
    s.world.use_nodes=True
    s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.21,.24,.29,1)
    s.world.node_tree.nodes.get('Background').inputs[1].default_value=.20
    s.render.engine='CYCLES'
    s.cycles.samples=64
    s.cycles.use_denoising=True
    s.cycles.max_bounces=8
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='METAL'
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use=dev.type=='METAL'
        s.cycles.device='GPU'
    except Exception:
        s.cycles.device='CPU'
    s.render.resolution_x=1400
    s.render.resolution_y=1000
    s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'
    s.render.film_transparent=False
    s.view_settings.view_transform='AgX'
    s.view_settings.exposure=.7
    s.render.filepath=str(ROOT/'renders/01-warm-ceiling-concept.png')
    viewport()


def checkpoint(name):
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'checkpoints'/name),compress=True,copy=True)


def finish():
    global RIBBONS
    RIBBONS=[bpy.data.objects[p['name']] for p in CONFIG['bands']]
    # Normalize the complete shade's maximum radial envelope to 1200 mm.
    maxr=max(math.hypot(v.co.x,v.co.y) for o in RIBBONS for v in o.data.vertices)
    factor=.5994/maxr  # Allow for the outward half-skin thickness.
    for o in RIBBONS:
        for v in o.data.vertices:
            v.co.x*=factor
            v.co.y*=factor
        o.data.update()
    ref=bpy.data.images.load(str(ROOT/'references/design-reference.jpg'),check_existing=True)
    ref.pack()
    o=bpy.data.objects.new('REFERENCE • supplied photograph',None)
    o.empty_display_type='IMAGE'
    o.data=ref
    o.empty_display_size=1.2
    o.location=(0,1.1,-.14)
    o.rotation_euler=(math.pi/2,0,0)
    COL['08 REFERENCE'].objects.link(o)
    o.hide_render=True
    o.hide_set(True)
    for name,path in [('START HERE • project plan',ROOT/'PLAN.md'),
                      ('PROCESS • journal',ROOT/'PROCESS.md'),
                      ('SOURCE • build_concept.py',ROOT/'scripts/build_concept.py')]:
        text=bpy.data.texts.new(name)
        text.write(path.read_text())
    text=bpy.data.texts.new('PARAMETERS • concept configuration')
    text.write(json.dumps(CONFIG,indent=2))
    (ROOT/'checks/concept-parameters.json').write_text(json.dumps(CONFIG,indent=2))
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    allcoords=[o.matrix_world@v.co for o in RIBBONS for v in o.evaluated_get(deps).data.vertices]
    lo=[min(v[k] for v in allcoords) for k in range(3)]
    hi=[max(v[k] for v in allcoords) for k in range(3)]
    report={
        'status':'Stage 1 concept, not manufacturing geometry',
        'shade_bounds_mm':{'min':[v*1000 for v in lo],'max':[v*1000 for v in hi],
                           'size':[(hi[k]-lo[k])*1000 for k in range(3)]},
        'max_shade_radial_diameter_mm':max(math.hypot(v.x,v.y) for v in allcoords)*2000,
        'surface_bands':len(RIBBONS),
        'base_surface_quads':sum(len(o.data.polygons) for o in RIBBONS),
        'skin_mm':CONFIG['skin_mm'],
        'support_and_lighting':'Indicative placement only; not dimensioned hardware',
        'optics':'Artistic material and lighting approximation, not physical validation',
        'not_yet_validated':['self intersections','band intersections','support interference',
                             'print splits','load capacity','temperature','real PETG diffusion'],
        'normalization_xy_factor':factor,
    }
    (ROOT/'checks/concept-report.json').write_text(json.dumps(report,indent=2))
    for f,label in [(1,'01 Flat ribbon'),(40,'02 Twist'),(80,'03 Layered silhouette'),
                    (120,'04 Fine ribs'),(160,'05 Carrier concept')]:
        bpy.context.scene.timeline_markers.new(label,frame=f)
    bpy.context.scene.frame_end=200
    bpy.context.scene.frame_set(1)
    viewport()
    bpy.context.view_layer.objects.active=RIBBONS[0]
    bpy.context.scene['progress']='Concept v01 • ready for silhouette review'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Circular-Ribbon-Concept-v01.blend'),compress=True)
    print('CONCEPT COMPLETE',json.dumps(report),flush=True)


def flat():
    replace_band(0,flat=True)
    checkpoint('01-flat-ribbon.blend')


def twist():
    replace_band(0)
    checkpoint('02-twisted-ribbon.blend')


def layered():
    replace_band(1)
    replace_band(2)
    checkpoint('03-layered-silhouette.blend')


def ribs():
    for i in range(3):
        replace_band(i,ribbed=True)


STEPS=[('New circular project',setup),('Flat ribbon surface',flat),
       ('Twisting the outer ribbon',twist),('Layered counterflow ribbons',layered),
       ('Shallow fine ribs',ribs),('Canopy and metal carrier concept',support),
       ('Warm lighting and presentation views',presentation),('Pack reference and save concept',finish)]
_step_index=0


def next_step():
    global _step_index
    try:
        label,fn=STEPS[_step_index]
        print('BUILD STEP',_step_index+1,label,flush=True)
        fn()
        bpy.context.scene['progress']=label
        bpy.ops.object.select_all(action='DESELECT')
        for scr in bpy.data.screens:
            for area in scr.areas:
                area.tag_redraw()
        _step_index+=1
        return 4.0 if _step_index<len(STEPS) else None
    except Exception:
        (ROOT/'checks/build-error.txt').write_text(traceback.format_exc())
        traceback.print_exc()
        return None


if BATCH:
    for label,fn in STEPS:
        print('BUILD STEP',label,flush=True)
        fn()
else:
    # Return to the viewport before beginning the timer-driven edits.
    if bpy.context.area and bpy.context.area.type=='CONSOLE':
        bpy.context.area.type='VIEW_3D'
    bpy.app.timers.register(next_step,first_interval=4.0)
