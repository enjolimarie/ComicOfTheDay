# CLAUDE.md — Comic of the Day

## Project Overview

Comic of the Day is a Flask web application that displays a random Marvel comic cover each day. It fetches comic metadata from an unofficial Marvel API, scrapes the cover image URL from the Marvel.com detail page, extracts two dominant colors from that image server-side, and renders them as a smoothly-animated CSS gradient background. Users can fetch a new random comic at any time via a button; their choice persists across page reloads via `localStorage`. The UI uses the Bangers typeface and hard-offset text shadows for a pop-art / comic book aesthetic.

---

## Setup and Running

```bash
# First-time setup
./bootstrap.sh          # creates venv/, installs deps, copies .env.example → .env

# Start the app
./start-comicoftheday.sh [--host HOST] [--port PORT] [--debug]

# Stop the app
./stop-comicoftheday.sh
```

App is available at `http://localhost:5000` by default.

The `.env` file only needs Flask settings — **no API keys required**:
```
FLASK_SECRET_KEY=changeme
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
```

Config priority: CLI flags > env vars > `config/comicoftheday.yaml` > defaults.

---

## Architecture

### Module map

```
src/comicoftheday/
├── cli.py       Entry point — argparse, loads .env + YAML config, calls create_app()
├── app.py       Flask factory — defines routes and _fetch_comic() / _get_daily_comic()
├── marvel.py    Unofficial API client + Marvel.com cover image scraper
├── colors.py    Server-side dominant color extraction (colorthief + Pillow)
└── cache.py     Daily JSON file cache (cache/YYYY-MM-DD.json)
```

### Data flow for a page load

```
cli.py
  └─ create_app(cfg)
       └─ GET /
            └─ _get_daily_comic()
                 ├─ cache hit?  → return cached dict
                 └─ cache miss
                      └─ _fetch_comic(seed=today_iso)
                           ├─ shuffle search_terms by seed
                           ├─ fetch_comics(term)          → marvel.emreparker.com/v1/search/issues
                           ├─ pick_comic_of_the_day()     → date-seeded random.choice
                           ├─ get_cover_image_url()       → scrape marvel.com detail page
                           └─ fetch_and_extract_colors()  → download image → colorthief
                      └─ save_cached_comic()  → cache/YYYY-MM-DD.json
```

### Randomness and seeding

- **Daily comic**: `random.Random(date.today().isoformat())` — same result all day, rotates at midnight.
- **Random comic (button)**: `random.Random(secrets.token_hex(8))` — truly random per click.
- Both paths use the same `_fetch_comic(seed)` helper; only the seed differs.

### Caching

`cache/YYYY-MM-DD.json` holds one dict per calendar day. On startup, files older than 7 days are purged. Writes are atomic (`os.replace` on a `.tmp` file) to avoid partial reads under concurrent requests.

### Color extraction

`colors.py` downloads the cover image into `io.BytesIO` (no disk I/O), passes it to `colorthief.ColorThief`, and requests a 5-color palette. The dominant color is `palette[0]`. The secondary color is the first palette entry whose Euclidean RGB distance from the dominant exceeds a threshold of 40 — ensuring the two colors are visually distinct. Falls back to deep-blue defaults if extraction fails.

### Gradient animation

The gradient uses two CSS registered custom properties (`@property`):

```css
@property --grad-color1 { syntax: '<color>'; inherits: false; initial-value: #1a1a2e; }
@property --grad-color2 { syntax: '<color>'; inherits: false; initial-value: #16213e; }

body {
  background: linear-gradient(135deg, var(--grad-color1), var(--grad-color2));
  transition: --grad-color1 1.2s ease, --grad-color2 1.2s ease;
}
```

Because the properties are registered as `<color>` types the browser can interpolate them, enabling smooth gradient transitions when JS calls `body.style.setProperty('--grad-color1', newColor)`. Without `@property`, custom properties are untyped strings and cannot be animated.

### localStorage persistence

When the "Fetch a New Comic" button succeeds, the full comic dict (image URL, title, series, issue, both colors) is written to `localStorage` under the key `comicoftheday`. On the next page load, an inline `<script>` runs synchronously before the first paint:

1. Reads and parses `localStorage`
2. Applies stored colors to the CSS custom properties
3. Swaps the `<img>` `src` and text content
4. Fades the image in via `opacity` once loaded

The image starts at `opacity: 0` in CSS so there is no flash of the server-rendered daily comic before the stored comic appears.

---

## Configuration Schema

```yaml
# config/comicoftheday.yaml

app:
  host: "127.0.0.1"    # overridden by FLASK_HOST or --host
  port: 5000           # overridden by FLASK_PORT or --port
  debug: false         # overridden by FLASK_DEBUG=true or --debug
  secret_key: "changeme"

cache:
  dir: "cache"         # relative to project root; resolved to absolute at runtime

comics:
  search_terms:        # shuffled by date seed; first 5 tried per request
    - "amazing"
    - "uncanny"
    - "wolverine"
    # add/remove to widen or narrow the comic pool
```

---

## Key Decisions and Development History

### API switch: official Marvel → unofficial Marvel Metadata API

The original design used the official Marvel Developer API (`gateway.marvel.com`) with MD5 hash authentication (`md5(ts + privateKey + publicKey)`). When the developer portal was found to be down, the project switched to the unofficial Marvel Metadata API at `marvel.emreparker.com`. This API requires no authentication and has 37,500+ issues but returns no image URLs.

### Cover image strategy: scraping Marvel.com detail pages

Because the unofficial API provides only metadata (no image URLs), the cover image is obtained by fetching the comic's `detailUrl` (e.g. `https://www.marvel.com/comics/issue/12168/wolverine_1982_1`) and extracting the first `cdn.marvel.com/u/prod/marvel/i/mg/.../portrait_uncanny.jpg` URL via regex. This was verified by inspecting the page HTML — Marvel.com is server-rendered and the cover image is the first CDN `<img>` in the document body. There is no `og:image` meta tag on these pages.

### CORS-free color extraction

Loading a cross-origin image onto an HTML5 `<canvas>` for pixel analysis taints the canvas and throws a security error. The solution is to download the image entirely server-side (`requests.get` → `io.BytesIO`) and run `colorthief` there. No canvas is involved and no CORS headers are needed.

### pyproject.toml build backend

`setuptools.backends.legacy:build` (the initially generated backend) requires setuptools ≥ 68.1 and is not available in all environments. Changed to `setuptools.build_meta`, which is the standard stable name supported across all modern setuptools versions.

### CSS `@property` for gradient animation

Plain CSS custom properties (e.g. `--color: red`) are untyped strings — browsers cannot interpolate between two string values, so `transition` has no effect. Registering the properties with `@property` and `syntax: '<color>'` tells the browser the value is a color, enabling full CSS transition support. This requires no JavaScript animation loop; the browser handles interpolation natively.

### Tilt effect implementation

The 3D tilt uses `perspective(700px) rotateX() rotateY() scale()` applied directly via `element.style.transform` on `mousemove` (no CSS transition on that path — direct application keeps tracking instantaneous). On `mouseleave`, the `.is-resetting` class is added, which applies a `cubic-bezier(0.23, 1, 0.32, 1)` transition for a smooth spring-back, then is removed on the next `mousemove`.

---

## Testing

No automated test suite is configured. Manual smoke test:

```bash
# With the app running:
curl http://localhost:5000/api/comic | python3 -m json.tool
curl http://localhost:5000/api/comic/random | python3 -m json.tool
```

Check that both return valid JSON with `image_url`, `dominant_color`, and `secondary_color` fields.
