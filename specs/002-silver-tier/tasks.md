# Tasks: Silver Tier Personal AI Employee

## Phase 1: Setup and Project Initialization

- [X] T001 Create project structure following Silver Tier vault structure with Inbox, Needs_Action, Pending_Approval, Approved, Rejected, Done, Logs, Plans directories
- [X] T002 Set up Python virtual environment with Python 3.13+ and install required packages (playwright, requests, python-dotenv)
- [X] T003 Install PM2 globally and create initial ecosystem configuration file
- [X] T004 Create .env file template with all required environment variables for MCP, LinkedIn, and process management
- [X] T005 Create gitignore file ensuring .env and other sensitive files are excluded from git
- [X] T006 Initialize the AI_Employee_Vault directory structure in the project
- [X] T007 Create base directories for mcp, watchers, src, and logs

## Phase 2: Foundational Components

- [X] T008 [P] Implement BaseWatcher abstract class in src/watchers/base_watcher.py following the pattern from quickstart guide
- [X] T009 [P] Create MCP server base structure in mcp/email-server.py with JSON-RPC over stdio implementation
- [X] T010 [P] Set up logging framework in src/utils/logger.py for audit logging
- [X] T011 [P] Create data model classes in src/models/ for WatcherInput, ActionFile, ApprovalRequest, AuditLogEntry, PlanFile, ProcessManager
- [X] T012 Create dashboard update utility in src/utils/dashboard_updater.py
- [X] T013 Set up configuration management in src/config/settings.py

## Phase 3: [US1] Multi-Channel Watcher Processing with HITL Approval

**User Story Goal**: Hackathon participant can extend Bronze tier AI employee to monitor multiple channels (Gmail, WhatsApp, LinkedIn) simultaneously and perform external actions like sending emails or posting on LinkedIn, but with mandatory human approval for all sensitive operations.

**Independent Test Criteria**: The system can receive inputs from Gmail, WhatsApp, and LinkedIn simultaneously, create Plan.md files for complex tasks, route sensitive actions to /Pending_Approval, and execute only approved actions via MCP servers.

**Acceptance Tests**:
- [X] T014 [P] [US1] Test that inputs arrive from Gmail, WhatsApp, and LinkedIn simultaneously and sensitive actions create Plan.md files and approval requests appear in /Pending_Approval
- [X] T015 [P] [US1] Test that approval requests in /Pending_Approval execute via MCP server when operator moves file to /Approved and results are logged

**Implementation Tasks**:
- [X] T016 [P] [US1] Implement WhatsApp Watcher using Playwright in watchers/whatsapp_watcher.py with persistent session handling
- [X] T017 [P] [US1] Implement LinkedIn Watcher using API in watchers/linkedin_watcher.py with OAuth2 authentication
- [X] T018 [P] [US1] Create Action File generator in src/utils/action_file_generator.py to create action files from watcher inputs
- [X] T019 [US1] Enhance main processor to create approval requests based on sensitive action detection
- [X] T020 [US1] Implement approval file format following constitution guidelines in src/utils/approval_formatter.py
- [X] T021 [US1] Add logic to detect sensitive actions requiring approval using keyword-based detection
- [X] T022 [US1] Create approval request generation from action files with proper formatting
- [X] T023 [US1] Update Gmail watcher to follow BaseWatcher pattern if not already implemented
- [X] T024 [US1] Test all watchers independently to ensure proper action file generation

## Phase 4: [US2] MCP Server Integration for External Actions

**User Story Goal**: Developer can execute external actions like sending emails or LinkedIn posts securely through MCP servers that handle authentication separately, preventing credential exposure in the vault or codebase.

**Independent Test Criteria**: The system can route external action requests to an MCP server (like email sending) and receive execution results back without exposing credentials.

**Acceptance Tests**:
- [X] T025 [P] [US2] Test that when approved external action request is triggered, MCP action execution skill executes via MCP server and result is received

**Implementation Tasks**:
- [X] T026 [P] [US2] Complete Email MCP server implementation in mcp/email-server.py with send_email, get_account_info, and validate_recipients methods
- [X] T027 [P] [US2] Implement MCP client connector in src/utils/mcp_client.py for JSON-RPC communication
- [X] T028 [US2] Create secure credential handling for email server using environment variables
- [X] T029 [US2] Implement error handling and rate limiting in MCP server
- [X] T030 [US2] Add logging and health check capabilities to MCP server
- [X] T031 [US2] Test MCP server with sample requests
- [X] T032 [US2] Document MCP server contract in specs/002-silver-tier/contracts/email-mcp-contract.md

## Phase 5: [US3] Continuous Operation and Process Management

**User Story Goal**: Operator can run the AI employee system continuously for 24+ hours with reliable process management to handle crashes and restarts automatically.

**Independent Test Criteria**: The system runs continuously for 24+ hours using PM2 or similar process manager, with automatic restart on crashes.

