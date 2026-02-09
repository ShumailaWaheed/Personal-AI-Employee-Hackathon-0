# Mark Done

Mark a task as done and move it to the Done folder.

## Description
This skill handles the completion workflow for tasks. It updates the task status, adds done metadata, moves files to the Done folder, and updates the Dashboard. This ensures proper task lifecycle management and audit trail.

## Instructions

1. **Identify Task to Mark Done**
   - User will provide either:
     - Full filename (e.g., `FILE_20260110_142301_invoice.md`)
     - Partial identifier (e.g., "marketing analysis task")
     - Task number from Dashboard listing

   - Search in these locations:
     - `AI_Employee_Vault/Needs_Action/` (in-progress tasks)
     - `AI_Employee_Vault/Plans/` (active plans)

2. **Verify Done Eligibility**
   - Read the task file
   - Check if all required steps are completed:
     - For action files: verify all suggested actions are done
     - For plans: verify all checkboxes are checked

   - If not all steps are complete:
     - Ask user if they want to mark as done anyway
     - If no, abort and report remaining steps

3. **Update Task File**
   - Add done metadata to frontmatter:
     ```yaml
     status: done
     done_at: [ISO timestamp]
     done_by: ai_employee
     ```

   - Add done summary at end of file:
     ```markdown
     ## Done Summary
     - Done: [ISO timestamp]
     - Duration: [time from detection to done]
     - Outcome: [brief description of result]
     ```

4. **Move to Done Folder**
   - Move the updated file to `AI_Employee_Vault/Done/`
   - Maintain original filename for traceability

   - If related plan exists in `/Plans`:
     - Move plan to `/Done` as well
     - Link them in done notes

5. **Update Dashboard**
   - Increment done counter
   - Add to "Recent Activity" section
   - Remove from "Pending Actions" list
   - Update "Done This Week" stat

6. **Log Done**
   - Append to today's log file
   - Include:
     - Task identifier
     - Done timestamp
     - Brief outcome description
     - Files moved

## Done Summary Template

Add this to the end of done task files:

```markdown
---

## Done Summary
- Done: [ISO timestamp]
- Duration: [X hours/days from detection]
- Outcome: [What was accomplished]
- Related Files:
  - Original: [Inbox/filename if applicable]
  - Plan: [Plans/plan_filename.md if applicable]
  - Archive: Done/[this file]

## Performance Metrics
- Response Time: [time from detection to first action]
- Total Time: [time from detection to done]
- Priority: [original priority level]

*Task marked done by AI Employee v0.1*
```

## Success Criteria
- Task file updated with done metadata
- File moved to Done folder
- Dashboard updated with done status
- Log entry created
- Related files also archived

## Example Usage

**User:** `claude skill mark-done marketing analysis`

**Expected Behavior:**
1. Find `task_quarterly_marketing_analysis.md` in /Needs_Action
2. Add done metadata
3. Move to Done folder
4. Find related `PLAN_20260129_012036_task_quarterly_marketing_analysis.md` in /Plans
5. Move plan to Done folder as well
6. Update Dashboard:
   - Remove from Pending Actions
   - Add to Recent Activity: "[2026-01-29 01:30] Processed marketing analysis"
   - Increment done counter
7. Log done event

## Error Handling

If task cannot be found:
```
Error: Could not find task matching "marketing analysis"

Available tasks in Needs_Action:
1. task_quarterly_marketing_analysis.md
2. task_supplier_negotiation.md
3. task11_customer_retenion_strategy.md

Please specify the full filename or select a number.
```

## Related Skills
- Use `process-needs-action` to create tasks from inbox items
- Use `update-dashboard` to refresh the dashboard after marking done