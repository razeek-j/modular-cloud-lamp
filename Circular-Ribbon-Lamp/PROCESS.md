# Process journal

The user requests short videos and a record of meaningful modeling changes throughout development. This journal links the actual media and distinguishes live recordings from walkthroughs or rendered animations.

## 00 — Brief and reference

- Agreed direction: circular 1,200 mm shade with broad overlapping ribbons, fine ribs, and warm transmitted light.
- Created the [portable plan](PLAN.md) and preserved the [reference image](references/design-reference.jpg).
- Established a separate project folder. No earlier project geometry was reused.
- No modeling footage exists for the brief stage; modeling has not yet begun.

## Recording workflow

- Short clips for meaningful modeling steps, generally 20–60 seconds, rather than hours of idle footage.
- `process/videos/`: video files, numbered by stage and revision.
- `process/stills/`: milestone screenshots.
- `checkpoints/`: editable Blender checkpoints before major revisions.
- Record only Blender project content without audio. Describe script-driven edits accurately.
- Each completed stage entry records changes, reason, checkpoint, media, checks, and outstanding issues.

## 01 — First circular ribbon concept, 4 November 2026

**Capture type:** live Blender screen recording of actual script-driven edits. It is not a recording of manual mouse modeling and is not a rendered animation.

### Changes

- Started a new Blender project from the default scene, retaining the other lamp project separately.
- Created a flat outer ribbon, twisted it into a flowing band, and added middle and inner counterflow bands.
- Added shallow, deliberately modeled longitudinal ribs and an unapplied provisional 1.2 mm Solidify skin.
- Added a 230 mm canopy, provisional metal support arms and short LED rails, and artistic warm lighting.
- Packed the supplied reference into the .blend and embedded the project plan, journal, source script, and parameter data as text blocks.

### Media and checkpoints

- [Live build recording — original MOV](process/videos/01-live-concept-build.mov), approximately 55 seconds, no audio.
- [Live build recording — shareable MP4](process/videos/01-live-concept-build.mp4).
- [Viewport milestone](process/stills/01-layered-ribbon-viewport.png).
- [Warm ceiling concept render](renders/01-warm-ceiling-concept.png).
- [Unlit circular underside render](renders/02-unlit-circular-underside.png).
- [Flat ribbon checkpoint](checkpoints/01-flat-ribbon.blend).
- [Twisted outer ribbon checkpoint](checkpoints/02-twisted-ribbon.blend).
- [Layered silhouette checkpoint](checkpoints/03-layered-silhouette.blend).
- [Complete concept v01](Circular-Ribbon-Concept-v01.blend).

### Checks and current limitations

- [Geometry facts](checks/concept-report.json): maximum radial shade envelope approximately 1,199 mm diameter; shade reaches approximately 273 mm below ceiling origin; three editable ribbon bands.
- [Pairwise base-surface intersection check](checks/surface-intersections.json): zero detected crossings between the three ribbon base surfaces. This excludes skin thickness, self-intersection, support interference, and physical validation.
- The support and LED rails are indicative. Some are visible through the gaps; their concealment, attachments, and routing need further development.
- The shaded material and light setup are artistic approximations. Filament diffusion, wall thickness, heat, print splits, and load capacity remain unvalidated.
- Next: inspect the warm and unlit views, refine the silhouette and carrier concealment, then proceed to material/light samples once the appearance is accepted.

## 02 — Camera framing and underside inspection, 4 November 2026

**Capture type:** live screen recording of a script-driven presentation edit and viewport inspection. Ribbon geometry is unchanged in this step.

- The [initial attempt](process/videos/02a-console-input-error.mov) hit a console input error because Blender retained the prior command when returning from the viewport. No presentation edits ran in that attempt. The corrected recording below captures the actual changes.
- The first render exposed an edge of the presentation ceiling and cropped the underside composition.
- Expanded the ceiling backdrop and adjusted the underside camera distance and lens to fit the full circular envelope.
- Inspected the complete shade from directly below and returned to the oblique modeling view.
- [Live framing and inspection recording](process/videos/02-live-framing-and-inspection.mov), approximately 30 seconds, no audio.
- [Shareable MP4 of framing and inspection](process/videos/02-live-framing-and-inspection.mp4).
- Saved changes into [concept v01](Circular-Ribbon-Concept-v01.blend); the unrefined saved version is retained by Blender as `Circular-Ribbon-Concept-v01.blend1`.
- Rendered views are artistic appearance studies. Provisional support rails remain visible in gaps, and physical diffusion, fit, heat, and strength are still outstanding.

