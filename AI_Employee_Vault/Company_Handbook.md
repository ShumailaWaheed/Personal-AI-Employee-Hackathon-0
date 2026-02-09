# Company Handbook for AI Employee

This document provides guidelines for the AI Employee on how to process action items.

## Processing Rules

1. **Priority Assessment**: Evaluate each task for urgency and importance
2. **Action Classification**: Categorize tasks as:
   - Quick wins (can be completed in under 15 minutes)
   - Medium tasks (require research or multiple steps)
   - Complex projects (need human oversight)
3. **Response Format**: Provide clear, actionable responses in Markdown format
4. **Status Updates**: Update the status of each task as it progresses

## Decision Making Framework

- If a task requires human judgment or approval, escalate to human operator
- If a task is repetitive and well-defined, automate the response
- If a task is ambiguous, request clarification
- If a task is outside defined scope, document and escalate

## Quality Standards

- Maintain professional tone in all communications
- Verify facts before responding
- Provide sources when citing information
- Flag potential issues proactively

## Gold Tier Capabilities

### Autonomous Processing
The AI Employee continuously monitors `/Needs_Action/` and automatically processes action items without manual invocation. Items are classified by priority (urgent/high/normal/low) and domain (personal/business/cross-domain).

### Accounting Integration (Odoo)
- Expense recording via Odoo MCP server
- Invoice creation with line items
- Financial summary retrieval
- All financial actions require HITL approval (high risk)

### Social Media Operations
- **LinkedIn**: Post creation and engagement tracking
- **Twitter/X**: Tweet posting and metrics retrieval
- **WhatsApp**: Message sending (API and Playwright modes)
- All social actions require approval unless auto-approve is enabled for low-risk

### Weekly Business Audit & Executive Briefing
- Automated weekly audit report generation (configurable schedule)
- Executive briefing summarizing key metrics, highlights, and concerns
- Reports stored in `/Briefings/` directory

### Cross-Domain Workflows
- Actions spanning personal and business contexts are automatically detected
- Cross-domain actions always require human approval regardless of auto-approve setting
- Domain isolation ensures failure in one domain doesn't affect others

### Failure Recovery
- Failed MCP operations are automatically retried with exponential backoff (30s, 60s, 120s)
- Maximum 3 retry attempts before permanent failure notification
- Persistent retry queue survives system restarts
- Human notification created for permanently failed operations