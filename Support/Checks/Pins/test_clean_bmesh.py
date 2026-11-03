import bpy, bmesh, math
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)

def make_box(bm, x_range, y_range, z_range):
    """Create a watertight box primitive in bmesh."""
    x0, x1 = x_range
    y0, y1 = y_range
    z0, z1 = z_range
    verts = [
        bm.verts.new((x0, y0, z0)), # 0
        bm.verts.new((x1, y0, z0)), # 1
        bm.verts.new((x1, y1, z0)), # 2
        bm.verts.new((x0, y1, z0)), # 3
        bm.verts.new((x0, y0, z1)), # 4
        bm.verts.new((x1, y0, z1)), # 5
        bm.verts.new((x1, y1, z1)), # 6
        bm.verts.new((x0, y1, z1)), # 7
    ]
    bm.verts.ensure_lookup_table()
    bm.faces.new([verts[0], verts[3], verts[2], verts[1]]) # -Z
    bm.faces.new([verts[4], verts[5], verts[6], verts[7]]) # +Z
    bm.faces.new([verts[0], verts[1], verts[5], verts[4]]) # -Y
    bm.faces.new([verts[2], verts[3], verts[7], verts[6]]) # +Y
    bm.faces.new([verts[0], verts[4], verts[7], verts[3]]) # -X
    bm.faces.new([verts[1], verts[2], verts[6], verts[5]]) # +X
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return verts

# Test make_box
bm = bmesh.new()
make_box(bm, (-6.55, -5.35), (-4, 4), (0, 8))
assert sum(not e.is_manifold for e in bm.edges) == 0
assert bm.calc_volume() > 0
print("make_box works, vol:", bm.calc_volume())
bm.free()