## Continuing work

1. Review the complete silhouette and compare its fold rhythm with the reference.
2. Refine concealment and placement of the provisional support and LED carriers.
3. Establish actual print segmentation and test the most demanding full-size overlap.
4. Continue the plan's physical optical and mechanical validation gates.

Preserve these recordings and add new journal entries and media for subsequent meaningful changes.

## 03 — V02 preliminary shape study, 4 November 2026

- Built [V02 work-in-progress](Circular-Ribbon-Concept-v02-WIP.blend) from a copy of V01, replacing its three rings with six open ribbon surfaces and six separate editable Bézier path references.
- [Initial warm render](renders/03-v02-wip-warm.png) exposes multiple ribbon ends and does not yet achieve the floating composition. It is a failed appearance checkpoint, not an accepted design.
- The guide curves are references only: editing a guide does not automatically regenerate its surface. The surfaces remain editable meshes.
- The former provisional support arms and LED rails were removed from the copy, but replacements, attachments and an actual load path have not been designed. Thus the preview does not establish structural concealment or feasibility.
- The composition was built with a background script. An attempted live viewport recording did not successfully open V02; [the recorded attempt](process/videos/03-v02-wip-viewport-inspection.mov) shows the earlier V01 scene and is not footage of V02 editing. No V02 build video is available for this step.
- Pending: redesign the six paths with concealed ends and staggered irregular crossings; connect each ribbon to a modeled carrier; inspect lit and unlit views from below and eight angles; analyze clearances, mass and attachment forces; create print divisions and prototype the overlap. Physical testing has not been performed.


## 04 — Stacked cloud and white washi direction, 4 November 2026

The user rejected the flower composition and clarified continuous stacked bands, supported from neighbour to neighbour at small concealed zones. They explicitly selected **soft washi paper** and asked that intrinsic FDM lines be considered instead of modeling fine surface ribs.

- Rebuilt four closed flowing bands with smooth skins and live Bezier Curve modifiers. Editing the path or its tilt now changes the actual band; each path is in the `V03 02 • EDITABLE PATHS` collection.
- Added an inner root ring/frame, three paired conceptual connection zones per adjacent-band interface, and short indicative low-voltage links. All hardware stays enabled in normal renders. Hardware sections and contact seating are provisional, not rated or assembly-ready.
- Added only a shader-level paper-grain mood preview. No fine rib, wood-grain, or layer-line geometry is added to the skin. Real texture depends on filament, orientation and toolpaths, and needs printed tests.
- The initial wider-band iteration crossed adjacent skins. Narrower spacing/width corrections removed detected pairwise intersections in the evaluated skins; [check results](checks/v03-intersections.json). This does not validate self-intersection or attachments.
- [Latest Blender study](Circular-Ribbon-Cloud-v03.blend), [warm room view](renders/04-v03-washi-warm.png), [unlit underside](renders/05-v03-washi-unlit.png).
- [Live build recording](process/videos/04-live-v03-stacked-cloud-build.mov): actual timed script-driven Blender construction, not manual mouse modeling. Background draft checks preceded this recorded build. Original MOV preserved; a shareable MP4 and decoded sample frames are also saved.
- [Geometry and support-zone report](checks/v03-report.json): approximately 1,198 mm maximum radial envelope, highest skin 81 mm below the ceiling and lowest 299 mm. Nominal transformed skin volume corresponds to approximately 1.58 kg at 1.27 g/cm³, excluding hardware and lighting. This is not a weighed print. The Solidify input is 1.2 mm before scene normalization; final manufacturing skins must be re-thickened uniformly after applying the final shape transforms.
- Pending: joint-seat details/retention, support concealment assessment, actual LED carriers and complete electrical routing, load/creep/temperature tests, seam/split design, and physical washi/print-texture samples. No print-ready claim.

