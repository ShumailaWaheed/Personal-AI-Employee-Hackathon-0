
# Personal AI Employee

An autonomous AI system that manages your workflows, handles business tasks, and maintains your online presence - all with human-in-the-loop oversight. Runs 24/7 on cloud with local browser automation support.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What Is This?

A **Personal AI Employee** is an autonomous system that:
- Monitors your task inbox 24/7 (cloud-deployed)
- Watches Gmail, LinkedIn, and WhatsApp for new tasks
- Analyzes, prioritizes, and plans tasks automatically
- Executes approved actions via 7 platform integrations
- Posts to LinkedIn, Facebook, Twitter/X, and Instagram
- Generates weekly business reports and executive briefings
- Maintains human oversight for sensitive actions
- Syncs between cloud and local machine via Git

---

## Features

### Bronze Tier (Foundation)
- File-based task monitoring (Obsidian vault structure)
- Automatic action detection and planning
- Markdown-based workflow with audit trail

### Silver Tier (Integrations)
- Human-in-the-loop (HITL) approval workflow
- Email integration via MCP (Model Context Protocol)
- LinkedIn posting and monitoring
- Risk assessment for sensitive actions
- Approval queue management

### Gold Tier (Autonomous)
- Fully autonomous background processing
- Priority-based task classification (urgent/high/normal/low)
- Domain-aware routing (personal/business/cross-domain)
- Auto-approval for low-risk actions
- 7 MCP integrations:
  - Email (Gmail SMTP)
  - Accounting (Odoo ERP)
  - LinkedIn (API)
  - Facebook Pages (Graph API)
  - WhatsApp (Playwright browser automation)
  - Twitter/X (Playwright browser automation)
  - Instagram (Playwright browser automation)
- Retry queue with exponential backoff
- Weekly audit reports and CEO briefings
- Gmail watcher (OAuth2 API)
- LinkedIn watcher (REST API)
- WhatsApp watcher (Playwright, keyword-triggered)

### Streamlit Web Dashboard
- Password-protected web UI for monitoring and management
- Real-time vault stats, task lists, and analytics
- Dark-themed with Plotly charts and interactive navigation
- Run with: `cd src && streamlit run streamlit_app.py`

### Platinum Tier (Cloud + Local Hybrid)
- 24/7 cloud deployment on GCP e2-micro (free tier)
- Cloud/Local separation — lightweight processes on cloud, browser automation stays local
- Git-based vault sync between cloud and local (every 5 minutes)
- Security isolation via GCP Secret Manager
- Health monitoring HTTP endpoint with GCP Uptime Checks
- PM2 process management with auto-restart
- Docker containerization

---

## Architecture

```
CLOUD (GCP e2-micro - 24/7)              LOCAL (Windows - on demand)
┌──────────────────────────┐              ┌──────────────────────────┐
│  main-processor (Gold)   │              │  whatsapp-watcher        │
│  file-system-watcher     │   Git Sync   │  twitter MCP (Playwright)│
│  gmail-watcher           │ <==========> │  instagram MCP (Playwright│
│  linkedin-watcher        │  every 5min  │                          │
│  health-check (:8080)    │              │                          │
│                          │              │                          │
│  MCP: email, linkedin,   │              │  MCP: whatsapp, twitter, │
│  facebook, odoo (API)    │              │  instagram (browser)     │
└──────────────────────────┘              └──────────────────────────┘
```

### Processor Inheritance

```
GoldProcessor (autonomous, priority-based, scheduled)
  └── SilverProcessor (HITL approval, MCP integration)
        └── VaultProcessor (file monitoring, basic planning)
```

### Vault Structure

```
AI_Employee_Vault/
├── Inbox/                    # New tasks (auto-detected)
├── Needs_Action/             # Pending processing
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved for execution
├── Rejected/                 # User-rejected actions
├── Done/                     # Completed tasks
├── Plans/                    # Generated action plans
├── Business/
│   ├── Accounting/           # Financial records
│   ├── Social/               # Social media activity
│   └── retry_queue.md        # Failed action retry queue
├── Briefings/                # Weekly reports
├── Logs/                     # Daily audit logs (JSON)
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Business context
└── Business_Goals.md         # Strategic objectives
```

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+ (for PM2 process manager)
- Microsoft Edge browser (required for Playwright browser automation)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/ShumailaWaheed/Personal-AI-Employee-Hackathon-0.git
cd Personal-AI-Employee-Hackathon-0

# Install dependencies (local with browser automation)
pip install -r requirements-local.txt

# Or cloud-only (no Playwright)
pip install -r requirements.txt

# Install PM2
npm install -g pm2

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Run Locally

