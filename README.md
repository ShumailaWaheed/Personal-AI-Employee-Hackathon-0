# Personal AI Employee

An autonomous AI system that manages your workflows, handles business tasks, and maintains your online presence - all with human-in-the-loop oversight.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 What Is This?

A **Personal AI Employee** is an autonomous system that:
- 📥 Monitors your task inbox 24/7
- 🧠 Analyzes, prioritizes, and plans tasks
- ✅ Executes approved actions via integrations
- 📊 Generates weekly business reports
- 🔒 Maintains human oversight for sensitive actions

Think of it as a digital assistant that actually *does* work, not just answers questions.

---

## ✨ Features

### 🥉 Bronze Tier (Foundation)
- ✅ File-based task monitoring (Obsidian vault structure)
- ✅ Automatic action detection and planning
- ✅ Markdown-based workflow
- ✅ Logging and audit trail

### 🥈 Silver Tier (Integrations)
- ✅ Human-in-the-loop approval workflow
- ✅ Email integration via MCP (Model Context Protocol)
- ✅ Multi-platform support (LinkedIn, Email)
- ✅ Risk assessment for actions
- ✅ Approval queue management

### 🥇 Gold Tier (Autonomous)
- ✅ Fully autonomous background processing
- ✅ Priority-based task classification
- ✅ Domain-aware routing (personal/business/cross-domain)
- ✅ 5 MCP integrations:
  - 📧 Email (Gmail SMTP)
  - 💼 Accounting (Odoo)
  - 🔗 LinkedIn
  - 📘 Facebook Pages
  - 💬 WhatsApp
- ✅ Retry queue with exponential backoff
- ✅ Weekly audit reports and executive briefings
- ✅ Business intelligence dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Gold Tier Processor                    │
│  (Autonomous, Priority-Based, Multi-Domain, Scheduled)  │
└─────────────────┬───────────────────────────────────────┘
                  │ extends
┌─────────────────▼───────────────────────────────────────┐
│                  Silver Tier Processor                   │
│      (HITL Approval, MCP Integration, Multi-Watch)      │
└─────────────────┬───────────────────────────────────────┘
                  │ extends
