# V11 Blender development

[Open the V11 project](Ribbon-Lamp-V11-Development.blend). It contains two scenes. The approved side and underside images are packed in the file. The three ribbon meshes are editable, and their generating centreline stations are included as a Blender text block and in the [source](../scripts/build_v11_development.py).

| Scene | What it contains |
| --- | --- |
| **01 | V11 three-ribbon layout** | Three continuous ripple skins, a centre-cover envelope, a sampled right overlap between A and B, and one modeled LED channel between those ribbons. |
| **02 | Full-size right joint bench** | A separate, full-scale cross-section study of a captive slide joint, the far-end stop, an adjacent LED bed and a recessed wire path. |

Use Blender’s Scene selector to switch between them. Choose **View → Cameras → Active Camera** to frame the bench detail. The source paths and overlap markers are in the guide collection. Reveal their eyes in the Outliner to inspect them.

## Shape and light

The working layout is **1,242 × 1,071 mm** with **159 mm maximum drop** and nominal 1.6 mm skins. The three loops are broader and shallower than the reference image’s rolled overlaps read in perspective. Their relative heights and edge roll are still open for refinement. The evaluated skins passed the closed-mesh, self-intersection and pairwise intersection checks.

The right overlap was sampled over a **66 × 26 mm** patch. The measured vertical gap ranged from **12.41 to 21.44 mm**, with about **17 mm** at the patch centre. A 100 mm LED fit envelope is placed farther along the bend between A and B, facing the opposite ribbon. The digital check screened all 120 sampled housing sightlines and blocked all 2,700 sampled direct emitter rays at or below horizontal. Light power and the PETG optical properties in the render are approximations. [Geometry and screening results](Development-checks.json)

[Underside](01-Underside.png) · [Low ceiling angle](02-Low-angle.png)

## Right-hand joint

The upper piece has an integral rail with a wider head. It slides lengthwise into the lower piece’s socket. The socket lips block upward withdrawal, and a built-in stop limits travel at the far end. The digital sample has **0.4 mm nominal clearance per side** and passed 30 sampled insertion positions. The open insertion end still needs an accessible keeper to prevent back-out. The wire runs in its own recessed groove away from the bearing faces.

[Joint bench](03-Right-joint-bench.png) · [End-on view of the captive profile](04-Keyed-end-section.png)

The next pass is to blend that profile into the actual A/B overlap and refine the visual rolls against the approved images. The six centre seats, continuous wire routes, final print cuts and physical retention are still open. Check fit, load, temperature and sustained sag on a full-size bench assembly before any overhead use.

[Verified Blender viewport recording](../process/videos/17-v11-development.mp4)
