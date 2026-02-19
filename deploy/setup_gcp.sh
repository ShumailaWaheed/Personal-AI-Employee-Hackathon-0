#!/bin/bash
# One-time GCP e2-micro instance setup
# Run as: bash deploy/setup_gcp.sh
set -euo pipefail

echo "=== Personal AI Employee - GCP e2-micro Setup ==="

# 1. System updates
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Python 3.13
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev

# 3. Install Node.js 20 + PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# 4. Install git
sudo apt-get install -y git

# 5. Clone application
APP_REPO="${APP_REPO:?Set APP_REPO to your git repo URL}"
git clone "$APP_REPO" /app
cd /app

# 6. Python virtual environment
python3.13 -m venv /app/venv
source /app/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Create directories
mkdir -p /app/logs
mkdir -p /app/AI_Employee_Vault/{Inbox,Needs_Action,Done,Pending_Approval,Approved,Rejected,Plans,Logs,Briefings,Business/Accounting,Business/Social}

# 8. Load secrets
if [ -f /app/deploy/load_secrets.sh ]; then
    bash /app/deploy/load_secrets.sh
fi

# 9. PM2 startup on boot
pm2 startup systemd -u "$USER" --hp "$HOME"

# 10. Vault sync cron (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /app && /app/venv/bin/python -c 'pass' && /app/deploy/sync_vault.sh >> /app/logs/vault-sync.log 2>&1") | crontab -

# 11. Start application
cd /app
source /app/venv/bin/activate
pm2 start ecosystem.cloud.config.js
pm2 save

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Upload secrets: bash deploy/load_secrets.sh (or copy .env manually)"
echo "  2. Init vault repo: VAULT_REPO=... bash deploy/init_vault_repo.sh"
echo "  3. Upload gmail_token.json (generate locally first)"
echo "  4. Configure GCP Uptime Check: http://EXTERNAL_IP:8080/health"
echo "  5. Add firewall rule: allow tcp:8080 from 130.211.0.0/22,35.191.0.0/16"
