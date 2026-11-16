# Current direction — V17 Borromean ribbon lamp, 16 November 2026

The user rejected V14–V16 (not like the reference from the side, no print plan) and asked for a premium product: clean deliberate curves, broad areas, mathematical "wow", and a complete print plan. Open `development-v17/Ribbon-Lamp-V17-Borromean.blend`, built by `scripts/build_v17_borromean.py` from `scripts/v17_geometry.py` (ellipse-plan rings, Borromean weave, Möbius half-twists, constrained spline height solver). The print set comes from `scripts/split_v17_print.py` (25 pieces, 8 plates) and `scripts/map_v17_assembly.py`. Never add random or noise terms. Compare renders with `references/design-reference.jpg` from the same angle. Keep the LEDs hidden per the sight-line test and zero intersections. Regenerate the print set after any shape change. Not yet accepted by the user.

# Previous direction — V16 layered broad ribbon, 16 November 2026

After V15 the user asked for more ribbon layers. Open `development-v16/Ribbon-Lamp-V16-Layered-Ribbon.blend`, built by `scripts/build_v16_layered_ribbon.py` from `scripts/v16_layered_geometry.py`: one band on a (3,4) knot path, three layers deep, under a Ø200 ceiling disc. Keep the broad band, the main-reference character (`references/design-reference.jpg`), LEDs hidden per the sight-line test, and zero self-intersections. The shape is not yet accepted; from below it reads as a four-armed pinwheel. Seats, wiring and print segmentation are open.

# Previous direction — V15 broad rolling ribbon, 16 November 2026

The user rejected V14's narrow upright band: they want the main reference look (`references/design-reference.jpg`: broad flowing ribbons, low profile, small ceiling disc) in a rounder, unusual outline. Open `development-v15/Ribbon-Lamp-V15-Broad-Ribbon.blend`, built by `scripts/build_v15_broad_ribbon.py` from `scripts/v15_broad_geometry.py`. Keep the band broad, the LEDs on the hidden top face and invisible in the sight-line test, and zero self-intersections. The shape is not yet accepted; it is simpler than the reference. Depth is 223 mm, minimum clearance 12.5 mm. Seats, wiring and print segmentation are open.

# Previous direction — V14 circular ribbon knot, 16 November 2026

The user supplied new references, including a circular rolling-ribbon lamp, and asked for a clean Blender model of it with hidden LEDs. This ends the "do not alter Blender" hold. Open `development-v14/Ribbon-Lamp-V14-Circular-Knot.blend`, built by `scripts/build_v14_circular_knot.py` from `scripts/v14_knot_geometry.py`. It is one continuous band on a flattened (2,5) knot path around a single Ø304 × 130 mm centre drum, and the drum is the only ceiling fixing. Keep the LEDs invisible from the room: rerun the sight-line test in Checks.json after any change. Keep zero self-intersections, and run `scripts/v14_clearance.py`. The user has not yet accepted the shape; it reads more regular than the reference. Depth (279 mm), seats, wiring and print segmentation are open.

# Previous direction — reference-led full calculation, 6 November 2026

The user rejected residual wiggles and the radial study, then explicitly asked for agents to independently calculate the geometry, mass and support. The cross-checked candidate set is documented in [Full-calculation-v01.md](harmony-plan/Full-calculation-v01.md), with reproducible inputs in `harmony-plan/calculate_candidate.py` and `harmony-plan/candidate-calculations.json`. Preserve the three crossing ribbons, nearly parallel A/B runs, diagonal C run, broad right fold in front, and lower sweep tucked behind. Keep long straight tangents, deliberate eased turns, no periodic waviness, no visible external straps, and no broad roof/deck. Use the specified 1,200 × 1,050 mm working outline, 180 mm shallow-profile cap, 1.6 mm face and provisional integral rear returns as assumptions only. Aim for 400–450 mm positive support bays and do not exceed 500 mm in the first screen. Align the CAD centre of mass to the centre mount; a freely pivoting single hook will rotate when those points are offset. **Do not alter Blender until the user steers to the model stage.** V13 remains the last modeled checkpoint; do not claim it matches the accepted reference.

