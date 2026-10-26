"""3D ház kiégetése: nappal/éjjel JPG + vetített folyam-SVG-k + buborék horgonyok."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run2 import render

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/deye_offgrid/www/deye"
SS = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
DIST = 98
os.makedirs(OUT, exist_ok=True)


def catenary(a, b, sag, n=16):
    return [[a[i] + (b[i] - a[i]) * t / n for i in range(2)] + [a[2] + (b[2] - a[2]) * t / n - sag * 4 * (t / n) * (1 - t / n)] for t in range(n + 1)]


# 3D folyam-útvonalak (x, y, z méterben) – a 3D modell geometriájához igazítva
FLOWS = {
    "pv": ("#F5A623", [
        [[8.0,-1.59,4.94],[17.2,-1.59,4.94],[17.4,0.5,2.85],[21.0,-0.4,3.2],[24.9,-1.2,3.2],[25.7,-7.6,3.0],[25.7,-8.0,2.5]],
        [[41.97,-0.4,4.26],[40.4,-0.4,3.3],[40.35,-2.1,3.0],[33.2,-2.1,3.0],[32.9,-4.6,3.15],[27.4,-7.6,3.0],[27.0,-8.0,2.5]],
        [[45.4,-0.4,4.8],[44.2,-0.4,3.15],[40.45,-0.4,3.1]],
    ]),
    "akku_tolt": ("#22C55E", [[[26.1,-8.0,1.2],[26.1,-7.3,0.15],[28.4,-7.3,0.15],[28.6,-7.55,0.6]]]),
    "akku_merit": ("#22C55E", [[[28.6,-7.55,0.6],[28.4,-7.3,0.15],[26.1,-7.3,0.15],[26.1,-8.0,1.2]]]),
    "halozat": ("#E5484D", [catenary([-8.6,-9.2,7.2],[-0.1,-6.2,5.5],0.8) + [[-0.1,0.3,2.6],[17.4,0.3,2.6],[24.7,-1.25,2.75],[25.3,-7.6,2.7],[25.6,-8.0,2.45]]]),
    "terheles": ("#3B82F6", [[[24.9,-1.25,2.3],[21.5,-0.6,2.3],[17.6,0.1,2.3],[12.3,2.8,2.5],[0.9,2.8,2.5]]]),
}
ANCHORS = {
    "pv": [9.0,-4.8,10.5], "haz_teto": [13.0,-0.3,5.4], "garazs_dk": [46.0,2.8,6.2], "garazs_dny": [40.5,-4.5,5.2],
    "halozat": [-8.6,-9.5,8.8], "inverter": [26.0,-8.3,4.4], "akku": [29.2,-7.9,3.2], "terheles": [6.0,2.8,3.4],
}

keys = list(FLOWS)
polys = [pl for k in keys for pl in FLOWS[k][1]]
anchor_keys = list(ANCHORS)
pts = render("day", os.path.join(OUT, "haz_nappal.jpg"), SS, DIST, polys + [[ANCHORS[k]] for k in anchor_keys])
render("night", os.path.join(OUT, "haz_ejjel.jpg"), SS, DIST)

proj_polys, proj_anch = pts[:len(polys)], pts[len(polys):]
i = 0
for k in keys:
    col, pls = FLOWS[k]
    body = []
    for _ in pls:
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in proj_polys[i]); i += 1
        body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="11" stroke-opacity="0.22" stroke-linecap="round" stroke-linejoin="round"/>')
        body.append(f'<path class="f" d="{d}" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100">'
           '<style>.f{stroke-dasharray:3 19;animation:m 0.9s linear infinite}@keyframes m{to{stroke-dashoffset:-22}}</style>'
           + "".join(body) + "</svg>")
    with open(os.path.join(OUT, f"folyam_{k}.svg"), "w") as f:
        f.write(svg)
anch = {k: [round(p[0][1] / 1100 * 100, 1), round(p[0][0] / 1600 * 100, 1)] for k, p in zip(anchor_keys, proj_anch)}   # (top%, left%)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "anchors_v2.json"), "w") as f:
    json.dump(anch, f)
print(json.dumps(anch))
