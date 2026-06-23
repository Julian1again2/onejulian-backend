#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"
EMAIL="${EMAIL:-automationfunding+$(date +%s)@gmail.com}"
PASSWORD="${PASSWORD:-M34g4n123}"
FULL_NAME="${FULL_NAME:-Automation Funding}"
TMP_DIR="$(mktemp -d)"
TOKEN=""
DELIVERY_ID=""

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
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
  local name="$1"
  local method="$2"
  local url="$3"
  local expected="$4"
  local body_file="$5"
  shift 5

  local response_file="$TMP_DIR/${name}.body"
  local status_file="$TMP_DIR/${name}.status"

  curl -sS -X "$method" "$url" \
    -H 'accept: application/json' \
    "$@" \
    -o "$response_file" \
    -w '%{http_code}' > "$status_file"

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

  if [[ -n "$body_file" ]]; then
    cp "$response_file" "$body_file"
  fi
}

echo "BASE_URL=$BASE_URL"
echo "EMAIL=$EMAIL"
echo "FULL_NAME=$FULL_NAME"

echo
echo "1) Register"
REGISTER_BODY="$TMP_DIR/register.json"
REGISTER_PAYLOAD="$TMP_DIR/register_payload.json"
cat > "$REGISTER_PAYLOAD" <<JSON
{
  "email": "$EMAIL",
  "full_name": "$FULL_NAME",
  "password": "$PASSWORD"
}
JSON
request register POST "$BASE_URL/api/v1/auth/register" 201 "$REGISTER_BODY" \
  -H 'Content-Type: application/json' \
  --data-binary @"$REGISTER_PAYLOAD"
cat "$REGISTER_BODY"
echo

echo
echo "2) Login"
LOGIN_BODY="$TMP_DIR/login.json"
request login POST "$BASE_URL/api/v1/auth/login" 200 "$LOGIN_BODY" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=$EMAIL" \
  --data-urlencode "password=$PASSWORD"
cat "$LOGIN_BODY"
echo
TOKEN="$(json_get "$LOGIN_BODY" access_token)"
echo "TOKEN acquired"

echo
echo "3) Get current client"
ME_BODY="$TMP_DIR/me.json"
request me GET "$BASE_URL/api/v1/clients/me" 200 "$ME_BODY" \
  -H "Authorization: Bearer $TOKEN"
cat "$ME_BODY"
echo

echo
echo "4) Create delivery"
CREATE_BODY="$TMP_DIR/create_delivery.json"
CREATE_PAYLOAD="$TMP_DIR/create_payload.json"
cat > "$CREATE_PAYLOAD" <<JSON
{
  "title": "Smoke Test Delivery",
  "description": "Created by automated smoke test",
  "status": "pending"
}
JSON
request create_delivery POST "$BASE_URL/api/v1/deliveries/" 201 "$CREATE_BODY" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @"$CREATE_PAYLOAD"
cat "$CREATE_BODY"
echo
DELIVERY_ID="$(json_get "$CREATE_BODY" id)"
echo "DELIVERY_ID=$DELIVERY_ID"

echo
echo "5) List deliveries"
LIST_BODY="$TMP_DIR/list_deliveries.json"
request list_deliveries GET "$BASE_URL/api/v1/deliveries/" 200 "$LIST_BODY" \
  -H "Authorization: Bearer $TOKEN"
cat "$LIST_BODY"
echo

echo
echo "6) Get one delivery"
GET_ONE_BODY="$TMP_DIR/get_delivery.json"
request get_delivery GET "$BASE_URL/api/v1/deliveries/$DELIVERY_ID" 200 "$GET_ONE_BODY" \
  -H "Authorization: Bearer $TOKEN"
cat "$GET_ONE_BODY"
echo

echo
echo "7) Update delivery"
PATCH_BODY="$TMP_DIR/patch_delivery.json"
PATCH_PAYLOAD="$TMP_DIR/patch_payload.json"
cat > "$PATCH_PAYLOAD" <<JSON
{
  "status": "completed",
  "description": "Updated by automated smoke test"
}
JSON
request patch_delivery PATCH "$BASE_URL/api/v1/deliveries/$DELIVERY_ID" 200 "$PATCH_BODY" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @"$PATCH_PAYLOAD"
cat "$PATCH_BODY"
echo

echo
echo "8) Delete delivery"
request delete_delivery DELETE "$BASE_URL/api/v1/deliveries/$DELIVERY_ID" 204 "" \
  -H "Authorization: Bearer $TOKEN"
echo "delete ok"

echo
echo "9) Confirm deleted"
CONFIRM_BODY="$TMP_DIR/confirm_deleted.json"
request confirm_deleted GET "$BASE_URL/api/v1/deliveries/$DELIVERY_ID" 404 "$CONFIRM_BODY" \
  -H "Authorization: Bearer $TOKEN"
cat "$CONFIRM_BODY"
echo

echo
echo "Smoke test PASSED"
echo "User: $EMAIL"
echo "Deleted delivery id: $DELIVERY_ID"