# Previous direction — V13 controlled right fold, 6 November 2026

Open `development-v13/Ribbon-Lamp-V13-Controlled-Fold.blend` for the latest shape trial. The user asked to reason explicitly about the straight run, bend onset, radius and ribbon width. V13 applies that method to the large right return on B. Its 240 mm approach widens from 130 to 165 mm. The turn holds 165 mm across a 120° plan sweep with a 110 mm centreline radius at its core. Bank and height are controlled separately. Review the [side](development-v13/03-Low-side.png) and [underside](development-v13/02-Underside.png) before propagating this method to the other visible folds. Preserve V12 as the comparison checkpoint. The central hook remains provisional, with structural connections, LED pockets and print segmentation still open.

# Previous direction — V12 sculpted lamp, 6 November 2026

Open `development-v12/Ribbon-Lamp-V12-Sculpted.blend`. The user rejected the V11 rolled result as insufficiently curved and asked for a rebuild of the lamp alone, without the roof, using one central hook. Use the same approved V11 side and below concept images as appearance targets. V12 reconstructs the major surfaces from independent 3D edge rails, including the high left crest, large right roll and rising lower fold. There is no ceiling geometry. Keep the irregular outline, broad/medium ribbons, integral future joins and central-only attachment. The skin depth is now about 227 mm; the earlier 160 mm target was a working target, and the greater depth needs visual/room-clearance review. Read `development-v12/README.md` for the exact stage: three closed skins pass intersection checks, but the single central mounting eye is an envelope, not a connected load path. Lighting uses three optical proxies; actual hardware and wire channels remain open. Do not describe this as print-ready or structurally complete. Preserve prior revisions and process media.

# Historical direction — V11 design and planning

Use references/v11-approved-broad-ribbons-side.png and references/v11-approved-broad-ribbons-below.png as the approved appearance targets. Open development-v11-rolled/Ribbon-Lamp-V11-Rolled.blend for the latest curve pass. V10 is a construction reference. Keep the irregular asymmetric footprint, low profile, centre-only attachment and integral joins. The next lighting layout puts a few short LEDs inside screened ribbon bends, with wires returning to one connection behind the centre cover. This supersedes V10's central-only lighting layout. Follow the staged V11 plan in PLAN.md before building the next Blender revision.

# Current deliverable — V10 integral ribbons

Open full-lamp-v10/Ribbon-Lamp-V10-Integral.blend. The user removed the tight lower-right curl and rejected any separate support arms or joining straps. Keep three low-profile ribbons, integrated panel laps and overlap lands, and all mount, wiring and light hardware confined to the one centre canopy. See full-lamp-v10/README.md for the full print set and bench-test requirements. V09 and earlier descriptions below are historical wherever they conflict.

# Current deliverable — V09 full lamp

Open full-lamp-v09/Ribbon-Lamp-V09-Full.blend. The supplied underside picture governs the four new ribbon paths and the roughly 1,194 × 934 mm silhouette. Only the central canopy attaches to the ceiling. Three recessed LED runs feed one parallel connection through the hollow central-rooted branches. See full-lamp-v09/README.md for the complete print and assembly handoff. Preserve earlier studies, and use actual fit, optical and overhead retention tests before treating the project as an installable product.

# Definitive current constraint — V07

Only the **central canopy** may attach to the ceiling. The user explicitly rejected the large base. Open Circular-Ribbon-Cloud-v07-centre-mount.blend. No broad ceiling light deck, outer ceiling anchors or perimeter ceiling rail may be introduced. Three internal branches may carry the shade from the centre; they do not attach to the ceiling along their lengths. V06/b deck architecture and long deck-hanging tongues are superseded/rejected. Preserve surface ripples and washi character. Read current PLAN.md, lighting-v07/README.md and PROCESS.md. Earlier instructions below are history where they conflict.

# Project instructions

Read PLAN.md and inspect references/design-reference.jpg before modeling.

