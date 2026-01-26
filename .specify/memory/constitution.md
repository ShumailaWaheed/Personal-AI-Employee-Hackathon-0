<!-- SYNC IMPACT REPORT:
Version change: v2.2.0 → v3.0.0
Modified principles: All principles (major update to full paper workflow integration)
Added sections: Paper workflow, Project Initialization, Git Integration, Complete Tiered Deliverables
Removed sections: None
Templates requiring updates: ⚠️ Manual review needed for plan-template.md, spec-template.md, tasks-template.md
Follow-up TODOs: None
-->
# AI Employee Project Constitution

## 1. Purpose
Define quality standards and workflow for all AI-driven papers/tasks in the Personal AI Employee Hackathon.

## 2. Project Initialization
1. Initialize a git repo: `git init`
2. Create Obsidian vault: `AI_Employee_Vault`
3. Set up Python 3.13+, Node.js, Claude Code, MCP servers.
4. Verify system: `claude --version`, run basic Watcher scripts.

## 3. Constitution Commit
- Commit `CONSTITUTION.md` to git:
```bash
git add CONSTITUTION.md
git commit -m "Add AI Employee Project Constitution"
```

## 4. Paper Workflow
For each paper/task:

### 4.1 /sp.specify
Write a specification file: /Specs/<PaperName>.md

Include purpose, inputs, outputs, dependencies, and tier.

### 4.2 /sp.clarify
Claude Code reviews the spec, highlights missing fields, and suggests clarifications.

Commit updated spec to git.

### 4.3 /sp.plan
Claude generates /Plans/<PaperName>.md with checklist tasks.

Assign human-in-the-loop approvals if needed.

### 4.4 /sp.tasks
Execute tasks as defined in Plan.md.

Watchers detect input changes and create action files in /Needs_Action.

### 4.5 /sp.implement
Claude Code executes actions (emails, social posts, payments, briefings).

Follow Ralph Wiggum loop for multi-step autonomous completion.

### 4.6 Commit Paper
Commit outputs (Plan.md, Briefings, Watcher scripts, MCP scripts) to git:

```bash
git add Plans/<PaperName>.md Briefings/<PaperName>.md Watchers/*.py MCP/*.js
git commit -m "Implement <PaperName> tasks"
```

## 5. Core Principles

### I. Local-First Architecture (NON-NEGOTIABLE)
- All data stored locally in Obsidian vault; Markdown is single source of truth
- External APIs allowed **read-only**
- Sensitive data (credentials, tokens, PII, WhatsApp sessions) **never committed or synced externally**
- Persistent state lives in Markdown files

**Vault Structures per Tier**

Bronze:
```
/Inbox
/Needs_Action
/Done
Dashboard.md
Company_Handbook.md
```

Silver:
```
/Inbox
/Needs_Action
/Pending_Approval
/Approved
/Rejected
/Done
/Logs
/Plans
Dashboard.md
Company_Handbook.md
```

Gold:
```
/Inbox
/Needs_Action # Personal + Business
/Pending_Approval
/Approved
/Rejected
/Done
/Logs
/Plans
/Business # Business tasks
/Accounting # Odoo transactions
/Briefings # CEO briefings and audit reports
Dashboard.md
Company_Handbook.md
Business_Goals.md
```

Rationale: Local-first ensures privacy; Silver adds approval workflow/logs; Gold adds cross-domain intelligence.

### II. External Actions and MCP Integration (Bronze → Silver)
- Bronze: Vault read/write only.
- Silver: External actions via MCP servers with HITL approval.

Allowed Operations:
- Bronze: Read/write Markdown, create action files from Watchers
- Silver: Email send, social posts, browser automation, any external HITL-approved action

MCP Server Requirements (Silver+):
- At least 1 MCP server
- JSON-RPC over stdio
- All external actions route through HITL
- Document capabilities in Company_Handbook.md

Rationale: Bronze builds foundation; Silver enables safe external actions.

### III. Agent Skills Implementation
- All AI functionality must be implemented as Claude Agent Skills (not hardcoded)
- Document each skill in SKILL.md: purpose, inputs, outputs, approval requirements, MCP used
- Skills must be composable, testable, and background-invocable

Gold Tier: autonomous processing, cross-domain support, self-scheduling

Skill File Format:
```
Skill: [Name]
Purpose
[Description]
Inputs
[Format/sources]
Outputs
[Format/destinations]
Approval Required
[Yes/No + conditions]
MCP Servers Used
[List]
```

Rationale: Modular skills enable maintainability and reusability.

### IV. Security and Privacy
Credential Management:
- Use .env (gitignore) or OS secrets manager
- Never store credentials in vault/code

Audit Logging:
- Silver+: JSON logs in /Logs/YYYY-MM-DD.json
- Format:
```
{
  "timestamp": "...",
  "action_type": "...",
  "actor": "...",
  "target": "...",
  "parameters": {...},
  "approval_status": "...",
  "result": "..."
}
```

