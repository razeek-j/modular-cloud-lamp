"""Photo-guided, parametric FIRST BLOCKOUT, not recovered manufacturing CAD.

Run with Blender --background --python build_lamp.py -- --render
In the open Blender Python console:
  exec(compile(open(PATH).read(), PATH, 'exec'), {'__name__':'lamp_live'})
  (this registers the Lamp sidebar; it does not rebuild on import)
"""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

ROOT = Path('/Users/razeek/Projects/3D printing/output/blender-lamp')
PARAMS = ROOT / 'parameters.json'
BLEND = ROOT / 'lamp-segment-v05.blend'
PREFIX = 'LAMP_'
CONTROL = 'LAMP_Dimensions — PROVISIONAL mm'
SCENES = ['01 • Single segment', '02 • Circle check', '03 • Carrier fit']
FIELDS = [
 ('segment_count','Segments',3,36),
 ('centerline_radius_mm','Circle centerline radius',60,250),
 ('section_radial_radius_mm','Cross-section radial radius',15,100),
 ('section_vertical_radius_mm','Cross-section vertical radius',15,100),
 ('wall_mm','Shell wall',0.8,5), ('end_web_mm','End diaphragm',0.8,5),
 ('seam_gap_mm','Joint clearance at centerline',0.1,2),
 ('flute_count','Flutes around cross-section',4,20),
 ('flute_depth_mm','Flute depth',0,6),
 ('end_taper_fraction','End narrowing / pillow bulge',0,0.25),
 ('twist_degrees','Flute phase change per segment',0,720),
 ('carrier_radius_mm','Clear carrier wall radius',50,200),
 ('carrier_wall_mm','Clear carrier wall thickness',0.6,4),
 ('carrier_height_mm','Clear carrier height',20,100),
 ('carrier_bottom_mm','Clear carrier bottom Z',-80,30),
 ('slot_clearance_each_side_mm','Slot clearance each side',0.2,2),
 ('slot_bottom_clearance_mm','Slot bottom clearance',0.2,3),
 ('open_insertion_entry','Open entry for axial insertion',0,1),
]

def material(name, color, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.65
    bs.inputs['Metallic'].default_value=metallic
    return m

def recalc(mesh):
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free(); mesh.update()

def mesh_object(name, verts, faces, collection, mat=None):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces); me.update()
    recalc(me)
    o=bpy.data.objects.new(name,me); collection.objects.link(o)
    if mat:o.data.materials.append(mat)
    return o

def annulus(name, radius, width, bottom, top, collection, steps=720, mat=None):
    v=[]
    for z,r in [(bottom,radius-width/2),(bottom,radius+width/2),
                (top,radius-width/2),(top,radius+width/2)]:
        for i in range(steps):
            t=2*math.pi*i/steps; v.append((r*math.cos(t),r*math.sin(t),z))
    f=[]
    for i in range(steps):
        j=(i+1)%steps
        f.extend([(i,j,steps+j,steps+i),
                  (steps+i,steps+j,3*steps+j,3*steps+i),
                  (3*steps+i,3*steps+j,2*steps+j,2*steps+i),
                  (2*steps+i,2*steps+j,j,i)])
    return mesh_object(name,v,f,collection,mat)

def boolean_apply(obj,cutter,operation='DIFFERENCE'):
    mod=obj.modifiers.new('Geometric carrier clearance','BOOLEAN')
    mod.object=cutter; mod.operation=operation; mod.solver='EXACT'
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=mod.name)

def oriented_box(name, x0, x1, y0, y1, z0, z1, angle, collection):
    co=math.cos(angle); si=math.sin(angle)
    verts=[(x*co-y*si,x*si+y*co,z) for x,y,z in
           [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
            (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]]
    return mesh_object(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),
                                  (1,2,6,5),(2,3,7,6),(3,0,4,7)],collection)

