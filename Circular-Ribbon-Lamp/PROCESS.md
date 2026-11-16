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

## 14 — V08: full-size seam and upward bounce test, 5 November 2026

**Source and build:** Kept V07 as the full-shade checkpoint and added the new underside reference to the [V08 Blender copy](prototype-v08/Ribbon-V08-fold-prototype.blend). Blender Python extracted two adjacent W01 sectors around row 294. It added two matching back-side splice plates with a nominal adhesive gap and a separately supported opaque aluminum LED trough opening toward a white bounce board. The trough and board are bench hardware. A viewport-only draft cut overlay in the V07 context scene shows 33 potential pieces and their scale. [Prototype notes and exports](prototype-v08/README.md)

**Media:** [Actual Blender-window review](process/videos/14-v08-fold-prototype.mp4), 8.55 s with one video track and no audio. It shows the assembled prototype in the real Blender viewport after script-driven construction. [Decoded viewport frame](process/stills/14-v08-fold-prototype/window-2s.png), [lit room-side render](prototype-v08/v08-bounce-room-side.png) and [rear assembly render](prototype-v08/v08-rear-assembly.png).

**Checks and next step:** Four exported closed single-part STLs pass Blender topology, self-intersection and pairwise intersection checks and Snapmaker Orca STL inspection. Snapmaker Orca CLI exited while loading process settings, so toolpath review remains open. The trough blocks all 8,640 sampled direct rays below or level with the LED. The lit sample shows dark hardware shadows and a visible seam. Most draft cuts are exposed directly below. Build and test a real overlapping pair with the joint and light channel outside the exposed panel's light path before releasing the full shade. [Geometry check](prototype-v08/geometry-check.json) · [Draft cut map](prototype-v08/draft-cut-map.json)

## 15 — V09: complete underside reconstruction and print set, 5 November 2026

**Geometry:** The user asked for the full lamp with the supplied underside composition. Traced four separate ripple bands around a plain centre cover and inferred their depths from the single view. The completed shade is about 1,194 × 934 mm in plan with a 298 mm maximum ceiling drop. Retained the single central attachment. Divided every band into numbered parts with matched rear splices and added ten rear mounting pads. [Full Blender model](full-lamp-v09/Ribbon-Lamp-V09-Full.blend) · [Panel map](full-lamp-v09/Panel-map.svg)

**Lighting:** Two 100 mm COB runs and one 200 mm run face upward from aluminum channels behind selected folds. Their three low-voltage pairs follow hollow branch routes back to one central parallel connection. Iterated the channel lengths, mounting depths and lower branch after the first angled render exposed hardware. [Wiring layout](full-lamp-v09/Wiring-map.svg)

**Review:** [Lit underside](full-lamp-v09/01-Directly-below-lit.png), [angled render](full-lamp-v09/02-Oblique-lit.png), and [rear service render](full-lamp-v09/04-Service-side.png). [Live Blender viewport recording](process/videos/15-v09-full-lamp.mp4) shows the first assembled V09 checkpoint after the background script build. Verified a 9.63-second video with no audio. [Decoded frame](process/stills/15-v09-full-lamp/window-2s.png). Final routing changes are represented in the Blender file and renders.

**Verification:** The 75 printable solids pass closure, connectivity, non-adjacent self-intersection and printed pairwise intersection checks. The modeled metal and optical housings clear the shade. Direct LED rays are shielded in the sampled hemisphere. Both room cameras pass wire and channel first-hit screening, with a few carrier hits through gaps. The OrcaSlicer 2.4.2 output is packaged as editable Kobra S1 Max projects, with the machine G-code removed. Bench checks are still needed for appearance, temperature, joints and overhead retention. [Geometry](full-lamp-v09/Build-map.json) · [View check](full-lamp-v09/View-check.json) · [Slicer report](full-lamp-v09/Slicer-check.json)

## 16 — V10: three integral ribbons and centre-only hardware, 5 November 2026

