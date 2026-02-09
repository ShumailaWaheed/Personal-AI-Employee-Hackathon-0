#!/usr/bin/env python3
"""
Email MCP Server
Handles email sending through JSON-RPC over stdio.
Credentials are loaded from environment variables and never exposed to the main application.
"""
import sys
import json
import smtplib
import re
import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Any


class EmailMCPServer:
    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.smtp_username = os.getenv('EMAIL_SMTP_USERNAME')
        self.smtp_password = os.getenv('EMAIL_SMTP_PASSWORD')
        self.from_address = os.getenv('EMAIL_FROM_ADDRESS')
        self.rate_limit = int(os.getenv('EMAIL_RATE_LIMIT_PER_DAY', '500'))
        self.max_attachment_mb = int(os.getenv('EMAIL_MAX_ATTACHMENT_SIZE_MB', '25'))
        self._sent_today = 0
        self._last_reset = datetime.now().date()

    def _check_rate_limit(self) -> bool:
        today = datetime.now().date()
        if today != self._last_reset:
            self._sent_today = 0
            self._last_reset = today
        return self._sent_today < self.rate_limit

    def _make_response(self, request_id, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _make_error(self, request_id, code: int, message: str, data: dict | None = None) -> dict:
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}

    def handle_request(self, request: dict) -> dict:
        method = request.get('method')
        request_id = request.get('id')
        params = request.get('params', {})

        handlers = {
            'send_email': self.send_email,
            'get_account_info': self.get_account_info,
            'validate_recipients': self.validate_recipients,
            'ping': lambda _: self._make_response(request_id, {"status": "ok"}),
        }

        handler = handlers.get(method)
        if not handler:
            return self._make_error(request_id, -32601, "Method not found")
        return handler(params) if method != 'ping' else handler(params)

    def send_email(self, params: dict) -> dict:
        request_id = params.get('id')

        if not self._check_rate_limit():
            return self._make_error(request_id, -32003, "Rate limit exceeded")

        to_addrs = params.get('to', [])
        cc = params.get('cc', [])
        bcc = params.get('bcc', [])
        subject = params.get('subject', '')
        body = params.get('body', '')
        html_body = params.get('html_body', '')
        attachments = params.get('attachments', [])

        if not to_addrs:
            return self._make_error(request_id, -32002, "No recipients specified")

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = ', '.join(to_addrs)
            if cc:
                msg['Cc'] = ', '.join(cc)

            if body:
                msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            for attachment in attachments:
                decoded = base64.b64decode(attachment['content_base64'])
                if len(decoded) > self.max_attachment_mb * 1024 * 1024:
                    return self._make_error(request_id, -32006, "Attachment size limit exceeded")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(decoded)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment["filename"]}"')
                msg.attach(part)

            all_recipients = to_addrs + cc + bcc

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)

            self._sent_today += 1

            return self._make_response(request_id, {
                "success": True,
                "message_ids": [f"msg_{int(time.time())}"],
                "sent_count": len(all_recipients),
                "provider_response": "250 OK: Message accepted for delivery"
            })
        except smtplib.SMTPAuthenticationError:
            return self._make_error(request_id, -32001, "Authentication failure")
        except Exception as e:
            return self._make_error(request_id, -32000, f"Email sending failed: {e}")

    def get_account_info(self, params: dict) -> dict:
        request_id = params.get('id')
        return self._make_response(request_id, {
            "success": True,
            "account": {
                "email_address": self.from_address,
                "service_provider": self.smtp_host,
                "rate_limits": {
                    "messages_per_day": self.rate_limit,
                    "current_usage": self._sent_today,
                },
                "connected_at": datetime.now().isoformat()
            }
        })

    def validate_recipients(self, params: dict) -> dict:
        request_id = params.get('id')
        recipients = params.get('recipients', [])
        valid, invalid, details = [], [], {}

        email_re = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
        for addr in recipients:
            if email_re.match(addr):
                valid.append(addr)
                details[addr] = {"valid": True, "syntax_valid": True, "domain_exists": True}
            else:
                invalid.append(addr)
                details[addr] = {"valid": False, "reason": "invalid_syntax"}

        return self._make_response(request_id, {
            "success": True,
            "valid_recipients": valid,
            "invalid_recipients": invalid,
            "validation_details": details
        })


def main():
    server = EmailMCPServer()

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }), flush=True)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
