# V04a piece-by-piece fit studies

Source: [V04a Blender checkpoint](../Circular-Ribbon-Cloud-v04a-clearance.blend). These are **fit-study sectors, not the final print/assembly package**.

The 32 STL files in `modules/` divide the four bands into 3, 7, 10 and 12 pieces, inner to outer. They include the integral returns and revised receiving relief. Closed cut faces are added at the sector boundaries. No final seam tongues, locking or bonding specification is included.

All 32 exports passed the closed-mesh check and have oriented extents under 303 mm, inside the printer's nominal 350 mm cube. This excludes supports, brims and final joint features. The tangential export orientation establishes fit only; review visible surfaces and actual toolpaths before selecting a print orientation. Units are millimetres. See [export checks](../checks/v04a-fit-module-check.json).

The assembled band meshes have no detected pairwise triangle intersections after receiving relief. That check does not establish minimum clearance, uniform wall thickness, assembly access or mechanical retention. See [relief check](../checks/v04-clearance-refinement.json).

The earlier [small flat lap test pair](../print-study-v04/README.md) remains available for basic clearance/finish trials. Its 0.25 mm nominal shelf gap is distinct from V04a's 0.50 mm normal-offset relief cutter; neither is a measured minimum clearance or validated curved joint.

Next prototype: develop one full-size hidden seam and an adjacent inter-band overlap, finalize uniform skin thickness and upper-side retention, then trial slice/print that partial assembly. Evaluate the white washi finish with the actual filament and lighting before producing the whole shade.
