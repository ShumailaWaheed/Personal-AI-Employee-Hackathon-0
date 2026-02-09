# Update Dashboard

Refresh Dashboard.md with current system status, pending approvals, and recent activity.

## Description
This skill regenerates `AI_Employee_Vault/Dashboard.md` with a real-time snapshot of the system state. It counts items across all vault directories, displays the pending approval queue, shows recent audit log activity, and reports MCP server status. The dashboard is the operator's primary visibility tool.

## When to Use
- After any file is processed, approved, rejected, or moved to Done
- After the `process-needs-action` skill runs
- After `hitl-approval` creates or resolves an approval request
- After `send-email-mcp` executes an action
- Periodically during continuous operation (every processing interval)
- When user asks for system status

## Inputs
- Vault directory state (file counts in each folder)
- Today's audit log (`AI_Employee_Vault/Logs/YYYY-MM-DD.json`)
- Config: DRY_RUN mode, PROCESSING_INTERVAL

## Outputs
- Updated `AI_Employee_Vault/Dashboard.md`

## Approval Required
- **No** - Dashboard updates are automatic

## MCP Servers Used
- None

## Dashboard Sections

### Status Overview
Shows counts for all vault directories:
```markdown
## Status Overview
- **Pending Approval**: 3 items
- **Needs Action**: 5 items
- **Approved (queued)**: 1 items
- **Completed**: 42 items
- **Rejected**: 2 items
```

### Pending Approval Queue
Lists up to 5 files awaiting human review:
```markdown
## Pending Approval Queue
- approval_1738889103.md
- approval_1738889245.md
- ... and 1 more
```

### Recent Activity
Last 5 audit log entries (newest first):
```markdown
## Recent Activity
- 2026-02-06T22:25:03: email_send - success
- 2026-02-06T22:24:58: route_to_approval - success
```

### MCP Server Status
```markdown
## MCP Server Status
- **Email MCP**: Operational
- **Last Heartbeat**: 2026-02-06 22:25:03
```

### System Settings
```markdown
## System Settings
- **Dry Run Mode**: Disabled
- **Processing Interval**: 30s
```

## Process Steps
1. Count files in each vault directory (Needs_Action, Pending_Approval, Approved, Rejected, Done)
2. Load today's audit log for recent activity
3. Generate markdown content with all sections
4. Write to `AI_Employee_Vault/Dashboard.md`

## Code Reference
- `src/utils/dashboard_updater.py` - DashboardUpdater class
- Called from `src/main.py` after each processing cycle
- Called from `src/processors/vault_processor.py` (Bronze tier compat)

## Quality Criteria
- Counts are accurate (match actual file counts)
- Dashboard is valid markdown viewable in Obsidian
- Recent activity shows latest actions
- No stale data (regenerated each call, not appended)
- Pending approval queue is visible and actionable

## Related Skills
- `process-needs-action` - Triggers dashboard update after processing
- `hitl-approval` - Changes approval counts reflected in dashboard
- `audit-log` - Recent logs displayed in dashboard
- `mark-done` - Completion updates reflected in dashboard
