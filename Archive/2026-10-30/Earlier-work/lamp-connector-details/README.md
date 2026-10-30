# Clip holder correction

## White module top and bottom correction

The user's additional photographs show a large open top and a partially covered underside with a narrow elongated passage for the circular support. Use `../lamp-reference-images/02-single-shade-module-v2-open-top.png` and `../lamp-reference-images/11-single-shade-module-v2-underside.png`. Source photographs are `source-crops/user-module-open-top.jpg` and `source-crops/user-module-slotted-underside.jpg`. The exact built-in image_gen prompts are recorded in `module-top-bottom-correction-prompts.json` and `module-underside-prompt.json`. These supersede the first open-cuff module reconstruction. The opening size and hidden geometry remain approximate.

## Stand cable opening correction

The user supplied two additional close-ups identifying the small opening beneath the stand's leg-root region as clearance for a wire. The current stand references are `10-stand-cable-opening-closeup.png` and `../lamp-reference-images/03-brown-three-leg-stand-v2-cable-opening.png`. They show an empty bottom-entering opening, with no invented clip or hinge. Its exact dimensions and hidden depth remain unmeasured. The earlier `08-brown-ring-junction-details.png` is superseded by this correction. The original user close-ups are retained in `source-crops/`, and the exact built-in image_gen prompts are in `stand-cable-opening-prompts.json`.

The user confirms that the white module has an empty holder with a rectangular opening. Its clip is a separate insert and is absent in the supplied zoom photo.

The earlier projecting-pegs / receiving-holes interpretation was wrong. That generated image and its saved variants have been deleted. Do not use the original product views as verified connector geometry.

09-empty-clip-holder.png is the current enlarged visual reference, generated from the user-provided zoom. It shows only the empty holder and its attachment to the shell, with no separate clip or latch.

The unchanged source zoom is source-crops/user-zoom-empty-clip-holder.jpg. The other original source crops remain included for context. The earlier inner-bracket and brown-ring sheets are approximate visual interpretations. No dimensions or hidden engagement geometry have been verified.

Generated with the built-in image_gen tool. The current full prompt is in empty-holder-prompt.json.
