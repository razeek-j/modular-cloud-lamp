"""Editable carrier and stand draft, using the approved v06 shade as fit reference."""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path('/Users/razeek/Projects/3D printing/output/blender-lamp')
sys.path.insert(0,str(ROOT))
import build_lamp as base
NAMES=['04 • LED carrier','05 • Brown stand','06 • Cable route assembly']
P=dict(carrier_radius_mm=105.0,carrier_wall_mm=1.2,carrier_bottom_mm=-30.,carrier_top_mm=5.,
       flange_width_mm=3.4,flange_bottom_mm=-31.,flange_top_mm=-30.,
       upper_notch_width_mm=10.,upper_notch_bottom_mm=1.,recess_width_mm=8.,recess_depth_mm=.45,
       port_width_mm=12.,port_bottom_mm=-27.,port_top_mm=-14.,neck_width_mm=6.,
       stand_ring_width_mm=3.4,stand_bottom_mm=-36.,stand_top_mm=-31.,
       stand_exit_width_mm=8.,stand_exit_top_mm=-32.5,leg_tube_radius_mm=3.,foot_z_mm=-103.)

def cutbox(obj,name,x0,x1,y0,y1,z0,z1,coll):
    c=base.oriented_box('LAMP_CUT '+name,x0,x1,y0,y1,z0,z1,0,coll)
    base.boolean_apply(obj,c);bpy.data.objects.remove(c,do_unlink=True)

def tube(name,points,radius,coll,mat,closed=False,steps=16):
    verts=[];faces=[];pts=[Vector(p) for p in points]
    previous_u=None
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        ref=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((0,1,0))
        u=(previous_u-tangent*previous_u.dot(tangent)).normalized() if previous_u is not None else tangent.cross(ref).normalized()
        v=tangent.cross(u).normalized();previous_u=u
        for j in range(steps):
            a=j*2*math.pi/steps;verts.append(p+radius*(math.cos(a)*u+math.sin(a)*v))
    for i in range(len(pts)-1):
        for j in range(steps):
            k=(j+1)%steps;faces.append((i*steps+j,i*steps+k,(i+1)*steps+k,(i+1)*steps+j))
    faces += [tuple(reversed(range(steps))),tuple((len(pts)-1)*steps+j for j in range(steps))]
    o=base.mesh_object(name,verts,faces,coll,mat)
    for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
    return o

def bez(a,b,c,d,count=25):
    a,b,c,d=map(Vector,[a,b,c,d]);return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in [i/count for i in range(count+1)]]

def clone(obj,coll,name):
    o=bpy.data.objects.new(name,obj.data);coll.objects.link(o);o.matrix_world=obj.matrix_world;return o

