# Feature Specification: Gold Tier Autonomous System

**Feature Branch**: `004-gold-tier`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Personal AI Employee - Gold Tier Autonomous System with fully autonomous background processing, business integrations, cross-domain workflows, audit/briefings, and backward compatibility with Bronze and Silver tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autonomous Action Item Processing (Priority: P1)

As a user, I want the AI Employee to automatically detect and process new action items without manual commands, so that routine work is handled continuously in the background.

**Why this priority**: This is the foundational Gold-tier capability. Without autonomous processing, all other Gold features are impossible. It transforms the system from a manually-invoked tool into a true autonomous employee.

**Independent Test**: Can be fully tested by placing action item files in `/Needs_Action/` and verifying they are automatically analyzed, prioritized, planned, and either completed (internal actions) or routed to approval (external actions) without any manual invocation.

**Acceptance Scenarios**:

1. **Given** the autonomous processor is running and a new action item file is placed in `/Needs_Action/`, **When** the next processing cycle occurs, **Then** the system detects the file, analyzes its content, determines priority and domain, and generates a plan within the configured interval.
2. **Given** an action item requires an external action (e.g., sending an email), **When** the system processes it, **Then** an approval request is created in `/Pending_Approval/` before any external execution occurs.
3. **Given** an action item requires only internal vault operations, **When** the system processes it, **Then** the action is completed autonomously, logged, and the file is moved to `/Done/`.
4. **Given** the autonomous processor is disabled via configuration, **When** a new action item appears, **Then** the system does not process it until re-enabled.
5. **Given** multiple action items exist with different urgency levels, **When** the system processes the queue, **Then** higher-priority items are processed before lower-priority ones.

---

### User Story 2 - Business Accounting Automation (Priority: P2)

As a business owner, I want the AI Employee to manage accounting-related tasks through an external accounting system, so that financial records stay updated with minimal manual effort.

**Why this priority**: Financial operations are the highest-value business integration. Automating accounting tasks directly reduces operational overhead for founders and solo entrepreneurs.

**Independent Test**: Can be fully tested by creating an accounting-related action item (e.g., "Record expense of $500 for software licenses") and verifying it generates an approval request, routes through MCP to the accounting system upon approval, and stores the transaction record locally.

**Acceptance Scenarios**:

1. **Given** a valid accounting MCP connection and an action item requesting expense recording, **When** the system processes the item, **Then** an approval request is created with the expense details, target system, and risk assessment.
2. **Given** an approved accounting action, **When** the system executes it, **Then** the transaction is created in the accounting system via MCP and a local record is stored in `/Business/Accounting/`.
3. **Given** the accounting MCP connection fails during execution, **When** the system encounters the error, **Then** it retries with exponential backoff up to 3 times, then queues the action for later retry and notifies the user.
4. **Given** an invoice creation request, **When** processed, **Then** the system requires approval before creating the invoice and logs the complete transaction lifecycle.

---

### User Story 3 - Social Media Operations (Priority: P3)

As a business owner, I want the AI Employee to assist with social media posting and performance tracking, so that online presence remains consistent.

**Why this priority**: Social media presence is critical for business growth but repetitive. Automating content proposals and posting (with approval) frees significant time while maintaining quality control.

**Independent Test**: Can be fully tested by creating a social media action item (e.g., "Post LinkedIn update about product launch") and verifying content is proposed for approval, posted via MCP upon approval, and engagement data is collected afterward.

**Acceptance Scenarios**:

1. **Given** a social media action item, **When** the system processes it, **Then** it generates proposed content and creates an approval request in `/Pending_Approval/` with the draft content and target platform.
2. **Given** approved social media content, **When** the system executes the post, **Then** it posts via the platform MCP server and logs the result with a reference to the posted content.
3. **Given** a platform MCP server is unavailable, **When** the system attempts to post, **Then** it queues the action, retries later, and does not block processing of other action items or domains.
4. **Given** a previously posted item, **When** the configured engagement check interval elapses, **Then** engagement metrics are collected and summarized in a local report file.

---

### User Story 4 - Weekly Business Audit & Executive Briefing (Priority: P4)

As a decision-maker, I want an automatic weekly audit and executive summary, so that I can understand business health at a glance.

**Why this priority**: Regular business intelligence provides the strategic value that distinguishes an AI Employee from simple task automation. It enables informed decision-making without manual report compilation.

**Independent Test**: Can be fully tested by triggering a scheduled audit cycle and verifying that financial, operational, and activity data are aggregated into an audit report and executive briefing in `/Briefings/`.

**Acceptance Scenarios**:

