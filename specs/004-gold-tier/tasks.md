# Tasks: Gold Tier Autonomous System

**Input**: Design documents from `/specs/004-gold-tier/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as the plan specifies a test-first approach (Phase 3: Red) with safety tests as critical requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Gold-tier vault directories, configuration, and dependency setup

- [x] T001 Create Gold-tier vault directory structure: `AI_Employee_Vault/Business/`, `AI_Employee_Vault/Business/Accounting/`, `AI_Employee_Vault/Business/Social/`, `AI_Employee_Vault/Briefings/`
- [x] T002 Extend Gold-tier configuration variables in `src/config/settings.py` — add `GOLD_TIER_ENABLED`, `AUTO_APPROVE_LOW_RISK`, `AUDIT_SCHEDULE`, `BRIEFING_SCHEDULE`, `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY`, `FACEBOOK_BEARER_TOKEN`, `FACEBOOK_API_KEY`, `FACEBOOK_API_SECRET`, `WHATSAPP_MODE`, `WHATSAPP_API_TOKEN` to load_config() and validate_config()
- [x] T003 [P] Update `.env.example` with all Gold-tier environment variables per `specs/004-gold-tier/quickstart.md`
- [x] T004 [P] Update `requirements.txt` with Gold-tier dependencies: `requests>=4.14.0`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and utilities that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Extend `ActionFile` dataclass in `src/models/action_file.py` — add optional `priority` (urgent/high/normal/low, default: normal), `domain` (personal/business/cross-domain, default: None), and `processor` (str, default: None) fields while preserving existing interface
- [x] T006 [P] Extend `ApprovalRequest` dataclass in `src/models/approval_request.py` — add optional `approval_source` (human/auto, default: None) and `domain` (personal/business/cross-domain, default: None) fields; update `to_frontmatter()` and `to_dict()`
- [x] T007 [P] Extend `AuditLogEntry` dataclass in `src/models/audit_log_entry.py` — add optional `domain` field; update `to_dict()`
- [x] T008 [P] Create `RetryQueueEntry` dataclass in `src/models/retry_queue_entry.py` — fields: id, operation, mcp_server, parameters, approval_ref, retry_count, max_retries(3), last_attempt, next_retry_after, error, status(queued/retrying/failed_permanent); include `to_markdown()` and `from_markdown()` methods
- [x] T009 [P] Create `MCPServerStatus` model in `src/models/mcp_server_status.py` — fields: server_name, status(healthy/degraded/unavailable), last_success, failure_count, consecutive_failures, retry_queue_depth, capabilities list; include `to_dict()`, `from_dict()`, and status transition methods
- [x] T010 [P] Create `AuditReportModel` dataclass in `src/models/audit_report.py` — fields: report_type(business_audit/ceo_briefing), period, generated, data_sources, missing_sources, sections dict; include `to_markdown()` for rendering to file
- [x] T011 Create `PriorityClassifier` in `src/utils/priority_classifier.py` — implement `classify_priority(content, frontmatter) -> str` using frontmatter `priority:` field when present, falling back to keyword inference (urgent, deadline, asap, critical → urgent; important, financial → high; default → normal; low-priority, optional → low)
- [x] T012 Create `DomainClassifier` in `src/utils/domain_classifier.py` — implement `classify_domain(content, frontmatter) -> str` using frontmatter `domain:` field when present, falling back to keyword sets (business: invoice, expense, revenue, client, vendor, tax; personal: personal, home, family, calendar, reminder; cross-domain: both sets detected)
- [x] T013 Create `RetryManager` in `src/utils/retry_manager.py` — implement `add_to_queue(entry)`, `get_ready_entries() -> list`, `update_entry(id, status)`, `remove_entry(id)`, `load_queue()`, `save_queue()` operating on `/Business/retry_queue.md` as persistent Markdown storage with exponential backoff calculation (30s, 60s, 120s)
- [x] T014 Extend `MCPClient` in `src/utils/mcp_client.py` — add server routing map (`_get_server_script(server_name) -> str`) to dispatch to correct MCP server script (email→email_server.py, odoo→odoo_server.py, facebook→facebook_server.py, linkedin→linkedin_server.py, whatsapp→whatsapp_server.py); add `ping_server(server_name)` method
- [x] T015 Write foundational tests in `tests/test_gold_foundations.py` — test PriorityClassifier (frontmatter precedence, keyword fallback, defaults), DomainClassifier (frontmatter precedence, keyword sets, cross-domain detection), RetryQueueEntry (to_markdown/from_markdown roundtrip), MCPServerStatus (status transitions), extended ActionFile/ApprovalRequest/AuditLogEntry backward compatibility

**Checkpoint**: Foundation ready — all new models, classifiers, and utilities available for user story implementation

---

## Phase 3: User Story 1 — Autonomous Action Item Processing (Priority: P1) MVP

**Goal**: System automatically detects, prioritizes, classifies, and processes action items from `/Needs_Action/` without manual invocation

**Independent Test**: Place action item files in `/Needs_Action/` and verify they are automatically analyzed, prioritized, planned, and either completed (internal) or routed to approval (external) without manual commands

### Tests for User Story 1

- [x] T016 [P] [US1] Write Gold processor unit tests in `tests/test_gold_processor.py` — test `process_all()` cycle: detects new files in Needs_Action, classifies priority/domain, generates plan, routes external actions to approval, completes internal actions, moves to Done; test priority ordering; test enable/disable toggle; test backward compatibility with Silver behavior
- [x] T017 [P] [US1] Write auto-approval tests in `tests/test_auto_approval.py` — test low-risk auto-approve when enabled, high-risk always requires human, cross-domain always requires human, auto-approve disabled by default, approval_source correctly set to "auto" or "human"

### Implementation for User Story 1

- [x] T018 [US1] Create `GoldProcessor` in `src/processors/gold_processor.py` — extends `SilverProcessor`; override `process_all()` to add: (1) priority sorting of Needs_Action items via PriorityClassifier, (2) domain classification via DomainClassifier, (3) auto-approval for low-risk when enabled, (4) retry queue processing via RetryManager, (5) scheduled task checking; preserve all Silver/Bronze behavior when Gold features disabled
- [x] T019 [US1] Extend `ApprovalFormatter` in `src/utils/approval_formatter.py` — add auto-approval logic: if `AUTO_APPROVE_LOW_RISK=true` AND `risk_level=="low"` AND `auto_approve_eligible==true` AND domain is NOT cross-domain, skip file creation and return auto-approved status; set `approval_source="auto"` in audit log
- [x] T020 [US1] Create integration status tracker — implement `load_status()`, `update_status(server, success/failure)`, `get_health(server)`, `save_status()` operating on `AI_Employee_Vault/Business/integration_status.json` within `src/utils/mcp_client.py` or as new method on MCPClient
- [x] T021 [US1] Update `src/main.py` — initialize GoldProcessor instead of SilverProcessor when `GOLD_TIER_ENABLED=true`; preserve SilverProcessor fallback when Gold disabled; add retry queue processing to main loop
- [x] T022 [US1] Extend `DashboardUpdater` in `src/utils/dashboard_updater.py` — add Gold-tier sections: autonomous processing status (enabled/disabled), integration health per MCP server, retry queue depth, domain metrics (personal/business/cross-domain counts), last audit/briefing timestamps

**Checkpoint**: Autonomous processing works end-to-end — action items are auto-detected, prioritized, classified, and processed/routed without manual invocation

---

## Phase 4: User Story 2 — Business Accounting Automation (Priority: P2)

**Goal**: AI Employee manages accounting tasks (expenses, invoices) through Odoo via MCP with HITL approval

**Independent Test**: Create an accounting action item (e.g., "Record expense $500 for software"), verify approval request is generated, execute via Odoo MCP on approval, and confirm local record stored in `/Business/Accounting/`

### Tests for User Story 2

- [x] T023 [P] [US2] Write Odoo MCP contract tests in `tests/test_mcp_odoo.py` — test `create_expense` request/response, `create_invoice` request/response, `get_financial_summary` request/response, `ping` health check, authentication error handling (-32001), validation error handling (-32010), DRY_RUN mode

### Implementation for User Story 2

- [x] T024 [US2] Create Odoo MCP server in `mcp/odoo_server.py` — JSON-RPC 2.0 over stdio; implement `create_expense(description, amount, currency, category, date, notes)`, `create_invoice(partner_name, lines, due_date, notes)`, `get_financial_summary(period, date)`, `ping()`; authenticate via Odoo XML-RPC using env vars (`ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY`); respect `DRY_RUN`; error codes per contract
- [x] T025 [US2] Extend `MCPClient` in `src/utils/mcp_client.py` — add `create_expense(params)`, `create_invoice(params)`, `get_financial_summary(params)` methods that route to `mcp/odoo_server.py`
- [x] T026 [US2] Add accounting action handling in `GoldProcessor` (`src/processors/gold_processor.py`) — detect `financial_action` type from SensitiveActionDetector, route to Odoo MCP on approval, store transaction record as Markdown in `AI_Employee_Vault/Business/Accounting/expense_YYYY-MM-DD_NNN.md` or `invoice_YYYY-MM-DD_NNN.md`
- [x] T027 [US2] Extend `sensitive_action_detector.py` — add Odoo-specific action detection keywords (expense, invoice, accounting, bookkeeping, financial record) mapping to `action_type: "financial_action"` with `risk_level: "high"` and `mcp_server: "odoo"`

**Checkpoint**: Accounting workflow works end-to-end — expenses and invoices created via Odoo MCP after human approval, local records stored

---

## Phase 5: User Story 3 — Social Media Operations (Priority: P3)

**Goal**: AI Employee assists with social media posting (LinkedIn, Facebook, WhatsApp) and engagement tracking via MCP

**Independent Test**: Create social media action item, verify content is proposed for approval, execute post via platform MCP on approval, and confirm engagement data collected

### Tests for User Story 3

- [x] T028 [P] [US3] Write Facebook MCP contract tests in `tests/test_mcp_facebook.py` — test `post_post` request/response, `get_engagement_metrics` request/response, `ping`, rate limit error (-32020), DRY_RUN mode
- [x] T029 [P] [US3] Write LinkedIn MCP contract tests in `tests/test_mcp_linkedin.py` — test `create_post` request/response, `get_post_metrics` request/response, `ping`, auth error, DRY_RUN mode
- [x] T030 [P] [US3] Write WhatsApp MCP contract tests in `tests/test_mcp_whatsapp.py` — test `send_message` request/response, `get_message_status` request/response, `ping`, session expired error (-32031), DRY_RUN mode

### Implementation for User Story 3

- [x] T031 [P] [US3] Create Facebook MCP server in `mcp/facebook_server.py` — JSON-RPC 2.0 over stdio; implement `post_post(text, reply_to_id)`, `get_engagement_metrics(post_id)`, `ping()`; authenticate via OAuth 2.0 Bearer token using `FACEBOOK_BEARER_TOKEN`; use requests library; respect `DRY_RUN`; handle rate limits (-32020)
- [x] T032 [P] [US3] Create LinkedIn MCP server in `mcp/linkedin_server.py` — JSON-RPC 2.0 over stdio; implement `create_post(text, visibility)`, `get_post_metrics(post_id)`, `ping()`; authenticate via `LINKEDIN_ACCESS_TOKEN`; use requests library; respect `DRY_RUN`
- [x] T033 [P] [US3] Create WhatsApp MCP server in `mcp/whatsapp_server.py` — JSON-RPC 2.0 over stdio; implement `send_message(to, message, media_url)`, `get_message_status(message_id)`, `ping()`; support both API mode (`WHATSAPP_API_TOKEN`) and Playwright mode; respect `DRY_RUN`
- [x] T034 [US3] Extend `MCPClient` in `src/utils/mcp_client.py` — add `post_post(params)`, `get_post_metrics(params)`, `create_linkedin_post(params)`, `get_linkedin_metrics(params)`, `send_whatsapp(params)` methods routing to respective MCP servers
- [x] T035 [US3] Add social media action handling in `GoldProcessor` (`src/processors/gold_processor.py`) — detect `linkedin_post`, `facebook_post`, `whatsapp_message` action types, route to appropriate MCP on approval, store activity records in `AI_Employee_Vault/Business/Social/`
- [x] T036 [US3] Extend `sensitive_action_detector.py` — add Facebook-specific keywords (post, facebook, post on x) mapping to `action_type: "facebook_post"` with `mcp_server: "facebook"`; add WhatsApp-specific keywords (whatsapp, send message to) mapping to `action_type: "whatsapp_message"` with `mcp_server: "whatsapp"`

**Checkpoint**: Social media workflow works — content proposed, approved, posted via MCP, engagement data collected for LinkedIn/Facebook/WhatsApp

---

## Phase 6: User Story 4 — Weekly Business Audit & Executive Briefing (Priority: P4)

**Goal**: Automatic weekly audit reports and executive briefings generated on schedule

**Independent Test**: Trigger scheduled audit cycle, verify audit report and executive briefing generated in `/Briefings/` with aggregated data from all available sources

### Tests for User Story 4

- [x] T037 [P] [US4] Write scheduler tests in `tests/test_scheduler.py` — test schedule checking logic (is_due returns true when past scheduled time and not run since), state persistence to `scheduler_state.json`, schedule parsing (day:time format), next_run calculation
- [x] T038 [P] [US4] Write report generator tests in `tests/test_report_generator.py` — test audit report generation from log files, test executive briefing generation from audit data, test missing data source handling (marked not failed), test zero-activity report generation, test frontmatter correctness

### Implementation for User Story 4

- [x] T039 [US4] Create `Scheduler` in `src/utils/scheduler.py` — implement `is_due(task_name) -> bool`, `mark_completed(task_name)`, `load_state()`, `save_state()` operating on `AI_Employee_Vault/Business/scheduler_state.json`; support day-of-week + time format (e.g., "monday:09:00"); calculate next_run based on schedule
- [x] T040 [US4] Create `ReportGenerator` in `src/utils/report_generator.py` — implement `generate_audit_report(vault_path, period) -> Path` aggregating data from `/Logs/` (action counts, success rates), `/Business/Accounting/` (financial summary), `/Business/Social/` (engagement metrics), vault directory counts; write to `/Briefings/audit_YYYY-MM-DD.md` with frontmatter per data-model.md; mark missing sources with `[DATA UNAVAILABLE: source_name]`
- [x] T041 [US4] Extend `ReportGenerator` — implement `generate_executive_briefing(vault_path, audit_path) -> Path` producing concise summary from audit data: key metrics (3-5 numbers), highlights, concerns, recommended actions; write to `/Briefings/ceo_briefing_YYYY-MM-DD.md`
- [x] T042 [US4] Integrate scheduling into `GoldProcessor` (`src/processors/gold_processor.py`) — on each processing cycle, call `Scheduler.is_due("weekly_audit")` and `Scheduler.is_due("weekly_briefing")`; if due, call ReportGenerator methods and mark completed

**Checkpoint**: Weekly audits and briefings generated automatically on schedule, handle missing data gracefully

---

## Phase 7: User Story 5 — Cross-Domain Workflows (Priority: P5)

**Goal**: Action items spanning personal and business contexts are classified, routed correctly, and require explicit approval

**Independent Test**: Create cross-domain action items, verify domain classification, confirm cross-domain always requires approval, verify domain metrics in dashboard, verify independent domain operation when one degrades

### Tests for User Story 5

- [x] T043 [P] [US5] Write domain classification integration tests in `tests/test_domain_classifier.py` — test personal-only classification, business-only classification, cross-domain detection (both keyword sets), frontmatter override, cross-domain always requires approval regardless of auto-approve setting

### Implementation for User Story 5

- [x] T044 [US5] Add cross-domain workflow handling in `GoldProcessor` (`src/processors/gold_processor.py`) — when domain is "cross-domain": create sub-actions per domain in `/Plans/`, force approval regardless of risk level and auto-approve setting (FR-019), track unified status across sub-actions
- [x] T045 [US5] Implement domain isolation in `GoldProcessor` — wrap each domain's processing in independent try/except blocks so failure in business integrations does not prevent personal domain processing and vice versa; log domain-specific errors independently
- [x] T046 [US5] Extend `DashboardUpdater` in `src/utils/dashboard_updater.py` — add per-domain metrics section showing action counts, success rates, and health status for personal and business domains separately plus combined totals

**Checkpoint**: Cross-domain workflows classified and routed correctly, domains operate independently under degradation

---

## Phase 8: User Story 6 — Reliability & Failure Recovery (Priority: P6)

**Goal**: System recovers from errors automatically with retry, restart, and human escalation

**Independent Test**: Simulate MCP failures, process crashes, and persistent errors; verify retry with backoff, automatic restart, and human notification for persistent failures

### Tests for User Story 6

- [x] T047 [P] [US6] Write retry manager tests in `tests/test_retry_manager.py` — test exponential backoff calculation (30s, 60s, 120s), queue persistence across load/save cycles, entry removal on success, failed_permanent after 3 retries, notification creation on permanent failure
- [x] T048 [P] [US6] Write safety tests in `tests/test_gold_safety.py` — test no external action without approval record (approval gate), DRY_RUN blocks all MCP execution, PII sanitization in Gold-tier logs (domain field, retry entries), domain isolation (fail one integration, others continue)

### Implementation for User Story 6

- [x] T049 [US6] Implement retry-on-failure in `GoldProcessor` (`src/processors/gold_processor.py`) — wrap MCP execution in try/except; on failure: log error, increment failure count, add to retry queue via RetryManager if retry_count < 3; on permanent failure: create notification action file in `/Needs_Action/` alerting user
- [x] T050 [US6] Implement retry queue processing in `GoldProcessor` — on each cycle: call `RetryManager.get_ready_entries()`, attempt execution for each ready entry, update status on success/failure, remove from queue on success
- [x] T051 [US6] Update `ecosystem.config.js` — add Gold-tier process configuration with `autorestart: true`, `max_restarts: 10`, `restart_delay: 5000`, separate log files for gold processor
- [x] T052 [US6] Implement integration health tracking in `GoldProcessor` — after each MCP call (success or failure), update `MCPServerStatus` via `src/utils/mcp_client.py` integration status tracker (T020); degrade integration after 3 consecutive failures; restore to healthy on success

**Checkpoint**: System recovers from transient failures within 3 retries, escalates persistent failures to human, restarts after crashes, domains isolated

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and validation across all user stories

- [x] T053 [P] Create `AI_Employee_Vault/Business_Goals.md` with placeholder Gold-tier business goals template per constitution
- [x] T054 [P] Update `AI_Employee_Vault/Company_Handbook.md` — add Gold-tier capabilities section documenting: autonomous processing, accounting integration, social media operations, weekly audits, cross-domain workflows, failure recovery
- [x] T055 Run full test suite (`python -m pytest tests/ -v`) and verify all existing Silver-tier tests still pass alongside new Gold-tier tests
- [x] T056 Validate system end-to-end in DRY_RUN mode — place test action items in `/Needs_Action/`, verify full pipeline: detection → classification → plan → approval → (mock) execution → Done
- [x] T057 Run `specs/004-gold-tier/quickstart.md` validation — verify all setup steps, directory creation, configuration, and basic workflow documented correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — MVP target
- **US2 (Phase 4)**: Depends on US1 (GoldProcessor must exist)
- **US3 (Phase 5)**: Depends on US1 (GoldProcessor must exist); can run in parallel with US2
- **US4 (Phase 6)**: Depends on US1 (GoldProcessor for scheduling integration)
- **US5 (Phase 7)**: Depends on US1 (GoldProcessor domain classification)
- **US6 (Phase 8)**: Depends on US1 (GoldProcessor retry integration); benefits from US2/US3 for real MCP failure scenarios
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — No dependencies on other stories — **MVP**
- **US2 (P2)**: Depends on US1 (GoldProcessor exists) — adds Odoo MCP integration
- **US3 (P3)**: Depends on US1 (GoldProcessor exists) — can run in parallel with US2
- **US4 (P4)**: Depends on US1 (scheduling integration) — can run in parallel with US2/US3
- **US5 (P5)**: Depends on US1 (domain classification) — can run in parallel with US2/US3/US4
- **US6 (P6)**: Depends on US1 (retry integration) — best after US2/US3 for realistic failure testing

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services/utilities
- Utilities before processor integration
- MCP servers before MCPClient extension
- Core implementation before dashboard/polish

### Parallel Opportunities

- T003, T004 (Setup) can run in parallel
- T005, T006, T007, T008, T009, T010 (Foundational models) can all run in parallel
- T011, T012 (classifiers) can run in parallel after models
- T016, T017 (US1 tests) can run in parallel
- T023 (US2 tests) can run alongside US3/US4/US5 tests
- T028, T029, T030 (US3 platform tests) can all run in parallel
- T031, T032, T033 (US3 MCP servers) can all run in parallel
- T037, T038 (US4 tests) can run in parallel
- T043 (US5 tests), T047, T048 (US6 tests) can run in parallel
- US2, US3, US4, US5 can run in parallel after US1 is complete

---

## Parallel Example: User Story 3

```bash
# Launch all MCP contract tests together:
Task: "Facebook MCP contract tests in tests/test_mcp_facebook.py"
Task: "LinkedIn MCP contract tests in tests/test_mcp_linkedin.py"
Task: "WhatsApp MCP contract tests in tests/test_mcp_whatsapp.py"

# Launch all MCP server implementations together:
Task: "Facebook MCP server in mcp/facebook_server.py"
Task: "LinkedIn MCP server in mcp/linkedin_server.py"
Task: "WhatsApp MCP server in mcp/whatsapp_server.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T015)
3. Complete Phase 3: User Story 1 (T016-T022)
4. **STOP and VALIDATE**: Test autonomous processing independently
5. System should auto-detect, prioritize, classify, and process action items

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → **MVP: Autonomous processing works**
3. Add US2 → Test independently → Accounting automation works
4. Add US3 → Test independently → Social media operations work
5. Add US4 → Test independently → Weekly audits generated
6. Add US5 → Test independently → Cross-domain routing works
7. Add US6 → Test independently → Failure recovery reliable
8. Polish → Full system validated

### Parallel Strategy

After US1 (MVP) is complete:
- Stream A: US2 (Accounting) + US4 (Audits) — both are business intelligence
- Stream B: US3 (Social Media) + US5 (Cross-Domain) — both extend processing
- Stream C: US6 (Reliability) — can start alongside any stream

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests are included as the plan mandates test-first (Phase 3: Red)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks trace back to FR-001 through FR-034 in the spec
