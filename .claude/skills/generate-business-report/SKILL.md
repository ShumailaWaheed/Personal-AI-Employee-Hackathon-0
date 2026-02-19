# Generate Business Report

Generate scheduled weekly audit reports and executive briefings from vault data sources.

## Description
This skill generates two types of business intelligence reports: (1) a comprehensive **Weekly Audit Report** aggregating data from logs, accounting, social media, vault activity, and integration health; and (2) a concise **CEO Executive Briefing** summarizing key metrics, highlights, concerns, and recommended actions. Reports are generated on a configurable schedule (default: Monday 9AM for audit, Monday 10AM for briefing) and stored in `/Briefings/`. Missing data sources are gracefully handled and clearly marked.

## When to Use
- The configured audit schedule is due (default: Monday 9AM)
- The configured briefing schedule is due (default: Monday 10AM)
- User manually requests a business report or executive summary
- After a significant batch of actions has been processed
- When reviewing overall system and business health

## Inputs
- **Logs**: `AI_Employee_Vault/Logs/*.json` - operational metrics (action counts, success/failure rates, action types)
- **Accounting**: `AI_Employee_Vault/Business/Accounting/*.md` - expense and invoice records
- **Social**: `AI_Employee_Vault/Business/Social/*.md` - social media post records
- **Vault Activity**: File counts in `Needs_Action/`, `Pending_Approval/`, `Done/`
- **Integration Health**: `AI_Employee_Vault/Business/integration_status.json` - MCP server status
- **Scheduler State**: `AI_Employee_Vault/Business/scheduler_state.json` - tracks last run times
- **Config**: `AUDIT_SCHEDULE`, `BRIEFING_SCHEDULE` from `.env`

## Outputs
- Audit report: `AI_Employee_Vault/Briefings/audit_YYYY-MM-DD.md`
- CEO briefing: `AI_Employee_Vault/Briefings/ceo_briefing_YYYY-MM-DD.md`
- Updated scheduler state with next run time
- Audit log entries for report generation

## Approval Required
- **No** - Reports are internal documents, no external action taken

## MCP Servers Used
- None (reads local data only)

## Schedule Configuration
In `.env`:
```
AUDIT_SCHEDULE=monday:09:00
BRIEFING_SCHEDULE=monday:10:00
```
Format: `day_of_week:HH:MM` (24-hour). The scheduler checks if the current time has passed the target and the task hasn't run this week.

## Audit Report Sections

### 1. Operational Metrics
Aggregated from `/Logs/*.json`:
- Total actions processed
- Success / failure counts
- Success rate percentage
- Top 5 action types by frequency

### 2. Financial Summary
From `/Business/Accounting/*.md`:
- Total financial records
- Expense count
- Invoice count

### 3. Social Media Performance
From `/Business/Social/*.md`:
- Total posts tracked

### 4. Action Item Statistics
From vault directory file counts:
- Needs_Action (pending)
- Pending_Approval (awaiting human)
- Done (completed)

### 5. Integration Health
From `/Business/integration_status.json`:
- MCP server statuses (operational/unavailable)

### Missing Data Handling
If any data source is unavailable, the report marks that section as:
```
[DATA UNAVAILABLE: source_name]
```
The report still generates successfully with available data.

## CEO Briefing Sections

The briefing is derived from the most recent audit report:

### 1. Key Metrics
- Extracted from audit: Total Actions, Success Rate (top 5 items)

### 2. Highlights
- 100% success rate noted as positive
- Mixed results flagged for review

### 3. Concerns
- Operation failures flagged
- Unavailable data sources noted

### 4. Recommended Actions
- Missing integrations highlighted
- Unavailable MCP servers flagged
- Default: "Continue normal operations"

## Report Frontmatter Format
```yaml
---
type: business_audit  # or ceo_briefing
period: 2026-W08
generated: 2026-02-19T09:00:00
data_sources:
  - logs
  - accounting
  - vault_activity
missing_sources:
  - social
  - integration_status
---
```

## Process Steps

### Audit Report
1. Scheduler checks if `weekly_audit` is due
2. `ReportGenerator.generate_audit_report()` collects data from all 5 sources
3. Missing sources are recorded but don't block generation
4. `AuditReportModel` renders Markdown with frontmatter
5. Report saved to `/Briefings/audit_YYYY-MM-DD.md`
6. Scheduler marks `weekly_audit` as completed, calculates next run
7. Audit log entry created for the generation event

### CEO Briefing
1. Scheduler checks if `weekly_briefing` is due
2. Finds the most recent `audit_*.md` in `/Briefings/`
3. `ReportGenerator.generate_executive_briefing()` extracts key metrics, highlights, concerns
4. Generates recommendations based on audit findings
5. Briefing saved to `/Briefings/ceo_briefing_YYYY-MM-DD.md`
6. Scheduler marks `weekly_briefing` as completed
7. Audit log entry created

## Code Reference
- `src/utils/report_generator.py` - ReportGenerator (generate_audit_report, generate_executive_briefing)
- `src/utils/scheduler.py` - Scheduler (is_due, mark_completed, configure)
- `src/models/audit_report.py` - AuditReportModel (data model + Markdown rendering)
- `src/processors/gold_processor.py` - GoldProcessor._process_scheduled_tasks() (orchestration)

## Quality Criteria
- Reports generate even when some data sources are missing
- Missing sources are clearly marked, not silently omitted
- Frontmatter is valid YAML parseable by Obsidian
- Scheduler prevents duplicate runs within the same week
- Briefing accurately reflects the audit data it's based on
- Zero-activity periods produce valid reports (not errors)
- All report generation events have corresponding audit log entries

## Example Output

### Audit Report
```markdown
---
type: business_audit
period: 2026-W08
generated: 2026-02-19T09:00:00
data_sources:
  - logs
  - vault_activity
missing_sources:
  - accounting
  - social
  - integration_status
---

# Business Audit Report - 2026-W08

## Operational Metrics
- **Total Actions**: 28
- **Successes**: 25
- **Failures**: 3
- **Success Rate**: 89%
- **Type: email_send**: 12

## Financial Summary
[DATA UNAVAILABLE: accounting]

## Action Item Statistics
- **Needs_Action**: 4
- **Pending_Approval**: 2
- **Done**: 35
```

### CEO Briefing
```markdown
---
type: ceo_briefing
period: 2026-W08
generated: 2026-02-19T10:00:00
data_sources:
  - audit_report
---

# Executive Briefing - 2026-W08

## Key Metrics
- Total Actions: 28
- Success Rate: 89%

## Highlights
- Operations running with mixed results - review failures

## Concerns
- Some operations experienced failures - review logs
- Some data sources were unavailable during report generation

## Recommended Actions
- Configure missing integrations to improve report coverage
- Continue normal operations
```

## Related Skills
- `audit-log` - Report generation events are logged
- `update-dashboard` - Dashboard shows system overview; reports provide deep analysis
- `process-needs-action` - Actions processed feed into report metrics
