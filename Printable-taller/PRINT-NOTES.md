# Taller lamp: three shade segments per batch

Open `Projects/Lamp-TALLER-U1-3-shades.3mf` in Snapmaker Orca as a project. It has three separate plates: three taller shade segments, the taller middle LED carrier, and the stand. No printer connection is needed to inspect or slice. Individual 3MFs and millimetre STL files are also supplied.

This is a fit-test prototype reverse-engineered from photographs, not recovered production CAD or a physically validated finished lamp. Plate 1 prints three identical shade segments in one job (layer by layer). Repeat plate 1 four times to obtain 12 segments. Print plates 2 and 3 only once each. Inspect the first batch before repeating it.

## Design changes

- Rebuilt the stand's six upper leg roots as vertical 2.6 × 6 mm necks inside the shade's radial slot. They widen into 6 mm tubular legs only below the taller shade (vertical necks to Z=-70 mm, full-size tubes below -78 mm). The ring remains 3.4 mm wide and 5 mm high, with the 8 mm underside cable opening retained.
- Widened the inside edge of the shade's carrier passage from radius 103.0 to 102.5 mm. Its outer edge stays at 107 mm. This lets the carrier's 0.8 mm backing behind the wire recess pass through during insertion, instead of catching the shade.
- Kept the middle carrier's requested 0.8 mm main wall, narrow bottom glue rim, wire recess and openings. It remains delicate; test before fitting LEDs or applying force.
- Saved an editable revised copy in `Lamp-taller-printable.blend`. The source `Lamp-taller-proposal.blend` has not been overwritten. This export uses its current smoothed cloud profile: 134.2 mm shade height and 41.5 mm carrier height. The old small model is not the source.

## Printer setup and orientations

Snapmaker U1, standard-flow 0.4 mm nozzles, textured PEI plate, 0.20 mm layers. Generic PLA is a prototype placeholder; the printer owner must select the actual filament's profile and re-slice before printing. All parts use one material/toolhead. Colour does not identify a mechanically suitable material.

| Plate | Approx. size in print orientation | Orientation and settings |
| --- | --- | --- |
| 1 — three shade segments | 103.2 × 130.9 × 83.5 mm | Each closed diaphragm down, open end up; third copy rotated 90° in the bed plane. Four walls, 20% gyroid, removable supports for internal brackets. |
| 2 — LED carrier | 213.4 × 213.4 × 41.5 mm | Bottom rim down. No supports; the main wall is about two extrusion widths. Handle carefully during brim removal. |
| 3 — stand | 231.7 × 222.3 × 75 mm | Flat support ring down, legs pointing up. Five walls, 35% gyroid, supports for the curved tips. |

The project uses a 5 mm outer brim, moderate print speeds, and same-material support with 0.2 mm top separation and 0.35 mm lateral separation. Supports inside the open shade need to be removed without breaking the holders. No automated orientation or rescaling is required. The full assembled shade is about 345 mm wide; each of its 12 identical segments fits the U1 individually.

## Verification and its limits

`Checks/geometry-report.json` records mesh topology, fit dimensions, solid overlaps and an empty-shell centre-of-mass estimate. Each unique part is one connected watertight solid, with positive volume and zero nonmanifold edges. Revised stand versus each of the 12 shade segments has zero computed solid overlap. The carrier has no detected final-position surface crossings with the shade, and the stand/carrier have zero solid overlap.

`Checks/insertion-check.json` samples vertical insertion of the carrier and stand from below, at 2 mm intervals over a 120 mm travel. This is a discrete mesh collision check, not continuous clearance certification or a physical assembly trial. No surface crossings were detected in these sampled insertion positions. This does not measure printed clearance.

`Checks/Slicing` contains local toolpath validation, using the installed Snapmaker Orca engine. Headless thumbnail rendering reports graphics/shader errors; toolpath generation is checked separately. Four filament slots are configured but all geometry uses toolhead 1; support-generator warnings about multiple materials do not indicate an intentional multimaterial job.

## First physical checks

1. Confirm the intended dimensions against the actual lamp, LED strip, connector and cable. Dimensions were estimated from photos. The taller carrier is 41.5 mm high overall, and its wire openings are stretched with it. Measure real hardware before relying on these clearances.
2. If desired, use the individual segment 3MF for a one-piece first test; the combined project intentionally prints three on plate 1. Check wall quality, support removal and the holder openings. Do not force a tight fit or scale the entire model to correct a local tolerance.
3. Print the carrier and revised stand. Dry-fit the shade segment on the carrier and near a stand root. Confirm the wider slot clears the backed wire channel while sliding up from below. Check that the thin carrier remains round and that the stand ring fully supports its bottom rim.
4. The segment has clip-holder apertures, but separate locking clips are not supplied in this three-part set. Holder dimensions and retention remain unverified. The three copies on plate 1 allow neighbouring-joint tests before printing all twelve. A partial set cannot establish full-ring closure or secure retention.
5. Check the stand on a level surface, under the intended assembled load, for rocking, flex, layer splitting and cable-pull tipping. The calculated empty-shell centre of mass lies near the centre of the three feet, but actual part masses, LEDs, cable forces and material strength have not been tested. Do not treat the digital centre-of-mass check as a load rating.
6. Confirm the final material, adhesive and LED operating temperature together. Generic PLA slicing does not establish suitability for a powered lamp. The files do not specify an electrical enclosure, strain relief or electrical installation.

Keep observations from the first prints: material/profile, measured slot and carrier diameters, tight/loose joints, support-removal damage and stand deflection. Those measurements should drive the next tolerance revision.

## Reproducing the preparation

Run `Scripts/prepare_print.py` with Blender in background mode; then run `Scripts/check_insertion.py` on the resulting editable copy. `Scripts/package_projects.py` packages the resulting STL geometry with native Snapmaker project settings captured locally in `Checks/UI-template.3mf`. The earlier `Scripts/slice_parts.py` records the initial CLI approach, which crashed when loading flattened standalone presets; the working validation loads the complete project instead. All artifacts and evidence remain in this project folder.

## Current slicer estimates

Plate 1 (three taller shade segments): 30 h 40 min and 197.5 g. Plate 2 (taller carrier): 3 h 54 min and 27.5 g. Plate 3 (stand): 4 h 36 min and 28.4 g. These estimates use the placeholder Generic PLA profile and include supports/brims. Re-slice after choosing the actual filament. Four shade batches plus one carrier and one stand are approximately 131 hours total under these settings.
