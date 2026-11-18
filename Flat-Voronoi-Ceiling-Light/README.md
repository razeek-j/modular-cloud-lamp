# Current direction: v06 Sun Piece (concept, 17 Nov 2026)

After a chromosphere photo from the user: no curls, only pointed flares (a slight bend at most), and a gentle curve so it reads as a piece of the sun. v06: a rounded, gently wobbling limb; surface of short bright fibrils that bunch into rosettes (7 main + 45 small field poles), carved thin on the back so they glow, with darker mottling between; a fringe of 420 fine pointed spicules plus 8 slim tall flares clustered on one side; limb brightening; amber palette (amber LEDs or translucent orange filament). About 932 × 676 mm.

- `scripts/concept_sun_piece.py` builds `maps/sun-*.npy`, `renders/v06-sun-glow.png`, `renders/v06-sun-oblique.png`, `Sun-Piece-v06.blend`.
- Concept only. Open: spicule tips are 1–2 mm wide (too fragile as drawn), tiling, LEDs, mount, real colour test.

# Current direction: v05 Solar Flares (concept, 17 Nov 2026)

The user asked to drop the circle and end the shape in flare tails. v05 keeps v04's twisted field-line fins and sunspots, but the outline now comes from the field: a calm body (~70 cm) with seven uneven flare tails traced along the field lines, fat at the root and curling to a point. Overall about 986 × 692 mm; every part is connected (no islands).

- `scripts/concept_solar_flares.py` builds `maps/flares-*.npy`, `renders/v05-flares-glow.png`, `renders/v05-flares-oblique.png` and `Solar-Flares-v05.blend`.
- Concept only: tip thickness, printability, tiling, LEDs and mount not done. Glow is simulated.

# Current direction: v04 Solar Field (concept, 17 Nov 2026)

The user rejected the moon (v02) and the uniform patterns (v03 diatom, gyroid, sunflower) and asked for something weird and non-uniform, "like a solar field". v04: raised fins follow the twisted magnetic field lines of seven off-centre "sunspot" poles; each pole is a glowing crater; the fins face the room.

- `scripts/concept_solar_field.py` builds the field, height map (`maps/solar-height.npy`), skin map, a flat glow preview (`renders/v04-solar-glow.png`), an oblique Cycles render (`renders/v04-solar-oblique.png`) and `Solar-Field-v04.blend` (metres).
- Concept only: no print tiles, printability check, LED backplate or mount yet. Glow is simulated.

# Current direction: v02 Voronoi Moon (concept, 17 Nov 2026)

v01 below was rejected as having no wow factor. v02 is a full-moon lithophane inside 450 irregular Voronoi cells, floating 40 mm below the ceiling on a hidden halo ring.

- `scripts/build_moon_concept.py` maps NASA's LROC near-side moon (`references/lroc_color_poles_2k.tif`, public domain) onto the Ø900 disc. It sets skin thickness from 0.6 to 3.0 mm (relief on the hidden back, face stays flat) and simulates light through white PLA (Beer–Lambert, mu ≈ 1.05/mm). Outputs go to `maps/` (thickness, walls, sites).
- `scripts/render_halo_room.py` renders the room view and saves `Voronoi-Moon-v02.blend` (metres, room hidden in the viewport, moon image packed inside). `Voronoi-Moon-v02-concept.blend` is obsolete.
- Renders: `02-moon-on`, `03-moon-off`, `04-halo-room`. These are simulations, not photos; the real contrast must be checked with a printed test tile.
- Not done: printable lithophane meshes, tiling, LED backplate and halo ring, ceiling mount, checking the moon isn't mirrored when viewed from below.

# Flat Voronoi Ceiling Light, v01 (superseded)

Ø900 mm × 25 mm disc, flush to the ceiling. Built headless in Blender 5.2 by `scripts/build_voronoi_disc.py`:

    /Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build_voronoi_disc.py

- 520 Voronoi cells (golden-angle seeds, Lloyd-relaxed): small and dense at the centre, larger toward the rim.
- Each cell is a pocket: 0.8 mm diffuser skin on the face, 1.6 mm ribs, 25 mm deep.
- 13 tiles (Ø290 hub + 12 sectors) for the 350 mm bed of the Anycubic Kobra S1 Max. Largest is 326 × 304 mm.
- Seams run along cell walls (1.2 mm each side) so they disappear into the pattern. All tiles are watertight.
- `print/*.stl` are centred and face down on the bed (z=0 is the visible face). Print the face in white/natural PLA so it glows.
- Open: light source, ceiling mount, seam glue/pins.
