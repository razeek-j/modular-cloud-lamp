# V20: spiral rosette

Built 17 November 2026 after V18 (messy) and V19 (rope-like wreath) were rejected. The user sent a flat spiral picture and asked for the lamp's folds to look like it from below, at the size from their earlier file. V14–V19 are kept unchanged.

[Blender model](Ribbon-Lamp-V20-Rosette.blend) · [Palette variant](Ribbon-Lamp-V20-Rosette-palette.blend) · [Assembly map](Assembly-map.png) · [Print files](Print-files/) · [Print map](Print-map.json) · [Print list](Print-list.md) · [Checks](Checks-geometry.json)

Renders: [From below next to your picture](Compare-from-below.png) · [Next to the ribbon photo](Compare-reference.png) · [From below](01-From-below.png) · [Photo's camera](00-Reference-camera.png) · [Room](02-Room-view.png) · [Side](03-Side.png) · [Oblique](04-Oblique.png) · palette variants have `-palette` in the name.

## How the request was read

The message was loose, so this is the reading used. Say if any part is wrong.

- **Picture:** five tapered blades start at a dark vortex round a small dot, sweep clockwise (seen from below) and widen into rounded crescents. A second, larger family of broad petals sits outside them, and a few ovals sit at the rim. Each blade overlaps its inner neighbour like the leaves of an iris. Copy: [references/v20-spiral-rosette-picture.png](../references/v20-spiral-rosette-picture.png).
- **"The lamp should look like this":** the ribbon lamp stays (translucent, glowing, centre-only fixing, printed in sections), but seen from below it should read as that spiral.
- **Size:** taken from the project's brief and your collage: **Ø1,200 mm, about 140 mm deep**, Kobra S1 Max (350 mm bed, 320 mm working box). You did not restate it in this message.

## The design

Three whorls of five, rotated so each sits between the one inside it. Everything comes from a few exact rules; there are no random terms.

| Whorl | What | Plan path (log spiral) | Width | Skin depth below ceiling |
|---|---|---|---|---|
| **B** inner blades (5) | Narrow tail under the hub, hugging the vortex for about 100°, then a flare to a broad rounded end | Centreline from R 70 to R 377 mm (outline to 414), turns 238° | 26 mm at the root, 225 mm at the belly | 31–87 mm |
| **M** outer blades (5) | The same crescent at a larger scale, tails tucked under B's bellies | Centreline R 318 to R 511 mm (outline 267–553), turns 96° | up to 250 mm | 76–119 mm |
| **O** rim ovals (5) | Radiate out from under the M lobes, lipped at the edge | Outline R 424–597 mm, turns 16° | 150 mm | 96–130 mm |

- **Handedness:** the pitch angle of each spiral eases through a knot program (from nearly tangent at the vortex to a flare). The blades sweep clockwise outward as seen from below, like the picture. Set `sigma` in `scripts/v20_geometry.py` to mirror it.
- **Overlap (iris rule):** each blade's free edge sits lower than the covered edge of its inner neighbour (a cross tilt of 0.16 for B, 0.13 for M), so the overlaps read as clean spiral edges. The cross-section is a convex cup of constant R 420 mm.
- **Lips:** every petal ends in a rolled lip (58° for B, 60° for M, 56° for O) rising toward the ceiling, with an average bend radius of 76–82 mm and a tightest radius of about 40–45 mm. They are meant to catch the inner light like the photo's glowing edges; the renders show that only weakly.
- **Depth order:** inner whorl nearest the ceiling, outer whorl lowest, so the lamp is a shallow funnel with the vortex at the centre. The skin spans 31–136 mm below the ceiling.
- **Hub:** Ø160 metal ceiling plate (supplied), printed hub body Ø192 × 23 mm (the only ceiling fixing), a smoked Ø188 cap that hides the blade roots and ten screws, and a frosted Ø48 dot lens over a small warm LED. The dark disc and dot are the picture's vortex.
- **Skin:** 1.4 mm PETG. No modelled ribs or noise. The soft layer lines in the renders are only a shader.

## Against your picture and the ribbon photo

| | Matches | Differs |
|---|---|---|
| **Your picture** (from below) | Clockwise swirl out of a dark vortex with a dot; tapered inner blades that widen; a larger outer family; detached ovals at the rim; different sizes. | Five-fold regular, where the picture is hand-drawn and uneven. Fewer overlaps (on average 1 layer, and 30% of the disc is open to the glowing ceiling; the picture shows 2–3). Warm white, not the picture's colours (a palette variant is rendered). No sprigs. |
| **Ribbon photo** (low side view) | Broad translucent sheets, rolled glowing lips, shallow depth, glowing halo on the ceiling. | **Reads as a rose or rosette from the side, not as long rolling ribbons.** There are no half-twists or hairpin loops, and the outline is a round lens. Choosing the picture's pattern over the photo's rhythm was the trade made here. |

## Checks (`scripts/check_v20.py`)

| Measure | Value |
|---|---|
| Intersections between petals | 0 |
| Smallest gap between sheets | 9.9 mm (M–M); B–B 12 mm, M–O 11.5 mm, B–M 17 mm |
| Outline / depth | Ø1,194 mm / 136 mm (limits 1,200 / 140) |
| Skin area and mass | 1.12 m², 1.99 kg at 1.4 mm (1.7 kg at 1.2 mm) |
| LED sight lines | 0 of 27,195 reach a strip (111 eye positions, 245 strip points). With the petals removed, 20,847 do, so the test is not empty. |
| Stud sight lines | the 40 studs were ranked by how little of each the room can see: 0 of 111 eye positions reach any stud (eyes 0.9–1.7 m below the ceiling, at least 17° elevation). Seen from the side at lamp level (`03-Side.png`) they show as short posts. |
| Closed solids | all 43 printed parts have 0 open edges, and re-import in Blender with 0 non-manifold edges and positive volume; the 25 half-lap seams do not overlap |

## Light, mount and structure

- **LEDs:** an 8 mm warm COB strip (3000 K, CRI 90+) in five 12 × 8 mm channels, one on each B blade's hidden face along its covered edge (246 mm each, 1.23 m), plus a 0.47 m ring round the hub drum, plus a 1 W dot puck. About 1.7 m of strip, roughly 15–20 W at 24 V. This is less strip than V18 (2.7 m), so the first test may show the outer whorl dim; M and O are lit through B and by ceiling bounce.
- **Where the strips sit:** the channels open toward the ceiling, so light bounces off it onto the petals' backs. Each channel is behind the neighbouring blade's free edge. Nothing is visible from the room in the sight-line test.
- **Load path:** hub body → ten M3 screws through the B root tabs (two per blade) → 10 B–B overlap studs → 10 studs hanging M from B → 10 M–M studs → 10 studs hanging O from M. 40 bonding studs in all (Ø9 mm, 14–26 mm tall, conformal flat tops 0.3 mm under the petal above). Every petal is tied to the hub through at least two studs. The skin's centre of mass is on the hub axis by five-fold symmetry. Mass hung from the ceiling is roughly 2.7–3 kg including the metal plate, LEDs and driver.
- **Not verified:** sag between studs, bond strength, creep, ceiling anchors. Choose fixings for at least five times the hung weight and test a pair before overhead use. The renders show the studs as faint dark specks on the petals. That is partly a shader limit (it cannot model light travelling along a solid stud, which would act as a light pipe), so the real look is unknown until a sample is lit.
- **Not drawn:** wiring along the blades, driver, connectors.

## Print set (`Print-files/`)

- **40 petal pieces:** B1–B5 in four pieces each (132–212 mm long), M1–M5 in three each (132–284 mm), O1–O5 in one each (200 mm). Plus **3 hub parts:** H1 hub body, H2 smoked cap, H3 dot lens. 24 plates (`Plate-01.3mf` to `Plate-24.3mf`). About **2.6 kg** of PETG as solid volume (the hub parts print with infill, so less).
- **Seams:** an 18 mm half-lap. Each side keeps half the 1.4 mm skin over the lap, so the skin stays 1.4 mm through the joint and shows no dark band. 0.15 mm glue gap, short sloped ramps instead of steps. Seam rows were chosen where the fewest room sight lines reach them. The neighbouring pieces were checked not to overlap.
- **Bosses and holes:** two Ø3.4 clearance holes in each blade's root tab (cut in the model). The hub body has ten Ø4.2 × 5.5 insert pockets from below, and the cap has ten Ø3.4 holes to countersink. The three M4 holes to the ceiling plate are drilled on site.
- **Orientation:** the search tried 38 tilts per piece. 30 pieces lean 60° from flat, 5 lean 45°, and the 5 ovals tip 45° along their length. No piece has overhang on its visible face; the largest overhang on a hidden face is 29% (M-3 pieces and ovals). The tallest piece stands 219 mm. They print on a small contact patch, so use a brim of 8–10 mm and slow outer walls.
- **Settings to start from:** 0.4 mm nozzle, 0.2 mm layers (test 0.16), 3 perimeters, no infill, thin-wall detection on (the lap halves are 0.63 mm), tree supports on the hidden face only, seam on the hidden edge. Milky natural PETG. Print time is an estimate of 110–170 h (15–23 g/h), not sliced.
- **Colour option:** each petal is its own print, so the picture's palette can be done with translucent ivory, terracotta, sage and sand PETG (render: `*-palette.png`). Tinted filaments will look different from the render; sample first.
- **Not slicer-verified.** The installed Snapmaker Orca has no Kobra S1 Max profile; open the 3MF plates in OrcaSlicer or Anycubic Slicer with your PETG profile.

## Assembly (on the bench, ceiling side down)

1. Print and test one seam pair and one stud pair first (M1-2 + M1-3, and O1-1 against the M5 piece above it).
2. Bond the half-laps with a PETG-safe solvent cement or CA gel to complete each blade.
3. Press ten M3 inserts into the hub body. Lay the five B blades with their tabs under the flange, add the cap, and fix with ten countersunk M3 screws from below.
4. Bond the B–B studs, then the M petals (studs point down onto B when built this way up), then the O ovals onto M.
5. Press the strips into the channels and the ring on the drum; run each pair along the blade's hidden face to the hub (clips not modelled).
6. Fix the ceiling plate, hang the shade, wire the driver in the hub.

## Open items

- **Look:** needs your side-by-side verdict. The honest gap is the side view: rosette, not rolling ribbons. More overlap, an uneven layout or longer ribbons are the next levers.
- **Seams and studs:** the half-lap and the studs are untested prints. Studs may show as spots.
- **Light:** the outer whorl may need strips on the M backs.
- **Structure and installation:** unverified, see above.
- **Process capture:** no viewport recording was made (background build).

Sources: [geometry](../scripts/v20_geometry.py) · [print parts](../scripts/v20_parts.py) · [Blender build](../scripts/build_v20_rosette.py) · [print split](../scripts/split_v20_print.py) · [checks](../scripts/check_v20.py) · [assembly map](../scripts/map_v20_assembly.py) · [comparisons](../scripts/compare_v20.py) · [plan-view preview](../scripts/v20_preview.py)
