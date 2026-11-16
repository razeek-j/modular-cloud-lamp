# V15: broad rolling ribbon, round but irregular

Built 16 November 2026 after the user reviewed V14 and said they expected the look of the main reference (`references/design-reference.jpg`): broad flowing ribbons, a low profile and a small ceiling disc, in a rounder, unusual outline. V14 is kept as a separate checkpoint.

[Blender model](Ribbon-Lamp-V15-Broad-Ribbon.blend) · [Build script](../scripts/build_v15_broad_ribbon.py) · [Geometry](../scripts/v15_broad_geometry.py) · [Checks](Checks.json)

Renders: [Room view](01-Room-view.png) · [From below](02-From-below.png) · [Oblique](03-Oblique-below.png) · [Close fold](04-Close-fold.png) · [Shape unlit](05-Shape-unlit.png)

## Shape

- **Band.** One continuous band, 175–252 mm wide and 4.6 m long, follows a (2,3) knot path: three large outer loops, three small inner loops under the ceiling disc, and three crossings.
- **Lie.** The band lies flat where it passes over or under itself. It banks up to 60° at the outer loops and rolls with an S-twist through each loop. The twist always tilts away from the other strand.
- **Irregular outline.** Loop size, loop spacing, width, bank and twist all differ from loop to loop. Footprint is about 1,201 × 1,000 mm.
- **Surface.** There are 20 grooves across the width, running diagonally along the band.
- **Mount.** A Ø240 × 32 mm ceiling disc is the only ceiling fixing. Three clear posts, 40–49 mm long, drop from it to the hidden top face of the inner loops.

## Hidden lighting

- An LED channel (12 × 8 mm) runs on the hidden top face along the inner edge and shines at the ceiling. The band screens it from the room.
- A sight-line test cast 416,875 rays from 725 eye positions, 0.6–1.6 m below the ceiling and out to 3.5 m away. Stretches a viewer could see were left without LEDs. After that pruning, no tested LED station is visible.
- 2,791 mm of strip remains, in three runs.

## Checks

| Measure | Value |
|---|---|
| Self-intersections | 0 |
| Non-manifold edges | 0 |
| Minimum clearance between separate parts | 12.5 mm |
| Depth below ceiling | 223 mm at the lowest point |
| Skin | 0.957 m², about 2.19 kg in PETG at 1.8 mm |
| Channel top below ceiling | 12 mm |

## Open items (not done)

- The user has not yet reviewed this shape. It is simpler than the reference, with three loops and one band instead of several layered ribbons.
- 223 mm depth is more than the reference's stated 140 mm.
- The 12.5 mm minimum clearance is tight for a flexible printed band and needs a sag check.
- Post seats, wire routes, real LED hardware and print segmentation are not designed. It is not print-ready.
- The three post seats still show faintly as small dots from directly below.
- No viewport recording was made because the build ran in Blender background mode.
