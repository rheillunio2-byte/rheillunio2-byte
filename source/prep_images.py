"""Prepare logo + portrait assets from the uploaded originals."""
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
UP = "/mnt/user-data/uploads/"
OUT = "/home/claude/retl-profile/assets/"

def black_to_alpha(path, out, crop=True):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    m = a.max(axis=2)
    alpha = np.clip((m - 10) / (215 - 10), 0, 1) ** 0.9
    rgb = np.where(alpha[..., None] > 0.02, a / np.maximum(alpha[..., None], 0.02), 0)
    rgb = np.clip(rgb, 0, 255)
    res = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    if crop:
        bb = res.getchannel("A").point(lambda v: 255 if v > 14 else 0).getbbox()
        pad = 24
        bb = (max(0, bb[0]-pad), max(0, bb[1]-pad), min(res.width, bb[2]+pad), min(res.height, bb[3]+pad))
        res = res.crop(bb)
    res.save(out, optimize=True)
    print(out, res.size)

black_to_alpha(UP + "RETL_LOGO_HORIZONTAL.png", OUT + "logo-horizontal.png")
black_to_alpha(UP + "RETL_LOGO.png", OUT + "logo-mark.png")

def grade(im):
    im = ImageEnhance.Brightness(im).enhance(1.18)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return im

photo = Image.open(UP + "1794014047756_image.png").convert("RGB")
# head-and-shoulders circle
cx, cy, r = 910, 850, 400
sq = photo.crop((cx - r, cy - r, cx + r, cy + r)).resize((640, 640), Image.LANCZOS)
sq = grade(sq)
mask = Image.new("L", (640 * 3, 640 * 3), 0)
ImageDraw.Draw(mask).ellipse([0, 0, 640 * 3 - 1, 640 * 3 - 1], fill=255)
mask = mask.resize((640, 640), Image.LANCZOS)
sq.putalpha(mask)
sq.save(OUT + "me-avatar.png", optimize=True)

# portrait rounded rect (more of the scene)
box = (420, 330, 1500, 1830)  # 1080 x 1500
pr = photo.crop(box).resize((540, 750), Image.LANCZOS)
pr = grade(pr)
m = Image.new("L", (540 * 3, 750 * 3), 0)
ImageDraw.Draw(m).rounded_rectangle([0, 0, 540 * 3 - 1, 750 * 3 - 1], radius=36 * 3, fill=255)
m = m.resize((540, 750), Image.LANCZOS)
pr.putalpha(m)
pr.save(OUT + "me-portrait.png", optimize=True)
print("done")
