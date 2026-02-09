# Feature Specification: Build Autonomous FTE Silver Tier

**Feature Branch**: `002-silver-tier`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Build Autonomous FTE Silver Tier

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
- Logging: JSON format exactly as in constitution (no secrets/PII in logs)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Channel Watcher Processing with HITL Approval (Priority: P1)

A hackathon participant wants to extend their Bronze tier AI employee to monitor multiple channels (Gmail, WhatsApp, LinkedIn) simultaneously and perform external actions like sending emails or posting on LinkedIn, but with mandatory human approval for all sensitive operations. The system should process inputs from all three channels, generate approval requests for external actions, and only execute approved actions.

**Why this priority**: This is the core functionality defining Silver tier - multi-channel monitoring with external action capabilities and HITL approval, which extends Bronze tier significantly.

**Independent Test**: The system can receive inputs from Gmail, WhatsApp, and LinkedIn simultaneously, create Plan.md files for complex tasks, route sensitive actions to /Pending_Approval, and execute only approved actions via MCP servers.

**Acceptance Scenarios**:

1. **Given** inputs arrive from Gmail, WhatsApp, and LinkedIn simultaneously, **When** sensitive actions are detected, **Then** Plan.md files are created and approval requests appear in /Pending_Approval
2. **Given** an approval request exists in /Pending_Approval, **When** operator moves file to /Approved, **Then** action executes via MCP server and results are logged

---

### User Story 2 - MCP Server Integration for External Actions (Priority: P1)

A developer wants to execute external actions like sending emails or LinkedIn posts securely through MCP servers that handle authentication separately, preventing credential exposure in the vault or codebase.

**Why this priority**: This is fundamental to the security model and architecture - external actions must be routed through MCP servers to maintain security compliance.

**Independent Test**: The system can route external action requests to an MCP server (like email sending) and receive execution results back without exposing credentials.

**Acceptance Scenarios**:

1. **Given** an approved external action request, **When** MCP action execution skill is triggered, **Then** action executes via MCP server and result is received

---

### User Story 3 - Continuous Operation and Process Management (Priority: P2)

An operator wants the AI employee system to run continuously for 24+ hours with reliable process management to handle crashes and restarts automatically.

**Why this priority**: This provides the production-like reliability that distinguishes Silver tier from Bronze, ensuring the system works consistently over time.

**Independent Test**: The system runs continuously for 24+ hours using PM2 or similar process manager, with automatic restart on crashes.

**Acceptance Scenarios**:

1. **Given** system is started with PM2, **When** a process crashes, **Then** it automatically restarts

---

### User Story 4 - Structured Audit Logging and Dashboard Updates (Priority: P2)

An operator wants comprehensive audit trails of all actions taken by the AI employee and real-time dashboard updates showing pending approvals and system status.

**Why this priority**: Essential for transparency, compliance, and operational visibility in the HITL model.

**Independent Test**: The system creates structured JSON audit logs and updates Dashboard.md with pending approval counts and MCP status.

**Acceptance Scenarios**:

1. **Given** an action is executed, **When** logging occurs, **Then** structured JSON entry appears in /Logs/YYYY-MM-DD.json
2. **Given** system status changes, **When** dashboard updates, **Then** Dashboard.md reflects current status

---

### Edge Cases

- What happens when MCP server becomes unavailable during action execution?
- How does the system handle rate limits on LinkedIn posting (1-3 posts/day)?
- What occurs when multiple watchers generate conflicting actions simultaneously?
- How does the system behave during extended periods of network unavailability?
- What happens when the vault directory structure is corrupted?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support at least three simultaneous watchers: Gmail (API-based), WhatsApp (Playwright-based), and one additional source
- **FR-002**: System MUST maintain full backward compatibility with existing Bronze tier functionality
- **FR-003**: System MUST route all sensitive external actions through MCP servers using JSON-RPC over stdio or HTTP
- **FR-004**: System MUST require Human-in-the-Loop approval for all sensitive operations before execution
- **FR-005**: System MUST create Plan.md files for complex multi-step tasks before execution
- **FR-006**: System MUST move approval request files to /Pending_Approval directory for human review
- **FR-007**: System MUST execute actions only when approval files are moved to /Approved directory
- **FR-008**: System MUST create structured JSON audit logs in /Logs/YYYY-MM-DD.json format
- **FR-009**: System MUST update Dashboard.md with pending approval counts and system status
- **FR-010**: System MUST run continuously for 24+ hours using process management tools like PM2
- **FR-011**: System MUST handle crashes and restart automatically
- **FR-012**: System MUST not store any credentials, tokens, or PII in vault or commit to git
- **FR-013**: System MUST respect DRY_RUN configuration for development and testing
- **FR-014**: LinkedIn automation MUST respect rate limits of 1-3 posts per day
- **FR-015**: System MUST integrate with Claude agent skills for all AI logic as defined in SKILL.md

### Key Entities

- **Watcher Input**: Data or events received from external sources (Gmail, WhatsApp, LinkedIn) that may trigger system actions
- **Approval Request**: Markdown file representing an action that requires human approval before execution
- **MCP Action**: External action that must be processed by an MCP server for security reasons
- **Audit Log Entry**: Structured JSON record containing comprehensive information about system actions and their outcomes
- **Process Manager**: Tool (like PM2) that ensures continuous operation and handles restarts for system components
- **Plan File**: Detailed Markdown document outlining complex multi-step tasks to be executed by the system

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All Bronze tier features continue to function unchanged during Silver tier operation
- **SC-002**: At least three watchers operate simultaneously: Gmail, WhatsApp, and one additional source
- **SC-003**: End-to-end HITL approval workflow functions: detection → Plan.md → /Pending_Approval → approval → execution → logging
- **SC-004**: At least one MCP server integrates successfully for external action execution
- **SC-005**: Automated LinkedIn post generation and execution demonstrates complete workflow
- **SC-006**: System runs continuously for 24+ hours without manual intervention
- **SC-007**: All external actions produce structured JSON audit entries with complete metadata
- **SC-008**: Dashboard.md updates accurately reflect pending approvals, MCP status, and log summaries
- **SC-009**: All security constraints met: no credentials in vault/git, DRY_RUN respected, skills properly documented
- **SC-010**: Silver tier functionality provides measurable productivity improvement over manual processing