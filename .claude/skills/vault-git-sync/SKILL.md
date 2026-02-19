# Vault Git Sync

Bidirectional Git-based vault synchronization between cloud (GCP) and local (Windows) machines.

## Description
This skill manages the bidirectional sync of the Obsidian vault between the cloud GCP instance and the local Windows machine using Git. Each side has strict ownership of specific directories to prevent merge conflicts. Cloud owns processed output directories (`Done/`, `Plans/`, `Logs/`, `Briefings/`). Local owns input directories (`Inbox/`, `Needs_Action/`). Sync runs every 5 minutes via cron (cloud) and Windows Task Scheduler (local).

## When to Use
- Automatically every 5 minutes via cron/scheduler
- After initial deployment to set up vault Git repo
- When debugging sync issues between cloud and local
- When setting up a new cloud or local environment

## Inputs
- `VAULT_PATH` environment variable (cloud: `/app/AI_Employee_Vault`, local: `D:/Hachathon-0/personal-ai-employee/AI_Employee_Vault`)
- `VAULT_REPO` environment variable (e.g., `git@github.com:user/vault.git`)
- Git repository state

## Outputs
- Synchronized vault files across both environments
- Git commit history tracking all changes
- Sync log output (`/app/logs/vault-sync.log` on cloud)

## Approval Required
- **No** — sync is automatic background infrastructure

## MCP Servers Used
- None

## Directory Ownership

```
LOCAL (Windows/Obsidian)          CLOUD (GCP e2-micro)
┌──────────────────────┐          ┌──────────────────────┐
│ User drops task in   │ git push │ Cloud pulls new tasks │
│ Inbox/ or edits      │ ───────> │ from Inbox/           │
│ Needs_Action/        │          │                       │
│                      │ git pull │ Cloud writes results  │
│ User sees results in │ <─────── │ to Done/, Plans/,     │
│ Done/, Briefings/    │          │ Logs/, Briefings/     │
└──────────────────────┘          └──────────────────────┘
```

| Directory | Owner | Why |
|-----------|-------|-----|
| `Inbox/` | Local | User drops new tasks here via Obsidian |
| `Needs_Action/` | Local | User creates action items here |
| `Company_Handbook.md` | Local | User-edited configuration |
| `Business_Goals.md` | Local | User-edited configuration |
| `Done/` | Cloud | Processor moves completed tasks here |
| `Plans/` | Cloud | Processor generates plans here |
| `Logs/` | Cloud | Processor writes audit logs here |
| `Briefings/` | Cloud | Report generator writes here |
| `Business/` | Cloud | Accounting, social data here |
| `Dashboard.md` | Cloud | Processor regenerates this |
| `Pending_Approval/` | Both | Cloud creates, local moves to Approved/Rejected |
| `Approved/` | Local | Human moves approved items here |
| `Rejected/` | Local | Human moves rejected items here |

## Conflict Resolution
- Cloud NEVER writes to `Inbox/` or `Needs_Action/` → no conflicts
- Local NEVER writes to `Done/`, `Plans/`, `Logs/` → no conflicts
- `Dashboard.md` → cloud regenerates it, cloud wins on conflict
- On merge conflicts: cloud uses `--strategy-option=ours` (cloud wins)
- Local uses `--theirs` for `Done/`, `Plans/`, `Logs/`, `Briefings/`, `Business/` (cloud wins for processed files)

## Scripts

### 1. `deploy/init_vault_repo.sh` — One-Time Setup
Initializes the vault as a Git repository:
```bash
# Usage: VAULT_REPO=git@github.com:user/vault.git bash deploy/init_vault_repo.sh
```
Steps:
1. Checks if already initialized (skips if `.git/` exists)
2. Creates vault `.gitignore` (excludes `*.tmp`, `.DS_Store`, `__pycache__/`, `*.pyc`, `Thumbs.db`)
3. `git init` → `git remote add origin` → `git add -A` → commit → `git push -u origin main`

### 2. `deploy/sync_vault.sh` — Cloud Sync (Cron)
Runs every 5 minutes on cloud:
```bash
# Cron: */5 * * * * /app/deploy/sync_vault.sh >> /app/logs/vault-sync.log 2>&1
```
Steps:
1. If not a git repo yet, initializes and connects to `VAULT_REPO`
2. Stages all current changes (cloud-processed results)
3. Commits if there are changes: `cloud-sync: YYYY-MM-DD HH:MM:SS - processed updates`
4. Fetches remote changes from `origin main`
5. Checks out local's `Inbox/` and `Needs_Action/` from remote (local owns these)
6. Merges remaining changes with `--strategy-option=ours` (cloud wins conflicts)
7. Pushes cloud's processed results back
8. Logs with timestamp prefix: `[vault-sync YYYY-MM-DD HH:MM:SS]`
9. Non-fatal: fetch/push failures don't crash the script

### 3. `deploy/local_vault_sync.sh` — Local Sync (Windows)
Runs every 5 minutes via Windows Task Scheduler:
```bash
# Command: "C:\Program Files\Git\bin\bash.exe" --login -i "D:\...\deploy\local_vault_sync.sh"
```
Steps:
1. Checks vault is git-initialized (errors if not)
2. Fetches and merges cloud's processed results
3. On merge conflict: `git checkout --theirs` for `Done/`, `Plans/`, `Logs/`, `Briefings/`, `Business/` (cloud wins for processed files)
4. Stages local changes: `Inbox/`, `Needs_Action/`, `Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`
5. Commits if changes exist: `local-sync: YYYY-MM-DD HH:MM:SS - new tasks`
6. Pushes to `origin main`

## Setup in `deploy/setup_gcp.sh`
Cron is configured during GCP setup:
```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /app && /app/venv/bin/python -c 'pass' && /app/deploy/sync_vault.sh >> /app/logs/vault-sync.log 2>&1") | crontab -
```

## Environment Variables
```
VAULT_PATH=./AI_Employee_Vault        # or /app/AI_Employee_Vault on cloud
VAULT_REPO=git@github.com:user/vault.git  # Private repo, SSH deploy key
```

## Code Reference
- `deploy/init_vault_repo.sh` — one-time vault git initialization
- `deploy/sync_vault.sh` — cloud-side cron sync script
- `deploy/local_vault_sync.sh` — local Windows sync script
- `deploy/setup_gcp.sh` — sets up cron job for cloud sync (line 49)

## Quality Criteria
- No merge conflicts due to strict directory ownership
- Sync runs reliably every 5 minutes on both sides
- Fetch/push failures are non-fatal (logged, not crashed)
- New tasks from local appear on cloud within 5 minutes
- Processed results from cloud appear on local within 5 minutes
- `init_vault_repo.sh` is idempotent (safe to run multiple times)
- Cloud sync auto-initializes git if not already a repo
- Local sync errors clearly if vault not initialized

## Related Skills
- `cloud-local-routing` — Determines what runs where (cloud vs local)
- `health-check-monitor` — Vault stats depend on synced files
- `secret-management` — Git credentials needed for push/pull
