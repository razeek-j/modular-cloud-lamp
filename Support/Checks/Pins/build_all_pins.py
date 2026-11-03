"""Master generator for lamp connection pins, test plates, full batch plates, and verification audits."""
import bpy, bmesh, math, struct, json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path("/Users/razeek/Projects/3D printing")
OUT_MODELS = ROOT / "Printable-fixed" / "Models" / "Pins"
OUT_CHECKS = ROOT / "Support" / "Checks" / "Pins"
OUT_MODELS.mkdir(parents=True, exist_ok=True)
OUT_CHECKS.mkdir(parents=True, exist_ok=True)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 0.001
    s.unit_settings.length_unit = 'MILLIMETERS'
    return s

def export_stl(obj, filepath):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    with open(filepath, 'wb') as f:
        f.write(b'\x00' * 80)
        f.write(struct.pack('<I', len(bm.faces)))
        for face in bm.faces:
            n = face.normal
            v = [face.verts[0].co, face.verts[1].co, face.verts[2].co]
            f.write(struct.pack('<12fH', n.x, n.y, n.z,
                                v[0].x, v[0].y, v[0].z,
                                v[1].x, v[1].y, v[1].z,
                                v[2].x, v[2].y, v[2].z, 0))
    bm.free()
    kb = filepath.stat().st_size / 1024
    print(f"Exported {filepath.name} ({kb:.1f} KB)")

def audit_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_m = sum(not e.is_manifold for e in bm.edges)
    degen = sum(f.calc_area() < 1e-8 for f in bm.faces)
    vol = bm.calc_volume()
    bounds = [[min(v.co[i] for v in bm.verts), max(v.co[i] for v in bm.verts)] for i in range(3)]
    dims = [b[1] - b[0] for b in bounds]
    bm.free()
    return {
        'name': obj.name,
        'non_manifold_edges': non_m,
        'degenerate_faces': degen,
        'signed_volume_mm3': vol,
        'dimensions_mm': dims,
        'bounds_mm': bounds,
        'is_manifold': (non_m == 0 and degen == 0 and vol > 0)
    }

# -------------------------------------------------------------
# 1. Type 1: BiDirectional Snap Pin (1-Piece Push-and-Click)
# -------------------------------------------------------------
def build_bidirectional_snap_pin(name="Lamp_Snap_Pin_BiDirectional"):
    pts = []
    cx = 0.4        # collar half-thickness (total 0.8mm)
    cy_col = 3.3    # collar half-width (total 6.6mm)
    cy_body = 2.3   # body half-width (total 4.6mm)
    sw = 0.5        # slot half-width (total 1.0mm)
    
    # Collar top (+Y)
    pts.append((cx, cy_col))
    pts.append((-cx, cy_col))
    pts.append((-cx, cy_body))
    
    # Left stem (+Y) - Segment 1 Bracket (depth 4.8mm)
    pts.append((-5.2, cy_body))
    pts.append((-5.6, 2.7)) # barb shoulder (total width 5.4mm)
    pts.append((-7.8, 1.7)) # lead-in ramp
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
    
    # Collar bottom (-Y)
    pts.append((cx, -cy_col))
    pts.append((cx, -cy_body))
    
    # Right stem (-Y) - Segment 2 Bracket (depth 5.0mm)
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
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

