# Detect Sensitive Action

Analyze content to determine if an action requires HITL approval.

## Description
This skill provides the detection logic that determines whether a task involves a sensitive external action requiring human approval. It is the gatekeeper for the HITL workflow - any action that could affect external systems, send communications, or involve financial transactions must pass through this check.

## When to Use
- Before processing any action file in /Needs_Action
- When determining whether to route directly (Bronze behavior) or to HITL approval (Silver behavior)
- When classifying incoming watcher inputs
- For pre-screening content before creating plans

## Inputs
- Text content from a markdown action file (the full file content)

## Outputs
- `requires_approval: bool` - Whether the action needs HITL
- `action_type: str` - Classified action type
- `risk_level: str` - Risk assessment (low/medium/high)

## Approval Required
- **No** - This is a detection/classification skill, not an execution skill

## MCP Servers Used
- None

## Detection Logic

### Sensitive Keywords
If ANY of these keywords appear (case-insensitive), the action requires approval:
```
email, send, post, publish, share, message,
contact, reach out, reply, respond, payment,
transaction, buy, purchase, transfer, linkedin
```

### Action Type Classification
| Content Contains | Action Type |
|-----------------|-------------|
| email, send, smtp, mail | `email_send` |
| linkedin, post, publish | `linkedin_post` |
| whatsapp, message, chat | `whatsapp_message` |
| payment, transaction, transfer, buy, purchase | `financial_action` |
| (other) | `general_action` |

### Risk Level Assessment
| Risk | Keywords |
|------|----------|
| **High** | payment, transaction, transfer, purchase, buy, delete, remove |
| **Medium** | email, send, post, publish, share, linkedin |
| **Low** | Everything else that matched a sensitive keyword |

## Decision Flow
```
Content → Check keywords →
  ├─ No match → Process directly (Bronze tier)
  └─ Match found →
       ├─ Classify action type
       ├─ Assess risk level
       └─ Route to HITL approval (Silver tier)
```

## Examples

### Sensitive (requires approval)
- "Please send an email to the client about the proposal" → `email_send`, medium risk
- "Post a LinkedIn update about our new product" → `linkedin_post`, medium risk
- "Make a payment of $500 to the vendor" → `financial_action`, high risk
- "Share the quarterly report with stakeholders" → `general_action`, medium risk

### Not Sensitive (direct processing)
- "Read the project status report" → No approval needed
- "Update the quarterly analysis spreadsheet" → No approval needed
- "Analyze the customer data trends" → No approval needed
- "Create a summary of recent meetings" → No approval needed

## Code Reference
- `src/utils/sensitive_action_detector.py` - requires_approval(), detect_action_type(), assess_risk()
- `src/config/settings.py` - SENSITIVE_KEYWORDS list
- Called by `src/processors/silver_processor.py` - SilverProcessor._process_needs_action()

## Quality Criteria
- Zero false negatives for external communication actions (email, social, messaging)
- Financial actions always flagged as high risk
- Non-sensitive read/analyze/update tasks pass through without HITL
- Classification is deterministic and testable

## Test Coverage
```python
assert requires_approval('Please send an email') == True
assert requires_approval('Update the report') == False
assert detect_action_type('send email to client') == 'email_send'
assert assess_risk('make a payment') == 'high'
assert assess_risk('send an email') == 'medium'
assert assess_risk('update document') == 'low'
```

## Related Skills
- `hitl-approval` - Downstream skill that creates the approval request
- `process-needs-action` - Calls this skill to determine routing
