# V17: Borromean ribbon lamp

Three broad, translucent ribbon rings are woven over and under each other in the **Borromean rings** pattern: A passes over B, B over C, and C over A. No two rings are linked, yet the three cannot be pulled apart. Each ring is also a **Möbius band**: it rolls over in three evenly spaced half-twists on its free outer arc, so it has a single continuous face and a single continuous edge. Every curve comes from a few deliberate rules. Nothing is random.

Built 16 November 2026, after the user rejected V14–V16 for looking unlike the reference and for having no print plan. V14–V16 are kept unchanged.

[Blender model](Ribbon-Lamp-V17-Borromean.blend) · [Assembly map](Assembly-map.png) · [Print files](Print-files/) · [Print map](Print-map.json) · [Checks](Checks.json)

Renders: [Room view at the reference angle](01-Room-view.png) · [From below](02-From-below.png) · [Low side](03-Side.png) · [Oblique](04-Oblique.png) · [Twist detail](05-Twist-detail.png) · [Shape, LEDs off](06-Shape-unlit.png)

## The design rules

| Rule | What it does |
|---|---|
| **Plan: three ellipses** | Each ring's plan is an ellipse, so curvature changes smoothly between four vertices and never wiggles. Sizes step by a constant ratio of 1 : 0.9 : 0.81, and the centres sit at unequal angles (96°, 222°, 338°), so the outline is round (1,084 × 1,102 mm) without being regular. |
| **Weave: Borromean order** | At each of the six crossings the upper ribbon follows the cyclic order A > B > C > A. A solver sets the heights: each ring's height is a smooth periodic cubic spline (one control point per 85 mm), the smoothest that keeps at least 18 mm between woven layers, while staying inside a depth band 22–153 mm below the ceiling. |
| **Twist: Möbius rhythm** | Each ring lies flat through its crossings and turns over in three half-twists on its free outer arc. The twist rate is constant, with eased ends. The twist axis holds the middle of the depth band, so the twists roll without bobbing. |
| **Width: deliberate** | Width is constant at 128 mm through the twists, so the edges sweep as clean helices. It opens to 165–195 mm where the ribbon lies flat (the large faces) and slims to 105 mm at the heart of the lamp, under the ceiling disc. |
| **Edge** | A 1.8 mm skin finishes in a Ø3.2 mm rounded bead along both edges, for a crisp edge and a stiffer ribbon. |
| **Texture** | The grooves in the reference are the printed layer lines. The model is smooth; the renders show the layers with a shader. Most pieces print standing on their edge, so the layers run along the ribbon, as in the reference. |

## Checks (Checks.json)

| Measure | Value |
|---|---|
| Self-intersections / ribbon-to-ribbon intersections | 0 / 0 |
| Non-manifold edges (ribbon solids) | 0 |
| Smallest gap between separate ribbon surfaces | 16.6 mm |
| Tightest bend radius along any ribbon | 180 mm |
| Footprint / depth below ceiling | 1,084 × 1,102 mm / 153 mm (top 22 mm below the ceiling) |
| Skin mass, PETG | 1.97 kg (2.04 kg for the printed pieces with tabs, bosses and channels) |
| Centre of mass offset from the ceiling disc | 6 mm, 13 mm |
| LED sight-line test | 195,025 rays from 725 eye positions (0.6–1.6 m below the ceiling, out to 3.5 m away): no LED point visible |

## Light

- **Channels:** 2.42 m of 8 mm COB strip (3000 K, CRI 90+, 24 V) sits in 12 × 8 mm channels printed on the ceiling-facing skin, near the inner edge. The strip shines at the ceiling, and the warm wash glows back through the translucent ribbons.
- **Placement:** channels are placed only where that face really points up and no viewer can see into them. The sight-line test removed every stretch a room viewer could see.
- **Power:** at about 14 W/m that is roughly 34 W. The driver (24 V, about 60 W, dimmable) sits in the ceiling disc.

## Mount and structure

