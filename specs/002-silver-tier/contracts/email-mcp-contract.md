# Email MCP Server Contract

## Overview
This contract defines the interface and capabilities of the Email MCP (Model Context Protocol) server for the Silver Tier Personal AI Employee system.

## Capabilities
The Email MCP server provides secure email sending capabilities through a JSON-RPC interface, ensuring that email credentials are never exposed to the main application.

## JSON-RPC Methods

### 1. send_email
**Description**: Sends an email to one or more recipients

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "method": "send_email",
  "params": {
    "to": ["recipient@example.com"],
    "cc": ["copy@example.com"],
    "bcc": ["blind_copy@example.com"],
    "subject": "Email subject line",
    "body": "Plain text body of the email",
    "html_body": "<p>HTML formatted body</p>",
    "attachments": [
      {
        "filename": "document.pdf",
        "content_base64": "base64_encoded_content",
        "mime_type": "application/pdf"
      }
    ],
    "priority": "normal" // normal, high, low
  }
}
```

**Response (Success)**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "result": {
    "success": true,
    "message_ids": ["msg_12345", "msg_67890"],
    "sent_count": 1,
    "provider_response": "250 OK: Message accepted for delivery"
  }
}
```

**Response (Error)**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "error": {
    "code": -32000,
    "message": "Email sending failed",
    "data": {
      "reason": "invalid_recipient",
      "details": "Recipient address not valid"
    }
  }
}
```

### 2. get_account_info
**Description**: Retrieves information about the connected email account

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "method": "get_account_info",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "result": {
    "success": true,
    "account": {
      "email_address": "user@example.com",
      "service_provider": "smtp.gmail.com",
      "rate_limits": {
        "messages_per_day": 500,
        "current_usage": 45
      },
      "connected_at": "2026-01-26T10:00:00Z"
    }
  }
}
```

### 3. validate_recipients
**Description**: Validates email addresses without sending an email

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "method": "validate_recipients",
  "params": {
    "recipients": ["test@example.com", "invalid-email"]
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "result": {
    "success": true,
    "valid_recipients": ["test@example.com"],
    "invalid_recipients": ["invalid-email"],
    "validation_details": {
      "test@example.com": {
        "valid": true,
        "syntax_valid": true,
        "domain_exists": true
      },
      "invalid-email": {
        "valid": false,
        "reason": "invalid_syntax"
      }
    }
  }
}
```

## Error Codes
- `-32000`: General email sending error
- `-32001`: Authentication failure
- `-32002`: Invalid recipient
- `-32003`: Rate limit exceeded
- `-32004`: Server temporarily unavailable
- `-32005`: Content violation (spam detection)
- `-32006`: Attachment size limit exceeded

## Configuration Parameters
The Email MCP server expects the following environment variables to be set:

- `EMAIL_SMTP_HOST`: SMTP server hostname (e.g., smtp.gmail.com)
- `EMAIL_SMTP_PORT`: SMTP server port (e.g., 587)
- `EMAIL_SMTP_USERNAME`: Username for authentication
- `EMAIL_SMTP_PASSWORD`: Password or app-specific token
- `EMAIL_FROM_ADDRESS`: Default sender address
- `EMAIL_RATE_LIMIT_PER_DAY`: Daily sending limit (default: 500)
- `EMAIL_MAX_ATTACHMENT_SIZE_MB`: Maximum attachment size in MB (default: 25)

## Security Measures
- Credentials are never logged or exposed to the main application
- All connections use TLS encryption
- Rate limiting prevents spam and service abuse
- Recipient validation prevents invalid email attempts
- Content scanning detects potential spam patterns

## Health Check
The server responds to ping requests to confirm operational status:
```json
{
  "jsonrpc": "2.0",
  "id": "ping",
  "method": "ping",
  "params": {}
}
```