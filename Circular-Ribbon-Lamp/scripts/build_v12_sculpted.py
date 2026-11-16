"""V12: independently traced 3D edge rails; lamp-only appearance reconstruction.

Coordinates are hand interpreted from the approved underside concept. Depth is
inferred, not recovered from a calibrated photograph. Run in Blender Python.
"""
import bpy, bmesh, math, json, sys
import numpy as np
from pathlib import Path
from itertools import combinations
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
CONTROLLED_FOLD = '--v13' in sys.argv
OUT = ROOT / ('development-v13' if CONTROLLED_FOLD else 'development-v12')
if CONTROLLED_FOLD:
    sys.path.insert(0, str(ROOT / 'scripts'))
    from v13_right_fold import right_fold
OUT.mkdir(exist_ok=True)
DRAFT = '--draft' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'V13 · Controlled right fold' if CONTROLLED_FOLD else 'V12 · Sculpted ribbon lamp'
scene.unit_settings.system='METRIC'
scene.unit_settings.length_unit='MILLIMETERS'
def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
skins=collection('01 · Broad sculpted ribbons')
mount=collection('02 · Single central hook envelope')
guides=collection('03 · Editable edge rails · hidden in renders')
studio=collection('04 · Lamp-only cameras and studio illumination')
lights=collection('05 · Fold light positions · optical study')
def material(name,color,translucent=0,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.48;p.inputs['Metallic'].default_value=metal
    if translucent:
        t=n.new('ShaderNodeBsdfTranslucent');t.inputs[0].default_value=(*color,1)
        mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=translucent
        l.new(p.outputs[0],mix.inputs[1]);l.new(t.outputs[0],mix.inputs[2])
        l.new(mix.outputs[0],n.get('Material Output').inputs[0])
    return m
paper=material('Ivory diffusing skin · appearance only',(.92,.87,.77),.38)
ivory=material('Ivory centre cover',(.9,.86,.77))
metal=material('Brushed metal · mounting envelope',(.36,.38,.4),metal=.8)
guide_mat=material('Edge rail teal',(.08,.5,.55))
def mesh(name,verts,faces,group,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);group.objects.link(ob)
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    return ob
def catmull(p,t):
    i=math.floor(t);u=t-i
    a,b,c,d=(p[j%len(p)] for j in range(i-1,i+3))
    return .5*(2*b+(c-a)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
def unit(v):return v/np.maximum(1e-12,np.linalg.norm(v,axis=-1,keepdims=True))
def curve(name,points,group,mat,radius=.0005,closed=True):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D'
    cu.bevel_depth=radius;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for v,p in zip(sp.points,points):v.co=(*p,1)
    sp.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,cu);group.objects.link(ob);cu.materials.append(mat)
    return ob

# Paired outer and inner rail stations in reference pixels, then depth in mm.
# The two edges rise and fall independently, shaping the entire ribbon face.
RAILS={
'A · High left crest and rear return':[
 (47,532,110,181,616,175),(139,449,90,240,569,165),
 (242,440,62,322,557,145),(281,288,32,370,515,125),
 (396,197,28,445,458,110),(510,229,43,530,420,110),
 (640,337,65,654,405,104),(736,349,57,754,439,115),
 (858,274,30,848,448,92),(988,270,43,941,432,125),
 (1063,357,78,971,456,156),(1091,480,125,945,499,180),
 (1070,581,169,933,568,166),(1170,605,128,1031,647,170),
 (1204,695,83,1045,682,141),(1136,758,57,1029,703,112),
 (1024,768,53,995,688,86),(915,701,48,884,599,82),
 (814,590,42,797,508,72),(689,513,36,680,450,66),
 (553,507,39,541,438,69),(418,561,50,409,481,90),
 (275,588,69,266,523,112),(151,641,108,160,531,146),
 (75,631,128,118,576,165)],
'B · Sweeping face and large right roll':[
 (84,658,153,184,676,194),(111,518,127,221,620,183),
 (206,482,112,307,622,171),(311,538,135,402,623,171),
 (430,524,126,498,600,154),(558,453,107,579,540,132),
 (676,377,72,652,486,128),(805,339,48,724,476,143),
 (918,355,62,809,513,161),(988,424,87,863,583,182),
 (1007,525,118,887,670,198),(969,649,166,870,737,210),
 (915,765,203,852,785,203),(861,837,215,834,787,183),
 (803,804,204,784,724,162),(743,717,182,737,641,132),
 (655,636,165,676,553,108),(574,612,161,591,506,87),
 (493,658,174,499,511,101),(404,744,188,407,577,129),
 (307,807,202,317,652,159),(217,878,213,242,714,185),
 (194,926,200,211,770,200),(154,882,174,203,786,203),
 (124,790,157,198,730,203)],
'C · Broad scalloped lower fold':[
 (160,823,133,271,825,168),(192,729,116,316,780,168),
 (306,683,112,416,735,164),(431,666,135,511,690,183),
 (547,581,146,575,665,195),(630,568,150,608,651,192),
 (729,665,166,669,731,200),(834,759,171,771,814,213),
 (960,759,156,909,831,203),(1110,754,128,1002,812,176),
 (1177,723,94,1058,794,153),(1125,824,94,1031,824,148),
 (1027,881,125,971,834,162),(976,940,161,912,865,185),
 (877,969,179,847,875,202),(762,936,168,770,865,200),
 (674,949,137,684,858,191),(589,1032,113,583,895,178),
 (508,1061,105,509,922,165),(419,1031,117,434,907,172),
 (340,967,142,379,867,186),(258,960,171,314,854,193),
 (194,926,162,280,852,181)]}

INNER_A=[(140,550),(230,505),(320,480),(390,420),(460,350),
 (535,360),(640,390),(740,400),(847,370),(950,375),(998,420),
 (1020,480),(1020,560),(1080,640),(1090,680),(1050,700),
 (995,675),(900,600),(800,510),(690,450),(550,445),(420,490),
 (290,540),(170,570),(135,565)]
INNER_B=[(205,680),(250,600),(300,570),(370,592),(463,578),
 (555,524),(645,454),(741,430),(815,454),(855,515),(871,595),
 (856,681),(832,739),(819,755),(791,722),(746,664),(678,605),
 (597,591),(508,629),(418,704),(330,755),(258,808),(241,826),
 (220,804),(205,750)]
for key,raw in RAILS.items():
    for i,row in enumerate(raw):
        row=list(row)
        if key[0]=='A':row[3:5]=INNER_A[i]
        elif key[0]=='B':row[3:5]=INNER_B[i]
        else:row[3:5]=[650+(row[3]-650)*.72,800+(row[4]-800)*.72]
        raw[i]=row
for key,raw in RAILS.items():
    if key[0]=='A':
        # The far return tucks behind the broad crossing face, keeping its
        # narrower hidden section out of the open gaps.
        for i,outer,inner in [(17,(915,550,48),(900,500,82)),
            (18,(814,460,42),(800,390,72)),(19,(689,448,36),(690,398,66)),
            (20,(553,520,39),(550,472,69)),(21,(418,585,50),(420,538,90)),
            (22,(275,580,69),(290,535,112))]:raw[i]=[*outer,*inner]
    if key[0]=='B':
        for i,outer,inner in [(20,(307,807,200),(285,740,160)),
            (21,(220,880,211),(220,770,170)),(22,(180,905,203),(196,800,175)),
            (23,(146,856,180),(182,790,177)),(24,(132,760,159),(190,730,180))]:
            raw[i]=[*outer,*inner]
    if key[0]=='C':
        for i,outer,inner in [(9,(1030,780,128),(900,805,176)),
            (10,(1070,825,110),(930,825,165)),(11,(1060,866,110),(925,850,165)),
            (12,(1010,906,125),(880,865,178)),(13,(976,940,161),(840,880,185)),
            (14,(877,969,179),(792,877,202))]:raw[i]=[*outer,*inner]

grids={};objects={};smooth_grids={}
for key,raw in RAILS.items():
    r=np.asarray(raw,float);r[:,[0,3]]=(r[:,[0,3]]-625)*1.025
    r[:,[1,4]]=(r[:,[1,4]]-625)*1.025;r[:,[2,5]]*=-1;r*=.001
    rows=len(r)*16;cols=121 if not DRAFT else 65
    a=np.array([catmull(r,t) for t in np.linspace(0,len(r),rows,endpoint=False)])
    camber=.016 if key[0]!='B' else .022
    if CONTROLLED_FOLD and key[0]=='B':
        a, fold_parameters = right_fold(a, camber)
    u=np.linspace(0,1,cols)
    grid=a[:,None,:3]*(1-u[None,:,None])+a[:,None,3:]*u[None,:,None]
    tangent=np.roll(grid,-1,axis=0)-np.roll(grid,1,axis=0)
    normal=unit(np.cross(tangent,np.gradient(grid,axis=1)))
    # Round the whole sheet section between the independently sculpted rails.
    grid[:,:,2]-=camber*np.sin(np.pi*u)[None,:]
    smooth_grids[key[0]]=grid.copy()
    normal=unit(np.cross(np.roll(grid,-1,axis=0)-np.roll(grid,1,axis=0),np.gradient(grid,axis=1)))
    if not DRAFT:
        # Long 5–7 mm parallel pleats; fine FDM layers are left to the slicer.
        ripple=.00035*np.cos(2*np.pi*27*u)*np.sin(np.pi*u)**.7
        amplitude=np.minimum(np.linalg.norm(a[:,:3]-a[:,3:],axis=1)/.14,1)**2
        grid+=normal*ripple[None,:,None]*amplitude[:,None,None]
    # Offset along the smooth sheet normal: both sides retain the pleat relief.
    # Offsetting along tiny pleat radii would make adjacent offsets intersect.
    count=rows*cols
    verts=np.concatenate(((grid-normal*.0008).reshape(-1,3),(grid+normal*.0008).reshape(-1,3)))
    faces=[]
    for i in range(rows):
        j=(i+1)%rows
        for k in range(cols-1):
            f=(i*cols+k,j*cols+k,j*cols+k+1,i*cols+k+1)
            faces.extend((f,tuple(x+count for x in reversed(f))))
        for k in (0,cols-1):
            p,q=i*cols+k,j*cols+k;faces.append((p,q,q+count,p+count))
    ob=mesh(key,verts.tolist(),faces,skins,paper)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob['Stage']='Appearance reconstruction. Integral root joints and print segmentation remain open.'
    ob['Nominal skin mm']=1.6
    grids[key[0]]=grid;objects[key[0]]=ob
    for side,n in [(0,'Outer'),(3,'Inner')]:
        rail=curve(key[0]+' · '+n+' edge',a[:,side:side+3],guides,guide_mat)
        rail.hide_render=True;rail.hide_set(True)
guides.hide_render=True

# Local nesting clearance changes depth only where the independently drawn
# surfaces overlap. The large crests, outline and full-width twist are retained.
def surface_bvh(grid):
    rows,cols=grid.shape[:2]
    faces=[]
    for i in range(rows):
        j=(i+1)%rows
        for k in range(cols-1):
            a,b,c,d=i*cols+k,j*cols+k,j*cols+k+1,i*cols+k+1
            faces.extend([(a,b,c),(a,c,d)])
    return BVHTree.FromPolygons(grid.reshape(-1,3).tolist(),faces,all_triangles=True)
front_tree=surface_bvh(grids['B'])
clearance_changes={}
for label in ['A','C']:
    grid=grids[label];need=np.zeros(grid.shape[:2])
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            x,y,z=grid[i,j]
            p=front_tree.ray_cast(Vector((x,y,.3)),Vector((0,0,-1)),1)[0]
            if p is not None:need[i,j]=max(0,p.z+.008-z)
    # Broad XY-based bumps give the same shift to neighboring projected
    # surfaces, avoiding creases at the boundary of an overlap mask.
    xy=grid[:,:,:2].reshape(-1,2);flat=need.ravel()
    constraints=np.flatnonzero(flat>.00001)
    displacement=np.zeros(len(flat))
    for start in range(0,len(constraints),64):
        ids=constraints[start:start+64]
        distance2=np.sum((xy[:,None,:]-xy[ids][None,:,:])**2,axis=2)
        bump=(flat[ids]+.001)[None,:]*np.exp(-distance2/(2*.065**2))
        displacement=np.maximum(displacement,bump.max(axis=1))
    displacement=displacement.reshape(need.shape)
    if label=='A':
        displacement+=.009*np.exp(-np.sum((grid[:,:,:2]-np.array([-.391,-.129]))**2,axis=2)/(2*.05**2))
    grid[:,:,2]+=displacement
    smooth_grid=smooth_grids[label];smooth_grid[:,:,2]+=displacement
    normal=unit(np.cross(np.roll(smooth_grid,-1,axis=0)-np.roll(smooth_grid,1,axis=0),np.gradient(smooth_grid,axis=1)))
    coords=np.concatenate(((grid-normal*.0008).reshape(-1,3),(grid+normal*.0008).reshape(-1,3)))
    for v,p in zip(objects[label].data.vertices,coords):v.co=p
    objects[label].data.update()
    clearance_changes[label]=round(float(displacement.max()*1000),2)
print('LOCAL NESTING ADJUSTMENT MM',clearance_changes,flush=True)

def cylinder(name,loc,radius,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=loc)
    ob=bpy.context.object;ob.name=name
    for c in list(ob.users_collection):c.objects.unlink(ob)
    mount.objects.link(ob);ob.data.materials.append(mat)
    bevel=ob.modifiers.new('Soft edge','BEVEL');bevel.width=.002;bevel.segments=3
    ob.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return ob
cover=cylinder('Compact centre cover · mounting envelope',(0,0,-.032),.084,.018,ivory)
plate=cylinder('Centre metal plate · mounting envelope',(0,0,-.020),.077,.005,metal)
# One metal eye. No outer anchors, suspension rods or ceiling plane.
eye=curve('Single central suspension eye · provisional',
 [(0,.014*math.cos(t),.012+.018*math.sin(t)) for t in np.linspace(0,math.tau,97)[:-1]],mount,metal,.003)
cylinder('Single eye stem · provisional',(0,0,-.009),.004,.026,metal)
mount['Status']='One central attachment envelope. Hook specification, concealed root capture and load test are pending.'
for ob in mount.objects:ob.location.y-=.1

def area(name,loc,target,energy,color,size,group=studio):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size
    ob=bpy.data.objects.new(name,d);group.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob
keylight=area('Large soft key',(-.6,-.6,-1.4),(0,0,-.1),9,(1,.93,.84),1.5)
filllight=area('Soft edge fill',(.8,.2,-.7),(0,0,-.12),4,(.85,.91,1),1.1)
toplight=area('Top softbox',(0,0,.7),(0,0,-.12),5,(1,.88,.69),1.3)
for name,position,target in [
 ('Left bend',(-.43,-.07,-.06),(-.46,-.03,-.16)),
 ('Right roll',(.27,-.12,-.04),(.35,-.06,-.15)),
 ('Lower fold',(-.06,.28,-.08),(-.05,.35,-.16))]:
    proxy=area('LED position study · '+name,position,target,6,(1,.53,.22),.08,lights)
    proxy.data.shape='RECTANGLE';proxy.data.size_y=.008
    proxy['Status']='80 x 8 mm optical proxy only. Housing, heat spreader and wire routing must be fitted after form review.'

def camera(name,elevation,azimuth=0,scale=1.45):
    el=math.radians(elevation);az=math.radians(azimuth)
    right=Vector((math.cos(az),math.sin(az),0))
    back=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),-math.sin(el)))
    up=back.cross(right)
    mat=Matrix((right,up,back)).transposed().to_4x4()
    ob=bpy.data.objects.new(name,bpy.data.cameras.new(name));studio.objects.link(ob)
    ob.matrix_world=mat;ob.location=Vector((0,0,-.12))+back*2
    ob.data.type='ORTHO';ob.data.ortho_scale=scale
    return ob
