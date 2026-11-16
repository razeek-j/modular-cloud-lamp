# V14: circular ribbon knot with hidden LEDs

A new direction from the user's two references, 16 November 2026. Their circular reference shows a round cloud of rolling, crossing ribbons with grooved faces and warm light from inside. V14 rebuilds the lamp as **one continuous closed band**. The band loops twice around a single centre drum and crosses over itself ten times. It is not a copy of V9–V13.

[Blender model](Ribbon-Lamp-V14-Circular-Knot.blend) · [Build script](../scripts/build_v14_circular_knot.py) · [Geometry](../scripts/v14_knot_geometry.py) · [Clearance check](../scripts/v14_clearance.py) · [Checks](Checks.json)

| View | File |
|---|---|
| From directly below, lit | [01-From-below.png](01-From-below.png) |
| Room view, about 1.15 m below the ceiling | [02-Room-view.png](02-Room-view.png) |
| Oblique from below | [03-Oblique-below.png](03-Oblique-below.png) |
| Centre detail | [04-Centre-detail.png](04-Centre-detail.png) |
| Shape only, LEDs off | [05-Shape-unlit.png](05-Shape-unlit.png) |

## How the shape is made

- **Path.** A (2,5) torus-knot path is flattened to a ceiling profile: 5 outer lobes, 5 inner lobes and 10 crossings. Every plan direction holds exactly two strands of the band.
- **Roll.** The ribbon's width direction is set square to the line joining the two strands at each angle. Their cross-sections therefore stay parallel and can't collide. The band stands as a wall in the lobes and lies flat where it passes over or under itself, which gives the rolling look.
- **Level top.** One constant stack height keeps the top edge level 21 mm below the ceiling. A strand narrows to no less than 90 mm while it climbs toward an over-crossing, so it never rises above that line.
- **Grade.** The height change between crossings runs at a near-constant grade along the plan path. The maximum is 28°, so there are no dives in the tight inner lobes.
- **Surface.** There are 22 continuous grooves across the width. Their depth is ±0.55 mm, and they fade out before the edges so the edges stay clean.

## Hidden lighting

- **Lobe channels.** Five upward-facing channels sit on the top edge of the outer lobe walls. They are 12 mm wide and 10 mm deep, with closed ends, and hold 1,059 mm of 8 mm COB strip in total. Each opening faces up and leans 35° toward the centre. The strip washes the ceiling and the inside faces of the band, and the lobe wall screens it from the room.
- **Placement.** Channels are only placed where the wall is upright (|Dz| > 0.70) and its top edge is near level (grade < 15°). On steeper edges the strip could be seen lengthwise from across the room.
- **Visibility check.** 12,483 sight lines were cast from 219 eye positions, 0.6–1.6 m below the ceiling and out to 3.5 m away. None reaches an LED.
- **Drum.** The base of the centre drum is an opal diffuser with a hidden LED board, which gives the centre a soft glow.

## Checks (Checks.json)

| Measure | Value |
|---|---|
| Footprint | about 1,066 × 1,046 mm |
| Depth | 279 mm below ceiling at the lowest point |
| Band | 6.19 m long, 90–176 mm wide, 1.8 mm thick |
| Skin | 0.81 m², about 1.85 kg in PETG |
| Self-intersections | 0 |
| Non-manifold edges | 0 |
| Minimum clearance between separate parts of the band | about 32 mm |
| Centre drum | Ø304 × 130 mm; the inner-lobe walls sit about 1.6 mm off its side |

## Open items (not done)

- **Depth.** 279 mm is deeper than earlier targets of 160–227 mm, so it needs a room-height check.
- **Load path.** Only the five inner-lobe seats on the drum are modelled. The clips or screws are not designed. The flat crossings span unsupported and need a sag calculation and a bench test.
- **Wiring.** No route from the outer-lobe channels to the drum is modelled yet.
- **LED hardware.** The channel is drawn as an opaque profile, either a bendable aluminium LED profile or a lined printed seat. The real hardware is not chosen.
- **Printing.** The band is not yet split into print-bed-sized segments with laps. It is not print-ready.
- **Appearance.** From below, V14 reads as a regular 5-lobe flower. The reference is a freer, asymmetric cloud. The user still has to review it.
- **Process capture.** No viewport recording was made for this step because it was built and rendered with Blender in background mode.
