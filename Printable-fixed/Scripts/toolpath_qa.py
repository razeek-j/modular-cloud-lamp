"""Check actual generated extrusion paths and render first-layer/support previews."""
from pathlib import Path
import re,math,json
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1];S=OUT/'Checks/Slicing'
float_re=re.compile(r'([XYZE])(-?\d*\.?\d+)')
# Selected model/support layer views. Images are generated from toolpaths, not renders.
selected=[.2,2,20,40,60,80]
pal={'Brim':'#a3a7b0','Support':'#fdab41','Support interface':'#f36d35','Bridge':'#bc69dc','Internal Bridge':'#bc69dc'}
summary={};tiles=[]
try:font=ImageFont.truetype('/System/Library/Fonts/SFNS.ttf',18)
except:font=ImageFont.load_default()
for f in sorted(S.glob('plate_*.gcode')):
 x=y=0.;z=None;feature='';width=.42;layer=0;seen=defaultdict(float);bounds=[1e9,1e9,-1e9,-1e9];first=defaultdict(float);objects=set();est=[];segments={v:[] for v in selected};layer_features=defaultdict(lambda:defaultdict(float));firstbyobj=defaultdict(float);obj='';printable=False
 with f.open() as file:
  for line in file:
   if line.startswith(';LAYER_CHANGE'):layer+=1;printable=True
   elif line.startswith(';Z:'):z=float(line[3:])
   elif line.startswith(';TYPE:'):feature=line[6:].strip()
   elif line.startswith(';WIDTH:'):width=float(line[7:])
   elif line.startswith('EXCLUDE_OBJECT_DEFINE '):objects.add(line.split('NAME=')[1].split()[0])
   elif line.startswith('EXCLUDE_OBJECT_START '):obj=line.split('NAME=')[1].strip()
   if '; estimated printing time (normal mode)' in line or '; total filament used [g]' in line:est.append(line.strip())
   if not line.startswith(('G0 ','G1 ')):continue
   vals={k:float(v) for k,v in float_re.findall(line)};nx=vals.get('X',x);ny=vals.get('Y',y);e=vals.get('E',0)
   dist=math.hypot(nx-x,ny-y)
   if printable and z is not None and e>0 and dist>.0001 and ('X' in vals or 'Y' in vals):
    bounds=[min(bounds[0],x,nx),min(bounds[1],y,ny),max(bounds[2],x,nx),max(bounds[3],y,ny)]
    seen[feature]+=dist;layer_features[round(z,3)][feature]+=dist
    if layer==1:
     first[feature]+=dist
     if feature not in ['Support','Support interface','Brim','Skirt']:firstbyobj[obj]+=dist
    for h in selected:
     if abs(z-h)<.015:segments[h].append((x,y,nx,ny,feature,width))
   x,y=nx,ny
 layers=sorted(layer_features)
 summary[f.name]={'object_count':len(objects),'objects':sorted(objects),'layer_count':len(layers),'first_layer_model_extrusion_length_mm_by_object':dict(firstbyobj),'first_layer_features_length_mm':dict(first),'extrusion_bounds_xy_mm':bounds,'within_U1_plate':bounds[0]>=.5 and bounds[1]>=1 and bounds[2]<=270.5 and bounds[3]<=271,'support_present':seen.get('Support',0)>0,'support_interface_present':seen.get('Support interface',0)>0,'estimates':est}
 assert summary[f.name]['within_U1_plate'],summary[f.name]
 assert firstbyobj,'No model extrusion on first layer'
 if f.name!='plate_2.gcode':assert summary[f.name]['support_present'] and summary[f.name]['support_interface_present']
 for h in selected:
  if not segments[h]:continue
  size=600;scale=(size-60)/270;im=Image.new('RGB',(size,size+50),'#111720');draw=ImageDraw.Draw(im);draw.rectangle((30,30,size-30,size-30),outline='#58616c')
  for x,y,nx,ny,feat,w in segments[h]:
   points=(30+(x-.5)*scale,size-30-(y-1)*scale,30+(nx-.5)*scale,size-30-(ny-1)*scale)
   color=pal.get(feat,'#69d0dc');draw.line(points,fill=color,width=max(1,round(w*scale)))
  draw.text((25,size+7),f'{f.stem} | Z = {h:g} mm',fill='white',font=font);tiles.append(im)
(OUT/'Checks/toolpath-qa.json').write_text(json.dumps(summary,indent=2))
# Three columns per sheet; save readable individual first layers too.
for im in tiles:
 pass
rows=math.ceil(len(tiles)/3);sheet=Image.new('RGB',(1800,rows*650+60),'#111720');d=ImageDraw.Draw(sheet);d.text((25,15),'Cyan: model   Orange: supports   Grey: brim   Purple: bridges',fill='white',font=font)
for i,im in enumerate(tiles):sheet.paste(im,((i%3)*600,60+(i//3)*650))
sheet.save(OUT/'Checks/toolpath-previews.png')
print(json.dumps(summary,indent=2))
