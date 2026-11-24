"""Reproject the IGN aerial export to Lambert-93 and cut a square centred on the lily water."""
import numpy as np
import rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.warp import Resampling, calculate_default_transform, reproject

from common import out_dir, p


def reproject_aerial(cfg):
    a = cfg["aerial"]
    with rasterio.open(p(cfg["inputs"]["aerial_tif"])) as r:
        src_crs = r.crs.to_string()
        t, w, h = calculate_default_transform(r.crs, a["target_crs"], r.width, r.height, *r.bounds,
                                              resolution=a["resolution_m"])
        arr = np.zeros((r.count, h, w), np.uint8)
        for b in range(r.count):
            reproject(rasterio.band(r, b + 1), arr[b], src_transform=r.transform, src_crs=r.crs,
                      dst_transform=t, dst_crs=a["target_crs"], resampling=Resampling.bilinear)
    return arr, t, src_crs


def square_crop(cfg, arr, t):
    a = cfg["aerial"]
    _, h, w = arr.shape
    side = int(round(h * a["crop_side_frac"]))
    cx, cy = int(w * a["crop_center_frac"][0]), int(h * a["crop_center_frac"][1])
    x0 = max(0, min(w - side, cx - side // 2))
    y0 = max(0, min(h - side, cy - side // 2))
    crop = arr[:, y0:y0 + side, x0:x0 + side]
    if crop.shape[0] == 4 and (crop[3] < 255).mean() > 0.001:
        raise ValueError("Square crop reaches the empty corners of the reprojected image; "
                         "reduce crop_side_frac or move crop_center_frac.")
    # bounds of the crop in Lambert-93
    left = t.c + x0 * t.a
    top = t.f + y0 * t.e
    right = left + side * t.a
    bottom = top + side * t.e
    return crop[:3], (left, bottom, right, top), side * abs(t.a)


def build_aerial(cfg):
    arr, t, src_crs = reproject_aerial(cfg)
    rgb, bounds_l93, side_m = square_crop(cfg, arr, t)
    img = Image.fromarray(np.moveaxis(rgb, 0, -1)).resize((cfg["output_px"],) * 2, Image.LANCZOS)
    out = out_dir(cfg) / "aerial.jpg"
    img.save(out, quality=cfg["jpeg_quality"], optimize=True, progressive=True)
    tr = Transformer.from_crs(cfg["aerial"]["target_crs"], "EPSG:4326", always_xy=True)
    cx, cy = (bounds_l93[0] + bounds_l93[2]) / 2, (bounds_l93[1] + bounds_l93[3]) / 2
    lon, lat = tr.transform(cx, cy)
    # grid convergence: angle between Lambert-93 grid north and true north at the centre
    lon2, lat2 = tr.transform(cx, cy + 100)
    conv = float(np.degrees(np.arctan2((lon2 - lon) * np.cos(np.radians(lat)), lat2 - lat)))
    meta = {"source_crs": src_crs, "crs": cfg["aerial"]["target_crs"], "bounds_l93": bounds_l93,
            "side_m": round(side_m, 2), "center_lonlat": [round(lon, 6), round(lat, 6)],
            "grid_north_offset_deg": round(conv, 2), "native_resolution_m": 0.20}
    return out, meta
