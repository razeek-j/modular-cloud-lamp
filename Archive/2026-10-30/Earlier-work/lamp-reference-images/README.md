# Lamp reference images

Module topology correction: the current single-module references are `02-single-shade-module-v2-open-top.png` and `11-single-shade-module-v2-underside.png`. The top has a large open cavity; the underside has a thin partial retaining base with a narrower elongated opening for the circular support band. The earlier `02-single-shade-module.png` incorrectly treated it as an open-ended cuff and is superseded. The current PNGs show the two opposite sides of the same reconstructed component. Slot dimensions remain unmeasured; original user top/bottom photographs and generation prompts are in `../lamp-connector-details/`.

Stand update: use `03-brown-three-leg-stand-v2-cable-opening.png` for the current stand reference. The user's additional zoom photos identify a small wire-clearance opening beneath the leg-root region. See `../lamp-connector-details/10-stand-cable-opening-closeup.png` for its enlarged view. The earlier stand rendering is superseded; the gap size remains approximate.

Connector correction: the user confirms that the white module has an empty holder with a rectangular opening; its clip is a separate insert. The projecting-pegs / receiving-holes image was incorrect and has been deleted. See `../lamp-connector-details/09-empty-clip-holder.png` and the user's original zoom in that folder. Do not use these initial product views as exact joint references.

These images are AI-generated visual reconstructions from the supplied screenshots. They preserve the observed design as closely as possible, but are not exact CAD geometry or verified manufacturing drawings.

## Deliverables

- `01-assembled-lamp.png`: complete lamp, unlit, isolated.
- `02-single-shade-module.png`: one white repeat module, isolated for individual image-to-3D input.
- `03-brown-three-leg-stand.png`: circular support with three triangular loop legs, inverted as in the printing reference.
- `04-led-carrier.png`: hollow translucent cylindrical carrier with LED strip, isolated.
- `05-complete-white-shade.png`: complete shade without stand or LED carrier.

Use one isolated part image at a time when generating separate meshes. Use the assembled lamp and complete shade as visual assembly references. The small fittings and partially hidden surfaces should be checked against the original screenshots before designing printable joints.

## Observations from the source

- The shade appears to use twelve white repeat modules; IMG_0242 shows two rows of six.
- The brown frame has a circular ring and three loop legs. IMG_0240 shows it upside down on the printer bed.
- The translucent carrier has a short cylindrical wall, an annular lower flange and a cable access opening. A yellow LED strip wraps around its outer circumference near one edge.
- The white shade is removable from the core and can be separated into linked arcs.

No physical dimensions, wall thicknesses, joint clearances or exact connector profiles can be verified from these screenshots. The printer's 260 x 260 mm label is its bed size, not a measured product size. Avoid using generated detail as evidence for hidden construction.

Generated with the built-in image_gen tool. Exact prompts and source image lists are in `generation-prompts.json`.
