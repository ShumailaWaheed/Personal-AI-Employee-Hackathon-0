# Silver Tier Deployment Guide

## Prerequisites
- Python 3.13+
- Node.js 18+ (for PM2)
- PM2 installed globally: `npm install -g pm2`
- Playwright installed: `pip install playwright && playwright install`

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start with PM2
```bash
pm2 start ecosystem.config.js
pm2 status
```

### 4. Monitor
```bash
pm2 logs          # View all logs
pm2 monit         # Real-time monitoring
pm2 status        # Process status
```

### 5. Stop
```bash
pm2 stop all
pm2 delete all
```

## Manual Start (without PM2)
```bash
python src/main.py
```

## Directory Structure
```
AI_Employee_Vault/
  Inbox/              - Drop new tasks here
  Needs_Action/       - Tasks being processed
  Pending_Approval/   - Actions waiting for human approval
  Approved/           - Move files here to approve
  Rejected/           - Move files here to reject
  Done/               - Completed tasks
  Logs/               - JSON audit logs
  Plans/              - Generated plan files
  Dashboard.md        - System status dashboard
```

## HITL Approval Workflow
1. System detects sensitive action in Needs_Action
2. Creates approval request in Pending_Approval
3. Human reviews and moves to Approved or Rejected
4. If approved, action executes via MCP server
5. Result is logged and file moves to Done

## Troubleshooting
- **WhatsApp session expired**: Delete `whatsapp_session/` directory and restart
- **LinkedIn API 401**: Refresh your LinkedIn access token in .env
- **PM2 crash loop**: Check `pm2 logs <process-name>` for errors
- **MCP server timeout**: Verify .env email credentials are correct
