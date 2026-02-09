# Implementation Plan: Gold Tier Autonomous System

**Branch**: `004-gold-tier` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-gold-tier/spec.md`

## Summary

Build a Gold-tier Personal AI Employee that runs continuously without manual invocation, autonomously processes action items from the vault, coordinates personal and business workflows, executes human-approved external actions via MCP servers (Odoo accounting, LinkedIn, Facebook, WhatsApp), generates weekly audit reports and executive briefings, and handles failures with persistent retry queues — all while maintaining full backward compatibility with Bronze and Silver tiers and strict compliance with the Project Constitution.

## Technical Context

**Language/Version**: Python 3.13+ (as mandated by constitution; 3.14 available on this machine)
**Primary Dependencies**: watchdog (filesystem), python-dotenv (config), requests (HTTP), playwright (WhatsApp), xmlrpc.client (Odoo, stdlib), requests (Facebook API v2)
**Storage**: Local Obsidian vault (Markdown files + JSON) — no database
**Testing**: pytest (from project root: `python -m pytest tests/ -v`)
**Target Platform**: Windows (primary development), cross-platform compatible
**Project Type**: Single project — Python CLI application with background processing
**Performance Goals**: Action items detected and processed within 30-second polling interval; MCP operations complete within 30s timeout
**Constraints**: Local-first architecture, single-user, no real-time push, file-based state, MCP-only external actions
**Scale/Scope**: Single user, ~10-50 action items/day, 5 MCP integrations (email, odoo, facebook, linkedin, whatsapp)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
| --------- | ------ | -------- |
| I. Local-First Architecture | PASS | All state in Obsidian vault as Markdown/JSON. External APIs read/write only via MCP with HITL. Gold vault structure matches constitution Section I. |
| II. External Actions & MCP Integration | PASS | All external actions route through MCP servers (FR-007). HITL approval required (FR-006). Email MCP exists; Odoo, Facebook, LinkedIn, WhatsApp MCP servers defined in contracts. |
| III. Agent Skills Implementation | PASS | Gold processor extends SilverProcessor as composable, testable, background-invocable skill. New capabilities (audit, classification, scheduling) implemented as discrete methods. |
| IV. Security and Privacy | PASS | Credentials in env vars only (FR-031). PII sanitization via existing log_sanitizer (FR-032). DRY_RUN support (FR-033). Audit logs in `/Logs/` with 90-day retention. |
| V. Multi-Watcher Architecture | PASS | Extends existing BaseWatcher pattern. LinkedIn, WhatsApp, FileSystem watchers preserved. No new watchers needed — Gold adds processing intelligence, not perception. |
| VI. HITL Approval Workflow | PASS | File-based approval flow preserved. Auto-approval opt-in for low-risk only (FR-034, default: disabled). Cross-domain always requires approval (FR-019). |
| VII. Autonomous Operation & Ralph Wiggum Loop | PASS | Gold processor runs continuously via PM2. Auto-detects `/Needs_Action/` files. Multi-step cross-domain coordination. Configuration toggle (FR-004). |
| VIII. Business Intelligence & Reporting | PASS | Weekly audit (FR-015) and CEO briefing (FR-016) generated on schedule to `/Briefings/`. Templates match constitution Section VIII. |
| IX. Paper Workflow & Git Integration | PASS | Plan artifacts in `specs/004-gold-tier/`. Implementation commits tracked per workflow. |
| X. Security & Ethics | PASS | HITL for all sensitive tasks. Audit logs for review. Dry-run for development. Transparency via Dashboard.md. |

**Gate Result**: PASS — No violations. Proceeding to design.

## Project Structure

### Documentation (this feature)

```text
specs/004-gold-tier/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions and lifecycles
├── quickstart.md        # Setup and usage guide
├── contracts/
│   └── mcp-contracts.md # MCP server interface contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── processors/
│   ├── vault_processor.py       # Bronze tier (unchanged)
│   ├── silver_processor.py      # Silver tier (unchanged)
│   ├── gold_processor.py        # NEW: Gold tier autonomous processor
│   └── action_item.py           # Extended with priority/domain
├── models/
│   ├── action_file.py           # Extended with priority/domain fields
│   ├── approval_request.py      # Extended with approval_source/domain
│   ├── audit_log_entry.py       # Extended with domain field
│   ├── plan_file.py             # Unchanged
│   ├── watcher_input.py         # Unchanged
│   ├── retry_queue_entry.py     # NEW: Retry queue data model
│   ├── audit_report.py          # NEW: Audit report data model
│   └── mcp_server_status.py     # NEW: Integration status model
├── watchers/
│   ├── base_watcher.py          # Unchanged
│   ├── file_system_watcher.py   # Unchanged
│   ├── linkedin_watcher.py      # Unchanged
│   └── whatsapp_watcher.py      # Unchanged
├── utils/
│   ├── config_loader.py         # Unchanged
│   ├── sensitive_action_detector.py  # Extended: domain classification
│   ├── approval_formatter.py    # Extended: auto-approve support
│   ├── audit_logger.py          # Unchanged
│   ├── log_sanitizer.py         # Unchanged
│   ├── mcp_client.py            # Extended: new server routing
│   ├── dashboard_updater.py     # Extended: Gold tier metrics
│   ├── logger.py                # Unchanged
│   ├── log_manager.py           # Unchanged
│   ├── action_file_generator.py # Unchanged
│   ├── priority_classifier.py   # NEW: Priority inference
│   ├── domain_classifier.py     # NEW: Domain classification
│   ├── retry_manager.py         # NEW: Retry queue management
│   ├── scheduler.py             # NEW: Scheduled task execution
│   └── report_generator.py      # NEW: Audit/briefing generation
├── config/
│   └── settings.py              # Extended: Gold tier config vars
├── social/
│   ├── linkedin_post_generator.py  # Unchanged
│   └── ...                         # Unchanged
├── workflows/                      # Unchanged
└── main.py                         # Extended: Gold processor init

