# MCP Server Contracts: Gold Tier

**Feature Branch**: `004-gold-tier`
**Protocol**: JSON-RPC 2.0 over stdio
**Created**: 2026-02-08

## Contract Format

All MCP servers follow the existing pattern from `mcp/email_server.py`:
- Read JSON-RPC request from stdin
- Process the request
- Write JSON-RPC response to stdout
- Exit after processing (stateless per invocation)

Request format:
```json
{"jsonrpc": "2.0", "method": "method_name", "params": {...}, "id": 1}
```

Success response:
```json
{"jsonrpc": "2.0", "result": {...}, "id": 1}
```

Error response:
```json
{"jsonrpc": "2.0", "error": {"code": -32001, "message": "Error description"}, "id": 1}
```

---

## Existing: Email MCP Server (`mcp/email_server.py`)

No changes required. Already implements:

| Method | Params | Returns |
| ------ | ------ | ------- |
| `send_email` | `{to, subject, body, cc?, bcc?, attachments?}` | `{message_id, status}` |
| `validate_recipients` | `{recipients: []}` | `{valid: [], invalid: []}` |
| `get_account_info` | `{}` | `{email, provider, rate_limit}` |
| `ping` | `{}` | `{status: "ok", timestamp}` |

---

## New: Odoo Accounting MCP Server (`mcp/odoo_server.py`)

**Purpose**: Expense recording and invoice creation via Odoo XML-RPC API.

**Environment Variables**:
- `ODOO_URL`: Odoo instance URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: Login username
- `ODOO_API_KEY`: API key for authentication

### Methods

| Method | Params | Returns | Error Codes |
| ------ | ------ | ------- | ----------- |
| `create_expense` | `{description, amount, currency, category?, date?, notes?}` | `{expense_id, status: "created"}` | -32001 (auth), -32010 (validation) |
| `create_invoice` | `{partner_name, lines: [{description, quantity, unit_price}], due_date?, notes?}` | `{invoice_id, status: "draft", total}` | -32001 (auth), -32010 (validation), -32011 (partner not found) |
| `get_financial_summary` | `{period: "week"\|"month"\|"quarter", date?}` | `{total_expenses, total_invoices, outstanding, period}` | -32001 (auth) |
| `ping` | `{}` | `{status: "ok", odoo_version, timestamp}` | -32001 (auth) |

### Error Codes
- `-32001`: Authentication failure (invalid credentials or expired API key)
- `-32010`: Validation error (missing required fields, invalid amounts)
- `-32011`: Reference not found (partner, category, etc.)

---

## New: Facebook MCP Server (`mcp/facebook_server.py`)

**Purpose**: Post posts and collect engagement metrics via Facebook API v2.

**Environment Variables**:
- `FACEBOOK_BEARER_TOKEN`: OAuth 2.0 Bearer token
- `FACEBOOK_API_KEY`: API key
- `FACEBOOK_API_SECRET`: API secret

### Methods

| Method | Params | Returns | Error Codes |
| ------ | ------ | ------- | ----------- |
| `post_post` | `{text, reply_to_id?}` | `{post_id, url, status: "posted"}` | -32001 (auth), -32020 (rate limit), -32021 (content policy) |
| `get_engagement_metrics` | `{post_id}` | `{likes, reposts, replies, impressions, timestamp}` | -32001 (auth), -32022 (post not found) |
| `ping` | `{}` | `{status: "ok", rate_limit_remaining, timestamp}` | -32001 (auth) |

### Error Codes
- `-32001`: Authentication failure
- `-32020`: Rate limit exceeded (include `retry_after` in error data)
- `-32021`: Content policy violation
- `-32022`: Resource not found

---

## New: LinkedIn MCP Server (`mcp/linkedin_server.py`)

**Purpose**: Create posts and collect engagement metrics via LinkedIn API v2.

**Environment Variables**:
- `LINKEDIN_ACCESS_TOKEN`: OAuth 2.0 access token
- `LINKEDIN_PERSONAL_ACCOUNT_ID`: User URN for posting

### Methods

| Method | Params | Returns | Error Codes |
| ------ | ------ | ------- | ----------- |
| `create_post` | `{text, visibility?: "PUBLIC"\|"CONNECTIONS"}` | `{post_id, url, status: "posted"}` | -32001 (auth), -32020 (rate limit) |
| `get_post_metrics` | `{post_id}` | `{likes, comments, shares, impressions, timestamp}` | -32001 (auth), -32022 (post not found) |
| `ping` | `{}` | `{status: "ok", timestamp}` | -32001 (auth) |

### Error Codes
- `-32001`: Authentication failure (token expired)
- `-32020`: Rate limit exceeded
- `-32022`: Resource not found

---

## New: WhatsApp MCP Server (`mcp/whatsapp_server.py`)

**Purpose**: Send messages via WhatsApp Business API or Playwright session.

**Environment Variables**:
- `WHATSAPP_API_TOKEN`: Business API token (if using API mode)
- `WHATSAPP_MODE`: "api" or "playwright" (default: "playwright")
- `WHATSAPP_USER_DATA_DIR`: Playwright session directory (if playwright mode)

### Methods

| Method | Params | Returns | Error Codes |
| ------ | ------ | ------- | ----------- |
| `send_message` | `{to, message, media_url?}` | `{message_id, status: "sent"}` | -32001 (auth), -32030 (recipient invalid), -32031 (session expired) |
| `get_message_status` | `{message_id}` | `{status: "sent"\|"delivered"\|"read", timestamp}` | -32001 (auth), -32022 (not found) |
| `ping` | `{}` | `{status: "ok", mode, timestamp}` | -32001 (auth), -32031 (session expired) |

### Error Codes
- `-32001`: Authentication failure
- `-32030`: Invalid recipient number
- `-32031`: WhatsApp session expired (requires re-login)
- `-32022`: Resource not found

---

## Shared Error Handling Contract

All MCP servers MUST:
1. Return valid JSON-RPC 2.0 responses (success or error)
2. Never throw unhandled exceptions to stdout
3. Include `timestamp` in all successful responses
4. Include descriptive `message` in all error responses
5. Use error code `-32001` consistently for authentication failures
6. Support `ping` method for health checking
7. Respect `DRY_RUN` environment variable (log but don't execute)

## MCPClient Extension

The existing `src/utils/mcp_client.py` MCPClient class needs extension to support new servers:

```
New methods:
- create_expense(params) → dict
- create_invoice(params) → dict
- get_financial_summary(params) → dict
- post_post(params) → dict
- get_post_metrics(params) → dict
- create_linkedin_post(params) → dict
- get_linkedin_metrics(params) → dict
- send_whatsapp(params) → dict
- ping_server(server_name) → dict
```

Server routing: MCPClient determines which subprocess to spawn based on `mcp_server` field in the approval request.
