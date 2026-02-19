# Implementation Plan: Platinum Tier — Cloud + Local Hybrid Deployment

**Branch**: `005-platinum-tier` | **Date**: 2026-02-18 | **Target**: Google Cloud Free Tier (e2-micro)
**Input**: Constitution v3.0.0 Platinum requirements + check.md

## Summary

Deploy the Personal AI Employee as a 24/7 cloud+local hybrid system on Google Cloud Free Tier (e2-micro: 0.25 vCPU, 1GB RAM, 30GB disk). Cloud handles lightweight watchers (Gmail, LinkedIn, FileSystem) and all processors. Local machine handles Playwright-based services (WhatsApp, Twitter, Instagram). Vault syncs between cloud and local via Git.

## Architecture: Cloud vs Local Split

### Why Split?
- e2-micro has **only 1GB RAM** — Playwright browsers use 200-500MB each
- Edge browser (`channel='msedge'`) not available on Linux
- WhatsApp/Twitter/Instagram require persistent browser sessions with display

### Cloud (GCP e2-micro) — Always-On 24/7
| Process | RAM Est. | Notes |
|---------|----------|-------|
| main-processor (Gold) | ~80MB | Core processing loop |
| file-system-watcher | ~50MB | Watches Inbox/ for new tasks |
| gmail-watcher | ~60MB | Gmail API polling every 120s |
| linkedin-watcher | ~60MB | LinkedIn API polling every 300s |
| health-check server | ~25MB | HTTP /health endpoint on :8080 |
| PM2 daemon | ~60MB | Process manager |
| OS + kernel | ~200MB | Debian slim |
| MCP subprocesses (peak) | ~50MB | Short-lived, per-request |
| **Total** | **~585MB** | **415MB headroom** |

Available MCP servers on cloud: email, linkedin, facebook, odoo (all API-only)

### Local (Windows) — On-Demand
| Process | Notes |
|---------|-------|
| whatsapp-watcher | Playwright + Chromium persistent session |
| twitter MCP (on-demand) | Playwright + Edge, invoked per-request |
| instagram MCP (on-demand) | Playwright + Edge, invoked per-request |

---

## Platinum Requirements Mapping

| Requirement | Solution |
|-------------|----------|
| Cloud 24/7 deployment | GCP e2-micro + PM2 + Docker |
| Local + Cloud separation | `DEPLOYMENT_MODE` env var + split ecosystem configs |
| Git vault sync | Cron-based bidirectional git sync (cloud ↔ local) |
| Security isolation | GCP Secret Manager + SSH-only + firewall rules |
| Health monitoring | stdlib HTTP server + GCP Uptime Check + PM2 auto-restart |

---

## Files to Create (14 new files)

### 1. Packaging & Dependencies
| File | Purpose |
|------|---------|
| `requirements.txt` | Cloud Python deps (no Playwright/Pillow) |
| `requirements-local.txt` | Local deps (extends cloud + Playwright + Pillow) |

### 2. Deployment Configuration
| File | Purpose |
|------|---------|
| `ecosystem.cloud.config.js` | PM2 config: 5 cloud processes (processor, 3 watchers, health) |
| `ecosystem.local.config.js` | PM2 config: local Playwright processes only |
| `Dockerfile` | python:3.13-slim + Node.js + PM2, ~585MB RAM budget |

### 3. Source Code
| File | Purpose |
|------|---------|
| `src/config/deployment.py` | `is_cloud()`, `is_local()`, enabled watchers/servers helpers |

### 4. Deploy Scripts
| File | Purpose |
|------|---------|
| `deploy/health_check.py` | stdlib HTTP health endpoint (:8080), no Flask |
| `deploy/sync_vault.sh` | Cloud-side vault git sync (cron every 5 min) |
| `deploy/local_vault_sync.sh` | Local Windows vault git sync |
| `deploy/init_vault_repo.sh` | One-time vault git repo initialization |
| `deploy/setup_gcp.sh` | One-time GCP instance bootstrap (Python, Node, PM2) |
| `deploy/load_secrets.sh` | GCP Secret Manager → .env loader |

### 5. Config Updates
| File | Purpose |
|------|---------|
| `.gitignore` | Add secrets, sessions, venv exclusions |