# -------------------------------------------------------------
# 2. Type 2: Two-Piece Male/Female Push-Lock Pin
# -------------------------------------------------------------
def build_two_piece_female(name="Lamp_TwoPiece_Female_Socket"):
    # Flange: 8.0 x 8.0 x 1.2 at X from -6.55 to -5.35 (center -5.95, Z center 4.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.95, 0, 4.0), scale=(1.2, 8.0, 8.0))
    ob = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Sleeve: 5.35 x 4.6 x 4.6 at X from -5.35 to 0.0 (center -2.675, Z center 4.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.675, 0, 4.0), scale=(5.35, 4.6, 4.6))
    ob_sleeve = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mod = ob.modifiers.new(name='Union_Sleeve', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_sleeve
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Union_Sleeve')
    bpy.data.objects.remove(ob_sleeve)
    
    # Bore: 3.0 x 3.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.5, 0, 4.0), scale=(6.0, 3.0, 3.0))
    ob_bore = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mod = ob.modifiers.new(name='Diff_Bore', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_bore
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Diff_Bore')
    bpy.data.objects.remove(ob_bore)
    
    # Windows: 1.7 x 6.0 x 2.2 at center -2.65
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.65, 0, 4.0), scale=(1.7, 6.0, 2.2))
    ob_win = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mod = ob.modifiers.new(name='Diff_Win', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_win
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Diff_Win')
    bpy.data.objects.remove(ob_win)
    
    ob.name = name
    return ob

def build_two_piece_male(name="Lamp_TwoPiece_Male_Latch"):
    # Flange: 8.0 x 8.0 x 1.2 at X from 5.35 to 6.55 (center 5.95, Z center 4.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5.95, 0, 4.0), scale=(1.2, 8.0, 8.0))
    ob = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Stem: 7.25 x 2.7 x 2.7 from 5.35 to -1.9 (center 1.725, Z center 4.0; overlaps barb by 0.1 to prevent coplanar boolean slivers)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.725, 0, 4.0), scale=(7.25, 2.7, 2.7))
    ob_stem = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mod = ob.modifiers.new(name='Union_Stem', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_stem
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Union_Stem')
    bpy.data.objects.remove(ob_stem)
    
    # Barb tip wedge: from -1.8 to -3.8 (length 2.0, width 3.5 down to 1.8)
    me_barb = bpy.data.meshes.new("barb")
    bm_barb = bmesh.new()
    v1 = bm_barb.verts.new((-1.8, -1.75, 2.65))
    v2 = bm_barb.verts.new((-1.8,  1.75, 2.65))
    v3 = bm_barb.verts.new((-1.8,  1.75, 5.35))
    v4 = bm_barb.verts.new((-1.8, -1.75, 5.35))
    v5 = bm_barb.verts.new((-3.8, -0.9, 2.65))
    v6 = bm_barb.verts.new((-3.8,  0.9, 2.65))
    v7 = bm_barb.verts.new((-3.8,  0.9, 5.35))
    v8 = bm_barb.verts.new((-3.8, -0.9, 5.35))
    bm_barb.verts.ensure_lookup_table()
    bm_barb.faces.new([v1, v2, v3, v4])
    bm_barb.faces.new([v8, v7, v6, v5])
    bm_barb.faces.new([v5, v6, v2, v1])
    bm_barb.faces.new([v4, v3, v7, v8])
    bm_barb.faces.new([v1, v4, v8, v5])
    bm_barb.faces.new([v6, v7, v3, v2])
    bmesh.ops.recalc_face_normals(bm_barb, faces=bm_barb.faces)
    bm_barb.to_mesh(me_barb); bm_barb.free()
    ob_barb = bpy.data.objects.new("barb", me_barb)
    bpy.context.scene.collection.objects.link(ob_barb)
    
    mod = ob.modifiers.new(name='Union_Barb', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_barb
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Union_Barb')
    bpy.data.objects.remove(ob_barb)
    
    # Slot: width 0.9 in Y, from X = -4.0 to X = 2.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.75, 0, 4.0), scale=(6.5, 0.9, 3.5))
    ob_slot = bpy.context.active_object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    mod = ob.modifiers.new(name='Diff_Slot', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_slot
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier='Diff_Slot')
    bpy.data.objects.remove(ob_slot)
    
    ob.name = name
    return ob

# -------------------------------------------------------------
# 3. Type 3: Alignment Dowel Pin
# -------------------------------------------------------------
def build_alignment_dowel(name="Lamp_Alignment_Dowel_Pin"):
    pts = [
        (0.4, 3.3), (-0.4, 3.3), (-0.4, 2.325),
        (-5.4, 2.325), (-5.8, 1.9), (-5.8, -1.9), (-5.4, -2.325),
        (-0.4, -2.325), (-0.4, -3.3), (0.4, -3.3), (0.4, -2.325),
        (5.6, -2.325), (6.0, -1.9), (6.0, 1.9), (5.6, 2.325),
        (0.4, 2.325)
    ]
    bm = bmesh.new()
    height = 4.65
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
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

def main():
    audits = []
    
    # 1. Export BiDirectional pin
    reset()
    ob1 = build_bidirectional_snap_pin("Lamp_Snap_Pin_BiDirectional")
    p1 = OUT_MODELS / "04_Lamp_Snap_Pin_BiDirectional.stl"
    export_stl(ob1, p1)
    audits.append(audit_mesh(ob1))
    
    # 2. Export Female socket
    reset()
    ob_fem = build_two_piece_female("Lamp_TwoPiece_Female_Socket")
    p_fem = OUT_MODELS / "05_Lamp_TwoPiece_Female_Socket.stl"
    export_stl(ob_fem, p_fem)
    audits.append(audit_mesh(ob_fem))
    
    # 3. Export Male latch
    reset()
    ob_male = build_two_piece_male("Lamp_TwoPiece_Male_Latch")
    p_male = OUT_MODELS / "06_Lamp_TwoPiece_Male_Latch.stl"
    export_stl(ob_male, p_male)
    audits.append(audit_mesh(ob_male))
    
    # 4. Export Two-piece pair (one female + one male flat on bed)
    reset()
    ob_f = build_two_piece_female("Female_Part")
    ob_m = build_two_piece_male("Male_Part")
    ob_f.location = Vector((0, -6.0, 0))
    ob_m.location = Vector((0,  6.0, 0))
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = ob_f
    ob_f.select_set(True); ob_m.select_set(True)
    bpy.ops.object.join()
    ob_pair = bpy.context.active_object
    ob_pair.name = "Lamp_TwoPiece_PushLock_Pair"
    p_pair = OUT_MODELS / "07_Lamp_TwoPiece_Pair.stl"
    export_stl(ob_pair, p_pair)
    audits.append(audit_mesh(ob_pair))
    
    # 5. Export Alignment dowel
    reset()
    ob_dow = build_alignment_dowel("Lamp_Alignment_Dowel_Pin")
    p_dow = OUT_MODELS / "08_Lamp_Alignment_Dowel.stl"
    export_stl(ob_dow, p_dow)
    audits.append(audit_mesh(ob_dow))
    
    # 6. Test Kit: 2x BiDirectional, 2x TwoPiece Pairs, 2x Dowels
    reset()
    test_objs = []
    for i in range(2):
        o = build_bidirectional_snap_pin(f"BiDir_{i}")
        o.location = Vector((i * 22.0 - 11.0, -22.0, 0))
        test_objs.append(o)
    for i in range(2):
        f = build_two_piece_female(f"Fem_{i}")
        m = build_two_piece_male(f"Male_{i}")
        f.location = Vector((i * 22.0 - 11.0, -7.0, 0))
        m.location = Vector((i * 22.0 - 11.0,  7.0, 0))
        test_objs.extend([f, m])
    for i in range(2):
        d = build_alignment_dowel(f"Dowel_{i}")
        d.location = Vector((i * 22.0 - 11.0, 22.0, 0))
        test_objs.append(d)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = test_objs[0]
    for o in test_objs: o.select_set(True)
    bpy.ops.object.join()
    ob_kit = bpy.context.active_object
    ob_kit.name = "Pins_Test_Sampler_Kit"
    p_kit = OUT_MODELS / "Pins_Test_Sampler_Kit.stl"
    export_stl(ob_kit, p_kit)
    audits.append(audit_mesh(ob_kit))
    
    # 7. Full batch of 28 BiDirectional pins (24 required + 4 spares)
    reset()
    batch_objs = []
    for r in range(4):
        for c in range(7):
            idx = r * 7 + c
            o = build_bidirectional_snap_pin(f"Pin_{idx}")
            o.location = Vector((c * 20.0 - 60.0, r * 10.0 - 15.0, 0))
            batch_objs.append(o)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = batch_objs[0]
    for o in batch_objs: o.select_set(True)
    bpy.ops.object.join()
    ob_batch = bpy.context.active_object
    ob_batch.name = "Pins_Full_Batch_28x_BiDirectional"
    p_batch = OUT_MODELS / "Pins_Full_Batch_28x_BiDirectional.stl"
    export_stl(ob_batch, p_batch)
    audits.append(audit_mesh(ob_batch))
    
    # 8. Full batch of 28 Two-Piece Pairs (28 male + 28 female)
    reset()
    batch_tp = []
    for r in range(4):
        for c in range(7):
            idx = r * 7 + c
            f = build_two_piece_female(f"Fem_{idx}")
            m = build_two_piece_male(f"Male_{idx}")
            f.location = Vector((c * 20.0 - 60.0, r * 20.0 - 30.0 - 5.5, 0))
            m.location = Vector((c * 20.0 - 60.0, r * 20.0 - 30.0 + 5.5, 0))
            batch_tp.extend([f, m])
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = batch_tp[0]
    for o in batch_tp: o.select_set(True)
    bpy.ops.object.join()
    ob_tp_batch = bpy.context.active_object
    ob_tp_batch.name = "Pins_Full_Batch_28x_TwoPiece"
    p_tp_batch = OUT_MODELS / "Pins_Full_Batch_28x_TwoPiece.stl"
    export_stl(ob_tp_batch, p_tp_batch)
    audits.append(audit_mesh(ob_tp_batch))
    
    # Save audit report
    audit_path = OUT_CHECKS / "pins-audit.json"
    audit_path.write_text(json.dumps(audits, indent=2))
    print(f"\nSaved audit report with {len(audits)} models to {audit_path}")
    for a in audits:
        print(f"- {a['name']}: manifold={a['is_manifold']}, non-m={a['non_manifold_edges']}, vol={a['signed_volume_mm3']:.1f} mm3, dims={[round(x,2) for x in a['dimensions_mm']]}")

def clean_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()

if __name__ == '__main__':
    main()
