"""Generate the V11 design blockout and a separate full-scale joint section in Blender."""
import json
import math
import sys
from itertools import combinations
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "development-v11"
OUT.mkdir(exist_ok=True)
UP = Vector((0,0,1))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "01 | V11 three-ribbon layout"
def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result

def material(name, color, metal=0, translucent=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1)
    principled.inputs["Metallic"].default_value = metal
    principled.inputs["Roughness"].default_value = .57
    if translucent:
        diffuse = nodes.new("ShaderNodeBsdfTranslucent")
        diffuse.inputs[0].default_value = (*color, 1)
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = translucent
        links.new(principled.outputs[0], mix.inputs[1])
        links.new(diffuse.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], nodes.get("Material Output").inputs[0])
    return mat

def catmull(points, t, closed):
    index = math.floor(t)
    u = t - index
    if closed:
        p0, p1, p2, p3 = (points[i % len(points)] for i in range(index - 1, index + 3))
    else:
        p0, p1, p2, p3 = (points[max(0, min(i, len(points) - 1))] for i in range(index - 1, index + 3))
    return .5 * ((2 * p1) + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u**2
                 + (-p0 + 3 * p1 - 3 * p2 + p3) * u**3)

def unit(values):
    return values / np.linalg.norm(values, axis=-1, keepdims=True)

def mesh_object(name, vertices, faces, group, mat, smooth=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    if mat:
        mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = smooth
    return obj

def box(name, position, dimensions, group, mat, axes=None):
    origin = Vector(position)
    rotation = Matrix.Identity(3) if axes is None else Matrix(axes).transposed()
    corners = [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
               (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]
    vertices = [origin + rotation @ Vector([p * size / 2 for p, size in zip(c, dimensions)]) for c in corners]
    faces = [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    return mesh_object(name, vertices, faces, group, mat, False)

def cylinder(name, position, radius, depth, group, mat, count=96):
    x, y, z = position
    coords = [(x + radius * math.cos(i * math.tau / count),
               y + radius * math.sin(i * math.tau / count), z + h)
              for h in (-depth / 2, depth / 2) for i in range(count)]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2*count))]
    faces.extend((i, (i+1)%count, (i+1)%count+count, i+count) for i in range(count))
    return mesh_object(name, coords, faces, group, mat, False)

def camera(name, position, scale, target=(0,0,-.14), direct=False):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = scale
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = position
    if direct:
        obj.rotation_euler = (math.pi, 0, 0)
    else:
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

def light(name, position, target, power, color, size, group=None):
    data = bpy.data.lights.new(name,'AREA')
    data.shape = 'DISK'
    data.size = size
    data.energy, data.color = power, color
    obj = bpy.data.objects.new(name, data)
    (group or studio).objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

def bvh(obj):
    obj.data.calc_loop_triangles()
    return BVHTree.FromPolygons([v.co for v in obj.data.vertices],
                                [tuple(t.vertices) for t in obj.data.loop_triangles], all_triangles=True)

def difference(obj, cutter):
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Clearance","BOOLEAN")
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def wire_curve(name, points, radius, group, mat):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for v,p in zip(spline.points,points):
        v.co = (*p,1)
    obj = bpy.data.objects.new(name,curve)
    group.objects.link(obj)
    curve.materials.append(mat)
    return obj

def nonadjacent_hits(obj,tree):
    ids = [set(tri.vertices) for tri in obj.data.loop_triangles]
    return sum(1 for i,j in tree.overlap(tree) if i<j and ids[i].isdisjoint(ids[j]))

def solid_check(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges), obj.name
    remaining = set(bm.verts)
    nodes = [remaining.pop()]
    while nodes:
        for edge in nodes.pop().link_edges:
            for v in edge.verts:
                if v in remaining:
                    remaining.remove(v)
                    nodes.append(v)
    assert not remaining, obj.name
    assert bm.calc_volume(signed=True)>0, obj.name
    bm.free()
    tree = bvh(obj)
    return tree,nonadjacent_hits(obj,tree)

