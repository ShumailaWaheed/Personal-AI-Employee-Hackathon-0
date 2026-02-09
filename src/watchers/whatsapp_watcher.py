"""
WhatsApp Watcher Implementation
Monitors WhatsApp Web for new messages using Playwright with persistent sessions
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.playwright = None
        self.browser = None
        self.page = None
        self.session_dir = os.getenv('WHATSAPP_SESSION_DIR', './whatsapp_session')
        self._seen_ids: set[str] = set()

    def _ensure_browser(self):
        """Initialize Playwright browser with persistent context if not already started"""
        if self.page is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            return

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true',
            viewport={'width': 1280, 'height': 800}
        )
        self.page = self.browser.new_page()
        self.page.goto("https://web.whatsapp.com/")
        logger.info("Waiting for WhatsApp Web login (scan QR if needed)...")
        self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
        logger.info("WhatsApp Web session ready")

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread conversations"""
        self._ensure_browser()
        if self.page is None:
            return []

        unread = []
        try:
            chat_elements = self.page.query_selector_all('[data-testid="cell-frame-container"]')
            for el in chat_elements:
                badge = el.query_selector('[data-testid="icon-unread-count"]')
                if not badge:
                    continue
                title_el = el.query_selector('span[title]')
                if not title_el:
                    continue
                contact = title_el.get_attribute('title')
                uid = f"wa_{contact}_{datetime.now().strftime('%Y%m%d_%H')}"
                if uid in self._seen_ids:
                    continue
                self._seen_ids.add(uid)
                unread.append({
                    'type': 'whatsapp_message',
                    'contact': contact,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'unread',
                })
        except Exception as e:
            logger.error(f"Error checking WhatsApp: {e}")

        return unread

    def create_action_file(self, item) -> Path:
        """Create an action file for a WhatsApp message"""
        ts = int(datetime.now().timestamp())
        safe_contact = "".join(c if c.isalnum() or c in '-_' else '_' for c in item['contact'])
        filename = f"whatsapp_{safe_contact}_{ts}.md"
        filepath = self.needs_action / filename

        content = f"""# WhatsApp Message Alert: {item['contact']}

## Message Details
- **Source**: WhatsApp
- **Contact**: {item['contact']}
- **Received**: {item['timestamp']}
- **Status**: {item['status']}

## Action Required
Review the message from {item['contact']} in WhatsApp Web and determine appropriate response.

## Recommended Actions
- Respond to important messages
- Schedule follow-up if needed
- Create task for ongoing conversations
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created WhatsApp action file: {filepath.name}")
        return filepath

    def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == "__main__":
    from utils.logger import setup_logger
    from utils.config_loader import load_config

    config = load_config()
    setup_logger(config.get('LOG_LEVEL', 'INFO'))
    watcher = WhatsAppWatcher(config['VAULT_PATH'])
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.cleanup()
