import bpy, bmesh, math
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)

def create_bidirectional_snap_pin():
    """Build 1-piece double-ended snap-fit pin."""
    pts = []
    cx = 0.4        # collar half-thickness (total 0.8mm)
    cy_col = 3.3    # collar half-width (total 6.6mm)
    cy_body = 2.3   # body half-width (total 4.6mm)
    sw = 0.5        # slot half-width (total 1.0mm)
    
    # Collar top
    pts.append((cx, cy_col))
    pts.append((-cx, cy_col))
    pts.append((-cx, cy_body))
    
    # Left stem (+Y) - Bracket 1 depth 4.8mm
    pts.append((-5.2, cy_body))
    pts.append((-5.6, 2.7)) # barb shoulder (total width 5.4mm)
    pts.append((-7.8, 1.7)) # lead ramp
    pts.append((-8.0, 1.4)) # tip corner
    pts.append((-8.0, sw))  # inner slot corner
    
    # Left inner slot root
    for a in [90, 45, 0, -45, -90]:
        rad = math.radians(a)
        pts.append((-1.2 + 0.5 * math.cos(rad), 0.5 * math.sin(rad)))
        
    # Left stem (-Y)
    pts.append((-8.0, -sw))
    pts.append((-8.0, -1.4))
    pts.append((-7.8, -1.7))
    pts.append((-5.6, -2.7))
    pts.append((-5.2, -cy_body))
    pts.append((-cx, -cy_body))
    pts.append((-cx, -cy_col))
    
    # Collar bottom
    pts.append((cx, -cy_col))
    pts.append((cx, -cy_body))
    
    # Right stem (-Y) - Bracket 2 depth 5.0mm
    pts.append((5.4, -cy_body))
    pts.append((5.8, -2.7))
    pts.append((8.0, -1.7))
    pts.append((8.2, -1.4))
    pts.append((8.2, -sw))
    
    # Right inner slot root
    for a in [-90, -45, 0, 45, 90]:
        rad = math.radians(a)
        pts.append((1.2 - 0.5 * math.cos(rad), 0.5 * math.sin(rad)))
        
    # Right stem (+Y)
    pts.append((8.2, sw))
    pts.append((8.2, 1.4))
    pts.append((8.0, 1.7))
    pts.append((5.8, 2.7))
    pts.append((5.4, cy_body))
    pts.append((cx, cy_body))
    
    bm = bmesh.new()
    height = 4.6
    v_bot = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    v_top = [bm.verts.new((x, y, height)) for x, y in pts]
    bm.verts.ensure_lookup_table()
    N = len(pts)
    
    bm.faces.new(reversed(v_bot))
    bm.faces.new(v_top)
    for i in range(N):
        i_next = (i + 1) % N
        bm.faces.new([v_bot[i], v_bot[i_next], v_top[i_next], v_top[i]])
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Lamp_Snap_Pin_BiDirectional")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(me.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

ob = create_bidirectional_snap_pin()
print("Created:", ob.name, "verts:", len(ob.data.vertices), "faces:", len(ob.data.polygons))
