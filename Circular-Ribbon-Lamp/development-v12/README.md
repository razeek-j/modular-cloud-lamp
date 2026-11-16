# V12 — sculpted ribbon lamp, appearance revision

Open [Ribbon-Lamp-V12-Sculpted.blend](Ribbon-Lamp-V12-Sculpted.blend). This rebuild replaces the V11 stacked paths with independently drawn three-dimensional edge rails. It follows the high left crest, broad right-hand fold and rising lower sweep of the approved concepts. All earlier projects are retained.

The scene contains the lamp alone, with no ceiling or room geometry. Three continuous ivory skins have long shallow surface pleats. There is one central metal eye/stem and a compact cover as a mounting **envelope**. There are no separate exterior straps or support arms. The skin envelope is approximately **1,191 × 889 × 227 mm**. The maximum skin drop is about 227 mm from the working Z datum; the eye adds about 33 mm above that datum. This is deeper than the earlier 160 mm working target to accommodate the fuller folds. Final installation clearance remains to be settled.

## Review the actual Blender geometry

- [Lamp alone, angled underside](01-Lamp-alone.png)
- [Directly below](02-Underside.png)
- [Low side](03-Low-side.png)
- [Rear, showing the single mounting eye](04-Rear-hook.png)
- [Neutral illumination, for judging shape](05-Neutral-shape.png)

These are renders of the saved Blender model. The two approved AI concept images are packed into the project as references. They are visual targets, not calibrated orthographic drawings. The model has larger openings and a different light distribution than those images; exact appearance has not been approved.

## What is modeled and what is still open

The A, B and C skins are separate closed solids. Nominal 1.6 mm thickness is measured along the smooth underlying sheet normal; both sides carry the shallow pleat displacement. Local nesting adjustments provide geometric separation while retaining the broad crests and twists. Editable source edge rails are hidden in a labelled collection, and the generation script is embedded in the project. The source rails precede the local clearance adjustments and are not live deformers.

Three 80 × 8 mm area-light proxies indicate candidate light locations inside selected bends. Their render energy is an artistic preview, not an electrical power specification. LED packages, opaque baffles, heat spreaders, wire channels and connector access have **not** been fitted to this new geometry. The lit views do not establish hardware concealment or measured diffusion.

The single eye, stem, plate and cover reserve the central mounting location. **The skins are not yet mechanically attached to that mount.** Integral root seats and inter-ribbon capture joints must be engineered into these new curves. The visible form is the present milestone. No working suspension or print-ready assembly is claimed.

## Geometry checks

[Intersection-check.json](Intersection-check.json) records zero non-manifold edges, zero detected non-adjacent self-intersections, and zero pairwise triangle intersections for the three final skins. These checks cover the skins only; they do not verify minimum normal thickness, load capacity, assembly access, LED concealment, heat, sag or print orientation.

There are no V12 production STLs. Earlier V09/V10 print packages do not fit this revised form. After visual review, design the concealed centre capture and mating overlaps, then the selected LED pockets and continuous wiring, then staggered panel divisions for the printer. Preserve the unbroken broad faces through this work.

Source: [build_v12_sculpted.py](../scripts/build_v12_sculpted.py). Checks: [check_v12_sculpted.py](../scripts/check_v12_sculpted.py).