- [Shareable V03 build video](process/videos/04-live-v03-stacked-cloud-build.mp4). Eight unlit oblique review views are saved as `renders/v03-review-00.png` through `07.png`, with all actual concept hardware enabled. The clean hero alone is not a concealment validation.


## 05 — Ceiling-close cloud with integrated overlapping returns, 4 November 2026

The user rejected visible clips and floating suspension, clarified **close against the ceiling**, and asked for overlapping construction and piece-by-piece printing. They invited a practical DIY enhancement without prescribing a steel pipe.

- Saved a separate [V04 Blender study](Circular-Ribbon-Cloud-v04-flush.blend), preserving V01–V03 and their recordings. Smooth skins are reshaped from the 81–299 mm depth range toward approximately **20–200 mm below the ceiling**.
- Removed the separate inter-band tabs and visible wire links. Built complementary folded shelves, with nominal 20 mm lap and 0.25 mm shelf clearance, and performed actual mesh unions into the parent/child bands. Widened the surrounding skin locally to read as an overlapping fold rather than adding a separate cover plate.
- The first prism/Boolean construction failed mesh checks, including loss of a band. Corrected the swept cross-section and manifold Boolean construction. A cover-plate attempt was rejected because it still read as clips from below. The final shape uses smoothly extended original skin around the interlap. Final checks are in [v04-mesh-check.json](checks/v04-mesh-check.json); geometry closure does not prove retention or strength.
- Added a shallow ceiling plate/inner frame study and a removable satin aluminum reflector behind inner folds. No electrical hardware SKU or driver fit has been selected; the light sources are still artistic previews.
- Derived a preliminary **32-piece division**: 3 inner, 7 second, 10 third and 12 outer sectors. Original sizing reserves an envelope under 310 mm before final joint features. [Print-study notes](print-study-v04/README.md) distinguish the geometric fit sectors from final manufacturing parts.
- Exported a small stepped-lap clearance pair, not a structural equivalent of the curved joints. It has no established locking or bonding method. No physical print has been made.
- [Warm view](renders/06-v04-flush-warm.png), [unlit underside](renders/07-v04-flush-unlit.png), [live script-driven construction recording](process/videos/05-live-v04-flush-overlap.mov). Background drafts preceded the recorded live Blender build. Preserve the MOV original and verify the MP4 after conversion.
- The [shareable V04 MP4](process/videos/05-live-v04-flush-overlap.mp4) was converted and verified at approximately 50 seconds, with decoded sample frames. Eight oblique unlit views and an [overview sheet](renders/v04-eight-view-review.jpg) are saved. These show that some return transitions still need concealment refinement.
- A subsequent pairwise check found intersections at all three adjacent-band interfaces (168, 132 and 151 intersecting triangle pairs). Thus V04's closed meshes did not establish assembly fit. See V04a below for the correction.
- Remaining: assess all-angle concealment and inter-band clearance, finish upper-side joint retention and root seating, develop actual seam joints on the fit sectors, select LEDs/carrier/driver, slice with the correct Kobra profile, and perform fit, heat, sag and load tests. Do not claim print/sales readiness from renders or manifold meshes.

## 06 — V04a receiving relief and export verification, 4 November 2026

**Capture type:** background Blender geometry refinement followed by a live viewport review. The review is not footage of the Boolean edits and is not manual modeling footage.

