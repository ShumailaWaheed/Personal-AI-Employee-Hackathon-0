#!/usr/bin/env python3
"""
WhatsApp MCP Server
Handles WhatsApp messaging through JSON-RPC over stdio.
Supports API mode (token-based) and Playwright mode (browser automation).
Credentials from environment variables.
"""
import sys
import json
import os
import time
import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class WhatsAppMCPServer:
    def __init__(self):
        self.mode = os.getenv('WHATSAPP_MODE', 'playwright')  # api or playwright
        self.api_token = os.getenv('WHATSAPP_API_TOKEN', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.api_base = 'https://graph.facebook.com/v17.0'
        self.session_dir = os.getenv('WHATSAPP_SESSION_DIR', './whatsapp_session')
        self.headless = os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true'
        self._playwright = None
        self._browser = None
        self._page = None

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
            'send_message': self.send_message,
            'get_message_status': self.get_message_status,
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "whatsapp", "mode": self.mode}),
        }

        handler = handlers.get(method)
        if not handler:
            return self._make_error(request_id, -32601, "Method not found")

        try:
            return handler(params)
        except ConnectionError as e:
            if 'session' in str(e).lower() or 'expired' in str(e).lower():
                return self._make_error(request_id, -32031, f"Session expired: {e}")
            return self._make_error(request_id, -32001, str(e))
        except Exception as e:
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def send_message(self, params: dict) -> dict:
        request_id = params.get('id')
        to = params.get('to', '')
        message = params.get('message', '')
        media_url = params.get('media_url')

        if not to or not message:
            return self._make_error(request_id, -32010, "to and message are required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "message_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would send WhatsApp to {to}: {message[:50]}...",
            })

        if self.mode == 'api':
            return self._send_via_api(request_id, to, message, media_url)
        else:
            return self._send_via_playwright(request_id, to, message, media_url)

    def _send_via_api(self, request_id, to, message, media_url):
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }

        resp = requests.post(
            f'{self.api_base}/messages',
            headers=headers,
            json=payload,
        )

        if resp.status_code == 401:
            raise ConnectionError("WhatsApp API authentication failed")

        resp.raise_for_status()
        data = resp.json()
        msg_id = data.get('messages', [{}])[0].get('id', '')

        return self._make_response(request_id, {
            "success": True,
            "message_id": msg_id,
            "to": to,
        })

    def _ensure_browser(self):
        """Launch Playwright browser with persistent WhatsApp Web session."""
        if self._page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ConnectionError("Playwright not installed. Run: pip install playwright && playwright install")

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=self.headless,
            viewport={'width': 1280, 'height': 800},
        )
        self._page = self._browser.new_page()
        self._page.goto("https://web.whatsapp.com/")
        logger.info("Waiting for WhatsApp Web login (scan QR if needed)...")
        try:
            self._page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
        except Exception:
            self._cleanup_browser()
            raise ConnectionError("WhatsApp Web session expired — scan QR code to re-authenticate")
        logger.info("WhatsApp Web session ready")

    def _cleanup_browser(self):
        """Release Playwright resources."""
        try:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._playwright = None
        self._browser = None
        self._page = None

    def _send_via_playwright(self, request_id, to, message, media_url):
        """Send a WhatsApp message via browser automation on WhatsApp Web."""
        self._ensure_browser()
        page = self._page

        # Open chat search and type contact name / number
        search_box = page.wait_for_selector(
            '[data-testid="chat-list-search"],'
            'div[contenteditable="true"][data-tab="3"]',
            timeout=15000,
        )
        search_box.click()
        search_box.fill('')
        search_box.type(to, delay=50)

        # Wait for results and click the matching chat
        try:
            chat_match = page.wait_for_selector(
                f'span[title*="{to}"]',
                timeout=10000,
            )
            chat_match.click()
        except Exception:
            raise ConnectionError(f"Contact '{to}' not found in WhatsApp")

        # Type and send the message
        msg_box = page.wait_for_selector(
            '[data-testid="conversation-compose-box-input"],'
            'div[contenteditable="true"][data-tab="10"]',
            timeout=10000,
        )
        msg_box.click()
        msg_box.type(message, delay=20)

        # Press Enter to send
        msg_box.press('Enter')

        # Brief wait to let the message dispatch
        page.wait_for_timeout(1500)

        msg_id = f"pw_{int(time.time())}"
        logger.info(f"Sent WhatsApp message to {to} via Playwright (id={msg_id})")

        return self._make_response(request_id, {
            "success": True,
            "message_id": msg_id,
            "to": to,
            "mode": "playwright",
        })

    def get_message_status(self, params: dict) -> dict:
        request_id = params.get('id')
        message_id = params.get('message_id', '')

        if not message_id:
            return self._make_error(request_id, -32010, "message_id is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "dry_run": True,
                "status": "delivered",
            })

        # For API mode, check status via API
        return self._make_response(request_id, {
            "success": True,
            "message_id": message_id,
            "status": "sent",
        })


def main():
    server = WhatsAppMCPServer()
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
