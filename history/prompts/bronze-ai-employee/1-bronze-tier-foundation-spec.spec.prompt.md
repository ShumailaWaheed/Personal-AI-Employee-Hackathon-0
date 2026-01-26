---
id: 1
title: bronze-tier-foundation-spec
stage: spec
date: 2026-01-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: bronze-ai-employee
branch: main
user: ShumailaWaheed
command: sp.specify
labels: [specification, ai-employee, bronze-tier, obsidian-vault, watcher]
links:
  spec: ../specs/003-bronze-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-bronze-ai-employee/spec.md
  - specs/003-bronze-ai-employee/checklists/requirements.md
tests:
  - spec-validation
---

## Prompt

```text
# Build Bronze Tier Foundation for Personal AI Employee
**Target audience:** Hackathon participants with intermediate command line/API skills, aiming to establish the minimum viable agent foundation.

## Objective
Establish a **local-first architecture** with Obsidian vault as the single source of truth, a working Watcher for perception, Claude Code for reading/writing vault files, and initial Agent Skill implementation. No external actions or HITL approval yet.

## Scope / Focus
- Obsidian vault as memory/dashboard
- One working Watcher (Gmail OR filesystem) for perception
- Claude Code reading/writing vault files
- First reusable Agent Skill(s)
- Local-first: no external dependencies required for core vault operations
- No external actions, scheduling, or multiple watchers

## Success Criteria
- Vault **AI_Employee_Vault** created with folders: `/Inbox`, `/Needs_Action`, `/Done`
- **Dashboard.md** shows real-time basic status: pending items count, last watcher activity, recent actions (last 24h)
- **Company_Handbook.md** created with basic rules (e.g., "Flag payments >$500", "Be polite on WhatsApp") and placeholders for priority/follow-up
- **Watcher script** (Gmail OR filesystem) creates `.md` action files in `/Needs_Action` on new input
- **Duplicate detection**: Watcher tracks processed items to prevent duplicates
- **Environment variable configuration** for watcher: check interval, source path/account, credentials (if Gmail)
- **Claude Code** reads action items and writes `Plan.md` or summaries with checkboxes
- **At least one Agent Skill** implemented and documented in `SKILL.md` (purpose, inputs, outputs; no approval yet)
- **All AI functionality** implemented as reusable Agent Skills (no inline prompts)
- **Error handling and logging**: graceful failure on watcher/Claude errors, console/log outputs without exposing credentials
- **Git repo initialized** with constitution committed and vault structure committed
- End-to-end workflow (Watcher → Action Item → Claude Code → Plan.md) can run **locally under 5 minutes**
- **System setup time** <3 hours; runs locally without internet dependency for core vault operations

## Constraints
- Exact stack: Obsidian v1.10.6+, Python 3.13+, Claude Code
- No Node.js/MCP yet
- Vault is single source of truth; all state in Markdown files
- Privacy: No secrets in vault/git; `.env` gitignored if used
- Timeline: 8–12 hours total for hackathon MVP
- Format: Markdown files, Python scripts, Git commits after major steps

## Key Entities
- **Action Item**: detected item requiring attention; attributes: source (email/file), title/subject, content summary, timestamp, priority placeholder
- **Plan**: structured response to an action item; attributes: linked action item, created timestamp, checkboxes, priority/due date placeholders
- **Dashboard**: real-time status summary; attributes: pending items count, recent actions, watcher status, last update timestamp
- **Company Handbook**: configuration/rules document; contains watcher settings, processing rules, priority placeholders

## Out of Scope
- Any MCP servers or external actions (email/social)
- Multiple watchers, autonomous processors, cross-domain
- Odoo/social integrations, CEO Briefing, audit logging
- Platinum cloud features, Syncthry, A2A

## Edge Cases / Notes
- Watcher handles permission issues and malformed files gracefully
- Duplicate action items are not created
- System logs errors without crashing
- Company_Handbook.md rules can be expanded for future priority/due-date logic
```

## Response snapshot

Created a comprehensive feature specification for the Bronze Tier Foundation for Personal AI Employee. The specification includes:

- User scenarios with priorities (P1-P3) and acceptance scenarios
- Functional requirements (FR-001 through FR-013) covering all aspects of the system
- Key entities definition for Action Items, Plans, Dashboard, Company Handbook, and Agent Skills
- Success criteria (SC-001 through SC-008) with measurable outcomes
- Edge cases addressing potential error conditions and system failures

The specification follows the template structure and avoids implementation details, focusing on user value and business needs. It defines a local-first architecture with Obsidian vault as the single source of truth, watcher functionality, Claude Code integration, and reusable agent skills.

## Outcome

- ✅ Impact: Created complete feature specification for Bronze Tier Foundation
- 🧪 Tests: Specification validation completed successfully
- 📁 Files: Created spec.md and requirements checklist
- 🔁 Next prompts: Ready for planning phase (/sp.plan)
- 🧠 Reflection: Specification is comprehensive and ready for implementation planning

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin planning phase