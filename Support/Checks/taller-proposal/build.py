import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('/Users/razeek/Projects/3D printing');out=root/'Support/Checks/taller-proposal'
bpy.ops.wm.open_mainfile(filepath=str(root/'Lamp.blend'))
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s;bpy.context.view_layer.update()
shade=s.objects['LAMP_Full Segment 01'].data;carrier=s.objects['LAMP_Full Carrier'].data
# Maintain height of the clip apertures in the bands around +/-30 mm.
def clamp(x):return max(0,min(10,x))
def stretch(z):return 1.15*z-.15*(clamp(z-25)+clamp(z+35)-10)
for v in shade.vertices:v.co.z=stretch(v.co.z)
for v in carrier.vertices:v.co.z=-31+(v.co.z+31)*1.05
shade.update();carrier.update();bpy.context.view_layer.update()
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
segments=[o for o in s.objects if o.type=='MESH' and 'Segment' in o.name];stand=s.objects['LAMP_Full Stand'];ca=s.objects['LAMP_Full Carrier']
trees={o.name:tree(o) for o in segments+[stand,ca]}
hits={o.name:len(trees[o.name].overlap(trees[ca.name])) for o in segments}
standhits={o.name:len(trees[o.name].overlap(trees[stand.name])) for o in segments}
segments.sort(key=lambda o:math.atan2(o.location.y,o.location.x))
neighbor=[len(trees[a.name].overlap(trees[segments[(i+1)%12].name])) for i,a in enumerate(segments)]
pts=[o.matrix_world@v.co for o in segments for v in o.data.vertices];cp=[ca.matrix_world@v.co for v in ca.data.vertices]
report={'shade_height_mm':max(p.z for p in pts)-min(p.z for p in pts),'shade_width_mm':max(p.x for p in pts)-min(p.x for p in pts),'carrier_height_mm':max(p.z for p in cp)-min(p.z for p in cp),'clip_hole_heights_mm':5,'carrier_shade_surface_pairs':hits,'neighbor_surface_pairs':neighbor,'stand_shade_surface_pairs':standhits,'known_issue':'Stand roots intersect shade; assembly not print ready.'}

for a in segments[:1]:
 pairs=trees[a.name].overlap(trees[ca.name]); vs=[a.matrix_world@a.data.vertices[k].co for i,j in pairs for k in a.data.polygons[i].vertices]; print('HIT_BOUNDS',[(min(p[i] for p in vs),max(p[i] for p in vs)) for i in range(3)] if vs else [],flush=True)
assert len(segments)==12 and not any(hits.values()) and not any(neighbor),report
for data in [shade,carrier]:
 bm=bmesh.new();bm.from_mesh(data);assert all(e.is_manifold for e in bm.edges);bm.free()
t=bpy.data.texts.new('Taller proposal - dimensions and checks');t.write(json.dumps(report,indent=2))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Lamp-taller-proposal.blend'))
(out/'checks.json').write_text(json.dumps(report,indent=2))
d=bpy.data.cameras.new('Proposal preview');c=bpy.data.objects.new('Proposal preview',d);s.collection.objects.link(c);c.location=(440,-550,290);c.rotation_euler=(Vector((0,0,-25))-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=420;s.camera=c
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=1100;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.filepath=str(out/'preview.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
