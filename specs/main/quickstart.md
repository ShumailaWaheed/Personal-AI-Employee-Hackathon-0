# Quickstart Guide: Bronze-tier Personal AI Employee

## Prerequisites

- Python 3.13+ installed on your system
- Obsidian installed (optional, for vault management)
- Claude Code environment set up
- Basic understanding of file system operations

## Setup Instructions

### 1. Clone and Install Dependencies
```bash
# Navigate to your project directory
cd personal-ai-employee

# Install Python dependencies
pip install watchdog python-dotenv pathlib
```

### 2. Configure Environment Variables
Create a `.env` file in the project root with the following content:

```env
VAULT_PATH=./AI_Employee_Vault
CHECK_INTERVAL=60
LOG_LEVEL=INFO
DRY_RUN=false
```

### 3. Set Up Vault Structure
Create the required vault directories:

```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done}
```

### 4. Create Initial Configuration Files
Create the following files in your vault:

**AI_Employee_Vault/Dashboard.md**:
```markdown
# AI Employee Dashboard

**Generated at**: 2026-01-28T00:00:00Z

## Status Overview
- 📥 **New Items**: 0
- 🔄 **Processing**: 0
- ✅ **Completed**: 0

## Recent Activity
- Last processed: None
- Next check: 2026-01-28T00:00:00Z
```

**AI_Employee_Vault/Company_Handbook.md**:
```markdown
# Company Handbook

## Processing Rules

### Rule 1: Default Processing
- **Condition**: When any item enters Needs_Action
- **Action**: Process and move to Done
- **Priority**: 1
```

## Running the AI Employee

### 1. Start the File System Watcher
```bash
cd src
python main.py
```

### 2. Add Items to Process
Place any Markdown file in the `AI_Employee_Vault/Inbox` directory:

```bash
echo "# Test Task
Process this test task" > AI_Employee_Vault/Inbox/test_task.md
```

### 3. Monitor Processing
- Watch the console output for processing logs
- Observe the file moving from `Inbox` → `Needs_Action` → `Done`
- Check `Dashboard.md` for updated counts

## Configuration Options

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| VAULT_PATH | Path to the Obsidian vault | ./AI_Employee_Vault |
| CHECK_INTERVAL | Interval between checks (seconds) | 60 |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| DRY_RUN | Enable dry-run mode | false |

### File Extensions to Monitor
By default, the watcher monitors `.md` files. You can modify this in the configuration.

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Ensure the vault directory is writable
   - Check that Python has access to the directory

2. **Files Not Being Detected**
   - Verify the vault path in `.env` is correct
   - Check that files have `.md` extension
   - Ensure the watcher is running

3. **Dashboard Not Updating**
   - Confirm the `Dashboard.md` file exists
   - Check that the application has write permissions

### Debugging Steps
1. Run with `LOG_LEVEL=DEBUG` for detailed output
2. Verify all required directories exist
3. Check `.env` file for correct configuration
4. Ensure Claude Code agent skills are properly configured

## Example Workflow

1. **Add a new task**:
   ```bash
   echo "# Schedule Meeting
   Schedule a meeting with the team for project review." > AI_Employee_Vault/Inbox/meeting_task.md
   ```

2. **Monitor the process**:
   - File appears in `Inbox`
   - Watcher detects and moves to `Needs_Action`
   - Claude Code processes the file
   - File moves to `Done`
   - Dashboard updates with new counts

3. **Verify completion**:
   - Check `AI_Employee_Vault/Done/meeting_task.md` exists
   - Confirm `Dashboard.md` reflects updated counts

## Next Steps

Once the basic setup is working:

1. Customize `Company_Handbook.md` with your specific processing rules
2. Add more sophisticated action items to test processing
3. Monitor the dashboard for performance metrics
4. Extend with additional watcher types (Silver tier)

## Support

For issues with the Bronze-tier Personal AI Employee:

- Check the [implementation plan](./plan.md) for detailed architecture
- Review the [data model](./data-model.md) for file format specifications
- Consult the [constitution](../../.specify/memory/constitution.md) for compliance requirements