def sector_mesh(p,collection,white):
    R=p['centerline_radius_mm']; rx=p['section_radial_radius_mm']; rz=p['section_vertical_radius_mm']
    w=p['wall_mm']; n=int(p['segment_count']); flute=int(p['flute_count'])
    half=math.pi/n-p['seam_gap_mm']/(2*R)
    umin=-half; umax=half; na=64
    # A single smooth arch per rib, terminating in one cusp at the valley.
    # No separate V-cut shoulders or narrow intermediate band.
    within=[j/64 for j in range(64)]
    sections=[(k+t)/flute for k in range(flute) for t in within]
    sharp_columns={k*len(within)+32 for k in range(flute)}
    nc=len(sections)
    web_angle=p['end_web_mm']/R
    verts=[]; faces=[]
    def loop(u,inner):
        frac=(u-umin)/(umax-umin)
        taper=1-p['end_taper_fraction']*(1-math.sin(math.pi*frac))
        for j,t in enumerate(sections):
            phase=2*math.pi*flute*t
            phi=2*math.pi*t+math.radians(p['twist_degrees'])*frac/flute
            ripple=p['flute_depth_mm']*(2*abs(math.cos(phase/2))-1)
            if inner:
                a=rx*taper-w+ripple; b=rz*taper-w+ripple
            else:a=rx*taper+ripple; b=rz*taper+ripple
            radial=R+a*math.cos(phi)
            verts.append((radial*math.cos(u),radial*math.sin(u),b*math.sin(phi)))
    for inner in (False,True):
        start=umin+(web_angle if inner else 0)
        for i in range(na+1):loop(start+(umax-start)*i/na,inner)
    layer=(na+1)*nc
    for side in (0,1):
        off=side*layer
        for i in range(na):
            for j in range(nc):
                a=off+i*nc+j;b=off+i*nc+(j+1)%nc;c=b+nc;d=a+nc
                faces.append((a,b,c,d) if side==0 else (d,c,b,a))
    # Open end has just the thin rim joining outside and cavity surface.
    a=na*nc;b=layer+na*nc
    for j in range(nc):faces.append((a+j,a+(j+1)%nc,b+(j+1)%nc,b+j))
    # Other end is a thin diaphragm. Carrier passage is cut in the solid below.
    faces.append(tuple(reversed(range(nc))))
    faces.append(tuple(layer+j for j in range(nc)))
    obj=mesh_object('LAMP_Segment master',verts,faces,collection,white)
    # Solid exterior envelope: every holder is clipped against this volume.
    envelope_faces=faces[:na*nc]+[tuple(reversed(range(nc))),tuple(na*nc+j for j in range(nc))]
    # Keep the trims slightly inside the visible exterior to avoid coincident
    # faces with the shade shell; the wall still overlaps the supports.
    envelope_verts=[]
    for x,y,z in verts[:layer]:
        r=math.hypot(x,y);rr=R+(r-R)*.985
        envelope_verts.append((x*rr/r,y*rr/r,z*.985))
    envelope=mesh_object('LAMP_Temporary exterior envelope',envelope_verts,envelope_faces,collection)

    sharp=obj.data.attributes.new('sharp_edge','BOOLEAN','EDGE')
    for edge in obj.data.edges:
        a,b=edge.vertices
        sharp.data[edge.index].value=(abs(a-b)==nc and a%nc in sharp_columns)
    cwidth=p['carrier_wall_mm']+2*p['slot_clearance_each_side_mm']
    bottom=p['carrier_bottom_mm']-p['slot_bottom_clearance_mm']
    top=rz+p['flute_depth_mm']+10 if p['open_insertion_entry'] else p['carrier_bottom_mm']+p['carrier_height_mm']+p['slot_bottom_clearance_mm']
    cutter=annulus('LAMP_Temporary passage',p['carrier_radius_mm'],cwidth,bottom,top,collection)
    boolean_apply(obj,cutter)
    bpy.data.objects.remove(cutter,do_unlink=True)
    # Two apertures at each mating end. The holder planes use the exact
    # 30-degree joint bisectors, so bores on adjacent copies are coaxial.
    # This is an adjustable geometric proposal; separate insert clips absent.
    joint=math.pi/n
    for end,angle,sign in [('diaphragm',-joint,1),('open rim',joint,-1)]:
        gap=p['seam_gap_mm']/2
        # Coordinate Y points inward at the diaphragm, outward at the open rim.
        y0,y1=(gap+.2, gap+5) if sign==1 else (-gap-5,-gap-.2)
        for hz in (-30.0,30.0):
            hx=R
            z0,z1=(hz-5,43) if hz>0 else (-43,hz+5)
            # A strap to the adjacent shell supports the open-end holder.
            if sign==1:z0,z1=hz-5,hz+5
            holder=oriented_box('LAMP_Temporary clip holder',hx-5,hx+5,
                                y0,y1,z0,z1,angle,collection)
            boolean_apply(holder,envelope,'INTERSECT')
            boolean_apply(obj,holder,'UNION');bpy.data.objects.remove(holder,do_unlink=True)
            aperture=oriented_box('LAMP_Temporary clip opening',hx-2.5,hx+2.5,
                                  -9,9,hz-2.5,hz+2.5,angle,collection)
            boolean_apply(obj,aperture);bpy.data.objects.remove(aperture,do_unlink=True)
    # The intersection above enforces the original outside silhouette.
    bpy.data.objects.remove(envelope,do_unlink=True)
    recalc(obj.data)
    # Boolean attribute interpolation can discard sharp-edge flags; recompute
    # only actual dihedral creases, leaving the arch itself smoothly shaded.
    bm=bmesh.new();bm.from_mesh(obj.data)
    for edge in bm.edges:
        edge.smooth=not (edge.is_manifold and edge.calc_face_angle()>.35)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    obj['Holder containment']='Each holder intersected with solid original exterior envelope before union.'
    obj['Clip holders']='Two 5 x 5 mm openings at each mating end. Matching bores share joint-plane axes. Provisional dimensions.'
    # Keep cap/slot faces flat; smooth the continuous tube surfaces only.
    for poly in obj.data.polygons:poly.use_smooth=len(poly.vertices)==4
    obj['Purpose']='One curved sector. Open axial end, opposite thin web with carrier passage.'
    obj['Status']='FIRST BLOCKOUT — provisional dimensions; not approved for printing.'
    obj['Slot entry']='Open top entry is a fit hypothesis, adjustable in Lamp sidebar.'
    obj['Rib profile']='One smooth rounded arch per rib; one sharp valley, no groove shoulders.'
    return obj

