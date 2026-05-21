import random
import secrets
from datetime import date
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, render_template

from .cache import get_cached_comic, purge_old_cache, save_cached_comic
from .colors import FALLBACK_COLORS, fetch_and_extract_colors
from .marvel import ComicAPIError, fetch_comics, get_cover_image_url, pick_comic_of_the_day

TEMPLATES_DIR = str(Path(__file__).parent.parent.parent / "web" / "templates")


def create_app(cfg: dict) -> Flask:
    app = Flask(__name__, template_folder=TEMPLATES_DIR)
    app.secret_key = cfg["app"].get("secret_key", "changeme")

    cache_dir = cfg["cache"]["dir"]
    search_terms = cfg["comics"]["search_terms"]

    purge_old_cache(cache_dir)

    def _fetch_comic(seed: str) -> Optional[dict]:
        """Try up to 5 search terms (shuffled by seed) and return a comic dict, or None."""
        terms = list(search_terms)
        random.Random(seed).shuffle(terms)
        for term in terms[:5]:
            try:
                comics = fetch_comics(term)
                comic = pick_comic_of_the_day(comics, seed + term)
                if not comic:
                    continue
                image_url = get_cover_image_url(comic["detailUrl"])
                if not image_url:
                    continue
                dominant, secondary = fetch_and_extract_colors(image_url)
                return {
                    "comic_id": comic.get("id"),
                    "title": comic.get("title", ""),
                    "issue_number": comic.get("issueNumber", ""),
                    "series_name": comic.get("seriesName", ""),
                    "image_url": image_url,
                    "dominant_color": dominant,
                    "secondary_color": secondary,
                }
            except ComicAPIError:
                continue
        return None

    def _get_daily_comic() -> dict:
        cached = get_cached_comic(cache_dir)
        if cached:
            return cached

        today = date.today().isoformat()
        data = _fetch_comic(today)

        if data is None:
            data = {
                "comic_id": None,
                "title": "No comic available today",
                "issue_number": "",
                "series_name": "Marvel Comics",
                "image_url": "",
                "dominant_color": FALLBACK_COLORS[0],
                "secondary_color": FALLBACK_COLORS[1],
            }

        data["date"] = today
        save_cached_comic(cache_dir, data)
        return data

    @app.route("/")
    def index():
        comic = _get_daily_comic()
        return render_template("index.html", comic=comic)

    @app.route("/api/comic")
    def api_comic():
        return jsonify(_get_daily_comic())

    @app.route("/api/comic/random")
    def api_comic_random():
        data = _fetch_comic(secrets.token_hex(8))
        if data is None:
            return jsonify({"error": "No comic found"}), 503
        return jsonify(data)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/api")
    def api_docs():
        return render_template("api_docs.html")

    @app.route("/sitemap")
    def sitemap():
        return render_template("sitemap.html")

    return app
