# V07 — central ceiling attachment only

Open **[Circular-Ribbon-Cloud-v07-centre-mount.blend](Circular-Ribbon-Cloud-v07-centre-mount.blend)**. The broad ceiling deck and outer ceiling fixings are removed. Only the compact Ø220 mm centre canopy attaches to the ceiling. Three internal branches carry the rippled shade from that centre.

- [Current warm view](renders/v07-centre-warm.png), [unlit view](renders/v07-centre-unlit.png), [directly below](renders/v07-centre-below.png)
- [Carrier-only technical cutaway](renders/v07-centre-carrier-cutaway.png)
- [Latest live viewport recording](process/videos/13-v07-current-review.mp4)
- [Current mount and LED plan](lighting-v07/README.md), [portable plan with original reference](PLAN.md), [process journal](PROCESS.md)

The central-only correction is implemented. Internal carrier/LED housing concealment, attachment details, practical fabrication, thermal/load checks and production printing remain unresolved. The shade's designed surface ripples are retained. All previous models and valid process clips are preserved.

## Historical revisions below

# V06b — flowing surface ripples

Open **[Circular-Ribbon-Cloud-v06b-surface-ripples.blend](Circular-Ribbon-Cloud-v06b-surface-ripples.blend)**. This follows the clarification: the missing detail is ripples across the ribbon surfaces. Closely spaced shallow pleats replace V06's coarse waves; the large folds have cleaner edges/camber. No extra ribbon pieces were added.

- [Ripple close-up](renders/v06b-surface-ripple-detail.png), [warm view](renders/v06b-waves-warm.png), [unlit view](renders/v06b-waves-unlit.png)
- [Actual live script-driven build](process/videos/09-live-v06b-ripple-build.mp4)
- [Actual live viewport review](process/videos/11-v06b-window-only-review.mp4)
- [Updated plan with original reference](PLAN.md), [process journal](PROCESS.md), [LED arrangement](lighting-v06/README.md)

V06b is open in Blender. Surface detail is revised; overall composition, support concealment and transmitted glow are still unresolved. The historical overlap STL remains a failed draft. No final V06b print package is released.

## Earlier V06 checkpoint

# V06 — wave and ceiling-light-deck development study

Open **[Circular-Ribbon-Cloud-v06-light-deck.blend](Circular-Ribbon-Cloud-v06-light-deck.blend)** in Blender. Earlier projects and recordings remain intact.

- [Current warm view](renders/v06-waves-warm.png), [unlit view](renders/v06-waves-unlit.png), and [all-direction review](renders/v06-review-contact-sheet.jpg)
- [LED placement, component candidates and current limitations](lighting-v06/README.md)
- [Rendered stage review video — not live editing](process/videos/08-v06-rendered-stage-review.mp4)
- [Plan with original reference](PLAN.md), [process journal](PROCESS.md), and [continuation instructions](AGENTS.md)
- [Failed overlap export / do not print](prototype-v06/README.md)

The six waves, integral folded returns, carrier, wiring, 35 mm ceiling light deck and actual strip locations are modeled. The perimeter ring plus two reflected fill sections total 3.0 m / 24 W nominal. **The current visual concept is not accepted:** the centre is crowded, some mount returns and the deck edge are visible, and lower-wave illumination is weaker than the reference. This is a development checkpoint, not the finished design or a production print package.

The current rendered process clip substitutes for unavailable screen capture while the Mac was locked. It shows actual Blender outputs and explicitly identifies cutaways.

## Historical revisions below

These notes and linked fit exports apply only to their stated versions.

# Current revision: V04a ceiling-close cloud

Open **[Circular-Ribbon-Cloud-v04a-clearance.blend](Circular-Ribbon-Cloud-v04a-clearance.blend)**. This preserves V04's shape and adds receiving relief where neighbouring folds previously collided. All four bands are single closed components, with zero detected pairwise triangle intersections. This does not establish minimum clearance, wall thickness, retention or strength.

- [Latest warm preview](renders/v04a-flush-warm.png) and [unlit underside](renders/v04a-flush-unlit.png)
- [Current 32-piece fit studies](print-study-v04a/README.md)
- [Viewport review video](process/videos/07-v04a-viewport-review.mp4)
- [Plan with reference image](PLAN.md) and [process journal](PROCESS.md)

The highest skin is 20 mm below the ceiling and the lowest is 200 mm. Integral returns still need concealment refinement. The model is a design study, with final joints, lighting and physical testing outstanding.