1. **Given** the scheduled audit time arrives (configurable, default Monday 9AM), **When** the audit process runs, **Then** it aggregates data from `/Business/Accounting/`, `/Logs/`, and vault activity into a comprehensive audit report at `/Briefings/audit_YYYY-MM-DD.md`.
2. **Given** the audit report is generated, **When** the briefing generation runs, **Then** a concise executive briefing is created at `/Briefings/ceo_briefing_YYYY-MM-DD.md` summarizing key metrics, anomalies, and recommended actions.
3. **Given** some data sources are unavailable during audit, **When** the audit runs, **Then** the report clearly marks missing data sections without failing the entire audit.
4. **Given** no activity occurred during the audit period, **When** the audit runs, **Then** a valid report is generated noting zero activity rather than producing an error.

---

### User Story 5 - Cross-Domain Workflows (Priority: P5)

As a user, I want the AI Employee to handle workflows that span personal and business contexts, so that tasks are routed correctly regardless of their domain.

**Why this priority**: Real-world tasks often cross boundaries between personal and business contexts. Correct routing and domain-aware processing prevent errors and ensure appropriate approval levels.

**Independent Test**: Can be fully tested by creating action items that span both personal and business domains and verifying they are classified correctly, require appropriate approvals, and metrics reflect activity in both domains.

**Acceptance Scenarios**:

1. **Given** an action item that involves both personal and business contexts (e.g., "Schedule meeting with investor and update personal calendar"), **When** the system processes it, **Then** it classifies each sub-action by domain and routes accordingly.
2. **Given** a cross-domain action, **When** the system detects it spans domains, **Then** it requires explicit approval before executing cross-domain operations.
3. **Given** the business domain integration is degraded, **When** a personal-domain action item arrives, **Then** the personal domain continues to operate independently without being affected.
4. **Given** actions across both domains, **When** metrics are aggregated, **Then** the dashboard reflects individual domain metrics and combined totals.

---

### User Story 6 - Reliability & Failure Recovery (Priority: P6)

As a system owner, I want the AI Employee to recover from errors automatically, so that reliability is maintained without constant monitoring.

**Why this priority**: An autonomous system that crashes and stays down is worse than a manual one. Reliability is the baseline expectation for any system claiming to be an "employee."

**Independent Test**: Can be fully tested by simulating various failure scenarios (MCP timeout, malformed action file, process crash) and verifying the system recovers gracefully, retries appropriately, and notifies when human intervention is needed.

**Acceptance Scenarios**:

1. **Given** an external MCP call fails, **When** the system encounters the error, **Then** it retries with exponential backoff (3 attempts), logs each attempt, and queues for later if all retries fail.
2. **Given** the main processor crashes, **When** the process manager detects the crash, **Then** it automatically restarts the processor and logs the crash event.
3. **Given** a persistent failure (more than 3 consecutive failures for the same integration), **When** the retry limit is exceeded, **Then** the system creates a notification action item in `/Needs_Action/` alerting the user and marks the integration as degraded.
4. **Given** one domain integration is failing, **When** other domains receive action items, **Then** they continue processing normally without cascade failure.

---

### Edge Cases

- What happens when an action item file has no recognizable content or is empty? The system logs the issue, moves the file to a quarantine area, and continues processing other items.
- What happens when multiple action items arrive simultaneously? The system queues and processes them in priority order, handling concurrency through sequential processing with priority sorting.
- What happens when an approved action's target system has changed its interface? The system detects the MCP protocol error, logs it, and creates a notification for the user rather than sending malformed data.
- What happens when the vault filesystem runs out of space? The system detects the write failure, pauses processing, and creates an urgent notification.
- What happens when a scheduled audit overlaps with heavy action processing? The audit runs in its own processing cycle and does not block or be blocked by action processing.
- What happens when credentials expire mid-operation? The system detects authentication failure, marks the integration as degraded, and notifies the user to refresh credentials.

## Requirements *(mandatory)*

### Functional Requirements

**Autonomous Processing**

- **FR-001**: System MUST run a background processor that continuously monitors `/Needs_Action/` for new action items at a configurable interval (default: 30 seconds).
- **FR-002**: System MUST determine each action item's priority (urgent, high, normal, low) using frontmatter metadata (`priority:` field) when present, falling back to keyword-based inference from content for unstructured items. System MUST also determine domain (personal, business, cross-domain) and required action type.
- **FR-003**: System MUST generate a processing plan for each action item before execution, stored in `/Plans/`.
- **FR-004**: System MUST support enabling and disabling autonomous processing mode via configuration without requiring a restart.
- **FR-005**: System MUST process action items in priority order when multiple items are pending.

