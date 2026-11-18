"""Flat Voronoi ceiling light, 900 mm disc, printed in 11 tiles (decagon hub + 10 sectors).
Run:  Blender -b --python scripts/build_voronoi_disc.py
Units: 1 Blender unit = 1 mm. Face (visible side) is z=0 = print bed side."""
import bpy, bmesh, math, os, sys
from mathutils import Vector, geometry

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R, HUB_R, N_SEC = 450.0, 145.0, 12
H, SKIN, WALL, BORDER = 25.0, 0.8, 1.6, 4.0   # depth, diffuser skin, cell wall, rim/seam wall (per side)
N_SITES, LLOYD = 520, 5

def clip(poly, a, b, c):  # keep a*x+b*y <= c
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a*p[0]+b*p[1]-c, a*q[0]+b*q[1]-c
        if fp <= 0: out.append(p)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp/(fp-fq); out.append((p[0]+t*(q[0]-p[0]), p[1]+t*(q[1]-p[1])))
    return out

def area_centroid(poly):
    A = cx = cy = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]; x1, y1 = poly[(i+1) % len(poly)]
        w = x0*y1-x1*y0; A += w; cx += (x0+x1)*w; cy += (y0+y1)*w
    A /= 2
    return A, ((cx/(6*A), cy/(6*A)) if abs(A) > 1e-9 else poly[0])

def disc_poly(r, n=360):
    return [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n)) for i in range(n)]

def bis(si, sj, inset=0.0):  # half-plane: closer to si than sj, shifted inward
    dx, dy = sj[0]-si[0], sj[1]-si[1]; d = math.hypot(dx, dy)
    return dx, dy, (sj[0]**2+sj[1]**2-si[0]**2-si[1]**2)/2 - inset*d/2*2/2*1.0 if False else \
           (sj[0]**2+sj[1]**2-si[0]**2-si[1]**2)/2 - inset*d

def neighbours(sites, i, k=18):
    p = sites[i]
    return sorted((j for j in range(len(sites)) if j != i),
                  key=lambda j: (sites[j][0]-p[0])**2+(sites[j][1]-p[1])**2)[:k]

def voronoi(sites, inset=0.0, bound=None):
    cells = []
    for i, s in enumerate(sites):
        poly = list(bound or disc_poly(R))
        for j in neighbours(sites, i):
            a, b, c = bis(s, sites[j], inset/2)
            poly = clip(poly, a, b, c)
            if len(poly) < 3: break
        cells.append(poly)
    return cells

# --- sites: phyllotaxis, denser toward the rim, Lloyd-relaxed ------------------
ga = math.pi*(3-math.sqrt(5))
sites = []
for i in range(N_SITES):
    u = (i+0.5)/N_SITES
    r = (R-18)*u**0.62
    sites.append((r*math.cos(i*ga), r*math.sin(i*ga)))
for _ in range(LLOYD):
    sites = [area_centroid(c)[1] for c in voronoi(sites)]
cells = voronoi(sites)
print("cells", len(cells))

# --- tiles = groups of whole cells (seams follow cell walls) ---------------------
def tile_of(i):
    x, y = area_centroid(cells[i])[1]
    if math.hypot(x, y) < HUB_R: return 0
    return 1 + int((math.atan2(y, x) % (2*math.pi)) / (2*math.pi/N_SEC))
tid = [tile_of(i) for i in range(len(sites))]
RIM = disc_poly(R-1.6, 180)

def pocket(i):
    pk = cells[i]
    for j in neighbours(sites, i):
        a, b, c = bis(sites[i], sites[j], 0.8 if tid[j] == tid[i] else 1.2)
        pk = clip(pk, a, b, c)
        if len(pk) < 3: return None
    for q in range(len(RIM)):
        a, b = RIM[q], RIM[(q+1) % len(RIM)]
        pass
    # rim clip: keep inside the R-1.6 circle (convex polygon)
    for a, b, c in inset_planes(RIM, 0.0):
        pk = clip(pk, a, b, c)
        if len(pk) < 3: return None
    return pk if abs(area_centroid(pk)[0]) > 30 else None

def inset_planes(poly, d):
    pl = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i+1) % len(poly)]
        dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy)
        nx, ny = dy/L, -dx/L
        pl.append((nx, ny, nx*p[0]+ny*p[1]-d))
    return pl

def key(p): return (round(p[0], 2), round(p[1], 2))

