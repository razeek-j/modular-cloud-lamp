import bpy,json,hashlib,shutil
from pathlib import Path
root=Path('/Users/razeek/Projects/3D printing')
path=root/'Lamp.blend'
backup=root/'Archive/2026-10-30/Versions/Lamp-before-removing-LED-proxy.blend'
assert not backup.exists(), 'Backup exists; do not overwrite it.'
shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
def fingerprint(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
 return h.hexdigest()
strip=[o for o in bpy.data.objects if o.type=='MESH' and ('LED strip' in o.name or 'LED strip' in o.data.name)]
assert len(strip)==4, [o.name for o in strip]
meshes=set(o.data for o in strip)
assert all(o in strip for o in bpy.data.objects if o.type=='MESH' and o.data in meshes)
before={o.name:fingerprint(o) for o in bpy.data.objects if o.type=='MESH' and o not in strip}
removed=[o.name for o in strip]
for o in strip:bpy.data.objects.remove(o,do_unlink=True)
for mesh in meshes:
 if mesh.users==0:bpy.data.meshes.remove(mesh)
after={o.name:fingerprint(o) for o in bpy.data.objects if o.type=='MESH'}
assert before==after, 'Printable geometry changed unexpectedly'
assert not any('LED strip' in o.name for o in bpy.data.objects)
s=bpy.data.scenes['01 • Complete lamp'];bpy.context.window.scene=s
assert sum(o.type=='MESH' for o in s.objects)==14
for material in list(bpy.data.materials):
 if 'LED strip' in material.name and material.users==0:bpy.data.materials.remove(material)
t=bpy.data.texts.get('START HERE - Lamp') or bpy.data.texts.new('START HERE - Lamp')
t.clear();t.write('Working file: Lamp.blend\nAll printable lamp components are stored in this file; no external linked libraries.\nYellow LED display proxy removed from every scene. Only the shade, carrier and stand remain as mesh parts.\nScenes: complete assembly; shade inspection; stand and carrier; thin carrier detail.\nCarrier: 0.8 mm wall, narrow bottom glue rim, backed 2 mm-deep wire channel.\nKnown unresolved issue: three stand leg roots intersect the shade. This draft is not yet print-ready.\nPhoto-derived dimensions; actual clip, wire, connector and print clearance need checking.\n')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(path))
report={'master':'Lamp.blend','removed_display_objects':removed,'printable_geometry_unchanged':before==after,'backup':str(backup),'mesh_objects_in_complete_assembly':14,'unique_printable_meshes':len({o.data.as_pointer() for o in s.objects if o.type=='MESH'}),'scenes':{sc.name:[o.name for o in sc.objects if o.type=='MESH'] for sc in bpy.data.scenes},'external_libraries':len(bpy.data.libraries)}
(root/'Support/master-inventory.json').write_text(json.dumps(report,indent=2))
(root/'Support/Checks/led-proxy-removal.json').write_text(json.dumps(report,indent=2))
readme=root/'README.md'
text=readme.read_text().replace('the stand, carrier and LED strip display model.','the stand and carrier.').replace('The LED strip is a display proxy.','The yellow LED strip display proxy has been removed from every scene; all remaining mesh parts are the shade, carrier or stand.')
readme.write_text(text)
p=root/'Support/cleanup-manifest.json';m=json.loads(p.read_text());m['master_sha256_before_led_removal']=m['master_sha256'];m['master_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();p.write_text(json.dumps(m,indent=2))
# Reopen the saved file to verify the on-disk result.
bpy.ops.wm.open_mainfile(filepath=str(path))
assert not any(o.type=='MESH' and 'LED strip' in o.name for o in bpy.data.objects)
assert len({o.data.as_pointer() for o in bpy.context.scene.objects if o.type=='MESH'})==3
assert {o.name:fingerprint(o) for o in bpy.data.objects if o.type=='MESH'}==before
print(json.dumps(report,indent=2))
