#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$HOME/onejulian/backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000
