"""Centre-crop the painting to a square and resize to match the aerial image."""
from PIL import Image

from common import out_dir, p


def build_painting(cfg):
    im = Image.open(p(cfg["inputs"]["painting"])).convert("RGB")
    w, h = im.size
    s = min(w, h)
    box = ((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)
    im = im.crop(box).resize((cfg["output_px"],) * 2, Image.LANCZOS)
    out = out_dir(cfg) / "painting.jpg"
    im.save(out, quality=cfg["jpeg_quality"], optimize=True, progressive=True)
    return out, {"source_px": [w, h], "crop_box": list(box)}