**User direction:** The previous underside composition was accepted. Remove its tight lower-right curl and the extra pieces that support or join the curves. Because the ceiling is low, check the new model from shallow angles.

**Model:** Started from the V09 ribbon traces. Kept the diagonal sweep, upper-left arch and lower roll and lowered the maximum drop from 298 mm to 160 mm. Replaced separate splices with 12 mm half-laps that are part of the 19 panels. Added two integral inter-ribbon contact lands and four mounting positions within a Ø210 mm central canopy. The A and C panels share two central fastener stacks. There are no supports, lights or wires outside the centre footprint. Three 100 mm upward COB runs connect to one splitter inside the centre. [Blender project](full-lamp-v10/Ribbon-Lamp-V10-Integral.blend) · [Joint section](full-lamp-v10/Joint-detail.svg)

**Review:** [Directly below](full-lamp-v10/01-Below.png), [low side](full-lamp-v10/02-Low-side.png), and [opposite low angle](full-lamp-v10/03-Opposite-low-side.png). [Real Blender viewport review](process/videos/16-v10-integral-ribbons.mp4) after script-driven construction, verified at 9.14 seconds with one video track and no audio. [Decoded frame](process/stills/16-v10-integral-ribbons/window-2s.png).

**Validation:** The 20 printed solids pass the topology, self-intersection and assembly intersection checks. In the camera sampling, the LED channels and wiring remain screened. A few shallow-angle rays reach central fasteners through pass-throughs. The seams and centrally weighted glow remain visible in the renders. Verify the real joints, heat, sag and overhead retention on the bench. [Build map](full-lamp-v10/Build-map.json) · [View check](full-lamp-v10/View-check.json) · [Print and assembly guide](full-lamp-v10/README.md)

## 17 — V11 concept approval and planning

