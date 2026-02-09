# Tasks: Bronze-tier Personal AI Employee

## Feature Overview

Build a Bronze-tier Personal AI Employee that monitors an Obsidian vault for new items in the Inbox directory, automatically moves them to Needs_Action, processes them using Claude Code agent skills, and updates a Dashboard.md with current task status. The system follows a local-first architecture using Python 3.13+ with filesystem watchers and Markdown files as the single source of truth.

## Phase 1: Setup

### Goal
Initialize the project structure and configure the development environment with all necessary dependencies and vault directories.

### Independent Test Criteria
The system can be started with a basic configuration and the vault directories exist with proper permissions.

### Tasks

- [X] T001 Create project structure per implementation plan in src/watchers/, src/processors/, src/utils/
- [X] T002 Initialize requirements.txt with watchdog, python-dotenv, pathlib, logging dependencies
- [X] T003 Create vault directory structure AI_Employee_Vault/{Inbox,Needs_Action,Done}/
- [X] T004 Create initial Dashboard.md in AI_Employee_Vault/Dashboard.md
- [X] T005 Create initial Company_Handbook.md in AI_Employee_Vault/Company_Handbook.md
- [X] T006 Create .env file with VAULT_PATH, CHECK_INTERVAL, LOG_LEVEL, DRY_RUN settings
- [X] T007 Set up gitignore for sensitive files and logs

## Phase 2: Foundational Components

### Goal
Implement the foundational components including the BaseWatcher pattern, configuration loading, and logging systems that will be used by all user stories.

### Independent Test Criteria
The base components can be imported and instantiated without errors, and configuration is properly loaded from environment variables.

### Tasks

- [X] T008 [P] Implement BaseWatcher abstract class in src/watchers/base_watcher.py
- [X] T009 [P] Implement concrete FilesystemWatcher class in src/watchers/file_system_watcher.py
- [X] T010 [P] Implement config_loader utility in src/utils/config_loader.py
- [X] T011 [P] Implement logger utility in src/utils/logger.py
- [X] T012 [P] Create main application entry point in src/main.py
- [X] T013 [P] Implement vault statistics functionality in src/processors/vault_processor.py
- [X] T014 [P] Create ActionItem model in src/processors/action_item.py

## Phase 3: [US1] Vault Monitoring and Processing

### Goal
Implement the core functionality that monitors the Inbox directory, moves files to Needs_Action, processes them using Claude Code, and updates the dashboard.

### Independent Test Criteria
Placing a file in the /Inbox directory results in it being automatically moved to /Needs_Action, processed by Claude Code, moved to /Done, and the dashboard updated with accurate counts.

### Tasks

- [X] T015 [P] [US1] Implement file system event detection in src/watchers/file_system_watcher.py
- [X] T016 [P] [US1] Implement file movement logic (Inbox → Needs_Action) in src/processors/vault_processor.py
- [X] T017 [US1] Integrate Claude Code agent skill processing in src/processors/vault_processor.py
- [X] T018 [P] [US1] Implement file movement logic (Needs_Action → Done) in src/processors/vault_processor.py
- [X] T019 [US1] Connect watcher to vault processor in src/main.py
- [X] T020 [P] [US1] Add file extension filtering to watcher in src/watchers/file_system_watcher.py
- [X] T021 [US1] Implement basic error handling for file operations in src/processors/vault_processor.py

## Phase 4: [US2] Dashboard Generation

### Goal
Implement the dashboard generation system that shows accurate counts of pending and completed items.

### Independent Test Criteria
The dashboard file accurately reflects the current state of the vault directories regardless of external processing.

### Tasks

- [X] T022 [P] [US2] Implement vault statistics collection in src/processors/vault_processor.py
- [X] T023 [US2] Create dashboard template and formatting in src/processors/vault_processor.py
- [X] T024 [US2] Implement dashboard update functionality in src/processors/vault_processor.py
- [X] T025 [P] [US2] Add timestamp tracking to dashboard updates in src/processors/vault_processor.py
- [X] T026 [US2] Integrate dashboard updates with file processing workflow in src/main.py
- [X] T027 [US2] Validate dashboard output format against specification in src/processors/vault_processor.py

## Phase 5: [US3] File System Watcher

### Goal
Implement the continuous file system monitoring that detects changes without manual intervention.

### Independent Test Criteria
The file watcher can detect file creation/modification in the monitored directory and trigger appropriate processing workflows.

### Tasks

- [X] T028 [P] [US3] Implement continuous monitoring loop in src/watchers/file_system_watcher.py
- [X] T029 [US3] Add debouncing logic to handle rapid file changes in src/watchers/file_system_watcher.py
- [X] T030 [US3] Implement event filtering for specific directories in src/watchers/file_system_watcher.py
- [X] T031 [P] [US3] Add monitoring status reporting in src/watchers/file_system_watcher.py
- [X] T032 [US3] Implement graceful shutdown for watcher in src/watchers/file_system_watcher.py
- [X] T033 [US3] Add retry mechanisms for transient failures in src/watchers/file_system_watcher.py

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Complete the implementation with proper error handling, validation, and edge case handling.

### Independent Test Criteria
The system handles all edge cases gracefully and maintains the local-first architecture with no external dependencies.

### Tasks

- [X] T034 [P] Implement comprehensive error handling across all modules
- [X] T035 [P] Add input validation for all file operations
- [X] T036 [P] Implement permission checking for vault directories
- [X] T037 [P] Add validation for Markdown file formats
- [X] T038 [P] Implement retry logic for failed file operations
- [X] T039 [P] Add health check functionality to main application
- [X] T040 [P] Complete documentation for all public interfaces
- [X] T041 [P] Add unit tests for core functionality
- [X] T042 [P] Final integration testing and validation

## Dependencies

### User Story Completion Order
1. US1 (Vault Monitoring and Processing) - Core functionality
2. US2 (Dashboard Generation) - Depends on US1 for data
3. US3 (File System Watcher) - Enables US1 functionality

### Blocking Dependencies
- T001-T007 must complete before any other tasks (setup)
- T008-T014 must complete before US1, US2, and US3 tasks (foundational components)
- US1 requires components from Phase 2 and vault monitoring capability (US3)

## Parallel Execution Examples

### Per User Story 1 (Vault Monitoring and Processing):
- T015 and T016 can run in parallel (both in vault_processor.py)
- T020 and T021 can run in parallel (error handling and filtering)

### Per User Story 2 (Dashboard Generation):
- T022 and T023 can run in parallel (statistics and template)
- T024 and T025 can run in parallel (update functionality and timestamps)

### Per User Story 3 (File System Watcher):
- T028 and T030 can run in parallel (monitoring loop and event filtering)
- T031 and T032 can run in parallel (status reporting and shutdown)

## Implementation Strategy

### MVP Scope (User Story 1 Only)
Focus on the core functionality of detecting files in Inbox, moving them to Needs_Action, processing them, and updating the dashboard. This provides immediate value while keeping the initial implementation manageable.

### Incremental Delivery
1. Complete Phase 1 & 2: Basic setup and foundational components
2. Complete US1: Core vault processing functionality
3. Complete US2: Dashboard generation
4. Complete US3: Enhanced file system watching
5. Complete Phase 6: Polish and edge cases

### Success Validation
- New files in /Inbox are detected and moved to /Needs_Action within 60 seconds
- Dashboard.md is updated accurately reflecting the current state of all vault directories
- Claude Code successfully processes 90% of action items without human intervention
- The system maintains local-first architecture with no external data storage