cams=[camera('01 · Lamp alone · underside oblique',55),camera('02 · Directly below',90),camera('03 · Low side',20),camera('04 · Rear and single hook',-40,180)]
scene.camera=cams[0]
scene.world=bpy.data.worlds.new('Neutral studio · no ceiling');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.32,.32,.32,1);bg.inputs[1].default_value=.35
wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links
pathnode=wn.new('ShaderNodeLightPath');viewbg=wn.new('ShaderNodeBackground')
viewbg.inputs[0].default_value=(.12,.105,.088,1);viewbg.inputs[1].default_value=.75
worldmix=wn.new('ShaderNodeMixShader');wl.new(pathnode.outputs['Is Camera Ray'],worldmix.inputs[0])
wl.new(bg.outputs[0],worldmix.inputs[1]);wl.new(viewbg.outputs[0],worldmix.inputs[2])
wl.new(worldmix.outputs[0],wn.get('World Output').inputs['Surface'])
scene.render.engine='CYCLES';scene.cycles.samples=16 if DRAFT else 48
scene.cycles.use_denoising=True;scene.render.film_transparent=False
scene.render.resolution_x=1100 if DRAFT else 1500
scene.render.resolution_y=1000 if DRAFT else 1300
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
for name in ['v11-approved-broad-ribbons-side.png','v11-approved-broad-ribbons-below.png']:
    im=bpy.data.images.load(str(ROOT/'references'/name));im.pack();im.use_fake_user=True
