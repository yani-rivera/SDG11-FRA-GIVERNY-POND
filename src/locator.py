"""Small locator of France (metropolitan) as an SVG path, with the pond marked."""
import geopandas as gpd
from shapely.geometry import box

from common import p


def build_locator(cfg, lonlat, size=120):
    c = gpd.read_file(p(cfg["inputs"]["countries_gpkg"]), layer=cfg["inputs"]["countries_layer"])
    fr = c[c.ADMIN == "France"].to_crs("EPSG:2154")
    metro = fr.geometry.iloc[0].intersection(box(50000, 6000000, 1300000, 7200000))
    metro = metro.simplify(4000)
    minx, miny, maxx, maxy = metro.bounds
    k = (size - 8) / max(maxx - minx, maxy - miny)

    def xy(x, y):
        return round(4 + (x - minx) * k, 1), round(4 + (maxy - y) * k, 1)

    parts = getattr(metro, "geoms", [metro])
    d = ""
    for poly in parts:
        ring = list(poly.exterior.coords)
        d += "M" + " L".join(f"{a},{b}" for a, b in (xy(*pt) for pt in ring)) + "Z"
    pt = gpd.GeoSeries(gpd.points_from_xy([lonlat[0]], [lonlat[1]]), crs="EPSG:4326").to_crs("EPSG:2154").iloc[0]
    px, py = xy(pt.x, pt.y)
    w = round(4 + (maxx - minx) * k + 4, 1)
    h = round(4 + (maxy - miny) * k + 4, 1)
    return {"d": d, "x": px, "y": py, "w": w, "h": h}
