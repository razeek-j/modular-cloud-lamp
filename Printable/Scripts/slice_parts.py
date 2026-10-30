"""Use installed Snapmaker Orca profiles and CLI; export projects and validate toolpaths."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Printable';P=Path('/Applications/Snapmaker Orca.app/Contents/Resources/profiles/Snapmaker');EXE='/Applications/Snapmaker Orca.app/Contents/MacOS/Snapmaker_Orca'
lookup={}
for f in P.rglob('*.json'):
 try:
  j=json.loads(f.read_text(encoding='utf-8-sig'));lookup[j.get('name',f.stem)]=j
 except Exception:pass
def resolve(name):
 j=lookup[name];result=resolve(j['inherits']) if j.get('inherits') else {};result.update(j);result.pop('inherits',None);return result
machine=resolve('Snapmaker U1 (0.4 nozzle)');machine['printer_settings_id']='Snapmaker U1 (0.4 nozzle)'
filament=resolve('Generic PLA @U1 base');filament.update(name='Generic PLA @U1 prototype',instantiation='true',filament_settings_id=['Generic PLA @U1 prototype'],compatible_printers=['Snapmaker U1 (0.4 nozzle)'])
proc=resolve('0.20mm Standard @Snapmaker U1 (0.4 nozzle)')
proc.update(enable_prime_tower='0',wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_type='outer_only',brim_width='5',brim_object_gap='0.15',enable_support='1',support_type='normal(auto)',support_on_build_plate_only='0',support_threshold_angle='35',support_top_z_distance='0.2',support_bottom_z_distance='0.2',support_object_xy_distance='0.35',support_interface_top_layers='3',support_interface_bottom_layers='2',outer_wall_speed=['60','60'],inner_wall_speed=['100','100'],sparse_infill_speed=['100','100'],initial_layer_speed='25',top_shell_layers='5',bottom_shell_layers='5',curr_bed_type='Textured PEI Plate',reduce_infill_retraction='0')
for name,data in [('machine',machine),('filament',filament)]: (OUT/'Checks'/f'{name}.json').write_text(json.dumps(data,indent=2))
for f in sorted((OUT/'Models').glob('*.stl')):
 process=dict(proc)
 if 'carrier' in f.stem:process.update(enable_support='0',brim_type='outer_and_inner',brim_width='4',outer_wall_speed=['40','40'])
 if 'Stand' in f.stem:process.update(sparse_infill_density='35%',wall_loops='5')
 process['name']='Lamp prototype - '+f.stem;process['print_settings_id']=process['name'];process['from']='user'
 settings=OUT/'Checks'/f'{f.stem}-process.json';settings.write_text(json.dumps(process,indent=2))
 cmd=[EXE,'--debug','2','--load-settings',str(OUT/'Checks/machine.json')+';'+str(settings),'--load-filaments',str(OUT/'Checks/filament.json'),'--orient','0','--arrange','1','--ensure-on-bed','--slice','0','--export-3mf',str(OUT/'Projects'/f'{f.stem}-U1.3mf'),'--outputdir',str(OUT/'Checks'/f.stem),str(f)]
 with (OUT/'Checks'/f'{f.stem}-slice.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 print(f.stem,'EXIT',r.returncode,flush=True)
 if r.returncode:print((OUT/'Checks'/f'{f.stem}-slice.log').read_text()[-6000:],flush=True);break