# Centreline stations in mm: X, Y, drop, projected width, crossfall.
# A sits behind the upper crossing, B sweeps across it, C returns below.
PATHS = {
    "A · Wide upper ribbon": [
        (-88,-53,49,136,-18),(-216,-106,53,142,-9),(-392,-135,48,162,15),
        (-496,-206,41,184,19),(-401,-358,36,201,12),(-235,-423,46,196,-15),
        (-83,-334,55,168,-14),(108,-273,50,168,12),(268,-341,38,181,23),
        (431,-327,43,184,-16),(487,-240,51,184,-17),(409,-162,51,151,10),
        (239,-130,56,118,12),(87,-81,55,112,-13),(13,-57,45,121,-11),
    ],
    "B · Middle crossing ribbon": [
        (-481,152,92,193,-20),(-542,48,99,190,-19),(-487,-53,102,174,18),
        (-341,-63,97,171,27),(-184,-29,93,155,-20),(-27,-33,93,119,-21),
        (133,-85,97,193,12),(308,-133,88,224,30),(458,-96,89,219,17),
        (513,3,97,190,-21),(483,137,102,199,-19),(391,209,101,188,17),
        (286,170,92,152,29),(209,93,83,131,10),(91,100,86,114,-17),
        (-46,111,93,116,-19),(-179,137,99,170,10),(-340,188,94,179,19),
    ],
    "C · Lower return ribbon": [
        (-398,278,135,163,-22),(-421,199,133,158,-19),(-344,125,128,177,18),
        (-189,107,135,184,20),(-64,101,136,151,-18),(81,160,135,163,-20),
        (191,227,135,168,21),(309,213,128,188,26),(403,281,130,179,-15),
        (375,365,139,170,-22),(237,417,139,183,19),(79,409,139,175,19),
        (-46,460,142,174,-21),(-181,461,141,173,-18),(-291,379,137,165,16),
    ],
}
DEPTHS = [(23,67), (71,111), (115,158)]

def set_scene(scene, background, exposure=0):
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.world = bpy.data.worlds.new(scene.name+" atmosphere")
    scene.world.use_nodes = True
    b = scene.world.node_tree.nodes.get("Background")
    b.inputs[0].default_value = (*background,1)
    b.inputs[1].default_value = .23
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 28
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = exposure

set_scene(scene,(.65,.56,.48))
skins=collection("01 · Continuous editable ribbon meshes")
guides=collection("02 · Source paths and joint study locations")
mount=collection("03 · Centre mount envelope")
lighting=collection("04 · Trial LED inside right bend")
studio=collection("05 · Reference views and studio")
paper=material("Washi ivory · milky finish study",(.93,.86,.73),translucent=.53)
ivory=material("Opaque ivory cap",(.89,.84,.74))
ceiling=material("Warm matte plaster",(.72,.59,.48))
metal=material("Matte aluminum",(.68,.65,.59),metal=.45)
cob=material("Warm COB tape package",(.94,.71,.31))
route_material=material("Guide only · teal",(.12,.39,.38))

def smooth(v,sigma):
    radius=math.ceil(3*sigma)
    weights=np.exp(-.5*(np.arange(-radius,radius+1)/sigma)**2)
    weights/=sum(weights)
    return sum(w*np.roll(v,j,axis=0) for j,w in zip(range(-radius,radius+1),weights))

