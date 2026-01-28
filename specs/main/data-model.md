# Data Model: Bronze-tier Personal AI Employee

## Key Entities

### 1. Action Item
**Entity Name**: ActionItem
**Fields**:
- `id` (str): Unique identifier for the action item
- `title` (str): Title/description of the action
- `content` (str): Full content of the action item
- `status` (str): Current status ('inbox', 'needs_action', 'done')
- `created_at` (datetime): Timestamp when item was created
- `processed_at` (datetime): Timestamp when item was processed (nullable)
- `source_path` (Path): File path in the vault
- `destination_path` (Path): Target path after processing (nullable)

**Relationships**:
- Belongs to a single vault directory
- Transitions through status states: inbox → needs_action → done

**Validation Rules**:
- ID must be unique within the vault
- Title and content must not be empty
- Status must be one of the defined values
- Created_at must be set when item is created

**State Transitions**:
- inbox → needs_action: When file is detected by watcher
- needs_action → done: When Claude Code processing is complete

### 2. Vault Directory
**Entity Name**: VaultDirectory
**Fields**:
- `path` (Path): Absolute path to the directory
- `type` (str): Directory type ('inbox', 'needs_action', 'done')
- `item_count` (int): Number of items currently in directory
- `last_modified` (datetime): Last modification timestamp

**Relationships**:
- Contains multiple ActionItems
- Related to other VaultDirectories in the vault structure

**Validation Rules**:
- Path must exist and be accessible
- Type must be one of the defined directory types
- Path must be writable for the application

### 3. Dashboard
**Entity Name**: Dashboard
**Fields**:
- `generated_at` (datetime): Timestamp when dashboard was last updated
- `pending_count` (int): Number of items in Needs_Action directory
- `completed_count` (int): Number of items in Done directory
- `new_count` (int): Number of items in Inbox directory
- `content` (str): Rendered dashboard content in Markdown format

**Relationships**:
- Composed of counts from multiple VaultDirectories
- Reflects the current state of the vault

**Validation Rules**:
- All counts must be non-negative integers
- Generated_at must be updated when dashboard is refreshed
- Content must be valid Markdown format

### 4. Processing Rule
**Entity Name**: ProcessingRule
**Fields**:
- `name` (str): Name of the rule
- `condition` (str): Condition that triggers the rule
- `action` (str): Action to take when condition is met
- `priority` (int): Priority of the rule (lower numbers = higher priority)

**Relationships**:
- Applied to ActionItems during processing
- Defined in Company_Handbook.md

**Validation Rules**:
- Name must be unique
- Condition and action must not be empty
- Priority must be a positive integer

## Data Relationships

```
Vault Directory (1) ←→ (Many) Action Item
Action Item (1) ←→ (1) Processing Rule (via Company_Handbook.md)
Dashboard (1) ←→ (Many) Vault Directory (for counts)
```

## State Machine: Action Item Lifecycle

```
[Inbox Directory]
       ↓ (detected by watcher)
[Needs_Action Directory]
       ↓ (processed by Claude Code)
[Done Directory]
       ↓ (dashboard updated)
[Completed]
```

States:
1. **inbox**: New items waiting to be processed
2. **needs_action**: Items currently being processed by Claude Code
3. **done**: Completed items after successful processing

Transitions:
- `detect_new_item`: inbox → needs_action
- `process_item`: needs_action → done
- `update_dashboard`: done → completed status reflected in dashboard

## File Format Specifications

### Action Item File Format (.md)
```markdown
---
id: unique_identifier
title: "Action Title"
status: inbox/needs_action/done
created_at: ISO_8601_TIMESTAMP
processed_at: ISO_8601_TIMESTAMP (optional)
---

# Action Title

Content of the action item...

## Details
Additional details for the AI to process...
```

### Dashboard File Format (Dashboard.md)
```markdown
# AI Employee Dashboard

**Generated at**: ISO_8601_TIMESTAMP

## Status Overview
- 📥 **New Items**: COUNT
- 🔄 **Processing**: COUNT
- ✅ **Completed**: COUNT

## Recent Activity
- Last processed: FILE_NAME at TIMESTAMP
- Next check: TIMESTAMP

## Quick Stats
- Total processed today: COUNT
- Success rate: PERCENTAGE
```

### Company Handbook Format (Company_Handbook.md)
```markdown
# Company Handbook

## Processing Rules

### Rule 1: [Rule Name]
- **Condition**: When [condition]
- **Action**: [action to take]
- **Priority**: [number]

### Rule 2: [Rule Name]
- **Condition**: When [condition]
- **Action**: [action to take]
- **Priority**: [number]
```

## Validation Requirements

### Input Validation
- Action item files must have valid YAML frontmatter
- Required fields (id, title, status) must be present
- File extensions must be .md
- File content must be valid Markdown

### Processing Validation
- Items must transition through states in order
- Processing must complete before moving to next state
- Errors must be logged but not halt entire system

### Output Validation
- Dashboard must be updated atomically
- Counters must remain consistent
- File operations must be atomic to prevent corruption