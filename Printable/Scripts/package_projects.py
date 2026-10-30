"""Create standard millimetre 3MF models with native Snapmaker settings, one part per plate."""
from pathlib import Path
import zipfile,struct,json,xml.etree.ElementTree as E,uuid
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Printable';NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
template=zipfile.ZipFile(OUT/'Checks/UI-template.3mf');default=json.loads(template.read('Metadata/project_settings.config'))
machine=json.loads((OUT/'Checks/machine.json').read_text());filament=json.loads((OUT/'Checks/filament.json').read_text())
# Native full-project format has four selected materials and scalar process speeds.
base=dict(default)
for k,v in machine.items():
 if k in base:base[k]=v
for k,v in filament.items():
 if k in base and k not in ['name','type','from','version','instantiation']:base[k]=v*4 if isinstance(v,list) and len(v)==1 else v
base.update(printer_model='Snapmaker U1',printer_variant='0.4',printer_settings_id='Snapmaker U1 (0.4 nozzle)',nozzle_diameter=['0.4']*4,filament_settings_id=['Generic PLA @U1 base']*4,filament_type=['PLA']*4,filament_colour=['#F4F1E8','#F4F1E8','#F4F1E8','#F4F1E8'],printer_flow_support=['standard'],process_flow_support=['standard'])
files=sorted((OUT/'Models').glob('*.stl'))
def make(files,path):
 m=E.Element('model',unit='millimeter',attrib={'xml:lang':'en-US','xmlns':NS});E.SubElement(m,'metadata',name='Application').text='Snapmaker_Orca-2.4.1';E.SubElement(m,'metadata',name='Snapmaker_Orca:3mfVersion').text='1';res=E.SubElement(m,'resources');build=E.SubElement(m,'build');config=E.Element('config');assemble=E.Element('assemble')
 for idx,f in enumerate(files):
  raw=f.read_bytes();n=struct.unpack_from('<I',raw,80)[0];verts=[];tris=[];lookup={}
  for i in range(n):
   vals=struct.unpack_from('<12fH',raw,84+i*50);ids=[]
   for j in [3,6,9]:
    p=tuple(vals[j:j+3]);key=tuple(round(v,5) for v in p)
    if key not in lookup:lookup[key]=len(verts);verts.append(p)
    ids.append(lookup[key])
   if len(set(ids))==3:tris.append(ids)
  oid=idx+1;o=E.SubElement(res,'object',id=str(oid),type='model',name=f.stem);mesh=E.SubElement(o,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
  for v in verts:E.SubElement(vs,'vertex',**{a:f'{x:.7f}' for a,x in zip('xyz',v)})
  for t in tris:E.SubElement(ts,'triangle',**{f'v{i+1}':str(x) for i,x in enumerate(t)})
  x=135.5+(idx%2)*324;y=136-(idx//2)*324;transform=f'1 0 0 0 1 0 0 0 1 {x} {y} 0';E.SubElement(build,'item',objectid=str(oid),transform=transform,printable='1')
  co=E.SubElement(config,'object',id=str(oid))
  for k,v in [('name',f.stem),('extruder','1'),('enable_support','0' if 'carrier' in f.stem else '1'),('wall_loops','5' if 'Stand' in f.stem else '4'),('sparse_infill_density','35%' if 'Stand' in f.stem else '20%')]:E.SubElement(co,'metadata',key=k,value=v)
  part=E.SubElement(co,'part',id=str(oid),subtype='normal_part');E.SubElement(part,'metadata',key='name',value=f.stem)
  plate=E.SubElement(config,'plate')
  for k,v in [('plater_id',str(idx+1)),('plater_name',f.stem),('locked','false'),('filament_map_mode','Auto For Flush'),('filament_maps','1 1 1 1')]:E.SubElement(plate,'metadata',key=k,value=v)
  instance=E.SubElement(plate,'model_instance')
  for k,v in [('object_id',str(oid)),('instance_id','0'),('identify_id',str(100+oid))]:E.SubElement(instance,'metadata',key=k,value=v)
  E.SubElement(assemble,'assemble_item',object_id=str(oid),instance_id='0',transform=transform,offset='0 0 0')
 config.append(assemble)
 process=json.loads((OUT/'Checks/01_Shade_segment-process.json').read_text());settings=dict(base)
 for k,v in process.items():
  if k in settings and k not in ['name','type','from','version','instantiation','compatible_printers']:settings[k]=v[0] if isinstance(v,list) and len(v)==2 and k.endswith('speed') else v
 settings.update(print_settings_id='Lamp U1 prototype 0.20mm - supports',layer_height='0.2',initial_layer_print_height='0.2',compatible_printers=['Snapmaker U1 (0.4 nozzle)'],compatible_prints=[],print_compatible_printers=['Snapmaker U1 (0.4 nozzle)'])
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="text/xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',E.tostring(m,encoding='utf-8',xml_declaration=True));z.writestr('Metadata/model_settings.config',E.tostring(config,encoding='utf-8',xml_declaration=True));z.writestr('Metadata/project_settings.config',json.dumps(settings,indent=2))
for f in files:make([f],OUT/'Projects'/f'{f.stem}-U1.3mf')
make(files,OUT/'Projects/Lamp-three-parts-U1.3mf');print('Packaged three individual projects and three-plate project')