source=bpy.data.texts.new('V12 source · independent 3D edge rails');source.write(Path(__file__).read_text())
if CONTROLLED_FOLD:
    fold_source = bpy.data.texts.new('V13 source · centreline radius, width and twist')
    fold_source.write((ROOT / 'scripts' / 'v13_right_fold.py').read_text())
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            v=a.spaces.active;v.overlay.show_overlays=False;v.shading.color_type='MATERIAL'
            v.shading.light='STUDIO';v.shading.studiolight_rotate_z=.3
            v.region_3d.view_rotation=cams[0].rotation_euler.to_quaternion()
            v.region_3d.view_location=(0,0,-.12);v.region_3d.view_distance=1.7
            v.region_3d.view_perspective='ORTHO'
allverts=np.concatenate([np.array([v.co[:] for v in ob.data.vertices]) for ob in objects.values()])
report={'stage':'Shape reconstruction; appearance and engineering checks pending',
 'envelope_mm':((allverts.max(0)-allverts.min(0))*1000).tolist(),
 'lowest_point_mm':-allverts[:,2].min()*1000,
 'central_attachment_count':1,'ceiling_geometry':False}
if CONTROLLED_FOLD:
    report['right_fold'] = fold_parameters
(OUT/'Geometry-review.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0
if CONTROLLED_FOLD:
    filename = 'Ribbon-Lamp-V13-Draft.blend' if DRAFT else 'Ribbon-Lamp-V13-Controlled-Fold.blend'
else:
    filename = 'Ribbon-Lamp-V12-Draft.blend' if DRAFT else 'Ribbon-Lamp-V12-Sculpted.blend'
path=OUT/filename
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
if '--render' in sys.argv:
    for cam,filename in zip(cams,['01-Lamp-alone','02-Underside','03-Low-side','04-Rear-hook']):
        if DRAFT and filename not in ['01-Lamp-alone','02-Underside']:continue
        scene.camera=cam;scene.render.filepath=str(OUT/(filename+('-draft' if DRAFT else '')+'.png'))
        bpy.ops.render.render(write_still=True)
    if not DRAFT:
        for o in lights.objects:o.hide_render=True
        keylight.data.energy=65;filllight.data.energy=45;toplight.data.energy=90
        scene.camera=cams[0];scene.render.filepath=str(OUT/'05-Neutral-shape.png')
        bpy.ops.render.render(write_still=True)
print('SAVED',path,report,flush=True)
