#!/usr/bin/env bash
# First-time project setup: creates venv, installs deps, copies .env.example
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Creating Python virtual environment..."
python3 -m venv venv

echo "==> Installing dependencies..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet -e .

echo "==> Creating cache directory..."
mkdir -p cache

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "  Created .env from .env.example"
    echo "  Edit .env and add your Marvel API keys before starting the app."
    echo ""
fi

echo "==> Bootstrap complete."
echo "    Run ./start-comicoftheday.sh to launch the app."
