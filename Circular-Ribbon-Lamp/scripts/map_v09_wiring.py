"""Project the real LED and hollow branch positions onto a service-side plan."""
import json
import math
from pathlib import Path

out=Path(__file__).resolve().parents[1]/"full-lamp-v09"
report=json.loads((out/"Build-map.json").read_text())["lighting"]

def xy(point):
    return (525+point[0]*.89,317+point[1]*.89)

def points(values):
    return " ".join(f"{x:.1f},{y:.1f}" for x,y in map(xy,values))

markup=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 595" width="1000" height="595" role="img" aria-labelledby="title desc">
<title id="title">Ribbon lamp V09 wiring</title>
<desc id="desc">Three paired wires follow three metal branches from one centre connection to three LED strips.</desc>
<style>
text {font-family:system-ui,sans-serif;fill:#24251f;font-size:16px}
.heading {font-size:33px;font-weight:600}
.small {font-size:14px;fill:#4c4f46}
</style>
<rect width="1000" height="595" fill="#f6f4ee"/>
<text class="heading" x="48" y="56">Three LED stations · One centre connection</text>
<text class="small" x="48" y="87">Plan projection. The paired low-voltage feeds run inside the metal branches.</text>
<circle cx="525" cy="317" r="98" fill="#e8e3d6" stroke="#6c6c62" stroke-width="1.5" stroke-dasharray="6 5"/>
<circle cx="525" cy="317" r="81" fill="#fffdf8" stroke="#6c6c62" stroke-width="1.5"/>
''']
colors=["#487a86","#9d633b","#637b42"]
offsets=[(-118,58),(42,-27),(-186,69)]
for station,route,color,offset in zip(report["parallel_tape_runs"],report["copper_routes"],colors,offsets):
    position=station["position_mm"]
    theta=math.radians(station["heading_degrees"])
    radius=station["nominal_tape_mm"]/2
    delta=(radius*math.cos(theta),radius*math.sin(theta))
    edge1=tuple(p-d for p,d in zip(position,delta))
    edge2=tuple(p+d for p,d in zip(position,delta))
    path=[(0,-32),*route["points_mm"],position]
    markup.append(f'<polyline points="{points(path)}" fill="none" stroke="#ddd6c8" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>')
    markup.append(f'<polyline points="{points(path)}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    markup.append(f'<polyline points="{points([edge1,edge2])}" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"/>')
    x,y=xy(position)
    dx,dy=offset
    markup.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}">{station["id"]} · {station["nominal_tape_mm"]} mm</text>')
markup.append('''<circle cx="525" cy="288.5" r="7.5" fill="#343b33" stroke="#fffdf8" stroke-width="2"/>
<path d="M534 288.5H634L673 331H741" fill="none" stroke="#68695e" stroke-width="1.5"/>
<text x="751" y="337">24 V splitter</text>
<text class="small" x="751" y="362">Three parallel runs</text>
<text class="small" x="48" y="551">The dashed circle marks the central ceiling plate.</text>
</svg>''')
(out/"Wiring-map.svg").write_text("\n".join(markup))