def build():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'lamp-segment-v06.blend'))
    for name in NAMES:

        if name in bpy.data.scenes:bpy.data.scenes.remove(bpy.data.scenes[name])
    cs,ss,ass=[base.setup_scene(n) for n in NAMES]
    cc=base.collection(cs,'LAMP_04 Carrier');sc=base.collection(ss,'LAMP_05 Stand');ac=base.collection(ass,'LAMP_06 Assembly')
    clear=base.material('LAMP Clear PETG draft',(.48,.76,.80));brown=base.material('LAMP Brown stand',(.25,.075,.028))
    amber=base.material('LAMP LED strip display',(.95,.52,.035))
    bpy.context.window.scene=cs
    r=P['carrier_radius_mm'];w=P['carrier_wall_mm']
    carrier=base.annulus('LAMP_LED carrier — notch, recessed lead path, lower port',r,w,-30,P['carrier_top_mm'],cc,mat=clear)
    flange=base.annulus('LAMP_TEMP flange',r,P['flange_width_mm'],-31,-30,cc)
    base.boolean_apply(carrier,flange,'UNION');bpy.data.objects.remove(flange,do_unlink=True)
    # Front is +X. A rim dip, shallow outside recess and lower opening share one meridian.
    cutbox(carrier,'upper rim dip',101,109,-5,5,2.0,8.0,cc)
    cutbox(carrier,'outside lead recess',r+w/2-P['recess_depth_mm'],110,-4,4,-15,2.1,cc)
    cutbox(carrier,'lower connector opening',100,110,-6,6,-27,-14,cc)
    cutbox(carrier,'downward wire neck',100,110,-3,3,-33,-25,cc)
    carrier['Routing']='Upper LED-end dip > shallow outside recess > lower access port > downward neck.'
    carrier['Status']='PROVISIONAL. Wiring/connector dimensions not supplied. Flange chosen to fit v06 slot.'
    strip=base.annulus('LAMP_LED strip — display proxy only',106.0,.6,-4.0,4.0,cc,mat=amber)
    cutbox(strip,'LED ends gap',100,112,-7,7,-5,5,cc)
    bpy.context.window.scene=ss
    stand=base.annulus('LAMP_Brown stand — three hairpin legs and underside wire exit',105,P['stand_ring_width_mm'],-36,-31,sc,mat=brown)
    for k in range(3):
        th=k*2*math.pi/3;co=math.cos(th);si=math.sin(th)
        def xyz(x,y,z):return (co*x-si*y,si*x+co*y,z)
        x=105*math.cos(math.radians(11));y=105*math.sin(math.radians(11))
        # Rounded triangular loop, two separated roots and a rounded low foot.
        pts=bez(xyz(x,-y,-36.7),xyz(110,-17,-54),xyz(121,-5,-91),xyz(122,-5,-98),30)
        pts += [xyz(122,-5*math.cos(a),-98-5*math.sin(a)) for a in [i*math.pi/24 for i in range(1,25)]]
        pts += bez(xyz(122,5,-98),xyz(121,5,-91),xyz(110,17,-54),xyz(x,y,-36.7),30)[1:]
        leg=tube('LAMP_TEMP hairpin',pts,3,sc,brown)
        base.boolean_apply(stand,leg,'UNION');bpy.data.objects.remove(leg,do_unlink=True)
    cutbox(stand,'underside cable tunnel',97,113,-4,4,-38,-32.5,sc)
    stand['Cable exit']='8 mm wide x 3.5 mm high underside channel at +X, between the first leg roots.'
    stand['Status']='Photo-guided draft; unmeasured.'
    # Assembly shares the exact component meshes. Sparse shade sectors expose the route.
    clone(carrier,ac,'LAMP_Assembly carrier');clone(strip,ac,'LAMP_Assembly LED proxy');clone(stand,ac,'LAMP_Assembly stand')
    shade=bpy.data.scenes[base.SCENES[1]]
    for o in shade.objects:
        if o.type=='MESH' and 'Segment' in o.name:
            if any(t in o.name for t in ['04','08','12']):
                v=clone(o,ac,'LAMP_Route '+o.name)
                index=int(o.name.split('Segment ')[1][:2])-1
                v.matrix_world=Matrix.Rotation(index*2*math.pi/12,4,'Z')@Matrix.Translation((125,0,0))
    # Also add carrier and stand to 02 • Circle check for direct visualization with all 12 segments
    circ_coll=base.collection(shade,'LAMP_02 Stand and Carrier')
    clone(carrier,circ_coll,'LAMP_Circle carrier')
    clone(strip,circ_coll,'LAMP_Circle LED strip')
    clone(stand,circ_coll,'LAMP_Circle stand')
    # Update 03 • Carrier fit with the detailed carrier
    fit_scene=bpy.data.scenes.get(base.SCENES[2])
    if fit_scene:
        for oc in [o for o in fit_scene.objects if 'LAMP_Test carrier CYLINDER WALL ONLY' in o.name]:
            bpy.data.objects.remove(oc,do_unlink=True)
        fit_coll=fit_scene.collection.children.get('LAMP_03 Wall fit study') or fit_scene.collection
        clone(carrier,fit_coll,'LAMP_Fit carrier detailed')
        clone(strip,fit_coll,'LAMP_Fit LED strip')
    # Explicit three-wire bundle as inspection geometry, not a specified electrical design.
    wires=[]
    for i,(color,label) in enumerate([((.12,.12,.13),'dark'),((.65,.07,.04),'red'),((.05,.22,.6),'blue')]):
        m=base.material('LAMP Wire '+label,color);dy=(i-1)*2.4
        pts=[(105.3,dy,4.0),(105.3,dy,0.0),(105.3,dy,-14),(105.3,dy,-20),
             (99,dy,-22),(97,dy,-25),(97,dy,-31),(99,dy,-34.4),(111,dy,-34.4),
             (116,dy,-37),(119,dy,-44),(124,dy,-65),(132,dy,-100),(155,dy,-104)]
        wires.append(tube('LAMP_Wire route — '+label,pts,1.0,ac,m))
    for obj in [carrier,stand]:
        base.recalc(obj.data)
        # Flat port faces with smooth cylindrical and tubular surfaces.
        for f in obj.data.polygons:f.use_smooth=True
        bm=bmesh.new();bm.from_mesh(obj.data)
        for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle()>.5)
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    base.camera(cs,cc,(410,-150,180),(0,0,-12),250)
    base.camera(ss,sc,(410,-180,170),(0,0,-64),300)
    base.camera(ass,ac,(540,-270,310),(0,0,-35),410)
    # Verification against actual meshes.
    ct=base.bvh_for(carrier,Matrix.Identity(4));st=base.bvh_for(stand,Matrix.Identity(4))
    wire_hits=[len(st.overlap(base.bvh_for(o,Matrix.Identity(4)))) for o in wires]
    flange_hits=[];stand_shade_hits=[]
    for o in shade.objects:
        if o.type=='MESH' and 'Segment' in o.name:
            index=int(o.name.split('Segment ')[1][:2])-1
            mx=Matrix.Rotation(index*2*math.pi/12,4,'Z')@Matrix.Translation((125,0,0))
            tree=base.bvh_for(o,mx)
            flange_hits.append(len(ct.overlap(tree)));stand_shade_hits.append(len(st.overlap(tree)))
    report={'status':'Unmeasured component draft', 'parameters':P,
      'carrier_mesh':base.mesh_stats(carrier),'stand_mesh':base.mesh_stats(stand),
      'carrier_shade_intersecting_surface_pairs_by_segment':flange_hits,
      'stand_shade_intersecting_surface_pairs_by_segment':stand_shade_hits,
      'shade_fit_status':'Carrier clears v06 shade; stand has identified intersections at the three leg roots. Stand-to-shade fit is pending revision.',
      'stand_wire_intersecting_surface_pairs':wire_hits,
      'not_verified':['actual LED/connector and cable dimensions','electrical design','physical tolerances','print supports','stability under load'],
      'routing_hypothesis':'Upper dip/recess to lower port; cable turns inward/down then exits the underside of the brown ring at the same +X meridian.',
      'flange_note':'3.4 mm flange width fits the 4 mm v06 slot; 0.3 mm radial clearance per side; narrower than some apparent photo proportions.'}
    for key in ['carrier_mesh','stand_mesh']:
        assert report[key]['nonmanifold_edges']==0 and report[key]['connected_components']==1, report[key]
    (ROOT/'component-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'component-parameters.json').write_text(json.dumps(P,indent=2)+'\n')
    t=bpy.data.texts.new('READ ME — carrier and stand');t.write(json.dumps(report,indent=2))
    t=bpy.data.texts.new('build_components.py');t.write(Path(__file__).read_text())
    bpy.context.window.scene=ass
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                v=area.spaces.active.region_3d;v.view_location=(0,0,-35);v.view_distance=490;v.view_rotation=ass.camera.rotation_euler.to_quaternion();v.view_perspective='ORTHO'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'lamp-assembly-v07.blend'))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'lamp-segment-v06.blend'))
    for s,name in [(cs,'led-carrier-v07.png'),(ss,'brown-stand-v07.png'),(ass,'wire-route-v07.png')]:
        s.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True,scene=s.name)
    print('COMPONENT_CHECKS',json.dumps(report))


