# V18: three looped ribbons woven round a slim disc

Built 16–17 November 2026 to the measured reference targets in [Reference-comparison.md](../development-v17/Reference-comparison.md), after the user asked to build to them. V17 and earlier are kept unchanged.

[Blender model](Ribbon-Lamp-V18-Braided.blend) · [Assembly map](Assembly-map.png) · [Print files](Print-files/) · [Print map](Print-map.json) · [Checks](Checks.json)

Renders: [From the reference photo's camera position](00-Reference-camera.png) · [Room view](01-Room-view.png) · [From below](02-From-below.png) · [Low side](03-Side.png) · [Oblique](04-Oblique.png) · [Detail](05-Twist-detail.png) · [Shape, LEDs off](06-Shape-unlit.png)

## How it is built

- **Layout:** like the reference's band, there is an upper hero ribbon (A), a middle ribbon (B) and a front ribbon (C). They are fanned to 0°, +52° and −52° so the outline is round (1,230 × 1,105 mm). The layout was chosen by search so that every crossing is at least 37°, crossings are at least 138 mm apart, and no three crossings form a tight triangle.
- **Curve program:** each ribbon is a closed loop with exact curve elements, mirrored through its centre:
  - outward-bowing sweeps of 760–900 mm radius
  - eased transitions of 80–95 mm
  - short inward necks of 175–190 mm radius
  - hairpin end loops of 92–100 mm radius that overturn past 180°
- **Weave:** all 1,024 patterns for the 10 crossings were checked. The chosen one keeps a "lens" (two ribbons crossing twice in quick succession) on the same side, and otherwise alternates over and under like a plait.
- **Stance:** at a crossing the ribbon necks to 84 mm and leans 45° from upright. It holds that lean over the whole overlap, which is longer for shallow crossings. In between, it rolls to a 25° lean on alternating sides. On long free stretches it twists through flat.
- **Width:** each span swells to 139 mm (A), 122 mm (B) or 108 mm (C) at mid-span and necks to 84 mm at the crossings. The width change is smoothed over about 150 mm and tapers 25% into the end loops.
- **Height:** a constrained smooth-spline solver (one control point per 70 mm) follows the designed over/under heights and keeps the woven layers apart inside a 21–188 mm depth band.
- **Section:** a 1.8 mm skin with Ø3.2 mm rounded edge beads. The ribbed texture is the printed layer lines (shown with a shader in the renders).

## Against the measured targets

| Target (from the reference) | V18 |
|---|---|
| End loops R 90–100, turning 195–230° | R 92–100. The loops overturn more than 180°; the exact turn depends on the necks. |
| Sweeps R ≥ 500 | 760–900 mm bowing sweeps (about half of each ribbon's length) |
| Waves R 150–210 | Necks at 175–190 mm (about 22% of length) |
| Rolled lips R 45–55 | **Not built** (0%). The tightest 3D bend is 44–47 mm, from twisting, not a true lip. |
| Twist node every 300–370 mm | Median spans 225–306 mm (range 141–483) |
| Width 95–165, swell mid-span and neck at nodes | 84–139 mm, swelling and necking; widest on the upper ribbon |
| Flat only at crossings, about 10% | 7% flat (at free twist points); crossings lean instead |
| Upright about 70% | 35% upright (over 55°), 58% leaning. More lean matched the photo better in the side-by-side comparison, so I chose it. |
| Four layers through the middle | Three ribbons, up to four passes where loops overlap |
| Depth about 140–165 | 188 mm |
| Round, not a long band | 1,230 × 1,105 mm |

## Checks (Checks.json)

| Measure | Value |
|---|---|
| Self or ribbon-to-ribbon intersections | 0 / 0 |
| Non-manifold edges | 0 |
| Smallest gap between separate ribbon surfaces | 9.5 mm (the solver's worst leftover constraint is 7.5 mm short of its 20 mm target) |
| Top below ceiling / depth | 21 mm / 188 mm |
| Ribbon skin | 1.59 kg PETG; centre of mass 10 mm from the disc axis |
| LED sight-line test | 218,950 rays from 725 room eye positions; no LED point visible |
| LED strip | 2.72 m |

## Light, mount and structure

- **LEDs:** 8 mm COB strip (3000 K, CRI 90+) in 12 × 8 mm channels on the ribbons' top edges, near the ceiling. The channels open upward and lean 25° toward the centre, so the strip washes the ceiling and the neighbouring ribbon faces.
- **Ceiling disc:** Ø300 × 32 mm, the only ceiling fixing. Each ribbon passes under it and is fixed by one hidden standoff (7, 9 and 65 mm long) into an M3 insert boss on its top edge.
- **Crossing pads:** at the 10 crossings, a translucent PETG pad (Ø12 mm, 24–58 mm long) bonds the upper ribbon to the lower one, so the woven ribbons brace each other. There are no metal arms. The longer pads can be seen from the side as short columns between ribbons.

## Print set (Print-files/)

- **Pieces:** 32 ribbon pieces (A01–A11, B01–B11, C01–C10), each 162–249 mm long, plus 10 crossing pads (P01–P10). 42 parts on 10 plates, about 1.8 kg of PETG.
- **Fit:** every part fits the 320 mm working box. Every STL is a closed solid (every edge shared by exactly two faces).
- **Orientation:** all ribbon pieces print standing on their edge, so the layer lines run along the ribbon.
- **Supports:** the largest overhang is 15% of a piece's surface. A01, A03–A07, A11, B02, C05, C06 and C10 need slim tree supports on their upper face.
- **Built into the pieces:** a bonded 16 mm lap tab on the upper face of every seam, LED channel segments on the top edges, and the three M3 seat bosses.
- **Not slicer-verified:** the 3MF plates hold geometry only. The installed Snapmaker Orca has no Kobra S1 Max profile, so open them in OrcaSlicer or Anycubic Slicer with your PETG profile.

## Open items

- **Look:** closest so far to the reference from its own camera, with broad leaning faces, layers, hairpin loops and rising and falling edges. Still different: no rolled lips; edges still show some small rises and falls; the inner glow is softer than the photo; and from below it reads as three looped ribbons, more open than the reference.
- **Structure:** sag between three seats and ten pads, bond strength and creep are not calculated or tested.
- **Hardware not drawn:** wire routes, the driver in the 32 mm disc, and the seat hardware detail.
- **Test print first:** a seam pair (A04 + A05) and one pad, to check fit, glue, texture and glow.
- **Process capture:** no viewport recording was made (background build).

Sources: [build](../scripts/build_v18_braided.py) · [geometry and solver](../scripts/v18_geometry.py) · [print split](../scripts/split_v18_print.py) · [assembly map](../scripts/map_v18_assembly.py)