**Approval & Execution**

- **FR-006**: All external actions (any action that communicates outside the local vault) MUST require explicit human approval before execution, unless the action is classified as low-risk and auto-approval is explicitly enabled via configuration (default: disabled). Auto-approved actions MUST still be fully logged.
- **FR-007**: Approved actions MUST execute exclusively through registered MCP servers.
- **FR-008**: System MUST create structured approval request files in `/Pending_Approval/` with action details, risk assessment, and clear approve/reject instructions.
- **FR-009**: System MUST monitor `/Approved/` and `/Rejected/` directories for approval decisions and act on them within the next processing cycle.
- **FR-010**: System MUST archive completed actions to `/Done/` with execution results and timestamps.

**Business Integrations**

- **FR-011**: System MUST integrate with an accounting system via MCP for expense recording and invoice creation/sending. Scope is limited to these two operations for Gold tier; additional accounting operations (payments, bank reconciliation, contacts) are out of scope.
- **FR-012**: System MUST integrate with LinkedIn, Facebook, and WhatsApp via MCP for content posting and engagement data collection. These three platforms define the Gold tier social/messaging scope.
- **FR-013**: System MUST store local copies of all business data synchronized from external systems in the appropriate vault subdirectories (`/Business/Accounting/`, `/Business/Social/`).
- **FR-014**: System MUST handle integration failures independently per integration without affecting other integrations or domains.

**Audit & Reporting**

- **FR-015**: System MUST generate weekly audit reports aggregating financial, operational, and activity data on a configurable schedule.
- **FR-016**: System MUST generate concise executive briefings summarizing the audit findings, anomalies, and recommended actions.
- **FR-017**: System MUST clearly mark missing or unavailable data in reports rather than failing silently or omitting sections.

**Cross-Domain Support**

- **FR-018**: System MUST classify each action item into a domain (personal, business, or cross-domain) based on content analysis.
- **FR-019**: Cross-domain actions MUST require explicit approval regardless of risk level.
- **FR-020**: Each domain MUST operate independently such that degradation in one domain does not cascade to others.

**Reliability**

- **FR-021**: System MUST retry failed external operations with exponential backoff (up to 3 attempts per operation).
- **FR-022**: System MUST support automatic restart via process manager after unexpected crashes.
- **FR-023**: System MUST generate human-readable notifications for persistent failures requiring manual intervention.
- **FR-024**: System MUST maintain a persistent operation queue for failed actions, stored as Markdown files in the vault (e.g., `/Business/retry_queue.md`), so they survive system restarts and can be retried when the integration recovers.

**Observability**

- **FR-025**: System MUST log all actions, decisions, approvals, and errors in structured JSON format in `/Logs/`.
- **FR-026**: System MUST maintain a unified dashboard (`Dashboard.md`) reflecting current system state, pending items, integration health, and recent activity across all domains.
- **FR-027**: System MUST expose per-integration and per-domain health status in the dashboard.

**Compatibility**

- **FR-028**: System MUST preserve all Bronze tier functionality (vault watching, action file creation, basic processing).
- **FR-029**: System MUST preserve all Silver tier functionality (HITL approval, MCP integration, multi-watcher, audit logging, sensitive action detection).
- **FR-030**: Gold-tier features MUST be individually configurable so they can be disabled without affecting Bronze/Silver functionality.

**Security**

- **FR-031**: System MUST manage all credentials through environment variables or OS secret manager, never in vault files or code.
- **FR-032**: System MUST sanitize all PII from audit logs per the existing log sanitization patterns.
- **FR-033**: System MUST support dry-run mode (`DRY_RUN=true`) for all external operations.
- **FR-034**: System MUST support an opt-in auto-approval mode (default: disabled) that automatically approves low-risk external actions matching configured criteria. Auto-approved actions MUST be logged identically to manually approved actions, with the approval source marked as "auto".

### Key Entities

- **Action Item**: A task file in the vault requiring processing. Attributes: content, priority (urgent/high/normal/low), domain (personal/business/cross-domain), status (pending/processing/awaiting_approval/approved/rejected/completed/failed), creation timestamp, completion timestamp, assigned processor.

- **Approval Request**: A structured file requesting human authorization for an external action. Attributes: action type, target system, parameters, risk level (low/medium/high), rationale, creation timestamp, decision timestamp, decision (approved/rejected). Lifecycle: created -> pending -> approved/rejected -> executed/cancelled -> archived.

