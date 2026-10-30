from pathlib import Path
import shutil,hashlib,json,zipfile
root=Path('/Users/razeek/Projects/3D printing')
archive=root/'Archive/2026-10-30'
support=root/'Support'
trash=Path('/Users/razeek/.Trash/Lamp-cleanup-2026-10-30')
if archive.exists() or trash.exists():raise SystemExit('Cleanup destination exists; inspect before proceeding.')
assert (root/'Lamp.blend').stat().st_size>1000000
moves=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def move(src,dst,reason):
 src=Path(src);dst=Path(dst)
 assert src.exists() and not dst.exists(),(src,dst)
 size=sum(p.stat().st_size for p in src.rglob('*') if p.is_file()) if src.is_dir() else src.stat().st_size
 sha=digest(src) if src.is_file() else None
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.move(str(src),str(dst))
 if sha:assert digest(dst)==sha
 moves.append({'from':str(src),'to':str(dst),'reason':reason,'bytes':size,'sha256':sha})
# Only remove byte-verified redundant content; preserve all unique revisions.
a=root/'lamp-centered-final.blend';b=root/'output/blender-lamp/lamp-centered-final.blend'
assert digest(a)==digest(b)
move(b,trash/'duplicates/lamp-centered-final.blend','Exact duplicate of retained historical root final')
for p in (root/'output').glob('*.zip'):
 with zipfile.ZipFile(p) as z:
  members=[i for i in z.infolist() if not i.is_dir()]
  redundant=bool(members) and all((root/'output'/i.filename).is_file() and hashlib.sha256(z.read(i)).hexdigest()==digest(root/'output'/i.filename) for i in members)
 if redundant:move(p,trash/'redundant-zips'/p.name,'Every archived member matches the retained extracted file byte for byte')
for p in list(root.rglob('.DS_Store')):
 move(p,trash/'metadata'/p.relative_to(root),'Regenerable Finder metadata')
cache=root/'output/blender-lamp/__pycache__'
if cache.exists():move(cache,trash/'cache/__pycache__','Regenerable Python bytecode cache')
move(root/'output/blender-lamp/reference',support/'References/Printed-parts','Original product reference photographs')
move(root/'output/lamp-connector-details/source-crops',support/'References/Detail-crops','Original product closeups')
move(root/'output/lamp-final-audit',support/'Checks/Previous-final-audit','Earlier final geometry audit; stand issue remains applicable')
for name in ['carrier-v09-checks.json','carrier-v09-preview.png']:
 move(root/'output/blender-lamp'/name,support/'Checks'/name,'Latest carrier checks and preview')
for name in ['lamp-centered-final.blend','lamp-thin-carrier-v09.blend']:
 move(root/name,archive/'Versions'/name,'Retained historical source version; use Lamp.blend for ongoing work')
move(root/'cutaway-preview.png',archive/'cutaway-preview.png','Previous preview')
move(root/'output',archive/'Earlier-work','All remaining previous builds, scripts and generated references')
manifest={'master':str(root/'Lamp.blend'),'master_sha256':digest(root/'Lamp.blend'),'moves':moves,'trash_bytes':sum(m['bytes'] for m in moves if m['to'].startswith(str(trash))),'unique_versions_preserved':True}
(support/'cleanup-manifest.json').write_text(json.dumps(manifest,indent=2))
(archive/'README.md').write_text('# Previous work\n\nUse ../../Lamp.blend for ongoing work. These are unique historical revisions and older previews, generated image interpretations, and build scripts. Original photographs are now in ../../Support/References.\n\nOld scripts and audit reports retain their historical absolute paths; do not run them without adapting paths and output destinations.\n')
(root/'README.md').write_text('''# Lamp project

Open **Lamp.blend** in Blender. This is the single working model and contains all lamp components, including the thin carrier revision.

Choose a scene from the menu at the top right:

1. **01 • Complete lamp** — the complete assembly; the default view.
2. **02 • Shade inspection** — the shade and its internal details.
3. **03 • Stand and LED carrier** — the stand, carrier and LED strip display model.
4. **04 • Thin carrier detail** — the 0.8 mm wall, narrow bottom glue rim and backed 2 mm-deep wire channel.

Save ongoing changes to Lamp.blend. Blender may create Lamp.blend1 automatically; that is its previous-save backup.

## Supporting files

- **Support/References** — original product photographs and detail crops.
- **Support/Checks** — geometry measurements, carrier checks and preview. The older final audit predates the thin-wall revision.
- **Support/cleanup-manifest.json** — where every moved file went, including Trash.
- **Archive/2026-10-30** — older unique versions, scripts and previous generated images. These are historical, not additional working masters.

## Current model status

Complete assembled dimensions are approximately 345.3 × 345.3 × 158.3 mm. The latest carrier clears the shade in its assembled position, and its mesh has zero nonmanifold edges.

**Unresolved: three stand leg roots intersect the shade.** The assembly is still a draft and needs this correction before a full print. Dimensions came from photographs; actual clips, wiring, connector clearance and physical print fit need testing. The LED strip is a display proxy.

Only verified duplicate content and regenerable metadata/cache were moved to Trash. Unique earlier versions remain in Archive. Nothing was permanently erased.
''')
print(json.dumps({'root_items':[p.name for p in root.iterdir()],'trash_bytes':manifest['trash_bytes'],'trash_location':str(trash),'moves':len(moves)},indent=2))
