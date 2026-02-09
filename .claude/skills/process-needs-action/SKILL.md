
# Process Needs Action Skill

## Description
This skill scans the /Needs_Action folder for pending tasks, analyzes each one based on the Company Handbook rules, and creates detailed action plans in the /Plans folder. It's the primary skill for transforming detected items into actionable work.

## When to Use
Use this skill when:
- New tasks appear in the /Needs_Action directory
- Tasks need detailed planning before execution
- You need to transform high-level requirements into actionable steps
- Dashboard needs updating with current task status
- Activity logging is required

## Inputs
- Markdown files from /Needs_Action directory containing pending tasks with metadata
- AI_Employee_Vault/Company_Handbook.md for processing rules
- AI_Employee_Vault/Business_Goals.md for priority context

## Outputs
- Detailed action plans in /Plans directory
- Updated action files with in_progress status
- Refreshed dashboard in Dashboard.md
- Activity logs in /Logs/YYYY-MM-DD.json

## Approval Required
- No for Bronze tier tasks (direct processing)
- Yes for Silver tier sensitive tasks (routed via `hitl-approval` skill)

## MCP Servers Used
- None directly. Sensitive actions are routed to `hitl-approval` which later uses MCP for execution.

## Silver Tier Enhancements
In Silver tier, this skill is enhanced by `SilverProcessor` which:
1. Runs `detect-sensitive-action` on each task before processing
2. Routes sensitive actions to `/Pending_Approval` via `hitl-approval`
3. Only processes non-sensitive actions directly (Bronze behavior preserved)
4. Creates audit log entries for all processing via `audit-log`
5. Updates dashboard after processing via `update-dashboard`

**Code**: `src/processors/silver_processor.py` extends `src/processors/vault_processor.py`

## Process Steps

### 1. Read Company Handbook
- Read AI_Employee_Vault/Company_Handbook.md to understand processing rules
- Note priority keywords and file handling guidelines

### 2. Scan Needs_Action Folder
- List all markdown files in AI_Employee_Vault/Needs_Action/
- Filter for files with status: pending in frontmatter
- Sort by priority (high → medium → low)

### 3. Process Each Action Item
For each pending file:

#### a. Read and Parse
- Read the full file content
- Extract frontmatter metadata (type, priority, source_file, detected)
- Identify the source file type and context

#### b. Analyze Content
- Based on file type and content, determine appropriate action
- Check for priority keywords (URGENT, CLIENT, INVOICE, DEADLINE)
- Cross-reference with Company Handbook rules
- Consider Business_Goals.md priorities

#### c. Create Detailed Plan
- Create a new file in AI_Employee_Vault/Plans/
- Filename: PLAN_[YYYYMMDD_HHMMSS]_[source_filename].md
- Include:
  - Clear objective
  - Step-by-step actions with checkboxes
  - Required information or approvals
  - Expected outcome
  - Links to related files

#### d. Update Action File
- Change status from pending to in_progress
- Add processing timestamp
- Add link to created plan

### 4. Update Dashboard
- Update AI_Employee_Vault/Dashboard.md
- List all pending actions with priorities
- Show count of items processed
- Update "Last Check" timestamp

### 5. Log Activity
- Append to today's log file in AI_Employee_Vault/Logs/YYYY-MM-DD.json
- Record: files processed, plans created, any errors

## Quality Criteria
- All pending action files are reviewed
- At least one detailed plan is created for each action
- Action files are updated to in_progress
- Dashboard shows current status
- Log entry created
- Plan follows template with all required sections
- Priority assessment is accurate
- Links between files are maintained

## Plan Template
Use this template when creating plans:

```
---
created: [ISO timestamp]
source_action: [filename of action file]
priority: [high/medium/low]
status: pending_approval
---

# Plan: [Clear Title]

## Objective
[What needs to be accomplished]

## Context
[Background information from source file]

## Action Steps
- [ ] Step 1: [Specific action]
- [ ] Step 2: [Specific action]
- [ ] Step 3: [Specific action]

## Required Resources
- [Any files, information, or approvals needed]

## Expected Outcome
[What success looks like]

## Notes
[Any additional considerations]
```

## Example Usage
When invoked, the skill will:
1. Find pending files in /Needs_Action
2. Read Company_Handbook.md for rules
3. Create detailed plans in /Plans
4. Update the action files to "in_progress"
5. Refresh Dashboard.md with current counts
6. Log all activity