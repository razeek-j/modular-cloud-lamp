# Lamp: three-part first-print prototype

Open `Projects/Lamp-three-parts-U1.3mf` in Snapmaker Orca as a project. It has three separate plates: one shade segment, the middle LED carrier, and the stand. No printer connection is needed to inspect or slice. Individual 3MFs and millimetre STL files are also supplied.

This is a fit-test prototype reverse-engineered from photographs, not recovered production CAD or a physically validated finished lamp. Do not print all 12 segments yet.

## Design changes

- Rebuilt the stand's six upper leg roots as vertical 2.6 × 6 mm necks inside the shade's radial slot. They widen into 6 mm tubular legs only below the shade. The ring remains 3.4 mm wide and 5 mm high, with the 8 mm underside cable opening retained.
- Widened the inside edge of the shade's carrier passage from radius 103.0 to 102.5 mm. Its outer edge stays at 107 mm. This lets the carrier's 0.8 mm backing behind the wire recess pass through during insertion, instead of catching the shade.
- Kept the middle carrier's requested 0.8 mm main wall, narrow bottom glue rim, wire recess and openings. It remains delicate; test before fitting LEDs or applying force.
- Saved an editable revised copy in `Lamp-printable.blend`. The root `Lamp.blend` is the original visual master and has not been overwritten.

## Printer setup and orientations

Snapmaker U1, standard-flow 0.4 mm nozzles, textured PEI plate, 0.20 mm layers. Generic PLA is a prototype placeholder; the printer owner must select the actual filament's profile and re-slice before printing. All parts use one material/toolhead. Colour does not identify a mechanically suitable material.

| Plate | Approx. size in print orientation | Orientation and settings |
| --- | --- | --- |
| 1 — shade segment | 100.9 × 102.8 × 84.5 mm | Closed diaphragm down; open end up. Four walls, 20% gyroid, removable supports for internal brackets. |
| 2 — LED carrier | 213.4 × 213.4 × 38 mm | Bottom rim down. No supports; the main wall is about two extrusion widths. Handle carefully during brim removal. |
| 3 — stand | 231.7 × 222.3 × 75 mm | Flat support ring down, legs pointing up. Five walls, 35% gyroid, supports for the curved tips. |

The project uses a 5 mm outer brim, moderate print speeds, and same-material support with 0.2 mm top separation and 0.35 mm lateral separation. Supports inside the open shade need to be removed without breaking the holders. No automated orientation or rescaling is required. The full assembled shade is about 345 mm wide; each of its 12 identical segments fits the U1 individually.

## Verification and its limits

`Checks/geometry-report.json` records mesh topology, fit dimensions, solid overlaps and an empty-shell centre-of-mass estimate. Each unique part is one connected watertight solid, with positive volume and zero nonmanifold edges. Revised stand versus each of the 12 shade segments has zero computed solid overlap. The carrier has no detected final-position surface crossings with the shade, and the stand/carrier have zero solid overlap.

`Checks/insertion-check.json` samples vertical insertion of the carrier and stand from below, at 2 mm intervals over a 100 mm travel. This is a discrete mesh collision check, not continuous clearance certification or a physical assembly trial. Check its results alongside the geometry report.

`Checks/Slicing` contains local toolpath validation, using the installed Snapmaker Orca engine. Headless thumbnail rendering reports graphics/shader errors; toolpath generation is checked separately. Four filament slots are configured but all geometry uses toolhead 1; support-generator warnings about multiple materials do not indicate an intentional multimaterial job.

## First physical checks

1. Confirm the intended dimensions against the actual lamp, LED strip, connector and cable. Dimensions were estimated from photos. The carrier's straight wall is 37 mm tall; wire openings are nominally 10 mm at the top, 12 × 13 mm at the lower access port and 6 mm at the downward exit. Measure real hardware before relying on these clearances.
2. Print one segment first. Check wall quality, support removal and the holder openings. Do not force a tight fit or scale the entire model to correct a local tolerance.
3. Print the carrier and revised stand. Dry-fit the shade segment on the carrier and near a stand root. Confirm the wider slot clears the backed wire channel while sliding up from below. Check that the thin carrier remains round and that the stand ring fully supports its bottom rim.
4. The segment has clip-holder apertures, but separate locking clips are not supplied in this three-part set. Holder dimensions and retention remain unverified. A second copy of the same segment is needed to test a real neighbouring joint before printing all twelve. One copy cannot establish full-ring closure or secure retention.
5. Check the stand on a level surface, under the intended assembled load, for rocking, flex, layer splitting and cable-pull tipping. The calculated empty-shell centre of mass lies near the centre of the three feet, but actual part masses, LEDs, cable forces and material strength have not been tested. Do not treat the digital centre-of-mass check as a load rating.
6. Confirm the final material, adhesive and LED operating temperature together. Generic PLA slicing does not establish suitability for a powered lamp. The files do not specify an electrical enclosure, strain relief or electrical installation.

Keep observations from the first prints: material/profile, measured slot and carrier diameters, tight/loose joints, support-removal damage and stand deflection. Those measurements should drive the next tolerance revision.

## Reproducing the preparation

Run `Scripts/prepare_print.py` with Blender in background mode; then run `Scripts/check_insertion.py` on the resulting editable copy. `Scripts/package_projects.py` packages the resulting STL geometry with native Snapmaker project settings captured locally in `Checks/UI-template.3mf`. The earlier `Scripts/slice_parts.py` records the initial CLI approach, which crashed when loading flattened standalone presets; the working validation loads the complete project instead. All artifacts and evidence remain in this project folder.
