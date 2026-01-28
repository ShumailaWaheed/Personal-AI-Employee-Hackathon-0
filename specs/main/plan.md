# Implementation Plan: Bronze-tier Personal AI Employee (2026 Hackathon)

**Branch**: `main` | **Date**: 2026-01-28 | **Spec**: [003-bronze-ai-employee/spec.md](../003-bronze-ai-employee/spec.md)
**Input**: Feature specification from `/specs/003-bronze-ai-employee/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Bronze-tier Personal AI Employee that monitors an Obsidian vault for new items in the Inbox directory, automatically moves them to Needs_Action, processes them using Claude Code agent skills, and updates a Dashboard.md with current task status. The system follows a local-first architecture using Python 3.13+ with filesystem watchers and Markdown files as the single source of truth.

## Technical Context

**Language/Version**: Python 3.13+ (as mandated by constitution v3.0.0)
**Primary Dependencies**: watchdog (filesystem monitoring), pathlib (path operations), python-dotenv (environment config), logging (monitoring)
**Storage**: Local Markdown files in Obsidian vault structure (Inbox, Needs_Action, Done directories)
**Testing**: pytest for automated testing, manual validation for core Bronze tier paths
**Target Platform**: Local system (Windows/Linux/Mac) with Obsidian vault
**Project Type**: Single project with Python-based file system watcher and agent skills
**Performance Goals**: Detect and move new files within 60 seconds, update dashboard in near real-time
**Constraints**: Local-first architecture (no external data storage), read-only external APIs, sensitive data never committed
**Scale/Scope**: Single user personal AI employee, local vault with structured directories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification:
- ✅ **Local-First Architecture**: All data stored locally in Obsidian vault as Markdown files per Bronze tier requirements
- ✅ **External API Usage**: Read-only access only (Bronze tier requirement)
- ✅ **Sensitive Data Protection**: Credentials stored in .env file (gitignored) per constitution
- ✅ **Vault Structure**: Implemented with required Bronze tier directories (Inbox, Needs_Action, Done)
- ✅ **Agent Skills**: Using existing `.claude/skills/process-action-items/` as required
- ✅ **BaseWatcher Pattern**: Will implement BaseWatcher pattern per constitution guidelines
- ✅ **Human-in-the-Loop**: Not required for Bronze tier (Silver+ requirement)
- ✅ **Security & Privacy**: Following credential management guidelines, no sensitive data committed

All constitution requirements satisfied for Bronze tier implementation.

## Architecture Sketch

### Data and Control Flow:
```
Python Filesystem Watcher → Claude Code → Obsidian vault (read/write) → Dashboard updates

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                     │    │                 │
│   /Inbox        │───▶│  BaseWatcher     │───▶│  Claude Code        │───▶│  Dashboard.md   │
│  (new items)    │    │  (watchdog)      │    │  (.claude/skills/)  │    │  (updates)      │
│                 │    │                  │    │                     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  /Needs_Action  │
                       │  (processing)   │
                       └─────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │    /Done       │
                        │  (completed)   │
                        └───────────────┘