```bash
# Start all processes with PM2
pm2 start ecosystem.config.js

# Or run directly
python src/main.py

# Or launch the web dashboard
cd src && streamlit run streamlit_app.py
```

### Deploy to Cloud (GCP)

```bash
# Option 1: Docker
docker build -t ai-employee .
docker run -d --env-file .env -p 8080:8080 ai-employee

# Option 2: Direct on GCP e2-micro
bash deploy/setup_gcp.sh
pm2 start ecosystem.cloud.config.js
```

See [Cloud Deployment](#cloud-deployment) for detailed setup.

---

## Usage

### Creating Tasks

Add a markdown file to `Inbox/`:

```markdown
---
priority: high
domain: business
---
# LinkedIn Post

Post on LinkedIn:

"Excited to share our latest milestone!
#AI #Innovation #Success"
```

The system automatically:
1. Detects the new task
2. Analyzes and prioritizes it
3. Creates a plan
4. Requests approval (if sensitive)
5. Executes upon approval
6. Logs the result

### Approving Actions

1. Check `Pending_Approval/` for approval requests
2. Review the proposed action
3. **Approve**: Move file to `Approved/`
4. **Reject**: Move file to `Rejected/`

---

## Integrations

### Social Media (Playwright - Free)

Twitter/X, Instagram, and WhatsApp use **Playwright browser automation** — no paid API required.

```env
# Twitter/X
TWITTER_MODE=playwright
TWITTER_HEADLESS=false
TWITTER_SESSION_DIR=./twitter_session

# Instagram
INSTAGRAM_MODE=playwright
INSTAGRAM_SESSION_DIR=./twitter_session
INSTAGRAM_HEADLESS=false

# WhatsApp
WHATSAPP_MODE=playwright
```

First run opens a browser for manual login. Session persists after that.

### LinkedIn

```env
LINKEDIN_ACCESS_TOKEN=your-token
LINKEDIN_PERSONAL_ACCOUNT_ID=your-id
```

### Facebook Pages

```env
FACEBOOK_ACCESS_TOKEN=your-page-token
FACEBOOK_PAGE_ID=your-page-id
```

### Email (Gmail)

```env
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
```

### Gmail Watcher (OAuth2)

```env
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
GMAIL_TOKEN_FILE=gmail_token.json
```

### Odoo Accounting

```env
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_API_KEY=your_api_key
```

---

## Cloud Deployment

### GCP Free Tier (e2-micro)

The Platinum tier runs on Google Cloud's always-free e2-micro instance (0.25 vCPU, 1GB RAM).

**RAM Budget (~585MB of 1024MB):**

| Process | RAM |
|---------|-----|
| main-processor | ~80MB |
| file-system-watcher | ~50MB |
| gmail-watcher | ~60MB |
| linkedin-watcher | ~60MB |
| health-check | ~25MB |
| PM2 daemon | ~60MB |
| OS | ~200MB |

**Cloud vs Local Split:**
- **Cloud**: Lightweight watchers + API-only MCP servers (email, linkedin, facebook, odoo)
- **Local**: Playwright-based services (whatsapp, twitter, instagram) — too heavy for 1GB RAM

### Setup Steps

1. Create GCP e2-micro instance (us-central1, Debian)
2. Run `bash deploy/setup_gcp.sh`
3. Upload secrets to GCP Secret Manager
4. Initialize vault git repo: `VAULT_REPO=... bash deploy/init_vault_repo.sh`
5. Upload `gmail_token.json` (generate locally first)
6. Start: `pm2 start ecosystem.cloud.config.js`
7. Configure GCP Uptime Check on `http://EXTERNAL_IP:8080/health`

### Vault Git Sync

Cloud and local sync every 5 minutes via Git:
- **Local owns**: `Inbox/`, `Needs_Action/` (user creates tasks)
- **Cloud owns**: `Done/`, `Plans/`, `Logs/`, `Briefings/` (system processes)

### Health Monitoring

```bash
curl http://EXTERNAL_IP:8080/health
```

Returns JSON with process status, disk usage, vault stats, and uptime.

### Security

- Secrets via GCP Secret Manager (no `.env` on cloud)
- SSH-only access (no password auth)
- Firewall: port 8080 open only to GCP health checker IPs
- Browser sessions never committed to Git

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tier tests
python -m pytest tests/test_gold_processor.py -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Test Coverage**: 179 tests across Bronze, Silver, and Gold tiers

---

## Project Structure

```
personal-ai-employee/
├── src/
│   ├── main.py                      # Entry point
│   ├── streamlit_app.py             # Web dashboard UI
│   ├── config/
│   │   ├── settings.py              # Configuration loader
│   │   └── deployment.py            # Cloud/local mode helpers
│   ├── processors/
│   │   ├── vault_processor.py       # Bronze tier
│   │   ├── silver_processor.py      # Silver tier
│   │   └── gold_processor.py        # Gold tier
│   ├── watchers/
│   │   ├── base_watcher.py          # Abstract base
│   │   ├── file_system_watcher.py   # Filesystem (watchdog)
│   │   ├── gmail_watcher.py         # Gmail API (OAuth2)
│   │   ├── linkedin_watcher.py      # LinkedIn API
│   │   └── whatsapp_watcher.py      # WhatsApp (Playwright)
│   ├── utils/
│   │   ├── mcp_client.py            # MCP JSON-RPC client
│   │   ├── priority_classifier.py   # Task prioritization
│   │   ├── domain_classifier.py     # Personal/business routing
│   │   ├── sensitive_action_detector.py
│   │   ├── retry_manager.py         # Exponential backoff
│   │   ├── scheduler.py             # Weekly reports
│   │   └── audit_logger.py          # JSON audit trail
│   └── models/                      # Data models
├── mcp/                             # MCP servers (JSON-RPC/stdio)
│   ├── email_server.py              # Gmail SMTP
│   ├── odoo_server.py               # Odoo XML-RPC
│   ├── facebook_server.py           # Graph API
│   ├── linkedin_server.py           # LinkedIn API
│   ├── whatsapp_server.py           # Playwright
│   ├── twitter_server.py            # Playwright + Edge
│   └── instagram_server.py          # Playwright + Edge
├── deploy/                          # Cloud deployment
│   ├── health_check.py              # HTTP health endpoint
│   ├── setup_gcp.sh                 # GCP instance bootstrap
│   ├── load_secrets.sh              # Secret Manager loader
│   ├── sync_vault.sh                # Cloud vault sync
│   ├── local_vault_sync.sh          # Local vault sync
│   └── init_vault_repo.sh           # Vault git init
├── tests/                           # 179 tests
├── specs/                           # Feature specifications
├── ecosystem.config.js              # PM2 config (local, all processes)
├── ecosystem.cloud.config.js        # PM2 config (cloud, no Playwright)
├── Dockerfile                       # Cloud container
├── requirements.txt                 # Cloud dependencies
├── requirements-local.txt           # Local dependencies (+ Playwright)
└── AI_Employee_Vault/               # Working vault
```

---

## Configuration

```env
# Deployment Mode
DEPLOYMENT_MODE=local              # 'local' or 'cloud'

# Gold Tier
GOLD_TIER_ENABLED=true
AUTO_APPROVE_LOW_RISK=false
PROCESSING_INTERVAL=30

# Scheduling
AUDIT_SCHEDULE=monday:09:00
BRIEFING_SCHEDULE=monday:10:00

# WhatsApp Keywords (triggers action file creation)
WHATSAPP_TRIGGER_KEYWORDS=urgent,bhai

# Dry Run (test without executing)
DRY_RUN=false

# Dashboard Auth
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=your-password

# Health Check (cloud)
HEALTH_PORT=8080

# Vault Git Sync (platinum)
VAULT_REPO=git@github.com:user/vault.git
```

---

## Troubleshooting

**Twitter/Instagram post fails with overlay error**
- Uses Ctrl+Enter (Twitter) and JavaScript clicks (Instagram) to bypass UI overlays
- Make sure `TWITTER_HEADLESS=false` for first login

**Gmail watcher not starting on cloud**
- Generate `gmail_token.json` locally first, then upload to cloud
- Token auto-refreshes after initial OAuth flow

**WhatsApp not connecting**
- Run locally with `WHATSAPP_HEADLESS=false`
- Scan QR code on first run, session persists after

**MCP server "not available in cloud mode"**
- Browser-based servers (whatsapp, twitter, instagram) only run locally
- Cloud mode automatically falls back to API mode or returns gracefully

**Health check returns 503**
- Check PM2 process status: `pm2 status`
- View logs: `pm2 logs`

---

## Security

- PII sanitization in logs
- Credentials via environment variables / GCP Secret Manager
- `.env` and browser sessions excluded from git
- Human approval required for sensitive actions
- Complete audit trail (JSON logs)
- Rate limiting on external APIs
- Cloud firewall: only health checker IPs on port 8080

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Acknowledgments

- Built with [Claude AI](https://claude.ai) (Anthropic)
- MCP (Model Context Protocol) architecture
- Playwright for browser automation
- PM2 for process management

---

**Built by Shumaila Waheed**
