"""Generate printable connector pins for the 12-segment lamp assembly."""
import bpy, bmesh, math, struct
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / 'Printable-fixed' / 'Models' / 'Pins'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def export_stl(mesh_obj, path):
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    with open(path, 'wb') as f:
        f.write(b'\x00' * 80)
        f.write(struct.pack('<I', len(bm.faces)))
        for face in bm.faces:
            n = face.normal
            verts = [face.verts[0].co, face.verts[1].co, face.verts[2].co]
            f.write(struct.pack('<12fH', n.x, n.y, n.z,
                                verts[0].x, verts[0].y, verts[0].z,
                                verts[1].x, verts[1].y, verts[1].z,
                                verts[2].x, verts[2].y, verts[2].z, 0))
    bm.free()
    size_kb = path.stat().st_size / 1024
    print(f"Exported {path.name}: {size_kb:.1f} KB")

def audit_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(not e.is_manifold for e in bm.edges)
    degenerate = sum(f.calc_area() < 1e-8 for f in bm.faces)
    vol = bm.calc_volume()
    bounds = [Vector((min(v.co[i] for v in bm.verts), max(v.co[i] for v in bm.verts))) for i in range(3)]
    dims = [b.y - b.x for b in bounds]
    bm.free()
    report = {
        'name': obj.name,
        'non_manifold_edges': non_manifold,
        'degenerate_faces': degenerate,
        'volume_mm3': vol,
        'dimensions_mm': dims,
        'is_manifold': (non_manifold == 0 and degenerate == 0 and vol > 0)
    }
    return report

print("Pins script framework ready.")
