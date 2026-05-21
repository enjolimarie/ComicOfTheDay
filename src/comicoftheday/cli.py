import argparse
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


def _load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _apply_env_overrides(cfg: dict) -> None:
    app = cfg.setdefault("app", {})
    if os.environ.get("FLASK_HOST"):
        app["host"] = os.environ["FLASK_HOST"]
    if os.environ.get("FLASK_PORT"):
        app["port"] = int(os.environ["FLASK_PORT"])
    if os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true"):
        app["debug"] = True
    if os.environ.get("FLASK_SECRET_KEY"):
        app["secret_key"] = os.environ["FLASK_SECRET_KEY"]



def main() -> None:
    project_root = Path(__file__).parent.parent.parent
    default_config = str(project_root / "config" / "comicoftheday.yaml")

    parser = argparse.ArgumentParser(
        prog="comicoftheday",
        description="Comic of the Day web application",
    )
    parser.add_argument("--host", help="Bind host (overrides config/env)")
    parser.add_argument("--port", type=int, help="Bind port (overrides config/env)")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    parser.add_argument(
        "--config",
        default=default_config,
        help=f"Path to YAML config file (default: {default_config})",
    )
    parser.add_argument("--cache-dir", help="Path to cache directory (overrides config)")
    args = parser.parse_args()

    load_dotenv(project_root / ".env")

    cfg = _load_config(args.config)
    _apply_env_overrides(cfg)

    # CLI args have highest priority
    if args.host:
        cfg["app"]["host"] = args.host
    if args.port:
        cfg["app"]["port"] = args.port
    if args.debug:
        cfg["app"]["debug"] = True
    if args.cache_dir:
        cfg["cache"]["dir"] = args.cache_dir

    # Resolve relative cache dir against project root
    cache_dir = cfg["cache"]["dir"]
    if not Path(cache_dir).is_absolute():
        cfg["cache"]["dir"] = str(project_root / cache_dir)

    from .app import create_app

    app = create_app(cfg)
    app.run(
        host=cfg["app"].get("host", "127.0.0.1"),
        port=cfg["app"].get("port", 5000),
        debug=cfg["app"].get("debug", False),
    )


if __name__ == "__main__":
    main()
