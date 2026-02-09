---
id: 4
title: Update Constitution Paper Workflow
stage: constitution
date: 2026-01-26
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: main
user: Shumaila Waheed
command: /sp.constitution
labels: [constitution,ai-employee,paper-workflow,specify-workflow]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

/sp.constitution

Create a comprehensive project constitution for the Personal AI Employee Hackathon 0 (Building Autonomous FTEs in 2026) as per the provided Panaversity document. The system is a proactive Digital FTE (Full-Time Equivalent) agent that manages personal affairs (Gmail, WhatsApp, bank/filesystem) and business affairs (social media, payments, project tasks, Odoo accounting) 24/7 on autopilot. Local-first, agent-driven, human-in-the-loop, privacy-focused. Use Claude Code as primary reasoning engine with Ralph Wiggum Stop hook (iterative loop to continue multi-step tasks until complete or blocked), Obsidian vault as local dashboard/memory/GUI (single source of truth in Markdown), lightweight Python Watchers (senses/perception) to monitor inputs and trigger agent via /Needs_Action .md files, Node.js MCP servers (hands/actions) for external operations (email send, browser clicks, Odoo JSON-RPC, etc.).

This constitution MUST define non-negotiable principles, quality standards, and tiered requirements for Bronze (Foundation: vault + 1 watcher + Claude read/write + Agent Skills), Silver (Functional Assistant: multi-watchers + MCP + HITL approval + scheduling + LinkedIn auto-post), Gold (Autonomous Employee: cross-domain personal/business + Odoo integration + FB/IG/X posting/summary + weekly Monday CEO Briefing + autonomous processor + Ralph Wiggum loop + error recovery/logging).

Incorporate these exact document elements:

1. Local-First Vault Structure (tiered):
   - Bronze: /Inbox, /Needs_Action, /Done
   - Silver: + /Pending_Approval, /Approved, /Rejected, /Logs (JSON audit), /Plans
   - Gold: + /Business (tasks), /Accounting (Odoo data), /Briefings (audits/CEO reports)
   - Required files: Dashboard.md (real-time summary: balances, pending, health), Company_Handbook.md (rules, thresholds, configs).

2. Architecture: Perception (Python Watchers) → Reasoning (Claude Code + Ralph Wiggum loop) → Action (MCP servers).
   - Watchers: Lightweight Python scripts (BaseWatcher pattern with __init__, check_for_updates, create_action_file, run loop); examples: Gmail (Google API unread), WhatsApp (Playwright web), Filesystem (watchdog on_created).
   - Ralph Wiggum loop: Claude iterates until task done (e.g., plan → approve → execute).
   - MCP: JSON-RPC stdio; Silver: at least 1 (e.g., email/Playwright); Gold: multiple (Odoo JSON-RPC for accounting, FB/IG/X, etc.).

3. Agent Skills: ALL AI functionality as reusable Claude Agent Skills (not inline prompts); document in SKILL.md with purpose, inputs/outputs, approval req, MCP used; Gold: autonomous invocation.

4. Human-in-the-Loop: Sensitive actions (send email, payments >$500, social post, Odoo write) require /Pending_Approval .md (YAML frontmatter + description/rationale/risk/instructions); move to /Approved or /Rejected; auto-approve optional low-risk in Handbook.

5. Audit Logging: Silver+: JSON in /Logs/YYYY-MM-DD.json (timestamp, action_type, actor, sanitized params, approval_status, result); retain 90 days; Dashboard shows recent entries/health.

6. Scheduling/Process: Silver+: cron/Task Scheduler for watchers; PM2 for restart/graceful shutdown.

7. Gold Specifics: Cross-domain (Personal + Business); Odoo Community self-hosted MCP (read/write with approval); FB/IG/X integrate post/summary; Weekly autonomous audit (Monday) aggregates data → /Briefings/audit_*.md (financial/social summary, alerts); CEO Briefing → /Briefings/ceo_briefing_*.md (exec summary, highlights, action items, priorities).

8. Security/Privacy: Secrets never sync; .env gitignored; dry-run (DRY_RUN=true); ethical disclosure.

9. Code Quality: Modular, commented, error-resilient (retries, degradation), Git commits after steps; tests manual Bronze, automated Silver critical paths.

10. Tiers Deliverables: Exact from document (Bronze: vault + 1 watcher + Claude vault I/O + Skills; Silver: multi watchers + MCP + approval + LinkedIn + scheduling; Gold: Odoo + social + weekly briefing + autonomous + Ralph loop + logging).

This is the supreme guiding document. All future /sp.specify, /sp.plan, /sp.tasks, /sp.implement MUST comply and reference these principles. Any deviation requires justification and approval. Version: 2.2 (full document alignment with tiered vault structures, watchers code patterns, Odoo MCP, CEO Briefing templates).

## Response snapshot

Updated the Personal AI Employee constitution to version 3.0, incorporating the complete paper workflow and project initialization procedures. The updated constitution now includes:

1. Complete paper workflow from /sp.specify to /sp.implement with git integration
2. Project initialization procedures and system setup requirements
3. All core principles with detailed implementation guidelines
4. Complete tiered deliverables with estimated hours
5. BaseWatcher pattern implementation with code examples
6. MCP server specifications and HITL approval workflows
7. CEO Briefing templates and business intelligence reporting
8. Quality standards and git version control procedures

The constitution now fully aligns with the hackathon workflow and provides a complete operational framework for implementing AI-driven papers/tasks.

## Outcome

- ✅ Impact: Updated constitution to comprehensive paper workflow integration with complete implementation guidelines
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md to v3.0.0
- 🔁 Next prompts: User can now proceed with /sp.specify to create first paper specification following the complete workflow
- 🧠 Reflection: The updated constitution provides a complete operational framework for the Personal AI Employee Hackathon

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with /sp.specify to create first paper specification