---
id: "gen-20260206-silver-plan-001"
stage: plan
date: 2026-02-06
title: Silver Tier AI Employee Planning
---

# Silver Tier AI Employee Planning

## PROMPT_TEXT

Build Autonomous FTE Silver Tier

Generate a detailed implementation plan for the Silver Tier Personal AI Employee system, extending the Bronze Tier as specified. The plan must include phased deliverables, research findings, key technical decisions with tradeoffs, architecture sketches, data models, MCP contracts, quickstart guides, and validation against success criteria and constitution principles. Ensure backward compatibility with Bronze Tier and emphasize HITL safety, local-first privacy, and modular agent skills.

**Core Silver Tier Additions**:
1. Multi-watcher support: Add WhatsApp (Playwright-based) and LinkedIn (API or browser-based) watchers, building on Gmail/filesystem from Bronze.
2. MCP server integration: Implement at least one MCP server (e.g., for email sending) with JSON-RPC support, routing all external actions through it.
3. Human-in-the-Loop (HITL) approval workflow: Create approval requests in /Pending_Approval for sensitive actions; human moves files to /Approved or /Rejected; execute only approved actions via MCP.
4. Social media automation: Generate and post LinkedIn content about business (e.g., sales generation) with mandatory approval.
5. Scheduling and process management: Use cron/Task Scheduler for basic scheduling; PM2/supervisord/watchdog for 24/7 watcher and processor uptime.
6. Audit logging: Implement mandatory JSON logging in /Logs/YYYY-MM-DD.json for all external actions, following constitution format (no secrets/PII).
7. Enhanced dashboard: Update Dashboard.md to include pending approvals, MCP server status, and log summaries.
8. Claude reasoning loop: Introduce basic loop for creating Plan.md files from /Needs_Action items.

**Reference Documents**:
- Existing Bronze tier spec and plan (assume prior completion).
- Hackathon document: Personal AI Employee Hackathon 0 PDF (Silver tier section on pages 4-5).
- Constitution: CONSTITUTION.md (Sections I-X, especially II, IV, V, VI, VII, IX).
- Existing skills: SKILL.md (extend with new skills like @create-approval-request, @execute-approved-actions).

**Research Required**: Conduct targeted research using web/X search or browsing on:
1. MCP server best practices (e.g., FastMCP vs official @modelcontextprotocol/server; JSON-RPC implementation in Python/Node.js).
2. Email MCP options (SMTP vs API like SendGrid; security considerations).
3. LinkedIn API v2 for posting/monitoring (OAuth2 flow, rate limits, content guidelines).
4. Playwright for WhatsApp Web automation (session persistence, headless mode, TOS compliance).
5. PM2 integration with Python scripts (ecosystem config, auto-restart, monitoring).
6. Audit logging patterns (JSON sanitization, retention policies, error handling).
7. HITL orchestrator designs (file polling vs event-driven; watchdog integration).
8. Cron/Task Scheduler cross-platform setups for AI agents.

**Silver Tier Constraints**:
- Maintain Bronze compatibility: No breaking changes to vault structure or core loops.
- All external actions require HITL approval (no auto-execution for sends/posts).
- Minimum one MCP server (email as default; expandable).
- Audit logging mandatory for traceability.
- Process management essential for reliability (uptime >99%, auto-restart <10s).
- All new functionality as Agent Skills (composable, documented in SKILL.md).
- Timeline: 20-30 hours; align with hackathon meetings.
- Security: DRY_RUN mode, .env for creds, 90-day log retention.

**Plan Structure Guidelines**:
- Phase 0: Research – Summarize findings in research.md with sections per topic.
- Phase 1: Design – Create data-model.md (new entities like ApprovalRequest, AuditLogEntry), contracts/ (JSON schemas for MCP tools), quickstart.md (step-by-step setup).
- Phase 1.5: Architecture Planning – Generate plan.md with summary, technical context, constitution check, project structure, implementation phases.
- Decisions needing documentation: List 7+ key choices (e.g., MCP framework) with options, tradeoffs, and rationale.
- Testing strategy: End-to-end tests for workflows, unit tests for watchers/MCP, validation checklists based on success criteria.
- Technical details: Use concurrent r

## RESPONSE_TEXT

Successfully completed the implementation plan for the Silver Tier Personal AI Employee. Created the following artifacts:

1. Research document (research.md) covering MCP server best practices, LinkedIn API integration, Playwright for WhatsApp automation, PM2 process management, audit logging patterns, email MCP options, HITL orchestrator design, and cross-platform scheduling.

2. Data model document (data-model.md) defining core entities including Watcher Input, Action File, Approval Request, Audit Log Entry, MCP Server Configuration, Plan File, and Process Management Configuration.

3. MCP contract document (email-mcp-contract.md) specifying the interface and capabilities of the Email MCP server with JSON-RPC methods for send_email, get_account_info, and validate_recipients.

4. Quickstart guide (quickstart.md) providing step-by-step instructions for setting up the Silver Tier system including prerequisites, vault structure, environment configuration, MCP server setup, watcher implementations, PM2 configuration, and main processor updates.

5. Implementation plan (plan.md) detailing the technical approach with constitution compliance check, project structure, implementation phases (7 phases from setup to integration testing), key technical decisions (7 major decisions), risk mitigation strategies, and success criteria validation.

All deliverables meet the Silver Tier requirements while maintaining backward compatibility with Bronze Tier and emphasizing HITL safety, local-first privacy, and modular agent skills as specified in the original request.