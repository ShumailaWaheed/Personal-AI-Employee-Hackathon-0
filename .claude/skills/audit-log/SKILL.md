# Audit Log

Create structured JSON audit entries for all system actions with PII sanitization.

## Description
This skill handles all audit logging for the AI Employee system. Every external action, approval routing, execution result, and system event is recorded as a structured JSON entry. All entries are sanitized to remove PII before storage. Logs are organized by date and support rotation/retention policies.

## When to Use
- After any action is processed (sensitive or not)
- After an approved action is executed via MCP
- When a file is routed to /Pending_Approval
- After an action is rejected
- On any system error during processing
- When generating log summaries for the dashboard

## Inputs
- Action metadata: action_type, actor, target, parameters, approval_status, result
- The `AuditLogEntry` data model (`src/models/audit_log_entry.py`)

## Outputs
- JSON entry appended to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- All entries are PII-sanitized before writing

## Approval Required
- **No** - Logging is automatic and transparent

## MCP Servers Used
- None

## Log Entry Format
```json
{
  "timestamp": "2026-02-06T22:25:03.123456",
  "action_type": "email_send",
  "actor": "system",
  "target": "[EMAIL_REDACTED]",
  "parameters": {
    "source_file": "task_outreach.md",
    "password": "***REDACTED***"
  },
  "approval_status": "executed",
  "result": "success",
  "execution_time_ms": 150
}
```

## PII Sanitization Rules
The sanitizer (`src/utils/log_sanitizer.py`) applies these rules:

### Patterns Redacted
| Pattern | Replacement |
|---------|-------------|
| Email addresses (`user@domain.com`) | `[EMAIL_REDACTED]` |
| Phone numbers (`+1 234-567-8901`) | `[PHONE_REDACTED]` |
| Bearer tokens (`Bearer abc123...`) | `Bearer ***REDACTED***` |

### Keys Always Masked
These dict keys have their values replaced with `***REDACTED***`:
- `password`
- `token`
- `secret`
- `api_key`
- `access_token`
- `smtp_password`

### What Is NOT Redacted
- Action types, timestamps, result status
- File names (they don't contain PII by convention)
- Risk levels, approval status

## Log Rotation
- Logs older than `LOG_RETENTION_DAYS` (default: 90) are deleted
- Rotation is handled by `LogManager.rotate()`
- Run periodically via PM2 or scheduled task

## Log Summary
`LogManager.get_log_summary(days=7)` returns:
```python
{
    "total_entries": 42,
    "success_count": 38,
    "failure_count": 4,
    "action_types": {"email_send": 15, "route_to_approval": 20, ...},
    "days_covered": 7,
}
```

## Process Steps
1. Create `AuditLogEntry` with all action metadata
2. Convert to dict via `.to_dict()`
3. Pass through `sanitize_entry()` to redact PII
4. Load existing log file for today (or create new)
5. Append sanitized entry
6. Write back to `Logs/YYYY-MM-DD.json`

## Code Reference
- `src/utils/audit_logger.py` - AuditLogger.log()
- `src/utils/log_sanitizer.py` - sanitize_entry()
- `src/utils/log_manager.py` - LogManager (rotation, summaries)
- `src/models/audit_log_entry.py` - AuditLogEntry data model

## Quality Criteria
- Every external action has a corresponding audit entry
- No PII appears in stored log files
- Logs are valid JSON (array of entries)
- Retention policy is enforced
- Log summaries accurately reflect stored data

## Related Skills
- `hitl-approval` - Generates audit entries when routing
- `send-email-mcp` - Generates audit entries on execution
- `update-dashboard` - Reads recent logs for display
