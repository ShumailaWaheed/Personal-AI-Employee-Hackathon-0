#!/usr/bin/env python3
"""
Instagram MCP Server
Handles Instagram posting operations through JSON-RPC over stdio.
Supports API mode (Graph API for business accounts) and Playwright mode (browser automation via Edge).
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


class InstagramMCPServer:
    def __init__(self):
        self.mode = os.getenv('INSTAGRAM_MODE', 'playwright')  # api or playwright
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.api_base = 'https://graph.facebook.com/v19.0'
        self.session_dir = os.getenv('INSTAGRAM_SESSION_DIR', './instagram_session')
        self.headless = os.getenv('INSTAGRAM_HEADLESS', 'false').lower() == 'true'
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
            'create_post': self.create_post,
            'get_post_metrics': self.get_post_metrics,
            'ping': lambda p: self._make_response(request_id, {"status": "ok", "server": "instagram", "mode": self.mode}),
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
            if 'unauthorized' in str(e).lower() or '401' in str(e) or '190' in str(e):
                return self._make_error(request_id, -32001, f"Authentication failed: {e}")
            return self._make_error(request_id, -32000, f"Operation failed: {e}")

    def create_post(self, params: dict) -> dict:
        """Create an Instagram post"""
        request_id = params.get('id')
        caption = params.get('caption', '')
        image_url = params.get('image_url', '')
        image_path = params.get('image_path', '')

        if not caption and not image_url and not image_path:
            return self._make_error(request_id, -32010, "caption, image_url, or image_path is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "post_id": f"dry_run_{int(time.time())}",
                "dry_run": True,
                "message": f"Would create Instagram post: {caption[:50]}...",
            })

        if self.mode == 'api':
            return self._post_via_api(request_id, caption, image_url)
        else:
            return self._post_via_playwright(request_id, caption, image_path)

    def _post_via_api(self, request_id, caption, image_url):
        """Post via Instagram Graph API (requires business account)"""
        if not self.account_id:
            return self._make_error(request_id, -32010,
                                    "INSTAGRAM_BUSINESS_ACCOUNT_ID is required for API mode")

        # Step 1: Create media container
        container_url = f'{self.api_base}/{self.account_id}/media'
        container_params = {
            'access_token': self.access_token,
            'caption': caption,
        }
        if image_url:
            container_params['image_url'] = image_url

        resp = requests.post(container_url, data=container_params)

        if resp.status_code in (401, 190):
            raise ConnectionError("Instagram authentication failed - check access token")

        resp.raise_for_status()
        container_id = resp.json().get('id')

        if not container_id:
            return self._make_error(request_id, -32000, "Failed to create media container")

        # Step 2: Publish the container
        publish_url = f'{self.api_base}/{self.account_id}/media_publish'
        publish_params = {
            'access_token': self.access_token,
            'creation_id': container_id,
        }
        resp = requests.post(publish_url, data=publish_params)
        resp.raise_for_status()
        post_id = resp.json().get('id', '')

        return self._make_response(request_id, {
            "success": True,
            "post_id": str(post_id),
            "caption": caption,
        })

    # ── Playwright browser automation (Edge + stealth) ─────────────────

    def _ensure_browser(self):
        """Launch Edge browser with persistent Instagram session and stealth."""
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

        self._page.goto("https://www.instagram.com/", timeout=60000, wait_until="domcontentloaded")
        self._page.wait_for_timeout(5000)

        url = self._page.url
        if 'login' in url.lower() or 'accounts/login' in url.lower():
            self._cleanup_browser()
            raise ConnectionError(
                "Instagram session not logged in. Please log in via browser first "
                "using the shared session directory."
            )

        logger.info("Instagram browser session ready")

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

    def _post_via_playwright(self, request_id, caption, image_path):
        """Post to Instagram via Edge browser automation."""
        self._ensure_browser()
        page = self._page

        # Generate a default image if no image_path provided
        if not image_path or not os.path.exists(image_path):
            image_path = self._generate_default_image(caption)

        image_path = os.path.abspath(image_path)

        # Step 1: Click Create (+ button)
        page.goto("https://www.instagram.com/", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        page.locator('svg[aria-label="New post"]').first.click(force=True)
        page.wait_for_timeout(3000)

        # Step 2: Upload image
        select_btn = page.locator(
            'button:has-text("Select from computer"), '
            'button:has-text("Select From Computer")'
        ).first
        with page.expect_file_chooser() as fc_info:
            select_btn.click()
        fc_info.value.set_files(image_path)
        page.wait_for_timeout(4000)

        # Step 3: Next (crop) via JS
        page.evaluate('''() => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (dialog) {
                const btns = dialog.querySelectorAll('div[role="button"]');
                for (const btn of btns) {
                    if (btn.textContent.trim() === "Next") { btn.click(); return; }
                }
            }
        }''')
        page.wait_for_timeout(3000)

        # Step 4: Next (filters) via JS
        page.evaluate('''() => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (dialog) {
                const btns = dialog.querySelectorAll('div[role="button"]');
                for (const btn of btns) {
                    if (btn.textContent.trim() === "Next") { btn.click(); return; }
                }
            }
        }''')
        page.wait_for_timeout(3000)

        # Step 5: Add caption
        if caption:
            caption_area = page.locator('div[contenteditable="true"]').first
            caption_area.click(force=True)
            page.wait_for_timeout(500)
            page.keyboard.type(caption, delay=20)
            page.wait_for_timeout(1000)

        # Step 6: Share (publish) - click the blue Share in header
        page.evaluate('''() => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (dialog) {
                const all = dialog.querySelectorAll('div[role="button"], span, button');
                for (const el of all) {
                    if (el.textContent.trim() === "Share" && el.getBoundingClientRect().y < 200) {
                        el.click();
                        return;
                    }
                }
            }
        }''')
        page.wait_for_timeout(10000)

        post_id = f"pw_{int(time.time())}"
        logger.info(f"Instagram post published via Playwright (id={post_id})")

        return self._make_response(request_id, {
            "success": True,
            "post_id": post_id,
            "caption": caption,
            "mode": "playwright",
        })

    def _generate_default_image(self, caption: str) -> str:
        """Generate a simple branded image when no image is provided."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ConnectionError("Pillow not installed. Run: pip install Pillow")

        img = Image.new('RGB', (1080, 1080), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for i in range(540):
            color = tuple(min(255, c) for c in (15 + i // 5, 23 + i // 8, 42 + i // 4))
            draw.rectangle([(0, i * 2), (1080, i * 2 + 2)], fill=color)

        try:
            font_large = ImageFont.truetype('arial.ttf', 60)
            font_small = ImageFont.truetype('arial.ttf', 28)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = font_large

        draw.rectangle([(40, 200), (1040, 210)], fill=(99, 102, 241))
        draw.text((540, 350), 'AI EMPLOYEE', fill=(255, 255, 255), font=font_large, anchor='mm')

        # Wrap caption text
        words = caption[:200].split()
        lines, current = [], ''
        for word in words:
            if len(current + ' ' + word) < 40:
                current = (current + ' ' + word).strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = 480
        for line in lines[:6]:
            draw.text((540, y), line, fill=(199, 210, 254), font=font_small, anchor='mm')
            y += 45

        draw.rectangle([(40, 870), (1040, 880)], fill=(99, 102, 241))
        draw.text((540, 940), 'Powered by Claude Code', fill=(100, 116, 139), font=font_small, anchor='mm')

        path = os.path.join(os.path.dirname(__file__), '..', 'ai_employee_post.jpg')
        img.save(path, quality=95)
        return path

    def get_post_metrics(self, params: dict) -> dict:
        request_id = params.get('id')
        post_id = params.get('post_id', '')

        if not post_id:
            return self._make_error(request_id, -32010, "post_id is required")

        if self.dry_run:
            return self._make_response(request_id, {
                "success": True,
                "dry_run": True,
                "metrics": {"likes": 0, "comments": 0, "reach": 0, "impressions": 0},
            })

        url = f'{self.api_base}/{post_id}/insights'
        params_data = {
            'access_token': self.access_token,
            'metric': 'impressions,reach,likes,comments',
        }
        resp = requests.get(url, params=params_data)
        resp.raise_for_status()
        insights = resp.json().get('data', [])

        metrics = {}
        for item in insights:
            name = item.get('name', '')
            values = item.get('values', [{}])
            metrics[name] = values[0].get('value', 0) if values else 0

        return self._make_response(request_id, {
            "success": True,
            "post_id": post_id,
            "metrics": {
                "likes": metrics.get('likes', 0),
                "comments": metrics.get('comments', 0),
                "reach": metrics.get('reach', 0),
                "impressions": metrics.get('impressions', 0),
            },
        })


def main():
    server = InstagramMCPServer()
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
