---
id: "gen-20260206-silver-tier-spec-002"
stage: spec
date: 2026-02-06
title: Silver Tier AI Employee Specification Creation
---

# Silver Tier AI Employee Specification Creation

## PROMPT_TEXT

Build Autonomous FTE Silver Tier

Target audience: Hackathon participants who have completed Bronze tier and want to advance to a functional assistant level, enabling safe external interactions and multi-channel monitoring.

Focus: Extend the Bronze local-first foundation with multi-watcher perception (Gmail + WhatsApp + LinkedIn), secure external actions via MCP servers, mandatory human-in-the-loop (HITL) approval for all sensitive operations, basic social media automation (LinkedIn posting with approval), continuous process management, and structured audit logging. Maintain full backward compatibility with Bronze tier while adding production-like reliability and safety.

Success criteria:
- All Bronze tier features continue to function unchanged (single watcher processing, vault read/write, basic agent skills).
- At least three watchers operational: Gmail (API-based), WhatsApp (Playwright-based), and one more (e.g., LinkedIn or filesystem drop).
- End-to-end HITL approval workflow works: sensitive action detected → Plan.md created → approval request file in /Pending_Approval → human review/move to /Approved or /Rejected → approved actions executed via MCP → logged and moved to /Done.
- At least one MCP server running and integrated (email sending recommended as simplest; must support JSON-RPC over stdio or HTTP).
- Automated LinkedIn post generation and execution demonstrated (draft in plan → approval → post via MCP → success logged).
- Watchers and processor run continuously for 24+ hours using PM2 (or equivalent like supervisord/watchdog).
- All external/sensitive actions produce structured JSON audit entries in /Logs/YYYY-MM-DD.json (timestamp, action_type, actor, target, parameters, approval_status, result).
- Dashboard.md updated to show pending approvals count, MCP server status, and recent log summary.
- Compliance with constitution: Local-first preserved, secrets never in vault/git, DRY_RUN respected, all AI logic as Agent Skills in SKILL.md.

Constraints:
- Tech stack additions: PM2 (npm install -g pm2), Playwright (pip install playwright && playwright install), additional libs (google-api-python-client if not already, requests if needed for MCP).
- Tier: Silver (20-30 hours estimated).
- Format: Markdown outputs in vault folders (/Specs, /Plans, /Pending_Approval, /Logs, etc.); Watcher code in Python; MCP in Node.js or compatible.
- Dependencies: Must use existing BaseWatcher pattern; MCP follows official Model Context Protocol spec (stdio/HTTP transport).
- Timeline: Align with hackathon pace and Wednesday research meetings; test incrementally.
- Security:
  - All external actions (send email, post LinkedIn, browser actions) require HITL approval by default.
  - No auto-approval for high-risk actions (payments, personal comms).
  - Credentials/tokens in .env only (gitignore).
  - Approval timeout flag optional (e.g., 24h no auto-reject).
- Backward compatibility: Bronze vault structure and single-watcher mode must still work.

Not building:
- Cross-domain personal/business separation or Odoo integration (Gold+).
- Multiple MCP servers or advanced delegation (Platinum).
- Full Ralph Wiggum autonomous multi-step persistence (Gold+).
- Cloud 24/7 deployment or synced vault delegation (Platinum).
- Facebook/Instagram/Twitter full integrations or weekly CEO briefings (Gold+).
- Advanced error recovery, graceful degradation, or comprehensive audit beyond basic logging (Gold+).
- Multi-user support or team delegation.

Additional notes:
- MCP server recommendation: Start with a simple email-sending server (e.g., using SMTP via Node.js) or reference community servers from modelcontextprotocol/servers repo.
- LinkedIn automation: Limit to 1-3 posts/day to respect rate limits; content generated via Claude skill based on business goals in Company_Handbook.md.
- Process management: Use PM2 ecosystem file or simple start scripts; include restart on crash.
- Logging: JSON format exactly as in constitution (no secrets/PII in logs).

## RESPONSE_TEXT

Specification created at specs/002-silver-tier/spec.md with all required sections including user scenarios, functional requirements, and success criteria. Created quality checklist at specs/002-silver-tier/checklists/requirements.md. The specification covers all aspects of the Silver tier functionality including multi-watcher support, MCP server integration, HITL approval workflows, process management, and audit logging as requested in the user input.