- Preserved V04 and saved [V04a](Circular-Ribbon-Cloud-v04a-clearance.blend). Cut receiving relief from the parent folds using neighbouring-band cutters with a nominal 0.50 mm normal offset. This is a geometric cutter offset, not a measured minimum clearance.
- A first 0.25 mm/manifold-solver attempt left a loose fragment and six triangle intersections. Switched to exact Boolean subtraction with 0.50 mm offset, removed a tiny 11-vertex trim fragment and closed one microscopic triangular Boolean pinhole. The final [refinement report](checks/v04-clearance-refinement.json) records these operations.
- All four resulting bands are single connected closed components with zero nonmanifold edges. All six pairwise band comparisons report zero intersecting triangle pairs. Self-intersection, minimum clearance, remaining wall thickness and load capacity are not established by these checks.
- Re-exported [32 fit-study sectors](print-study-v04a/README.md). Every export is closed and inside 320 mm per axis; largest dimension is approximately 302.7 mm. No final segment seam retention, support allowance or validated print orientation is included.
- [Warm V04a preview](renders/v04a-flush-warm.png), [unlit underside](renders/v04a-flush-unlit.png) and eight oblique unlit views `renders/v04a-review-00.png` through `07.png` were rendered with actual concept hardware enabled. Integral return transitions remain visible in some views; concealment is not accepted as complete.
- [Current geometry facts](checks/v04a-report.json): skin/return bounds remain 20–200 mm below the ceiling. Modeled volume at nominal 1.27 g/cm³ is approximately 1.40 kg, excluding frame, lighting and fasteners. This is an estimate, not a weighed print. The inherited 1.2 mm Solidify input does not establish a uniform final manufacturing wall after deformation.
- [Initial opening recording](process/videos/06-v04a-clearance-walkthrough.mov), approximately 30 seconds, primarily shows the file-opening interaction. It is preserved as an attempt, not the final review clip. Its MP4 conversion was verified.
- [V04a viewport review](process/videos/07-v04a-viewport-review.mp4), approximately 15 seconds, no audio; [original MOV](process/videos/07-v04a-viewport-review.mov) preserved. Decoded stills verify the displayed checkpoint.
- V04a was opened in the actual Blender application and verified by its window title and viewport. The current external plan, reference image, export notes and journal provide the handoff for other models.
- Next: refine visible return transitions; finish root seating and upper-side retention; re-establish uniform manufacturing walls and hidden segment seams; choose actual LEDs and test a demanding full-size partial assembly for finish, fit, light, sag and temperature. No physical testing or production print package is claimed.


## 08 — V05/V06: wave hierarchy, lighting and integral returns, 4 November 2026

**Capture:** actual script-driven Blender background modeling and rendering. The Mac was locked, so live viewport recording was unavailable. Earlier footage is preserved. [08-v06-rendered-stage-review.mp4](process/videos/08-v06-rendered-stage-review.mp4) is a rendered stage review assembled from actual model outputs, **not live editing or a screen recording**.

### Changes and rejected experiments

- Compared the original reference with V04/a. Identified missing smaller counter-waves and an undeveloped LED plan.
- V05 tried independent open wave sweeps, tightly rolled optical leaves and short straight LED pockets. Rejected exposed ends, excessive cup/tube forms, visible tray bars and dull surfaces. Preserved V05 project/checkpoints/renders.
- V06 combines three broad twisted sweeps and three smaller counter-waves. Provisional broad 30 mm surface undulations and a paper-grain shader were added; neither represents fine FDM layer geometry. Clarification on broad surface ripples versus folded pieces remains pending.
- Moved tape into a separate shallow ceiling deck. An eight-straight-section layout showed a stripe pattern through its cover and was rejected. The saved version uses one 2.8 m inward perimeter ring plus two 100 mm upward reflected fills. Modeled metal heat sleeves/rails, first mixing film, lower opal cover, low-voltage routes and central service driver/controller space.
- Replaced disconnected skin clips with continuous folded boundary returns on the actual wave meshes, reinforced toward nominal 3 mm. Added actual paired M3 clearances, receivers, carrier connections, diffuser slots and opaque slot collars. Separate rectangular ventilation slots were rejected in favor of continuous baffled shadow reveals.

### Saved work and media

- [V06 assembled project](Circular-Ribbon-Cloud-v06-light-deck.blend); [composition checkpoint](checkpoints/v06-composition.blend).
- [Composition stage](renders/v06-composition-stage.png); [service cutaway](renders/v06-light-deck-cutaway.png); [isolated folded-lap cutaway](renders/v06-integral-lap-cutaway.png). Cutaways deliberately remove surrounding parts for explanation; they are not concealment evidence.
- [Warm view](renders/v06-waves-warm.png); [unlit view](renders/v06-waves-unlit.png); [review sheet](renders/v06-review-contact-sheet.jpg). All physical supports remain enabled in these normal review views.
- [LED placement and component study](lighting-v06/README.md); [overlap export status](prototype-v06/README.md).