The user approved the low-angle concept showing light coming from selected bends and asked to settle the asymmetric design, then plan the light pockets, wiring and staggered print divisions before modeling. Retained the [approved image](references/v11-approved-fold-light-concept.png) and recorded three candidate pockets, a common centre connection, deliberate ripple texture, and a working 320 mm oriented part envelope for the Kobra S1 Max. Pocket sizes and the final cut map remain open for the optical sample and slicer checks. [V11 design and development order](PLAN.md#v11-design-baseline-and-development-order)

## 18 — V11 broad-ribbon appearance approved and layout planning

The user approved the new [low-angle](references/v11-approved-broad-ribbons-side.png) and [underside](references/v11-approved-broad-ribbons-below.png) concepts, then requested the hidden support, light and joint plan. Assigned three separate routes to the same centre plate, a primary right nesting overlap and a candidate left bearing overlap. Reserved three optional short light pockets with wire pairs behind their own ribbons and documented staggered split zones. The candidate map is an overlay for planning. Seat fit, real cross sections, wiring clearances, part counts and physical retention remain open. [V11 support, lighting and split plan](PLAN.md#v11-support-lighting-and-split-plan)

## 19 — V11 first Blender development checkpoint

**Built:** Reconstructed three broad, continuous ribbon meshes as the first CAD layout from the approved concepts. Packed both approved images and retained the generating path stations. The working envelope is 1,242 × 1,071 mm with a 159 mm drop. Measured a real A/B right overlap and placed one short, shielded LED envelope between the facing folds. Added a separate full-size bench scene with a captive rail, recessed socket, integral end stop and a wire groove. [Blender file](development-v11/Ribbon-Lamp-V11-Development.blend) · [Development notes](development-v11/README.md)

**Checks:** Three closed skins with zero detected self and pairwise intersections. The trial LED was screened at the four sampled room directions, and 2,700 sampled direct source rays at or below horizontal were blocked. The bench joint passed 30 sampled axial insertion positions, and its captive lips intersected the attempted upward escape. The back-out keeper, centre seats, continuous wire runs and final print divisions remain open. The shape needs another pass against the approved images. [Check results](development-v11/Development-checks.json)

**Review media:** [Underside](development-v11/01-Underside.png) · [Low angle](development-v11/02-Low-angle.png) · [Joint bench](development-v11/03-Right-joint-bench.png) · [End-on joint section](development-v11/04-Keyed-end-section.png). The [Blender-only recording](process/videos/17-v11-development.mp4) shows the actual saved model in the live viewport after the scripted build. Verified 9.56 seconds with no audio. [Decoded frame](process/stills/17-v11-development/window-2s.png)

## 20 — V11 rolled curves and recessed cover, 6 November 2026

**Changed:** The user identified the missing cross-width roll in the initial Blender layout. Developed a separate rolled revision with deeper turns at the left, right and lower bands. Added localized returns at the lips and raised the centre cover behind the front folds. The generator constrains clearance near actual projected overlaps and lets the ends roll more freely. Retained the initial development file as the previous checkpoint. [Rolled Blender file](development-v11-rolled/Ribbon-Lamp-V11-Rolled.blend) · [Development notes](development-v11-rolled/README.md)

**Checks:** The selected right section increased from 35 mm to 121 mm of cross-width depth. The three shells pass self, pairwise and canopy intersection checks. Repositioned the trial LED within the rolled folds. Three sampled camera sweeps found zero first hits on the housing or tape. The current render shows a soft hardware shadow. The overlap still needs the integrated captive joint, centre seats, final loom and panel division. [Geometry and light checks](development-v11-rolled/Development-checks.json) · [Section and camera checks](development-v11-rolled/Room-view-check.json)

**Review:** [Room angle](development-v11-rolled/05-Room-angle.png) · [Low side](development-v11-rolled/02-Low-angle.png) · [Underside](development-v11-rolled/01-Underside.png). The [actual Blender viewport recording](process/videos/18-v11-rolled-ribbons.mp4) shows the saved revision after the scripted build. Verified 9.52 seconds, one video track and no audio. [Decoded frame](process/stills/18-v11-rolled-ribbons/window-2s.png)

## 21 — V12: reconstruct the broad folds, lamp alone, 6 November 2026

**User correction:** V11 still looked like stacked bands and missed the approved concept's curviness. The user requested a fix, with the lamp alone, no roof, and one central hook. The previous claim of improved reference fidelity was too strong. Appearance remains subject to review.

**Rebuilt:** Created independent 3D outer and inner edge rails for each ribbon instead of extending the V11 centreline blockout. The broad left crest, large right roll and rising lower sweep determine the whole surface. Rounded the lower-right return, moved the narrow rear return farther behind the broad crossing face, and preserved shallow continuous pleats. Local smooth depth adjustments resolve actual overlap regions. There is no ceiling or room mesh. A single metal eye/stem, compact plate and cover reserve the central mounting location. [Blender checkpoint](development-v12/Ribbon-Lamp-V12-Sculpted.blend) · [Source](scripts/build_v12_sculpted.py)

**Scope:** The skin envelope is approximately 1,191 × 889 × 227 mm. The fuller folds exceed the previous 160 mm working depth target; installation clearance and visual acceptance are open. The central mount is an envelope: the skins still require integral roots and mechanically captured joints to connect to it. Three bend lights are optical proxies only. Actual LED packages, shielding, heat spreading, wire routing, structural capture and print segmentation have not been fitted to V12. No V12 production print set is released.

**Checks:** Initial independent rails folded through themselves at tight returns; reparameterized those returns and adjusted local nesting. Offsetting thickness along the fine pleat normals also caused local self-intersections. The final skins use the smooth underlying sheet normals for thickness and carry the same relief on both faces. The three final skins have zero non-manifold edges, zero detected non-adjacent self-intersections and zero pairwise triangle intersections. These are skin checks, not a test of suspension, minimum wall thickness, concealment or thermal performance. [Results](development-v12/Intersection-check.json)

**Actual model review:** [Angled underside](development-v12/01-Lamp-alone.png) · [Below](development-v12/02-Underside.png) · [Low side](development-v12/03-Low-side.png) · [Rear hook](development-v12/04-Rear-hook.png) · [Neutral shape](development-v12/05-Neutral-shape.png). These are Blender renders, with no generative image substitution. The model's openings and light distribution still differ from the approved concept. [Development notes](development-v12/README.md)

**Process capture:** [19 — initial V12 viewport](process/videos/19-v12-sculpted-ribbons.mp4) is a verified 9.36-second Blender-window recording before the final thickness-offset repair. [20 — checked V12 viewport](process/videos/20-v12-checked-shape.mp4) records the reloaded final geometry. Both are actual project-window captures after scripted modeling, not recordings of manual construction. No microphone or system audio is captured. [Final decoded frame](process/stills/20-v12-checked-shape/window-2s.png)

## 22 — V13: dimension the right fold, 6 November 2026

The right ribbon now follows a measured 239.6 mm approach that departs from its end-to-end chord by at most 4.2 mm. Its width increases from 130 to 165 mm and holds at 165 mm through a 120° turn. A 110 mm centreline radius governs the core in plan. Each end has a 36 mm curvature ramp, bringing the total curved run to 266.3 mm in plan. The ribbon banks from −21° to +41° through the turn, then tapers toward the overlap. The trial makes the right return broader and closes some of the gap visible from the side. Local clearances for the adjacent skins were recalculated. [Blender checkpoint](development-v13/Ribbon-Lamp-V13-Controlled-Fold.blend) · [Fold source](scripts/v13_right_fold.py) · [Measured geometry](development-v13/Geometry-review.json)

The three skins have zero non-manifold edges and zero detected self or pairwise intersections. The skin envelope is about 1,191 × 889 × 214 mm, with its lowest point 218 mm below the working datum. The hook connections, LED hardware and print divisions remain open. [Mesh checks](development-v13/Intersection-check.json) · [V13 side](development-v13/03-Low-side.png) · [V12 side](development-v12/03-Low-side.png) · [V13 underside](development-v13/02-Underside.png)

The 9.48-second recording shows the saved V13 model in the live Blender viewport after the scripted build. It has one video track and no audio. [Viewport capture](process/videos/21-v13-controlled-right-fold.mp4) · [Decoded frame](process/stills/21-v13-controlled-right-fold/window-2s.png)

## 23 — First-ribbon harmony calculation, 6 November 2026

The user identified residual waviness and asked for straight runs with consistent tight bends and a route between real attachment locations. Calculated one 165 mm wide trial ribbon with a 491 mm outbound leg, a 196 mm eased turn around a 52 mm core radius and a 490 mm straight return. The 190° sweep brings both seats back to the shared hub. The bend plane inclination gives a calculated depth of about 158 mm with nominal skin thickness. This step produced a dimensioned sketch and seat coordinates for review. The last Blender checkpoint is V13. [Sketch](process/stills/22-first-ribbon-math.png) · [Calculation](PLAN.md#earlier-single-return-calculation)

## 24 — Reference measurements after rejecting radial layout, 6 November 2026

The three-ribbon radial calculation fit six provisional seats within one hub and cleared the sampled skin intersections. Its outline spread into three separate spokes, which missed the reference. The user asked to return to the image. Archived that calculation and mapped the visible runs, turn locations and outline directly from the approved underside view. The mapped face crossing and tuck determined the next geometry. [Reference map](harmony-plan/Reference-map.png) · [Current calculations](harmony-plan/Full-calculation-v01.md) · [Discarded radial study](harmony-plan/discarded-radial-study/Assembly-layout.png)

## 25 — Three-ribbon harmony, mass and support calculation V01, 6 November 2026

**Direction:** The user asked for independent agent calculations for the full ribbon design, mass, and support before moving to the next modeling stage. The calculation follows the approved crossing composition. It does not use the rejected spoke arrangement and adds no Blender geometry.

**Reference geometry:** At a 1,200 mm image width, the three projected visible chords are A 280 mm at −3.8°, B 292 mm at −9.1°, and C 392 mm at +32.6°. A/B remain almost parallel while C crosses diagonally. The image outline is about 1,200 × 894 mm; a local outer-lobe extension of 78 mm at each end of the short direction gives a 1,200 × 1,050 mm working footprint. Candidate turns use 35 mm linear-curvature shoulders: A/C 150° around R120 mm and B 165° around R125 mm, giving 349 / 395 / 349 mm turn lengths and 35 mm inner-edge radii. Route budgets are estimated at 1.9 / 1.8 / 2.0 m; projected chords and hand-marked folds do not determine complete 3D routes.

**Mass:** Three path-times-mean-width estimates yield 0.933 m² of skin and 1.896 kg at 1.6 mm PETG, using the nominal 1.27 g/cm³ density in the cited Prusament datasheet. Two continuous 12 × 1.6 mm integral rear returns over the estimated 5.7 m route add 0.278 kg. Laps, captured seats and keys, LED hardware, and the central metal hub bring the estimated assembly to 2.70–3.17 kg without an onboard driver, or 2.80–3.42 kg with one. A 4.0 kg working budget is used for load screening.

**Support cross-check:** For a 4 kg screen mass, static load is 39.2 N and the selected 5× bench screen is 196 N. Six equal roots would carry 32.7 N each at that screen load, but the design does not rely on equal sharing. Candidate root-seat test capacity is 300 N each. The beam check uses a 1.6 mm face with two 12 × 1.6 mm rear webs, an assumed effective modulus of 1.5 GPa and positive simple supports. The first independent cross-section pass mislocated the web centroid and returned I=1,730 mm⁴; a second arithmetic review corrected the section to I=2,074.8 mm⁴ for a 170 mm face and 2,042.7 mm⁴ for a 150 mm face. The updated model estimates 1.18–1.20 mm static sag over a 450 mm span under the deliberately uniform full-mass load, or about 5.9–6.0 mm at 5×. A 500 mm cantilever is about 17 mm static, showing why positive hidden overlap seats matter. This straight-beam comparison excludes twisting, creep, temperature, joint flexibility, and print anisotropy.

**Print and lighting plan:** Use 23–25 parts with 240–260 mm net panel advance and 20 mm integral laps within a 320 mm working box inside the Kobra S1 Max's manufacturer-listed 350 mm volume. Since each ribbon is an open root-to-root path, that means 20–22 panel-to-panel laps. Reserve three approximately 100 mm hidden COB pockets, one in each selected fold, and route three wire pairs through provisional 6 × 4 mm channels to one central connection. At 24 V and 9.6 W/m, the example 300 mm of tape draws 2.88 W / 0.12 A; actual LED hardware remains unselected.

**Saved calculation:** [Full report](harmony-plan/Full-calculation-v01.md) · [Reproducible calculator](harmony-plan/calculate_candidate.py) · [Machine-readable outputs](harmony-plan/candidate-calculations.json) · [Updated reference plan](PLAN.md#current-design-plan--harmony-calculations-v01). The calculation and formulas were independently cross-checked. No Blender geometry or recording was created for this math-only step; V13 remains the last model. A 3D blockout, actual slicer volumes, material selection, and physical joint/retention/thermal tests remain open.

## 26 — V14: circular ribbon knot with hidden LEDs, 16 November 2026

**Direction:** The user supplied two new references, a long ribbon lamp and a circular one, and asked for the circular look, built in Blender, with hidden LEDs and a very clean finish. This moves the project back to the model stage.

**Built:** The lamp is now one continuous closed band on a flattened (2,5) torus-knot path, with 5 outer lobes, 5 inner lobes and 10 crossings, around a single Ø304 × 130 mm centre drum. The width direction is set square to the line between the two strands at each angle, so the band stands as a wall in the lobes and lies flat at the crossings. It cannot hit itself. The top edge is level 21 mm below the ceiling, the grade between crossings is controlled (28° maximum), and 22 continuous grooves cover the faces. [Blender checkpoint](development-v14/Ribbon-Lamp-V14-Circular-Knot.blend) · [Source](scripts/build_v14_circular_knot.py) · [Notes](development-v14/README.md)

**Lighting:** Five upward channels on the outer-lobe crests hold 1.06 m of COB strip. Each opening leans 35° toward the centre. The drum base is an opal diffuser. A sight-line test cast 12,483 rays from 219 room eye positions, and none reaches an LED. The first attempts failed this test. Open, concave channel end caps let rays in, and channels on steep edges could be seen lengthwise. Solid end walls, openings that face straight up, and a 15° grade limit fixed it.

**Checks:** Zero self-intersections and zero non-manifold edges. The minimum clearance between separate parts of the band is about 32 mm. The skin envelope is about 1,066 × 1,046 × 279 mm. The skin is 0.81 m², about 1.85 kg in PETG. [Checks](development-v14/Checks.json)

**Renders:** [Below](development-v14/01-From-below.png) · [Room view](development-v14/02-Room-view.png) · [Oblique](development-v14/03-Oblique-below.png) · [Centre](development-v14/04-Centre-detail.png) · [Shape unlit](development-v14/05-Shape-unlit.png). These are Blender Cycles renders of the actual model.

**Open:** The 279 mm depth needs review. Seat clips, sag at the flat crossings, wire routes, real LED profile and print segmentation are not done. From below the form reads as a regular 5-lobe flower, which is more ordered than the reference. No viewport recording was made because the build and renders ran in Blender background mode.

## 27 — V15: broad rolling ribbon, 16 November 2026

**Direction:** The user reviewed V14 and said they expected the main reference look (broad flowing ribbons, low profile, small ceiling disc) but "a bit round" and unusual. V14's narrow upright band was the wrong character.

**Built:** One continuous band 175–252 mm wide on a (2,3) knot path: three large irregular outer loops, three inner loops under a Ø240 × 32 mm ceiling disc, three crossings. The band lies flat at crossings, banks up to 60° at the outer loops and rolls with an S-twist through each loop. Three clear posts carry it from the disc. [Blender checkpoint](development-v15/Ribbon-Lamp-V15-Broad-Ribbon.blend) · [Source](scripts/build_v15_broad_ribbon.py) · [Notes](development-v15/README.md)

**Problems found on the way:** The first twist rule tilted the band into the other strand near crossings. Bank and twist now start only once the two strands are apart in plan, measured as true plan distance, and the twist direction follows the over/under order. Cross-slope is measured square to the path. A centre-line LED channel showed through the band as a dark line, so it moved to the inner edge. The LED channel was first built on the visible underside by a sign error; fixed.

**Checks:** Zero self-intersections, zero non-manifold edges, 12.5 mm minimum clearance, about 1,201 × 1,000 × 223 mm, 0.957 m², about 2.19 kg PETG. LED sight-line test: 416,875 rays from 725 eye positions, no tested LED station visible; 2.79 m of strip kept. [Checks](development-v15/Checks.json)

**Renders:** [Room view](development-v15/01-Room-view.png) · [Below](development-v15/02-From-below.png) · [Oblique](development-v15/03-Oblique-below.png) · [Close fold](development-v15/04-Close-fold.png) · [Shape unlit](development-v15/05-Shape-unlit.png). Blender Cycles renders of the actual model.

**Open:** User review of the shape; depth 223 mm; sag at 12.5 mm clearance; post seats, wiring, LED hardware and print segmentation. No viewport recording (background build).

## 28 — V16: three-layer broad ribbon, 16 November 2026

**Direction:** The user reviewed V15 and asked for more ribbon layers.

**Built:** The band now follows a (3,4) knot path, three times round the centre, so three strands are layered at every plan direction: four outer loops, four inner loops, eight crossings. Band 142–205 mm wide, 6.79 m long. When two strands cross, the third is far away radially, which keeps the layers apart. A Ø200 × 32 mm ceiling disc and four clear posts carry it. [Blender checkpoint](development-v16/Ribbon-Lamp-V16-Layered-Ribbon.blend) · [Source](scripts/build_v16_layered_ribbon.py) · [Notes](development-v16/README.md)

**Fix on the way:** The band edge overlapped the first Ø240 disc by 1.5 mm at its rim. The disc is now Ø200, leaving a 5.4 mm gap.

**Checks:** Zero self-intersections, zero non-manifold edges, 25.6 mm minimum clearance, about 1,205 × 1,165 × 182 mm, 1.172 m², about 2.68 kg PETG. LED sight-line test: 555,350 rays from 725 eye positions, no tested LED station visible; 4.32 m of strip kept. [Checks](development-v16/Checks.json)

**Renders:** [Room view](development-v16/01-Room-view.png) · [Below](development-v16/02-From-below.png) · [Oblique](development-v16/03-Oblique-below.png) · [Close fold](development-v16/04-Close-fold.png) · [Shape unlit](development-v16/05-Shape-unlit.png). Blender Cycles renders of the actual model.

**Open:** User review; pinwheel reading from directly below; 44° band slope near inner loops; post seats, wiring, LED hardware, sag and print segmentation. No viewport recording (background build).

## 29 — V17: Borromean ribbon lamp with a full print set, 16 November 2026

**Direction:** The user rejected V14–V16. They did not match the reference from the side, they had no print plan, and the user asked for a premium product with clean, deliberate curves, broad areas, a mathematical idea and a "wow factor".

**Design:** Three ellipse-plan ribbon rings are woven in the Borromean order (A over B, B over C, C over A). Each ring is a Möbius band with three evenly spaced half-twists on its free outer arc. Ring sizes step 1 : 0.9 : 0.81. Width is constant through the twists and broad where the ribbons lie flat. A constrained solver chooses the smoothest periodic-spline heights that keep the woven layers at least 18 mm apart inside a 22–153 mm depth band. [Blender checkpoint](development-v17/Ribbon-Lamp-V17-Borromean.blend) · [Notes](development-v17/README.md)

**Iterations:** Fixed-level and Fourier height rules collided where the broad ribbons overlap. A small spot covered by all three rings made the cyclic order impossible, so the centre was slimmed to 105 mm. The first solver pressed everything against the ceiling and flattened the look, so it now tracks the designed over/under heights. Crossing spacer posts showed from the side and were replaced by a hidden ceiling-white spider. A single slow twist per ring read as flat petals, five twists read as a frill, and three constant-width twists were chosen. Side-by-side comparisons with the reference drove each step.

**Checks:** Zero self or pairwise intersections, zero non-manifold edges, a 16.6 mm minimum gap, a 180 mm tightest bend radius, about 1,084 × 1,102 × 153 mm, and 1.97 kg of PETG skin. LED sight-line test: 195,025 rays from 725 eye positions, none reaching an LED; 2.42 m of strip. About 14% of sampled sight lines reach some part of a spider arm. [Checks](development-v17/Checks.json)

**Print set:** 25 pieces of 150–249 mm, all within the 320 mm working box, on 8 plates (3MF). 24 print standing on their edge so the layer lines run along the ribbon. Bonded 16 mm lap tabs, printed LED channels and M3 insert bosses are part of the pieces. All 25 STLs are closed shells. The plates were not slicer-verified, because only a Kobra S1 profile is installed. [Print map](development-v17/Print-map.json) · [Assembly map](development-v17/Assembly-map.png)

**Open:** Sag and joint-strength tests, wire routes, driver and spider detail design, softer inner glow than the reference, and slightly pointed twist ends at close range. No viewport recording was made (background build).
