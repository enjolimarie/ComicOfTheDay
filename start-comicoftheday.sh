#!/usr/bin/env bash
# Start the Comic of the Day web application
# Usage: ./start-comicoftheday.sh [--host HOST] [--port PORT] [--debug] [--config PATH] [--cache-dir PATH]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "==> venv not found, running bootstrap first..."
    bash "$SCRIPT_DIR/bootstrap.sh"
fi

source venv/bin/activate

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Run ./bootstrap.sh and add your Marvel API keys."
    exit 1
fi

mkdir -p cache

exec comicoftheday "$@"