def ribbon_grid(anchors,lo,hi,band):
    count=len(anchors)*15
    points=np.array([catmull(np.asarray(anchors,float),t,True)
                     for t in np.linspace(0,len(anchors),count,endpoint=False)])*.001
    points=smooth(points,3.1)
    c=points[:,:2]
    derivative=(np.roll(c,-1,axis=0)-np.roll(c,1,axis=0))/2
    tangent=unit(derivative)
    left=np.stack((-tangent[:,1],tangent[:,0]),axis=1)
    d_t=(np.roll(tangent,-1,axis=0)-np.roll(tangent,1,axis=0))/2
    k=smooth(np.sum(d_t*left,axis=1)/np.linalg.norm(derivative,axis=1),4.2)
    half=points[:,3]/2
    # The inside radius gently tapers. Softening the width limit keeps
    # tight turns from pinching and leaves the outside edge full-width.
    def concave_width(orientation):
        curv=np.maximum(orientation*k,0)
        return smooth(half/(1+(half*curv/.53)**4)**.25,3.1)
    width_left=concave_width(1)
    width_right=concave_width(-1)
    u=np.linspace(0,1,113)
    run=width_left[:,None]*u-width_right[:,None]*(1-u)
    xy=c[:,None,:]+left[:,None,:]*run[:,:,None]
    def smoothstep(x):
        v=np.clip(x,0,1)
        return v*v*(3-2*v)
    # More roll on isolated outer crests. Tighten the Z envelope near
    # the adjacent bands, where the surfaces need to clear each other.
    floor,ceil=lo*.001,hi*.001
    if band=="A":
        ceil=ceil+.025*smoothstep((-xy[...,1]-.273)/.104)
    elif band=="B":
        floor=floor-.020*smoothstep((xy[...,0]-.434)/.102)*smoothstep((xy[...,1]+.070)/.07)
        ceil=ceil+.020*smoothstep((-xy[...,0]-.46)/.110)
    else:
        floor=floor-.032*smoothstep((xy[...,1]-.27)/.125)
    mid=(lo+hi)*.0005
    nominal=mid+(points[:,2,None]-mid)*1.13+points[:,4,None]*(u-.5)*2.06+.007*np.sin(np.pi*u)
    z=-np.clip(nominal,floor,ceil)+.00031*np.cos(2*np.pi*22*u)[None,:]*np.sin(np.pi*u)**.6
    grid=np.dstack((xy,z))
    tangent3=(np.roll(grid,-1,axis=0)-np.roll(grid,1,axis=0))/2
    normal=unit(np.cross(tangent3,np.gradient(grid,axis=1)))
    return grid,normal

def closed_skin(name,grid,normal):
    rows,cols=grid.shape[:2]
    layer=rows*cols
    coords=np.concatenate(((grid-normal*.0008).reshape(-1,3),(grid+normal*.0008).reshape(-1,3)))
    faces=[]
    for r in range(rows):
        k=(r+1)%rows
        for c in range(cols-1):
            q=(r*cols+c,k*cols+c,k*cols+c+1,r*cols+c+1)
            faces.extend((q,tuple(i+layer for i in reversed(q))))
        for c in (0,cols-1):
            a,b=r*cols+c,k*cols+c
            faces.append((a,b,b+layer,a+layer))
    obj=mesh_object(name,coords.tolist(),faces,skins,paper)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    return obj

grids={}
bands={}
for (name,path),(lo,hi) in zip(PATHS.items(),DEPTHS):
    grid,normals=ribbon_grid(path,lo,hi,name[0])
    grids[name[0]]=grid
    ob=closed_skin(name,grid,normals)
    ob["Construction"]="Continuous layout master, nominal 1.6 mm skin. Support design and print division are separate milestones."
    bands[name[0]]=ob
    points=[Vector((x*.001,y*.001,-z*.001)) for x,y,z,_,_ in path]
    guide=wire_curve(name[0]+" centreline · design guide",points+[points[0]],.0015,guides,route_material)
    guide.hide_render=True
guides.hide_render=True

box("Ceiling datum",(0,0,.014),(5,5,.028),studio,ceiling)
plate=cylinder("Central metal mounting plate · layout envelope",(0,0,-.003),.101,.006,mount,metal)
cap=cylinder("Removable ivory centre cover · layout envelope",(0,0,-.118),.093,.004,mount,ivory)
cap["Status"]="Canopy envelope. Six captured root seats are reserved for the next mechanical layout."

