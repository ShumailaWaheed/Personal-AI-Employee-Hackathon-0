---
id: 1
title: Create Personal AI Employee Constitution
stage: constitution
date: 2026-01-26
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution,ai-employee,privacy,security,human-in-the-loop]
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

Build a comprehensive project constitution for the "Personal AI Employee" hackathon project: an autonomous Digital FTE (Full-Time Equivalent) that proactively manages personal and business affairs 24/7 using Claude Code as reasoning engine, Obsidian as local dashboard/memory, lightweight Python Watchers for perception (Gmail, WhatsApp, filesystem monitoring), and Node.js-based MCP servers for actions (email send, browser clicks, etc.). The system is local-first, privacy-focused, agent-driven, with strong human-in-the-loop for sensitive decisions.

Non-negotiable principles and quality standards that ALL future specifications, plans, tasks, implementations, and Agent Skills MUST follow:

1. Privacy & Security First
   - All data (emails, messages, bank info, WhatsApp sessions) remains strictly local; never sync secrets (.env, tokens, sessions) to cloud or git.
   - Use environment variables or secure vaults for credentials; rotate regularly.
   - Minimize data retention: process and delete transient data after action.
   - Log actions auditably but anonymize personal info in logs.
   - Comply with terms of service (e.g., careful with WhatsApp Web automation).

2. Human-in-the-Loop & Safety
   - All sensitive actions (sending emails, payments > $50/500, posting to social media, approving invoices) MUST require explicit human approval via Obsidian file (e.g., /Pending_Approval/) before execution.
   - AI MUST flag uncertain or high-risk decisions and pause for user input.
   - Never auto-execute destructive actions (delete, transfer money) without multi-step confirmation.

3. Autonomy & Proactivity
   - The agent MUST be proactive: use Watchers to detect changes and trigger reasoning loops without waiting for user prompts.
   - Implement Ralph Wiggum Stop hook / loop pattern to continue iterating on multi-step tasks until complete or blocked (e.g., needs approval).
   - Generate Plans.md with checkboxes, update Dashboard.md, and produce Monday Morning CEO Briefing autonomously.

4. Code & Implementation Quality
   - All code (Python watchers, Node.js MCP, orchestration) MUST be modular, well-commented, error-resilient with retries and graceful degradation.
   - Use type hints, logging, and comprehensive error handling.
   - Follow PEP 8 (Python) and standard Node.js best practices.
   - Implement tests where possible; aim for high coverage on core logic (watchers, MCP integrations).
   - Version control everything via Git; commit after major steps (constitution, spec, plan, tasks, implement).

5. Architecture & Tech Adherence
   - Stick to proposed stack: Claude Code (primary brain), Obsidian (GUI/memory), Python 3.13+ (watchers/orchestration), Node.js v24+ (MCP servers).
   - All AI functionality MUST be implemented as reusable Agent Skills (prompts convertible to skills via Claude).
   - Use file-based communication (e.g., /Needs_Action, /Plans, /Done folders) for persistence and multi-agent handoff in higher tiers.
   - Support tiered deliverables: Bronze (basic watcher + vault read/write), Silver (multiple watchers + MCP + approval), Gold (Odoo integration + social posting + weekly briefing), Platinum (cloud/local split + always-on).

6. Documentation & Reusability
   - Every phase (spec, plan, tasks) MUST produce markdown artifacts saved in history/ or appropriate folders.
   - Maintain audit logging for all agent actions.
   - Write clear lessons learned and architecture docs at Gold/Platinum.
   - Favor simplicity, local-first, and exponential scaling over complex cloud setups initially.

7. Ethical & Responsible AI
   - Disclose when communicating as AI (e.g., in emails/social posts).
   - Avoid emotional, legal, medical, or high-stakes advice without human oversight.
   - Ensure transparency: user can always inspect Obsidian vault and logs.

This constitution is the supreme guiding document. All subsequent /sp.specify, /sp.plan, /sp.tasks, /sp.implement MUST explicitly reference and comply with these principles. Any deviation requires justification in the plan and user approval.

## Response snapshot

Created a comprehensive constitution for the Personal AI Employee project that incorporates all seven principles provided by the user. The constitution includes:

1. Privacy & Security First - Ensuring all data remains local and credentials are properly secured
2. Human-in-the-Loop & Safety - Requiring human approval for sensitive actions
3. Autonomy & Proactivity - Making the agent proactive with reasoning loops
4. Code & Implementation Quality - Maintaining high standards for code quality
5. Architecture & Tech Adherence - Following the specified technology stack
6. Documentation & Reusability - Ensuring proper documentation practices
7. Ethical & Responsible AI - Maintaining ethical standards in AI communications

The constitution also includes additional constraints, development workflow requirements, and governance guidelines. The file was created at .specify/memory/constitution.md with version 1.0.0.

## Outcome

- ✅ Impact: Created foundational constitution document that will guide all future development
- 🧪 Tests: none
- 📁 Files: Created .specify/memory/constitution.md with comprehensive principles
- 🔁 Next prompts: User can now proceed with /sp.specify to create feature specifications that comply with this constitution
- 🧠 Reflection: The constitution establishes clear guardrails for privacy, security, and human-in-the-loop requirements which are essential for an AI employee managing personal affairs

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with /sp.specify to create first feature specification