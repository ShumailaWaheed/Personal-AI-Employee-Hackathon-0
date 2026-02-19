# Auto-Approve Action

Automatically approve and execute low-risk actions without human intervention.

## Description
This skill enables the Gold tier's autonomous operation by automatically approving and executing actions that meet strict safety criteria. Only low-risk, single-domain actions are eligible. Cross-domain items, financial actions, and anything medium/high risk always require human approval. Auto-approval is controlled by the `AUTO_APPROVE_LOW_RISK` config flag and can be disabled entirely.

## When to Use
- A sensitive action is detected in `/Needs_Action/` during Gold tier processing
- The action's risk level is `low`
- The action's domain is NOT `cross-domain`
- `AUTO_APPROVE_LOW_RISK=true` is set in `.env`

## Inputs
- Action file from `/Needs_Action/`
- Risk level from `detect-sensitive-action` skill
- Domain from `classify-priority-domain` skill
- Config flag: `AUTO_APPROVE_LOW_RISK`

## Outputs
- Action executed via appropriate MCP server (or logged in DRY_RUN mode)
- Audit log entry with `approval_status: auto_approved`
- Action file moved to `/Done/`

## Approval Required
- **No** — this skill IS the automatic approval mechanism
- It bypasses HITL for eligible actions only

## MCP Servers Used
- Depends on action type: `email_mcp`, `linkedin_mcp`, `twitter_mcp`, `facebook_mcp`, `instagram_mcp`, `whatsapp_mcp`, `odoo_mcp`

## Eligibility Criteria

### Must ALL be true:
| Criteria | Check |
|----------|-------|
| Config enabled | `AUTO_APPROVE_LOW_RISK=true` in `.env` |
| Risk level | Must be `low` |
| Domain | Must NOT be `cross-domain` |

### What gets auto-approved (examples):
- Low-risk general actions in personal or business domain
- Simple status updates, internal notifications

### What NEVER gets auto-approved:
| Blocked | Reason |
|---------|--------|
| Financial actions | Always high risk |
| Email sends | Medium risk |
| Social media posts | Medium risk |
| Cross-domain items | Extra scrutiny needed |
| Anything medium/high risk | Safety first |

## Decision Flow
```
Action detected as sensitive
  │
  ├─ AUTO_APPROVE_LOW_RISK=false? → Route to HITL approval
  │
  ├─ Risk level != low? → Route to HITL approval
  │
  ├─ Domain == cross-domain? → Route to HITL approval
  │
  └─ All checks pass → Auto-approve and execute
```

## Process Steps
1. `GoldProcessor._process_single_action()` detects a sensitive action
2. Calls `_can_auto_approve(risk_level, domain)` to check eligibility
3. If eligible, calls `_auto_approve_action()`:
   a. Logs audit entry with `approval_status: auto_approved`
   b. Executes via MCP (respects DRY_RUN mode)
   c. Logs execution result (success/failure) with timing
   d. Moves action file to `/Done/`
4. If not eligible, falls through to `_route_to_approval_gold()` (HITL)

## Audit Trail
Every auto-approved action generates TWO audit log entries:

### Entry 1: Auto-approval decision
```json
{
  "action_type": "linkedin_post",
  "actor": "system",
  "target": "task_share_update.md",
  "parameters": {"risk_level": "low", "auto_approved": true},
  "approval_status": "auto_approved",
  "result": "success",
  "domain": "business"
}
```

### Entry 2: Execution result
```json
{
  "action_type": "linkedin_post",
  "actor": "system",
  "target": "task_share_update.md",
  "parameters": {"dry_run": false, "auto_approved": true},
  "approval_status": "executed",
  "result": "success",
  "execution_time_ms": 1250,
  "domain": "business"
}
```

## Configuration
In `.env`:
```
AUTO_APPROVE_LOW_RISK=false   # Default: disabled for safety
```

Set to `true` only when you trust the system's risk classification and want autonomous operation.

## Code Reference
- `src/processors/gold_processor.py` — `_can_auto_approve()`, `_auto_approve_action()`
- `src/utils/sensitive_action_detector.py` — `assess_risk()` (provides risk level)
- `src/utils/domain_classifier.py` — `classify_domain()` (provides domain)

## Quality Criteria
- Auto-approval NEVER triggers when config flag is disabled
- Financial and cross-domain actions are NEVER auto-approved
- Every auto-approved action has a complete audit trail
- DRY_RUN mode is respected (log only, no execution)
- Failed executions are logged with failure status (not silently dropped)

## Related Skills
- `classify-priority-domain` — Provides domain classification used in eligibility check
- `detect-sensitive-action` — Provides risk level used in eligibility check
- `hitl-approval` — Fallback when auto-approval criteria are not met
- `audit-log` — Records all auto-approval decisions and executions
- `retry-failed-action` — Handles failures from auto-approved executions
