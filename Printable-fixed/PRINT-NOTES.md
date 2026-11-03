# Current fixed taller lamp — print project

Source: `../Lamp-taller-proposal.blend`, SHA-256 `248097b1a36c31ccebea06ead3f329ee27820bc29085cffd33c5c9ffb16825de`.

This export reads the current fixed Blender meshes directly. It does not rebuild the stand, recut the slots or change the model's geometry. The older build scripts describe previous construction steps and should not be rerun on the manually fixed source.

## What to print

Open `Lamp-TALLER-FIXED-U1-3-shades.3mf` as a PROJECT in Snapmaker Orca.

- Plate 1: three identical taller shade segments. Print four batches for twelve total, after checking the first batch's fit.
- Plate 2: one taller LED carrier. Print once.
- Plate 3: one stand. Print once.

Shade height in the assembled lamp is 134.2 mm; the carrier is 41.5 mm high. The shade is rotated onto its closed end for printing, so its print height is about 83.5 mm. These are different orientations, not a scale change.

## How the print project was prepared

1. Export evaluated Blender geometry in millimetres, retaining the latest fixed mesh and dimensions.
2. Check each unique part is one watertight solid with positive volume and no degenerate faces. Check neighbour surfaces and the sliding insertion path.
3. Orient the shade closed-end down/open-end up, the carrier bottom-rim down, and the stand support-ring down with its legs upward.
4. Select U1 standard-flow 0.4 mm nozzle settings, 0.20 mm layers, supports and adhesion settings. Arrange three shade copies with room for the generated toolpaths.
5. Generate toolpaths in the installed Snapmaker Orca engine. Inspect actual extrusion paths and selected first, intermediate and upper layers, rather than relying only on the exterior Blender render.

## Holes and sliding fit

The four sampled clip-holder openings measure 5 × 5 mm in the mesh. The carrier and stand have no detected surface crossings with the shade at their assembled positions. Their insertion from below was checked at 1 mm intervals over 120 mm, with no detected collisions. Adjacent shade segments have no detected surface crossings.

The shade's broad closed face sits on the bed. Sampled first-layer previews show the two small openings on that end remaining open. Removable supports are present beneath internal holders; the open end provides access for their removal. Digital hole size and discrete collision tests cannot prove physical clearance, surface finish or clip retention. A printed hole can come out smaller or rougher, and support removal can damage a thin holder. Test the actual matching parts; do not force a tight joint.

Separate locking clip inserts are not included. Confirm their fit and retention with the actual clips before printing every shade segment. The design's actual LED strip, connectors and cable have not been supplied for measurement.

## Supports and bed adhesion

The file uses automatic normal/grid supports for the shade and stand, and no supports for the carrier. Actual toolpaths contain support and support-interface extrusion on both relevant plates.

- Model outer brim: 5 mm.
- Initial support-layer expansion: 4 mm, to enlarge the feet of support towers; no raft is enabled.
- Support speed: 60 mm/s; support interface: 40 mm/s.
- Default acceleration: 3000 mm/s²; outer walls: 1500 mm/s².
- Outer walls: 50 mm/s; inner walls: 80 mm/s.
- Support top/bottom separation: 0.20 mm; lateral separation: 0.35 mm.
- Shade: four walls, 20% gyroid. Stand: five walls, 35% gyroid.

Wider support bases are intended to improve adhesion of the stand's small support towers. Initial-layer expansion enlarges the first support layer for this purpose; see the [OrcaSlicer support settings documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/support_settings_support#initial-layer-expansion). A brim increases the first-layer footprint; see [Prusa's brim documentation](https://help.prusa3d.com/article/skirt-and-brim_133969).

These measures reduce risk; they cannot guarantee that a print or support will stay attached. Actual filament, plate cleanliness, bed temperature, first-layer calibration, cooling and warping still matter. Watch the first layers, and stop if a piece or support detaches.

## Before printing

Generic PLA is a PLACEHOLDER. Select the actual loaded filament profile and re-slice. Do not use a different material with the placeholder temperatures. First print and inspect the initial batch before the remaining three shade runs. Confirm support removal, hole/slot fit, clip retention and stand rigidity. Suitability for LED heat and the assembled load is not physically validated.

## Evidence

- `Checks/source-and-fit-audit.json`: current source identity, dimensions, topology, 5 mm holes, neighbouring surfaces and insertion tests.
- `Checks/toolpath-qa.json`: actual generated objects, first-layer model extrusion, support/interface presence and plate-bound checks.
- `Checks/toolpath-previews.png`: selected layer views from the generated extrusion paths (cyan model, orange support, grey brim).
- `Checks/Slicing`: local toolpath validation. The command-line renderer reports headless thumbnail/shader errors; the three G-code toolpaths are generated and checked independently.

This is a first-print prototype, not a physically certified finished lamp. A successful slice proves that the slicer can generate paths, not that all manufacturing and assembly failure modes have been eliminated.
