# Monet's Garden of Lilies — interactive (v1.0.2)

*Is this a map?* The lily pond at Giverny seen from above (IGN aerial photo) changes square by square into Monet's *The Water-Lily Pond* (1899). Press Play, drag the slider, or jump to Photo / Halfway / Painting. The map clues (north arrow, 10 m scale bar, locator of France) fade out as the painting takes over.

#30DayMapChallenge 2026, Day 25.

## Run

```
python src/run.py --config config/config.yaml
```

Requires Python 3.10+, rasterio, pyproj, geopandas, shapely, pillow, pyyaml.

## Layout

| Path | What it is |
|---|---|
| `config/config.yaml` | inputs, crop, output size, grid, credits, script version |
| `data/monetpond.tif` | IGN Ortho 20 cm export from QGIS (EPSG:8857, 5448 × 3184) |
| `data/NG4240_water_lily_pond.jpg` | National Gallery download, 1600 × 1552 |
| `data/ne_countries.gpkg` | Natural Earth countries (locator) |
| `src/aerial.py` | reprojects the aerial to Lambert-93 (EPSG:2154) at 0.05 m and cuts a square centred on the lily water |
| `src/painting.py` | centre-crops the painting to a square |
| `src/locator.py` | metropolitan France outline as an SVG path, with the pond marked |
| `src/run.py` | builds everything and writes `provenance.json` |
| `web/template.html` | the page; data is inlined at build time |
| `out/` | `index.html` (self-contained, about 0.75 MB), `aerial.jpg`, `painting.jpg` (1200 × 1200 each, for reuse), `provenance.json` |

## Opening it

`out/index.html` has both images inside it as data URIs, so it works the same everywhere: double-click from your computer, offline, on GitHub Pages or any web server. Nothing else is needed next to it.

Why: browsers do not let a page read pixel colours from image files opened from disk (`file://`), and the pixel change needs those colours. In v1.0.1, opening `index.html` by double-click showed "SecurityError: The operation is insecure". Since v1.0.2 the images are always inlined and the separate `monet_pond_standalone.html` is gone.

## Methods

- **Reprojection.** The QGIS export was in Equal Earth (EPSG:8857), which bends shapes slightly at 49° N. It is reprojected to Lambert-93, which is conformal, so the pond's shape and the scale bar are true. The square is 56.65 m on a side, centred at 49.07435° N, 1.53411° E. Lambert-93 grid north is 1.06° off true north there; the north arrow is turned by that amount.
- **Resolution.** The photo's real detail is 20 cm per pixel, so the pond is about 280 real pixels across this square. The 1200 px output is resampled, and looks soft up close.
- **The pixel change.** Both images are cut into the same 40 × 40 grid. Each square gets a fixed threshold: 62% distance from the lily water and 38% seeded noise, so the change ripples outward and is the same every visit. While a square is changing, it shows one flat colour that blends from the photo's average to the painting's average.
- **Alignment.** Monet painted the pond from the bank, in perspective; the photo looks straight down. The two images are not georeferenced to each other; they share the frame, not the geometry. That gap is the "is this a map?" question.

## Mobile and security

- **Mobile.** The stage is square and fits the screen width and about 72% of its height. Controls are at least 44 px tall. The canvas redraws only when its width changes.
- **Motion.** With reduced motion turned on, the change is a simple fade and nothing plays by itself.
- **Security.** No outside scripts at all, and no input, storage or network calls. A Content-Security-Policy meta tag allows only the page's own images and Google Fonts. All text is escaped before display. If the images fail to load, the page says so.
- **Provenance.** `provenance.json` records the SHA-256 of every input and output.

## Sources

**Aerial photo.** IGN, BD ORTHO, *Ortho 20 cm* (layer HR.ORTHOIMAGERY.ORTHOPHOTOS), served by the Géoplateforme WMTS, https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities. Exported in QGIS on 23 Nov 2026. Licence Ouverte Etalab 2.0.

**Painting.** Claude Monet, *The Water-Lily Pond*, 1899. Oil on canvas, 88.3 × 93.1 cm. The National Gallery, London, NG4240. https://www.nationalgallery.org.uk/paintings/claude-monet-the-water-lily-pond. Image downloaded from the National Gallery website, © The National Gallery, London, for non-commercial use under its Creative Commons terms.

Note: the Wikimedia Commons record for this painting gives the French title *Le Bassin aux nymphéas, harmonie verte*. That title belongs to a different canvas, Musée d'Orsay RF 2004 (89.5 × 92.5 cm), https://www.musee-orsay.fr/fr/oeuvres/1175. The image used here is the National Gallery's.

**Locator.** Natural Earth, 1:50m Admin 0 Countries. Public domain.

## Licence

Code: MIT. The page and images are for non-commercial use, because the painting image is licensed non-commercially. The aerial photo itself is open (Licence Ouverte).
