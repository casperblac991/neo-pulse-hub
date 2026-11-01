#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

printf '%s\n' '== Neo Pulse Hub safe check: read/validate/build only =='

if [[ -f scripts/normalize_catalog.py ]]; then
  python3 scripts/normalize_catalog.py --check
fi

python3 -m py_compile \
  backend/ai_engine.py \
  backend/ai_orchestrator.py \
  backend/customer_bot.py

python3 -m unittest discover -s backend -p 'test_ai_engine.py' -v

if command -v pnpm >/dev/null 2>&1; then
  pnpm run build
else
  npm exec --yes pnpm@10.15.1 -- run build
fi

if [[ -d .git ]]; then
  git diff --check
  git status --short
else
  printf '%s\n' 'No .git metadata found; skipped Git diff checks.'
fi

printf '%s\n' '== Safe check completed successfully =='
