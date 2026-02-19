#!/usr/bin/env python3
"""
Twitter/X MCP Server
Handles Twitter posting operations through JSON-RPC over stdio.
Supports API mode (OAuth) and Playwright mode (browser automation via Edge).
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


class TwitterMCPServer:
    def __init__(self):
        self.mode = os.getenv('TWITTER_MODE', 'playwright')  # api or playwright
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.api_key = os.getenv('TWITTER_API_KEY', '')
        self.api_secret = os.getenv('TWITTER_API_SECRET', '')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.api_base = 'https://api.twitter.com/2'
        self.session_dir = os.getenv('TWITTER_SESSION_DIR', './twitter_session')
        self.headless = os.getenv('TWITTER_HEADLESS', 'false').lower() == 'true'
        self._playwright = None
        self._browser = None
        self._page = None

    def _oauth1_header(self):
        """Generate OAuth 1.0a header for user-context endpoints (posting)"""
        from requests_oauthlib import OAuth1
        return OAuth1(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )

    def _bearer_header(self):
        return {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }

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
            'create_tweet': self.create_tweet,
            'get_tweet_metrics': self.get_tweet_metrics,
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "twitter", "mode": self.mode}),
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
            if 'unauthorized' in str(e).lower() or '401' in str(e):
                return self._make_error(request_id, -32001, f"Authentication failed: {e}")
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def create_tweet(self, params: dict) -> dict:
        request_id = params.get('id')
        text = params.get('text', '')

        if not text:
            return self._make_error(request_id, -32010, "text is required")

        if len(text) > 280:
            return self._make_error(request_id, -32010, "Tweet exceeds 280 character limit")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "tweet_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create tweet: {text[:50]}...",
            })

        if self.mode == 'api':
            return self._tweet_via_api(request_id, text)
        else:
            return self._tweet_via_playwright(request_id, text)

    def _tweet_via_api(self, request_id, text):
        """Post tweet via Twitter API v2 (requires paid plan)"""
        url = f'{self.api_base}/tweets'
        payload = {"text": text}
        resp = requests.post(url, json=payload, auth=self._oauth1_header())

        if resp.status_code == 401:
            raise ConnectionError("Twitter authentication failed - check API keys")

        resp.raise_for_status()
        data = resp.json().get('data', {})

        return self._make_response(request_id, {
            "success": True,
            "tweet_id": data.get('id', ''),
            "text": data.get('text', text),
        })

    # ── Playwright browser automation (Edge + stealth) ─────────────────

    def _ensure_browser(self):
        """Launch Edge browser with persistent Twitter/X session and stealth."""
        if self._page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ConnectionError("Playwright not installed. Run: pip install playwright && playwright install")

        try:
            from playwright_stealth import Stealth
            self._stealth = Stealth()
        except ImportError:
            self._stealth = None

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=self.headless,
            channel='msedge',
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled'],
            ignore_default_args=['--enable-automation'],
        )
        self._page = self._browser.new_page()

        if self._stealth:
            self._stealth.apply_stealth_sync(self._page)

        self._page.goto("https://x.com/home", timeout=60000, wait_until="domcontentloaded")
        self._page.wait_for_timeout(5000)

        # Check if logged in by URL
        url = self._page.url
        if 'login' in url.lower():
            self._cleanup_browser()
            raise ConnectionError(
                "Twitter/X session not logged in. Please run login first:\n"
                "  python -c \"from playwright.sync_api import sync_playwright; import time; "
                "pw=sync_playwright().start(); b=pw.chromium.launch_persistent_context("
                "user_data_dir='./twitter_session', headless=False, channel='msedge', "
                "args=['--disable-blink-features=AutomationControlled'], "
                "ignore_default_args=['--enable-automation']); p=b.new_page(); "
                "p.goto('https://x.com/i/flow/login'); time.sleep(120); b.close(); pw.stop()\""
            )

        logger.info("Twitter/X browser session ready")

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

    def _tweet_via_playwright(self, request_id, text):
        """Post a tweet via Edge browser automation on Twitter/X."""
        self._ensure_browser()
        page = self._page

        # Navigate directly to compose page
        page.goto("https://x.com/compose/post", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Type the tweet text into the compose box
        tweet_box = page.wait_for_selector(
            '[data-testid="tweetTextarea_0"]',
            timeout=15000,
        )
        tweet_box.click()
        page.wait_for_timeout(500)

        # Use keyboard.type for reliability
        page.keyboard.type(text, delay=30)
        page.wait_for_timeout(1000)

        # Use Ctrl+Enter to post (bypasses overlay click issues)
        page.keyboard.press('Control+Enter')
        page.wait_for_timeout(5000)

        tweet_id = f"pw_{int(time.time())}"
        logger.info(f"Tweet posted via Playwright (id={tweet_id})")

        return self._make_response(request_id, {
            "success": True,
            "tweet_id": tweet_id,
            "text": text,
            "mode": "playwright",
        })

    def get_tweet_metrics(self, params: dict) -> dict:
        request_id = params.get('id')
        tweet_id = params.get('tweet_id', '')

        if not tweet_id:
            return self._make_error(request_id, -32010, "tweet_id is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "dry_run": True,
                "metrics": {"likes": 0, "retweets": 0, "replies": 0, "impressions": 0},
            })

        url = f'{self.api_base}/tweets/{tweet_id}'
        params_data = {'tweet.fields': 'public_metrics'}
        resp = requests.get(url, params=params_data, headers=self._bearer_header())
        resp.raise_for_status()
        data = resp.json().get('data', {})
        metrics = data.get('public_metrics', {})

        return self._make_response(request_id, {
            "success": True,
            "tweet_id": tweet_id,
            "metrics": {
                "likes": metrics.get('like_count', 0),
                "retweets": metrics.get('retweet_count', 0),
                "replies": metrics.get('reply_count', 0),
                "impressions": metrics.get('impression_count', 0),
            },
        })


def main():
    server = TwitterMCPServer()
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
