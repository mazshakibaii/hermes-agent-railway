#!/usr/bin/env bash
set -e

AUTO_UPDATE="${AUTO_UPDATE:-true}"

if [ "$AUTO_UPDATE" = "true" ]; then
  echo "Checking for Hermes updates..."
  cd /opt/hermes-agent
  if git pull --recurse-submodules 2>&1 | grep -v 'Already up to date'; then
    echo "Updating dependencies..."
    VIRTUAL_ENV=/opt/hermes-agent/venv uv pip install -e ".[all]" --quiet
    echo "Update complete."
  else
    echo "Already up to date."
  fi
fi

PORT="${PORT:-8080}"
DASHBOARD_PORT=9119
DASHBOARD_USER="${DASHBOARD_USER:-admin}"
DASHBOARD_PASSWORD="${DASHBOARD_PASSWORD:-}"

if [ -z "$DASHBOARD_PASSWORD" ]; then
  echo "ERROR: DASHBOARD_PASSWORD must be set. Your dashboard would be publicly accessible without it."
  exit 1
fi

HASHED_PASSWORD=$(caddy hash-password --plaintext "$DASHBOARD_PASSWORD")

cat > /etc/caddy/Caddyfile <<EOF
:${PORT} {
  basicauth /* {
    ${DASHBOARD_USER} ${HASHED_PASSWORD}
  }
  reverse_proxy localhost:${DASHBOARD_PORT}
}
EOF

hermes dashboard --host 127.0.0.1 --port "$DASHBOARD_PORT" --no-open &

exec caddy run --config /etc/caddy/Caddyfile
