# Secret Management

Load credentials from GCP Secret Manager on cloud or `.env` file on local.

## Description
This skill manages how credentials and sensitive configuration are loaded depending on the deployment mode. On cloud (GCP), secrets are stored in GCP Secret Manager and loaded at runtime via `deploy/load_secrets.sh` — the `.env` file is never stored on disk permanently. On local (Windows), the standard `.env` file is used with `python-dotenv`. This ensures credentials are never committed to Git and follow the principle of least privilege.

## When to Use
- During GCP instance bootstrap (`deploy/setup_gcp.sh` calls `load_secrets.sh`)
- When starting the application on cloud (secrets loaded before PM2 starts)
- When rotating credentials on cloud (re-run `load_secrets.sh`)
- When setting up a new local development environment (copy `.env.example` to `.env`)

## Inputs
- `GCP_PROJECT_ID` environment variable (cloud only)
- `GCP_SECRET_NAME` environment variable (default: `ai-employee-env`)
- `.env.example` template file
- GCP Secret Manager secret containing all env vars

## Outputs
- On cloud: `/app/.env.runtime` file created from Secret Manager, symlinked as `/app/.env`
- On local: `.env` file read directly by `python-dotenv`
- `chmod 600` on `.env.runtime` (owner-read-only)

## Approval Required
- **No** — infrastructure credential loading, not an action

## MCP Servers Used
- None (this is a prerequisite for MCP servers to function)

## Cloud Flow: `deploy/load_secrets.sh`

### Steps:
1. Read `GCP_SECRET_NAME` (default: `ai-employee-env`) and `GCP_PROJECT_ID`
2. If `GCP_PROJECT_ID` is not set:
   - Falls back to local `.env` file
   - If `/app/.env` exists, uses it
   - If not, warns to copy `.env.example`
   - Exits gracefully (non-fatal)
3. If `GCP_PROJECT_ID` is set:
   - Runs `gcloud secrets versions access latest --secret=SECRET_NAME --project=PROJECT_ID`
   - Writes output to `/app/.env.runtime`
   - Sets `chmod 600` (owner-read-only permissions)
   - Creates symlink: `/app/.env` → `/app/.env.runtime`
   - `python-dotenv` picks up the symlinked `.env` automatically

### Prerequisites:
- `gcloud` CLI installed on the GCP instance
- Instance IAM role: **Secret Manager Secret Accessor**
- Secret created in GCP Secret Manager with all env vars

## Local Flow
1. Copy `.env.example` to `.env`
2. Fill in values manually
3. `python-dotenv` loads `.env` via `src/config/settings.py`:
   ```python
   env_path = Path('.') / '.env'
   if env_path.exists():
       load_dotenv(env_path)
   ```

## Secret Contents
The GCP secret (or `.env` file) contains all credentials:

### Core
```
VAULT_PATH, CHECK_INTERVAL, LOG_LEVEL, DRY_RUN, PROCESSING_INTERVAL
DEPLOYMENT_MODE=cloud
```

### Email
```
EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_SMTP_USERNAME
EMAIL_SMTP_PASSWORD, EMAIL_FROM_ADDRESS, EMAIL_RATE_LIMIT_PER_DAY
```

### Social Media
```
LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSONAL_ACCOUNT_ID
FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID
TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID
WHATSAPP_API_TOKEN
```

### Business
```
ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY
```

### Gold Tier
```
GOLD_TIER_ENABLED, AUTO_APPROVE_LOW_RISK
AUDIT_SCHEDULE, BRIEFING_SCHEDULE
```

### Platinum Tier
```
GCP_PROJECT_ID, GCP_SECRET_NAME
VAULT_REPO, HEALTH_PORT
```

## Security Design

### What is protected:
| Item | Protection |
|------|-----------|
| API keys & tokens | In Secret Manager (cloud) or `.env` (local, gitignored) |
| SMTP passwords | Never in code, loaded at runtime |
| OAuth tokens (`gmail_token.json`) | Generated locally, uploaded to cloud manually |
| Browser sessions | In `.gitignore`, never committed |
| `.env` file | In `.gitignore`, never committed |

### Infrastructure security:
| Control | Implementation |
|---------|---------------|
| SSH-only access | No password auth on GCP instance |
| Firewall | Only port 8080 open, only to GCP health checker IPs (`130.211.0.0/22`, `35.191.0.0/16`) |
| IAM | Instance has only Secret Manager Secret Accessor role |
| Git vault repo | Private repo with SSH deploy key |
| File permissions | `.env.runtime` is `chmod 600` |

### What NEVER gets committed:
Listed in `.gitignore`:
- `.env`, `.env.runtime` — credentials
- `gmail_token.json`, `credentials.json` — OAuth tokens
- `twitter_session/`, `*_session/` — browser sessions
- `venv/`, `__pycache__/` — runtime artifacts

## GCP Setup in `deploy/setup_gcp.sh`
Load secrets step (step 8 of 11):
```bash
if [ -f /app/deploy/load_secrets.sh ]; then
    bash /app/deploy/load_secrets.sh
fi
```
This runs during initial GCP instance bootstrap, before PM2 starts.

## Credential Rotation
To rotate credentials on cloud:
1. Update the secret in GCP Secret Manager console
2. SSH into the instance
3. Run: `bash /app/deploy/load_secrets.sh`
4. Restart PM2: `pm2 restart all`

## Code Reference
- `deploy/load_secrets.sh` — GCP Secret Manager loader script
- `deploy/setup_gcp.sh` — calls `load_secrets.sh` during bootstrap (line 41-43)
- `src/config/settings.py` — `load_config()` reads `.env` via `python-dotenv`
- `.env.example` — template with all required environment variables
- `.gitignore` — ensures credentials are never committed

## Quality Criteria
- Cloud: secrets loaded from GCP Secret Manager, not stored in code/Git
- Local: `.env` file gitignored, never committed
- `.env.runtime` has `chmod 600` (owner-read-only)
- Graceful fallback when `GCP_PROJECT_ID` is not set
- `load_secrets.sh` is idempotent (safe to run multiple times)
- Symlink approach lets `python-dotenv` work unchanged
- All credential keys documented in `.env.example`

## Related Skills
- `cloud-local-routing` — Uses loaded config to determine deployment mode
- `health-check-monitor` — Depends on loaded config for `HEALTH_PORT`
- `vault-git-sync` — Needs Git credentials for push/pull
- `send-email-mcp` — Needs SMTP credentials loaded by this skill
