#!/usr/bin/env bash
# start_https.sh — start combined API + static file server over HTTPS
# Usage: ./start_https.sh

set -e
cd "$(dirname "$0")"

PYTHON=.venv/bin/python3

# Load secrets from .env.local (never committed to git)
if [ -f .env.local ]; then
  # shellcheck disable=SC1091
  set -a && source .env.local && set +a
fi

# Fallback: set these here only for local dev if .env.local is absent
# export OPENAI_API_KEY=""
# export SMTP_USER=""
# export SMTP_PASS=""

# Kill anything already on port 8443
lsof -ti:8443 | xargs kill -9 2>/dev/null || true
# Also kill old separate static server if running
lsof -ti:8444 | xargs kill -9 2>/dev/null || true

echo "======================================================"
echo " USS Pampanito Tour — HTTPS Server"
echo "======================================================"
echo ""
echo " On your iPhone, open Safari and go to:"
echo ""
echo "   https://192.168.0.108:8443/web/tour.html"
echo ""
echo " API base URL (in Settings on the page):"
echo "   https://192.168.0.108:8443"
echo ""
echo " Press Ctrl-C to stop."
echo "======================================================"
echo ""

$PYTHON -m uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile certs/key.pem \
  --ssl-certfile certs/cert.pem \
  --log-level warning