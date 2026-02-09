# Implementation Plan: Silver Tier Personal AI Employee

## Summary
This plan outlines the implementation of the Silver Tier Personal AI Employee system, extending the Bronze Tier foundation with multi-watcher support, MCP server integration, Human-in-the-Loop (HITL) approval workflows, social media automation, process management, and audit logging.

## Technical Context
The Silver Tier system builds upon the Bronze Tier architecture by adding:

1. **Multi-watcher support**: Adding WhatsApp (Playwright-based) and LinkedIn (API or browser-based) watchers alongside existing Gmail/filesystem watcher
2. **MCP server integration**: Implementing JSON-RPC-based MCP server for secure external action execution
3. **HITL approval workflow**: Creating approval request files in /Pending_Approval for sensitive actions
4. **Social media automation**: Generating and posting LinkedIn content with mandatory approval
5. **Process management**: Using PM2 for 24/7 uptime of watchers and processors
6. **Audit logging**: Implementing JSON logging for all external actions
7. **Enhanced dashboard**: Updating Dashboard.md with pending approvals and system status

The system maintains full backward compatibility with Bronze Tier functionality while adding Silver Tier capabilities.

## Constitution Check
The implementation must comply with the AI Employee Project Constitution:

### I. Local-First Architecture ✅
- All data stored locally in Obsidian vault
- Markdown remains single source of truth
- Sensitive data never committed or synced externally
- Vault structure follows Silver tier specification

### II. External Actions and MCP Integration ✅
- MCP server handles all external actions with JSON-RPC over stdio
- All sensitive external actions route through HITL approval
- At least 1 MCP server implemented (email MCP)

### III. Agent Skills Implementation
- New functionality implemented as Claude Agent Skills
- Skills documented in SKILL.md with purpose, inputs, outputs, approvals, MCP usage

### IV. Security and Privacy ✅
- Credentials stored in .env (gitignored) or OS secrets manager
- Audit logging in JSON format with sanitization
- DRY_RUN mode respected throughout system

### V. Multi-Watcher Architecture ✅
- BaseWatcher pattern extended with WhatsApp and LinkedIn watchers
- Multiple watchers (Gmail + WhatsApp + LinkedIn) operating simultaneously
- PM2 required for continuous operation

### VI. Human-in-the-Loop Approval Workflow ✅
- Approval files in /Pending_Approval
- Human moves files to /Approved or /Rejected
- Execution via MCP only for approved actions

### VII. Autonomous Operation ✅
- Processor runs continuously with PM2
- Auto-detect /Needs_Action files and invoke skills
- Ralph Wiggum Loop for multi-step completion

### IX. Paper Workflow & Git Integration ✅
- Follows /sp.specify → /sp.plan → /sp.tasks → /sp.implement workflow
- Outputs committed as specified in constitution

## Project Structure
```
specs/
└── 002-silver-tier/
    ├── spec.md                 # Feature specification
    ├── plan.md                 # This file
    ├── research.md             # Research findings
    ├── data-models/
    │   └── data-model.md       # Entity relationships and schemas
    ├── contracts/
    │   └── email-mcp-contract.md  # MCP server interface specification
    ├── quickstarts/
    │   └── quickstart.md       # Setup and deployment guide
    └── checklists/
        └── requirements.md     # Quality validation checklist
```

## Implementation Phases

### Phase 0: Setup and Research
**Duration**: 2-4 hours
**Dependencies**: Bronze tier completion

Tasks:
- [x] Research MCP server best practices
- [x] Research LinkedIn API v2 capabilities and limitations
- [x] Research Playwright for WhatsApp automation
- [x] Research PM2 for Python process management
- [x] Document findings in research.md
- [x] Plan MCP server architecture

### Phase 1: MCP Server Implementation
**Duration**: 4-6 hours
**Dependencies**: Phase 0 completion

Tasks:
- [ ] Implement Email MCP server with JSON-RPC over stdio
- [ ] Create secure credential handling for email server
- [ ] Implement error handling and rate limiting
- [ ] Add logging and health check capabilities
- [ ] Test MCP server with sample requests
- [ ] Document MCP server contract in contracts/ directory