**Acceptance Tests**:
- [X] T033 [P] [US3] Test that when system is started with PM2 and a process crashes, it automatically restarts

**Implementation Tasks**:
- [X] T034 [P] [US3] Complete PM2 ecosystem file in ecosystem.config.js for all processes (gmail-watcher, whatsapp-watcher, linkedin-watcher, main-processor)
- [X] T035 [P] [US3] Configure auto-restart and monitoring in PM2 configuration
- [X] T036 [US3] Set up log management in PM2 configuration with proper file paths
- [X] T037 [US3] Test process resilience with simulated failures
- [X] T038 [US3] Document deployment procedures in docs/deployment.md

## Phase 6: [US4] Structured Audit Logging and Dashboard Updates

**User Story Goal**: Operator has comprehensive audit trails of all actions taken by the AI employee and real-time dashboard updates showing pending approvals and system status.

**Independent Test Criteria**: The system creates structured JSON audit logs and updates Dashboard.md with pending approval counts and MCP status.

**Acceptance Tests**:
- [X] T039 [P] [US4] Test that when an action is executed, structured JSON entry appears in /Logs/YYYY-MM-DD.json
- [X] T040 [P] [US4] Test that when system status changes, Dashboard.md reflects current status including pending approvals and MCP status

**Implementation Tasks**:
- [X] T041 [P] [US4] Implement JSON audit logging in src/utils/audit_logger.py following constitution format
- [X] T042 [P] [US4] Add sanitization to remove PII from logs in src/utils/log_sanitizer.py
- [X] T043 [US4] Implement log rotation and retention policies in src/utils/log_manager.py
- [X] T044 [US4] Update Dashboard.md to show pending approvals, MCP status and recent log summaries in src/utils/dashboard_updater.py
- [X] T045 [US4] Add summary of recent log entries to dashboard
- [X] T046 [US4] Test logging functionality with various action types

## Phase 7: Social Media Automation Implementation

- [X] T047 [P] Implement LinkedIn post generation logic in src/social/linkedin_post_generator.py
- [X] T048 [P] Create content templates based on Company_Handbook.md in src/social/content_templates.py
- [X] T049 Implement rate limiting (1-3 posts per day) in src/social/rate_limiter.py
- [X] T050 Integrate LinkedIn posting with approval workflow in src/workflows/linkedin_approval_flow.py
- [X] T051 Test LinkedIn post creation and approval flow
- [X] T052 Add monitoring for posted content performance in src/social/performance_tracker.py

## Phase 8: Integration and Testing

- [X] T053 Perform end-to-end testing of complete workflow from watcher input to MCP execution and logging
- [X] T054 Test multi-watcher simultaneous operation to ensure no conflicts
- [X] T055 Validate backward compatibility with Bronze tier functionality
- [X] T056 Conduct performance testing for 24+ hour operation
- [X] T057 Perform security validation to ensure no credentials in vault/git
- [X] T058 Verify constitution compliance across all implemented features
- [X] T059 Run all acceptance tests for user stories to verify completion
- [X] T060 Create comprehensive test suite for continuous integration

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T061 Add error handling and logging to all watchers
- [X] T062 Implement graceful degradation for MCP server unavailability
- [X] T063 Add proper exception handling throughout the codebase
- [X] T064 Update Company_Handbook.md with new MCP server capabilities
- [X] T065 Create SKILL.md documenting new agent skills with purpose, inputs, outputs, approval requirements, and MCP usage
- [X] T066 Optimize performance of main processing loop in src/main.py
- [X] T067 Add health check endpoints for monitoring
- [X] T068 Update documentation for all new features and configuration options

## Dependencies

- User Story 1 (Multi-Channel Watcher) requires foundational components (Phase 2) to be completed first
- User Story 2 (MCP Integration) can run in parallel with User Story 1 after foundational components
- User Story 3 (Process Management) can begin after User Story 1 and 2 core functionality is implemented
- User Story 4 (Audit Logging) can run in parallel with other user stories
- Social Media Automation (Phase 7) depends on MCP Integration (US2) and HITL Approval (US1)
- Integration and Testing (Phase 8) depends on completion of all user stories

## Parallel Execution Opportunities

- Multiple watchers (WhatsApp, LinkedIn, Gmail enhancement) can be developed in parallel
- MCP server and client connector can be developed in parallel
- Audit logging and dashboard updates can be developed in parallel
- Different user stories can have parallel components within them (marked with [P] tags)

## Implementation Strategy

1. **MVP Scope**: Begin with User Story 1 (Multi-Channel Watcher) and User Story 2 (MCP Integration) as they form the core Silver Tier functionality
2. **Incremental Delivery**: Each user story should be delivered as a complete, independently testable increment
3. **Iterative Approach**: Implement core functionality first, then add enhancements and error handling
4. **Continuous Testing**: Validate each component as it's implemented against the acceptance criteria