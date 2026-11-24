"""Build the Monet pond interactive: aerial and painting squares, locator, and the HTML page.

    python src/run.py [--config config/config.yaml]
"""
import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aerial import build_aerial  # noqa: E402
from common import load_config, out_dir, p, write_provenance  # noqa: E402
from locator import build_locator  # noqa: E402
from painting import build_painting  # noqa: E402


def build_page(cfg, meta, locator):
    data = {"title": cfg["title"], "question": cfg["question"], "version": cfg["version"],
            "grid": cfg["grid_cells"], "side_m": meta["side_m"], "center": meta["center_lonlat"],
            "north_offset": meta["grid_north_offset_deg"], "credits": cfg["credits"], "locator": locator}
    tpl = p("web/template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    out = out_dir(cfg) / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def inline_images(cfg, page, images):
    """Inline the images as data URIs in index.html itself.

    Browsers refuse to let a page read pixel colours from image files opened from
    disk (file://), which breaks the canvas pixel change ("SecurityError"). With the
    images inside the page it works the same everywhere: double-click, GitHub Pages
    or any server. The JPEGs are still written next to it for reuse.
    """
    html = page.read_text(encoding="utf-8")
    for name, path in images.items():
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        html = html.replace(f'load("{name}")', f'load("data:image/jpeg;base64,{b64}")')
    if 'load("data:image/jpeg' not in html:
        raise SystemExit("inline_images: image placeholders not found in the page")
    page.write_text(html, encoding="utf-8")
    old = out_dir(cfg) / "monet_pond_standalone.html"
    if old.exists():
        old.unlink()          # replaced by the self-contained index.html
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/config.yaml")
    cfg = load_config(ap.parse_args().config)
    aerial_out, meta = build_aerial(cfg)
    paint_out, pmeta = build_painting(cfg)
    loc = build_locator(cfg, meta["center_lonlat"])
    page = build_page(cfg, meta, loc)
    page = inline_images(cfg, page, {"aerial.jpg": aerial_out, "painting.jpg": paint_out})
    prov = write_provenance(cfg, {"aerial": aerial_out, "painting": paint_out, "page": page},
                            {"aerial": meta, "painting": pmeta})
    print(json.dumps({"aerial": meta, "painting": pmeta, "provenance": str(prov)}, indent=1))


if __name__ == "__main__":
    main()
