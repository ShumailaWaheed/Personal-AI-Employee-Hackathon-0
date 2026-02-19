#!/bin/bash
# Local (Windows) vault sync - run via Git Bash or WSL
# Windows Task Scheduler: every 5 minutes
# Command: "C:\Program Files\Git\bin\bash.exe" --login -i "D:\...\deploy\local_vault_sync.sh"

set -euo pipefail

VAULT_PATH="${VAULT_PATH:-D:/Hachathon-0/personal-ai-employee/AI_Employee_Vault}"

cd "$VAULT_PATH"

if [ ! -d ".git" ]; then
    echo "Vault not initialized as git repo. Run init_vault_repo.sh first."
    exit 1
fi

# Pull cloud's processed results (Done, Plans, Logs, Briefings)
git fetch origin main 2>/dev/null || {
    echo "Fetch failed - check network"
    exit 1
}
git merge origin/main --no-edit 2>/dev/null || {
    echo "Merge conflict detected - resolving with cloud priority for processed files"
    git checkout --theirs Done/ Plans/ Logs/ Briefings/ Business/ 2>/dev/null || true
    git add -A
    git commit -m "local-sync: resolved conflicts (cloud wins for processed files)" 2>/dev/null || true
}

# Push local changes (new tasks in Inbox, Needs_Action)
git add Inbox/ Needs_Action/ Dashboard.md Company_Handbook.md Business_Goals.md 2>/dev/null || true

if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "local-sync: $(date '+%Y-%m-%d %H:%M:%S') - new tasks"
    git push origin main
fi

echo "Local vault sync complete at $(date)"
