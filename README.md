# Comic of the Day

A Flask web application that surfaces a random Marvel comic cover every day. The page background dynamically shifts to match the two dominant colors extracted from that day's cover art. Click **Fetch a New Comic** to pull a different one at any time — your pick persists across reloads.

> Data provided by the [Marvel Metadata API](https://marvel.emreparker.com) (unofficial).  
> © 2026 MARVEL

---

## Features

- **Daily comic** — date-seeded selection stays consistent all day, rotates at midnight
- **Dynamic gradient background** — two dominant colors are extracted server-side from the cover image using `colorthief`; the gradient transitions smoothly when a new comic is fetched
- **Fetch a New Comic** — button pulls a random comic without a full page reload; persists to `localStorage` so it survives refreshes
- **Tilt + gloss effect** — hover over the cover for a 3D perspective tilt with a moving gloss highlight
- **Comic book title** — pop-art styled header using the Bangers typeface with black stroke and hard drop shadows
- **No API keys required** — uses the public Marvel Metadata API

---

## Screenshots

| Daily view | Hover effect |
|---|---|
| Gradient background matches the comic cover colors | 3D tilt with radial gloss highlight on cursor |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [Flask](https://flask.palletsprojects.com/) |
| Templating | Jinja2 |
| Styling | [Tailwind CSS](https://tailwindcss.com/) (CDN) |
| Partial updates | [HTMX](https://htmx.org/) (CDN) |
| Font | [Bangers](https://fonts.google.com/specimen/Bangers) (Google Fonts) |
| Color extraction | [colorthief](https://github.com/fengsp/color-thief-py) + Pillow |
| HTTP client | requests |
| Config | PyYAML + python-dotenv |
| Comic data | [marvel.emreparker.com](https://marvel.emreparker.com) |

---

## Requirements

- Python 3.9 or later
- pip / venv

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/enjolimarie/ComicOfTheDay.git
cd ComicOfTheDay

# 2. Bootstrap: creates venv, installs deps, copies .env.example → .env
./bootstrap.sh
```

The `.env` file only needs Flask settings — no API keys required:

```
FLASK_SECRET_KEY=change_me_to_a_random_string
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
```

---

## Running

```bash
./start-comicoftheday.sh
```

Open <http://localhost:5000> in your browser.

**Options:**

```bash
./start-comicoftheday.sh --host 0.0.0.0 --port 8080 --debug
```

**Stop:**

```bash
./stop-comicoftheday.sh
```

---

## How It Works

```
Browser                    Flask                      External
  │                          │                            │
  │  GET /                   │                            │
  │─────────────────────────>│                            │
  │                          │  Search for comics         │
  │                          │───────────────────────────>│ marvel.emreparker.com
  │                          │<───────────────────────────│
  │                          │  Fetch detail page         │
  │                          │───────────────────────────>│ marvel.com
  │                          │<───────────────────────────│
  │                          │  Extract cover image URL   │
  │                          │  Download image + colors   │
  │                          │  Cache → cache/YYYY-MM-DD.json
  │<─────────────────────────│                            │
  │  HTML with gradient      │                            │
```

1. A search term is picked each day from a curated list, seeded by the date
2. The Marvel Metadata API returns up to 50 matching comics
3. One comic is selected (also date-seeded — consistent all day)
4. Flask fetches the comic's Marvel.com detail page and extracts the first cover image URL
5. The cover is downloaded in memory (`io.BytesIO`) and two dominant colors are extracted with `colorthief`
6. Colors are injected into the page as CSS custom properties (`@property`) — enabling smooth gradient transitions
7. The result is cached in `cache/YYYY-MM-DD.json`; the external APIs are called at most **once per calendar day**

---

## Configuration

All settings live in `config/comicoftheday.yaml`. Override priority:

```
CLI flags  >  environment variables  >  comicoftheday.yaml  >  defaults
```

Key options:

```yaml
app:
  host: "127.0.0.1"
  port: 5000
  debug: false

comics:
  search_terms:          # add/remove terms to widen or narrow the comic pool
    - "amazing"
    - "uncanny"
    - "wolverine"
    # ...

cache:
  dir: "cache"           # resolved to absolute path at runtime
```

---

## Project Structure

```
ComicOfTheDay/
├── src/comicoftheday/
│   ├── app.py           # Flask factory, routes, daily + random comic logic
│   ├── marvel.py        # API client, cover image extraction
│   ├── colors.py        # Server-side dominant color extraction
│   ├── cache.py         # Daily JSON file cache
│   └── cli.py           # Entry point (argparse, config loading)
├── web/templates/
│   ├── base.html        # Nav, Bangers font, glass styles
│   ├── index.html       # Comic display, tilt/gloss, gradient JS
│   ├── about.html
│   ├── api_docs.html
│   └── sitemap.html
├── config/
│   └── comicoftheday.yaml
├── man/                 # Man pages for start/stop scripts
├── bootstrap.sh
├── start-comicoftheday.sh
└── stop-comicoftheday.sh
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Daily comic page |
| `GET` | `/api/comic` | Daily comic as JSON (cached) |
| `GET` | `/api/comic/random` | Fresh random comic as JSON |
| `GET` | `/about` | Project info & dependencies |
| `GET` | `/api` | API documentation |
| `GET` | `/sitemap` | Sitemap |

---

## License

MIT — do whatever you like with it.
