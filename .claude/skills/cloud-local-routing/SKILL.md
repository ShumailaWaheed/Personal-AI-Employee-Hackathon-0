# Cloud-Local Routing

Route watchers and MCP servers between cloud (GCP e2-micro) and local (Windows) based on deployment mode.

## Description
This skill manages the Platinum tier's hybrid architecture where the system runs split across two environments: a GCP e2-micro cloud instance (always-on, 24/7, lightweight API-only services) and a local Windows machine (on-demand, Playwright-based browser services). The `DEPLOYMENT_MODE` environment variable (`cloud` or `local`) determines which watchers and MCP servers are available. Browser-based services (WhatsApp, Twitter, Instagram) require Playwright and only run locally. API-based services (Email, LinkedIn, Facebook, Odoo) run on cloud.

## When to Use
- When starting the AI Employee system to determine which services to enable
- When an MCP call is made to check if the target server is available in the current mode
- When configuring watchers at startup
- When debugging why a specific service is unavailable

## Inputs
- `DEPLOYMENT_MODE` environment variable: `cloud` or `local` (default: `local`)
- MCP server name being requested

## Outputs
- `is_cloud() -> bool` — true if running on GCP
- `is_local() -> bool` — true if running on Windows
- `get_enabled_watchers() -> list[str]` — watchers available in current mode
- `get_enabled_mcp_servers() -> list[str]` — MCP servers available in current mode
- Graceful error response when unavailable server is called in cloud mode

## Approval Required
- **No** — this is infrastructure routing, not an action

## MCP Servers Used
- Determines which MCP servers are available, doesn't call them directly

## Cloud vs Local Split

### Cloud (GCP e2-micro) — Always-On 24/7
| Process | RAM Est. | PM2 Name |
|---------|----------|----------|
| Gold processor (`src/main.py`) | ~80MB | `main-processor` |
| File system watcher | ~50MB | `file-system-watcher` |
| Gmail watcher | ~60MB | `gmail-watcher` |
| LinkedIn watcher | ~60MB | `linkedin-watcher` |
| Health check server | ~25MB | `health-server` |
| PM2 daemon | ~60MB | — |
| OS + kernel | ~200MB | — |
| MCP subprocesses (peak) | ~50MB | — |
| **Total** | **~585MB** | **415MB headroom on 1GB** |

Available MCP servers on cloud: `email`, `linkedin`, `facebook`, `odoo`

### Local (Windows) — On-Demand
| Process | Notes |
|---------|-------|
| WhatsApp watcher | Playwright + Chromium persistent session |
| Twitter MCP | Playwright + Edge, invoked per-request |
| Instagram MCP | Playwright + Edge, invoked per-request |

Available MCP servers on local: all cloud servers + `whatsapp`, `twitter`, `instagram`

### Why This Split?
- e2-micro has **only 1GB RAM** — Playwright browsers use 200-500MB each
- Edge browser (`channel='msedge'`) not available on Linux
- WhatsApp/Twitter/Instagram require persistent browser sessions with display

## Enabled Services by Mode

### `get_enabled_watchers()`
| Mode | Watchers |
|------|----------|
| `cloud` | `file_system`, `gmail`, `linkedin` |
| `local` | `file_system`, `gmail`, `linkedin`, `whatsapp` |

### `get_enabled_mcp_servers()`
| Mode | MCP Servers |
|------|-------------|
| `cloud` | `email`, `linkedin`, `facebook`, `odoo` |
| `local` | `email`, `linkedin`, `facebook`, `odoo`, `whatsapp`, `twitter`, `instagram` |

## MCP Client Guard
When `MCPClient._call_server()` is called, it checks `get_enabled_mcp_servers()` first. If the requested server is not available in the current deployment mode, it returns an error without attempting the call:

```json
{
  "error": {
    "code": -32000,
    "message": "Server 'twitter_mcp' not available in cloud mode. Playwright-based servers run locally only."
  }
}
```

This prevents crashes and allows the retry queue to handle it.

## Auto-Mode Override
In `src/config/settings.py`, when `DEPLOYMENT_MODE=cloud`:
- `WHATSAPP_MODE` is forced to `api` (no Playwright)
- This prevents any accidental Playwright imports on cloud

## PM2 Ecosystem Configs

### Cloud: `ecosystem.cloud.config.js`
5 processes, all using `python3` interpreter:
- `main-processor` — Gold tier processor with `GOLD_TIER_ENABLED=true`
- `file-system-watcher` — watches `Inbox/` for new tasks
- `gmail-watcher` — Gmail API polling
- `linkedin-watcher` — LinkedIn API polling
- `health-server` — HTTP health endpoint on port 8080

All processes: `autorestart: true`, `max_restarts: 10`, `restart_delay: 5000ms`

### Local: `ecosystem.config.js`
6 processes using `python` interpreter:
- `main-processor`, `file-system-watcher`, `gmail-watcher`, `linkedin-watcher`
- `whatsapp-watcher` — Playwright-based WhatsApp monitoring
- `gold-processor` — Gold tier enabled

## Docker Deployment
`Dockerfile` builds cloud image:
- Base: `python:3.13-slim`
- Installs: git, Node.js 20, PM2
- Uses `requirements.txt` (no Playwright deps)
- Creates full vault directory structure
- Sets `DEPLOYMENT_MODE=cloud`, `HEALTH_PORT=8080`
- Health check: `curl -f http://localhost:8080/health`
- Entry: `pm2-runtime ecosystem.cloud.config.js`

## Code Reference
- `src/config/deployment.py` — `is_cloud()`, `is_local()`, `get_enabled_watchers()`, `get_enabled_mcp_servers()`
- `src/config/settings.py` — `DEPLOYMENT_MODE` config, auto-mode override for WhatsApp
- `src/utils/mcp_client.py` — `_call_server()` guard checking `get_enabled_mcp_servers()`
- `ecosystem.cloud.config.js` — PM2 cloud process config (5 processes)
- `ecosystem.config.js` — PM2 local process config (6 processes)
- `Dockerfile` — Cloud container image

## Quality Criteria
- Cloud mode never attempts to start Playwright-based services
- Unavailable server requests return structured error (not crash)
- `is_cloud()` / `is_local()` correctly read `DEPLOYMENT_MODE` env var
- RAM stays within 1GB budget on e2-micro
- All PM2 processes have auto-restart enabled
- Docker health check correctly monitors the system

## Related Skills
- `health-check-monitor` — Monitors cloud process health
- `vault-git-sync` — Syncs vault between cloud and local
- `secret-management` — Loads credentials on cloud from GCP Secret Manager
