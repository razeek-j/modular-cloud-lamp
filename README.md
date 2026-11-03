# Lamp project

## Repaired sharing package — 3 November 2026

Use **Share-with-cousin/Lamp.3mf** or **Share-with-cousin/Lamp-TALLER-FIXED-U1-REPAIRED.zip**:
- **`Share-with-cousin/Lamp.3mf`**: Open directly as a project in Snapmaker Orca (`File` -> `Open Project`). It preserves all 3 plates (3 taller cloud shades on Plate 1, LED carrier on Plate 2, and 3-legged stand on Plate 3) with calibrated Snapmaker U1 printer settings and support parameters.
- **`Share-with-cousin/Lamp-TALLER-FIXED-U1-REPAIRED.zip`**: Complete archive with `Lamp-TALLER-FIXED-U1-3-shades-REPAIRED.3mf`, print notes, and STL fallback models.

The exact extracted 3MF has been imported and sliced successfully by Snapmaker Orca.

The earlier shared files failed because a metadata-writing step reserialized core model XML with `ns0:` prefixes which the Snapmaker importer did not recognize. Those broken files are archived under Archive/2026-11-03/Broken-share-before-repair. Use Scripts/repair_share_package.py under Printable-fixed to build the corrected share package without rewriting the model XML. Evidence: Printable-fixed/Checks/Compatibility/repair-manifest.json.

Open **Lamp-taller-proposal.blend** for the current editable assembly. It contains the smoothed taller cloud-shaped shade, thin LED carrier and corrected stand. The yellow LED display strip has been removed.

## Views in Blender

1. **01 • Complete lamp** — the full assembly.
2. **02 • Shade inspection** — shade and internal details.
3. **03 • Stand and LED carrier** — carrier, support ring and feet.
4. **04 • Thin carrier detail** — wire channel, upper notch and glue rim.

## Current dimensions and fixes

The shade is approximately 345.3 mm across and 134.2 mm high. The carrier is 41.5 mm high with a 0.8 mm wall. The full assembly is approximately 173.1 mm tall. The sampled clip-holder bores measure 5 × 5 mm.

The current proposal now includes the mechanical fixes from Printable-taller: the stand has narrow vertical roots down to Z=-70 mm before widening into tubular feet; the shade passage inner radius is 102.5 mm, allowing the backed wire channel to pass through. The exterior cloud profile is retained.

Support/Checks/assembly-fixes/verification.json records the independent recheck and synchronization. No surface crossings were detected between stand and shade or carrier and shade. Carrier and stand insertion from below were sampled every 1 mm over 120 mm, with no detected collisions. This is a discrete check, not a continuous clearance proof. Actual clip fit, printed clearances, supports, strength and hardware dimensions remain physically unverified.

## Files for a test print

Use **Printable-taller/Projects/Lamp-TALLER-U1-3-shades.3mf** in Snapmaker Orca for the taller version. It contains three shade pieces on plate 1, one carrier on plate 2 and one stand on plate 3. The matching editable printable copy is **Printable-taller/Lamp-taller-printable.blend**. Read **Printable-taller/PRINT-NOTES.md** for settings and test-print guidance. This set already contains the same mechanical corrections; its print geometry did not need changing during synchronization.

Lamp.blend and the files under Printable are earlier, smaller versions. Keep them only for comparison; they are not the current taller assembly. The original Lamp.blend still has the earlier stand interference.

## Supporting files

- **Support/References** — original photographs and detail crops.
- **Support/Checks** — measurements, previews and reports. Older reports describe earlier versions and may list issues now fixed.
- **Archive/2026-10-30** — previous versions and scripts. The pre-fix taller model is Versions/Lamp-taller-proposal-before-assembly-fixes.blend.
- **Support/cleanup-manifest.json** — earlier file organization history.

Build scripts are historical recipes. Verify their input and output paths before running them; some regenerate earlier geometry. Save current manual edits to Lamp-taller-proposal.blend.

## Latest export from the fixed source

`Printable-fixed` re-exports the current fixed `Lamp-taller-proposal.blend` directly without reconstructing or modifying its geometry. The primary share file is `Share-with-cousin/Lamp.3mf` (and bundled in `Share-with-cousin/Lamp-TALLER-FIXED-U1-REPAIRED.zip`): three shade segments on plate 1, carrier on plate 2, stand on plate 3. Support feet are enlarged and support speed/acceleration reduced. See `Printable-fixed/PRINT-NOTES.md` and its current source/fit and actual toolpath checks. The files under Printable-taller are the previous export.
