# AI Employee Agent Skills

Consolidated skill registry per Constitution Section III.
Each skill is composable, testable, and background-invocable.

---

## Skill: audit-log
**Purpose**: Creates structured JSON audit entries for all system actions with PII sanitization.
**Inputs**: Action metadata (type, actor, target, parameters, result)
**Outputs**: JSON log entries in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
**Approval Required**: No
**MCP Servers Used**: None
**Code**: `src/utils/audit_logger.py`, `src/utils/log_sanitizer.py`, `src/utils/log_manager.py`

---

## Skill: detect-sensitive-action
**Purpose**: Analyzes content to determine if an action requires HITL approval. Gatekeeper for the approval workflow.
**Inputs**: Action file content (Markdown)
**Outputs**: `requires_approval: bool`, `action_type: str`, `risk_level: str`
**Approval Required**: No (detection only)
**MCP Servers Used**: None
**Code**: `src/utils/sensitive_action_detector.py`

---

## Skill: generate-linkedin-post
**Purpose**: Generates LinkedIn post content with templates and rate limiting, routes through HITL before publishing.
**Inputs**: Topic, style (professional/thought_leadership/engagement), template type
**Outputs**: Draft post in `/Pending_Approval/`, published post via LinkedIn MCP on approval
**Approval Required**: Yes (always)
**MCP Servers Used**: `mcp/linkedin_server.py`
**Code**: `src/utils/linkedin_post_generator.py`, `src/utils/content_templates.py`, `src/utils/rate_limiter.py`

---

## Skill: hitl-approval
**Purpose**: Routes sensitive actions through Human-in-the-Loop approval before execution.
**Inputs**: Sensitive action file from `/Needs_Action/`
**Outputs**: Approval request in `/Pending_Approval/`, execution on approval, archive to `/Done/`
**Approval Required**: Yes (this IS the approval workflow)
**MCP Servers Used**: Depends on action type (email, LinkedIn, WhatsApp, Odoo, Facebook)
**Code**: `src/utils/approval_formatter.py`, `src/models/approval_request.py`, `src/processors/silver_processor.py`

---

## Skill: mark-done
**Purpose**: Marks a task as completed, updates metadata, moves to `/Done/`, and refreshes dashboard.
**Inputs**: Task identifier (filename or partial match)
**Outputs**: Updated task file in `/Done/`, dashboard refresh, log entry
**Approval Required**: No
**MCP Servers Used**: None
**Code**: `src/processors/vault_processor.py`

---

## Skill: process-needs-action
**Purpose**: Scans `/Needs_Action/` for pending tasks, analyzes them, creates plans, and routes for processing.
**Inputs**: Markdown files in `/Needs_Action/`, `Company_Handbook.md`, `Business_Goals.md`
**Outputs**: Action plans in `/Plans/`, updated action files, dashboard refresh, audit log entries
**Approval Required**: No for Bronze tasks; Yes for Silver+ sensitive tasks (routed via hitl-approval)
**MCP Servers Used**: None directly (sensitive actions routed through hitl-approval)
**Code**: `src/processors/vault_processor.py`, `src/processors/silver_processor.py`, `src/processors/gold_processor.py`

---

## Skill: send-email-mcp
**Purpose**: Sends emails securely through the Email MCP server. Credentials never leave the MCP process.
**Inputs**: Approved action file from `/Approved/` with email parameters (to, subject, body)
**Outputs**: Email sent via SMTP, audit log entry, file moved to `/Done/`
**Approval Required**: Yes (must be in `/Approved/` first)
**MCP Servers Used**: `mcp/email_server.py`
**Code**: `src/utils/mcp_client.py`, `src/processors/silver_processor.py`

---

## Skill: update-dashboard
**Purpose**: Refreshes `Dashboard.md` with real-time system state, pending approvals, and recent activity.
**Inputs**: Vault directory state, today's audit log, system config
**Outputs**: Updated `AI_Employee_Vault/Dashboard.md`
**Approval Required**: No
**MCP Servers Used**: None
**Code**: `src/utils/dashboard_updater.py`

---

## Skill Dependencies

```
process-needs-action
  --> detect-sensitive-action (checks each task)
  --> hitl-approval (routes sensitive tasks)
       --> send-email-mcp | LinkedIn MCP | WhatsApp MCP | Odoo MCP | Facebook MCP
  --> mark-done (completes non-sensitive tasks)
  --> update-dashboard (refreshes after processing)
  --> audit-log (logs all actions)
```

## MCP Server Registry

| Server | File | Protocol | Purpose |
|--------|------|----------|---------|
| Email | `mcp/email_server.py` | JSON-RPC 2.0 / stdio | Send emails via SMTP |
| LinkedIn | `mcp/linkedin_server.py` | JSON-RPC 2.0 / stdio | Create posts, get metrics |
| Facebook | `mcp/facebook_server.py` | JSON-RPC 2.0 / stdio | Create posts, get engagement |
| WhatsApp | `mcp/whatsapp_server.py` | JSON-RPC 2.0 / stdio | Send messages (API + Playwright) |
| Odoo | `mcp/odoo_server.py` | JSON-RPC 2.0 / stdio | Expenses, invoices, financial summary |

## Watcher Registry

| Watcher | File | Source | Interval |
|---------|------|--------|----------|
| FileSystem | `src/watchers/file_system_watcher.py` | Local vault files | 60s |
| Gmail | `src/watchers/gmail_watcher.py` | Gmail inbox (OAuth2) | 120s |
| WhatsApp | `src/watchers/whatsapp_watcher.py` | WhatsApp Web (Playwright) | 30s |
| LinkedIn | `src/watchers/linkedin_watcher.py` | LinkedIn API (OAuth2) | 300s |
