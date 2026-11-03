"""Rebuild the share package without reserializing model XML.

The previous packaging step introduced ns0: tag prefixes which the installed
Snapmaker importer fails to recognize. Retain the successfully sliced original
model bytes. Test the actual extracted delivery payload separately.
"""
from pathlib import Path
import hashlib,zipfile,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Printable-fixed';SHARE=ROOT/'Share-with-cousin';NAME='Lamp-TALLER-FIXED-U1-3-shades-REPAIRED.3mf'
source=OUT/'Projects/Lamp-TALLER-FIXED-U1-3-shades.3mf';dest=SHARE/NAME
with zipfile.ZipFile(source) as z:
 model=z.read('3D/3dmodel.model');assert b'<model ' in model and b'<ns0:' not in model
 config=E.fromstring(z.read('Metadata/model_settings.config'))
 assert [len(p.findall('model_instance')) for p in config.findall('plate')]==[3,1,1]
 for p,name in zip(config.findall('plate'),['01_Three_taller_shades_PRINT_4_TIMES','02_Taller_carrier_PRINT_ONCE','03_Stand_PRINT_ONCE']):p.find("metadata[@key='plater_name']").set('value',name)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
  for n in z.namelist():out.writestr(n,E.tostring(config,encoding='utf-8',xml_declaration=True) if n=='Metadata/model_settings.config' else z.read(n))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 assert z.read('3D/3dmodel.model')==model
readme='''TALLER FIXED LAMP - REPAIRED PACKAGE

1. Extract this outer ZIP completely into a folder.
2. In Snapmaker Orca choose Open Project and open:
   Lamp-TALLER-FIXED-U1-3-shades-REPAIRED.3mf
   Do not unzip the 3MF itself. It is the project file.
3. Select your actual filament profile and re-slice for your U1's
   standard 0.4 mm nozzles.

Plate 1: 3 taller shade pieces. Print this plate four times for 12.
Plate 2: 1 taller LED carrier. Print once.
Plate 3: 1 stand. Print once.

The shade is 134.2 mm tall in the assembled lamp and the carrier is
41.5 mm tall. Models are already oriented and arranged for printing.
Supports/brims and reduced support speeds are included. Inspect the
first batch for printed fit, support removal and adhesion before
repeating the shade plate.

FALLBACK ONLY, IF YOUR SLICER VERSION CANNOT OPEN THE PROJECT:
Import the three STL files from STL-fallback. They contain actual model
geometry in millimetres, in print orientations. STLs do not carry print
settings. Select your U1 0.4 mm printer/material profiles and set up the
supports and brims yourself. Duplicate the shade three times and arrange
on one plate. Print carrier and stand on separate plates. Confirm scale
and slice previews before printing.

The model geometry matches the fixed taller export. This repair fixes
project-file packaging, not dimensions or mechanical design. Physical
printed tolerances, clip retention, heat suitability and strength still
require a test print.
'''
bundle=SHARE/'Lamp-TALLER-FIXED-U1-REPAIRED.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(dest,NAME);z.writestr('READ-ME.txt',readme)
 for f in sorted((OUT/'Models').glob('*.stl')):z.write(f,'STL-fallback/'+f.name)
# The validation must open the exact bytes the recipient extracts.
extract=OUT/'Checks/Compatibility/Extracted-delivery';extract.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(bundle) as z:
 assert z.testzip() is None
 data=z.read(NAME);assert data==dest.read_bytes();(extract/NAME).write_bytes(data)
manifest={'geometry_xml_sha256':hashlib.sha256(model).hexdigest(),'geometry_xml_unchanged_from_sliced_source':True,'replacement':str(dest),'replacement_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'zip':str(bundle),'zip_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'validation_input':str(extract/NAME),'plates':[3,1,1]}
(OUT/'Checks/Compatibility/repair-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
