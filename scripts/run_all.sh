#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
"$DIR/onejulian_smoke_test.sh"
echo
"$DIR/onejulian_negative_test.sh"