trees={key:bvh(obj) for key,obj in bands.items()}
diagnostics={}
for key,obj in bands.items():
    diagnostics[key]=solid_check(obj)[1]
overlaps={a+b:len(trees[a].overlap(trees[b])) for a,b in combinations(bands,2)}
print("SKIN CHECKS",diagnostics,overlaps,flush=True)
# Sample a contiguous A/B overlap, sized for a future short hidden join.
hits=[]
for x in np.arange(.23,.45,.010):
    for y in np.arange(-.27,-.07,.010):
        origin_xy=Vector((float(x),float(y),.003))
        for theta in (-.45,0,.45,1.20):
            axial=Vector((math.cos(theta),math.sin(theta),0))
            transverse=UP.cross(axial)
            samples=[]
            for u in (-.033,0,.033):
                for v in (-.013,0,.013):
                    p=origin_xy+axial*u+transverse*v
                    a,na,_,_=trees["A"].ray_cast(p,-UP,.20)
                    b,nb,_,_=trees["B"].ray_cast(p,-UP,.20)
                    if a is not None and b is not None and abs(na.z)>.60 and abs(nb.z)>.60:
                        samples.append((a,b,a.z-b.z))
            if len(samples)!=9:
                continue
            distances=[d for _,_,d in samples]
            mean=sum(distances)/len(distances)
            if min(distances)<.003:
                continue
            score=abs(mean-.017)+(max(distances)-min(distances))*.44
            hits.append((score,samples[4],min(distances),max(distances),theta))
if hits:
    _,(p,q,gap),minimum,maximum,theta=min(hits,key=lambda x:x[0])
    for pos,label in ((p,"A parent surface"),(q,"B parent surface")):
        marker=wire_curve("Right overlap · "+label,[pos-UP*.005,pos+UP*.008],.002,guides,route_material)
        marker.hide_render=True
    right=dict(centre_gap_mm=round(gap*1000,2),sample_patch_mm=[66,26],
               sampled_gap_range_mm=[round(v*1000,2) for v in (minimum,maximum)],
               heading_degrees=round(math.degrees(theta),1),
               a_mm=[round(v*1000,1) for v in p],b_mm=[round(v*1000,1) for v in q])
else:
    right=None
print("RIGHT OVERLAP",right,flush=True)

# Search between A and B so the first strip washes the opposite ribbon.
# The emitter sits on B's rear side; A intercepts the upward beam.
def pick_light():
    lookup=list(trees.values())
    directions=[-UP,Vector((.55,-1.85,-.73)).normalized(),
                Vector((-.55,1.85,-.73)).normalized(),Vector((.79,.10,-.47)).normalized()]
    best=None
    for length in (.100,.075,.050):
        for x in np.arange(.26,.52,.016):
            for y in np.arange(-.30,-.085,.016):
                for theta in (-.60,-.24,.12,.46,1.12,1.55):
                    along=Vector((math.cos(theta),math.sin(theta),0))
                    across=UP.cross(along)
                    xy=Vector((float(x),float(y),0))
                    checks=[xy+along*u+across*v for u in np.linspace(-length/2-.006,length/2+.006,5)
                            for v in (-.011,0,.011)]
                    upper=[]
                    lower=[]
                    for p in checks:
                        a,_,_,_=trees["A"].ray_cast(p+UP*.002,-UP,.2)
                        b,_,_,_=trees["B"].ray_cast(p+UP*.002,-UP,.2)
                        if a is None or b is None:
                            break
                        upper.append(a.z)
                        lower.append(b.z)
                    if len(upper)!=len(checks):
                        continue
                    z=max(lower)+.007
                    gap=min(upper)-z
                    if gap<.014:
                        continue
                    position=xy+UP*z
                    cover=0
                    for p in checks:
                        for h in (.001,.010):
                            sample=Vector((p.x,p.y,z+h))
                            cover+=sum(any(tree.ray_cast(sample,d,.5)[0] is not None for tree in lookup)
                                       for d in directions)
                    score=cover+18*length-12*math.hypot(x-.375,y+.152)+10*min(gap,.025)
                    if best is None or score>best[0]:
                        best=(score,position,along,across,cover,len(checks)*len(directions)*2,length,gap)
        if best and best[4]==best[5]:
            break
    if best is None:
        raise RuntimeError("No inter-ribbon location fits a short trough")
    return best