### Digital checks and limits

Six evaluated skins are each connected and closed with zero detected non-manifold edges. All 15 pairwise skin comparisons report zero intersections. The volume-derived skin/return estimate is 1.952 kg using nominal PETG density 1.27 g/cm³; metal, wiring, LEDs, driver and hardware are excluded. This is not a weighed mass or strength proof. See `checks/v06-assembly-check.json`.

Opaque source-ray screening from 42 sampled positions reports zero exposed inward emitting probes; the upward fill emitters have no front-facing underside probes. This does not establish diffuser glare, transmitted silhouettes or all-view concealment. See `checks/v06-source-visibility.json`. Light proxies are an uncalibrated 28% radiant equivalent; the shaders are not measured material data.

The exported outer overlap fits a 252 × 169 × 191 mm box but reports 241 nonadjacent triangle overlap candidates. It is **failed/quarantined**, despite closed edges. Self-intersection repair, wall-thickness evaluation, final segment joints, slicer validation, installed-load checks and thermal tests remain outstanding.

### Appearance gate

**Not passed.** The reference has clearer broad alternating waves and stronger transmitted glow. V06 remains crowded at the centre; folded returns and the deck rim are visible in some normal views, and the lower faces are too dull. Do not describe this as an accepted “wow” concept. Next shape work must simplify and open the centre, conceal those connections, and test the actual optical stack before final manufacturing exports. The original reference and explicit user feedback take priority over preserving this experimental silhouette.


## 09–11 — V06b: clarified surface ripples, 4 November 2026

**User clarification:** “Ripples across ribbon surfaces.” No additional folded pieces are required by that correction. “Mac is unlocked.” This resolves the previous pending surface question and recording blocker.

**Changes:** Replaced V06's coarse 30 mm surface undulations with shallow parallel pleats flowing along the ribbon twists. Main-band pleat counts: 28 / 25 / 20. Smaller-band counts: 13 / 12 / 12. Starting broad-band pitch is about 6 mm; source normal displacement amplitude is 0.5 mm before shape normalization. Fade at edges and narrow tips. Removed the added longitudinal 8 mm camber variation and 6 mm edge wobble that made the surfaces look crumpled. Increased across-width mesh resolution to 192 samples on main bands and 96 on shorter bands. This is intended design texture, not modeled FDM layer lines. Existing six paths and lighting architecture are retained; no new ribbon pieces added.

**Blender and capture:** Opened V06 in the unlocked desktop Blender, then executed the revision builder with timed construction stages in the actual viewport. [09-live-v06b-ripple-build.mp4](process/videos/09-live-v06b-ripple-build.mp4) is a verified approximately 55-second real screen recording of script-driven construction, without audio. The first save attempt hit an embedded-source filename mismatch after geometry construction; corrected the link and saved [Circular-Ribbon-Cloud-v06b-surface-ripples.blend](Circular-Ribbon-Cloud-v06b-surface-ripples.blend). The generator has that correction. A foreground-app change made the first review capture unsuitable. Removed the unintended generated foreground capture and its derived frames. [11-v06b-window-only-review.mp4](process/videos/11-v06b-window-only-review.mp4) replaces it: a true live recording restricted to the Blender project window using ScreenCaptureKit's desktop-independent window filter, with no microphone/system audio and no desktop fallback. The orbit/zoom actions are actual desktop controls. This is a viewport review, not a rendered animation or additional modeling. Overlays/gizmos are disabled; all physical supports remain enabled. Use `scripts/record_blender_window.swift` for future captures, because a screen-region capture can include another app when foreground focus changes.

**Media:** [Ripple detail](renders/v06b-surface-ripple-detail.png), [warm review](renders/v06b-waves-warm.png), [unlit review](renders/v06b-waves-unlit.png). Composition checkpoint: `checkpoints/v06b-composition.blend`. Source: `scripts/build_v06b_surface_ripples.py`, embedded in the saved project.

