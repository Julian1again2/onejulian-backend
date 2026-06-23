#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$HOME/onejulian/backend"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > "$HOME/onejulian/backend/uvicorn-8001.log" 2>&1 &
echo $! > "$HOME/onejulian/backend/uvicorn-8001.pid"
sleep 3
cat "$HOME/onejulian/backend/uvicorn-8001.pid"
