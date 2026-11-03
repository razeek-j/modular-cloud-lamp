# Share with cousin — Snapmaker U1 Print Files

This folder contains the verified, repaired 3D printing files configured for the **Snapmaker U1** printer (0.4 mm nozzles, 0.20 mm layer height).

## Files

- **`Lamp.3mf`** (Primary Snapmaker project file):
  - Direct 3MF project ready to open immediately in Snapmaker Orca (`File` -> `Open Project`).
  - Pre-arranged across 3 plates:
    - **Plate 1**: 3 taller cloud shade pieces (print 4 times for total of 12 segments).
    - **Plate 2**: 1 middle LED carrier (print once).
    - **Plate 3**: 1 three-legged stand (print once).
  - Includes calibrated support bases, brim settings, and reduced support acceleration.
  - **Do not delete this file.**

- **`Lamp-TALLER-FIXED-U1-REPAIRED.zip`** (Complete standalone package):
  - Contains `Lamp-TALLER-FIXED-U1-3-shades-REPAIRED.3mf`, detailed `READ-ME.txt` print instructions, and the `STL-fallback/` directory with raw millimeter STLs (`01_Shade_segment.stl`, `02_Middle_LED_carrier.stl`, `03_Stand.stl`) if the slicer cannot open multi-plate 3MF projects.

- **`Pins/`** (Lamp Segment Connection Pins):
  - **`00_Single_Snap_Pin_BiDirectional-U1.3mf`**: Single pin project for Snapmaker Orca (~4 min print, 0.37 g PLA/PETG). Send this first to test the snap fit in the shade holes!
  - **`02_Pins_Full_Batch_28x_BiDirectional-U1.3mf`**: Full print project with 28 pins (24 required for all 12 seams + 4 spares). Print once after verifying the single pin fit.
  - **`04_Lamp_Snap_Pin_BiDirectional.stl`**: Raw 3D model for single pin (compatible with any slicer).
  - **`Pins_Full_Batch_28x_BiDirectional.stl`**: Raw 3D plate of 28 pins.