**Checks:** Six evaluated skins each remain one connected component with zero detected non-manifold edges. All 15 pairwise skin intersection comparisons report zero. Current radial diameter is about 1,199 mm and maximum drop about 279 mm. Nominal skin/return volume estimate: 1.999 kg at 1.27 g/cm³, excluding hardware/light engine. Opaque source-ray check still reports zero exposed emitting probes within its sampled scope. See `checks/v06b-assembly-check.json`, `checks/v06b-report.json`, `checks/v06b-source-visibility.json`. Rendering initially encountered a suffixed daylight name left by live rebuilding; the review scripts now locate that named light robustly. This did not change geometry.

**Limits:** Surface correction is implemented; overall aesthetic acceptance remains open. The centre is crowded, the deck rim/returns remain visible and lower folds receive weak light in the current optical preview. The V06 failed overlap export has not been reissued for V06b. Self-intersections within a skin, thickness, printed finish, retention, thermal behavior and load capacity still need validation. V06b is not print-ready. Earlier .blend files and all media remain preserved.


## 12–13 — V07: remove broad base, attach only at the centre

**User correction:** the large ceiling base is unacceptable. Only the middle part should attach to the ceiling. The V06 deck changed the design too much; that direction is rejected.

**Implemented:** Started from the actual V06b pre-deck ripple-skin checkpoint, preserving the earlier projects/media. Removed the entire 900 mm deck, perimeter LED ring, outer fixing grid and the long tongues connecting each ribbon to that deck. Retained only a compact Ø220 × 48 mm central canopy, central plate/hub and four provisional central fixing clearances. Added three internal carrier branches rooted at the centre, constrained to separate approximately 120° sectors. They follow upper-fold routes and have no outer ceiling attachment. Added paired back-side saddle/stud placement studies for all six ribbons. These pads are separate intersecting assembly studies, not final unioned printable joints.

**Lighting:** Twelve straight 100 mm modules at six selected backlighting stations, replacing the perimeter deck optics. Total nominal tape 1.2 m / 9.6 W / 0.40 A at 24 V. Modeled metal heat beds, opaque side/end lips, opal windows and paired wire routes from the centre. Existing driver/controller envelopes are only space reservations; current load requires hardware selection to be revisited. No arbitrary emission was added to the printed skins.

**Saved:** [Circular-Ribbon-Cloud-v07-centre-mount.blend](Circular-Ribbon-Cloud-v07-centre-mount.blend), source `scripts/build_v07_centre_mount.py`, and [current carrier/lighting notes](lighting-v07/README.md). Initial routing checkpoint preserved as `checkpoints/v07-first-centre-routing.blend` before separating branch sectors.

**Media:** [Initial centre-mount revision screen recording](process/videos/12-v07-centre-mount-revision.mp4), [latest V07 screen recording](process/videos/13-v07-current-review.mp4), [warm view](renders/v07-centre-warm.png), [unlit view](renders/v07-centre-unlit.png), [directly below](renders/v07-centre-below.png), [carrier-only cutaway](renders/v07-centre-carrier-cutaway.png). Recordings capture the actual Blender project window without audio; they are live revision/viewport reviews, not recordings of manual modeling. Geometry was authored through actual Blender Python. The cutaway explicitly removes skins/ceiling for explanation; all actual physical components remain enabled in normal images.

**Verification:** `checks/v07-centre-contact-check.json` tests that no modeled physical geometry contacts the ceiling outside the central footprint, no deck objects exist and no physical supports are hidden. `checks/v07-assembly-check.json` reports six connected closed bare skins, zero detected non-manifold edges and zero pairwise skin intersections. Their modeled volume estimates 1.789 kg at nominal PETG density 1.27 g/cm³, excluding pads and all other hardware. This is not a weighed mass, load proof or complete intersection test of the carrier assembly.

**Remaining:** The central-only architecture correction is implemented. Some optical cells/connections remain visible; overall reference match and glow are still not accepted. The 18 × 16 × 1.5 mm hollow branch envelopes are routing studies: bends/splices, material/sections, mounting capacity and deflection remain to be designed and tested. Pad union, final retention, assembly access, self-intersections, minimum thickness, print segmentation, temperature and sag are not validated. No production STL release. Do not solve those issues by reintroducing a large ceiling plate.