---

## Files to Modify (3 existing files)

| File | Change |
|------|--------|
| `src/config/settings.py` | Add `DEPLOYMENT_MODE` + auto-set MCP modes to `api` on cloud |
| `src/utils/mcp_client.py` | Use `python3` on Linux; guard unavailable servers in cloud mode |
| `.env.example` | Add cloud deployment env vars |

---

## Implementation Order (12 Steps)

### Step 1: .gitignore update
Add secrets, sessions, venv, runtime files exclusions. Prevents accidental secret commits.

### Step 2: requirements.txt + requirements-local.txt
Cloud deps (no Playwright). Local deps extends cloud + adds Playwright/Pillow.

### Step 3: src/config/deployment.py (NEW)
Cloud/local detection helpers: `is_cloud()`, `get_enabled_watchers()`, `get_enabled_mcp_servers()`.

### Step 4: src/config/settings.py (MODIFY)
Add `DEPLOYMENT_MODE` config key. Auto-set `WHATSAPP_MODE`, `TWITTER_MODE`, `INSTAGRAM_MODE` to `api` when `DEPLOYMENT_MODE=cloud`.

### Step 5: src/utils/mcp_client.py (MODIFY)
- Use `python3` on Linux (`os.name != 'nt'`)
- Guard `_call_server()` to skip unavailable servers in cloud mode

### Step 6: ecosystem.cloud.config.js + ecosystem.local.config.js (NEW)
Split PM2 configs. Cloud: 5 processes with `python3` interpreter. Local: whatsapp-watcher only.

### Step 7: deploy/health_check.py (NEW)
Stdlib `http.server` on port 8080. Reports PM2 process status, disk usage, vault stats, last processing time. ~25MB RAM.

### Step 8: deploy/sync_vault.sh + deploy/local_vault_sync.sh (NEW)
Git-based vault sync. Cloud owns `Done/`, `Plans/`, `Logs/`, `Briefings/`. Local owns `Inbox/`, `Needs_Action/`. Cron every 5 minutes.

### Step 9: deploy/init_vault_repo.sh (NEW)
One-time vault git initialization with .gitignore.

### Step 10: deploy/setup_gcp.sh + deploy/load_secrets.sh (NEW)
GCP instance bootstrap: Python 3.13, Node.js, PM2, git, venv, cron setup. Secret Manager integration.

### Step 11: Dockerfile (NEW)
`python:3.13-slim`, install Node.js + PM2, copy app code, `pm2-runtime ecosystem.cloud.config.js`.

### Step 12: Deploy & Configure
- Create GCP e2-micro instance
- Upload secrets to Secret Manager
- Init vault git repo
- Start PM2 with cloud config
- Configure GCP Uptime Check on :8080/health
- Set firewall: only GCP health checker IPs on port 8080

---

## Git Vault Sync Strategy

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

**Conflict Resolution:**
- Cloud NEVER writes to `Inbox/` or `Needs_Action/` → no conflicts
- Local NEVER writes to `Done/`, `Plans/`, `Logs/` → no conflicts
- `Dashboard.md` → cloud regenerates it, cloud wins

---

## Security Design

1. **No .env on cloud** — secrets loaded from GCP Secret Manager at runtime
2. **SSH-only access** — no password auth, key-based SSH
3. **Firewall** — only port 8080 open, only to GCP health checker IPs (130.211.0.0/22, 35.191.0.0/16)
4. **Git vault repo** — private repo, SSH deploy key
5. **Browser sessions** — never committed (in .gitignore)

---

## Known Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Gmail OAuth needs browser for first token | Generate `gmail_token.json` locally, upload to cloud. Auto-refreshes after that. |
| e2-micro CPU throttling (0.25 vCPU) | All operations are I/O-bound (API calls, file reads). CPU is not a bottleneck. |
| Twitter/Instagram need Playwright | Stay on local machine. Cloud returns "server not available" gracefully. |
| Vault merge conflicts | Strict ownership split: local owns Inbox, cloud owns Done. No overlap. |
| PM2 needs Node.js + Python both | Dockerfile installs both. ~100MB overhead total. |
