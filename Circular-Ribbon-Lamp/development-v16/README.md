# V16: layered broad ribbon, three layers deep

Built 16 November 2026 after the user reviewed V15 and asked for more ribbon layers. V15 is kept as a separate checkpoint.

[Blender model](Ribbon-Lamp-V16-Layered-Ribbon.blend) · [Build script](../scripts/build_v16_layered_ribbon.py) · [Geometry](../scripts/v16_layered_geometry.py) · [Checks](Checks.json)

Renders: [Room view](01-Room-view.png) · [From below](02-From-below.png) · [Oblique](03-Oblique-below.png) · [Close fold](04-Close-fold.png) · [Shape unlit](05-Shape-unlit.png)

## Shape

- **Band.** One continuous band, 142–205 mm wide and 6.79 m long, follows a (3,4) knot path. It circles the centre three times, so three strands of the band are layered at every plan direction. There are four outer loops, four inner loops and eight crossings.
- **Why it clears itself.** On this path, when two strands cross (one high, one low), the third is far away radially. The band lies near flat at the crossings. Bank and twist act only where strands are apart in plan.
- **Irregular outline.** Loop size, spacing, width, bank (up to 50°) and twist differ from loop to loop. Footprint is about 1,205 × 1,165 mm.
- **Mount.** A Ø200 × 32 mm ceiling disc is the only ceiling fixing. Four clear posts, 47–52 mm long, drop to the hidden top face of the inner loops.

## Hidden lighting

- The LED channel (12 × 8 mm) runs on the hidden top face along the inner edge and shines at the ceiling.
- Sight-line test: 555,350 rays from 725 eye positions, 0.6–1.6 m below the ceiling and out to 3.5 m away. Visible stretches were left without LEDs. No tested LED station is visible.
- 4,320 mm of strip remains.

## Checks

| Measure | Value |
|---|---|
| Self-intersections | 0 |
| Non-manifold edges | 0 |
| Minimum clearance between separate parts | 25.6 mm |
| Depth below ceiling | 182 mm at the lowest point |
| Gap between band and ceiling disc | 5.4 mm |
| Channel top below ceiling | 11.4 mm |
| Skin | 1.172 m², about 2.68 kg in PETG at 1.8 mm |

## Open items (not done)

- The user has not yet reviewed this shape. From directly below it reads as a four-armed pinwheel, more ordered than the reference.
- The band slopes up to 44° along its length near the inner loops.
- The four post seats show faintly as small dots from directly below.
- Post seats, wire routes, real LED hardware, sag and print segmentation are not designed. It is not print-ready.
- No viewport recording was made because the build ran in Blender background mode.
