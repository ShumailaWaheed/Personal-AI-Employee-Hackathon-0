# Health Check Monitor

HTTP health endpoint for cloud deployment monitoring via GCP Uptime Checks.

## Description
This skill provides a lightweight HTTP health check server (`deploy/health_check.py`) that runs on the cloud GCP e2-micro instance. It exposes two endpoints: `/health` (full JSON status report) and `/ready` (simple 200 OK). The server uses Python stdlib only (no Flask) to minimize RAM usage (~25MB). It reports PM2 process status, disk usage, vault directory counts, and last processing timestamp. GCP Uptime Checks poll this endpoint to detect outages.

## When to Use
- Automatically started as part of cloud PM2 ecosystem (`health-server` process)
- GCP Uptime Checks poll `/health` every 30 seconds
- Manual debugging: `curl http://EXTERNAL_IP:8080/health`
- Monitoring system health from external dashboards

## Inputs
- `HEALTH_PORT` environment variable (default: `8080`)
- `VAULT_PATH` environment variable for vault directory stats
- PM2 process list via `pm2 jlist` command
- Filesystem disk usage via `shutil.disk_usage('/')`
- Audit log files from `AI_Employee_Vault/Logs/*.json`

## Outputs
- HTTP responses on port 8080:
  - `GET /health` — Full JSON health report (200 or 503)
  - `GET /ready` — Simple `OK` text (200)
  - Other paths — 404

## Approval Required
- **No** — read-only monitoring, no actions taken

## MCP Servers Used
- None

## Endpoints

### GET /health (or GET /)
Returns full health report as JSON.

**Response 200 (healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-19T09:00:00+00:00",
  "uptime_seconds": 86400,
  "deployment_mode": "cloud",
  "processes": {
    "main-processor": {
      "status": "online",
      "restarts": 0,
      "uptime": 1708300000000
    },
    "file-system-watcher": {
      "status": "online",
      "restarts": 1,
      "uptime": 1708300000000
    },
    "gmail-watcher": {
      "status": "online",
      "restarts": 0,
      "uptime": 1708300000000
    },
    "linkedin-watcher": {
      "status": "online",
      "restarts": 0,
      "uptime": 1708300000000
    },
    "health-server": {
      "status": "online",
      "restarts": 0,
      "uptime": 1708300000000
    }
  },
  "disk": {
    "total_gb": 30.0,
    "used_gb": 8.5,
    "free_gb": 21.5,
    "used_pct": 28.3
  },
  "vault": {
    "inbox": 0,
    "needs_action": 3,
    "done": 42,
    "pending_approval": 2
  },
  "last_processed": "2026-02-19T08:55:00",
  "unhealthy": []
}
```

**Response 503 (degraded):**
Same JSON but `status: "degraded"` and `unhealthy` lists process names not in `online` or `launching` state.

### GET /ready
Simple readiness probe:
- Response: `200 OK` with body `OK`
- Used for quick liveness checks

## Health Status Logic
```
processes = pm2 jlist
unhealthy = [p for p in processes if p.status not in ('online', 'launching')]

if no unhealthy processes → status: "healthy" (200)
if any unhealthy process  → status: "degraded" (503)
```

## Data Sources

### PM2 Process Status
Runs `pm2 jlist` (JSON output, 5s timeout) to get:
- Process name, status (`online`, `stopped`, `errored`)
- Restart count
- Uptime timestamp

### Disk Usage
Uses `shutil.disk_usage('/')`:
- Total, used, free in GB
- Used percentage

### Vault Stats
Counts `.md` files in key directories:
- `Inbox/` — new incoming tasks
- `Needs_Action/` — pending processing
- `Done/` — completed tasks
- `Pending_Approval/` — awaiting human review

### Last Processing
Reads the most recent entry from the latest `Logs/*.json` file and returns its timestamp.

## PM2 Configuration
In `ecosystem.cloud.config.js`:
```javascript
{
  name: 'health-server',
  script: './deploy/health_check.py',
  interpreter: 'python3',
  autorestart: true,
  max_restarts: 10,
  restart_delay: 3000,
  env: {
    HEALTH_PORT: '8080'
  }
}
```

## Docker Health Check
In `Dockerfile`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

## GCP Uptime Check Setup
1. Target: `http://EXTERNAL_IP:8080/health`
2. Check interval: 60 seconds
3. Timeout: 10 seconds
4. Alert on: 2 consecutive failures

## Firewall Rules
Port 8080 open ONLY to GCP health checker IPs:
- `130.211.0.0/22`
- `35.191.0.0/16`

No public access to health endpoint.

## Server Implementation Details
- Uses `http.server.BaseHTTPRequestHandler` (stdlib)
- Binds to `0.0.0.0:HEALTH_PORT`
- Per-request logging suppressed (`log_message` overridden)
- Uptime tracked from `START_TIME = time.time()` at server start
- Timestamps in UTC via `datetime.now(timezone.utc)`

## Code Reference
- `deploy/health_check.py` — `HealthHandler` class, `get_pm2_status()`, `get_disk_usage()`, `get_vault_stats()`, `get_last_log_entry()`
- `ecosystem.cloud.config.js` — `health-server` PM2 process entry
- `Dockerfile` — `HEALTHCHECK` directive, `EXPOSE 8080`
- `src/config/settings.py` — `HEALTH_PORT` config key

## Quality Criteria
- Server uses ~25MB RAM (stdlib only, no Flask)
- Responds within 10 seconds (GCP timeout)
- Correctly detects degraded processes (errored/stopped)
- Disk usage accurately reported
- Vault stats match actual file counts
- Server auto-restarts via PM2 if it crashes
- Request logging suppressed to avoid log bloat

## Related Skills
- `cloud-local-routing` — Determines which processes run where
- `update-dashboard` — Dashboard shows similar vault stats but in Markdown
- `vault-git-sync` — Vault files must be synced for accurate stats
