"""Actual-model review renders and labelled technical cutaways; never saves visibility changes."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp');s=bpy.context.scene
s.cycles.device='CPU';s.cycles.samples=16;s.render.resolution_x=1050;s.render.resolution_y=750;s.render.resolution_percentage=100
def aim(cam,position,target):
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
def render(name):s.render.filepath=str(R/'renders'/name);bpy.ops.render.render(write_still=True)
def neutral():
 for o in bpy.data.objects:
  if o.type=='LIGHT' and 'COB equivalent' in o.name:o.data.energy=0
 s.world.node_tree.nodes.get('Background').inputs[1].default_value=.4;s.view_settings.exposure=0
 bpy.data.objects['Room daylight • review only'].data.energy=28
if '--composition' in sys.argv:
 neutral();render('v06-composition-stage.png');raise SystemExit
if '--angles' in sys.argv:
 neutral();s.cycles.samples=10;s.render.resolution_x=600;s.render.resolution_y=420;cam=bpy.data.objects['CAM • warm room view'];cam.data.type='PERSP';cam.data.lens=48
 aim(cam,(0,0,-2.2),(0,0,-.15));render('v06-review-below.png')
 for i in range(8):
  a=i*math.tau/8;aim(cam,(2.3*math.cos(a),2.3*math.sin(a),-.90),(0,0,-.15));render(f'v06-review-{i:02d}.png')
 for i in range(4):
  a=i*math.tau/4;aim(cam,(2.3*math.cos(a),2.3*math.sin(a),-.45),(0,0,-.15));render(f'v06-shallow-{i:02d}.png')
 raise SystemExit
# Service inspection uses an explicit cutaway, never a concealment acceptance image.
neutral()
for o in bpy.data.objects:
 if o.name.startswith('Ceiling backdrop') or o.name in ['Light deck • thin rear cover','Service ceiling plate','Upper vent light baffle','Lower vent light baffle','R01 • continuous thermal coupling lip']:o.hide_render=True
for key in ['V06 01 • LARGE ROLLED WAVES','V06 02 • IN-BETWEEN WAVES']:
 for o in bpy.data.collections[key].objects:o.hide_render=True
light=bpy.data.lights.new('Technical cutaway studio','AREA');light.energy=70;light.shape='DISK';light.size=1.5;lo=bpy.data.objects.new(light.name,light);s.collection.objects.link(lo);lo.location=(0,-.5,1.7);lo.rotation_euler=(Vector((0,0,0))-lo.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects['CAM • service top'];cam.data.type='ORTHO';cam.data.ortho_scale=1.10;aim(cam,(0,-.55,1.4),(0,0,-.02));render('v06-light-deck-cutaway.png')
# Joint detail: all surrounding housing is omitted to expose the actual lap and receiver.
facts=json.loads((R/'checks/v06-report.json').read_text());a=facts['attachments'][0];p=Vector(a['contact_mm'])/1000;centre=Vector((p.x,p.y,-.025));receiver=bpy.data.objects[f'Receiver {a["band"]}.{a["sector"]} • paired lap'];band=sorted(bpy.data.collections['V06 01 • LARGE ROLLED WAVES'].objects,key=lambda o:o.name)[a['band']-1]
for o in bpy.data.objects:
 if o.type not in {'MESH','CURVE'}:continue
 keep=o==band or o==receiver or (any(k in o.name for k in ['shank','screw head','retention nut','return-slot collar']) and (o.location-centre).length<.065)
 o.hide_render=not keep
lo.location=centre+Vector((.05,-.1,.22));lo.rotation_euler=(centre-lo.location).to_track_quat('-Z','Y').to_euler();lo.data.energy=8;lo.data.size=.25
cam.data.ortho_scale=.17;out=Vector((p.x,p.y,0)).normalized();T=Vector((-out.y,out.x,0));aim(cam,centre+out*.13+T*.07+Vector((0,0,.13)),centre+Vector((0,0,-.012)));render('v06-integral-lap-cutaway.png')
