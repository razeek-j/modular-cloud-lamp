# Lamp Connection Pins — Print and Assembly Notes

This document provides print settings, material recommendations, and assembly guidance for the modular connector pins connecting the 12 lamp shade segments of the Airy Table Lamp.

---

## 1. Do You Need Bendable (TPU) Filament?

**No, flexible / TPU filament is NOT required.**

- **Geometric Compliance**: Elasticity is achieved geometrically through thin dual cantilever spring arms separated by a central slot, rather than material elasticity.
- **Strain Analysis**: The maximum barb deflection during insertion is $0.35\text{ mm}$ over an $8.0\text{ mm}$ cantilever beam length ($\approx 1.7\%$ elastic bending strain).
- **Material Compatibility**:
  - **Standard PLA**: Fully capable of this elastic deflection without yielding or snapping.
  - **PETG (Recommended)**: High fatigue endurance, slightly more ductile, and transparent/translucent PETG blends seamlessly with the lamp's light diffusion.
- **Layer Orientation**: When printed flat on the build plate (as oriented in the STL and 3MF files), the toolpath extrusion paths run continuously along the length of the cantilever arms. This provides maximum tensile strength and prevents layer delamination during snap engagement.

---

## 2. Pin Designs Provided

| File | Type | Description | Dimensions |
| :--- | :--- | :--- | :--- |
| `04_Lamp_Snap_Pin_BiDirectional.stl` | 1-Piece Snap | Double-ended cantilever snap pin with central stop collar and dual $22^\circ$ lead ramps | $16.2 \times 6.6 \times 4.6\text{ mm}$ |
| `05_Lamp_TwoPiece_Female_Socket.stl` | 2-Piece Socket | Female sleeve with $8\times8\text{ mm}$ outer flange, $3\times3\text{ mm}$ bore, and dual side latch windows | $6.55 \times 8.0 \times 8.0\text{ mm}$ |
| `06_Lamp_TwoPiece_Male_Latch.stl` | 2-Piece Male | Male barbed latch with $8\times8\text{ mm}$ flange and split spring-cantilever barb | $10.35 \times 8.0 \times 8.0\text{ mm}$ |
| `07_Lamp_TwoPiece_Pair.stl` | 2-Piece Pair | 1 female socket + 1 male latch oriented flat for a single joint test | $13.1 \times 20.0 \times 8.0\text{ mm}$ |
| `08_Lamp_Alignment_Dowel.stl` | Solid Dowel | Precision solid alignment dowel with stop collar for friction fit or glued joints | $11.8 \times 6.6 \times 4.65\text{ mm}$ |

### Ready-to-Print Batches & Test Plates:
- **`04_Lamp_Snap_Pin_BiDirectional.stl`** / **`00_Single_Snap_Pin_BiDirectional-U1.3mf`**:
  Single BiDirectional snap-fit pin centered on the build plate for an immediate 1-piece test print.
  - **Print time**: ~4 minutes
  - **Filament**: 0.37 g (23 layers at 0.20 mm)
  - **Purpose**: Quick physical check of hole insertion, barb engagement, and retention click.
- **`Pins_Test_Sampler_Kit.stl`** / **`01_Pins_Test_Sampler_Kit-U1.3mf`**:
  Contains 2× BiDirectional snap pins, 2× Two-Piece pairs, and 2× Dowels.
  - **Print time**: ~22 minutes
  - **Filament**: ~1.9 g
  - **Purpose**: Rapid test print to compare all designs and verify printer tolerances before running the full batch.
- **`Pins_Full_Batch_28x_BiDirectional.stl`** / **`02_Pins_Full_Batch_28x_BiDirectional-U1.3mf`**:
  Full print plate of 28 BiDirectional snap pins (24 required + 4 spares) in a neat $4 \times 7$ grid.
- **`Pins_Full_Batch_28x_TwoPiece.stl`** / **`03_Pins_Full_Batch_28x_TwoPiece-U1.3mf`**:
  Full print plate of 28 Two-Piece pairs (28 male + 28 female).

---

## 3. Recommended Print Settings

- **Print Orientation**: Flat on the build plate (pre-oriented in the files).
- **Layer Height**: `0.16 mm` to `0.20 mm` (`0.16 mm` gives optimal ramp smoothness for the snap barb).
- **Wall Loops**: `4` walls (produces 100% solid perimeters across the small pin shafts).
- **Infill**: `100%` solid.
- **Supports**: **DISABLED / NONE**.
  - All overhangs on the barbs are $22^\circ$ from horizontal, well within support-free bridging limits.
- **Brim**: None needed (parts have flat contact bases).
- **Cooling**: 100% part fan for crisp overhangs and slot definition.

---

## 4. Assembly Instructions

Total joints: 12 seams around the circumference.
Pins required per seam: 2 pins (one at upper bracket $Z = +38.8\text{ mm}$, one at lower bracket $Z = -38.8\text{ mm}$).
Total pins needed for complete lamp: **24 pins**.

### Option A: 1-Piece BiDirectional Snap Pin (Fastest Assembly)
1. Push one end of the pin into the $5\times5\text{ mm}$ bracket hole of Segment 1 until the central collar stops against the bracket surface.
2. The barb will snap over the inside edge of the Segment 1 bracket.
3. Align the bracket hole of Segment 2 with the protruding end of the pin.
4. Press firmly until the second barb snaps into place. The $0.8\text{ mm}$ collar fills the seam gap and keeps the segments aligned.

### Option B: 2-Piece Push-Lock Pin (Highest Clamping Force)
1. Insert the **Female Socket** through the bracket hole from the inside of Segment 1 (flange stops against the bracket).
2. Insert the **Male Latch** through the bracket hole from the inside of Segment 2.
3. Squeeze both flange heads together across the joint.
4. The male barb compresses through the female bore and clicks into the side locking windows. The two flanges sandwich both brackets firmly together.

---

## 5. Verification & Quality Assurance

- **Watertight & Manifold**: All 8 STL models and 3MF projects verified with 0 non-manifold edges, 0 degenerate faces, and positive volume.
- **Geometric Mating Check**: Measured directly against Blender source geometry:
  - Bracket aperture: $5.00 \times 5.00\text{ mm}$.
  - Pin body: $4.60 \times 4.60\text{ mm}$ ($0.20\text{ mm}$ clearance per side for smooth insertion).
  - Bracket thickness: $4.80\text{ mm}$ (Segment 1) and $5.01\text{ mm}$ (Segment 2).
  - Pin shaft lengths: $5.20\text{ mm}$ and $5.40\text{ mm}$ ($0.40\text{ mm}$ clearance before snap shoulder).
  - Barb catch width: $5.40\text{ mm}$ ($0.40\text{ mm}$ retention shoulder per side).
