# Ribbon lamp V10

Three continuous ribbon shapes, with the small lower-right curl removed. The silhouette is approximately **1,194 × 934 mm**, with **160 mm maximum drop** from the ceiling. The upper-right sweep, left arch, and lower roll carry the form around a plain centre disc.

[Blender model](Ribbon-Lamp-V10-Integral.blend) · [Directly below](01-Below.png) · [Low side](02-Low-side.png) · [Opposite low side](03-Opposite-low-side.png) · [Joint section](Joint-detail.svg)

## Complete print set

The set contains **19 ribbon panels and one centre face**. The panel edges and contact lands are part of the same prints. Print A01–A10, B01–B04, C01–C05, and E01. Use milky PETG for the ribbons and opaque ivory PETG for E01. The panel skins are approximately 1.6 mm before the local joint geometry and forming. The arch is compressed in depth from V09, so its thickness varies with the roll.

| Group | Parts | Purpose |
| --- | ---: | --- |
| [A](Slicer-projects/A-Kobra-S1-Max.3mf) | 10 | Diagonal sweep and upper-right roll |
| [B](Slicer-projects/B-Kobra-S1-Max.3mf) | 4 | Upper-left arch |
| [C](Slicer-projects/C-Kobra-S1-Max.3mf) | 5 | Lower roll |
| [E](Slicer-projects/E-Kobra-S1-Max.3mf) | 1 | Removable centre face |

The [individual STLs](Print/) are in millimetres and already have trial bed orientations. The editable projects use the Kobra S1 Max 0.4 mm profile, Generic PETG, 0.16 mm layers and slim tree supports. Use your filament’s temperatures and review first-layer contact, supports and the thin walls on every plate. Keep support contact on the rear where practical. [Anycubic printer specifications](https://store.anycubic.com/products/kobra-s1-max)

OrcaSlicer generated toolpaths for all 20 parts across **11 plates**. Its trial estimate was about **2.1 kg of PETG with supports** and **119 hours**. Orca flagged the generic bed temperature, so use your actual filament and plate settings. The supplied 3MFs contain editable plate layouts and settings.

## Join the ribbons on the bench

1. **Start with B01 and B02.** The outgoing rear lip of B01 seats in the corresponding recess in B02. The overlap is **12 mm nominal**, with **0.26 mm nominal separation** between the mating levels. Check the fit, rib alignment and appearance in the actual filament before printing the rest. The lip is a bonded lap, with a broad mating surface for a compatible adhesive.
2. Assemble each ribbon in number order with the room-facing surfaces flush. Close A10 to A01, B04 to B01, and C05 to C01. Keep the last two joints loose during the full dry fit and bond the complete loop in a jig. Confirm the adhesive on a sample of the actual filament and keep squeeze-out off the lit surfaces.
3. A and B meet at the built-in rear land in the upper-left overlap. C and A meet at the second land in the lower-left overlap. The [build map](Build-map.json) and Blender assembly locate both lands. Each land is shaped into the rear of its own panel. Fit and bond the contact areas on the bench while the centre fastener positions are aligned.
4. The Ø210 mm metal canopy plate is the only ceiling attachment. Two concealed seats clamp the A/C stack and two hold B, all behind the centre face. The compact metal sleeve has ribbon pass-throughs. The mounting plate, collars, fasteners, sleeve and cover keeper are fabricated or purchased hardware. Their Blender dimensions are a fit layout. Confirm seating, thread engagement, load, backup retention and long-term sag with the assembled shade before hanging it.

## Centre-only light and wiring

Three **100 mm warm 24 V COB strips** sit in aluminum uplight channels in the same centre canopy. Their pairs join in parallel at one splitter, fed by one compatible driver. The reflector is the nearby ceiling. The compact sleeve screens the internal hardware and lets reflected light escape through the top. Use a tape width of up to 8 mm for the modeled beds and a cut pitch that divides 100 mm. Keep the driver and connections accessible behind the removable face.

With the light gathered at the centre, the render shows a halo and softer outer folds. The modeled seams remain visible. The actual filament, adhesive line and ceiling finish will affect how much they show.

## Validation

The [build map](Build-map.json) records the dimensions, printed part sizes, centre seats and contact locations. Digital checks found zero non-adjacent self-intersections, panel intersections or hardware-to-shade intersections. Three sampled views screened the LED channels and wires. A few low-side sightlines reached a fastener through a centre pass-through. [Camera and footprint check](View-check.json) · [Slicer results](Slicer-check.json)

Print the fit pair and test the complete shade on a bench before any overhead use. The files establish the assembled geometry. Bond strength, long-term creep and heat, fasteners and overhead retention still need physical verification. [PETG material guidance](https://prusament.com/materials/prusament-petg/)

[Blender viewport recording](../process/videos/16-v10-integral-ribbons.mp4) · [Editable build source](../scripts/build_v10_integral_ribbons.py)
