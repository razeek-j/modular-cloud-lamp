# V04 print studies

These files establish a piece-by-piece route for the 1.2 m shade. They are **geometric fit studies**, not a production-ready assembly set.

## Stepped lap test pair

`lap-test-A.stl` and `lap-test-B.stl` are small 50 × 24 × 3 mm flat test pieces. Their complementary stepped shelves have nominal 0.25 mm clearance. Print both with their unstepped face on the bed (flip B over), using the intended filament, 0.4 mm nozzle and a trial 0.16 mm layer height. Check sliding fit, warping, surface appearance, and the visible step. No final locking fastener, adhesive system, or overhead load rating is established by this pair. It is a clearance sample, not a structural coupon equivalent to the curved lamp joints.

## Shade divisions

The current division layout is 3 + 7 + 10 + 12 = **32 pieces**, inner to outer. `piece-layout.json` contains the original smooth-surface sizing calculation, which excludes integral returns. The `modules/` STLs are then cut from the actual V04 meshes, including modeled returns. See the [actual module check](../checks/v04-fit-module-check.json) for actual exported extents and manifold checks.

Each sector is closed at its cut faces and translated to millimetres at bed origin, with a tangential orientation chosen for size checking. These cuts do **not** include final segment-to-segment seam tongues, retention, or final supports. The orientation is a fit check, not a validated print orientation. Reserve room for the brim/supports, and review toolpaths before any trial print. No G-code is supplied.

Next, choose one full-size difficult sector and its neighbour, develop their actual hidden segment seam and integral inter-band lap, and test those before printing the complete shade. Layer orientation and seam placement must make natural FDM lines suit the white washi aesthetic; fine lines are not modeled into the mesh.
