# Data Model: Silver Tier Personal AI Employee

## Overview
This document defines the data structures and relationships for the Silver Tier Personal AI Employee system. The system extends Bronze Tier functionality with multi-watcher support, MCP integration, HITL approval workflows, and enhanced audit logging.

## Core Entities

### 1. Watcher Input
**Description**: Data or events received from external sources that may trigger system actions

**Attributes**:
- id: Unique identifier for the input
- source_type: Type of source (gmail, whatsapp, linkedin, filesystem)
- source_id: Identifier from the source system
- timestamp: When the input was received
- content: Raw content from the source
- metadata: Additional metadata from the source
- processed: Boolean indicating if input has been processed
- action_required: Boolean indicating if action is needed

**Relationships**:
- One-to-many with Action Files (one input may generate multiple action files)

### 2. Action File
**Description**: Markdown file representing an action that requires processing by the system

**Attributes**:
- id: Unique identifier
- filename: Name of the markdown file
- filepath: Full path to the file
- created_at: Timestamp when file was created
- action_type: Type of action to be performed
- content: Markdown content describing the action
- priority: Priority level (low, medium, high)
- status: Current status (pending, processing, completed, failed)

**Relationships**:
- Many-to-one with Watcher Input (multiple action files may come from one input)
- One-to-many with Approval Request (one action may generate approval request)

### 3. Approval Request
**Description**: Markdown file representing an action that requires human approval before execution

**Attributes**:
- id: Unique identifier
- filename: Name of the markdown file
- filepath: Full path to the file
- created_at: Timestamp when request was created
- action_type: Type of action requiring approval (email_send, linkedin_post, etc.)
- target: Target of the action (email address, LinkedIn post recipient)
- parameters: Parameters for the action (excluding sensitive data)
- risk_level: Risk assessment (low, medium, high)
- auto_approve_eligible: Whether action can be auto-approved
- mcp_server: Name of MCP server that will execute the action
- status: Current status (pending, approved, rejected, executed, failed)

**Relationships**:
- One-to-many with Audit Log Entry (each approval generates audit entries)

### 4. Audit Log Entry
**Description**: Structured JSON record containing comprehensive information about system actions and their outcomes

**Attributes**:
- timestamp: ISO 8601 timestamp of the action
- action_type: Type of action performed
- actor: Who initiated the action (system, user)
- target: Target of the action
- parameters: Parameters passed to the action (sanitized)
- approval_status: Status of approval (approved, rejected, auto_approved)
- result: Result of the action (success, failure, error message)
- execution_time_ms: Time taken to execute the action
- user_id: ID of user who approved (if applicable)

**Relationships**:
- Many-to-one with Approval Request (multiple audit entries may relate to one approval)

### 5. MCP Server Configuration
**Description**: Configuration information for MCP servers that handle external actions

**Attributes**:
- id: Unique identifier for the server
- name: Display name of the server
- type: Type of service (email, social_media, browser_automation, etc.)
- protocol: Communication protocol (stdio, http)
- executable_path: Path to the server executable
- capabilities: List of supported actions
- status: Current status (active, inactive, error)
- health_check_url: URL for health checking (for HTTP-based servers)

**Relationships**:
- One-to-many with Approval Request (server processes multiple requests)
- One-to-many with Audit Log Entry (server generates audit entries)

### 6. Plan File
**Description**: Detailed Markdown document outlining complex multi-step tasks to be executed by the system

**Attributes**:
- id: Unique identifier
- filename: Name of the markdown file
- filepath: Full path to the file
- created_at: Timestamp when plan was created
- title: Title of the plan
- description: Description of the plan
- steps: Ordered list of steps to be executed
- status: Current status (draft, pending_approval, approved, in_progress, completed, failed)
- dependencies: Other files or actions this plan depends on

**Relationships**:
- One-to-many with Approval Request (plan may generate multiple approval requests)

### 7. Process Management Configuration
**Description**: Configuration for managing processes with PM2 or similar tools

**Attributes**:
- id: Unique identifier
- process_name: Name of the process
- script_path: Path to the script file
- interpreter: Python interpreter to use
- args: Arguments to pass to the script
- instances: Number of instances to run (1 or max)
- autorestart: Whether to auto-restart on failure
- watch: Whether to watch for file changes
- env: Environment variables for the process

## State Transitions

### Approval Request States:
1. **pending** → Created in `/Pending_Approval` directory
2. **pending** → `approved` → Moved to `/Approved` directory by user
3. **pending** → `rejected` → Moved to `/Rejected` directory by user
4. **approved** → `executing` → MCP server begins execution
5. **executing** → `executed` → MCP server completes successfully
6. **executing** → `failed` → MCP server execution fails
7. **rejected** → Remains in rejected state

### Action File States:
1. **pending** → Created in `/Needs_Action` directory
2. **pending** → `processing` → System begins processing
3. **processing** → `completed` → Action completed successfully
4. **processing** → `needs_approval` → Action requires human approval
5. **needs_approval** → Transferred to Approval Request
6. **processing** → `failed` → Action failed during processing

## Validation Rules

1. **Approval Request**: Must have valid action_type, target, and parameters before creation
2. **Audit Log Entry**: Timestamp must be current, and sensitive data must be sanitized
3. **Action File**: Must have valid markdown structure and required metadata
4. **MCP Server Configuration**: Executable path must exist and be executable
5. **Watcher Input**: Source type must be registered in the system
6. **Plan File**: Must have at least one step defined before processing

## Indexes
- Approval Request: Index on status and created_at for efficient querying
- Audit Log Entry: Index on timestamp for chronological retrieval
- Action File: Index on status for workflow management
- Watcher Input: Index on source_type and processed for efficient processing