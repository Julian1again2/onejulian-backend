#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export BASE_URL

bash "$SCRIPT_DIR/onejulian_smoke_test.sh"
echo
bash "$SCRIPT_DIR/onejulian_negative_test.sh"
