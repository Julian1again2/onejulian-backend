#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$HOME/onejulian/backend"
ss -ltnp | grep ':8000' > "$HOME/onejulian/backend/port8000.txt" || true
pid="$(ss -ltnp | awk '/:8000/ {match($0,/pid=([0-9]+)/,m); if (m[1] != "") print m[1]}' | head -n 1)"
if [ -n "${pid:-}" ]; then
  kill "$pid" || true
  sleep 2
fi
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
