# Research: Gold Tier Autonomous System

**Feature Branch**: `004-gold-tier`
**Created**: 2026-02-08
**Status**: Complete

## Research Stream 1: MCP Protocol & Server Patterns

### Decision: JSON-RPC 2.0 over stdio (continue existing pattern)

**Rationale**: The Silver tier already implements MCP via JSON-RPC 2.0 over stdio (see `mcp/email_server.py` and `src/utils/mcp_client.py`). This pattern is proven, simple, and allows each MCP server to be an independent process spawned on demand.

**Alternatives Considered**:
- FastMCP (Python SDK): More ergonomic but adds a dependency and changes the established pattern. Rejected for consistency.
- HTTP-based JSON-RPC: Would require a persistent server process per integration. Rejected for complexity.
- gRPC: Over-engineered for single-user, local-only system. Rejected.

**Key Findings**:
- Existing MCPClient spawns subprocess with `subprocess.run()` and 30s timeout
- Each MCP server reads stdin, processes one request, writes stdout
- Error codes follow JSON-RPC 2.0 spec (-32000 to -32099 for server errors)
- Gold tier needs new MCP servers for: Odoo accounting, Facebook, WhatsApp messaging (LinkedIn posting can extend existing watcher)

### New MCP Server Contracts Required

1. **Odoo Accounting MCP** (`mcp/odoo_server.py`)
   - Methods: `create_expense`, `create_invoice`, `get_financial_summary`
   - Auth: Odoo XML-RPC with API key from env vars
   - Self-hosted Odoo assumption per constitution

2. **Facebook MCP** (`mcp/facebook_server.py`)
   - Methods: `post_post`, `get_engagement_metrics`
   - Auth: OAuth 2.0 Bearer token from env vars
   - Rate limits: Facebook API v2 limits (300 posts/3hrs for free tier)

3. **WhatsApp MCP** (`mcp/whatsapp_server.py`)
   - Methods: `send_message`, `get_message_status`
   - Auth: WhatsApp Business API or Playwright-based (existing pattern)
   - Extends existing WhatsApp watcher session management

4. **LinkedIn MCP** (`mcp/linkedin_server.py`)
   - Methods: `create_post`, `get_post_metrics`
   - Auth: OAuth 2.0 from env vars (existing LINKEDIN_ACCESS_TOKEN)
   - Extends existing LinkedInWatcher pattern

## Research Stream 2: Autonomous Processing Patterns

### Decision: Polling-based autonomous processor extending SilverProcessor

**Rationale**: The existing `SilverProcessor.process_all()` already implements a scan-process-execute cycle. The Gold processor extends this with:
- Priority queue sorting before processing
- Domain classification per action item
- Scheduled task support (audit generation)
- Retry queue management

**Alternatives Considered**:
- Event-driven with watchdog Observer: Already used in FileSystemWatcher but unreliable for complex workflows. Polling is more predictable.
- asyncio event loop: Would require rewriting the entire processing pipeline. Rejected for backward compatibility.
- Celery/Redis task queue: Over-engineered for single-user file-based system. Rejected.

**Key Findings**:
- Current processing interval: configurable via `PROCESSING_INTERVAL` (default 30s in ecosystem.config.js)
- PM2 handles process lifecycle (autorestart, max restarts: 10, restart delay: 5s)
- Gold processor inherits from SilverProcessor, adding autonomous scheduling and priority processing
- Configuration hot-reload: check config on each cycle to support enable/disable without restart (FR-004)

## Research Stream 3: HITL Enforcement via Filesystem

### Decision: Continue file-based approval with auto-approval extension

**Rationale**: Silver tier's file-movement approval pattern is proven and aligned with the constitution. Gold tier adds:
- Auto-approval for low-risk actions when opted-in (FR-034)
- Approval source tracking ("human" vs "auto") in audit logs

**Key Findings**:
- Approval file format already supports `auto_approve_eligible` in frontmatter
- Risk assessment exists in `sensitive_action_detector.py` with low/medium/high levels
- Auto-approval flow: if `AUTO_APPROVE_LOW_RISK=true` in config AND `risk_level == "low"` AND `auto_approve_eligible == true`, skip Pending_Approval and log with `approval_status: "auto_approved"`
- Cross-domain actions always require manual approval regardless of auto-approve setting (FR-019)