_,origin,along,across,screened,total,tape_length,optical_gap=pick_light()
axes=(along,across,UP)
outer=tape_length+.012
trough=[box("Short aluminum heat bed",origin,(outer,.022,.002),lighting,metal,axes)]
for sign in (-1,1):
    trough.append(box("Opaque side lip",origin+across*.010*sign+UP*.005,
                      (outer,.002,.012),lighting,metal,axes))
    trough.append(box("Opaque end cap",origin+along*(outer/2-.001)*sign+UP*.005,
                      (.002,.018,.012),lighting,metal,axes))
box(f"{tape_length*1000:.0f} mm COB tape · fit envelope",origin+UP*.0017,
    (tape_length,.008,.0014),lighting,cob,axes)
proxy=light("Right pocket · opposite ribbon bounce proxy",origin+UP*.0026,origin+UP,.92,(1,.63,.40),tape_length,lighting)
proxy.data.shape="RECTANGLE"
proxy.data.size_y=.008
shield_trees=[bvh(o) for o in trough]
assert not any(shield.overlap(tree) for shield in shield_trees for tree in trees.values())
blocked=0
for u in (-.49,-.25,0,.25,.49):
    for v in (-.0038,0,.0038):
        p=origin+along*(u*tape_length)+across*v+UP*.0026
        for elevation in (0,-15,-30,-60,-90):
            pitch=math.radians(elevation)
            for azimuth in range(0,360,10):
                yaw=math.radians(azimuth)
                ray=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
                assert any(tree.ray_cast(p,ray,1)[0] is not None for tree in shield_trees)
                blocked+=1
print("LED SCREENING",screened,total,blocked,flush=True)

below=camera("01 · Directly below",(.0,.02,-2),1.59,direct=True)
side=camera("02 · Low ceiling angle",(.55,-1.85,-.81),1.62,target=(0,.015,-.083))
light("Room fill",(-.46,-.4,-1.5),(0,0,-.08),21,(1,.91,.81),1.5)
scene.camera=below

for key,filename in (("low angle","v11-approved-broad-ribbons-side.png"),
                     ("underside","v11-approved-broad-ribbons-below.png")):
    reference=bpy.data.images.load(str(ROOT/"references"/filename))
    reference.name="Approved concept · "+key
    reference.use_fake_user=True
    reference.pack()

# Joint bench: two separate solids that slide together axially. The
# male rail is built into the upper sheet; the socket is part of the lower.
# These simplified local ribbons let clearance and insertion be measured
# before the profile is blended into the global broad sweeps.
main=scene
scene=bpy.data.scenes.new("02 | Full-size right joint bench")
bpy.context.window.scene=scene
set_scene(scene,(.59,.64,.72),.25)
coupons=collection("01 · Two integral joint pieces")
sample_optics=collection("02 · Adjacent LED and wire recess")
studio=collection("03 · Section and joint review")
a_mat=material("Bench part A · warm ivory",(.80,.60,.39))
b_mat=material("Bench part B · cool ivory",(.52,.67,.71))
bench_metal=material("Bench aluminum",(.66,.67,.70),metal=.35)