The user wants to document the process throughout this project. For each meaningful modeling or design step:
- Capture a short Blender viewport recording when capture is available. Record only the relevant project window/region, without microphone or system audio.
- Save clips in process/videos with sequential names, and save useful milestone screenshots in process/stills.
- Add an entry to PROCESS.md with what changed, why, the related .blend checkpoint, media links, validation, and remaining issues.
- Clearly distinguish live screen recordings, staged viewport walkthroughs, and rendered animations. Do not describe a reconstruction as live editing footage.
- Keep an editable checkpoint before major revisions. Do not discard earlier process media when iterating.
- If recording fails, document the limitation and preserve screenshots and notes. Do not claim a video was captured without verifying the file.

Maintain the current design: circular 1,200 mm footprint, translucent unpainted ribbon surfaces, close ceiling mount, warm ambient light, and future printed-shade product. Treat conceptual lighting and support geometry as provisional until physically validated.

Preserve the other lamp project outside this directory.

Latest user direction (4 November 2026): restore a stacked continuous-band cloud, not flower petals. Inner band carries the adjacent outer bands through small paired contact areas, with a traceable load path. Surface geometry is smooth: NO modeled fine ribs or wood grain. The selected texture character is soft white washi paper; intrinsic FDM layers must be handled through print design and real samples. A shader is mood visualization only. Latest scene: Circular-Ribbon-Cloud-v03.blend.

Latest superseding direction: user explicitly wants CEILING-CLOSE mounting, not a floating lamp. V04 removes separate clip objects and studies integral folded/stepped interlaps. The visible skin is about 20–200 mm below the ceiling. Latest file: Circular-Ribbon-Cloud-v04-flush.blend. Keep the washi finish and no modeled fine ribs. The 32 module STLs are FIT STUDIES without final seam joints; do not describe them as a production print package.

Latest checkpoint: **Circular-Ribbon-Cloud-v04a-clearance.blend**, with receiving relief added after V04 adjacent folds intersected. Four closed connected bands, no detected pairwise triangle intersections. V04a fit sectors are in print-study-v04a; final minimum clearances, skin thickness, retention and concealment remain unvalidated. Preserve V04 and all recordings.


Latest checkpoint (supersedes V04a): **Circular-Ribbon-Cloud-v06-light-deck.blend**. Read current PLAN.md and lighting-v06/README.md. Six independent wave meshes and integral folded mounting returns; separate 900 × 35 mm ceiling light deck with one 2.8 m perimeter strip and two 100 mm upward fill sections. Appearance gate has NOT passed: crowded centre, deck rim/return visibility, weak lower-wave glow. Continue toward reference rather than treating this checkpoint as an accepted design. Fine FDM lines remain excluded; broad surface ripples in V06 are provisional pending clarification. Guide curves are references, not live deformers. Final segmentation is not ready. The prototype-v06 overlap export failed its self-overlap check; do not print or describe it as ready. V04/a sectors do not apply. V06 capture was unavailable while the Mac was locked; its clip is a rendered stage review, not live editing footage.


Latest clarification and checkpoint: **Circular-Ribbon-Cloud-v06b-surface-ripples.blend**. The user explicitly means **surface ripples**, not missing smaller folded pieces. This supersedes prior pending interpretation and the blanket exclusion of intentional modeled ribs; fine FDM layer geometry is still excluded. V06b has approximately 6 mm starting pleat pitch, 0.5 mm source displacement amplitude, counts 28/25/20 main and 13/12/12 smaller bands. Removed coarse 30 mm ripples and extra camber/edge wobble. No extra ribbon pieces added. Mac unlocked; 09 is actual script-driven live Blender construction footage; 11 is the replacement Blender-window-only live viewport review. Use scripts/record_blender_window.swift for future captures; screen-region recording can accidentally capture another app when focus changes. Preserve both and prior media. Closure and pairwise checks pass for V06b, but the overall appearance/lighting and self-intersection/wall-thickness/manufacturing gates remain open. Read PLAN.md and PROCESS.md.
