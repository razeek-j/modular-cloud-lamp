# Final lamp geometry audit

Source: `/Users/razeek/Projects/3D printing/lamp-centered-final.blend`  
SHA-256: `5c448d9353efaac80db6d697be4f213d2d5141f534a1fa29c226561cccadf61e`  
The source Blender file was inspected without saving changes.

## Measured dimensions

All measurements are millimeters, from actual transformed mesh vertices in scene `02 • Full 360 Assembly`. X × Y × Z describes the current assembly orientation, not an optimized printing orientation.

| Part | X × Y × Z (mm) |
| --- | --- |
| Complete lamp | 345.3 × 345.3 × 158.3 |
| White shade | 345.3 × 345.3 × 104.6 |
| One white segment | 96.1 × 87.4 × 104.6 |
| Clear carrier with flange | 213.4 × 213.4 × 38.0 |
| Brown stand | 231.7 × 222.2 × 75.0 |

The measured shade diameter is 345.3 mm, approximately 5.3 mm greater than the earlier nominal 340 mm estimate.

## Results

- Twelve identical shade meshes are spaced at 30-degree increments and complete the circle. No surface crossings were detected between adjacent segments.
- The carrier and LED strip proxy have no detected surface crossings with the shade in their current assembled positions. This does not verify the entire insertion path.
- The measured radial carrier passage is 4.0 mm wide at Z=0. The sampled upper and lower clip-holder openings measure 5.0 × 5.0 mm. Separate clip fit and retention remain unverified.
- All four unique meshes have zero nonmanifold edges and one connected component. These checks do not replace slicer or physical print validation.
- **Three stand leg roots penetrate the shade**, at segments 01, 05 and 09. Exact Boolean intersection checks confirm solid overlap of approximately 79.3 mm³ per leg. This is real interference, not just touching faces. The stand-to-shade fit needs revision before printing the complete assembly.
- Carrier and stand share a support/contact boundary. Exact Boolean intersection volume is zero, so the two surface contact pairs are not evidence of solid overlap.
- No wire bundle geometry is present in this final file; clearance for actual wires and connectors has not been verified.

## Physical sizing

Dimensions were reverse-engineered from photos and remain provisional. Actual LED strip, wiring, clip, material and printer tolerances are not established by this geometry audit. A two-segment and clip test print is appropriate before printing all twelve pieces. Carrier wall and opening clearance should be checked against the actual strip and its connector.

## Evidence

- `final-audit.json`: detailed dimensions, topology and surface checks.
- `interference-volumes.json`: exact Boolean intersection volumes.
- `full-assembly.png`: complete assembly preview.
- `components.png`: carrier, LED strip proxy and stand preview.
