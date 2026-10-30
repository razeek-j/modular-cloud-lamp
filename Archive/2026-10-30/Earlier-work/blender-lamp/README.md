# Blender segment — sharp groove iteration

Open `lamp-segment-v06.blend`. It contains three scenes:

- **01 • Single segment** — the editable curved component in a review/printing orientation.
- **02 • Circle check** — 12 linked copies of the same mesh, spaced at 30 degrees.
- **03 • Carrier fit** — a simple cyan cylindrical wall passing through three spaced segments so the contact area is exposed.

The original reference photos are packed into the blend file as hidden image empties and retained in `reference/`. No AI-generated product image was used to construct this geometry.

## Change dimensions

The **Lamp** tab in the viewport sidebar is active in the current Blender session. Change parameters, then click **Rebuild segment + circle + fit checks**. The three scenes share a single mesh; direct Edit Mode changes also propagate to the circular copies. Rebuilding regenerates that mesh and replaces direct mesh edits, so save a separate version before mixing manual edits with regeneration.

On a later fresh Blender session, the geometry still opens normally. To re-enable the optional controls, use the Python console (Shift F4 while pointing inside the viewport) and run:

```python
import sys
sys.path.insert(0, '/Users/razeek/Projects/3D printing/output/blender-lamp')
import build_lamp
```

Return with Shift F5, press N if needed and select the Lamp tab. No global auto-run preference needs changing. The same builder and `parameters.json` can regenerate the file using Blender's background command line.

## Shape and scale assumptions

This is the first adjustable blockout for iteration, not an exact reconstruction or a print-ready original design. The key modeling hypothesis is a short curved toroidal sector with one open axial face and one thin end diaphragm. A narrow opening in that diaphragm accommodates the **clear cylindrical LED carrier**, as clarified by the user.

Provisional values: 12 segments, 125 mm circle centerline radius, 45 x 48 mm section radii, 1.6 mm wall/web, 0.70 mm joint clearance at the centerline, 10 helical flutes and 8% end taper. These nominal dimensions give roughly 340 mm overall diameter before flute relief and 96 mm height. They are not measurements from the original product.

The fit proxy is a 105 mm radius cylinder wall, 1.2 mm thick and 60 mm high. The opening has 0.8 mm radial clearance on either side. Its entry provisionally opens through the upper inner shoulder so a cylinder can be lowered axially. That entry path and the rib profile need visual review against the photos. Changing the open-entry setting allows comparison with an enclosed passage.

The carrier **flange**, clip-holder details, separate clips, LED strip and brown stand are not yet included in this focused first-segment model. The current fit check therefore applies to the cylindrical wall only.

## Checks

`geometry-checks.json` records the mesh topology, connectedness, adjacent-sector intersections, circle spacing, seated cylinder wall intersections and sampled vertical insertion positions. A computer clearance check at assumed dimensions is not evidence of physical fit. No STL is supplied as an approved printable part at this stage.

The three PNG previews are rendered directly from Blender geometry.

## Revision 02 — sharper bends and visible grooves

The rounded rib surfaces now meet through explicit V-shaped recesses. Each groove has a sharp bottom and two defined lips, with geometry aligned along the helical path. These are actual mesh creases, not painted shading. The additional groove depth starts at 2 mm and its opening spans 25% of a rib pitch; both values are adjustable in the Lamp sidebar. The joint clearance between neighboring modules increased from 0.35 to 0.70 mm at the circle centerline. Carrier slot dimensions were preserved.

The previous live scene, including its current object orientation, is saved as `lamp-before-sharp-grooves.blend`. Earlier script, parameters, checks and previews are in `v01-backup/`. The new version uses the standard review orientation.

The regenerated mesh remains one closed connected shell. Twelve copies complete 360 degrees without detected neighboring surface intersections. The cylindrical wall clearance checks still pass at the assumed dimensions; this does not validate the unmodeled flange or physical print fit.

## Revision 03 — clip holder

A provisional raised holder with a 5 × 5 mm empty through-opening is integrated into the inside of the end diaphragm. The separate clip is not modeled; its shape and fit are unverified. The holder location and size are estimates from the photograph, not measured dimensions. The prior version remains available as `lamp-segment-v02.blend`.

## Revision 04 — paired holders across neighboring segments

There are now two empty holder openings on the end diaphragm and a matching pair on the open rim, four openings per segment. Open-rim straps support the holders from the shell. Their placement (radius 125 mm, heights ±30 mm), 5 × 5 mm aperture and support shape are provisional engineering estimates rather than recovered source measurements. Separate clips remain unmodeled.

The two mating patterns use the same joint-plane axes after a 30-degree copy rotation. Computed lateral misalignment is below 0.00001 mm, angular error is zero at numerical precision, and the mating gap is 0.70 mm. Actual mesh ray checks confirm all four bore centerlines are clear. The connected mesh, adjacent-sector and cylindrical-wall clearance checks pass. These checks establish alignment of this proposed geometry, not the original product or a physical clip fit.

## Revision 05 — continuous arches and contained holders

The added V-cut lips have been removed. Each rib now has one smooth arch, meeting the next at one sharp cusp. Holder supports are intersected with a solid envelope inset from the visible exterior by 1.5% of the cross-section radius. This puts their tips beneath the outer silhouette and prevents exterior tabs. Front and open-end pairs retain their common joint-plane bore axes. All four bore centerline rays are clear; the 12-part ring and simplified cylindrical carrier wall remain free of detected intersections. The final shell has one connected component and no nonmanifold edges.

Likely source identified from the original printer filename: IAP Airy Table Lamp Super Pack by iamprinted. The designer listing includes IAP_mini clip.stl (20 × 6.5 × 5 mm overall) and recommends transparent PETG for the small clips. This supports a separately printed insert connector, rather than identifying a standard purchased hook. The clip file and its precise latch geometry have not been accessed, so this draft does not claim compatibility with that original clip. Reference: https://cults3d.com/en/3d-model/home/iap-airy-table-lamp-super-pack

## Revision 06 — larger LED carrier passage

The long carrier slot increased from 2.8 mm to 4.0 mm in radial width. At the provisional 1.2 mm carrier-wall thickness this gives 1.4 mm clearance on each side. Bottom clearance increased from 0.8 mm to 1.2 mm. The entry remains open. Mesh continuity, holder bore clearance and alignment, adjacent segment clearance and sampled carrier-wall insertion checks pass. Physical carrier dimensions and flange fit remain unverified.
