# API Contract: Bronze-tier Personal AI Employee

## Overview

This document defines the API contracts for the Bronze-tier Personal AI Employee system. The system operates primarily through file-based interactions within the Obsidian vault, with programmatic interfaces for monitoring and control.

## File System Event API

### Watcher Interface
```
Interface: BaseWatcher
```

#### Methods

**check_for_updates()**
- **Description**: Checks the vault for new or changed files
- **Input**: None
- **Output**: Array of file paths that have been modified/added
- **Error Conditions**: Permission denied, directory not found, I/O errors

**create_action_file(item)**
- **Description**: Creates an action file in the Needs_Action directory
- **Input**:
  - item: Object with path and metadata
- **Output**: Path to created action file
- **Error Conditions**: Write permissions, disk space, invalid file format

**run()**
- **Description**: Starts the continuous monitoring loop
- **Input**: None
- **Output**: Continuous monitoring with periodic checks
- **Error Conditions**: Cannot start monitoring thread

### Vault Operations API

**move_file(source_path, destination_dir)**
- **Description**: Moves a file from source to destination directory
- **Input**:
  - source_path: Path to source file
  - destination_dir: Destination directory path
- **Output**: Path to moved file
- **Error Conditions**: File not found, permission denied, disk space

**update_dashboard()**
- **Description**: Updates the Dashboard.md with current vault statistics
- **Input**: None
- **Output**: Boolean indicating success
- **Error Conditions**: Cannot read vault directories, cannot write dashboard

**get_vault_stats()**
- **Description**: Gets current statistics for all vault directories
- **Input**: None
- **Output**: Object with counts for each directory
```
{
  "inbox_count": 0,
  "needs_action_count": 0,
  "done_count": 0,
  "last_updated": "2026-01-28T10:30:00Z"
}
```

## Configuration API

**load_config()**
- **Description**: Loads configuration from environment variables and .env file
- **Input**: None
- **Output**: Configuration object with all settings
```
{
  "vault_path": "./AI_Employee_Vault",
  "check_interval": 60,
  "log_level": "INFO",
  "dry_run": false
}
```

**validate_config(config)**
- **Description**: Validates the configuration settings
- **Input**: Configuration object
- **Output**: Boolean indicating validity and array of validation errors

## Processing API

**process_action_item(file_path)**
- **Description**: Processes an action item using Claude Code agent skills
- **Input**: Path to action item file
- **Output**: Processing result with success status
```
{
  "success": true,
  "processed_file": "/path/to/done/file.md",
  "duration_ms": 1250
}
```

## Event Definitions

### File System Events
```
{
  "event_type": "file_created|file_modified|file_moved",
  "path": "/absolute/path/to/file.md",
  "timestamp": "2026-01-28T10:30:00Z",
  "directory_type": "inbox|needs_action|done"
}
```

### Processing Events
```
{
  "event_type": "processing_started|processing_completed|processing_failed",
  "file_path": "/path/to/file.md",
  "timestamp": "2026-01-28T10:30:00Z",
  "duration_ms": 1250
}
```

### Dashboard Update Events
```
{
  "event_type": "dashboard_updated",
  "timestamp": "2026-01-28T10:30:00Z",
  "stats": {
    "inbox_count": 0,
    "needs_action_count": 0,
    "done_count": 5
  }
}
```

## Error Response Format
```
{
  "error": {
    "code": "FILE_NOT_FOUND|PERMISSION_DENIED|INVALID_CONFIG|PROCESSING_FAILED",
    "message": "Descriptive error message",
    "details": "Additional error details",
    "timestamp": "2026-01-28T10:30:00Z"
  }
}
```

## Validation Rules

### Input Validation
- All file paths must be within the vault directory
- File extensions must be .md for action items
- Configuration values must be within acceptable ranges
- Directory permissions must allow read/write operations

### Output Validation
- Dashboard updates must produce valid Markdown
- File operations must preserve original content
- Statistics must be non-negative integers
- Timestamps must be in ISO 8601 format

## Performance Guarantees

### Response Times
- File detection: < 1 second after file creation
- Dashboard update: < 500ms
- Processing initiation: < 100ms

### Reliability
- System should handle up to 100 files per hour
- 99% uptime during operational hours
- Graceful degradation when individual files fail processing