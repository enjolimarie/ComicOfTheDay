import io
import math
from typing import Tuple

import requests
from colorthief import ColorThief

FALLBACK_COLORS = ("#1a1a2e", "#16213e")
_SIMILARITY_THRESHOLD = 40


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def fetch_and_extract_colors(
    image_url: str,
    timeout: int = 10,
) -> Tuple[str, str]:
    try:
        resp = requests.get(image_url, timeout=timeout)
        resp.raise_for_status()
        buf = io.BytesIO(resp.content)
        ct = ColorThief(buf)
        palette = ct.get_palette(color_count=5, quality=5)
    except Exception:
        return FALLBACK_COLORS

    if not palette:
        return FALLBACK_COLORS

    dominant = palette[0]
    # find a second color sufficiently different from the dominant
    secondary = None
    for candidate in palette[1:]:
        if _color_distance(dominant, candidate) >= _SIMILARITY_THRESHOLD:
            secondary = candidate
            break
    if secondary is None:
        secondary = palette[1] if len(palette) > 1 else (22, 33, 62)

    return _rgb_to_hex(*dominant), _rgb_to_hex(*secondary)