### Phase 2: Watcher Development
**Duration**: 6-8 hours
**Dependencies**: Phase 1 completion

Tasks:
- [ ] Implement WhatsApp Watcher using Playwright
  - [ ] Set up persistent session handling
  - [ ] Implement message detection logic
  - [ ] Create action file generation
- [ ] Implement LinkedIn Watcher using API or browser
  - [ ] Set up OAuth2 authentication
  - [ ] Implement activity monitoring
  - [ ] Create action file generation
- [ ] Update Gmail watcher to follow BaseWatcher pattern
- [ ] Test all watchers independently
- [ ] Add error handling and logging to all watchers

### Phase 3: HITL Approval Workflow
**Duration**: 4-6 hours
**Dependencies**: Phase 2 completion

Tasks:
- [ ] Enhance main processor to create approval requests
- [ ] Implement approval file format following constitution guidelines
- [ ] Add logic to detect sensitive actions requiring approval
- [ ] Create approval request generation from action files
- [ ] Implement execution logic for approved actions via MCP
- [ ] Test complete approval workflow

### Phase 4: Process Management and Deployment
**Duration**: 2-4 hours
**Dependencies**: Phase 3 completion

Tasks:
- [ ] Create PM2 ecosystem file for all processes
- [ ] Configure auto-restart and monitoring
- [ ] Set up log management
- [ ] Test process resilience with simulated failures
- [ ] Document deployment procedures

### Phase 5: Audit Logging and Dashboard Enhancement
**Duration**: 3-4 hours
**Dependencies**: Phase 4 completion

Tasks:
- [ ] Implement JSON audit logging following constitution format
- [ ] Add sanitization to remove PII from logs
- [ ] Implement log rotation and retention policies
- [ ] Update Dashboard.md to show pending approvals, MCP status
- [ ] Add summary of recent log entries to dashboard
- [ ] Test logging functionality

### Phase 6: Social Media Automation
**Duration**: 3-4 hours
**Dependencies**: Phase 5 completion

Tasks:
- [ ] Implement LinkedIn post generation logic
- [ ] Create content templates based on Company_Handbook.md
- [ ] Implement rate limiting (1-3 posts per day)
- [ ] Integrate with approval workflow
- [ ] Test LinkedIn post creation and approval flow
- [ ] Add monitoring for posted content performance

### Phase 7: Integration and Testing
**Duration**: 4-6 hours
**Dependencies**: All previous phases

Tasks:
- [ ] End-to-end testing of complete workflow
- [ ] Test multi-watcher simultaneous operation
- [ ] Validate backward compatibility with Bronze tier
- [ ] Performance testing for 24+ hour operation
- [ ] Security validation (no credentials in vault/git)
- [ ] Constitution compliance verification

## Key Technical Decisions

### Decision 1: MCP Server Technology
**Issue**: How to implement MCP server for external actions?
**Options**:
- A: Python-based server with JSON-RPC over stdio
- B: Node.js-based server with JSON-RPC over stdio
- C: HTTP-based MCP server
**Chosen**: A (Python-based server with JSON-RPC over stdio)
**Rationale**: Aligns with existing codebase, provides secure isolation of credentials, follows constitution requirement for stdio communication

### Decision 2: WhatsApp Automation Method
**Issue**: How to implement WhatsApp automation?
**Options**:
- A: Playwright with WhatsApp Web (persistent sessions)
- B: WhatsApp Business API
- C: Third-party libraries like python-whatsapp
**Chosen**: A (Playwright with WhatsApp Web)
**Rationale**: Free to use, fits existing technology stack, allows persistent sessions to avoid repeated authentication

### Decision 3: LinkedIn Integration Approach
**Issue**: How to integrate with LinkedIn?
**Options**:
- A: LinkedIn Marketing Developer API
- B: Browser automation with Playwright
- C: RSS feeds or third-party services
**Chosen**: A (LinkedIn Marketing Developer API)
**Rationale**: Official API provides stable integration, proper OAuth2 authentication, respects rate limits