## V04 source checkpoint

Open **[Circular-Ribbon-Cloud-v04-flush.blend](Circular-Ribbon-Cloud-v04-flush.blend)**. This follows the latest ceiling-close direction, replacing visible separate clips with integral folded overlap geometry and reducing the floating gap.

- [Warm ceiling preview](renders/06-v04-flush-warm.png)
- [Unlit underside](renders/07-v04-flush-unlit.png)
- [Piece-by-piece fit studies and lap test pair](print-study-v04/README.md)
- [Current plan](PLAN.md) and [process journal](PROCESS.md)

V04 skins/returns are evaluated mesh geometry; the earlier live V03 curve masters are retained, hidden, as references. Rebuilding V04 overwrites its current file. Keep manual edits in a new revision. No full production print/retention or electrical package has been validated.

The "wow" direction is continuous cloud folds and controlled warm light, with a removable concealed aluminum reflector as a DIY optical detail. The reflector is provisional and needs testing with the actual LED system.

## Earlier revision notes

# Circular cloud ceiling shade — current V03

Open **[Circular-Ribbon-Cloud-v03.blend](Circular-Ribbon-Cloud-v03.blend)** for the current stacked continuous-band study. V01 and the flower-like V02 remain as earlier checkpoints.

The user selected a **soft white washi-paper character**. Visible skins are smooth, without modeled fine ribs. Real printing layers will be addressed through curvature, consistent layer height, seam placement and orientation tests. The material shader illustrates the mood only.

- [Current warm view](renders/04-v03-washi-warm.png)
- [Current unlit underside](renders/05-v03-washi-unlit.png)
- [Live V03 build video](process/videos/04-live-v03-stacked-cloud-build.mp4)
- [Process journal and earlier checkpoints](PROCESS.md)
- [Current brief and development plan](PLAN.md)
- [Instructions for continuing models](AGENTS.md)

## Editing V03

Four ribbon meshes have live **Curve** modifiers linked to Bezier paths in `V03 02 • EDITABLE PATHS`. Reveal a path in the Outliner, edit its control points or tilt, and the associated smooth band follows it. The source generator is `scripts/build_v03_cloud.py` and is embedded in the scene. Regeneration replaces V03; preserve manual edits in a new version before running it.

The support concept is traceable: ceiling bracket → inner carrier ring → inner band → each adjacent outer band. Three provisional paired zones per interface resist rotation conceptually. These are placement studies, not validated joint seats or rated hardware. Some hardware remains visible; concealment and assembly need further work.

Read `checks/v03-report.json` and the intersection check. The shape is normalized to approximately 1.2 m circular envelope and 299 mm maximum drop. The Solidify input is 1.2 mm before normalization, so production geometry must receive a final uniform skin after shape transforms. LEDs, thermal behaviour, sag, fastening, print segmentation and real texture still require physical development and validation.

## Earlier work


Open **[Circular-Ribbon-Concept-v01.blend](Circular-Ribbon-Concept-v01.blend)** in Blender. It is the first editable concept at approximately 1,200 mm circular envelope, with a packed reference, ribbed ribbon surfaces, provisional canopy/support/light carriers, and review cameras.

- [Warm ceiling preview](renders/01-warm-ceiling-concept.png)
- [Complete unlit underside](renders/02-unlit-circular-underside.png)
- [55-second live build video](process/videos/01-live-concept-build.mp4)
- [30-second framing and inspection video](process/videos/02-live-framing-and-inspection.mp4)
- [Process journal and checkpoints](PROCESS.md)
- [Agreed design and development plan](PLAN.md)
- [Instructions for continuing models, including recording](AGENTS.md)

## Editing

The three ribbon objects are editable surface meshes with unapplied Solidify modifiers. The source parameters and generator are in `scripts/build_concept.py` and embedded Blender text blocks. The reference image is packed into the file and remains separately available in `references/`.

The source generator recreates the concept and writes the v01 file and early checkpoints. Preserve manual changes before rebuilding; change its output `ROOT` or use a separate copy for a new design revision. The timer-driven UI run is used for real screen recordings; a background rebuild uses `-- --batch` after the script argument. Read the source before running it.

Stage 1 appearance studies are complete enough for review. Support concealment, module splits, joints, real PETG diffusion, thermal performance, and mechanical retention remain to be developed and physically validated. The current file is not a print-ready or sales-ready model.