def sweep_x(name,profile,sections,group,material):
    # Profile is a concave polygon in YZ. The cross-section is translated
    # by the Z offset at each longitudinal station.
    n=len(profile)
    verts=[(x,y,z+dz) for x,dz in sections for y,z in profile]
    faces=[]
    for i in range(len(sections)-1):
        a=i*n
        faces.extend((a+j,a+(j+1)%n,a+n+(j+1)%n,a+n+j) for j in range(n))
    faces.extend((tuple(reversed(range(n))),tuple(range(len(verts)-n,len(verts)))))
    obj=mesh_object(name,verts,faces,group,material,False)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    return obj

# Dimensions in millimetres. The broad rail head cannot pass through the
# socket mouth vertically. Slide along X to install. End stop remains
# a separate design item in the whole ribbon assembly.
def mprofile(points):
    return [(y*.001,z*.001) for y,z in points]

male=mprofile([(-59,17),(22,17),(37,22),(40,19),(24,13),
               (5,13),(5,7),(8,7),(8,3),(-8,3),(-8,7),(-5,7),(-5,13),(-59,13)])
female=mprofile([(-62,-4),(-21,-4),(-12,-3),(-12,10),(-5.4,10),(-5.4,7.4),
                 (-8.4,7.4),(-8.4,2.6),(8.4,2.6),(8.4,7.4),(5.4,7.4),
                 (5.4,10),(12,10),(12,-2),(28,-6),(56,-6),(62,-9),(60,-12),(27,-10),(-62,-8)])
male_body=sweep_x("A · Integral captive rail",male,[(-.062,0),(.062,0)],coupons,a_mat)
female_body=sweep_x("B · Open-ended socket and lower fold",female,[(-.076,0),(.076,0)],coupons,b_mat)
# Receiver has a short closed far end. Keep it integrated with the socket
# by exact union, outside the 124 mm male rail's installed envelope.
stop_profile=mprofile([(-12,-3),(12,-3),(12,10),(-12,10)])
stop=sweep_x("Integral end stop cutter body",stop_profile,[(.069,0),(.076,0)],coupons,b_mat)
bpy.context.view_layer.objects.active=female_body
union=female_body.modifiers.new("Solid end stop","BOOLEAN")
union.operation="UNION"
union.solver="EXACT"
union.object=stop
bpy.ops.object.modifier_apply(modifier=union.name)
bpy.data.objects.remove(stop,do_unlink=True)
# Place the LED above the lower sheet, behind the neighboring fold lip,
# with the channel entirely separate from the dovetail faces.
bench_origin=Vector((0,.042,-.0035))
box("LED aluminum bed · trial size",bench_origin,(.112,.015,.002),sample_optics,bench_metal)
for sy in (-1,1):
    box("Opaque optical lip",bench_origin+Vector((0,sy*.0065,.004)),(.112,.002,.008),
        sample_optics,bench_metal)
box("COB strip · 100 mm reservation",bench_origin+UP*.0017,(.100,.008,.0014),sample_optics,cob)
# Recess for the wire, machined into the rear side at the edge of the
# bench's socket piece. Leave the bearing web undisturbed.
wire_tool=box("Tool · 4 mm wire recess",(0,-.030,-.0039),(.153,.004,.004),coupons,b_mat)
difference(female_body,wire_tool)
wire_curve("Paired wire in rear recess",[Vector((x,-.030,-.0050)) for x in (-.076,-.025,.038,.073)],.00065,sample_optics,metal)

# Check the rest fit and the straight axial insertion up to the installed location.
tb,bc=solid_check(female_body)
ta,ac=solid_check(male_body)
assert not ac and not bc,(ac,bc)
male_body.data.calc_loop_triangles()
indices=[tuple(t.vertices) for t in male_body.data.loop_triangles]
coords=[v.co.copy() for v in male_body.data.vertices]
steps=[]
for offset in np.linspace(-.145,0,30):
    moved=BVHTree.FromPolygons([v+Vector((float(offset),0,0)) for v in coords],indices,all_triangles=True)
    steps.append(len(moved.overlap(tb)))
