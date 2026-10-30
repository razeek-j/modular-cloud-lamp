import bpy,bmesh,math,json,shutil
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path('/Users/razeek/Projects/3D printing');out=root/'Support/Checks/cloud-tall'
bpy.ops.wm.open_mainfile(filepath=str(root/'Lamp.blend'))
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
master=s.objects['LAMP_Full Segment 01'];shade=master.data;carrier=s.objects['LAMP_Full Carrier'].data
# C2 axial transition: keep clip apertures rigid without horizontal slope steps.
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def integral_smooth(t):
 t=max(0,min(1,t));return 2.5*t**4-3*t**5+t**6
height_gain=(67.105-52.3)/(52.3-12)
def band_integral(z):
 if z<=22:return 0
 if z<26:return 4*integral_smooth((z-22)/4)
 if z<=34:return 2+z-26
 if z<38:
  t=(z-34)/4
  return 10+4*(t-integral_smooth(t))
 return 12
def stretch(z):
 a=abs(z);return math.copysign(a+height_gain*(a-band_integral(a)),z)
clip_center=stretch(30)
end_angle=math.pi/12-.7/(2*125)
for v in shade.vertices:
 x=v.co.x+125;y=v.co.y;z=stretch(v.co.z)
 r=math.hypot(x,y);u=math.atan2(y,x);frac=max(0,min(1,(u+end_angle)/(2*end_angle)))
 # Broad, smooth shoulders at both ends. No additional groove or raised lip.
 return_weight=(.5+.5*math.cos(2*math.pi*frac))**3
 q=r-125;length=math.hypot(q,z/1.35)
 # Protect the hardware interface around the two clip-holder bores.
 clip_distance=max(abs(r-125)-7,abs(abs(z)-clip_center)-6)
 free=smooth(clip_distance/8)
 # Keep the carrier's 4 mm radial passage unchanged.
 radial_free=1-(1-smooth((abs(r-105)-2.5)/4))*(1-smooth((z-13)/10))
 if length>1:
  dr=-2.0*return_weight*(q/length)*free*radial_free
  dz=-2.0*return_weight*(z/1.35/length)*1.35*free*radial_free
  newr=r+dr;v.co=(x*newr/r-125,y*newr/r,z+dz)
 else:v.co.z=z
# Keep the glue plane fixed, add useful height while staying below slot ceiling.
for v in carrier.vertices:v.co.z=-31+(v.co.z+31)*(41.5/38)
for data in [shade,carrier]:
 data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update()
bpy.context.view_layer.update()
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
segments=[o for o in s.objects if o.type=='MESH' and 'Segment' in o.name];stand=s.objects['LAMP_Full Stand'];ca=s.objects['LAMP_Full Carrier'];trees={o.name:tree(o) for o in segments+[stand,ca]}
segments.sort(key=lambda o:math.atan2(o.location.y,o.location.x))
def dims(objects):
 ps=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 return [max(p[i] for p in ps)-min(p[i] for p in ps) for i in range(3)]
report={'shade_dimensions_mm':dims(segments),'carrier_dimensions_mm':dims([ca]),'complete_dimensions_mm':dims(segments+[ca,stand]),'seam_return_depth_mm':2,'clip_hole_target_mm':[5,5], 'shade_count':len(segments), 'carrier_vs_shade':{o.name:len(trees[o.name].overlap(trees[ca.name])) for o in segments},'neighbor_intersections':[len(trees[a.name].overlap(trees[segments[(i+1)%12].name])) for i,a in enumerate(segments)],'stand_vs_shade':{o.name:len(trees[o.name].overlap(trees[stand.name])) for o in segments},'topology':{}}
# Measure both openings on both ends of one actual sector, and compare joint centers.
bores=[];centers={}
for sign in [-1,1]:
 rot=Matrix.Rotation(sign*math.pi/12,3,'Z')
 for z in [-clip_center,clip_center]:
  origin=rot@Vector((125,-sign*1,z));rr=[]
  for direction in [(1,0,0),(0,0,1)]:
   d=rot@Vector(direction);hits=[trees[master.name].ray_cast(origin,d*k,20) for k in [-1,1]]
   rr.append(sum(h[3] for h in hits) if all(h[0] is not None for h in hits) else None)
  bores.append({'end':sign,'height':z,'width_height_mm':rr})
report['measured_bores']=bores
for data in [shade,carrier,stand.data]:
 bm=bmesh.new();bm.from_mesh(data);report['topology'][data.name]={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':abs(bm.calc_volume(signed=True))};bm.free()
print(json.dumps(report,indent=2),flush=True)
(out/'checks.json').write_text(json.dumps(report,indent=2))
assert not any(report['carrier_vs_shade'].values()) and not any(report['neighbor_intersections'])
assert all(c['nonmanifold_edges']==0 for c in report['topology'].values())
assert all(all(q is not None and abs(q-5)<.02 for q in p['width_height_mm']) for p in bores),bores
report['known_issue']='Stand leg roots still intersect shade. Proposal for proportions; printable exports not updated.'
for name in ['START HERE - Lamp','Taller cloud profile - checks']:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write(json.dumps(report,indent=2))
# Set the saved default view to the new proportions.
rot=(Vector((0,0,-25))-Vector((440,-550,290))).to_track_quat('-Z','Y')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   rv=area.spaces.active.region_3d;rv.view_location=(0,0,-20);rv.view_distance=470;rv.view_rotation=rot;rv.view_perspective='ORTHO'
backup=root/'Archive/2026-10-30/Versions/Lamp-taller-proposal-before-top-smoothing.blend'
if not backup.exists():shutil.copy2(root/'Lamp-taller-proposal.blend',backup)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Lamp-taller-proposal.blend'))
(out/'checks.json').write_text(json.dumps(report,indent=2))
# Camera previews are inspection artifacts only, not extra printable mesh.
def render(scene,path,loc,target,scale):
 bpy.context.window.scene=scene
 d=bpy.data.cameras.new('Cloud inspection');c=bpy.data.objects.new('Cloud inspection',d);scene.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;scene.camera=c
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(out/path);bpy.ops.render.render(write_still=True)
render(s,'assembly.png',(440,-550,290),(0,0,-20),420)
detail=bpy.data.scenes.new('Temporary single piece preview')
a=master.copy();a.data=master.data;detail.collection.objects.link(a)
render(detail,'single-piece.png',(380,-240,180),(125,0,0),185)
