#!/usr/bin/env bash
# Prepare systemd USER units for read-only polling. Does NOT enable or start anything.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$ROOT" =~ [[:space:]] ]]; then
  echo 'ABORT: paths with whitespace unsupported by this installer' >&2
  exit 1
fi
CFG_DIR="$HOME/.config/redeti-hermes-autonomy"
UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$CFG_DIR" "$UNIT_DIR"
if [ ! -e "$CFG_DIR/config.json" ]; then
  cp "$ROOT/config/autonomy.example.json" "$CFG_DIR/config.json"
  chmod 600 "$CFG_DIR/config.json"
fi
cat > "$UNIT_DIR/redeti-hermes-autonomy.service" <<EOF
[Unit]
Description=RedeTI Hermes autonomous issue polling (SIMULATION ONLY)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $ROOT/scripts/autonomy_watcher.py --config $CFG_DIR/config.json
NoNewPrivileges=yes
PrivateTmp=yes
EOF
cat > "$UNIT_DIR/redeti-hermes-autonomy.timer" <<'EOF'
[Unit]
Description=Poll GitHub Issues 60 seconds after previous scan completes

[Timer]
OnBootSec=60s
OnUnitInactiveSec=60s
AccuracySec=1s
Unit=redeti-hermes-autonomy.service

[Install]
WantedBy=timers.target
EOF
systemctl --user daemon-reload
echo 'STAGED ONLY: timer NOT enabled or started.'
