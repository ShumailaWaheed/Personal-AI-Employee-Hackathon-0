# Quickstart: Gold Tier Autonomous System

**Feature Branch**: `004-gold-tier`
**Prerequisites**: Bronze + Silver tier implemented and working

## 1. Environment Setup

### Required Environment Variables

Add to `.env` (in addition to existing Bronze/Silver vars):

```bash
# Gold Tier - Autonomous Processing
GOLD_TIER_ENABLED=true
AUTO_APPROVE_LOW_RISK=false
PROCESSING_INTERVAL=30

# Gold Tier - Scheduling
AUDIT_SCHEDULE=monday:09:00
BRIEFING_SCHEDULE=monday:10:00

# Odoo Accounting MCP
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_API_KEY=your_api_key

# Facebook MCP
FACEBOOK_BEARER_TOKEN=your_bearer_token
FACEBOOK_API_KEY=your_api_key
FACEBOOK_API_SECRET=your_api_secret

# WhatsApp MCP (extends existing)
WHATSAPP_MODE=playwright
WHATSAPP_API_TOKEN=your_token

# LinkedIn MCP (extends existing)
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSONAL_ACCOUNT_ID=your_urn
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

New Gold-tier dependencies (added to requirements.txt):
- `xmlrpc.client` (stdlib, for Odoo)
- `requests>=4.14.0` (Facebook API v2 client)
- `schedule>=1.2.0` (lightweight scheduling, optional)

## 2. Vault Directory Setup

Gold tier extends the Silver vault with additional directories:

```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Done/
├── Logs/
├── Plans/
├── Business/              # NEW: Gold tier
│   ├── Accounting/        # Transaction records from Odoo
│   ├── Social/            # Social media activity records
│   ├── retry_queue.md     # Persistent retry queue
│   ├── integration_status.json  # MCP server health
│   └── scheduler_state.json     # Scheduled task tracking
├── Briefings/             # NEW: Gold tier
│   ├── audit_YYYY-MM-DD.md
│   └── ceo_briefing_YYYY-MM-DD.md
├── Dashboard.md
├── Company_Handbook.md
└── Business_Goals.md      # NEW: Gold tier
```

## 3. Running the System

### Start with PM2 (recommended)

```bash
pm2 start ecosystem.config.js
```

### Start manually

```bash
python src/main.py
```

### Verify Gold tier is active

Check `Dashboard.md` for:
- Gold tier status: enabled/disabled
- Integration health per MCP server
- Autonomous processing status

## 4. Creating Action Items

Place Markdown files in `/Needs_Action/` with optional frontmatter:

```markdown
---
priority: high
domain: business
---
# Record Q1 Software Expenses

Record the following expenses in the accounting system:
- Software licenses: $500
- Cloud hosting: $200
- Development tools: $150
```

The system will automatically:
1. Detect the file within 30 seconds
2. Classify priority and domain
3. Generate a plan in `/Plans/`
4. Create an approval request in `/Pending_Approval/` (if external action)
5. Execute via MCP after approval
6. Archive to `/Done/`

## 5. Approving Actions

1. Check `/Pending_Approval/` for new requests
2. Review the approval file contents
3. Move to `/Approved/` to execute, or `/Rejected/` to cancel
4. The system processes the decision on the next cycle

## 6. Monitoring

- **Dashboard**: `AI_Employee_Vault/Dashboard.md` (auto-updated)
- **Audit Logs**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Integration Health**: `AI_Employee_Vault/Business/integration_status.json`
- **Weekly Reports**: `AI_Employee_Vault/Briefings/`

## 7. Dry Run Mode

Set `DRY_RUN=true` in `.env` to test without executing external actions. All operations are logged but no MCP calls are made.
