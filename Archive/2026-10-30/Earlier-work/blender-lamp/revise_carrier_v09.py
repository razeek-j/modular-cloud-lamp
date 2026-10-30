"""Revise only the carrier in the user's centered final, preserving the source."""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path('/Users/razeek/Projects/3D printing')
OUT = ROOT / 'output/blender-lamp'
sys.path.insert(0, str(OUT))
import build_lamp as base

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'lamp-centered-final.blend'))
scene = bpy.data.scenes['02 • Full 360 Assembly']
bpy.context.window.scene = scene
bpy.context.view_layer.update()
original = scene.objects['LAMP_Full Carrier']
old_mesh = original.data
collection = bpy.data.collections.new('V09 temporary construction')
scene.collection.children.link(collection)
material = old_mesh.materials[0]

# Keep the external LED mounting diameter and bottom support elevation unchanged.
carrier = base.annulus('V09 carrier construction', 105.2, .8, -30, 7,
                       collection, mat=material)
brim = base.annulus('V09 bottom brim', 105.75, 1.9, -31, -29.95, collection)
base.boolean_apply(carrier, brim, 'UNION')
bpy.data.objects.remove(brim, do_unlink=True)

# A local inward backing allows a deeper external wire channel without thinning
# the entire tube or cutting through the remaining 0.8 mm rear wall.
angles = [math.radians(-3.2 + 6.4*i/32) for i in range(33)]
verts = [(r*math.cos(a), r*math.sin(a), z)
         for z,r in [(-14.9,102.8),(-14.9,105.61),(2.3,102.8),(2.3,105.61)]
         for a in angles]
n=len(angles); faces=[]
for i in range(n-1):
    j=i+1
    faces.extend([(i,j,n+j,n+i),(n+i,n+j,3*n+j,3*n+i),
                  (3*n+i,3*n+j,2*n+j,2*n+i),(2*n+i,2*n+j,j,i)])
faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
backing=base.mesh_object('V09 channel backing',verts,faces,collection)
base.boolean_apply(carrier,backing,'UNION')
bpy.data.objects.remove(backing,do_unlink=True)

def cut(label,x0,x1,y0,y1,z0,z1):
    box=base.oriented_box(label,x0,x1,y0,y1,z0,z1,0,collection)
    base.boolean_apply(carrier,box)
    bpy.data.objects.remove(box,do_unlink=True)

cut('V09 open rim notch',101,110,-5,5,2,8)
cut('V09 deep lead channel',103.6,110,-4,4,-15,2.1)
cut('V09 lower access port',100,110,-6,6,-27,-14)
cut('V09 downward wire exit',100,110,-3,3,-33,-25)
base.recalc(carrier.data)
bm=bmesh.new();bm.from_mesh(carrier.data)
for face in bm.faces:
    face.smooth=abs(face.normal.z)<.95
for edge in bm.edges:
    edge.smooth=not(edge.is_manifold and edge.calc_face_angle()>.5)
bm.to_mesh(carrier.data);bm.free();carrier.data.update()

new_mesh=carrier.data
new_mesh.name='LAMP V09 thin carrier with backed deep wire channel'
updated=[]
for obj in list(bpy.data.objects):
    if obj.data==old_mesh:
        obj.data=new_mesh
        obj['V09 carrier']='0.8 mm main wall; 1.1 mm outward bottom overhang; backed 2 mm-deep channel.'
        updated.append(obj.name)
bpy.data.objects.remove(carrier,do_unlink=True)
bpy.data.collections.remove(collection)
bpy.context.view_layer.update()

def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [tuple(p.vertices) for p in obj.data.polygons])
carrier=scene.objects['LAMP_Full Carrier'];ct=tree(carrier)
def radial_hits(z,angle):
    a=math.radians(angle);d=Vector((math.cos(a),math.sin(a),0));p=Vector((0,0,z));hits=[]
    for _ in range(8):
        h=ct.ray_cast(p,d,150)
        if h[0] is None:break
        hits.append(math.hypot(h[0].x,h[0].y));p=h[0]+d*.001
    return hits
bm=bmesh.new();bm.from_mesh(new_mesh)
unseen=set(bm.verts);components=0
while unseen:
    components+=1;stack=[unseen.pop()]
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            q=e.other_vert(v)
            if q in unseen:unseen.remove(q);stack.append(q)
report={
    'source':'lamp-centered-final.blend','output':'lamp-thin-carrier-v09.blend',
    'main_wall_mm':.8,'outer_wall_radius_mm':105.6,'height_with_brim_mm':38,
    'bottom_brim_height_mm':1.05,'bottom_brim_outward_overhang_mm':1.1,
    'bottom_brim_total_radial_width_mm':1.9,
    'wire_channel_width_mm':8,'wire_channel_depth_at_center_mm':2,
    'wire_channel_backing_wall_mm':.8,'top_notch_width_mm':10,
    'updated_objects':updated,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
    'connected_components':components,'volume_mm3':abs(bm.calc_volume(signed=True)),
    'radial_samples':{f'z{z}_angle{a}':radial_hits(z,a) for z,a in [(-10,90),(-10,0),(-30.5,90),(3,0)]},
    'carrier_vs_shade_surface_pairs':{o.name:len(ct.overlap(tree(o))) for o in scene.objects if 'Segment' in o.name},
    'unchanged_issue':'Three stand leg roots intersect shade, as documented in prior audit. Stand and shade were not modified.',
    'physical_status':'Provisional dimensions; actual clip, wires, connector and print fit not measured.'
}
bm.free()
assert report['nonmanifold_edges']==0 and components==1,report
assert all(v==0 for v in report['carrier_vs_shade_surface_pairs'].values()),report

# A separate inspection scene makes the notch, channel and glue brim easy to review.
detail=bpy.data.scenes.new('04 • V09 thin carrier detail')
detail.unit_settings.system='METRIC';detail.unit_settings.scale_length=.001
for source in [carrier,scene.objects['LAMP_Full LED strip']]:
    obj=source.copy();obj.data=source.data;detail.collection.objects.link(obj)
detail.display.shading.color_type='MATERIAL';detail.display.shading.light='STUDIO'
detail.display.shading.show_cavity=True
d=bpy.data.cameras.new('V09 inspection camera');camera=bpy.data.objects.new('V09 inspection camera',d)
detail.collection.objects.link(camera);camera.location=(430,-190,170)
camera.rotation_euler=(Vector((0,0,-12))-camera.location).to_track_quat('-Z','Y').to_euler()
d.type='ORTHO';d.ortho_scale=250;detail.camera=camera
detail.render.engine='BLENDER_WORKBENCH';detail.render.resolution_x=1500;detail.render.resolution_y=1100
detail.render.resolution_percentage=100
bpy.context.window.scene=detail
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            view=area.spaces.active.region_3d
            view.view_location=(0,0,-12);view.view_distance=300
            view.view_rotation=camera.rotation_euler.to_quaternion();view.view_perspective='ORTHO'
note=bpy.data.texts.new('V09 carrier changes and checks');note.write(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'lamp-thin-carrier-v09.blend'))
(OUT/'carrier-v09-checks.json').write_text(json.dumps(report,indent=2))
detail.render.filepath=str(OUT/'carrier-v09-preview.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