## Research Stream 4: Retry & Queue Persistence

### Decision: Markdown-based retry queue in vault

**Rationale**: Consistent with local-first architecture. Failed operations are stored as structured Markdown with frontmatter tracking retry state.

**Key Findings**:
- Retry queue location: `/Business/retry_queue.md` (single file, append-based)
- Each entry: frontmatter block with operation details, retry count, last attempt timestamp, error message
- On each processing cycle, check retry queue for items past their backoff interval
- Exponential backoff: 30s, 60s, 120s (3 attempts)
- After 3 failures: mark as "failed_permanent", create notification in Needs_Action
- On integration recovery: retry queued items in FIFO order

## Research Stream 5: Scheduled Task Execution

### Decision: Cron-style scheduling within the processor loop

**Rationale**: Rather than adding a separate scheduling dependency (APScheduler, cron), embed schedule checks within the existing processing loop. Each cycle checks if any scheduled tasks are due.

**Key Findings**:
- Audit schedule: configurable, default Monday 9AM (FR-015)
- Check mechanism: compare current time against last run timestamp stored in config/state file
- State file: `/Business/scheduler_state.json` with `{task_name: last_run_iso}`
- Scheduled tasks: `weekly_audit`, `weekly_briefing`
- Schedule format: day-of-week + time (e.g., `AUDIT_SCHEDULE=monday:09:00`)

## Research Stream 6: Domain Classification

### Decision: Keyword-based classification with frontmatter override

**Rationale**: Matches the established priority inference pattern (frontmatter metadata > keyword fallback).

**Key Findings**:
- Domain field in frontmatter: `domain: personal|business|cross-domain`
- Keyword sets for inference:
  - Business: invoice, expense, revenue, profit, accounting, financial, client, customer, vendor, tax, payroll
  - Personal: personal, home, family, health, calendar, reminder, appointment
  - Cross-domain: detected when both business AND personal keywords present
- Classification stored in action item metadata during processing
- Cross-domain always requires approval (FR-019)

## Research Stream 7: Audit Report & Briefing Generation

### Decision: Template-based Markdown generation from aggregated data

**Rationale**: The constitution already defines audit and CEO briefing templates (Section VIII). Generate reports by scanning vault directories and log files, then filling templates.

**Key Findings**:
- Data sources for audit: `/Logs/` (JSON entries), `/Business/Accounting/` (transaction records), `/Done/` (completed actions), `/Business/Social/` (engagement data)
- Aggregation: count actions by type, sum financial data, calculate success/failure rates
- Missing data handling: mark sections with `[DATA UNAVAILABLE: source_name]` rather than failing
- Template locations per constitution:
  - Audit: `/Briefings/audit_YYYY-MM-DD.md`
  - Briefing: `/Briefings/ceo_briefing_YYYY-MM-DD.md`
- Report frontmatter: `type: business_audit|ceo_briefing`, `period: YYYY-WW`, `generated: ISO_TIMESTAMP`

## Research Stream 8: OAuth & Credential Lifecycle

### Decision: Environment variables with graceful degradation on expiry

**Rationale**: Constitution mandates credentials in env vars or OS secret manager. Tokens may expire; system must detect and degrade gracefully.

**Key Findings**:
- Odoo: API key (long-lived), no OAuth flow needed. Config: `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY`
- Facebook: OAuth 2.0 Bearer token. Config: `FACEBOOK_BEARER_TOKEN`, `FACEBOOK_API_KEY`, `FACEBOOK_API_SECRET`
- LinkedIn: OAuth 2.0 access token (existing). Config: `LINKEDIN_ACCESS_TOKEN`
- WhatsApp: Playwright session (existing) or Business API token. Config: `WHATSAPP_API_TOKEN`
- On auth failure (HTTP 401/403): mark integration as degraded, create notification, skip retries for auth errors (retries only for transient failures like timeouts/5xx)
