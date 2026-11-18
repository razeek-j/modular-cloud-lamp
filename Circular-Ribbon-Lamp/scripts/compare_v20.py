"""Side-by-side comparisons for V20 (PIL only).

Compare-from-below.png : the user's spiral picture | V20 from below (and the palette variant)
Compare-reference.png  : the ribbon-lamp photo above | V20 from the photo's camera position below

Run: python3 scripts/compare_v20.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "development-v20"
REF = ROOT / "references"
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
except Exception:
    font = ImageFont.load_default()


def label(im, text):
    d = ImageDraw.Draw(im, "RGBA")
    w = d.textlength(text, font=font) + 24
    d.rectangle([10, 10, 10 + w, 52], fill=(0, 0, 0, 150))
    d.text((22, 15), text, fill=(255, 255, 255, 255), font=font)
    return im


H = 1000
pic = Image.open(REF / "v20-spiral-rosette-picture.png").convert("RGB").resize((H, H), Image.LANCZOS)
white = Image.open(DEV / "01-From-below.png").convert("RGB").resize((H, H), Image.LANCZOS)
tiles = [label(pic, "Your picture"), label(white, "V20 from below")]
pal = DEV / "01-From-below-palette.png"
if pal.exists():
    tiles.append(label(Image.open(pal).convert("RGB").resize((H, H), Image.LANCZOS), "V20 palette variant"))
sheet = Image.new("RGB", (H * len(tiles), H))
for k, t in enumerate(tiles):
    sheet.paste(t, (k * H, 0))
sheet.save(DEV / "Compare-from-below.png")

ref = Image.open(REF / "design-reference.jpg").convert("RGB")
cam = Image.open(DEV / "00-Reference-camera.png").convert("RGB")
w = 1280
ref = ref.resize((w, int(ref.height * w / ref.width)), Image.LANCZOS)
cam = cam.resize((w, int(cam.height * w / cam.width)), Image.LANCZOS)
sheet = Image.new("RGB", (w, ref.height + cam.height))
sheet.paste(label(ref, "Ribbon-lamp photo"), (0, 0))
sheet.paste(label(cam, "V20, same camera position"), (0, ref.height))
sheet.save(DEV / "Compare-reference.png")
print("saved comparisons")
