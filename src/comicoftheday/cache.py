import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


def _cache_path(cache_dir: str) -> Path:
    return Path(cache_dir) / f"{date.today().isoformat()}.json"


def get_cached_comic(cache_dir: str) -> Optional[dict]:
    path = _cache_path(cache_dir)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("date") == date.today().isoformat():
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def save_cached_comic(cache_dir: str, data: dict) -> None:
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    path = _cache_path(cache_dir)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)


def purge_old_cache(cache_dir: str, keep_days: int = 7) -> None:
    cache = Path(cache_dir)
    if not cache.exists():
        return
    cutoff = date.today() - timedelta(days=keep_days)
    for f in cache.glob("*.json"):
        try:
            file_date = date.fromisoformat(f.stem)
            if file_date < cutoff:
                f.unlink()
        except (ValueError, OSError):
            pass
