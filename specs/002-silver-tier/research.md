# Research Findings: Silver Tier Personal AI Employee

## 1. MCP Server Best Practices

**Decision**: Implement a Python-based MCP server using JSON-RPC over stdio for email sending functionality.

**Rationale**:
- JSON-RPC over stdio provides secure, isolated communication between the AI employee and external services
- Python implementation aligns with the existing codebase architecture
- Stdio communication prevents credential exposure in the main application
- Allows for easy expansion to additional MCP services

**Alternatives Considered**:
- Node.js MCP server: Would require additional runtime environment
- HTTP-based MCP: Less secure than stdio, potential credential exposure
- Direct API calls: Violates security principle of separating credentials

## 2. Email MCP Options

**Decision**: Use SMTP-based MCP server with support for API-based email services (SendGrid, etc.)

**Rationale**:
- SMTP is universal and well-supported
- API services offer additional features like analytics and deliverability
- MCP server handles all credential management separately
- JSON-RPC interface makes it easy to switch between SMTP and API providers

**Security Considerations**:
- Credentials stored only in MCP server environment
- Main application never sees credentials
- Rate limiting and error handling built into MCP server

## 3. LinkedIn API v2 Integration

**Decision**: Use LinkedIn's Marketing Developer Platform API for posting functionality

**Rationale**:
- Official API provides stable and supported integration
- OAuth2 authentication keeps credentials secure
- Rate limits well-documented (typically 200 calls per day per application)
- Content guidelines restrict promotional content to business-oriented posts

**Rate Limits & Guidelines**:
- Maximum 1-3 posts per day to respect platform guidelines
- Content must be business-oriented and valuable to audience
- OAuth2 tokens require refresh management

## 4. Playwright for WhatsApp Automation

**Decision**: Implement WhatsApp Web automation using Playwright with persistent sessions

**Rationale**:
- Playwright offers excellent browser automation capabilities
- Persistent sessions maintain login state between runs
- Headless mode allows for background operation
- Session persistence avoids frequent re-authentication

**TOS Compliance**:
- Respect rate limits to avoid detection
- Implement random delays between actions
- Monitor for CAPTCHA or anti-bot measures

## 5. PM2 Python Integration

**Decision**: Configure PM2 to manage Python watcher processes using ecosystem file

**Rationale**:
- PM2 provides robust process management and auto-restart capabilities
- Cross-platform compatibility
- Monitoring and logging features
- Easy configuration for multiple watcher processes

**Implementation**:
- Ecosystem file configures multiple Python scripts
- Auto-restart on failure
- Memory and CPU monitoring
- Cluster mode for high availability

## 6. Audit Logging Patterns

**Decision**: Implement structured JSON logging with sanitization and retention policies

**Rationale**:
- Structured JSON enables easy parsing and analysis
- Sanitization removes sensitive information before logging
- Configurable retention policies (90 days as per constitution)
- Compliant with constitutional requirements for transparency

**Sanitization Strategy**:
- Remove PII from log entries
- Mask sensitive parameters
- Validate log content before writing

## 7. HITL Orchestrator Design

**Decision**: Implement file system polling with watchdog for approval workflow

**Rationale**:
- File system operations are reliable and well-understood
- Watchdog integration provides efficient file change detection
- Simple to implement and maintain
- Aligns with local-first architecture principles

**Implementation**:
- Polling checks for file moves between directories
- Event-driven approach using filesystem watchers
- Timeout handling for pending approvals

## 8. Cross-Platform Scheduling

**Decision**: Use platform-appropriate scheduling tools with Python fallback

**Rationale**:
- Cron on Unix systems provides reliable scheduling
- Task Scheduler on Windows offers similar functionality
- Python-based scheduling as fallback for portability
- Ensures uptime and maintenance tasks execute reliably

**Configuration**:
- Daily backup schedules
- Log rotation and cleanup
- Health check execution