- **External Action**: An operation that communicates outside the local vault via MCP. Attributes: MCP server target, operation type, parameters, approval reference, execution status, retry count, result. Lifecycle: planned -> approval_requested -> approved -> executing -> completed/failed -> archived.

- **Audit Report**: A periodic aggregation of business and operational data. Attributes: reporting period, data sources, financial summary, operational metrics, anomalies detected, generation timestamp. Lifecycle: scheduled -> collecting -> generated -> delivered.

- **Executive Briefing**: A concise summary derived from audit reports for decision-making. Attributes: reporting period, key metrics, highlights, concerns, recommended actions, generation timestamp. Lifecycle: audit_complete -> generated -> delivered.

- **Cross-Domain Workflow**: A task that spans personal and business contexts requiring coordinated processing. Attributes: source domain, target domains, sub-actions per domain, unified status, approval requirements. Lifecycle: detected -> classified -> sub-actions_created -> approved -> executed -> completed.

- **MCP Server Status**: The health and availability state of each registered MCP integration. Attributes: server name, connection status (healthy/degraded/unavailable), last successful contact, failure count, capabilities, retry queue depth.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% or more of action items placed in `/Needs_Action/` are detected, analyzed, and processed (either completed or routed to approval) without manual intervention within one processing cycle.
- **SC-002**: 100% of external actions are gated by approval (human or auto-approved when opted-in for low-risk actions) - zero external executions occur without an approval record under any circumstances.
- **SC-003**: Zero data loss occurs during integration failures - all failed operations are queued and recoverable after the integration is restored.
- **SC-004**: Weekly audit reports and executive briefings are generated on schedule with all available data aggregated, even when some sources are temporarily unavailable.
- **SC-005**: The system reduces manual operational effort by handling action items end-to-end, requiring human input only for approval decisions and credential management.
- **SC-006**: Full compliance with the Project Constitution - every system behavior respects approval boundaries, autonomy limits, local-first architecture, and audit requirements.
- **SC-007**: Domain isolation is maintained - failure in one domain (e.g., accounting integration down) does not prevent other domains from processing their action items.
- **SC-008**: The system recovers automatically from transient failures within 3 retry attempts, and escalates persistent failures to human attention within 5 minutes.

## Constraints

- Architecture must be file-system and MCP based, consistent with the local-first principle from the Project Constitution.
- Single-user system only - no multi-user access or collaboration features.
- No real-time push notifications - the system operates on polling intervals and file-system based communication.
- No multi-level approval chains - a single human approver is the only approval authority.
- No vendor-specific lock-in - MCP servers must use the standard JSON-RPC protocol and be replaceable.
- Must be backward compatible with the existing Bronze and Silver tier implementations.

## Assumptions

- External MCP servers for accounting (Odoo) and social media platforms are available and configured with valid endpoints.
- The user provides valid credentials via environment variables or OS secret manager before enabling integrations.
- A process manager (PM2 or equivalent) is configured to manage the background processor lifecycle including auto-restart.
- English is the primary language for all action items, reports, and system communications.
- The Obsidian vault filesystem has sufficient storage for logs, reports, and cached business data.
- The Gold-tier vault directory structure (including `/Business/`, `/Accounting/`, `/Briefings/`) extends the existing Silver-tier structure per the constitution.
- Action item priority is determined from frontmatter metadata when present, with keyword-based inference (e.g., "urgent," "deadline today," financial amounts) as fallback for unstructured items.

## Clarifications

### Session 2026-02-08

- Q: Should the retry queue for failed operations persist across system restarts? → A: Yes, persisted to vault Markdown files (e.g., `/Business/retry_queue.md`), consistent with local-first architecture.
- Q: How should action item priority be determined? → A: Frontmatter metadata (e.g., `priority: urgent`) takes precedence when present; keyword-based inference from content serves as fallback for unstructured items.
- Q: Should Gold tier support auto-approval for low-risk external actions? → A: Yes, but only when explicitly opted-in via configuration (default: off). User can gradually enable auto-approval for trusted low-risk patterns.
- Q: What is the scope of accounting operations for Gold tier? → A: Expenses and invoices only (record expenses, create/send invoices). Additional operations can be added incrementally in future tiers.
- Q: Which social/messaging platforms are in scope for Gold tier? → A: LinkedIn, Facebook, and WhatsApp.

## Explicitly Out of Scope

- Multi-user collaboration or team-based workflows
- Autonomous decision-making without human approval for external actions
- Advanced analytics dashboards or data visualization tools
- Mobile or web UI applications
- CRM, HR, or e-commerce integrations beyond accounting and social media
- Real-time streaming or webhook-based event processing
- Natural language conversation interface (the system operates through vault files, not chat)