def build_tile(name, idxs):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); cache = {}
    def V(x, y, z):
        k = (round(x, 3), round(y, 3), round(z, 3))
        if k not in cache: cache[k] = bm.verts.new((x, y, z))
        return cache[k]
    def F(vs, mat=0):
        try: f = bm.faces.new(vs); f.material_index = mat
        except ValueError: pass
    def fan(pts, z, mat):
        vs = [V(x, y, z) for x, y in pts]
        for i in range(1, len(vs)-1): F([vs[0], vs[i], vs[i+1]], mat)
    def ring(cell, pk, z):
        if pk is None: fan(cell, z, 0); return
        loops = [[Vector((x, y, z)) for x, y in cell], [Vector((x, y, z)) for x, y in pk]]
        flat = [v for lp in loops for v in lp]
        for t in geometry.tessellate_polygon(loops): F([V(flat[i].x, flat[i].y, z) for i in t], 0)
    edges = set()
    for i in idxs:
        c = cells[i]
        for q in range(len(c)): edges.add((key(c[q]), key(c[(q+1) % len(c)])))
    npk = 0
    for i in idxs:
        c, pk = cells[i], pocket(i)
        ring(c, pk, 0.0); ring(c, pk, H)
        for q in range(len(c)):
            a, b = c[q], c[(q+1) % len(c)]
            if (key(b), key(a)) not in edges:  # tile boundary -> outer wall
                F([V(a[0], a[1], 0), V(b[0], b[1], 0), V(b[0], b[1], H), V(a[0], a[1], H)])
        if pk:
            npk += 1
            fan(pk, 0.0, 1)   # glowing diffuser (z=0 face of the pocket)
            fan(pk, SKIN, 0)
            for q in range(len(pk)):
                (x0, y0), (x1, y1) = pk[q], pk[(q+1) % len(pk)]
                F([V(x0, y0, SKIN), V(x1, y1, SKIN), V(x1, y1, H), V(x0, y0, H)])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bad = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob, npk, bad

bpy.ops.wm.read_factory_settings(use_empty=True)
glow = bpy.data.materials.new("Diffuser"); glow.use_nodes = True
nt = glow.node_tree; nt.nodes.clear()
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1, 0.86, 0.62, 1); em.inputs[1].default_value = 0.9
nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs[0])
wallm = bpy.data.materials.new("Rib"); wallm.diffuse_color = (0.25, 0.22, 0.2, 1)
os.makedirs(os.path.join(OUT, "print"), exist_ok=True)
for f in os.listdir(os.path.join(OUT, "print")): os.remove(os.path.join(OUT, "print", f))
tile_objs = []
for t in range(N_SEC+1):
    name = "T00-hub" if t == 0 else f"T{t:02d}-sector"
    ob, npk, bad = build_tile(name, [i for i in range(len(sites)) if tid[i] == t])
    ob.data.materials.append(wallm); ob.data.materials.append(glow)
    ang = 0.0 if t == 0 else -(t-0.5)*2*math.pi/N_SEC
    ob.rotation_euler = (0, 0, ang); bpy.context.view_layer.update()
    ws = [ob.matrix_world @ v.co for v in ob.data.vertices]
    xs = [v.x for v in ws]; ys = [v.y for v in ws]
    cx, cy = (max(xs)+min(xs))/2, (max(ys)+min(ys))/2
    print("TILE", name, "cells", npk, "bbox %.0f x %.0f" % (max(xs)-min(xs), max(ys)-min(ys)), "open_edges", bad)
    # STL (face down, centred, bed-aligned)
    ob.location = (-cx, -cy, 0); bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, "print", name + ".stl"), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
    ob.location = (0, 0, 0); ob.rotation_euler = (0, 0, 0)

cam = bpy.data.cameras.new("c"); cam.lens = 28; cam.clip_start = 10; cam.clip_end = 5000
co = bpy.data.objects.new("Cam", cam); bpy.context.collection.objects.link(co)
co.location = (0, 0, -1150); co.rotation_euler = (math.pi, 0, 0)
bpy.context.scene.camera = co
w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.025, 1)
bpy.context.scene.world = w
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.device = "CPU"
sc.render.resolution_x = sc.render.resolution_y = 1400
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)
sc.render.filepath = os.path.join(OUT, "renders", "01-from-below.png")
sc.view_settings.view_transform = "Standard"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Voronoi-Disc-v01.blend"))