mcp/
├── email_server.py              # Unchanged
├── odoo_server.py               # NEW: Odoo accounting MCP
├── facebook_server.py            # NEW: Facebook MCP
├── linkedin_server.py           # NEW: LinkedIn posting MCP
└── whatsapp_server.py           # NEW: WhatsApp messaging MCP

tests/
├── test_silver_tier.py          # Unchanged
├── test_gold_processor.py       # NEW: Gold processor tests
├── test_priority_classifier.py  # NEW: Priority classification tests
├── test_domain_classifier.py    # NEW: Domain classification tests
├── test_retry_manager.py        # NEW: Retry queue tests
├── test_scheduler.py            # NEW: Scheduler tests
├── test_report_generator.py     # NEW: Audit/briefing tests
├── test_mcp_odoo.py             # NEW: Odoo MCP contract tests
├── test_mcp_facebook.py          # NEW: Facebook MCP contract tests
├── test_mcp_linkedin.py         # NEW: LinkedIn MCP contract tests
├── test_mcp_whatsapp.py         # NEW: WhatsApp MCP contract tests
└── test_auto_approval.py        # NEW: Auto-approval tests
```

**Structure Decision**: Single project layout (Option 1), extending the existing `src/` structure. No frontend/backend split needed — this is a CLI-based background processing system. New files are additive; no existing files are deleted or renamed.

## Phased Execution Plan

### Phase 0: Research Foundation (Complete)

**Purpose**: Ensure all external dependencies and architectural patterns are well-understood.

**Outputs**:
- [research.md](./research.md) — 8 research streams covering MCP patterns, autonomous processing, HITL enforcement, retry strategies, scheduling, domain classification, reporting, and OAuth lifecycle
- All NEEDS CLARIFICATION items resolved via spec clarification session

**Exit Gate**: PASS
- No unknown external dependencies
- All write operations confirmed HITL-gated
- MCP contracts defined for all 5 integrations

---

### Phase 1: System Design (Complete)

**Purpose**: Translate requirements into concrete system structures.

**Outputs**:
- [data-model.md](./data-model.md) — 9 entities with lifecycle states, relationships, and storage formats
- [contracts/mcp-contracts.md](./contracts/mcp-contracts.md) — JSON-RPC contracts for 5 MCP servers
- [quickstart.md](./quickstart.md) — Setup, configuration, and usage guide

**Exit Gate**: PASS
- Every external action mapped to approval workflow (via MCP contracts)
- Backward compatibility verified (all existing models extended additively, not modified destructively)

---

### Phase 2: Task Decomposition

**Purpose**: Break design into dependency-ordered, testable tasks.

**Output**: `tasks.md` (generated via `/sp.tasks`)

**Exit Gate**:
- No task bypasses HITL
- All tasks traceable to spec requirements (FR-001 through FR-034)

---

### Phase 3: Test-First Implementation (Red)

**Purpose**: Write failing tests before implementation.

**Key Test Categories**:
1. **Unit Tests**: Priority classifier, domain classifier, retry manager, scheduler, report generator
2. **Integration Tests**: MCP server contracts (mock), approval gating with auto-approve, Gold processor cycle
3. **End-to-End Tests**: Watcher → Action → Approval → Execution → Done, cross-domain workflows, weekly audit generation
4. **Safety Tests**: No external action without approval record, DRY_RUN respected, logs contain no secrets, domain isolation (failure in one doesn't cascade)

**Exit Gate**:
- Tests exist for all critical paths
- Unsafe execution paths blocked by default

---

### Phase 4: Implementation (Green)

**Purpose**: Build functionality to satisfy tests.

**Implementation Order** (dependency-driven):
1. Data models (retry_queue_entry, audit_report, mcp_server_status)
2. Utility modules (priority_classifier, domain_classifier, retry_manager, scheduler, report_generator)
3. Gold processor (extends SilverProcessor)
4. MCP servers (odoo, facebook, linkedin, whatsapp)
5. MCPClient extension (new server routing)
6. Config extension (Gold tier settings)
7. Dashboard extension (Gold tier metrics)
8. Main entry point update

**Exit Gate**:
- All tests passing
- System operates end-to-end in DRY_RUN mode

---

### Phase 5: Refinement and Hardening

**Purpose**: Improve reliability, documentation, and maintainability.

**Key Activities**:
- Validate retry/recovery behavior under simulated failures
- Verify domain isolation (one integration down, others continue)
- Verify audit report generation with missing data sources
- Update ecosystem.config.js for Gold tier processes
- Update Company_Handbook.md with Gold tier capabilities

**Exit Gate**:
- No constitution violations
- System stable under failure simulation
- All success criteria (SC-001 through SC-008) verifiable

## Key Architectural Decisions

### ADR-001: Autonomous File-Based Processing

**Context**: Gold tier requires continuous autonomous processing without manual invocation.

**Decision**: Extend the existing polling-based processor (SilverProcessor) with a GoldProcessor that adds priority sorting, domain classification, scheduled tasks, and retry management within the same processing loop.

**Options Considered**:
1. Manual agent invocation (current Silver behavior) — rejected: doesn't meet Gold autonomy requirements
2. Event queue with message broker (Redis/RabbitMQ) — rejected: violates local-first, adds infrastructure
3. **Continuous file watcher with intelligent processing (selected)** — preserves local-first, minimal infrastructure, transparent state

**Tradeoff**: 30-second polling latency vs. architectural simplicity. Acceptable for the use case.

### ADR-002: MCP-Only External Actions

**Context**: External actions need to be auditable, approval-gated, and centrally controlled.

**Decision**: All external actions execute exclusively through registered MCP servers via JSON-RPC 2.0 over stdio.

**Options Considered**:
1. Direct API calls from processor — rejected: no centralized audit, hard to gate
2. Mixed direct + MCP calls — rejected: inconsistent security model
3. **MCP-only execution (selected)** — enforces auditability, centralizes security, simplifies approval

**Tradeoff**: Additional abstraction layer adds latency (~100ms subprocess spawn). Acceptable for reliability and security.

### ADR-003: File-Based HITL Approval

**Context**: Human approval is required for all external actions.

**Decision**: Continue the Silver-tier pattern of file movement between directories (Pending_Approval → Approved/Rejected) with Gold-tier addition of opt-in auto-approval for low-risk actions.

**Options Considered**:
1. UI-based approval system — rejected: out of scope, adds web dependency
2. Chat-based approvals — rejected: requires messaging integration for control, circular dependency
3. **Filesystem state transitions (selected)** — tool-agnostic, version controllable, human-readable

**Tradeoff**: Manual file movement required by the user. Mitigated by Obsidian's file explorer.

### ADR-004: Scheduled Intelligence Reports

**Context**: Weekly audit reports and executive briefings need to be generated automatically.

**Decision**: Embed schedule checking within the processor loop. Each cycle compares current time against stored last-run timestamps.

**Options Considered**:
1. On-demand generation — rejected: requires manual invocation, defeats autonomy
2. Event-triggered generation — rejected: no reliable event source for weekly cadence
3. **Fixed schedule with processor-embedded checks (selected)** — predictable, no extra dependencies

**Tradeoff**: Less reactive to real-time events. Acceptable since reports are weekly summaries.

### ADR-005: Persistent Retry Queue

**Context**: Failed MCP operations must not be lost on system restart (SC-003: zero data loss).

**Decision**: Store retry queue as structured Markdown in `/Business/retry_queue.md`, consistent with local-first vault architecture.

**Options Considered**:
1. In-memory queue — rejected: lost on restart, violates SC-003
2. SQLite database — rejected: adds non-Markdown storage, breaks local-first consistency
3. JSON file — viable but less human-readable
4. **Markdown with structured sections (selected)** — human-readable, vault-consistent, version-controllable

**Tradeoff**: Markdown parsing overhead vs. consistency with vault architecture. Parsing is trivial for expected queue sizes.

## Testing and Validation Strategy

### Validation Levels

| Level | Scope | Tools | Key Scenarios |
| ----- | ----- | ----- | ------------- |
| Unit | Individual classifiers, models, utilities | pytest, tmp_path | Priority inference, domain classification, retry backoff calculation, schedule checking |
| Integration | MCP contracts, processor cycles, approval flow | pytest, mock subprocess | MCP server request/response, approval gating with auto-approve, Gold processor full cycle |
| End-to-End | Complete workflows | pytest, tmp_path vault | Watcher → Action → Approval → MCP → Done, cross-domain routing, audit generation |
| Safety | Security invariants | pytest | No unapproved external execution, DRY_RUN blocks all MCP calls, logs contain no PII, domain isolation |

### Safety Tests (Critical)

1. **Approval Gate**: Create external action → verify approval request created → verify no MCP call occurs without approval file in `/Approved/`
2. **Auto-Approve Boundary**: Enable auto-approve → verify only low-risk actions auto-approved → verify high-risk still requires human
3. **Cross-Domain Gate**: Create cross-domain action → verify always requires manual approval regardless of auto-approve setting
4. **DRY_RUN**: Enable dry run → verify all MCP calls logged but not executed
5. **PII Sanitization**: Create action with email/phone → verify logs contain only redacted values
6. **Domain Isolation**: Fail one integration → verify other domains continue processing

## Quality Gates

Before moving to `/sp.tasks`, the following must be true:

- [x] All constitution principles explicitly addressed (see Constitution Check table)
- [x] All external actions approval-gated (MCP contracts + FR-006/FR-007)
- [x] All data persisted locally (vault Markdown/JSON — no external storage)
- [x] All decisions documented with tradeoffs (ADR-001 through ADR-005)
- [x] Testing strategy covers all acceptance criteria (4 validation levels + 6 safety tests)
- [x] Backward compatibility verified (additive model extensions, no destructive changes)
- [x] Research complete, no unresolved NEEDS CLARIFICATION items

**Gate Result**: ALL PASS — Ready for `/sp.tasks`.

## Complexity Tracking

No constitution violations to justify. All architectural decisions align with established principles.
