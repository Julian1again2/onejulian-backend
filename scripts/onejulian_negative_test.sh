#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"
EMAIL="${EMAIL:-automationfunding+neg$(date +%s)@gmail.com}"
PASSWORD="${PASSWORD:-M34g4n123}"
FULL_NAME="${FULL_NAME:-Automation Funding Negative}"
TMP_DIR="$(mktemp -d)"
TOKEN=""

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}
need_cmd curl
need_cmd python

json_get() {
  local file="$1"
  local expr="$2"
  python - "$file" "$expr" <<'PY'
import json, sys
path, expr = sys.argv[1], sys.argv[2]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
parts = [p for p in expr.split('.') if p]
cur = data
for p in parts:
    if isinstance(cur, list):
        cur = cur[int(p)]
    else:
        cur = cur[p]
if isinstance(cur, (dict, list)):
    print(json.dumps(cur, separators=(',', ':')))
else:
    print(cur)
PY
}

request() {
  local name="$1" method="$2" url="$3" expected="$4" body_file="$5"
  shift 5
  local response_file="$TMP_DIR/${name}.body"
  local status_file="$TMP_DIR/${name}.status"
  curl -sS -X "$method" "$url" -H 'accept: application/json' "$@" -o "$response_file" -w '%{http_code}' > "$status_file"
  local status
  status="$(cat "$status_file")"
  echo "[$name] HTTP $status"
  if [[ "$status" != "$expected" ]]; then
    echo "[$name] Expected HTTP $expected but got $status" >&2
    echo "[$name] Response body:" >&2
    cat "$response_file" >&2
    echo >&2
    exit 1
  fi
  [[ -n "$body_file" ]] && cp "$response_file" "$body_file"
}

echo "BASE_URL=$BASE_URL"
echo "EMAIL=$EMAIL"

echo
echo "1) Register valid user for auth-negative checks"
REGISTER_BODY="$TMP_DIR/register.json"
REGISTER_PAYLOAD="$TMP_DIR/register_payload.json"
cat > "$REGISTER_PAYLOAD" <<JSON
{"email":"$EMAIL","full_name":"$FULL_NAME","password":"$PASSWORD"}
JSON
request register POST "$BASE_URL/api/v1/auth/register" 201 "$REGISTER_BODY" -H 'Content-Type: application/json' --data-binary @"$REGISTER_PAYLOAD"
cat "$REGISTER_BODY"
echo

echo
echo "2) Bad login should fail"
BAD_LOGIN_BODY="$TMP_DIR/bad_login.json"
request bad_login POST "$BASE_URL/api/v1/auth/login" 401 "$BAD_LOGIN_BODY" -H 'Content-Type: application/x-www-form-urlencoded' --data-urlencode "username=$EMAIL" --data-urlencode 'password=wrongpassword'
cat "$BAD_LOGIN_BODY"
echo

echo
echo "3) Good login for remaining checks"
LOGIN_BODY="$TMP_DIR/login.json"
request login POST "$BASE_URL/api/v1/auth/login" 200 "$LOGIN_BODY" -H 'Content-Type: application/x-www-form-urlencoded' --data-urlencode "username=$EMAIL" --data-urlencode "password=$PASSWORD"
cat "$LOGIN_BODY"
echo
TOKEN="$(json_get "$LOGIN_BODY" access_token)"

echo
echo "4) Protected route without token should fail"
NO_TOKEN_BODY="$TMP_DIR/no_token.json"
request no_token GET "$BASE_URL/api/v1/clients/me" 401 "$NO_TOKEN_BODY"
cat "$NO_TOKEN_BODY"
echo

echo
echo "5) Protected route with bad token should fail"
BAD_TOKEN_BODY="$TMP_DIR/bad_token.json"
request bad_token GET "$BASE_URL/api/v1/clients/me" 401 "$BAD_TOKEN_BODY" -H 'Authorization: Bearer not-a-real-token'
cat "$BAD_TOKEN_BODY"
echo

echo
echo "6) Invalid create payload should fail"
BAD_CREATE_BODY="$TMP_DIR/bad_create.json"
BAD_CREATE_PAYLOAD="$TMP_DIR/bad_create_payload.json"
cat > "$BAD_CREATE_PAYLOAD" <<JSON
{"description":"missing required title"}
JSON
request bad_create POST "$BASE_URL/api/v1/deliveries/" 422 "$BAD_CREATE_BODY" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' --data-binary @"$BAD_CREATE_PAYLOAD"
cat "$BAD_CREATE_BODY"
echo

echo
echo "7) Non-existent delivery should be 404"
NOT_FOUND_BODY="$TMP_DIR/not_found.json"
request not_found GET "$BASE_URL/api/v1/deliveries/999999" 404 "$NOT_FOUND_BODY" -H "Authorization: Bearer $TOKEN"
cat "$NOT_FOUND_BODY"
echo

echo
echo "Negative test PASSED"
