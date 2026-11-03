import bpy, bmesh, math
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)

def create_female_socket():
    # Female part: flange at X from -6.55 to -5.35 (thickness 1.2, 8x8mm)
    # Sleeve: X from -5.35 to 0.0 (length 5.35, 4.6x4.6mm outer, 3.0x3.0mm inner)
    # Side windows: X from -3.5 to -1.8 (length 1.7, through Y=+-2.3)
    # We will build it cleanly as a manifold mesh
    bm = bmesh.new()
    
    # Create outer shape: box for flange, box for sleeve
    # Flange box: center at (-5.95, 0, 0), size (1.2, 8.0, 8.0)
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((1.2, 8.0, 8.0)), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector((-5.95, 0, 0)), verts=bm.verts)
    
    # Save flange verts
    flange_geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    
    me_flange = bpy.data.meshes.new("flange")
    bm.to_mesh(me_flange)
    bm.clear()
    ob_flange = bpy.data.objects.new("flange", me_flange)
    bpy.context.scene.collection.objects.link(ob_flange)
    
    # Sleeve box: center at (-2.675, 0, 0), size (5.35, 4.6, 4.6)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.675, 0, 0), scale=(5.35, 4.6, 4.6))
    ob_sleeve = bpy.context.active_object
    
    # Union flange and sleeve
    mod = ob_flange.modifiers.new(name='Union', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_sleeve
    bpy.context.view_layer.objects.active = ob_flange
    bpy.ops.object.modifier_apply(modifier='Union')
    bpy.data.objects.remove(ob_sleeve)
    
    # Bore cutter: size (6.0, 3.0, 3.0), center at (-2.5, 0, 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.5, 0, 0), scale=(6.0, 3.0, 3.0))
    ob_bore = bpy.context.active_object
    mod = ob_flange.modifiers.new(name='Diff_Bore', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_bore
    bpy.ops.object.modifier_apply(modifier='Diff_Bore')
    bpy.data.objects.remove(ob_bore)
    
    # Window cutter: size (1.7, 6.0, 2.2), center at (-2.65, 0, 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.65, 0, 0), scale=(1.7, 6.0, 2.2))
    ob_win = bpy.context.active_object
    mod = ob_flange.modifiers.new(name='Diff_Win', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_win
    bpy.ops.object.modifier_apply(modifier='Diff_Win')
    bpy.data.objects.remove(ob_win)
    
    ob_flange.name = "Lamp_TwoPiece_Female_Socket"
    return ob_flange

ob_fem = create_female_socket()
bm_fem = bmesh.new()
bm_fem.from_mesh(ob_fem.data)
print("Female socket:", ob_fem.name, "verts:", len(bm_fem.verts), "non-manifold:", sum(not e.is_manifold for e in bm_fem.edges), "vol:", bm_fem.calc_volume())
bm_fem.free()

def create_male_latch():
    # Flange: 8.0 x 8.0 x 1.2 at X from 5.35 to 6.55 (center at 5.95)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5.95, 0, 0), scale=(1.2, 8.0, 8.0))
    ob_flange = bpy.context.active_object
    
    # Shaft stem: from 5.35 to -2.0 (length 7.35, 2.7x2.7)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.675, 0, 0), scale=(7.35, 2.7, 2.7))
    ob_stem = bpy.context.active_object
    
    mod = ob_flange.modifiers.new(name='Union_Stem', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_stem
    bpy.context.view_layer.objects.active = ob_flange
    bpy.ops.object.modifier_apply(modifier='Union_Stem')
    bpy.data.objects.remove(ob_stem)
    
    # Barb wedge: from -2.0 to -4.0 (length 2.0)
    # We can create a tapered prism for the barb tip
    # at X=-2.0, size is 3.5 x 2.7; at X=-4.0, size is 1.8 x 2.7
    me_barb = bpy.data.meshes.new("barb")
    bm_barb = bmesh.new()
    # 8 verts of the frustum
    # Back face at X = -2.0 (Y = +-1.75, Z = +-1.35)
    v1 = bm_barb.verts.new((-2.0, -1.75, -1.35))
    v2 = bm_barb.verts.new((-2.0,  1.75, -1.35))
    v3 = bm_barb.verts.new((-2.0,  1.75,  1.35))
    v4 = bm_barb.verts.new((-2.0, -1.75,  1.35))
    # Front face at X = -4.0 (Y = +-0.9, Z = +-1.35)
    v5 = bm_barb.verts.new((-4.0, -0.9, -1.35))
    v6 = bm_barb.verts.new((-4.0,  0.9, -1.35))
    v7 = bm_barb.verts.new((-4.0,  0.9,  1.35))
    v8 = bm_barb.verts.new((-4.0, -0.9,  1.35))
    bm_barb.verts.ensure_lookup_table()
    
    bm_barb.faces.new([v1, v2, v3, v4]) # back (+X)
    bm_barb.faces.new([v8, v7, v6, v5]) # front (-X)
    bm_barb.faces.new([v5, v6, v2, v1]) # bottom (-Z)
    bm_barb.faces.new([v4, v3, v7, v8]) # top (+Z)
    bm_barb.faces.new([v1, v4, v8, v5]) # side (-Y)
    bm_barb.faces.new([v6, v7, v3, v2]) # side (+Y)
    bmesh.ops.recalc_face_normals(bm_barb, faces=bm_barb.faces)
    bm_barb.to_mesh(me_barb)
    bm_barb.free()
    ob_barb = bpy.data.objects.new("barb", me_barb)
    bpy.context.scene.collection.objects.link(ob_barb)
    
    mod = ob_flange.modifiers.new(name='Union_Barb', type='BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = ob_barb
    bpy.context.view_layer.objects.active = ob_flange
    bpy.ops.object.modifier_apply(modifier='Union_Barb')
    bpy.data.objects.remove(ob_barb)
    
    # Cut center slot: width 0.9 in Y, from X = -4.2 to X = 2.5 (length 6.7)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.85, 0, 0), scale=(6.7, 0.9, 3.5))
    ob_slot = bpy.context.active_object
    mod = ob_flange.modifiers.new(name='Diff_Slot', type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = ob_slot
    bpy.context.view_layer.objects.active = ob_flange
    bpy.ops.object.modifier_apply(modifier='Diff_Slot')
    bpy.data.objects.remove(ob_slot)
    
    ob_flange.name = "Lamp_TwoPiece_Male_Latch"
    return ob_flange

ob_male = create_male_latch()
bm_male = bmesh.new()
bm_male.from_mesh(ob_male.data)
print("Male latch:", ob_male.name, "verts:", len(bm_male.verts), "non-manifold:", sum(not e.is_manifold for e in bm_male.edges), "vol:", bm_male.calc_volume())
bm_male.free()
