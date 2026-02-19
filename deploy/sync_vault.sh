#!/bin/bash
# Cloud-side vault sync script
# Cron: */5 * * * * /app/deploy/sync_vault.sh >> /app/logs/vault-sync.log 2>&1

set -euo pipefail

VAULT_PATH="${VAULT_PATH:-/app/AI_Employee_Vault}"
VAULT_REPO="${VAULT_REPO:-}"
LOG_PREFIX="[vault-sync $(date '+%Y-%m-%d %H:%M:%S')]"

if [ -z "$VAULT_REPO" ]; then
    echo "$LOG_PREFIX VAULT_REPO not set, skipping sync"
    exit 0
fi

cd "$VAULT_PATH"

# Initialize git if not already a repo
if [ ! -d ".git" ]; then
    git init
    git remote add origin "$VAULT_REPO"
    git fetch origin
    git checkout -b main origin/main || git checkout -b main
fi

# Stage all current changes (cloud-processed results)
git add -A

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "cloud-sync: $(date '+%Y-%m-%d %H:%M:%S') - processed updates"
fi

# Pull remote changes (local machine's new tasks)
git fetch origin main 2>/dev/null || {
    echo "$LOG_PREFIX Fetch failed (non-fatal)"
    exit 0
}

# Accept local's Inbox and Needs_Action (local owns these directories)
git checkout origin/main -- Inbox/ Needs_Action/ 2>/dev/null || true

# Merge remaining changes - cloud wins on conflicts
git merge origin/main --strategy-option=ours --no-edit 2>/dev/null || \
    git merge --abort 2>/dev/null || true

# Push cloud's processed results back
git push origin main 2>/dev/null || echo "$LOG_PREFIX Push failed (non-fatal)"

echo "$LOG_PREFIX Sync complete"
