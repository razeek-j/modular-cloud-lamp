# Ribbon Lamp V09

The complete shade is modeled from the supplied view from below. It measures **1,194 × 934 mm** in plan and drops **298 mm** from the ceiling. The diagonal sweep, upper-right roll, upper-left opening, and lower roll are separate ribbon paths around the plain central disc. The original image is packed in Blender. The depth and rear construction were inferred from that view.

[Blender model](Ribbon-Lamp-V09-Full.blend) · [Lit underside](01-Directly-below-lit.png) · [Angled view](02-Oblique-lit.png) · [Unlit underside](03-Directly-below-unlit.png) · [Service-side view](04-Service-side.png) · [Numbered panel map](Panel-map.svg)

## Print the complete set

Open the editable **Kobra S1 Max** 3MF projects in OrcaSlicer, or import the [individual STLs](Print/) in millimetres. The 3MFs use the Kobra S1 Max 0.4 mm profile, 0.16 mm layers, Arachne walls, and automatic supports. Select your actual plate and filament. Check the preview for support contact, the first layer, and extrusion through the 1.3 mm skin. The initial plate layouts are already arranged for the printer’s 350 mm build volume. [Anycubic Kobra S1 Max manual](https://wiki.anycubic.com/M02010206-Kobra%20S1%20Max%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C-EN-260106.pdf)

| Project | What to print | Material |
| --- | --- | --- |
| [A](Slicer-projects/A-Kobra-S1-Max.3mf) | 10 diagonal sweep and upper-right roll panels | Milky, light-diffusing PETG |
| [B](Slicer-projects/B-Kobra-S1-Max.3mf) | 4 upper-left arch panels | Milky PETG |
| [C](Slicer-projects/C-Kobra-S1-Max.3mf) | 5 lower roll panels | Milky PETG |
| [D](Slicer-projects/D-Kobra-S1-Max.3mf) | 3 inner curl panels | Milky PETG |
| [Splices](Slicer-projects/Splices-Kobra-S1-Max.3mf) | 42 conformal strips, two per seam | Clear PETG |
| [Mounts](Slicer-projects/Mounts-Kobra-S1-Max.3mf) | 10 conformal rear mounting pads | Clear PETG |
| [Centre](Slicer-projects/Centre-Kobra-S1-Max.3mf) | 1 removable centre cover | Opaque ivory PETG |

OrcaSlicer estimated **12 plates**, about **4.0 kg of PETG including support**, and **197 hours** with these trial settings. Ribbon A uses tree supports to keep the largest panels practical. Orca flagged the generic bed-temperature setting, so use the plate temperature specified for your actual filament.

The smallest first assembly is **D01, D02, D-J01i and D-J01o**. Check that the edge and ripples meet, and that the two splices sit flush before running the remaining plates. Label the parts on their rear after removing supports. Keep every numbered piece with its own ribbon, since the two sides of each seam have distinct curves.

## Join and hang the ribbons

1. Lay the panels out in order using the [numbered panel map](Panel-map.svg). Ribbons **A, B and C are closed**. Their J01 joins the last panel to 01, J02 joins 01 to 02, and the numbering continues around the loop. Ribbon **D is open**. D-J01 joins D01 and D02, and D-J02 joins D02 and D03.
2. Dry-fit both curved splice strips on each rear seam. The i and o suffixes identify the two edges. Use the Blender assembly to match the side on the open D ribbon. The show surfaces butt together with a nominal **0.18 mm gap at the seam centre**. The rear strips have nominal space for a thin adhesive bond line. Hold each loop in a jig while bonding and confirm the adhesive with the actual filament on a sample.
3. Fit the -M pads on the listed panels. Their dots are shown on the map and their positions are given in the [build map](Build-map.json). The two blind recesses per pad are a preliminary M3 mounting interface. Fit the actual fastening method and confirm depth and retention on scrap first. The saddles connect the four ribbons to the three central metal branches. Use the Blender model or the branch coordinates in the build map for the fabricated layout.
4. Assemble the four ribbons to the metal carrier on a bench. The Ø220 mm metal plate at the centre is the only ceiling attachment. Fit the plain Ø182 mm cover over the central keeper and secure it through the three side slots. Keep the driver and connector accessible through the cover. Confirm the carrier, fastener retention, bonded parts, backup retention, and stability at operating temperature on the full bench assembly before any overhead installation.

## Three strips, one connection

[Wiring plan and station locations](Wiring-map.svg)

| Station | Strip length | Location |
| --- | ---: | --- |
| L1 | 100 mm | Recessed behind the upper-left overlap |
| L2 | 200 mm | Behind the large upper-right fold |
| L3 | 100 mm | Recessed behind the lower ribbon |

Choose warm **24 V constant-voltage COB tape**, around 2700 K, with a cut interval that divides 100 mm and a width that fits the 20 mm clear channel. The three runs total **400 mm**. Each sits in an aluminum heat channel with opaque sides and ends, facing the ceiling. The channel floor shields the direct view and the reflected light falls back onto the ribbons.

Run one low-voltage pair from each strip through its hollow metal branch. Join the three pairs **in parallel at one serviceable splitter inside the centre canopy**, fed by one compatible 24 V driver. Leave a short service loop at each channel end and protect cable exits through metal. The driver envelope in Blender reserves **65 × 33 × 26 mm**. Select the driver once the actual tape load and its manufacturer’s requirements are known.

## What the digital checks cover

- All 75 printable meshes are closed, and the assembly check found zero non-adjacent self-intersections and zero intersections between printed pieces. The metal branches and LED housings clear the modeled shade in the geometric check. [Build map and checks](Build-map.json)
- The three channels blocked **8,100 sampled direct emitter sightlines** at or below the source plane. A separate first-hit test sampled both room camera angles and found no direct hits on the LED channels or wires. A few samples hit the support branches through gaps. The renders include the assembled hardware and separate room fill. The lamp has faint hardware shadows and seam lines, and the real glow depends on the tape, ceiling finish, and filament. [Two-view screening results](View-check.json)
- OrcaSlicer generated trial toolpaths for each object. The supplied projects are editable plates that reslice using your local setup. [Slicer check](Slicer-check.json)
- The support sizing, bond strength, light output, temperatures and overhead retention need a physical check with the actual parts and hardware. The print files cover the plastic pieces. The metal carrier, electrical components, and fasteners are separate fabricated or purchased parts.

[Blender viewport recording](../process/videos/15-v09-full-lamp.mp4) · [Editable model generator](../scripts/build_v09_full_lamp.py)
