# V06 overlap export — failed draft, do not print

`SAMPLE-W01-folded-overlap-mm.stl` is an actual full-size crop from the evaluated outer wave, including an integral folded return and two screw clearances. The artificial sector cuts are capped and do not represent final production seams.

The bounding box is approximately **252 × 169 × 191 mm**, fitting inside the Kobra S1 Max's nominal volume before support/brim allowances. However, `sample-check.json` reports **241 nonadjacent triangle overlap candidates**. Zero non-manifold edges alone does not establish validity. This export is quarantined for repair and is **not a ready-to-print prototype**. No slicing or physical fit has been verified.

`receiver-prototype-outline-mm.svg` is a true-size provisional receiver outline with 3.3 mm hole marks, derived from the modeled corresponding metal receiver. `receiver-dimensions.json` records its dimensions. The suggested 3 mm aluminum stock and M3 interface have not been load-rated; do not substitute a printed plate for the metal structural part.

Next: resolve return/cut-surface intersections, inspect actual wall thickness, re-export and slice with the exact printer profile. Trial 0.4 mm nozzle / 0.16 mm layer height using the actual filament manufacturer's settings. Select orientation and supports to protect luminous surfaces. Test fit, appearance, removal, sustained sag and temperature with the real metal receiver and light engine before overhead use. Final complete-shade segmentation remains outstanding.