assert not any(steps),steps
# Test upward escape at the installed X location. Contact with the lips
# is the expected result and shows the form is captured in that direction.
lifted=BVHTree.FromPolygons([v+UP*.001 for v in coords],indices,all_triangles=True)
assert lifted.overlap(tb)
male_body["Fit"]="0.4 mm nominal clearance on each socket side. Slides along X; vertical pull meets captive lips."
female_body["Fit"]="Open insertion end at negative X. Integral far-end stop. Anti-backout keeper remains to be resolved at assembly."

box("Bench background",(0,0,-.045),(.8,.8,.012),studio,material("Technical review background",(.32,.35,.39)))
joint_camera=camera("01 · Joint and light pocket",(-.43,-.32,.28),.31,target=(0,0,0))
end_camera=camera("02 · Captured end section",(-.43,0,.022),.173,target=(0,0,.005))
light("Technical softbox",(-.25,-.2,.35),(0,0,0),34,(1,.89,.78),.36)
light("Technical fill",(.22,.2,.16),(0,0,0),15,(.77,.87,1),.31)
scene.camera=joint_camera

report=dict(
    layout=dict(skin_self_crossings=diagnostics,skin_pair_crossings=overlaps,right_overlap=right,
                approximate_span_mm=[round((max(v.co[i] for o in bands.values() for v in o.data.vertices)-
                                            min(v.co[i] for o in bands.values() for v in o.data.vertices))*1000,1)
                                     for i in (0,1)],
                maximum_ceiling_drop_mm=round(-min(v.co.z for o in bands.values() for v in o.data.vertices)*1000,1)),
    trial_emitter=dict(position_mm=[round(v*1000,1) for v in origin],
                       tape_envelope_mm=round(tape_length*1000), minimum_gap_to_opposite_face_mm=round(optical_gap*1000,1),
                       housing_sightline_samples_screened=screened,housing_sightline_samples_total=total,
                       direct_source_rays_blocked=blocked),
    joint_bench=dict(nominal_clearance_per_side_mm=.4,insertion_samples=len(steps),
                     sampled_insertion_intersections=sum(steps),lift_captured=True),
)
(OUT/"Development-checks.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2),flush=True)
source=bpy.data.texts.new("V11 generator · edit the centreline stations")
source.write(Path(__file__).read_text())
instructions=bpy.data.texts.new("START HERE · V11 development")
instructions.write(
    "01 | V11 three-ribbon layout: separate continuous editable meshes, packed approved concepts, "
    "low-angle and underside cameras, one inter-ribbon LED study. Toggle source path guides in the Outliner.\n"
    "02 | Full-size right joint bench: simplified captive profiles with an adjacent LED bed and wire recess. "
    "The coupon profile still needs blending into the full lamp and a physical test.\n"
    "Centre seat details, full loom, anti-backout keeper, final outline and print divisions are open.\n"
)
bpy.context.window.scene=main
scene=main
for guide in guides.objects:
    guide.hide_set(True,view_layer=main.view_layers[0])
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            view=area.spaces.active
            view.overlay.show_overlays=False
            view.shading.color_type="MATERIAL"
            view.region_3d.view_rotation=below.rotation_euler.to_quaternion()
            view.region_3d.view_location=(0,.02,-.1)
            view.region_3d.view_distance=1.60
            view.region_3d.view_perspective="ORTHO"
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Ribbon-Lamp-V11-Development.blend"),compress=True)
if "--render" in sys.argv:
    bench=bpy.data.scenes["02 | Full-size right joint bench"]
    for s,cam,file in ((main,below,"01-Underside"),(main,side,"02-Low-angle"),
                       (bench,joint_camera,"03-Right-joint-bench"),(bench,end_camera,"04-Keyed-end-section")):
        bpy.context.window.scene=s
        s.camera=cam
        s.render.filepath=str(OUT/(file+".png"))
        bpy.ops.render.render(write_still=True)
