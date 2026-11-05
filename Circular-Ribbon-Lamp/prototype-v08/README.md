# V08 ribbon fit and lighting prototype

[Open the Blender project](Ribbon-V08-fold-prototype.blend). It opens on the rear of the full-size two-piece test. Use the Scene selector to open **V07 | Full fixture context** for the 1.2 m model. Choose **View → Cameras → Active Camera** for the full-fixture view and enable **V08 · Draft cut lines (viewport only)** in the Outliner to inspect the cuts.

The [underside reference](underside-reference.png) adds a clear view of the target silhouette. Its large upper-right roll, open pockets around the central disk, and broad diagonal sweep are the comparison points for the next full-shade review. The V07 context model still reads more concentrically from below. V08 tests a joining and lighting detail on its actual W01 surface.

## Print this test first

| Part | Quantity | Oriented size in mm |
| --- | ---: | --- |
| [Ribbon A](Models/01_Ribbon_A.stl) | 1 | 178.4 × 50.9 × 151.8 |
| [Ribbon B](Models/02_Ribbon_B.stl) | 1 | 177.5 × 61.1 × 155.5 |
| [Inner rear splice](Models/03_Rear_splice_inner.stl) | 1 | 48.3 × 18.8 × 7.3 |
| [Outer rear splice](Models/04_Rear_splice_outer.stl) | 1 | 37.1 × 17.9 × 7.2 |

1. Import the four STLs in millimetres. They have trial orientations already. Use the Kobra S1 Max 0.4 mm preset and milky, light-diffusing PETG. Start with **0.16 mm layers**. The two tall skins stand on their seam ends. Inspect bed contact, thin-wall toolpaths, and overhangs in Preview. Use a brim and keep support contact on the rear where practical. Start with Ribbon A on a plate by itself. [Anycubic Slicer Next quick start](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta%28orca-version%29/anycubic-slicer-next-slicing-software-quick-start-guide)
2. Face the two cut ends toward one another and line up the ripples. Dry-fit the longer inner splice and shorter outer splice on the back, following their matching curves. The two shade halves meet edge to edge with a modeled **0.20 mm centreline gap**. The splice undersides follow the rear contour with **0.15 mm nominal space** for an adhesive bond line. Use removable tape or a soft jig to hold the seam for the first light test. Test any permanent adhesive on scrap of the actual filament. These splices align a bench sample. The ceiling carrier and final positive retention remain separate design work.
3. Place a straight **100 mm** section of warm COB tape in an opaque aluminum channel approximately **120 × 24 mm**, with side lips and end caps. Support the channel separately from the printed test. Set the bottom of the channel roughly **35 mm behind the seam centre**, with the LED facing a matte white board around **115 mm from the emitter**. View the ribbon from below and at an angle. Compare the seam and splices with the tape off and on. Treat the Blender output as a relative shadow study.
4. Repeat with the channel shifted toward an overlapping fold so the hardware is outside the backlighting path of the exposed panel. Inspect whether the adjacent fold conceals the channel body from the room. Before exporting the rest, test one real overlapping pair with the seam, splice and wiring tucked behind it.

## What the checks showed

- Blender checked the four parts for closed, connected mesh topology, non-adjacent self-intersection and assembled pairwise intersections. Snapmaker Orca independently read each STL as one manifold part. Its CLI crashed when loading process settings, so the print orientation and toolpaths still need a slicer review. [Geometry results](geometry-check.json)
- All **8,640** sampled emitter sightlines at or below horizontal hit the metal trough in Blender. The [lit room-side render](v08-bounce-room-side.png) still shows the trough's shadow and the two splice shadows through the ribbon. The [rear view](v08-rear-assembly.png) shows where those shadows originate. The current bench layout demonstrates emitter shielding and exposes the remaining optical problem.
- The full-shade [draft cut map](draft-cut-map.json) fits 33 provisional skin pieces in one trial orientation per piece. Counts for W01–W06 are **13 / 7 / 5 / 3 / 3 / 2**. The largest calculated axis is 284.3 mm before supports and joint features. The Kobra S1 Max has a nominal 350 mm cube. Only **one** seam had at least half its samples screened by an adjacent ribbon directly below. Move the final seam lines into redesigned overlaps before exporting the full set. [Anycubic Kobra S1 Max specifications](https://store.anycubic.com/products/kobra-s1-max)

Keep the Ø220 mm central canopy as the ceiling attachment. The final carrier should run inside the folds from that canopy. Position the LED channels and joint seats in those same screened pockets and leave the luminous faces free of backing hardware. Check service access, heat, creep, and positive retention on the full-size partial assembly before overhead installation.

[Live Blender viewport review](../process/videos/14-v08-fold-prototype.mp4) · [Build source](../scripts/build_v08_fold_prototype.py) · [Cut-map source](../scripts/plan_v08_cuts.py)