### Decision 4: Process Management Solution
**Issue**: How to ensure 24/7 uptime for watchers and processor?
**Options**:
- A: PM2 with ecosystem file
- B: systemd services (Linux only)
- C: Docker containers with restart policies
**Chosen**: A (PM2 with ecosystem file)
**Rationale**: Cross-platform solution, good Python support, built-in monitoring features, fits constitution's local-first approach

### Decision 5: Audit Logging Format
**Issue**: What format and structure for audit logs?
**Options**:
- A: JSON format following constitution specification exactly
- B: Custom structured format
- C: Standard log format (CSV, etc.)
**Chosen**: A (JSON format following constitution specification)
**Rationale**: Constitution requirement, provides flexibility for analysis, easy to sanitize PII

### Decision 6: HITL Approval Detection
**Issue**: How to determine which actions require human approval?
**Options**:
- A: Keyword-based detection in action content
- B: Predefined action types that require approval
- C: Risk scoring algorithm
**Chosen**: A (Keyword-based detection with predefined sensitive actions)
**Rationale**: Simple to implement, effective for initial implementation, can be enhanced later

### Decision 7: Credential Management
**Issue**: How to securely manage credentials without committing to git?
**Options**:
- A: .env files with gitignore
- B: OS-level secrets management (Windows Credential Manager, macOS Keychain)
- C: Encrypted configuration files
**Chosen**: A (.env files with gitignore) with option to enhance with B
**Rationale**: Simple to implement, widely understood, constitution compliant, can be enhanced later

## Risks and Mitigation Strategies

### Risk 1: WhatsApp Web TOS Compliance
**Risk**: WhatsApp may block automation attempts
**Mitigation**: Implement conservative rate limiting, random delays, and monitor for detection

### Risk 2: LinkedIn API Rate Limits
**Risk**: Exceeding LinkedIn's rate limits
**Mitigation**: Implement strict rate limiting (1-3 posts/day), proper error handling, and retry logic

### Risk 3: MCP Server Security
**Risk**: Vulnerability in MCP server communication
**Mitigation**: Use stdio (not network), sanitize all inputs, validate all requests, implement proper authentication

### Risk 4: Process Stability
**Risk**: Watchers or processor crashing
**Mitigation**: Robust error handling, PM2 auto-restart, proper logging, graceful degradation

## Testing Strategy

### Unit Tests
- MCP server request/response handling
- Watcher update detection logic
- Approval request generation
- Audit log formatting

### Integration Tests
- End-to-end approval workflow
- MCP server communication
- Multi-watcher simultaneous operation
- Process restart scenarios

### Acceptance Tests
- Complete Bronze tier functionality remains intact
- Silver tier features work as specified in success criteria
- Constitution compliance verified
- 24+ hour continuous operation

## Success Criteria Validation

### SC-001: Bronze tier features unchanged
**Validation**: Run existing Bronze tier tests and verify functionality

### SC-002: Three watchers operational
**Validation**: Start Gmail, WhatsApp, LinkedIn watchers simultaneously and verify they all detect updates

### SC-003: End-to-end HITL workflow
**Validation**: Trigger sensitive action, verify approval request creation, manual approval, MCP execution, logging

### SC-004: MCP server integration
**Validation**: Execute external action via MCP server and verify successful completion

### SC-005: LinkedIn post automation
**Validation**: Generate LinkedIn post content, approve, execute, and verify post creation

### SC-006: 24+ hour operation
**Validation**: Run system for 24+ hours with PM2 monitoring

### SC-007: Structured JSON audit logs
**Validation**: Verify all external actions produce properly formatted JSON audit entries

### SC-008: Dashboard updates
**Validation**: Verify Dashboard.md reflects pending approvals, MCP status, and log summaries

### SC-009: Security constraints met
**Validation**: Verify no credentials in vault/git, DRY_RUN respected, skills documented

### SC-010: Productivity improvement
**Validation**: Measure time saved versus manual processing of similar tasks