def collection(scene,name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c

def setup_scene(name):
    s=bpy.data.scenes.new(name)
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
    s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'
    d=s.display.shading;d.light='STUDIO';d.color_type='MATERIAL';d.show_shadows=True;d.show_cavity=True
    d.cavity_type='BOTH';d.curvature_ridge_factor=1.2;d.curvature_valley_factor=1.0
    d.background_type='WORLD';d.background_color=(.075,.085,.10)
    s.world=bpy.data.worlds.new(name+' world');s.world.color=(.075,.085,.1)
    return s

def camera(scene,collection,pos,target,scale):
    data=bpy.data.cameras.new('LAMP_Camera '+scene.name)
    o=bpy.data.objects.new(data.name,data);collection.objects.link(o);o.location=pos
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=scale;data.clip_start=.1;data.clip_end=5000;scene.camera=o
    o.hide_viewport=True
    return o

def guide_curve(name, radius,z, collection,color):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=.20;cu.bevel_resolution=1
    sp=cu.splines.new('POLY');sp.points.add(359)
    for i,pt in enumerate(sp.points):
        a=i*2*math.pi/360;pt.co=(radius*math.cos(a),radius*math.sin(a),z,1)
    sp.use_cyclic_u=True
    o=bpy.data.objects.new(name,cu);collection.objects.link(o);cu.materials.append(color);o.hide_render=True
    return o

def bvh_for(obj,matrix=None):
    m=matrix if matrix is not None else obj.matrix_world
    verts=[m@v.co for v in obj.data.vertices]
    polys=[tuple(f.vertices) for f in obj.data.polygons]
    return BVHTree.FromPolygons(verts,polys,all_triangles=False)

def mesh_stats(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    r={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
       'connected_components':0,'volume_mm3':abs(bm.calc_volume(signed=True))}
    unseen=set(bm.verts)
    while unseen:
        stack=[unseen.pop()];r['connected_components']+=1
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                q=e.other_vert(v)
                if q in unseen:unseen.remove(q);stack.append(q)
    bm.free();return r

def reference_board(scene,coll,p):
    # Packed ORIGINAL photographs, viewport-only, intentionally no AI reconstructions.
    refs=[('printed-segments.png','Original: individual parts'),
          ('segment-underside.png','Original: opposite face and passage'),
          ('assembled-arcs.png','Original: curved assembly')]
    for i,(filename,label) in enumerate(refs):
        im=bpy.data.images.load(str(ROOT/'reference'/filename),check_existing=True);im.pack()
        o=bpy.data.objects.new('LAMP_REF '+label,None);coll.objects.link(o)
        o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=140
        o.location=(-230+155*i,160,55);o.rotation_euler=(math.pi/2,0,0)
        o.hide_render=True;o.hide_viewport=True

def text_notes(p,report):
    t=bpy.data.texts.get('READ ME — first geometry iteration') or bpy.data.texts.new('READ ME — first geometry iteration')
    t.clear();t.write('PHOTO-GUIDED LAMP / FIRST GEOMETRY ITERATION\n\n'
      '01 Single segment: one curved part in its printing/review orientation.\n'
      '02 Circle check: linked copies of the same mesh around the circle.\n'
      '03 Carrier fit: three separated sectors plus a cyan test cylinder wall.\n\n'
      'This is a parametric engineering hypothesis, NOT the original CAD recovered from photographs.\n'
      'All dimensions are provisional millimeters. Count 12 is inferred from the original photo layout.\n'
      'The module is a short toroidal sector, not a complete small lampshade.\n'
      'One end is open; its opposite end has a thin diaphragm and a carrier slot.\n'
      'The user confirmed the CLEAR LED CYLINDER passes through this slot.\n'
      'The entry is provisionally open toward the upper inner shoulder to permit axial insertion.\n'
      'Toggle Open entry to compare an enclosed slot; this requires a different insertion path.\n'
      'Flutes, twist, carrier size and entry shape require visual approval.\n'
      'The separate clip, carrier flange, LEDs and brown stand are intentionally\n'
      'not built in this first part blockout. Carrier fit covers the simple cylindrical WALL ONLY.\n'
      'No physical-print fit has been demonstrated. No claim of exact source dimensions.\n\n'
      'PARAMETERS\n'+json.dumps(p,indent=2)+'\n\nCHECKS\n'+json.dumps(report,indent=2))
    t=bpy.data.texts.get('build_lamp.py') or bpy.data.texts.new('build_lamp.py');t.clear();t.write(Path(__file__).read_text() if '__file__' in globals() else (ROOT/'build_lamp.py').read_text())

def holder_alignment(p):
    n=int(p['segment_count']); theta=2*math.pi/n; R=p['centerline_radius_mm']
    joint=theta/2; gap=p['seam_gap_mm']/2
    rot=Matrix.Rotation(theta,4,'Z')
    a=Matrix.Rotation(joint,4,'Z'); b=rot@Matrix.Rotation(-joint,4,'Z')
    normal=a.to_3x3()@Vector((0,1,0))
    checks=[]
    for z in (-30.0,30.0):
        pa=a@Vector((R,-gap,z));pb=b@Vector((R,gap,z))
        d=pb-pa; across=d.dot(normal); offset=(d-normal*across).length
        axis_b=b.to_3x3()@Vector((0,1,0))
        checks.append({'height_mm':z,'axis_lateral_error_mm':offset,
                       'axis_angle_error_degrees':math.degrees(normal.angle(axis_b)),
                       'joint_gap_mm':abs(across)})
    return checks

def build_project(p=None,save=True):
    p=p or json.loads(PARAMS.read_text())
    assert p['wall_mm']<min(p['section_radial_radius_mm'],p['section_vertical_radius_mm'])/4
    old=bpy.context.window.scene
    temp=bpy.data.scenes.new('LAMP temporary rebuild')
    bpy.context.window.scene=temp
    for name in SCENES:
        if name in bpy.data.scenes:bpy.data.scenes.remove(bpy.data.scenes[name])
    # Only our named objects are cleaned during regeneration.
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
    for c in list(bpy.data.collections):
        if c.name.startswith(PREFIX):bpy.data.collections.remove(c)
    single,assembly,fit=[setup_scene(n) for n in SCENES]
    sc=collection(single,'LAMP_01 Single editable mesh');ac=collection(assembly,'LAMP_02 Linked circular copies')
    fc=collection(fit,'LAMP_03 Wall fit study');rc=collection(single,'LAMP_Original photo references (hidden)')
    white=material('LAMP White polymer',(.84,.84,.80));cyan=material('LAMP Carrier test wall',(.09,.55,.62))
    guide=material('LAMP Guide blue',(.12,.35,.65))
    bpy.context.window.scene=assembly
    master=sector_mesh(p,ac,white)
    master.name='LAMP_Segment 01 — master shared mesh'
    copies=[master]
    n=int(p['segment_count']);R=p['centerline_radius_mm']
    # Keep the editable part's origin near its own center, while sharing one mesh.
    for v in master.data.vertices:v.co.x-=R
    master.location.x=R
    for i in range(1,n):
        o=bpy.data.objects.new('LAMP_Segment %02d — linked'%(i+1),master.data);ac.objects.link(o)
        o.matrix_world=Matrix.Rotation(2*math.pi*i/n,4,'Z')@Matrix.Translation((R,0,0));copies.append(o)
    one=bpy.data.objects.new('LAMP_Single segment — EDIT THIS MESH',master.data);sc.objects.link(one)
    # Rotate the sector so its open tangential face points upward, like the printed source part.
    one.matrix_world=Matrix.Translation((0,0,36))@Matrix.Rotation(math.pi/2,4,'X')
    control=bpy.data.objects.new(CONTROL,None);sc.objects.link(control);control.empty_display_type='PLAIN_AXES';control.empty_display_size=8
    control.hide_render=True;control.hide_viewport=True
    for key,label,mn,mx in FIELDS:
        control[key]=p[key]
        if not isinstance(p[key],bool):control.id_properties_ui(key).update(min=mn,max=mx,description=label+' — PROVISIONAL')
    control['dimension_status']='UNMEASURED / first blockout'
    ac.objects.link(control);fc.objects.link(control)
    # Sparse sectors expose the cylinder's passage through the end diaphragms.
    for i in (0,n//3,2*n//3):
        o=bpy.data.objects.new('LAMP_Fit sector %02d'%i,master.data);fc.objects.link(o)
        o.matrix_world=Matrix.Rotation(2*math.pi*i/n,4,'Z')@Matrix.Translation((R,0,0))
    carrier=annulus('LAMP_Test carrier CYLINDER WALL ONLY',p['carrier_radius_mm'],p['carrier_wall_mm'],
        p['carrier_bottom_mm'],p['carrier_bottom_mm']+p['carrier_height_mm'],fc,mat=cyan)
    carrier['Limitation']='No flange, LEDs or joints; wall clearance only.'
    guide_curve('LAMP_Circle centerline guide',R,0,ac,guide)
    camera(single,sc,(30,-65,310),(0,0,38),155)
    camera(assembly,ac,(450,-600,460),(0,0,0),420)
    camera(fit,fc,(420,-520,350),(0,0,0),385)
    reference_board(single,rc,p)
    # Mesh-level checks, using the same geometry shared by every radial instance.
    bpy.context.view_layer.update()
    stats=mesh_stats(master)
    assert stats['vertices']>20000 and stats['volume_mm3']>20000, 'Shell lost during holder booleans'
    assert stats['nonmanifold_edges']==0 and stats['connected_components']==1, 'Invalid joined shell'
    seg_tree=bvh_for(master,master.matrix_world);other_tree=bvh_for(copies[1],copies[1].matrix_world)
    overlaps=seg_tree.overlap(other_tree)
    carrier_tree=bvh_for(carrier,Matrix.Identity(4))
    seated_pairs=len(seg_tree.overlap(carrier_tree))
    # Sample a straight axial insertion from above. This excludes the unmodeled flange.
    samples=[]
    for dz in [100,80,60,45,30,20,10,5,0]:
        tree=bvh_for(carrier,Matrix.Translation((0,0,dz)))
        samples.append({'offset_z_mm':dz,'intersecting_surface_pairs':len(seg_tree.overlap(tree))})
    bore_tests=[]
    for end,ang in [('open',math.pi/n),('diaphragm',-math.pi/n)]:
        rotation=Matrix.Rotation(ang,4,'Z')
        for zz in (-30.0,30.0):
            origin=rotation@Vector((R,-8,zz))
            direction=rotation.to_3x3()@Vector((0,1,0))
            hit=seg_tree.ray_cast(origin,direction,16)
            bore_tests.append({'end':end,'height_mm':zz,'centerline_clear':hit[0] is None})
    report={'actual_holder_bore_centerline_checks':bore_tests,'status':'PROVISIONAL geometric blockout, not measured or print-tested',
      'segment_mesh':stats,'segment_count':n,'step_degrees':360/n,
      'full_turn_degrees':(360/n)*n,
      'nominal_shade_outer_diameter_mm':2*(R+p['section_radial_radius_mm']),
      'nominal_shade_inner_diameter_mm':2*(R-p['section_radial_radius_mm']),
      'nominal_shade_height_mm':2*p['section_vertical_radius_mm'],
      'seam_gap_at_centerline_mm':p['seam_gap_mm'],
      'rib_profile':'single smooth arch ending in cusp; no intermediate band',
      'holder_containment':'Boolean intersection with solid original exterior envelope',
      'sharp_edges':sum(x.value for x in (master.data.attributes.get('sharp_edge').data if master.data.attributes.get('sharp_edge') else [])),
      'clip_holder_opening_mm':[5,5],
      'holder_openings_per_mating_end':2,
      'holder_openings_per_segment':4,
      'neighbor_holder_alignment':holder_alignment(p),
      'clip_holder_dimensions_status':'provisional visual estimate; separate clip not modeled',
      'adjacent_segment_surface_intersections':len(overlaps),
      'slot_radial_width_mm':p['carrier_wall_mm']+2*p['slot_clearance_each_side_mm'],
      'carrier_wall_mm':p['carrier_wall_mm'],
      'radial_clearance_each_side_mm':p['slot_clearance_each_side_mm'],
      'seated_carrier_wall_surface_intersections':seated_pairs,
      'sampled_vertical_insertion':samples,
      'insertion_samples_clear':all(x['intersecting_surface_pairs']==0 for x in samples),
      'not_checked':['physical dimensions','carrier flange','separate clip fit','LEDs','brown stand',
                     'continuous swept collision between sample positions','printer tolerances'],
      'shape_hypotheses':['30-degree toroidal sector','10 helical flutes',
                          'entry open through inner shoulder for vertical insertion']}
    (ROOT/'geometry-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    PARAMS.write_text(json.dumps(p,indent=2)+'\n')
    text_notes(p,report)
    # Save a useful editable viewport, focused on the single component.
    bpy.context.window.scene=single
    bpy.ops.object.select_all(action='DESELECT');one.select_set(True);bpy.context.view_layer.objects.active=one
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.clip_end=5000;sp.clip_start=.05
                sp.shading.color_type='MATERIAL';sp.shading.show_cavity=True
                sp.overlay.show_floor=False;sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
                sp.region_3d.view_distance=240;sp.region_3d.view_location=(0,0,38)
                sp.region_3d.view_rotation=single.camera.rotation_euler.to_quaternion();sp.region_3d.view_perspective='ORTHO'
    for s in list(bpy.data.scenes):
        if s==temp or (s.name=='Scene' and len(s.objects)<=3):bpy.data.scenes.remove(s)
    if save:
        bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print('LAMP_CHECKS',json.dumps(report))
    return report

def read_controls():
    c=bpy.data.objects.get(CONTROL)
    return {key:c[key] for key,_,_,_ in FIELDS}

class LAMP_OT_rebuild(bpy.types.Operator):
    bl_idname='lamp.rebuild';bl_label='Rebuild segment + circle + fit checks';bl_options={'REGISTER'}
    def execute(self,context):
        try:build_project(read_controls(),save=True)
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
        self.report({'INFO'},'Rebuilt shared mesh, circle and carrier checks. Saved v05.');return {'FINISHED'}

class LAMP_OT_scene(bpy.types.Operator):
    bl_idname='lamp.review_scene';bl_label='Review view'
    index:bpy.props.IntProperty(default=0)
    def execute(self,context):
        context.window.scene=bpy.data.scenes[SCENES[self.index]]
        scene=context.window.scene
        for area in context.screen.areas:
            if area.type=='VIEW_3D':
                region=area.spaces.active.region_3d
                region.view_rotation=scene.camera.rotation_euler.to_quaternion()
                region.view_location=(0,0,38) if self.index==0 else (0,0,0)
                region.view_distance=240 if self.index==0 else 500
                region.view_perspective='ORTHO'
        return {'FINISHED'}

class LAMP_PT_parameters(bpy.types.Panel):
    bl_label='Lamp — smooth arches and internal holders';bl_idname='LAMP_PT_parameters'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Lamp'
    def draw(self,context):
        l=self.layout;c=bpy.data.objects.get(CONTROL)
        if not c:l.label(text='Open lamp-segment-v05.blend');return
        l.label(text='All dimensions provisional (mm)',icon='INFO')
        row=l.row(align=True)
        for i,label in enumerate(['Single','Circle','Carrier fit']):
            op=row.operator('lamp.review_scene',text=label);op.index=i
        for key,label,_,_ in FIELDS:l.prop(c,'["'+key+'"]',text=label)
        l.operator('lamp.rebuild',icon='FILE_REFRESH')
        l.label(text='Carrier check covers wall only.')
        l.label(text='No flange/clip/physical fit validation.')

def register_ui():
    for cls in [LAMP_OT_rebuild,LAMP_OT_scene,LAMP_PT_parameters]:
        old=getattr(bpy.types,cls.__name__,None)
        if old:
            try:bpy.utils.unregister_class(old)
            except RuntimeError:pass
        bpy.utils.register_class(cls)
    return 'Lamp sidebar ready'

register_ui()
if __name__=='__main__':
    build_project()
    if '--render' in sys.argv:
        for name,filename in zip(SCENES,['single-segment.png','circle-check.png','carrier-fit.png']):
            scene=bpy.data.scenes[name];scene.render.filepath=str(ROOT/filename)
            bpy.ops.render.render(write_still=True,scene=name)
