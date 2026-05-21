import random
import re
from typing import List, Optional

import requests

BASE_URL = "https://marvel.emreparker.com/v1"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Regex to find the first cdn.marvel.com cover image in a Marvel.com detail page
_COVER_PATTERN = re.compile(
    r'https://cdn\.marvel\.com/u/prod/marvel/i/mg/[^"]+/portrait_uncanny\.jpg'
)


class ComicAPIError(Exception):
    pass


def fetch_comics(search_term: str, timeout: int = 10) -> List[dict]:
    try:
        resp = requests.get(
            f"{BASE_URL}/search/issues",
            params={"q": search_term},
            headers=_HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ComicAPIError(f"Network error searching '{search_term}': {exc}") from exc
    return resp.json().get("items", [])


def pick_search_term(terms: List[str], date_str: str) -> str:
    return random.Random(date_str).choice(terms)


def pick_comic_of_the_day(comics: List[dict], date_str: str) -> Optional[dict]:
    if not comics:
        return None
    return random.Random(date_str + "comic").choice(comics)


def get_cover_image_url(detail_url: str, timeout: int = 10) -> Optional[str]:
    """Fetch the Marvel.com detail page and extract the first cover image URL."""
    try:
        resp = requests.get(detail_url, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        m = _COVER_PATTERN.search(resp.text)
        if m:
            return m.group(0)
    except Exception:
        pass
    return None
