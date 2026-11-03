import bpy, bmesh

bpy.ops.wm.read_factory_settings(use_empty=True)

# Flange at X from 5.35 to 6.55 (center 5.95)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5.95, 0, 4.0), scale=(1.2, 8.0, 8.0))
ob_flange = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Stem from 5.35 to -1.8 (center 1.775, length 7.15, size 2.7x2.7)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.775, 0, 4.0), scale=(7.15, 2.7, 2.7))
ob_stem = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

mod = ob_flange.modifiers.new(name='Union_Stem', type='BOOLEAN')
mod.operation = 'UNION'
mod.solver = 'EXACT'
mod.object = ob_stem
bpy.context.view_layer.objects.active = ob_flange
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

mod = ob_flange.modifiers.new(name='Union_Barb', type='BOOLEAN')
mod.operation = 'UNION'
mod.solver = 'EXACT'
mod.object = ob_barb
bpy.context.view_layer.objects.active = ob_flange
bpy.ops.object.modifier_apply(modifier='Union_Barb')
bpy.data.objects.remove(ob_barb)

# Cut center slot: width 0.9 in Y, from X = -4.0 to X = 2.5
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.75, 0, 4.0), scale=(6.5, 0.9, 3.5))
ob_slot = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

mod = ob_flange.modifiers.new(name='Diff_Slot', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = ob_slot
bpy.context.view_layer.objects.active = ob_flange
bpy.ops.object.modifier_apply(modifier='Diff_Slot')
bpy.data.objects.remove(ob_slot)

bm = bmesh.new()
bm.from_mesh(ob_flange.data)
bounds = [[min(v.co[i] for v in bm.verts), max(v.co[i] for v in bm.verts)] for i in range(3)]
dims = [b[1] - b[0] for b in bounds]
print("Male Latch true bounds:", bounds)
print("Male Latch true dims:", dims)
print("Manifold:", sum(not e.is_manifold for e in bm.edges) == 0, "Vol:", bm.calc_volume())
bm.free()
