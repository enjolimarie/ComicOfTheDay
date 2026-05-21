#!/usr/bin/env bash
# Stop the Comic of the Day web application
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PID=$(pgrep -f "comicoftheday" 2>/dev/null || true)
if [ -z "$PID" ]; then
    echo "comicoftheday: no running process found"
    exit 0
fi

kill "$PID"
echo "comicoftheday: stopped (PID $PID)"

find "$SCRIPT_DIR/cache" -name "*.tmp" -delete 2>/dev/null || true
