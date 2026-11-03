"""Create standard millimetre 3MF models for lamp connection pins with native Snapmaker U1 settings."""
from pathlib import Path
import zipfile, struct, json, xml.etree.ElementTree as E

ROOT = Path("/Users/razeek/Projects/3D printing")
OUT = ROOT / "Printable-fixed"
TEMPLATE_3MF = OUT / "Checks/UI-template.3mf"
PINS_DIR = OUT / "Models/Pins"
PINS_PROJ_DIR = OUT / "Projects/Pins"
PINS_PROJ_DIR.mkdir(parents=True, exist_ok=True)

NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'

template = zipfile.ZipFile(TEMPLATE_3MF)
default_proj = json.loads(template.read('Metadata/project_settings.config'))
machine = json.loads((OUT / 'Checks/machine.json').read_text())
filament = json.loads((OUT / 'Checks/filament.json').read_text())

base = dict(default_proj)
for k, v in machine.items():
    if k in base: base[k] = v
for k, v in filament.items():
    if k in base and k not in ['name','type','from','version','instantiation']:
        base[k] = v*4 if isinstance(v, list) and len(v)==1 else v

base.update(
    printer_model='Snapmaker U1',
    printer_variant='0.4',
    printer_settings_id='Snapmaker U1 (0.4 nozzle)',
    nozzle_diameter=['0.4']*4,
    filament_settings_id=['Generic PLA @U1 base']*4,
    filament_type=['PLA']*4,
    filament_colour=['#3399FF']*4,
    printer_flow_support=['standard'],
    process_flow_support=['standard'],
    enable_support='0',
    sparse_infill_density='100%',
    wall_loops='4',
    layer_height='0.2',
    initial_layer_print_height='0.2',
    brim_type='no_brim',
    compatible_printers=['Snapmaker U1 (0.4 nozzle)'],
    compatible_prints=[],
    print_compatible_printers=['Snapmaker U1 (0.4 nozzle)']
)

def make_3mf(stl_path, out_3mf_path, part_name):
    m = E.Element('model', unit='millimeter', attrib={'xml:lang':'en-US', 'xmlns':NS})
    E.SubElement(m, 'metadata', name='Application').text = 'Snapmaker_Orca-2.4.1'
    E.SubElement(m, 'metadata', name='Snapmaker_Orca:3mfVersion').text = '1'
    res = E.SubElement(m, 'resources')
    build = E.SubElement(m, 'build')
    config = E.Element('config')
    assemble = E.Element('assemble')
    
    raw = stl_path.read_bytes()
    n = struct.unpack_from('<I', raw, 80)[0]
    verts = []
    tris = []
    lookup = {}
    for i in range(n):
        vals = struct.unpack_from('<12fH', raw, 84 + i * 50)
        ids = []
        for j in [3, 6, 9]:
            p = tuple(vals[j:j+3])
            key = tuple(round(v, 5) for v in p)
            if key not in lookup:
                lookup[key] = len(verts)
                verts.append(p)
            ids.append(lookup[key])
        if len(set(ids)) == 3:
            tris.append(ids)
            
    oid = 1
    o = E.SubElement(res, 'object', id=str(oid), type='model', name=part_name)
    mesh = E.SubElement(o, 'mesh')
    vs = E.SubElement(mesh, 'vertices')
    ts = E.SubElement(mesh, 'triangles')
    for v in verts:
        E.SubElement(vs, 'vertex', **{a: f'{x:.7f}' for a, x in zip('xyz', v)})
    for t in tris:
        E.SubElement(ts, 'triangle', **{f'v{i+1}': str(x) for i, x in enumerate(t)})
        
    transform = '1 0 0 0 1 0 0 0 1 135.5 135.5 0'
    E.SubElement(build, 'item', objectid=str(oid), transform=transform, printable='1')
    
    co = E.SubElement(config, 'object', id=str(oid))
    for k, v in [
        ('name', part_name),
        ('extruder', '1'),
        ('enable_support', '0'),
        ('wall_loops', '4'),
        ('sparse_infill_density', '100%'),
        ('brim_type', 'no_brim')
    ]:
        E.SubElement(co, 'metadata', key=k, value=v)
        
    part = E.SubElement(co, 'part', id=str(oid), subtype='normal_part')
    E.SubElement(part, 'metadata', key=k, value=part_name)
    
    plate = E.SubElement(config, 'plate')
    for k, v in [
        ('plater_id', '1'),
        ('plater_name', part_name),
        ('locked', 'false'),
        ('filament_map_mode', 'Auto For Flush'),
        ('filament_maps', '1 1 1 1')
    ]:
        E.SubElement(plate, 'metadata', key=k, value=v)
        
    instance = E.SubElement(plate, 'model_instance')
    for k, v in [('object_id', str(oid)), ('instance_id', '0'), ('identify_id', '101')]:
        E.SubElement(instance, 'metadata', key=k, value=v)
        
    E.SubElement(assemble, 'assemble_item', object_id=str(oid), instance_id='0', transform=transform, offset='0 0 0')
    config.append(assemble)
    
    with zipfile.ZipFile(out_3mf_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version=\"1.0\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"model\" ContentType=\"application/vnd.ms-package.3dmanufacturing-3dmodel+xml\"/><Default Extension=\"config\" ContentType=\"text/xml\"/></Types>')
        z.writestr('_rels/.rels', '<?xml version=\"1.0\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Target=\"/3D/3dmodel.model\" Id=\"rel0\" Type=\"http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel\"/></Relationships>')
        z.writestr('3D/3dmodel.model', E.tostring(m, encoding='utf-8', xml_declaration=True))
        z.writestr('Metadata/model_settings.config', E.tostring(config, encoding='utf-8', xml_declaration=True))
        z.writestr('Metadata/project_settings.config', json.dumps(base, indent=2))
    print(f'Generated {out_3mf_path.name} ({out_3mf_path.stat().st_size / 1024:.1f} KB)')

if __name__ == '__main__':
    make_3mf(PINS_DIR / '04_Lamp_Snap_Pin_BiDirectional.stl', PINS_PROJ_DIR / '00_Single_Snap_Pin_BiDirectional-U1.3mf', '04_Lamp_Snap_Pin_BiDirectional')
    make_3mf(PINS_DIR / 'Pins_Test_Sampler_Kit.stl', PINS_PROJ_DIR / '01_Pins_Test_Sampler_Kit-U1.3mf', 'Pins_Test_Sampler_Kit')
    make_3mf(PINS_DIR / 'Pins_Full_Batch_28x_BiDirectional.stl', PINS_PROJ_DIR / '02_Pins_Full_Batch_28x_BiDirectional-U1.3mf', 'Pins_Full_Batch_28x_BiDirectional')
    make_3mf(PINS_DIR / 'Pins_Full_Batch_28x_TwoPiece.stl', PINS_PROJ_DIR / '03_Pins_Full_Batch_28x_TwoPiece-U1.3mf', 'Pins_Full_Batch_28x_TwoPiece')
