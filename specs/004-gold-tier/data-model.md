# Data Model: Gold Tier Autonomous System

**Feature Branch**: `004-gold-tier`
**Created**: 2026-02-08
**Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Entity Overview

| Entity | Storage | Format | New/Extended |
| ------ | ------- | ------ | ------------ |
| ActionItem | Vault files | Markdown + frontmatter | Extended (add priority, domain) |
| ApprovalRequest | `/Pending_Approval/` | Markdown + YAML frontmatter | Extended (add approval_source) |
| ExternalAction | In-memory + audit log | JSON log entries | New |
| RetryQueueEntry | `/Business/retry_queue.md` | Markdown sections | New |
| AuditReport | `/Briefings/` | Markdown + frontmatter | New |
| ExecutiveBriefing | `/Briefings/` | Markdown + frontmatter | New |
| CrossDomainWorkflow | `/Plans/` | Markdown + frontmatter | New |
| MCPServerStatus | `/Business/integration_status.json` | JSON | New |
| SchedulerState | `/Business/scheduler_state.json` | JSON | New |

---

## Entity Definitions

### ActionItem (Extended)

Extends existing `src/models/action_file.py` ActionFile dataclass.

**New Fields**:
- `priority`: enum (urgent, high, normal, low). Default: normal. Source: frontmatter `priority:` field or keyword inference.
- `domain`: enum (personal, business, cross-domain). Source: frontmatter `domain:` field or keyword inference.
- `processor`: str. Which processor handled this item. Default: "gold_processor".

**Frontmatter Example**:
```yaml
---
title: Record Q1 software expenses
priority: high
domain: business
action_type: financial_action
status: pending
created: 2026-02-08T09:00:00Z
---
```

**State Transitions**:
```
pending → processing → awaiting_approval → approved → completed
                    ↘ completed (internal)     ↘ rejected → archived
                                                ↘ failed → retry_queued
```

---

### ApprovalRequest (Extended)

Extends existing `src/models/approval_request.py`.

**New Fields**:
- `approval_source`: enum (human, auto). Tracks how the approval was granted.
- `domain`: enum (personal, business, cross-domain). Inherited from action item.

**Frontmatter Example**:
```yaml
---
type: approval_request
action: email_send
created: 2026-02-08T09:05:00Z
status: pending
risk_level: medium
auto_approve_eligible: false
mcp_server: email
domain: business
approval_source: pending
---
```

**State Transitions**:
```
created → pending → approved (human) → executed → archived
                  → approved (auto)  → executed → archived
                  → rejected         → archived
```

---

### ExternalAction (New)

Represents a single external operation executed via MCP. Tracked in audit logs, not as a separate file.

**Fields**:
- `id`: str. Format: `action_{timestamp}_{mcp_server}`
- `mcp_server`: str. Target MCP server name (email, odoo, facebook, linkedin, whatsapp)
- `operation`: str. Method name (e.g., `send_email`, `create_expense`)
- `parameters`: dict. Operation-specific parameters
- `approval_ref`: str. Reference to ApprovalRequest ID
- `status`: enum (pending, executing, completed, failed, retry_queued)
- `retry_count`: int. Number of retry attempts (max 3)
- `result`: dict. Response from MCP server or error details
- `execution_time_ms`: int. Duration of execution
- `timestamp`: ISO datetime

**State Transitions**:
```
pending → executing → completed → logged
                   → failed → retry_queued → executing (retry)
                                           → failed_permanent → notified
```

---

### RetryQueueEntry (New)

Stored in `/Business/retry_queue.md` as sequential sections.

**Fields per Entry**:
- `id`: str. Unique entry identifier
- `operation`: str. MCP method to retry
- `mcp_server`: str. Target server
- `parameters`: dict. Original operation parameters
- `approval_ref`: str. Original approval reference
- `retry_count`: int. Attempts so far
- `max_retries`: int. Always 3
- `last_attempt`: ISO datetime
- `next_retry_after`: ISO datetime (calculated from exponential backoff)
- `error`: str. Last error message
- `status`: enum (queued, retrying, failed_permanent)

**Markdown Format**:
```markdown
## Retry: action_20260208_odoo_001

- **Operation**: create_expense
- **MCP Server**: odoo
- **Parameters**: {"amount": 500, "description": "Software licenses"}
- **Approval Ref**: approval_20260208T090500
- **Retry Count**: 1/3
- **Last Attempt**: 2026-02-08T09:10:00Z
- **Next Retry After**: 2026-02-08T09:11:00Z
- **Error**: Connection timeout
- **Status**: queued

---
```

**State Transitions**:
```
queued → retrying → completed (removed from queue)
                  → queued (retry count < 3, update backoff)
                  → failed_permanent (retry count >= 3, notify user)
```

