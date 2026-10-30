import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
out=Path('/Users/razeek/Projects/3D printing/output/lamp-final-audit')
s=bpy.data.scenes['02 • Full 360 Assembly'];bpy.context.window.scene=s;bpy.context.view_layer.update()
k=s.unit_settings.scale_length*1000
objs=[o for o in s.objects if o.type=='MESH'];shade=[o for o in objs if 'Segment' in o.name]
carrier=next(o for o in objs if 'Carrier' in o.name);stand=next(o for o in objs if 'Stand' in o.name);led=next(o for o in objs if 'strip' in o.name)
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(os):
 ps=[p for o in os for p in points(o)];lo=[min(p[i] for p in ps)*k for i in range(3)];hi=[max(p[i] for p in ps)*k for i in range(3)]
 return {'dimensions_mm':[b-a for a,b in zip(lo,hi)],'min_mm':lo,'max_mm':hi}
def topo(o):
 bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);c=0
 while unseen:
  c+=1;stack=[unseen.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in unseen:unseen.remove(q);stack.append(q)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_components':c,'volume_mm3':abs(bm.calc_volume(signed=True))*k**3}
 bm.free();return r
def tree(o):return BVHTree.FromPolygons(points(o),[tuple(f.vertices) for f in o.data.polygons])
trees={o.name:tree(o) for o in objs}
def overlaps(a,b):return trees[a.name].overlap(trees[b.name])
def detail(a,b):
 pairs=overlaps(a,b)
 if not pairs:return {'surface_pairs':0}
 ids=set(i for i,j in pairs);ps=[a.matrix_world@a.data.vertices[v].co for i in ids for v in a.data.polygons[i].vertices]
 return {'surface_pairs':len(pairs),'area_bounds_mm':[[min(p[i] for p in ps)*k,max(p[i] for p in ps)*k] for i in range(3)]}
report={'file':bpy.data.filepath,'units':'millimeters','dimensions':{'complete_lamp':bounds(objs),'shade':bounds(shade),'one_segment':bounds([shade[0]]),'carrier_including_flange':bounds([carrier]),'stand':bounds([stand]),'LED_strip_proxy':bounds([led])},'topology':{o.name:topo(o) for o in [shade[0],carrier,stand,led]},'shade_count':len(shade),'angular_steps_degrees':[],
 'neighbor_intersections':[],'carrier_vs_shade':[],'stand_vs_shade':[],'LED_vs_shade':[],'carrier_vs_stand':detail(carrier,stand)}
shade.sort(key=lambda o:math.atan2(o.location.y,o.location.x))
for i,a in enumerate(shade):
 b=shade[(i+1)%len(shade)];report['neighbor_intersections'].append({'a':a.name,'b':b.name,**detail(a,b)})
 report['angular_steps_degrees'].append(math.degrees((math.atan2(b.location.y,b.location.x)-math.atan2(a.location.y,a.location.x))%(2*math.pi)))
 for obj,key in [(carrier,'carrier_vs_shade'),(stand,'stand_vs_shade'),(led,'LED_vs_shade')]:report[key].append({'shade':a.name,**detail(obj,a)})
# Measure the front passage and holder openings in actual final mesh via ray pairs.
master=next(o for o in shade if o.name.endswith('01'));tr=trees[master.name];rot=Matrix.Rotation(-math.pi/12,3,'Z')
def opening(x,y,z,axis):
 origin=rot@Vector((x,y,z));direction=(rot@Vector(axis)).normalized();ds=[]
 for sign in [-1,1]:
  hit=tr.ray_cast(origin,direction*sign,30)
  ds.append(hit[3] if hit[0] is not None else None)
 return sum(ds)*k if all(d is not None for d in ds) else ds
report['measured_openings_mm']={'carrier_slot_radial_width_at_z0':opening(105,1,0,(1,0,0)),
 'holder_upper_radial_width':opening(125,1,30,(1,0,0)), 'holder_lower_radial_width':opening(125,1,-30,(1,0,0)),
 'holder_upper_height':opening(125,1,30,(0,0,1)), 'holder_lower_height':opening(125,1,-30,(0,0,1))}
(out/'final-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
# Evidence previews from original geometry. Do not save the source blend.
for scene in [s,bpy.data.scenes['03 • Carrier, Stand and LED Strip Only']]:
 bpy.context.window.scene=scene
 d=bpy.data.cameras.new('Audit camera');cam=bpy.data.objects.new('Audit camera',d);scene.collection.objects.link(cam)
 cam.location=(440,-550,290);cam.rotation_euler=(Vector((0,0,-25))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=420 if scene==s else 300;scene.camera=cam
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1300;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
 scene.render.filepath=str(out/('full-assembly.png' if scene==s else 'components.png'));bpy.ops.render.render(write_still=True)
