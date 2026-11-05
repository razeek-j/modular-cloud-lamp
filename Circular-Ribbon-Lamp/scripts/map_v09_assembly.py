"""Draw a numbered assembly map from the four actual full-lamp ribbon meshes."""
from html import escape
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

directory = Path(bpy.data.filepath).parent
data = json.loads((directory/"Build-map.json").read_text())
colors = {"A":("#f4c797","#e9a76a"),"B":("#c8dbc5","#a9c6a7"),
          "C":("#c9d8ef","#a9bfdf"),"D":("#ead0df","#d3acc3")}
columns = {"A":157,"B":91,"C":127,"D":85}
span = {"A":264,"B":180,"C":180,"D":192}
cells = [("#0b2e36",53,137),("#173329",680,137),
         ("#15305b",53,540),("#512844",680,540)]
elements = []

def label(x,y,value,cls):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}">{escape(value)}</text>'

for (key,band),(ink,tx,ty) in zip(data["bands"].items(),cells):
    panels = []
    cols = columns[key]
    for item in band["panels"]:
        name = item["file"][:-4]
        obj = next(o for o in bpy.context.scene.objects if o.name.startswith(name+" · "))
        mesh = obj.data
        rows = len(mesh.vertices)//(2*cols)
        assert rows*cols*2 == len(mesh.vertices)
        bounds = [*range(cols), *range(2*cols-1,rows*cols,cols),
                  *range(rows*cols-2,(rows-1)*cols-1,-1), *range((rows-2)*cols,0,-cols)]
        boundary = [mesh.vertices[i].co for i in bounds]
        mesh.calc_loop_triangles()
        tree = BVHTree.FromPolygons([v.co for v in mesh.vertices],
                                    [tuple(tri.vertices) for tri in mesh.loop_triangles],all_triangles=True)
        panels.append((name,boundary,rows,mesh,tree))
    pts = [p for _,boundary,*_ in panels for p in boundary]
    xmin,xmax = min(p.x for p in pts),max(p.x for p in pts)
    ymin,ymax = min(p.y for p in pts),max(p.y for p in pts)
    scale = min(530/(xmax-xmin),277/(ymax-ymin))
    margin_x = (550-(xmax-xmin)*scale)/2
    margin_y = (294-(ymax-ymin)*scale)/2
    def project(p):
        return tx+margin_x+(p.x-xmin)*scale,ty+61+margin_y+(p.y-ymin)*scale
    elements.append(f'<rect x="{tx-14}" y="{ty-22}" width="586" height="377" rx="10" fill="#fff" stroke="#d7d6d1"/>')
    elements.append(label(tx+12,ty+10,f"{key}  {band['name']}","section"))
    elements.append(label(tx+12,ty+34,f"{len(panels)} panels  /  {'closed loop' if band['closed'] else 'open return'}","sub"))
    for name,boundary,_,_,_ in sorted(panels,key=lambda item:-sum(v.z for v in item[1])/len(item[1])):
        points = " ".join(f"{x:.2f},{y:.2f}" for x,y in map(project,boundary))
        elements.append(f'<polygon points="{points}" fill="{colors[key][int(name[-2:])%2]}" stroke="{ink}" stroke-width="1.2"/>')

    placed = []
    for name,_,rows,mesh,tree in panels:
        candidates = []
        for r in range(1,rows-1,max(1,rows//12)):
            for c in range(7,cols-7,max(1,cols//17)):
                p = mesh.vertices[r*cols+c].co
                hit = max((tree2.ray_cast(Vector((p.x,p.y,-.6)),Vector((0,0,1)),.6)[2] is not None
                           and tree2.ray_cast(Vector((p.x,p.y,-.6)),Vector((0,0,1)),.6)[0].z < p.z-.003
                           for _,_,_,_,tree2 in panels),default=False)
                x,y = project(p)
                distance = min((((x-a)**2+(y-b)**2)**.5 for a,b in placed),default=200)
                cost = (140 if hit else 0) + 7*abs(r/rows-.5) + 11*abs(c/cols-.5) + max(0,50-distance)
                candidates.append((cost,x,y))
        _,x,y = min(candidates)
        placed.append((x,y))
        elements.append(f'<rect x="{x-20:.1f}" y="{y-11:.1f}" width="40" height="22" rx="4" fill="#fff" stroke="{ink}"/>')
        elements.append(label(x,y+5,name,"id"))
    for anchor in data["attachments"]:
        if anchor["id"][0]!=key:
            continue
        p = Vector(anchor["location_mm"])/1000
        x,y=project(p)
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{ink}" stroke="#fff" stroke-width="1.5"><title>{anchor["id"]} on {anchor["panel"]}</title></circle>')

svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1290" height="950" viewBox="0 0 1290 950" role="img" aria-labelledby="title desc">
<title id="title">Ribbon lamp V09 assembly map</title><desc id="desc">Four isolated ribbons viewed from below, with each panel numbered and the carrier pad locations marked by dots.</desc>
<style>
text {font-family: system-ui, sans-serif; fill:#222823}
.heading {font-size:32px;font-weight:600}
.section {font-size:22px;font-weight:600}
.sub {font-size:15px;fill:#505750}
.id {font-size:14px;font-weight:600;text-anchor:middle}
</style>
<rect width="1290" height="950" fill="#f3f2ee"/>
<text x="40" y="52" class="heading">Ribbon lamp · Panel map</text>
<text x="40" y="84" class="sub">Each ribbon is shown separately from below. Dots mark the rear carrier pads.</text>
""" + "\n".join(elements) + "</svg>"
(directory/"Panel-map.svg").write_text(svg)
