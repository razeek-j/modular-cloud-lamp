import bpy, bmesh

bpy.ops.wm.read_factory_settings(use_empty=True)

# Create flange
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.95, 0, 4.0), scale=(1.2, 8.0, 8.0))
ob_flange = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Create sleeve
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.675, 0, 4.0), scale=(5.35, 4.6, 4.6))
ob_sleeve = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Union
mod = ob_flange.modifiers.new(name='Union', type='BOOLEAN')
mod.operation = 'UNION'
mod.solver = 'EXACT'
mod.object = ob_sleeve
bpy.context.view_layer.objects.active = ob_flange
bpy.ops.object.modifier_apply(modifier='Union')
bpy.data.objects.remove(ob_sleeve)

# Bore
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.5, 0, 4.0), scale=(6.0, 3.0, 3.0))
ob_bore = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

mod = ob_flange.modifiers.new(name='Bore', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = ob_bore
bpy.context.view_layer.objects.active = ob_flange
bpy.ops.object.modifier_apply(modifier='Bore')
bpy.data.objects.remove(ob_bore)

# Windows
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.65, 0, 4.0), scale=(1.7, 6.0, 2.2))
ob_win = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

mod = ob_flange.modifiers.new(name='Win', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = ob_win
bpy.context.view_layer.objects.active = ob_flange
bpy.ops.object.modifier_apply(modifier='Win')
bpy.data.objects.remove(ob_win)

bm = bmesh.new()
bm.from_mesh(ob_flange.data)
bounds = [[min(v.co[i] for v in bm.verts), max(v.co[i] for v in bm.verts)] for i in range(3)]
dims = [b[1] - b[0] for b in bounds]
print("Female Socket true bounds:", bounds)
print("Female Socket true dims:", dims)
print("Manifold:", sum(not e.is_manifold for e in bm.edges) == 0, "Vol:", bm.calc_volume())
bm.free()
