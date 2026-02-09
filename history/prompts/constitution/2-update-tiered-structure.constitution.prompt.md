---
id: 2
title: Update Personal AI Employee Constitution
stage: constitution
date: 2026-01-26
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: main
user: Shumaila Waheed
command: /sp.constitution
labels: [constitution,ai-employee,tiered-structure,local-first,human-in-the-loop]
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

Build a comprehensive, tiered project constitution for the "Personal AI Employee" hackathon project (from Panaversity document): an autonomous Digital FTE that proactively manages personal (Gmail, WhatsApp, bank) and business affairs (social media, payments, projects, accounting via Odoo) 24/7. Use Claude Code as reasoning engine (with Ralph Wiggum Stop hook/loop for iterative multi-step task completion), Obsidian as local-first dashboard/memory (single source of truth via Markdown), lightweight Python Watchers for perception (senses: monitor inputs and create .md in /Needs_Action), and Node.js MCP servers for actions (hands: external like email send, browser clicks, Odoo JSON-RPC). System is local-first, privacy-focused, agent-driven, human-in-the-loop for sensitive actions.

This constitution defines NON-NEGOTIABLE principles and standards for ALL phases, Agent Skills, code, and deliverables across tiers: Bronze (Foundation: vault + 1 watcher + read/write), Silver (Functional: multi-watchers + MCP + HITL + scheduling), Gold (Autonomous: cross-domain + Odoo + social integrations + weekly CEO Briefing + autonomous processor). Platinum elements optional/reference only.

Core Principles & Tiered Requirements (ALL MUST comply; higher tiers extend lower):

I. Local-First & Vault as Single Source of Truth
- All persistent state/data in Obsidian vault Markdown files; never external DB unless Odoo self-hosted local (Gold).
- Secrets (.env, tokens, WhatsApp sessions, creds) NEVER in vault/git; use env vars/OS managers, gitignore .env.
- Tier Vault Structure:
  - Bronze: /Inbox, /Needs_Action, /Done
  - Silver+: Add /Pending_Approval, /Approved, /Rejected, /Logs (JSON audit), /Plans
  - Gold+: Add /Business, /Accounting (Odoo data), /Briefings (audits/CEO reports)
- Required Files: Dashboard.md (real-time summary: pending items, watcher/MCP health, balances, recent logs), Company_Handbook.md (rules, thresholds, configs).

II. Autonomy, Proactivity & Ralph Wiggum Loop
- Agent proactive: Watchers trigger reasoning without user input.
- Implement Ralph Wiggum loop (iterative: continue until task complete/blocked/needs approval).
- Gold: Autonomous AI Processor daemon (PM2/systemd) auto-detects /Needs_Action files, invokes Agent Skills, handles multi-step/cross-domain flows, self-schedules (weekly audits).
- Generate Plan.md (checkboxes), update Dashboard, produce autonomous Monday CEO Briefing (audit revenue/bottlenecks).

III. Human-in-the-Loop (HITL) & Safety
- Sensitive/external actions (send email, payments >$500, social posts, Odoo writes, invoices) REQUIRE explicit approval via /Pending_Approval .md file (move to /Approved or /Rejected).
- Approval file format: YAML frontmatter (type:approval_request, action, risk_level, parameters) + description, rationale, risk assessment.
- Auto-approve optional low-risk (config in Handbook, e.g., <100 words emails to known); log as "auto_approved".
- Never auto destructive (delete/transfer money).

IV. Agent Skills Implementation
- ALL AI functionality as reusable Claude Agent Skills (not inline prompts); document in SKILL.md files (purpose, inputs/outputs, approval req, MCP used).
- Skills composable, testable; Gold: invocable by autonomous processor, support background/self-scheduling.

V. Watchers (Perception Layer)
- Python 3.13+ lightweight scripts; follow BaseWatcher pattern (check_for_updates, create_action_file, run loop).
- Bronze: 1 watcher (Gmail or filesystem).
- Silver: 2+ (e.g., Gmail + WhatsApp Playwright + LinkedIn); PM2 required, health checks, graceful shutdown.
- Config: interval via env, log health to /Logs.

VI. MCP Servers (Action Layer)
- Node.js v24+; JSON-RPC over stdio; document in Handbook.
- Silver: At least 1 (e.g., email, Playwright for browser/WhatsApp).
- Gold: Multiple (email, LinkedIn, Facebook, Instagram, Twitter/X, Odoo JSON-RPC for accounting read/write with approval).
- All external via HITL; dry-run support (DRY_RUN=true).

VII. Audit Logging & Observability
- Silver+: Mandatory JSON logs in /Logs/YYYY-MM-DD.json (timestamp, action_type, actor, parameters sanitized, approval_status, result).
- Dashboard shows: pending/approvals, MCP/watcher health, recent logs, error counts.
- Retain 90 days; no PII/creds in logs.

VIII. Scheduling & Process Management
- Silver+: Cron/Task Scheduler for watchers; PM2 for auto-restart, signals handling.
- Gold: Autonomous processor as daemon; schedule weekly Monday audit/briefing.

IX. Gold Tier Specifics
- Cross-domain (Personal + Business) integration.
- Odoo Community local self-hosted; MCP for JSON-RPC (read invoices/transactions, write with approval).
- Social: FB/IG/X posting + summaries.
- Weekly audit: Aggregate Xero-like data (Odoo), social metrics; save to /Briefings/audit_*.md (financial summary, alerts).
- CEO Briefing: Executive summary + insights; /Briefings/ceo_briefing_*.md.

X. Code Quality, Security, Ethics
- Modular, commented, type hints, PEP8/Node best practices, error-resilient (retries, degradation).
- Tests: Bronze manual, Silver automated for critical paths (MCP, HITL).
- Ethical: Disclose AI, avoid high-stakes advice, transparency via vault/logs.
- Git commit after major steps; dry-run mode.

This is the supreme guiding document. All /sp.specify, /sp.plan, /sp.tasks, /sp.implement MUST reference/comply; deviations need justification + approval. Version: 2.0 (updated for full document alignment).

## Response snapshot

Updated the Personal AI Employee constitution to version 2.0, incorporating the detailed tiered structure and requirements. The updated constitution now includes:

1. Ten detailed core principles with specific requirements for each
2. Tiered requirements for Bronze (Foundation), Silver (Functional), Gold (Autonomous), and Platinum (Reference Only) levels
3. Enhanced development workflow with specific quality gates and review processes
4. Clear governance guidelines for ongoing development

The constitution now properly reflects the sophisticated architecture of the Personal AI Employee system with its local-first approach, human-in-the-loop safety measures, and progressive implementation tiers from basic foundation to fully autonomous operation.

## Outcome

- ✅ Impact: Updated constitution to comprehensive tiered structure with detailed requirements
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md to v2.0.0
- 🔁 Next prompts: User can now proceed with /sp.specify to create feature specifications that comply with this enhanced constitution
- 🧠 Reflection: The updated constitution provides much more specific guidance for implementation across the different tiers of the Personal AI Employee system

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with /sp.specify to create first feature specification aligned with tiered requirements