- Retain 90 days, no secrets/PII

Development Mode:
- DRY_RUN=true respected (log without executing)

Rationale: Security-first prevents breaches.

### V. Multi-Watcher Architecture
**BaseWatcher Pattern:**
```python
import time, logging
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)
```

- Bronze: 1 watcher (Gmail OR filesystem)
- Silver: 2+ watchers (Gmail + WhatsApp + LinkedIn), PM2 required

Gmail Watcher Example (Python):
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime

class GmailWatcher(BaseWatcher):
    # Implementation details...
```

WhatsApp Watcher (Playwright), Filesystem Watcher (watchdog) included as per reference.

Rationale: Modular watchers enable reliable perception.

### VI. Human-in-the-Loop (HITL) Approval Workflow
1. Proposal files in /Pending_Approval
2. Human moves to /Approved or /Rejected
3. Execution via MCP
4. Archive to /Done or /Rejected

Approval File Format:
```
---
type: approval_request
action: [email_send|linkedin_post|payment|...]
created: [ISO_TIMESTAMP]
status: pending
risk_level: [low|medium|high]
auto_approve_eligible: [true|false]
mcp_server: [name]
---
# Approval Request: [Title]
## Proposed Action
[Description]
## Target
[Email/URL/etc.]
## Parameters
[Details]
## Rationale
[Why]
## Risk Assessment
[Issues]
## Approval Instructions
- Move to /Approved/ to execute
- Move to /Rejected/ to cancel
```

Auto-approve optional for low-risk actions. Rationale: Prevents unintended actions.

### VII. Autonomous Operation & Ralph Wiggum Loop
- Processor runs continuously (PM2 recommended)
- Auto-detect /Needs_Action files, invoke skills
- Multi-step, cross-domain coordination
- Ralph Wiggum Loop: iterative Stop-hook ensures tasks complete before exit.

Example Flow:
Watcher → /Needs_Action/file.md → Processor → Plan.md → Human Approves → MCP executes → Logs → /Done

Config:
```
AI_PROCESSOR_ENABLED=true
PROCESSING_INTERVAL=30
```

### VIII. Business Intelligence & Reporting (Gold)
- Weekly audit (Monday 9AM) → /Briefings/audit_YYYY-MM-DD.md
- CEO briefing (Monday 10AM) → /Briefings/ceo_briefing_YYYY-MM-DD.md

Audit Template:
```
---
type: business_audit
period: YYYY-WW
generated: ISO_TIMESTAMP
---
# Weekly Business & Accounting Audit
...
```

CEO Briefing Template:
```
---
type: ceo_briefing
period: YYYY-WW
generated: ISO_TIMESTAMP
---
# CEO Briefing: Week of [Date]
...
```

Odoo Integration: self-hosted, MCP JSON-RPC, read/write with HITL approval.

### IX. Paper Workflow & Git Integration
For each paper/task:
- /sp.specify → create /Specs/<Paper>.md
- /sp.clarify → refine spec via Claude Code
- /sp.plan → generate /Plans/<Paper>.md
- /sp.tasks → execute tasks, Watchers create action files
- /sp.implement → execute via Claude + MCP
- Commit outputs as specified in Section 4.6

Rationale: Full alignment with hackathon workflow.

### X. Security & Ethics
- HITL for sensitive tasks
- Audit logs for review
- Dry-run for development
- Only capture necessary data
- Maintain transparency and human accountability

## 6. Quality Standards
- Error handling: retry logic, watchdog auto-restart, dry-run testing.
- Logging: store in /Vault/Logs/YYYY-MM-DD.json.
- Security: credentials never committed; environment variables or secret manager only.
- Human-in-the-loop: approvals required for sensitive actions.
- Completion verification: files moved to /Done before exit.

## 7. Git & Version Control
- Maintain clear commit messages.
- Tag milestones by tier (Bronze/Silver/Gold/Platinum).
- Backup Obsidian vault and MCP scripts regularly.

## 8. Tiered Deliverables

| Tier | Requirements | Estimated Hours |
|------|-------------|----------------|
| Bronze | Vault, Dashboard.md, Company_Handbook.md, 1 watcher, Agent Skills | 8-12 |
| Silver | Multi-watchers, LinkedIn auto-post, MCP server, HITL approvals | 20-30 |
| Gold | Cross-domain integration, Odoo accounting, social integration, weekly audits | 40+ |
| Platinum | Cloud + Local hybrid, always-on watchers, A2A delegation, 24/7 uptime | 60+ |

## 9. Governance

This constitution is the supreme guiding document. All subsequent /sp.specify, /sp.plan, /sp.tasks, /sp.implement MUST explicitly reference and comply with these principles. Any deviation requires justification in the plan and user approval. All PRs/reviews must verify compliance with privacy, security, and human-in-the-loop requirements. All team members must acknowledge and agree to these principles before contributing to the project.

**Version**: v3.0.0 | **Ratified**: 2026-01-26 | **Last Amended**: 2026-01-26