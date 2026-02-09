# Send Email via MCP

Execute email sending through the Email MCP server using JSON-RPC over stdio.

## Description
This skill sends emails securely through the Email MCP server. Credentials never leave the MCP server process - the main application only sends the request payload. This skill should ONLY be invoked after HITL approval has been granted (file moved to /Approved/).

## When to Use
- An approved email action exists in /Approved/
- The system needs to send a notification, response, or outreach email
- Email validation is needed before sending

## Inputs
- Approved action file from `AI_Employee_Vault/Approved/` containing email parameters
- Or direct parameters: to, cc, bcc, subject, body, html_body, attachments

## Outputs
- Email sent via SMTP through the MCP server
- Send confirmation with message_id
- Audit log entry in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- Approved file moved to `AI_Employee_Vault/Done/`

## Approval Required
- **Yes** - Must go through `hitl-approval` first
- Only files in /Approved/ trigger execution

## MCP Server
- **Server**: `mcp/email_server.py`
- **Protocol**: JSON-RPC 2.0 over stdio
- **Credentials**: Loaded from environment variables (never exposed)

## Environment Variables Required
```
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=your-email@gmail.com
EMAIL_RATE_LIMIT_PER_DAY=500
EMAIL_MAX_ATTACHMENT_SIZE_MB=25
```

## Available MCP Methods

### send_email
```json
{
  "jsonrpc": "2.0",
  "id": "unique_id",
  "method": "send_email",
  "params": {
    "to": ["recipient@example.com"],
    "cc": [],
    "bcc": [],
    "subject": "Subject line",
    "body": "Plain text body",
    "html_body": "<p>HTML body</p>",
    "attachments": [],
    "priority": "normal"
  }
}
```

### validate_recipients
Validates email addresses without sending. Use before send_email.
```json
{
  "jsonrpc": "2.0",
  "id": "unique_id",
  "method": "validate_recipients",
  "params": {
    "recipients": ["test@example.com", "invalid-email"]
  }
}
```

### get_account_info
Returns current account status and rate limit usage.

### ping
Health check - returns `{"status": "ok"}`.

## Error Codes
- `-32000`: General email sending error
- `-32001`: Authentication failure (check EMAIL_SMTP_PASSWORD)
- `-32002`: Invalid recipient
- `-32003`: Rate limit exceeded (daily limit)
- `-32004`: Server unavailable / timeout
- `-32006`: Attachment too large

## Process Steps
1. Validate the action has been approved (file is in /Approved/)
2. Parse email parameters from the approval file
3. Optionally validate recipients via `validate_recipients`
4. If DRY_RUN=true, log intent and skip actual send
5. Call `send_email` via MCP client (`src/utils/mcp_client.py`)
6. Log result to audit log (PII sanitized)
7. Move file to /Done/

## Code Reference
- `mcp/email_server.py` - EmailMCPServer class
- `src/utils/mcp_client.py` - MCPClient.send_email()
- `src/processors/silver_processor.py` - SilverProcessor._execute_via_mcp()

## Security Notes
- Credentials are ONLY in .env (gitignored) and loaded by MCP server process
- Main application never sees SMTP password
- All log entries are sanitized (emails redacted, passwords masked)
- Rate limiting prevents abuse (configurable daily limit)
- TLS is required for SMTP connections

## Related Skills
- `hitl-approval` - Must approve before this skill can execute
- `audit-log` - Logs all email send attempts
- `detect-sensitive-action` - Detects email-related actions
