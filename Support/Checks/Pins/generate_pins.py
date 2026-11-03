import bpy, bmesh, math
from mathutils import Vector, Matrix
from pathlib import Path
import json, struct

# Clear existing objects in Blender scene
bpy.ops.wm.read_factory_settings(use_empty=True)

out_dir = Path("/Users/razeek/Projects/3D printing/Printable-fixed/Models/Pins")
out_dir.mkdir(parents=True, exist_ok=True)

def create_mesh_object(name):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, me

def export_stl(ob, filepath):
    # Ensure all modifiers/mesh evaluated
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    with open(filepath, 'wb') as f:
        f.write(b'\x00' * 80)
        f.write(struct.pack('<I', len(bm.faces)))
        for face in bm.faces:
            n = face.normal
            v = [v.co for v in face.verts]
            f.write(struct.pack('<12fH', n.x, n.y, n.z,
                                v[0].x, v[0].y, v[0].z,
                                v[1].x, v[1].y, v[1].z,
                                v[2].x, v[2].y, v[2].z, 0))
    bm.free()
    print(f"Exported {filepath.name}: {filepath.stat().st_size} bytes")

print("Script template ready.")
