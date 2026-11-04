import bpy,json
from pathlib import Path
R=Path('/Users/razeek/Projects/3D printing/Circular-Ribbon-Lamp')
for name,p in [('V06 • source','scripts/build_v06_light_deck.py'),('V06 • plan','PLAN.md'),('V06 • process journal','PROCESS.md'),('V06 • lighting study','lighting-v06/README.md'),('V06 • overlap export status','prototype-v06/README.md')]:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write((R/p).read_text())
s=bpy.context.scene;s['appearance_gate']='NOT PASSED: crowded centre, visible deck edge/returns, weak lower-wave illumination. See PLAN.md.';s['manufacturing_gate']='NOT PASSED: overlap export has 241 triangle overlap candidates. Do not print.';s['process_media']='08-v06-rendered-stage-review.mp4 — rendered review, not live editing; Mac locked.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Circular-Ribbon-Cloud-v06-light-deck.blend'),compress=True)
print('Saved V06 with updated embedded plan, journal, lighting and honest acceptance status.')