class LAMP_OT_component_view(bpy.types.Operator):
    bl_idname='lamp.component_view';bl_label='View lamp component'
    index:bpy.props.IntProperty(default=0)
    def execute(self,context):
        scene=bpy.data.scenes[NAMES[self.index]];context.window.scene=scene
        for area in context.screen.areas:
            if area.type=='VIEW_3D':
                v=area.spaces.active.region_3d;v.view_rotation=scene.camera.rotation_euler.to_quaternion()
                v.view_location=(0,0,-35 if self.index==2 else (-64 if self.index==1 else 0))
                v.view_distance=490 if self.index==2 else 350;v.view_perspective='ORTHO'
        return {'FINISHED'}
class LAMP_PT_components(bpy.types.Panel):
    bl_label='Carrier, stand and cable route';bl_idname='LAMP_PT_components'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Lamp parts'
    def draw(self,context):
        l=self.layout
        for i,label in enumerate(['LED carrier','Brown stand','Cable route assembly']):
            op=l.operator('lamp.component_view',text=label);op.index=i
        l.label(text='Draft dimensions; inspect before printing.')
        l.label(text='Cable bundle is a routing illustration.')
def register_parts_ui():
    for cls in [LAMP_OT_component_view,LAMP_PT_components]:
        old=getattr(bpy.types,cls.__name__,None)
        if old:
            try:bpy.utils.unregister_class(old)
            except RuntimeError:pass
        bpy.utils.register_class(cls)
register_parts_ui()

if __name__=='__main__':build()
