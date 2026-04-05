#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/projects/ops-dashboard
while true; do
  python3 server.py
  sleep 2
done
