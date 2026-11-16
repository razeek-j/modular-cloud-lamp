"""Render the saved, checked V12 geometry without regenerating it."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-v12'
scene=bpy.context.scene
readme=bpy.data.texts.get('START HERE · V12 shape revision') or bpy.data.texts.new('START HERE · V12 shape revision')
readme.clear();readme.write((OUT/'README.md').read_text())
cameras=sorted([o for o in scene.objects if o.type=='CAMERA'],key=lambda o:o.name)
scene.camera=cameras[0]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
for cam,name in zip(cameras,['01-Lamp-alone','02-Underside','03-Low-side','04-Rear-hook']):
    scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
for o in bpy.data.collections['05 · Fold light positions · optical study'].objects:o.hide_render=True
bpy.data.lights['Large soft key'].energy=65
bpy.data.lights['Soft edge fill'].energy=45
bpy.data.lights['Top softbox'].energy=90
scene.camera=cameras[0];scene.render.filepath=str(OUT/'05-Neutral-shape.png')
bpy.ops.render.render(write_still=True)