---

### AuditReport (New)

Stored in `/Briefings/audit_YYYY-MM-DD.md`.

**Frontmatter**:
```yaml
---
type: business_audit
period: 2026-W06
generated: 2026-02-08T09:00:00Z
data_sources:
  - logs
  - accounting
  - social
  - vault_activity
missing_sources: []
---
```

**Sections**:
1. Financial Summary (from `/Business/Accounting/`)
2. Operational Metrics (from `/Logs/` - action counts, success rates)
3. Social Media Performance (from `/Business/Social/`)
4. Action Item Statistics (from vault directory counts)
5. Integration Health (from `/Business/integration_status.json`)
6. Anomalies & Alerts (derived from data patterns)

**State Transitions**:
```
scheduled → collecting → generated → delivered
```

---

### ExecutiveBriefing (New)

Stored in `/Briefings/ceo_briefing_YYYY-MM-DD.md`.

**Frontmatter**:
```yaml
---
type: ceo_briefing
period: 2026-W06
generated: 2026-02-08T10:00:00Z
audit_ref: audit_2026-02-08.md
---
```

**Sections**:
1. Key Metrics (3-5 headline numbers)
2. Highlights (what went well)
3. Concerns (what needs attention)
4. Recommended Actions (1-3 prioritized next steps)

**State Transitions**:
```
audit_complete → generated → delivered
```

---

### CrossDomainWorkflow (New)

Stored as a plan file in `/Plans/` with cross-domain metadata.

**Frontmatter**:
```yaml
---
type: cross_domain_workflow
source_domain: personal
target_domains: [business]
status: pending_approval
created: 2026-02-08T09:00:00Z
sub_actions:
  - domain: personal
    action: update_calendar
    status: pending
  - domain: business
    action: schedule_meeting
    status: pending
approval_required: true
---
```

**State Transitions**:
```
detected → classified → sub_actions_created → pending_approval → approved → executing → completed
                                             → rejected → archived
```

---

### MCPServerStatus (New)

Stored in `/Business/integration_status.json`.

**Schema**:
```json
{
  "servers": {
    "email": {
      "status": "healthy",
      "last_success": "2026-02-08T09:00:00Z",
      "failure_count": 0,
      "consecutive_failures": 0,
      "retry_queue_depth": 0,
      "capabilities": ["send_email", "validate_recipients", "get_account_info"]
    },
    "odoo": {
      "status": "degraded",
      "last_success": "2026-02-07T15:30:00Z",
      "failure_count": 5,
      "consecutive_failures": 3,
      "retry_queue_depth": 2,
      "capabilities": ["create_expense", "create_invoice", "get_financial_summary"]
    }
  },
  "last_updated": "2026-02-08T09:05:00Z"
}
```

**Status Values**: healthy, degraded (1-2 consecutive failures), unavailable (3+ consecutive failures)

**State Transitions**:
```
healthy → degraded (on failure) → unavailable (on 3+ consecutive failures)
unavailable → healthy (on successful operation)
degraded → healthy (on successful operation)
```

---

### SchedulerState (New)

Stored in `/Business/scheduler_state.json`.

**Schema**:
```json
{
  "weekly_audit": {
    "schedule": "monday:09:00",
    "last_run": "2026-02-03T09:00:00Z",
    "next_run": "2026-02-10T09:00:00Z",
    "status": "completed"
  },
  "weekly_briefing": {
    "schedule": "monday:10:00",
    "last_run": "2026-02-03T10:00:00Z",
    "next_run": "2026-02-10T10:00:00Z",
    "status": "completed"
  }
}
```

---

## Relationship Map

```
ActionItem ──→ ApprovalRequest (1:0..1, external actions only)
ApprovalRequest ──→ ExternalAction (1:1, on approval)
ExternalAction ──→ RetryQueueEntry (1:0..1, on failure)
ExternalAction ──→ MCPServerStatus (N:1, updates status)
ActionItem ──→ CrossDomainWorkflow (1:0..1, if cross-domain)
CrossDomainWorkflow ──→ ActionItem (1:N, sub-actions)
AuditReport ──→ ExecutiveBriefing (1:1)
SchedulerState ──→ AuditReport (triggers generation)
```

## Backward Compatibility

All existing Silver-tier models remain unchanged. New fields are additive:
- `ActionFile` gains optional `priority`, `domain`, `processor` fields (defaults preserve Silver behavior)
- `ApprovalRequest` gains optional `approval_source`, `domain` fields
- `AuditLogEntry` gains optional `domain` field
- Existing code paths continue to work without Gold-tier configuration enabled