```

### BaseWatcher Pattern Integration:
- The system implements the BaseWatcher pattern as specified in the constitution
- Integrated with existing Agent Skill at `.claude/skills/process-action-items/`
- Watcher monitors `/Inbox` directory and moves files to `/Needs_Action` for processing
- After processing, files are moved to `/Done` and dashboard is updated

## Project Structure

### Documentation (this feature)

```text
specs/main/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── watchers/              # File system watchers implementing BaseWatcher pattern
│   ├── base_watcher.py    # Base class with abstract methods
│   ├── file_system_watcher.py  # Concrete implementation for filesystem monitoring
│   └── __init__.py
├── processors/            # Claude Code integration and processing logic
│   ├── vault_processor.py # Logic for vault operations and dashboard updates
│   ├── action_item.py     # Action item entity and processing rules
│   └── __init__.py
├── utils/                 # Utility functions
│   ├── config_loader.py   # Environment variable loading
│   ├── logger.py          # Logging setup
│   └── __init__.py
├── main.py                # Main entry point for the AI employee
└── __init__.py
```

### Vault Structure (Obsidian)

```text
AI_Employee_Vault/
├── Inbox/                 # New items to be processed
├── Needs_Action/          # Items currently being processed
├── Done/                  # Completed items
├── Dashboard.md           # Current status dashboard
├── Company_Handbook.md    # Processing rules and guidelines
├── Logs/                  # (Future Silver tier - log files)
└── .env                   # Environment variables (gitignored)
```

**Structure Decision**: Single Python project with modular architecture following the BaseWatcher pattern and local-first principles from the constitution.

## Phased Implementation Approach

### Phase 0: Research → Foundation
- Research filesystem monitoring best practices with Python watchdog
- Investigate Claude Code integration patterns with agent skills
- Study Obsidian vault structures and Markdown processing techniques
- Define vault directory structure and dashboard format standards

**Required Files**:
- `research.md` - Research findings and technology decisions
- `/Inbox`, `/Needs_Action`, `/Done` - Vault directories
- `Dashboard.md` - Dashboard template and format
- `Company_Handbook.md` - Processing rules documentation

**Expected Outputs**:
- Technology stack decisions documented
- Vault structure finalized
- Integration patterns validated

### Phase 1: Foundation → Analysis
- Implement BaseWatcher pattern for filesystem monitoring
- Create vault processor for Claude Code integration
- Build dashboard generation logic
- Set up configuration and environment management

**Required Files**:
- `base_watcher.py` - Abstract base class for watchers
- `file_system_watcher.py` - Concrete filesystem watcher implementation
- `vault_processor.py` - Claude Code integration layer
- `config_loader.py` - Environment configuration

**Expected Outputs**:
- Working filesystem watcher
- Basic vault processing capability
- Configurable system setup

### Phase 2: Analysis → Synthesis
- Integrate all components into cohesive system
- Implement complete file movement workflow (Inbox → Needs_Action → Done)
- Create dashboard update mechanism
- Conduct manual testing and validation

**Required Files**:
- `main.py` - Main application entry point
- `logger.py` - Centralized logging system
- Updated `Dashboard.md` - Dynamic dashboard generation
- `tests/` - Optional automated tests for core paths

**Expected Outputs**:
- Fully functional Bronze-tier AI employee
- Validated acceptance criteria
- Test results and documentation

## Research-Concurrent Methodology

Research will be conducted concurrently with implementation focusing on:

1. **Documentation Gathering**:
   - Python watchdog library documentation and best practices
   - Claude Code agent skills integration patterns
   - Obsidian vault structure and API documentation
   - File system monitoring techniques

2. **API Research**:
   - Filesystem event handling patterns
   - Claude Code skill invocation mechanisms
   - Markdown parsing and generation libraries

3. **Vault Design Research**:
   - Obsidian vault best practices
   - Markdown formatting standards for action items
   - Dashboard generation patterns
   - Cross-reference with constitution requirements

**Sources**: All research findings will be documented with APA-style citations as per constitution requirements.

## Critical Decisions Requiring Documentation

### 1. Watcher Type Selection
**Decision**: Filesystem watcher vs Gmail watcher
- **Chosen**: Filesystem watcher (watchdog library)
- **Rationale**: Simpler implementation, aligns with Bronze tier requirements, no external API authentication needed
- **Trade-offs**:
  - Gmail watcher: Requires API authentication, more complex setup, but broader input sources
  - Filesystem watcher: Simpler, local-only, meets Bronze tier requirements

### 2. Vault Organization and Markdown Standards
**Decision**: Markdown formatting and vault structure
- **Chosen**: Simple file-based structure with standardized directory organization
- **Rationale**: Aligns with constitution's local-first architecture, easy to manage and extend
- **Standards**:
  - Files in `/Inbox` are raw input items
  - Files in `/Needs_Action` contain processing instructions
  - Files in `/Done` contain final processed results

### 3. Claude Code Integration Choices
**Decision**: Read/write structure and error handling approach
- **Chosen**: Use existing `.claude/skills/process-action-items/` skill with standardized interfaces
- **Rationale**: Leverages existing infrastructure, follows constitution requirements
- **Error Handling**: Log errors and continue processing, with retry mechanisms for transient failures

## Quality Validation Procedures

### Manual Testing Procedures:
1. **Watcher Trigger Validation**:
   - Place file in `/Inbox` directory
   - Verify automatic movement to `/Needs_Action`
   - Confirm proper file handling and error logging

2. **Claude Code Integration Validation**:
   - Verify Claude Code reads files from vault correctly
   - Confirm proper processing using agent skills
   - Validate write-back to vault after processing

3. **Dashboard Update Validation**:
   - Confirm dashboard updates accurately reflect vault state
   - Verify correct counting of pending and completed items
   - Test dashboard refresh after file movements

### Automated Testing (Optional for Bronze tier):
- Core file movement workflow tests
- Dashboard generation accuracy tests
- Configuration loading tests
- Error handling tests

### Error Handling:
- All exceptions logged in console (Silver tier will add `/Logs` directory)
- Retry logic for transient failures
- Graceful degradation when individual files fail processing

## Testing Strategy

### Acceptance Criteria Validation:

1. **Vault Directories Exist and Are Writeable**:
   - Test: Verify `/Inbox`, `/Needs_Action`, `/Done` directories exist and are writable
   - Validation: System can create, move, and delete files in these directories

2. **Watcher Correctly Detects New Items and Generates Action Files**:
   - Test: Place new file in `/Inbox`, observe automatic movement to `/Needs_Action`
   - Validation: File is detected within 60 seconds and moved appropriately

3. **Agent Skill Executes in Sandboxed Claude Code Environment**:
   - Test: Process files in `/Needs_Action` using existing agent skill
   - Validation: Files are processed according to Company_Handbook.md rules

4. **Dashboard Shows Correct Counts of Pending and Done Items**:
   - Test: Verify Dashboard.md updates with accurate counts after file movements
   - Validation: Dashboard reflects real-time state of all vault directories

### Test Scenarios:
- Normal operation: Files flow from Inbox → Needs_Action → Done with dashboard updates
- Error conditions: Handle corrupted files, permission issues, missing directories
- Concurrent operations: Multiple files arriving simultaneously
- Configuration changes: Environment variable updates and reload

## Risk Mitigation

1. **Data Loss Prevention**: Files are moved (not copied) with error recovery mechanisms
2. **System Reliability**: Watchdog library provides robust filesystem monitoring
3. **Configuration Management**: Environment variables stored securely in .env file
4. **Error Recovery**: Comprehensive logging and retry mechanisms for transient failures

## Success Metrics

1. **Performance**: New files detected and moved within 60 seconds (per FR-001)
2. **Accuracy**: Dashboard.md accurately reflects vault state (per FR-005)
3. **Reliability**: 90% of action items processed successfully without human intervention (per SC-003)
4. **Architecture**: Maintains local-first architecture with no external data storage (per SC-004)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

All constitution requirements are met without violations requiring justification.