┌─────────────────▼───────────────────────────────────────┐
│                  Bronze Tier Processor                   │
│          (File Monitoring, Basic Planning)              │
└─────────────────────────────────────────────────────────┘
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
│   ├── Accounting/          # Financial records
│   ├── Social/              # Social media activity
│   └── retry_queue.md       # Failed action retry queue
├── Briefings/               # Weekly reports
├── Logs/                    # Daily audit logs (JSON)
├── Dashboard.md             # Real-time status dashboard
├── Company_Handbook.md      # Business context
└── Business_Goals.md        # Strategic objectives
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+ (3.14 works)
- Git
- API keys for integrations (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/personal-ai-employee.git
cd personal-ai-employee

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Basic Configuration

Edit `.env`:

```env
# Vault Configuration
VAULT_PATH=./AI_Employee_Vault
CHECK_INTERVAL=60
LOG_LEVEL=INFO
DRY_RUN=false

# Gold Tier
GOLD_TIER_ENABLED=true
AUTO_APPROVE_LOW_RISK=false
PROCESSING_INTERVAL=30

# Integrations (optional)
LINKEDIN_ACCESS_TOKEN=your-token
LINKEDIN_PERSONAL_ACCOUNT_ID=your-id

FACEBOOK_ACCESS_TOKEN=your-page-token
FACEBOOK_PAGE_ID=your-page-id

EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
```

### Run

```bash
# Start the AI Employee
python src/main.py
```

---

## 📖 Usage

### Creating Tasks

1. **Add a task file to `/Inbox/`:**

```markdown
---
priority: high
domain: business
---
# LinkedIn Post

Post on LinkedIn:

"Just achieved a major milestone! 🎉

Details about your achievement...

#AI #Innovation #Success"
```

2. **The system automatically:**
   - Detects the new task
   - Analyzes and prioritizes it
   - Creates a plan
   - Requests approval (if needed)
   - Executes upon approval
   - Logs the result

### Approving Actions

1. Check `/Pending_Approval/` for approval requests
2. Review the proposed action
3. **Approve**: Move to `/Approved/`
4. **Reject**: Move to `/Rejected/`

The system executes approved actions automatically.

---

## 🔌 Integrations

### LinkedIn Setup

1. Get LinkedIn OAuth token: [docs/linkedin-setup.md](docs/linkedin-setup.md)
2. Add to `.env`:
   ```env
   LINKEDIN_ACCESS_TOKEN=your-token
   LINKEDIN_PERSONAL_ACCOUNT_ID=your-id
   ```

### Facebook Setup

1. Get Facebook Page Access Token: [docs/facebook-setup.md](docs/facebook-setup.md)
2. Add to `.env`:
   ```env
   FACEBOOK_ACCESS_TOKEN=your-page-token
   FACEBOOK_PAGE_ID=your-page-id
   ```

### Email Setup

Gmail App Password required:
```env
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-16-char-app-password
```

### Odoo Accounting (Optional)

```env
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_API_KEY=your_api_key
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific tier tests
python -m pytest tests/test_gold_processor.py -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Test Coverage**: 152 tests across Bronze, Silver, and Gold tiers

---

## 📊 Monitoring

### Dashboard

Real-time status: `AI_Employee_Vault/Dashboard.md`

```markdown
# AI Employee Dashboard

Last Updated: 2026-02-09 15:30:00

## Status
- System: ✅ Running (Gold Tier)
- Tasks Processed Today: 3
- Pending Approvals: 0

## Recent Activity
- [15:25] LinkedIn post published
- [15:20] Facebook post approved
- [15:15] Email sent
```

### Audit Logs

Daily JSON logs: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

```json
{
  "timestamp": "2026-02-09T15:25:30.123456",
  "action_type": "linkedin_post",
  "actor": "system",
  "result": "success",
  "post_id": "urn:li:share:1234567890"
}
```

### Weekly Reports

Executive briefings: `AI_Employee_Vault/Briefings/`

- `audit_YYYY-MM-DD.md` - Detailed audit
- `ceo_briefing_YYYY-MM-DD.md` - Executive summary

---

## 🛠️ Development

### Project Structure

```
personal-ai-employee/
├── src/
│   ├── main.py                      # Entry point
│   ├── processors/
│   │   ├── vault_processor.py       # Bronze tier
│   │   ├── silver_processor.py      # Silver tier
│   │   └── gold_processor.py        # Gold tier
│   ├── watchers/
│   │   ├── base_watcher.py
│   │   ├── file_system_watcher.py
│   │   ├── linkedin_watcher.py
│   │   └── whatsapp_watcher.py
│   ├── utils/
│   │   ├── mcp_client.py            # MCP integration
│   │   ├── priority_classifier.py
│   │   ├── domain_classifier.py
│   │   ├── retry_manager.py
│   │   └── audit_logger.py
│   ├── models/
│   │   ├── action_file.py
│   │   ├── approval_request.py
│   │   └── audit_log_entry.py
│   └── config/
│       └── settings.py
├── mcp/                             # MCP servers
│   ├── email_server.py
│   ├── odoo_server.py
│   ├── facebook_server.py
│   ├── linkedin_server.py
│   └── whatsapp_server.py
├── tests/                           # 152 tests
├── docs/                            # Documentation
├── specs/                           # Feature specifications
└── AI_Employee_Vault/               # Working vault
```

### Adding New Integrations

1. Create MCP server in `mcp/your_service_server.py`
2. Implement JSON-RPC 2.0 interface
3. Add to `MCPClient` routing map
4. Update `sensitive_action_detector.py`
5. Add tests in `tests/test_mcp_your_service.py`

---

## 🔒 Security

- ✅ PII sanitization in logs
- ✅ Credentials via environment variables
- ✅ `.env` excluded from git
- ✅ Human approval for sensitive actions
- ✅ Complete audit trail
- ✅ Rate limiting on external APIs

**Never commit:**
- `.env` file
- API tokens
- Personal data

---

## 📝 Configuration

### Gold Tier Settings

```env
# Autonomous Processing
GOLD_TIER_ENABLED=true
AUTO_APPROVE_LOW_RISK=false
PROCESSING_INTERVAL=30

# Scheduling (cron-style)
AUDIT_SCHEDULE=monday:09:00
BRIEFING_SCHEDULE=monday:10:00

# Retry Configuration (automatic)
# - Exponential backoff: 30s, 60s, 120s
# - Max retries: 3
# - Persistent queue in /Business/retry_queue.md
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📚 Documentation

- [LinkedIn Setup Guide](docs/linkedin-setup.md)
- [Facebook Setup Guide](docs/facebook-setup.md)
- [Architecture Overview](specs/004-gold-tier/spec.md)
- [Development Guide](specs/004-gold-tier/plan.md)
- [API Contracts](specs/004-gold-tier/contracts/mcp-contracts.md)

---

## 🐛 Troubleshooting

### Common Issues

**Q: LinkedIn post fails with 403 Forbidden**
- Check token has `w_member_social` permission
- Verify account ID is correct member ID (not client ID)
- Token format should be `urn:li:person:MEMBER_ID`

**Q: Facebook post fails with 403**
- Need **Page Access Token**, not User Access Token
- Grant `pages_read_engagement` and `pages_manage_posts` permissions
- Use Graph API Explorer → "Get Page Access Token"

**Q: Tasks not being processed**
- Check `GOLD_TIER_ENABLED=true` in `.env`
- Verify vault path exists
- Check logs in `AI_Employee_Vault/Logs/`

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [Claude AI](https://claude.ai) (Anthropic)
- MCP (Model Context Protocol) architecture
- Inspired by the concept of Agentic AI
- Python ecosystem (watchdog, requests, pytest)

---

## 📞 Contact

- **Author**: Your Name
- **Project**: Personal AI Employee
- **Repository**: https://github.com/yourusername/personal-ai-employee

---

## 🎯 Roadmap

- [ ] Slack integration
- [ ] Calendar automation (Google Calendar)
- [ ] Task analytics and insights
- [ ] Mobile app for approvals
- [ ] Web dashboard
- [ ] Multi-user support
- [ ] AI model fine-tuning on user patterns

---

**Built with ❤️ and AI**