- **Ceiling disc:** Ø260 × 30 mm, the only ceiling fixing.
- **Seats:** each ring passes about 10 mm under the disc and is fixed there by one short standoff (35–58 mm) into an M3 insert boss on its hidden face.
- **Hidden spider:** six 12 × 5 mm aluminium flat bars run from the disc in the 6–11 mm gap under the ceiling, finished in ceiling white. Each carries a ring at a high, ceiling-facing spot through a Ø6 mm hanger, 28–62 mm long. Every ring therefore has three supports.
- **Spider visibility:** the bars are ceiling-coloured, but about 14% of the sampled room sight lines reach some part of an arm. Up close they are visible as thin lines against the ceiling.

## Print set (Print-files/)

- **Pieces:** 25 pieces (A01–A09, B01–B08, C01–C08), each 150–249 mm along the ribbon. All 25 fit the 320 mm working box inside the Kobra S1 Max volume.
- **Plates:** 8 plates, as 3MF files with geometry only. Open them in OrcaSlicer or Anycubic Slicer and apply your own Kobra S1 Max, PETG and 0.16 mm process settings.
- **Orientation:** 24 pieces print standing on their edge, so the layer lines run along the ribbon; C06 lies on its face. The steepest pieces have up to 16% of their surface as overhang. A02, A03, A04, A07, B01, B05, B06, C02, C06 and C07 need slim tree supports on the rear (ceiling-facing) side. Pieces stand up to 296 mm tall with a 1.8 mm wall, so use a brim and test the tallest piece first.
- **Joint:** every piece ends in a bonded lap tab, 16 × 1.2 mm with a 0.2 mm glue gap, on the ceiling-facing skin. The tab edges register between the edge beads of the next piece.
- **Seam placement:** seams were placed by an optimiser that scores how many room sight lines reach each candidate seam, and keeps every piece within the length limits.
- **Built into the pieces:** LED channel segments and M3 insert bosses (Ø12 mm, 7 mm high) for every seat and hanger.
- **Mesh check:** every STL is made of closed shells; every edge is shared by exactly two faces.
- **Not slicer-verified:** this Mac only has Snapmaker Orca, whose Anycubic profile is the smaller Kobra S1 (250 mm bed). Slice the plates in a slicer that has the Kobra S1 Max before printing.

## Assembly order

1. **Test print first:** B03 and B04 (a lap joint with an LED channel), and the tallest piece (A09), to check wall stability, the joint fit, glue, texture and glow.
2. **Build ring C** piece by piece on a flat jig, gluing each tab in number order. Close the loop last, with the Möbius flip between C08 and C01.
3. **Build rings B and A** the same way. Ring A must pass under C and over B while it is still open, so weave A's last piece through before closing it. Each ring can only be closed once the others are in place: that is the Borromean property.
4. **Fit the strips and wiring:** lay the LED strip in the channels, and run the wires along the hidden face to the nearest seat or hanger and up into the disc.
5. **Mount:** fit the disc and spider to the ceiling, hang the rings on their seats and hangers, then level them.

## Open items (not done or not verified)

- **Look:** this is closer to the reference from the side, with rolling half-twists and broad faces, but it is a different, more geometric composition. The inside glow is softer than the reference, and some twist ends read slightly pointed at close range.
- **Spider:** the arms can be seen from some angles (14% of sampled sight lines).
- **Structure:** sag and creep of the woven rings between supports, and the bond strength of the lap joints, are not calculated or tested. A bench test of a full ring is needed before overhead use.
- **Hardware not drawn:** the wire routes are not modelled, and the slim driver inside the 30 mm deep disc, the spider hub and the hanger fixings are not designed in detail.
- **Superseded trial:** `development-v17/Print/` holds a first 22-piece trial split; `Print-files/` supersedes it. Delete the old folder yourself if you want — I was not able to remove it.
- **Process capture:** no viewport recording was made, because the build ran in Blender background mode.

Sources: [build](../scripts/build_v17_borromean.py) · [geometry and solver](../scripts/v17_geometry.py) · [print split](../scripts/split_v17_print.py) · [assembly map](../scripts/map_v17_assembly.py) · [plan sketch](../scripts/v17_sketch.py)
