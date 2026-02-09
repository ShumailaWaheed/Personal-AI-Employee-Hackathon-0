# HITL Approval Workflow

Route sensitive actions through Human-in-the-Loop approval before execution.

## Description
This skill handles the complete HITL approval lifecycle. It detects sensitive actions in /Needs_Action, creates formatted approval request files in /Pending_Approval, and processes approved/rejected decisions. All sensitive external actions (emails, social posts, payments) MUST go through this workflow before execution.

## When to Use
- A task in /Needs_Action involves external communication (email, LinkedIn, WhatsApp)
- An action involves financial operations (payments, transfers, purchases)
- Content will be published or shared externally
- Any action that could represent the organization publicly
- The `process-needs-action` skill detects sensitive keywords

## Inputs
- Markdown action files from `AI_Employee_Vault/Needs_Action/`
- Content is analyzed for sensitive keywords (see Detection section)
- Company_Handbook.md for organizational context

## Outputs
- Plan file in `AI_Employee_Vault/Plans/PLAN_[timestamp]_[name].md`
- Approval request in `AI_Employee_Vault/Pending_Approval/approval_[timestamp].md`
- Audit log entry in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- Original action file moved to `AI_Employee_Vault/Done/`

## Approval Required
- **This skill creates the approval** - it does not itself require approval
- The generated approval file requires human action (move to /Approved or /Rejected)

## MCP Servers Used
- None during routing (MCP is used only after approval, via `send-email-mcp` or similar)

## Process Steps

### 1. Detect Sensitive Action
```python
# Keywords that trigger HITL routing (from src/config/settings.py)
SENSITIVE_KEYWORDS = [
    'email', 'send', 'post', 'publish', 'share', 'message',
    'contact', 'reach out', 'reply', 'respond', 'payment',
    'transaction', 'buy', 'purchase', 'transfer', 'linkedin',
]
```
If ANY keyword is found in the action file content (case-insensitive), the action is routed to HITL.

### 2. Assess Risk Level
- **High**: payment, transaction, transfer, purchase, buy, delete, remove
- **Medium**: email, send, post, publish, share, linkedin
- **Low**: Everything else that matched a sensitive keyword

### 3. Detect Action Type
- `email_send` - if content mentions email, send, smtp, mail
- `linkedin_post` - if content mentions linkedin, post, publish
- `whatsapp_message` - if content mentions whatsapp, message, chat
- `financial_action` - if content mentions payment, transaction, transfer
- `general_action` - fallback

### 4. Create Plan File
Create in `/Plans/` with frontmatter:
```yaml
---
created: [ISO timestamp]
source_action: [original filename]
priority: medium
status: pending_approval
---
```

### 5. Create Approval Request
Create in `/Pending_Approval/` with frontmatter:
```yaml
---
type: approval_request
action: [action_type]
created: [ISO timestamp]
status: pending
risk_level: [high/medium/low]
auto_approve_eligible: false
mcp_server: [email_mcp/linkedin_mcp]
---
```

Include:
- Proposed action description
- Target (extracted from content)
- Parameters
- Risk assessment
- Clear instructions: "Move to /Approved/ to execute, /Rejected/ to cancel"

### 6. Process Approved Items
When files appear in `/Approved/`:
1. Read the approval file to determine action type
2. Execute via appropriate MCP server (DRY_RUN mode skips actual execution)
3. Create audit log entry with execution result
4. Move to `/Done/`

### 7. Log Everything
Every routing and execution creates a sanitized audit log entry.

## Code Reference
- `src/processors/silver_processor.py` - SilverProcessor._route_to_approval()
- `src/utils/sensitive_action_detector.py` - requires_approval(), detect_action_type(), assess_risk()
- `src/utils/approval_formatter.py` - ApprovalFormatter.create_approval_file()
- `src/models/approval_request.py` - ApprovalRequest data model

## Quality Criteria
- All sensitive actions are detected (no false negatives for external communications)
- Approval files contain clear instructions for the human reviewer
- Risk level is accurately assessed
- Audit trail is complete for every routed action
- Non-sensitive actions bypass HITL and process directly (Bronze tier behavior preserved)

## Related Skills
- `detect-sensitive-action` - Standalone detection check
- `send-email-mcp` - Executes email after approval
- `generate-linkedin-post` - Creates LinkedIn drafts for approval
- `audit-log` - Logs all actions
- `process-needs-action` - Upstream skill that triggers HITL routing
