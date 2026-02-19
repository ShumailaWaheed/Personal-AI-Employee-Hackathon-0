#!/bin/bash
# One-time: Initialize AI_Employee_Vault as a git repo
# Usage: VAULT_REPO=git@github.com:user/vault.git bash deploy/init_vault_repo.sh

set -euo pipefail

VAULT_PATH="${VAULT_PATH:-./AI_Employee_Vault}"
VAULT_REPO="${VAULT_REPO:?VAULT_REPO must be set (e.g. git@github.com:user/vault.git)}"

cd "$VAULT_PATH"

if [ -d ".git" ]; then
    echo "Vault is already a git repo. Skipping init."
    exit 0
fi

# Create vault .gitignore
cat > .gitignore << 'EOF'
*.tmp
.DS_Store
__pycache__/
*.pyc
Thumbs.db
EOF

git init
git remote add origin "$VAULT_REPO"
git add -A
git commit -m "Initial vault commit"
git branch -M main
git push -u origin main

echo "Vault initialized and pushed to $VAULT_REPO"
